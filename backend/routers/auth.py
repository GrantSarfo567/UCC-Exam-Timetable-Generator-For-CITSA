"""
routers/auth.py
Handles admin login and JWT token generation.
"""

from unittest import result

from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

from database import supabase
from models import LoginRequest, TokenResponse

load_dotenv()

router = APIRouter()

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
SECRET_KEY  = os.getenv("SECRET_KEY")
ALGORITHM   = os.getenv("ALGORITHM")
EXPIRE_MINS = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

pwd_context = CryptContext(schemes=["bcrypt"], 
                           deprecated="auto",
                           bycrypt__rounds=12
                           )  # Increased rounds for better security


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=EXPIRE_MINS)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────

@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest):
    """
    Authenticate an admin and return a JWT token.
    """
    # Fetch admin from Supabase by username
    result = supabase.table("admins") \
        .select("*") \
        .eq("username", credentials.username) \
        .execute()

   
    if not result.data or len(result.data) == 0:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password"
       )

    admin = result.data[0]

    # Verify password
    if not verify_password(credentials.password, admin["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    # Generate JWT
    token = create_access_token({"sub": admin["username"]})

    return TokenResponse(
        access_token=token,
        admin_name=admin["full_name"]
    )