import re
from pydantic import BaseModel, EmailStr, field_validator


class UserBase(BaseModel):
    full_name: str
    email: EmailStr


class UserCreate(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Password cannot be empty")
        if len(v) < 12:
            raise ValueError(
                "Password must be atleast 12 characters long"
            )
        if not re.search(r"[A-Z]", v):
            raise ValueError(
                "Password must contain atleast one upper case"
            )

        if not re.search(r"[a-z]", v):
            raise ValueError(
                "Password must contain atleast one lower case"
            )
        if not re.search(r"\d", v):
            raise ValueError(
                "Password must contain atleast one digit"
            )
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError(
                "Password must contain at least one special character"
            )
        return v


class UserResponse(UserBase):
    id: str
    is_verified: bool


