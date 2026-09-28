from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from auth.auth import (
    hash_password,
    verify_password,
    create_access_token
)

from auth.database import (
    create_user,
    get_user
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


class SignupRequest(BaseModel):
    username: str
    password: str
    role: str = "user"


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/signup")
def signup(data: SignupRequest):

    if len(data.password) < 6:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 6 characters"
        )

    existing_user = get_user(data.username)

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    password_hash = hash_password(data.password)

    success = create_user(
        username=data.username,
        password_hash=password_hash,
        role=data.role
    )

    if not success:
        raise HTTPException(
            status_code=400,
            detail="Could not create user"
        )

    return {
        "message": "User created successfully",
        "username": data.username,
        "role": data.role
    }


@router.post("/login")
def login(data: LoginRequest):

    user = get_user(data.username)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    if not verify_password(
        data.password,
        user["password_hash"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    access_token = create_access_token(
        data={
            "sub": user["username"],
            "role": user["role"]
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user["username"],
        "role": user["role"]
    }