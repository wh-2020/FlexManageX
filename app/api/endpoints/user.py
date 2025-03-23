from fastapi import APIRouter, Depends, Path, Query, Request
from app.schemas.user import (
    UserCreate, UserUpdate, ProfileUpdate, 
    PasswordReset, UserRoleAdd, UserQuery, UserDetail
)
from app.services.user import UserService
from app.utils.response import ResponseModel
from app.utils.exceptions import CustomException, ErrorCode
from app.utils.dependencies import get_current_active_user, check_roles, check_preview
from typing import List, Optional

router = APIRouter()

@router.post("", response_model=dict)
async def create_user(
    user_data: UserCreate,
    _: bool = Depends(check_preview),
    current_user = Depends(check_roles(["SUPER_ADMIN"]))
):
    """创建用户"""
    user = await UserService.create_user(user_data)
    return ResponseModel.success({"id": user.id, "username": user.username})

@router.get("", response_model=dict)
async def get_users(
    request: Request,
    page: int = Query(1, ge=1, alias="pageNo"),
    page_size: int = Query(10, ge=1, le=100, alias="pageSize"),
    username: Optional[str] = None,
    enable: Optional[bool] = None,
    current_user = Depends(get_current_active_user)
):
    """获取用户列表"""
    # 检查是否使用了 pageNo 和 pageSize 参数
    if "pageNo" in request.query_params or "pageSize" in request.query_params:
        result = await UserService.get_users_with_details(page, page_size, username, enable)
    else:
        result = await UserService.get_users(page, page_size, username, enable)
    return ResponseModel.success(result)

@router.delete("/{user_id}", response_model=dict)
async def delete_user(
    user_id: int = Path(..., ge=1),
    _: bool = Depends(check_preview),
    current_user = Depends(check_roles(["SUPER_ADMIN"]))
):
    """删除用户"""
    # 不能删除自己
    if current_user.id == user_id:
        raise CustomException(ErrorCode.ERR_11006, "非法操作，不能删除自己！")
    
    await UserService.delete_user(user_id)
    return ResponseModel.success()

@router.patch("/{user_id}", response_model=dict)
async def update_user(
    user_data: UserUpdate,
    user_id: int = Path(..., ge=1),
    _: bool = Depends(check_preview),
    current_user = Depends(check_roles(["SUPER_ADMIN", "SYS_ADMIN"]))
):
    """更新用户"""
    user = await UserService.update_user(user_id, user_data)
    return ResponseModel.success({"id": user.id, "username": user.username})

@router.patch("/profile/{user_id}", response_model=dict)
async def update_profile(
    profile_data: ProfileUpdate,
    user_id: int = Path(..., ge=1),
    _: bool = Depends(check_preview),
    current_user = Depends(get_current_active_user)
):
    """更新用户资料"""
    # 只能本人修改
    if current_user.id != user_id:
        raise CustomException(ErrorCode.ERR_11004, "越权操作，用户资料只能本人修改！")
    
    profile = await UserService.update_profile(user_id, profile_data)
    return ResponseModel.success(profile)

@router.get("/detail")
async def get_user_info(current_user = Depends(get_current_active_user)):
    """获取当前用户详情"""
    user_detail = await UserService.get_user_detail(current_user.id)
    return ResponseModel.success(user_detail)

@router.get("/{username}", response_model=dict)
async def get_user_by_username(
    username: str,
    current_user = Depends(check_roles(["SUPER_ADMIN"]))
):
    """通过用户名获取用户"""
    user = await UserService.get_user_by_username(username)
    if not user:
        raise CustomException(ErrorCode.ERR_11001)
    
    return ResponseModel.success({"id": user.id, "username": user.username})

@router.get("/profile/{user_id}", response_model=dict)
async def get_user_profile(
    user_id: int = Path(..., ge=1),
    current_user = Depends(get_current_active_user)
):
    """获取用户资料"""
    # 只能本人或超管查询
    if current_user.id != user_id:
        # 检查是否为超管
        user_roles = await UserService.get_user_roles(current_user.id)
        is_super_admin = any(role.code == "SUPER_ADMIN" for role in user_roles)
        
        if not is_super_admin:
            raise CustomException(ErrorCode.ERR_11003)
    
    profile = await UserService.get_user_profile(user_id)
    return ResponseModel.success(profile)

@router.post("/roles/add/{user_id}", response_model=dict)
async def add_user_roles(
    role_data: UserRoleAdd,
    user_id: int = Path(..., ge=1),
    _: bool = Depends(check_preview),
    current_user = Depends(check_roles(["SUPER_ADMIN"]))
):
    """给用户添加角色"""
    await UserService.add_user_roles(user_id, role_data.role_ids)
    return ResponseModel.success()

@router.patch("/password/reset/{user_id}", response_model=dict)
async def reset_password(
    password_data: PasswordReset,
    user_id: int = Path(..., ge=1),
    _: bool = Depends(check_preview),
    current_user = Depends(check_roles(["SUPER_ADMIN"]))
):
    """管理员重置密码"""
    await UserService.reset_password(user_id, password_data.password)
    return ResponseModel.success() 