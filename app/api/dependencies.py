from typing import Annotated
from jose import JWTError
from fastapi import Depends, HTTPException, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import User, Habit
from app.database.session import get_session
from app.services.user import UserService
from app.services.habits import HabitService
from app.core.security import oauth2_scheme
from app.utils import decode_access_token
from app.database.redis import is_jti_blacklisted
from app.services.log import LogService


SessionDeps = Annotated[AsyncSession, Depends(get_session)]


def get_user_service(session: SessionDeps):
    return UserService(session)


UserDeps = Annotated[UserService, Depends(get_user_service)]


def get_token_data(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = decode_access_token(token)
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired Token"
        )


async def get_current_user(
    payload: Annotated[dict, Depends(get_token_data)],
    service: UserDeps
):
    user_id = payload.get("id")
    if user_id is None or await is_jti_blacklisted(payload["jti"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or blacklisted"
        )
    user = await service.get(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Verify your email"
        )
    return user

CurrentUserDps = Annotated[User, Depends(get_current_user)]


def get_habit_service(session: SessionDeps):
    return HabitService(session=session)


HabitsDeps = Annotated[HabitService, Depends(get_habit_service)]


def get_log_services(session: SessionDeps):
    return LogService(session)


async def get_current_habit(
    habit_id: str,
    user: CurrentUserDps,
    service: HabitsDeps
):
    habit = await service.get_habit_by_id(id=habit_id, user=user)
    if habit is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not Found"
        )
    return habit
LogDeps = Annotated[LogService, Depends(get_log_services)]

CurrentHabitDeps = Annotated[Habit, Depends(get_current_habit)]




