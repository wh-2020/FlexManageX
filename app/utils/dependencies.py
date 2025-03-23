from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.core.config import settings
from app.utils.exceptions import CustomException, ErrorCode
from app.services.user import UserService
from typing import List, Optional
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """获取当前用户"""
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        user_id = int(payload.get("sub"))
        if user_id is None:
            raise CustomException(
                error_code=ErrorCode.ERR_10002,
                status_code=status.HTTP_401_UNAUTHORIZED
            )
    except JWTError:
        raise CustomException(
            error_code=ErrorCode.ERR_10002,
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    user = await UserService.get_user_by_id(user_id)
    if user is None:
        raise CustomException(
            error_code=ErrorCode.ERR_11001,
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    return user

async def get_current_active_user(current_user = Depends(get_current_user)):
    """获取当前活跃用户"""
    if not current_user.enable:
        raise CustomException(
            error_code=ErrorCode.ERR_10002,
            detail="用户已被禁用",
            status_code=status.HTTP_403_FORBIDDEN
        )
    return current_user

def check_roles(required_roles: List[str]):
    """检查用户角色"""
    async def _check_roles(current_user = Depends(get_current_active_user)):
        user_roles = await UserService.get_user_roles(current_user.id)
        user_role_codes = [role.code for role in user_roles]
        
        # 超级管理员拥有所有权限
        if "SUPER_ADMIN" in user_role_codes:
            return current_user
        
        # 检查是否有所需角色
        for role in required_roles:
            if role in user_role_codes:
                return current_user
        
        raise CustomException(
            error_code=ErrorCode.ERR_10005,
            detail="权限不足，需要以下角色之一: " + ", ".join(required_roles),
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    return _check_roles

def check_preview():
    """检查是否为预览环境"""
    if not settings.IS_PREVIEW:
        raise CustomException(
            error_code=ErrorCode.ERR_10005,
            detail="此功能仅在预览环境可用",
            status_code=status.HTTP_403_FORBIDDEN
        )
    return True 