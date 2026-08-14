"""API-layer tests (README §15). Full HTTP round-trips via TestClient."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.seed.seeder import seed_all
from app.db.session import get_db
from app.main import create_app
from app.models import Base


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False},
        poolclass=StaticPool, future=True,
    )

    @event.listens_for(engine, "connect")
    def _fk(dbapi_connection, _rec):
        cur = dbapi_connection.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        cur.close()

    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine, expire_on_commit=False, future=True)
    session = TestingSession()
    seed_all(session)

    def override_get_db():
        yield session

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c

    session.close()
    Base.metadata.drop_all(engine)
    engine.dispose()


def _auth_headers(client, email="seller@example.com"):
    client.post("/api/v1/auth/register",
                json={"email": email, "password": "password123", "name": "Seller"})
    token = client.post("/api/v1/auth/login",
                        json={"email": email, "password": "password123"}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


COMPARE_BODY = {
    "name": "Kitchen container", "category": "Home & Kitchen",
    "cost_price": "450.00", "selling_price": "999.00", "weight_g": 400,
}


class TestAuth:
    def test_register_returns_201(self, client):
        r = client.post("/api/v1/auth/register",
                        json={"email": "a@b.com", "password": "password123", "name": "A"})
        assert r.status_code == 201
        assert r.json()["user_id"] >= 1

    def test_duplicate_email_409(self, client):
        body = {"email": "d@b.com", "password": "password123", "name": "D"}
        client.post("/api/v1/auth/register", json=body)
        assert client.post("/api/v1/auth/register", json=body).status_code == 409

    def test_login_and_me(self, client):
        headers = _auth_headers(client)
        me = client.get("/api/v1/auth/me", headers=headers)
        assert me.status_code == 200
        assert me.json()["email"] == "seller@example.com"

    def test_login_wrong_password_401(self, client):
        client.post("/api/v1/auth/register",
                    json={"email": "w@b.com", "password": "password123", "name": "W"})
        r = client.post("/api/v1/auth/login",
                        json={"email": "w@b.com", "password": "wrong"})
        assert r.status_code == 401

    def test_me_without_token_401(self, client):
        assert client.get("/api/v1/auth/me").status_code == 401


class TestCompare:
    def test_anonymous_compare_reproduces_worked_example(self, client):
        r = client.post("/api/v1/compare", json=COMPARE_BODY)
        assert r.status_code == 200
        body = r.json()
        assert body["recommendation"]["winner"] == "Flipkart"
        assert body["recommendation"]["margin_over_next"] == "34.52"
        assert body["recommendation"]["deciding_factor"] == "commission"

    def test_money_serialized_as_strings(self, client):
        body = client.post("/api/v1/compare", json=COMPARE_BODY).json()
        winner = body["results"][0]
        assert winner["platform"] == "Flipkart"
        bd = winner["breakdown"]
        assert bd["effective_profit"] == "264.59"      # str, not float
        assert isinstance(bd["effective_profit"], str)
        assert bd["cash_at_settlement"] == "709.59"    # TCS reflected in cash only

    def test_anonymous_does_not_persist(self, client):
        client.post("/api/v1/compare", json=COMPARE_BODY)  # no auth
        headers = _auth_headers(client)
        assert client.get("/api/v1/comparisons", headers=headers).json() == []

    def test_authenticated_compare_persists_history(self, client):
        headers = _auth_headers(client)
        resp = client.post("/api/v1/compare", json=COMPARE_BODY, headers=headers).json()
        n_platforms = len(resp["results"])
        history = client.get("/api/v1/comparisons", headers=headers).json()
        assert len(history) == n_platforms  # one row per participating platform
        profits = {h["effective_profit"] for h in history}
        assert {"230.07", "264.59"}.issubset(profits)  # Amazon + Flipkart preserved

    def test_unknown_category_422(self, client):
        body = {**COMPARE_BODY, "category": "Nonexistent"}
        assert client.post("/api/v1/compare", json=body).status_code == 422

    def test_negative_weight_rejected_422(self, client):
        body = {**COMPARE_BODY, "weight_g": -5}
        assert client.post("/api/v1/compare", json=body).status_code == 422


class TestProductsAndFeeRules:
    def test_create_and_list_products(self, client):
        headers = _auth_headers(client)
        created = client.post("/api/v1/products", json=COMPARE_BODY, headers=headers)
        assert created.status_code == 201
        listed = client.get("/api/v1/products", headers=headers).json()
        assert len(listed) == 1
        assert listed[0]["selling_price"] == "999.00"

    def test_products_require_auth(self, client):
        assert client.get("/api/v1/products").status_code == 401

    def test_fee_rules_listing(self, client):
        from app.db.seed import data

        headers = _auth_headers(client)
        rules = client.get("/api/v1/fee-rules", headers=headers).json()
        active = [r for r in data.FEE_RULES if r["effective_to"] is None]
        assert len(rules) == len(active)
        assert all(r["effective_to"] is None for r in rules)


class TestBulkCompare:
    CSV = (
        "category,cost_price,selling_price,weight_g\n"
        "Home & Kitchen,450.00,999.00,400\n"
        "Books,100.00,250.00,200\n"
        "Nonexistent,10.00,20.00,100\n"
    )

    def test_bulk_processes_valid_and_reports_invalid(self, client):
        headers = _auth_headers(client)
        files = {"file": ("skus.csv", self.CSV, "text/csv")}
        r = client.post("/api/v1/compare/bulk", files=files, headers=headers)
        assert r.status_code == 200
        body = r.json()
        assert body["total_rows"] == 3
        assert body["processed"] == 2      # Home & Kitchen, Books
        assert body["failed"] == 1         # Nonexistent category
        hk = next(x for x in body["results"] if x["category"] == "Home & Kitchen")
        assert hk["winner"] == "Flipkart"
        assert hk["margin_over_next"] == "34.52"
        assert body["errors"][0]["line"] == 4  # header + 1-based row index

    def test_bulk_requires_auth(self, client):
        files = {"file": ("skus.csv", self.CSV, "text/csv")}
        assert client.post("/api/v1/compare/bulk", files=files).status_code == 401

    def test_bulk_missing_columns_422(self, client):
        headers = _auth_headers(client)
        bad = "category,cost_price\nBooks,100.00\n"
        files = {"file": ("bad.csv", bad, "text/csv")}
        r = client.post("/api/v1/compare/bulk", files=files, headers=headers)
        assert r.status_code == 422


class TestResearchCompare:
    BODY = {"category": "Home & Kitchen", "cost_price": "450.00",
            "selling_price": "999.00", "weight_g": 400}

    def test_returns_provenance_and_dataset_version(self, client):
        r = client.post("/api/v1/compare/research", json=self.BODY)
        assert r.status_code == 200
        body = r.json()
        assert body["dataset_version"] == "2026.08"
        assert "does not represent a live" in body["disclaimer"]
        meesho = next(x for x in body["results"] if x["marketplace"] == "Meesho")
        assert meesho["status"] == "PARTIAL"
        assert meesho["net_profit_min"] == "372.00"
        assert meesho["net_profit_max"] == "487.64"
        assert meesho["sources"]                      # provenance surfaced
        assert meesho["fee_breakdown"][0]["verification_status"]

    def test_partial_marketplaces_visible_with_limitations(self, client):
        body = client.post("/api/v1/compare/research", json=self.BODY).json()
        amazon = next(x for x in body["results"] if x["marketplace"] == "Amazon")
        assert amazon["ranking_eligible"] is False
        assert "PAYMENT" in amazon["unavailable_components"]
        assert any("PAYMENT" in lim for lim in amazon["limitations"])
        assert body["definitive_winner"] == "Meesho"

    def test_unsupported_category_422(self, client):
        bad = {**self.BODY, "category": "Nonexistent"}
        assert client.post("/api/v1/compare/research", json=bad).status_code == 422

    def test_negative_weight_422(self, client):
        bad = {**self.BODY, "weight_g": -5}
        assert client.post("/api/v1/compare/research", json=bad).status_code == 422
