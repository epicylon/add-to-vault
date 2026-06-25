import os
import secrets
import warnings
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from jwt import PyJWTError as JWTError
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from . import models, database


# ── Security Configuration ────────────────────────────────────────────────
SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not SECRET_KEY:
    SECRET_KEY = "super-secret-development-key-add-to-vault"
    warnings.warn(
        "JWT_SECRET_KEY is not set! Using a hard-coded development key. "
        "Set JWT_SECRET_KEY in your environment before deploying to production.",
        RuntimeWarning,
        stacklevel=2,
    )

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # Token valid for 7 days

# ── Password Hashing ──────────────────────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ── OAuth2 Scheme ─────────────────────────────────────────────────────────
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# ── Helper Functions ──────────────────────────────────────────────────────

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a plain password using bcrypt."""
    return pwd_context.hash(password)


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a JWT access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# ── Dependency: Current User ──────────────────────────────────────────────

def get_current_user(
    db: Session = Depends(database.get_db),
    token: str = Depends(oauth2_scheme),
) -> models.User:
    """
    Dependency that resolves the currently authenticated user from a Bearer token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception
    return user
