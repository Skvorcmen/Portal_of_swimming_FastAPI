from fastapi import Depends, HTTPException, status

from app.auth import get_current_user
from app.models import User, UserRole


def require_role(required_roles: list[UserRole]):
    """Dependency factory: доступ только для перечисленных ролей (+ ADMIN всегда)."""

    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        allowed = set(required_roles) | {UserRole.ADMIN}
        if current_user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role {current_user.role} not allowed. Required: {required_roles}",
            )
        return current_user

    return role_checker
