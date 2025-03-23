from typing import List, Dict, Any
from fastapi import APIRouter
from app.services.permission import PermissionService

router = APIRouter()

@router.get("/menu/tree", response_model=List[Dict[str, Any]])
async def get_menu_tree():
    """获取菜单树"""
    return await PermissionService.get_menu_tree()

@router.get("/resource/menu/tree", response_model=List[Dict[str, Any]])
async def get_resource_menu_tree():
    """获取资源管理菜单树（包括禁用的菜单）"""
    return await PermissionService.get_resource_menu_tree()

@router.get("/button/{menu_id}", response_model=Dict[str, Any])
async def get_button_permissions(menu_id: int):
    """获取按钮权限"""
    buttons = await PermissionService.get_button_permissions(menu_id)
    return {"items": buttons, "total": len(buttons)}

@router.get("/stats", response_model=Dict[str, Any])
async def get_permission_stats():
    """获取权限统计数据"""
    return await PermissionService.get_permission_stats() 