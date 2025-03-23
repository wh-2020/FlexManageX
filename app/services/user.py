from app.models.user import User, Profile
from app.models.role import Role
from app.schemas.user import UserCreate, UserUpdate, ProfileUpdate
from app.core.security import get_password_hash, verify_password
from app.utils.exceptions import CustomException, ErrorCode
from typing import List, Optional, Dict, Any
from tortoise.expressions import Q
from tortoise.transactions import atomic

class UserService:
    @staticmethod
    @atomic()
    async def create_user(user_data: UserCreate) -> User:
        """创建用户"""
        # 检查用户名是否已存在
        exists = await User.filter(username=user_data.username).exists()
        if exists:
            raise CustomException(ErrorCode.ERR_11002)
        
        # 创建用户
        hashed_password = get_password_hash(user_data.password)
        user = await User.create(
            username=user_data.username,
            password=hashed_password,
            enable=user_data.enable
        )
        
        # 创建用户资料
        await Profile.create(user_id=user.id)
        
        # 如果提供了角色ID，则添加角色
        if user_data.roleIds:
            roles = await Role.filter(id__in=user_data.roleIds).all()
            await user.roles.add(*roles)
        
        return user
    
    @staticmethod
    async def get_user_by_id(user_id: int) -> Optional[User]:
        """通过ID获取用户"""
        return await User.filter(id=user_id).first()
    
    @staticmethod
    async def get_user_by_username(username: str) -> Optional[User]:
        """通过用户名获取用户"""
        return await User.filter(username=username).first()
    
    @staticmethod
    async def get_user_with_password(username: str) -> Optional[User]:
        """获取用户（包含密码）"""
        return await User.filter(username=username).first()
    
    @staticmethod
    async def update_user(user_id: int, user_data: UserUpdate) -> Optional[User]:
        """更新用户"""
        user = await UserService.get_user_by_id(user_id)
        if not user:
            raise CustomException(ErrorCode.ERR_11001)
        
        update_data = user_data.dict(exclude_unset=True)
        if update_data:
            await user.update_from_dict(update_data).save()
        
        return user
    
    @staticmethod
    async def delete_user(user_id: int) -> bool:
        """删除用户"""
        user = await UserService.get_user_by_id(user_id)
        if not user:
            raise CustomException(ErrorCode.ERR_11001)
        
        await user.delete()
        return True
    
    @staticmethod
    async def update_profile(user_id: int, profile_data: ProfileUpdate) -> Dict[str, Any]:
        """更新用户资料"""
        # 检查用户是否存在
        user = await UserService.get_user_by_id(user_id)
        if not user:
            raise CustomException(ErrorCode.ERR_11001)
            
        # 查找用户资料，通过 user_id 外键查询
        profile = await Profile.filter(user_id=user_id).first()
        
        if not profile:
            # 如果用户资料不存在，则创建
            profile_dict = profile_data.dict(exclude_unset=True)
            # 创建关联到用户的资料
            profile = await Profile.create(**profile_dict, user_id=user_id)
        else:
            # 更新用户资料
            update_data = profile_data.dict(exclude_unset=True)
            if update_data:
                await profile.update_from_dict(update_data).save()
        
        # 将 Profile 对象转换为字典
        return {
            "id": profile.id,
            "userId": profile.user_id,  # 这是 OneToOneField 自动创建的属性
            "gender": profile.gender,
            "avatar": profile.avatar,
            "email": profile.email,
            "nickName": profile.nick_name
        }
    
    @staticmethod
    async def get_user_profile(user_id: int) -> Dict[str, Any]:
        """获取用户资料"""
        profile = await Profile.filter(user_id=user_id).first()
        
        if not profile:
            return None
            
        # 将 Profile 对象转换为字典
        return {
            "id": profile.id,
            "userId": profile.user_id,  # 这是 OneToOneField 自动创建的属性
            "gender": profile.gender,
            "avatar": profile.avatar,
            "email": profile.email,
            "nickName": profile.nick_name
        }
    
    @staticmethod
    async def get_user_roles(user_id: int) -> List[Role]:
        """获取用户角色"""
        user = await User.filter(id=user_id).prefetch_related("roles").first()
        if not user:
            raise CustomException(ErrorCode.ERR_11001)
        
        return user.roles
    
    @staticmethod
    async def get_user_permissions(user_id: int) -> List[Dict[str, Any]]:
        """获取用户权限"""
        user = await User.filter(id=user_id).prefetch_related("roles__permissions").first()
        if not user:
            raise CustomException(ErrorCode.ERR_11001)
        
        permissions = []
        permission_ids = set()
        
        for role in user.roles:
            for permission in role.permissions:
                if permission.id not in permission_ids:
                    permission_ids.add(permission.id)
                    permissions.append({
                        "id": permission.id,
                        "name": permission.name,
                        "code": permission.code,
                        "type": permission.type
                    })
        
        return permissions
    
    @staticmethod
    @atomic()
    async def add_user_roles(user_id: int, role_ids: List[int]) -> User:
        """添加用户角色"""
        user = await User.filter(id=user_id).prefetch_related("roles").first()
        if not user:
            raise CustomException(ErrorCode.ERR_11001)
        
        # 清除现有角色关联
        await user.roles.clear()
        
        # 如果有新角色，则添加
        if role_ids and len(role_ids) > 0:
            roles = await Role.filter(id__in=role_ids).all()
            await user.roles.add(*roles)
        
        return user
    
    @staticmethod
    async def reset_password(user_id: int, new_password: str) -> bool:
        """重置密码"""
        user = await User.filter(id=user_id).first()
        if not user:
            raise CustomException(ErrorCode.ERR_11001)
        
        hashed_password = get_password_hash(new_password)
        user.password = hashed_password
        await user.save()
        
        return True
    
    @staticmethod
    async def get_users(
        page: int = 1, 
        page_size: int = 10, 
        username: Optional[str] = None,
        enable: Optional[bool] = None
    ) -> Dict[str, Any]:
        """获取用户列表"""
        query = User.all()
        
        if username:
            query = query.filter(username__contains=username)
        
        if enable is not None:
            query = query.filter(enable=enable)
        
        total = await query.count()
        users = await query.offset((page - 1) * page_size).limit(page_size).all()
        
        # 将 User 对象转换为字典
        user_list = []
        for user in users:
            user_list.append({
                "id": user.id,
                "username": user.username,
                "enable": user.enable,
                "createTime": user.create_time.isoformat() + "Z" if user.create_time else None,
                "updateTime": user.update_time.isoformat() + "Z" if user.update_time else None
            })
        
        return {
            "items": user_list,
            "total": total,
            "page": page,
            "page_size": page_size
        }
        
    @staticmethod
    async def get_users_with_details(
        page: int = 1, 
        page_size: int = 10, 
        username: Optional[str] = None,
        enable: Optional[bool] = None
    ) -> Dict[str, Any]:
        """获取用户列表（包含详细信息）"""
        query = User.all()
        
        if username:
            query = query.filter(username__contains=username)
        
        if enable is not None:
            query = query.filter(enable=enable)
        
        total = await query.count()
        users = await query.prefetch_related("profile", "roles").offset((page - 1) * page_size).limit(page_size).all()
        
        # 将 User 对象转换为字典，并包含详细信息
        user_list = []
        for user in users:
            # 获取角色信息
            roles = []
            for role in user.roles:
                roles.append({
                    "id": role.id,
                    "code": role.code,
                    "name": role.name,
                    "enable": role.enable
                })
            
            # 获取用户资料
            gender = None
            avatar = "https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif?imageView2/1/w/80/h/80"
            email = None
            
            if hasattr(user, "profile") and user.profile:
                gender = user.profile.gender
                avatar = user.profile.avatar
                email = user.profile.email
            
            # 构建用户信息
            user_dict = {
                "id": user.id,
                "username": user.username,
                "enable": user.enable,
                "createTime": user.create_time.isoformat() + "Z" if user.create_time else None,
                "updateTime": user.update_time.isoformat() + "Z" if user.update_time else None,
                "roles": roles,
                "gender": gender,
                "avatar": avatar,
                "email": email
            }
            
            user_list.append(user_dict)
        
        return {
            "pageData": user_list,
            "total": total
        }
    
    @staticmethod
    async def get_user_detail(user_id: int) -> Dict[str, Any]:
        """获取用户详情"""
        user = await User.filter(id=user_id).prefetch_related("profile", "roles").first()
        if not user:
            raise CustomException(ErrorCode.ERR_11001)
        
        # 提取角色名称列表，而不是对象
        role_names = [role.name for role in user.roles]
        role_objects = [{"id": role.id, "code": role.code, "name": role.name, "enable": role.enable} for role in user.roles]
        permissions = await UserService.get_user_permissions(user_id)
        
        # 将 Profile 对象转换为字典
        profile_dict = None
        if user.profile:
            profile_dict = {
                "id": user.profile.id,
                "userId": user.profile.user_id,
                "gender": user.profile.gender,
                "avatar": user.profile.avatar,
                "email": user.profile.email,
                "phone": user.profile.phone,
                "nickName": user.profile.nick_name
            }
        
        # 获取当前角色（优先使用超级管理员角色）
        current_role = None
        for role in user.roles:
            if role.code == "SUPER_ADMIN":
                current_role = {
                    "id": role.id,
                    "code": role.code,
                    "name": role.name,
                    "enable": role.enable
                }
                break
        
        if not current_role and user.roles:
            current_role = {
                "id": user.roles[0].id,
                "code": user.roles[0].code,
                "name": user.roles[0].name,
                "enable": user.roles[0].enable
            }
        
        return {
            "id": user.id,
            "username": user.username,
            "enable": user.enable,
            "roles": role_objects,  # 返回完整角色对象
            "roleNames": role_names,  # 返回角色名称列表，用于前端显示
            "permissions": permissions,
            "profile": profile_dict,
            "currentRole": current_role
        } 
