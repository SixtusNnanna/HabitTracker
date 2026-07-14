from fastapi import HTTPException, status
from passlib.context import CryptContext
from sqlalchemy import select
from app.database.models import User
from app.api.schemas.user import UserCreate
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.base import BaseService
from app.core.email_token import generate_verification_token, verify_verfication_token

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)


class UserService(BaseService[User]):

    def __init__(self, session:  AsyncSession):
        super().__init__(session, User)

    async def signup(self, user_data: UserCreate):
        existing = await self.session.execute(
            select(User).where(User.email == user_data.email)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already Registerd"
            )

        hash_password = pwd_context.hash(user_data.password)
        new_user = User(
            **user_data.model_dump(exclude={"password"}),
            hashed_password=hash_password
        )
        await self.add(new_user)
        token = generate_verification_token(new_user.email)
        print(f"""
                http://127.0.0.1:8000/auth/verify?token={token}
            """)
        return new_user

    async def authenticate_user(self, email: str, password: str) -> User | None:
        user = await self.get_item(email=email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User is not registered")

        if not pwd_context.verify(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid password and Email"
            )
        return user

    async def verify_email(self, token: str):
        email = verify_verfication_token(token)
        print("decoded email:", email)
        if email is None:
            return None
        user = await self.get_item(email=email)
        if user is None:
            return None
        if user.is_verified:
            return user
        user.is_verified = True
        await self.session.commit()
        await self.session.refresh(user)
        return user








