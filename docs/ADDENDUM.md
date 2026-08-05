# README Addendum — §15–§18

> **Status:** Proposed 2026-08-05, approved for Phase 0. This document fills the sections
> missing from `README updated.md` (which ends at §13). It is binding for §15–§18 and
> introduces no decision that contradicts §1–§13 of the source of truth.

## §16 — Folder Structure

Clean-architecture layering. Dependencies point inward: `api → services → repositories →
models → db`. The `services` (engine) layer never imports from `api`, so it is testable
without a web server.

```
final-year/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app factory + health check
│   │   ├── core/                   # cross-cutting, no business logic
│   │   │   ├── config.py           #   Pydantic Settings <- .env  (§10)
│   │   │   ├── money.py            #   Decimal + ROUND_HALF_UP    (Phase 1, §13.1)
│   │   │   ├── logging.py
│   │   │   └── security.py         #   PyJWT + bcrypt             (§10)
│   │   ├── db/
│   │   │   ├── base.py             #   Declarative Base
│   │   │   ├── session.py          #   engine, SessionLocal, get_db, FK pragma
│   │   │   └── seed/               #   source-cited fee_rules / rto_rates (Phase 3)
│   │   ├── models/                 # SQLAlchemy 2.0, one file per table (§12)
│   │   │   ├── user.py  product.py  platform.py
│   │   │   ├── fee_rule.py  rto_rate.py  comparison.py
│   │   ├── schemas/                # Pydantic request/response models
│   │   ├── repositories/           # Repository Pattern
│   │   ├── services/               # THE ENGINE — pure, framework-free
│   │   │   ├── fee_engine.py
│   │   │   ├── platforms/
│   │   │   │   ├── base.py          #   shared interface (interchangeability, §11.2)
│   │   │   │   ├── amazon_fees.py
│   │   │   │   └── flipkart_fees.py
│   │   │   ├── tax_calculator.py    #   GST + TCS (§13.3)
│   │   │   ├── rto_estimator.py     #   §13.2
│   │   │   ├── breakeven.py         #   piecewise-linear solver (§13.4)
│   │   │   ├── recommendation_engine.py
│   │   │   └── explainer.py         #   signed decomposition (§13.5, RG8)
│   │   └── api/
│   │       ├── deps.py              # get_db, get_current_user
│   │       └── v1/
│   │           ├── router.py
│   │           └── routes/{auth,products,compare,fee_rules}.py
│   ├── tests/                      # mirrors app/ ; unit + integration
│   ├── alembic/                    # migrations (Phase 11)
│   ├── requirements.txt
│   ├── .env.example
│   └── pytest.ini
├── frontend/                       # Vite + React 18 (Phase 10)
├── docs/ADDENDUM.md                # this document
├── .gitignore
└── README updated.md               # §1–§13, the source of truth
```

## §15 — API Specification (v1)

Base path `/api/v1`. JWT bearer auth. **All monetary values are serialised as JSON strings**
(never floats) to preserve the NFR3 exact-decimal guarantee across the wire.

| Method | Path | Auth | Purpose |
|---|---|---|---|
| POST | `/auth/register` | — | Create seller → 201 |
| POST | `/auth/login` | — | → `{access_token, token_type}` (FR9) |
| GET  | `/auth/me` | JWT | Current user |
| POST | `/products` | JWT | Persist a product (FR1) |
| GET  | `/products` | JWT | List own products |
| POST | `/compare` | JWT / anon | Core: product → ranked results + explanation (FR2–FR8) |
| GET  | `/comparisons` | JWT | History (FR8) |
| POST | `/compare/bulk` | JWT | CSV upload ≥200 rows (FR10, at risk) |
| GET  | `/fee-rules` | JWT | List active rules |
| POST | `/fee-rules` | Admin | Insert effective-dated rule, no redeploy (FR11) |

### `POST /compare` response contract

```jsonc
{
  "product": { "...": "echoed input" },
  "results": [
    { "platform": "Flipkart", "rank": 1,
      "breakdown": {
        "gross_revenue":"999.00","commission":"89.91","fixed_fee":"35.00",
        "shipping":"58.00","gateway":"19.98","gst_on_fees":"36.52",
        "rto_adjusted_cost":"45.00","tcs_withheld":"5.00",
        "net_settlement":"714.59","cash_at_settlement":"709.59",
        "effective_profit":"264.59","margin_pct":"26.49","breakeven_price":"..." },
      "rule_id": 88 }
  ],
  "recommendation": {
    "winner":"Flipkart","margin_over_next":"34.52",
    "explanation":[
      {"factor":"commission","delta":"29.97"},
      {"factor":"shipping","delta":"7.00"},
      {"factor":"rto","delta":"-15.00"} ]
  }
}
```

## §17 — Installation & Dev Setup (Windows-first, per §9)

```
python -m venv venv
venv\Scripts\activate
pip install -r backend/requirements.txt
copy backend\.env.example backend\.env
cd backend
uvicorn app.main:app --reload
```

## §18 — Testing Strategy

- **Framework:** `pytest`; tests mirror `app/` under `backend/tests/`.
- **Engine coverage (O2):** unit tests for every public function in `core/money`,
  `tax_calculator`, `rto_estimator`, platform modules, `fee_engine`, `breakeven`.
  `breakeven` additionally has boundary tests at every price-band edge (§13.4).
- **Money tests are exact-value**: assert `Decimal('119.88')`, never approximate.
- **Integration:** API via FastAPI `TestClient`; DB layer against PostgreSQL before any demo.
- **Empirical validation (O6/C6):** `validation/` deviation report over ≥25 SKUs vs
  platform-native calculators. Research output, not a unit test.
- **CI:** GitHub Actions runs `pytest` on every PR (Phase 11).
- Every module ships Unit Tests + Manual Test Cases + Expected Output + Edge Cases.
