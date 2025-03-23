from fastapi import APIRouter, Depends, Path, Query
from app.schemas.permission import PermissionCreate, PermissionUpdate, PermissionQuery
from app.services.permission import PermissionService
from app.utils.response import ResponseModel
from app.utils.exceptions import CustomException, ErrorCode
from app.utils.dependencies import get_current_active_user, check_roles, check_preview
from typing import List, Optional

router = APIRouter()

@router.post("", response_model=dict, name="创建用户权限")
async def create_permission(
    permission_data: PermissionCreate,
    _: bool = Depends(check_preview),
    current_user = Depends(check_roles(["SUPER_ADMIN"]))
):
    """创建权限"""
    permission = await PermissionService.create_permission(permission_data)
    return ResponseModel.success({"id": permission.id, "code": permission.code, "name": permission.name})

@router.get("", response_model=dict, name="获取用户权限")
async def get_permissions(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    name: Optional[str] = None,
    code: Optional[str] = None,
    type: Optional[str] = None,
    enable: Optional[bool] = None,
    current_user = Depends(get_current_active_user)
):
    """获取权限列表"""
    result = await PermissionService.get_permissions(page, page_size, name, code, type, enable)
    return ResponseModel.success(result)

@router.get("/tree", response_model=dict, name="获取权限树")
async def get_permission_tree(current_user = Depends(get_current_active_user)):
    """获取权限树"""
    tree = await PermissionService.get_permission_tree()
    return ResponseModel.success(tree)

@router.get("/menu/tree", response_model=dict, name="获取菜单树")
async def get_menu_tree(current_user = Depends(get_current_active_user)):
    """获取菜单树"""
    tree = await PermissionService.get_menu_tree()
    return ResponseModel.success(tree)

@router.get("/resource/menu/tree", response_model=dict, name="获取资源管理菜单树")
async def get_resource_menu_tree(current_user = Depends(get_current_active_user)):
    """获取资源管理菜单树（包括禁用的菜单）"""
    tree = await PermissionService.get_resource_menu_tree()
    return ResponseModel.success(tree)

@router.get("/button/{menu_id}", response_model=dict, name="获取特定菜单下的按钮权限")
async def get_button_permissions(
    menu_id: int = Path(..., ge=1),
    current_user = Depends(get_current_active_user)
):
    """获取特定菜单下的按钮权限"""
    buttons = await PermissionService.get_button_permissions(menu_id)
    return ResponseModel.success(buttons)

@router.get("/stats", response_model=dict, name="获取权限统计数据")
async def get_permission_stats(current_user = Depends(get_current_active_user)):
    """获取权限统计数据"""
    stats = await PermissionService.get_permission_stats()
    return ResponseModel.success(stats)

@router.get("/{permission_id}", response_model=dict, name="获取权限详情")
async def get_permission(
    permission_id: int = Path(..., ge=1),
    current_user = Depends(get_current_active_user)
):
    """获取权限详情"""
    permission = await PermissionService.get_permission_by_id(permission_id)
    if not permission:
        raise CustomException(ErrorCode.ERR_13001)
    
    return ResponseModel.success(permission)

@router.patch("/{permission_id}", response_model=dict, name="更新权限")
async def update_permission(
    permission_data: PermissionUpdate,
    permission_id: int = Path(..., ge=1),
    _: bool = Depends(check_preview),
    current_user = Depends(check_roles(["SUPER_ADMIN"]))
):
    """更新权限"""
    permission = await PermissionService.update_permission(permission_id, permission_data)
    return ResponseModel.success({"id": permission.id, "code": permission.code, "name": permission.name})

@router.delete("/{permission_id}", response_model=dict, name="删除权限")
async def delete_permission(
    permission_id: int = Path(..., ge=1),
    _: bool = Depends(check_preview),
    current_user = Depends(check_roles(["SUPER_ADMIN"]))
):
    """删除权限"""
    await PermissionService.delete_permission(permission_id)
    return ResponseModel.success()

@router.get("/menu/validate", response_model=dict, name="验证菜单路径是否存在")
async def validate_menu_path(
    path: str = Query(...),
    current_user = Depends(get_current_active_user)
):
    """验证菜单路径是否存在"""
    # 验证逻辑...
    return ResponseModel.success(True)  # 或者 False

@router.get("/menu/check-disabled", response_model=dict)
async def check_menu_disabled(
    path: str = Query(...),
    current_user = Depends(get_current_active_user)
):
    """检查菜单是否被禁用"""
    # 查找匹配路径的菜单
    menu = await PermissionService.filter(type="MENU", path=path).first()
    
    if not menu:
        # 菜单不存在
        return ResponseModel.success({
            "exists": False,
            "disabled": False,
            "menuName": None
        })
    
    # 返回菜单状态
    return ResponseModel.success({
        "exists": True,
        "disabled": not menu.enable,
        "menuName": menu.name
    }) 