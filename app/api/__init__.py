from fastapi import APIRouter
from app.api.endpoints import auth, user, role, permission

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["认证管理"])
api_router.include_router(user.router, prefix="/user", tags=["用户管理"])
api_router.include_router(role.router, prefix="/role", tags=["角色管理"])
api_router.include_router(permission.router, prefix="/permission", tags=["权限管理"])