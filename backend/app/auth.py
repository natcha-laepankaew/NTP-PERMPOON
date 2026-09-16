from typing import Annotated, Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from .database import get_db
from .models import Role, User
from .security import decode_access_token


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)

DbSession = Annotated[Session, Depends(get_db)]


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: DbSession,
) -> User:

    user_id = decode_access_token(token)

    user = (
        db.scalar(
            select(User)
            .options(
                selectinload(User.role)
                .selectinload(Role.permissions),

                selectinload(User.driver),
            )
            .where(User.id == user_id)
        )
        if user_id
        else None
    )

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid, expired, or inactive account",
        )

    return user


def require_permission(code: str) -> Callable:

    def dependency(
        user: Annotated[User, Depends(get_current_user)]
    ) -> User:

        if code not in {item.code for item in user.role.permissions}:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permission: {code}",
            )

        return user

    return dependency