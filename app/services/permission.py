from app.models.permission import Permission
from app.schemas.permission import PermissionCreate, PermissionUpdate, PermissionNode
from app.utils.exceptions import CustomException, ErrorCode
from typing import List, Optional, Dict, Any

class PermissionService:
    @staticmethod
    async def create_permission(permission_data: PermissionCreate) -> Permission:
        """创建权限"""
        # 检查权限代码是否已存在
        exists = await Permission.filter(code=permission_data.code).exists()
        if exists:
            raise CustomException(ErrorCode.ERR_13002)
        
        # 创建权限
        permission = await Permission.create(**permission_data.dict())
        
        return permission
    
    @staticmethod
    async def get_permission_by_id(permission_id: int) -> Optional[Permission]:
        """通过ID获取权限"""
        return await Permission.filter(id=permission_id).first()
    
    @staticmethod
    async def update_permission(permission_id: int, permission_data: PermissionUpdate) -> Optional[Permission]:
        """更新权限"""
        permission = await PermissionService.get_permission_by_id(permission_id)
        if not permission:
            raise CustomException(ErrorCode.ERR_13001)
        
        # 将 PermissionUpdate 模型转换为字典
        update_data = permission_data.dict(exclude_unset=True)
        
        # 特别处理 parent_id 字段
        if 'parent_id' in update_data:
            # 确保 parent_id 被正确设置，即使是 None 值
            permission.parent_id = update_data['parent_id']
            # 从 update_data 中移除 parent_id，因为我们已经手动处理了
            del update_data['parent_id']
        
        # 更新其他字段
        if update_data:
            await permission.update_from_dict(update_data).save()
        else:
            # 如果只有 parent_id 被更新，需要手动保存
            await permission.save()
        
        return permission
    
    @staticmethod
    async def delete_permission(permission_id: int) -> bool:
        """删除权限"""
        permission = await PermissionService.get_permission_by_id(permission_id)
        if not permission:
            raise CustomException(ErrorCode.ERR_13001)
        
        await permission.delete()
        return True
    
    @staticmethod
    async def get_permissions(
        page: int = 1, 
        page_size: int = 10, 
        name: Optional[str] = None,
        code: Optional[str] = None,
        type: Optional[str] = None,
        enable: Optional[bool] = None
    ) -> Dict[str, Any]:
        """获取权限列表"""
        query = Permission.all()
        
        if name:
            query = query.filter(name__contains=name)
        
        if code:
            query = query.filter(code__contains=code)
        
        if type:
            query = query.filter(type=type)
        
        if enable is not None:
            query = query.filter(enable=enable)
        
        total = await query.count()
        permissions = await query.offset((page - 1) * page_size).limit(page_size).all()
        
        return {
            "items": permissions,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    
    @staticmethod
    async def get_permission_tree() -> List[Dict[str, Any]]:
        """获取权限树"""
        # 获取所有权限
        permissions = await Permission.all().order_by("order")
        
        # 构建权限树
        permission_map = {}
        root_permissions = []
        
        # 先将所有权限放入字典
        for permission in permissions:
            permission_dict = {
                "id": permission.id,
                "name": permission.name,
                "code": permission.code,
                "type": permission.type,
                "parent_id": permission.parent_id,
                "path": permission.path,
                "redirect": permission.redirect,
                "icon": permission.icon,
                "component": permission.component,
                "layout": permission.layout,
                "keep_alive": permission.keep_alive,
                "method": permission.method,
                "description": permission.description,
                "show": permission.show,
                "enable": permission.enable,
                "order": permission.order,
                "children": []
            }
            permission_map[permission.id] = permission_dict
        
        # 构建树结构
        for permission_id, permission_dict in permission_map.items():
            parent_id = permission_dict["parent_id"]
            if parent_id is None:
                root_permissions.append(permission_dict)
            else:
                if parent_id in permission_map:
                    permission_map[parent_id]["children"].append(permission_dict)
        
        return root_permissions
        
    @staticmethod
    async def get_menu_tree() -> List[Dict[str, Any]]:
        """获取菜单树 - 用于路由菜单显示"""
        # 获取所有启用的菜单类型的权限
        permissions = await Permission.filter(type="MENU", enable=True, show=True).order_by("order")
        
        # 构建菜单树
        menu_map = {}
        root_menus = []
        
        # 先将所有菜单放入字典
        for permission in permissions:
            menu_dict = {
                "id": permission.id,
                "name": permission.name,
                "code": permission.code,
                "type": permission.type,
                "parent_id": permission.parent_id,
                "path": permission.path,
                "redirect": permission.redirect,
                "icon": permission.icon,
                "component": permission.component,
                "layout": permission.layout,
                "keep_alive": permission.keep_alive,
                "enable": permission.enable,
                "show": permission.show,
                "order": permission.order,
                "children": []
            }
            menu_map[permission.id] = menu_dict
        
        # 构建树结构
        for menu_id, menu_dict in menu_map.items():
            parent_id = menu_dict["parent_id"]
            if parent_id is None:
                root_menus.append(menu_dict)
            else:
                if parent_id in menu_map:
                    menu_map[parent_id]["children"].append(menu_dict)
        
        return root_menus

    @staticmethod
    async def get_resource_menu_tree() -> List[Dict[str, Any]]:
        """获取资源管理菜单树 - 用于资源管理页面显示"""
        # 获取所有菜单类型的权限，包括禁用的
        permissions = await Permission.filter(type="MENU").order_by("order")
        
        # 构建菜单树
        menu_map = {}
        root_menus = []
        
        # 先将所有菜单放入字典
        for permission in permissions:
            menu_dict = {
                "id": permission.id,
                "name": permission.name,
                "code": permission.code,
                "type": permission.type,
                "parent_id": permission.parent_id,
                "path": permission.path,
                "redirect": permission.redirect,
                "icon": permission.icon,
                "component": permission.component,
                "layout": permission.layout,
                "keep_alive": permission.keep_alive,
                "enable": permission.enable,
                "show": permission.show,
                "order": permission.order,
                "children": []
            }
            menu_map[permission.id] = menu_dict
        
        # 构建树结构
        for menu_id, menu_dict in menu_map.items():
            parent_id = menu_dict["parent_id"]
            if parent_id is None:
                root_menus.append(menu_dict)
            else:
                if parent_id in menu_map:
                    menu_map[parent_id]["children"].append(menu_dict)
        
        return root_menus
    
    @staticmethod
    async def get_button_permissions(menu_id: int) -> List[Dict[str, Any]]:
        """获取特定菜单下的按钮权限"""
        # 获取所有按钮类型的权限，且父ID为指定的菜单ID
        buttons = await Permission.filter(type="BUTTON", parent_id=menu_id, enable=True).order_by("order")
        
        # 将按钮权限转换为字典列表
        button_list = []
        for button in buttons:
            button_dict = {
                "id": button.id,
                "name": button.name,
                "code": button.code,
                "type": button.type,
                "parent_id": button.parent_id,
                "path": button.path,
                "method": button.method,
                "description": button.description,
                "enable": button.enable,
                "order": button.order
            }
            button_list.append(button_dict)
        
        return button_list
    
    @staticmethod
    async def get_permission_stats() -> Dict[str, Any]:
        """获取权限统计数据"""
        # 获取所有权限
        permissions = await Permission.all()
        
        # 初始化统计数据
        menu_count = 0
        button_count = 0
        enabled_count = 0
        disabled_count = 0
        
        # 统计各类型权限数量
        for permission in permissions:
            if permission.type == "MENU":
                menu_count += 1
            elif permission.type == "BUTTON":
                button_count += 1
                
            if permission.enable:
                enabled_count += 1
            else:
                disabled_count += 1
        
        # 返回统计结果
        return {
            "menuCount": menu_count,
            "buttonCount": button_count,
            "enabledCount": enabled_count,
            "disabledCount": disabled_count
        } 