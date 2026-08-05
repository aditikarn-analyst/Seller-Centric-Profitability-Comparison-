"""Authentication routes (README §15, FR9)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.models import User
from app.repositories import UsersRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.serializers import serialize_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> dict:
    users = UsersRepository(db)
    if users.get_by_email(payload.email) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        )
    user = users.create(
        email=payload.email,
        password_hash=hash_password(payload.password),
        name=payload.name,
    )
    db.commit()
    return serialize_user(user)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = UsersRepository(db).get_by_email(payload.email)
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    return TokenResponse(access_token=create_access_token(user.user_id))


@router.get("/me")
def me(user: User = Depends(get_current_user)) -> dict:
    return serialize_user(user)
