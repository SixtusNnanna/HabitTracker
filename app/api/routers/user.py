from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.api.dependencies import UserDeps
from app.api.schemas.user import UserResponse, UserCreate
from app.core.security import TokenData
from app.utils import create_access_token


router = APIRouter()

@router.post("/signup", response_model=UserResponse)
async def signup(service: UserDeps, user_create: UserCreate):
    return await service.signup(user_create)


@router.post("/token", response_model=TokenData)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: UserDeps
    ):
    user = await service.authenticate_user(
       email=form_data.username,
       password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ivalid email or password"
        )
    access_token = create_access_token(payload={"id": user.id})
    return {"access_token": access_token, "token_type" : "bearer"}

