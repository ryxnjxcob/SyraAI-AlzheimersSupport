from fastapi import APIRouter, HTTPException, Depends
from pydantic import EmailStr
from bson import ObjectId
from ..db import users_col
from ..auth import hash_password, verify_password, create_access_token
from ..models import UserCreate, TokenResponse, UserPublic

router = APIRouter(prefix="/auth", tags=["auth"])

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/register", response_model=UserPublic)
async def register(user: UserCreate):
    existing = await users_col.find_one({"email": user.email})
    if existing:
        raise HTTPException(400, "Email already registered")
    doc = {
        "email": user.email,
        "password": hash_password(user.password),
        "name": user.name,
        "role": user.role,
    }
    res = await users_col.insert_one(doc)
    return {
        "id": str(res.inserted_id),
        "email": user.email,
        "name": user.name,
        "role": user.role,
    }


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest):
    user = await users_col.find_one({"email": credentials.email})
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(401, "Invalid credentials")

    token = create_access_token({"sub": str(user["_id"]), "role": user["role"]})
    return {"access_token": token, "role": user["role"]}
