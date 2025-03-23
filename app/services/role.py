from app.models.role import Role
from app.models.permission import Permission
from app.models.user import User
from app.schemas.role import RoleCreate, RoleUpdate
from app.utils.exceptions import CustomException, ErrorCode
from typing import List, Optional, Dict, Any
from tortoise.transactions import atomic
from tortoise.functions import Count

class RoleService:
    @staticmethod
    async def create_role(role_data: RoleCreate) -> Role:
        """创建角色"""
        # 检查角色代码是否已存在
        exists = await Role.filter(code=role_data.code).exists()
        if exists:
            raise CustomException(ErrorCode.ERR_12002)
        
        # 检查角色名称是否已存在
        exists = await Role.filter(name=role_data.name).exists()
        if exists:
            raise CustomException(ErrorCode.ERR_12002)
        
        # 创建角色
        role = await Role.create(
            code=role_data.code,
            name=role_data.name,
            enable=role_data.enable
        )
        
        return role
    
    @staticmethod
    async def get_role_by_id(role_id: int) -> Optional[Role]:
        """通过ID获取角色"""
        return await Role.filter(id=role_id).first()
    
    @staticmethod
    async def update_role(role_id: int, role_data: RoleUpdate) -> Optional[Role]:
        """更新角色"""
        role = await RoleService.get_role_by_id(role_id)
        if not role:
            raise CustomException(ErrorCode.ERR_12001)
        
        update_data = role_data.dict(exclude_unset=True)
        if update_data:
            # 检查名称是否已存在
            if "name" in update_data and update_data["name"] != role.name:
                exists = await Role.filter(name=update_data["name"]).exists()
                if exists:
                    raise CustomException(ErrorCode.ERR_12002)
            
            await role.update_from_dict(update_data).save()
        
        return role
    
    @staticmethod
    async def delete_role(role_id: int) -> bool:
        """删除角色"""
        role = await RoleService.get_role_by_id(role_id)
        if not role:
            raise CustomException(ErrorCode.ERR_12001)
        
        await role.delete()
        return True
    
    @staticmethod
    async def get_role_permissions(role_id: int) -> List[Dict[str, Any]]:
        """获取角色权限"""
        role = await Role.filter(id=role_id).prefetch_related("permissions").first()
        if not role:
            raise CustomException(ErrorCode.ERR_12001)
        
        # 将 Permission 对象转换为字典
        permissions = []
        for permission in role.permissions:
            permissions.append({
                "id": permission.id,
                "code": permission.code,
                "name": permission.name,
                "type": permission.type,
                "parent_id": permission.parent_id
            })
        
        return permissions
    
    @staticmethod
    @atomic()
    async def add_role_permissions(role_id: int, permission_ids: List[int]) -> Role:
        """添加角色权限"""
        role = await Role.filter(id=role_id).first()
        if not role:
            raise CustomException(ErrorCode.ERR_12001)
        
        permissions = await Permission.filter(id__in=permission_ids).all()
        await role.permissions.add(*permissions)
        
        return role
    
    @staticmethod
    @atomic()
    async def set_role_permissions(role_id: int, permission_ids: List[int]) -> Role:
        """设置角色权限（替换现有权限）"""
        role = await Role.filter(id=role_id).first()
        if not role:
            raise CustomException(ErrorCode.ERR_12001)
        
        # 清除现有权限
        await role.permissions.clear()
        
        # 添加新权限
        permissions = await Permission.filter(id__in=permission_ids).all()
        await role.permissions.add(*permissions)
        
        return role
    
    @staticmethod
    async def get_roles(
        page: int = 1, 
        page_size: int = 10, 
        code: Optional[str] = None,
        name: Optional[str] = None,
        enable: Optional[bool] = None
    ) -> Dict[str, Any]:
        """获取角色列表"""
        query = Role.all()
        
        if code:
            query = query.filter(code__contains=code)
        
        if name:
            query = query.filter(name__contains=name)
        
        if enable is not None:
            query = query.filter(enable=enable)
        
        total = await query.count()
        roles = await query.offset((page - 1) * page_size).limit(page_size).all()
        
        # 将 Role 对象转换为字典
        role_list = []
        for role in roles:
            role_list.append({
                "id": role.id,
                "code": role.code,
                "name": role.name,
                "enable": role.enable
            })
        
        return {
            "items": role_list,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    
    @staticmethod
    async def get_roles_with_permissions(
        page: int = 1, 
        page_size: int = 10, 
        code: Optional[str] = None,
        name: Optional[str] = None,
        enable: Optional[bool] = None
    ) -> Dict[str, Any]:
        """获取角色列表（包含权限ID）"""
        query = Role.all()
        
        if code:
            query = query.filter(code__contains=code)
        
        if name:
            query = query.filter(name__contains=name)
        
        if enable is not None:
            query = query.filter(enable=enable)
        
        total = await query.count()
        roles = await query.prefetch_related("permissions").offset((page - 1) * page_size).limit(page_size).all()
        
        # 将 Role 对象转换为字典，并包含权限ID
        role_list = []
        for role in roles:
            permission_ids = [p.id for p in role.permissions]
            role_list.append({
                "id": role.id,
                "code": role.code,
                "name": role.name,
                "enable": role.enable,
                "permissionIds": permission_ids
            })
        
        return {
            "pageData": role_list,
            "total": total
        }
    
    @staticmethod
    async def get_role_detail(role_id: int) -> Dict[str, Any]:
        """获取角色详情"""
        role = await Role.filter(id=role_id).prefetch_related("permissions").first()
        if not role:
            raise CustomException(ErrorCode.ERR_12001)
        
        permissions = [
            {
                "id": permission.id,
                "name": permission.name,
                "code": permission.code,
                "type": permission.type
            } 
            for permission in role.permissions
        ]
        
        return {
            "id": role.id,
            "code": role.code,
            "name": role.name,
            "enable": role.enable,
            "permissions": permissions
        }
        
    @staticmethod
    async def get_role_permissions_tree(current_user) -> List[Dict[str, Any]]:
        """获取角色权限树"""
        from app.services.permission import PermissionService

        # 获取所有权限树
        permission_tree = await PermissionService.get_permission_tree()

        # 获取当前用户的角色
        await current_user.fetch_related("roles")
        user_roles = current_user.roles

        # **修正1：获取所有角色代码**
        user_role_codes = [role.code for role in user_roles]
        print("用户角色:", user_role_codes)

        # **修正2：获取所有角色的权限**
        roles = await Role.filter(code__in=user_role_codes).prefetch_related("permissions")
        if not roles:
            return permission_tree

        # **修正3：合并所有角色的权限ID**
        user_permission_ids = set()
        for role in roles:
            for perm in role.permissions:
                user_permission_ids.add(perm.id)  # 记录所有权限ID

        print("用户权限ID:", user_permission_ids)

        # 递归标记权限树
        def mark_permissions(nodes, permission_ids):
            result = []
            for node in nodes:
                if node["id"] in permission_ids:
                    node_copy = node.copy()
                    if "children" in node and node["children"]:
                        node_copy["children"] = mark_permissions(node["children"], permission_ids)
                    result.append(node_copy)
            return result

        return mark_permissions(permission_tree, user_permission_ids)
    
    @staticmethod
    async def get_role_stats() -> Dict[str, Any]:
        """获取角色统计数据"""
        # 获取所有角色
        roles = await Role.all()
        
        # 获取所有用户
        users = await User.all().prefetch_related('roles')
        
        # 获取所有权限
        permissions = await Permission.all()
        
        # 初始化统计数据
        total = len(roles)
        active = 0
        users_count = len(users)
        permissions_count = len(permissions)
        
        # 统计启用的角色数量
        for role in roles:
            if role.enable:
                active += 1
        
        # 返回统计结果
        return {
            "total": total,
            "active": active,
            "users": users_count,
            "permissions": permissions_count
        }
    
    @staticmethod
    async def get_role_users(role_id: int) -> List[Dict[str, Any]]:
        """获取角色用户列表"""
        # 获取角色
        role = await Role.filter(id=role_id).first().prefetch_related('users')
        if not role:
            raise CustomException(ErrorCode.ERR_12001)
        
        # 获取用户列表
        user_list = []
        for user in role.users:
            user_dict = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "avatar": user.avatar,
                "gender": user.gender,
                "enable": user.enable,
                "createTime": user.create_time.isoformat() if user.create_time else None
            }
            user_list.append(user_dict)
        
        return user_list 