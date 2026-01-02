from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.api import models
from src.api.auth import create_access_token, get_current_user, hash_password, verify_password
from src.api.db import get_db
from src.api.schemas import TokenResponse, UserCreate, UserLogin, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Creates a new user account. Email must be unique.",
    operation_id="auth_register",
)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> UserOut:
    """Create a new user."""
    user = models.User(email=str(payload.email).lower(), password_hash=hash_password(payload.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already registered")
    db.refresh(user)
    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login",
    description="Returns a JWT access token for valid credentials.",
    operation_id="auth_login",
)
def login(payload: UserLogin, db: Session = Depends(get_db)) -> TokenResponse:
    """Authenticate a user and return a bearer token."""
    stmt = select(models.User).where(models.User.email == str(payload.email).lower())
    user = db.execute(stmt).scalar_one_or_none()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    token = create_access_token(user.id)
    return TokenResponse(access_token=token, token_type="bearer")


@router.get(
    "/me",
    response_model=UserOut,
    summary="Current user",
    description="Returns the currently authenticated user from Bearer token.",
    operation_id="auth_me",
)
def me(current_user: models.User = Depends(get_current_user)) -> UserOut:
    """Return current authenticated user's profile."""
    return current_user
