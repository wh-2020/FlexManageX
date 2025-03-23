from fastapi import APIRouter, Depends, Path, Query, Body, Request
from app.schemas.role import RoleCreate, RoleUpdate, RolePermissionAdd, RoleQuery
from app.services.role import RoleService
from app.utils.response import ResponseModel
from app.utils.exceptions import CustomException, ErrorCode
from app.utils.dependencies import get_current_active_user, check_roles, check_preview
from typing import List, Optional, Dict, Any
from app.models.role import Role

router = APIRouter()

@router.post("", response_model=dict)
async def create_role(
    role_data: RoleCreate,
    _: bool = Depends(check_preview),
    current_user = Depends(check_roles(["SUPER_ADMIN"]))
):
    """创建角色"""
    role = await RoleService.create_role(role_data)
    return ResponseModel.success({"id": role.id, "code": role.code, "name": role.name})

@router.get("", response_model=dict)
async def get_roles(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    code: Optional[str] = None,
    name: Optional[str] = None,
    enable: Optional[bool] = None,
    current_user = Depends(get_current_active_user)
):
    """获取角色列表"""
    if enable is not None:
        query = Role.all()
        if enable:
            query = query.filter(enable=enable)
        roles = await query.all()
        
        role_list = []
        for role in roles:
            role_list.append({
                "id": role.id,
                "code": role.code,
                "name": role.name,
                "enable": role.enable
            })
        
        return ResponseModel.success(role_list)
    else:
        result = await RoleService.get_roles(page, page_size, code, name, enable)
        return ResponseModel.success(result)

@router.get("/page", response_model=dict)
async def get_roles_page(
    pageNo: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
    code: Optional[str] = None,
    name: Optional[str] = None,
    enable: Optional[bool] = None,
    current_user = Depends(get_current_active_user)
):
    """获取角色列表（兼容前端 pageNo 和 pageSize 参数）"""
    result = await RoleService.get_roles_with_permissions(pageNo, pageSize, code, name, enable)
    return ResponseModel.success(result)

@router.get("/permissions/tree", response_model=dict)
async def get_role_permissions_tree(current_user = Depends(get_current_active_user)):
    """获取角色权限树"""
    tree = await RoleService.get_role_permissions_tree(current_user)
    return ResponseModel.success(tree)

@router.get("/permissions/by-role", response_model=dict)
async def get_role_permissions_by_id(
    id: int = Query(..., ge=1),
    current_user = Depends(get_current_active_user)
):
    """获取角色权限（通过查询参数）"""
    permissions = await RoleService.get_role_permissions(id)
    return ResponseModel.success(permissions)

@router.get("/stats", response_model=dict)
async def get_role_stats(current_user = Depends(get_current_active_user)):
    """获取角色统计数据"""
    stats = await RoleService.get_role_stats()
    return ResponseModel.success(stats)

@router.get("/users/{role_id}", response_model=dict)
async def get_role_users(
    role_id: int = Path(..., ge=1),
    current_user = Depends(get_current_active_user)
):
    """获取角色用户列表"""
    users = await RoleService.get_role_users(role_id)
    return ResponseModel.success(users)

@router.get("/{role_id}", response_model=dict)
async def get_role(
    role_id: int = Path(..., ge=1),
    current_user = Depends(get_current_active_user)
):
    """获取角色详情"""
    role_detail = await RoleService.get_role_detail(role_id)
    return ResponseModel.success(role_detail)

@router.patch("/{role_id}", response_model=dict)
async def update_role(
    role_data: RoleUpdate,
    role_id: int = Path(..., ge=1),
    _: bool = Depends(check_preview),
    current_user = Depends(check_roles(["SUPER_ADMIN"]))
):
    """更新角色"""
    role = await RoleService.update_role(role_id, role_data)
    return ResponseModel.success({"id": role.id, "code": role.code, "name": role.name})

@router.delete("/{role_id}", response_model=dict)
async def delete_role(
    role_id: int = Path(..., ge=1),
    _: bool = Depends(check_preview),
    current_user = Depends(check_roles(["SUPER_ADMIN"]))
):
    """删除角色"""
    await RoleService.delete_role(role_id)
    return ResponseModel.success()

@router.get("/{role_id}/permissions", response_model=dict)
async def get_role_permissions(
    role_id: int = Path(..., ge=1),
    current_user = Depends(get_current_active_user)
):
    """获取角色权限"""
    permissions = await RoleService.get_role_permissions(role_id)
    return ResponseModel.success(permissions)

@router.post("/{role_id}/permissions", response_model=dict)
async def add_role_permissions(
    permission_data: RolePermissionAdd,
    role_id: int = Path(..., ge=1),
    _: bool = Depends(check_preview),
    current_user = Depends(check_roles(["SUPER_ADMIN"]))
):
    """添加角色权限"""
    await RoleService.add_role_permissions(role_id, permission_data.permission_ids)
    return ResponseModel.success()

@router.put("/{role_id}/permissions", response_model=dict)
async def set_role_permissions(
    request: Request,
    role_id: int = Path(..., ge=1),
    _: bool = Depends(check_preview),
    current_user = Depends(check_roles(["SUPER_ADMIN"]))
):
    """设置角色权限（替换现有权限）"""
    # 直接从请求体中获取数据
    body = await request.json()
    permission_ids = body.get("permission_ids", [])
    
    if not isinstance(permission_ids, list):
        raise CustomException(ErrorCode.ERR_10001, "permission_ids必须是数组")
    
    await RoleService.set_role_permissions(role_id, permission_ids)
    return ResponseModel.success() 