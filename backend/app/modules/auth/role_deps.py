from collections.abc import Callable

from fastapi import Depends, HTTPException, status

from app.modules.auth.deps import get_current_user
from app.modules.auth.models import User


def require_roles(*roles: str) -> Callable:
    allowed = set(roles)

    def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource.",
            )
        return current_user

    return checker


require_admin = require_roles("admin")
require_kol = require_roles("kol", "admin")
require_customer = require_roles("customer", "kol", "admin")
