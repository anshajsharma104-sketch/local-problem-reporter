from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import timedelta

from ..database import get_db
from ..models import User
from ..services.auth import (
    hash_password, verify_password, create_access_token, decode_access_token
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


class UserLogin(BaseModel):
    email: str
    password: str


class UserRegister(BaseModel):
    email: str
    username: str
    full_name: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    email: str
    is_authority: bool


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str
    is_authority: bool

    class Config:
        orm_mode = True


@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user"""
    
    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if username already exists
    existing_username = db.query(User).filter(User.username == user_data.username).first()
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Create new user
    hashed_password = hash_password(user_data.password)
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        password_hash=hashed_password,
        is_authority=False  # New users are regular users by default
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create access token
    access_token = create_access_token(
        data={"sub": str(db_user.id), "email": db_user.email, "is_authority": db_user.is_authority}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": db_user.id,
        "email": db_user.email,
        "is_authority": db_user.is_authority
    }


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login a user"""
    
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not user.password_hash:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create access token
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "is_authority": user.is_authority}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email,
        "is_authority": user.is_authority
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user(token: str = Query(...), db: Session = Depends(get_db)):
    """Get current authenticated user"""
    
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


@router.post("/verify-authority")
async def verify_authority(token: str = Query(...), db: Session = Depends(get_db)):
    """Verify if current user is an authority"""
    
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    is_authority = payload.get("is_authority", False)
    if not is_authority:
        raise HTTPException(status_code=403, detail="User is not an authority")
    
    return {"is_authority": True}
