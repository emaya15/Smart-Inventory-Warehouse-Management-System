from fastapi import Depends, HTTPException, status
from typing import List
from app.utils.enums import UserRole

def require_roles(allowed_roles: List[UserRole]):
    def role_checker(current_user = Depends(get_current_active_user)):
        if current_user.role not in [role.value for role in allowed_roles] and current_user.role != UserRole.ADMIN.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have enough permissions to perform this operation"
            )
        return current_user
    return role_checker

from app.dependencies import get_current_active_user
