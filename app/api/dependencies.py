from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_session
from app.services.user import UserService

SessionDeps = Annotated[AsyncSession, Depends(get_session)]


def get_user_service(session: SessionDeps):
    return UserService(session)


UserDeps = Annotated[UserService, Depends(get_user_service)]


