from app.models.user import User
from app.core.security import verify_password, create_access_token
from app.utils.exceptions import CustomException, ErrorCode
from app.services.user import UserService
from app.core.redis import redis_client
from typing import Dict, Any, Optional
from datetime import timedelta
from app.core.config import settings

class AuthService:
    @staticmethod
    async def authenticate_user(username: str, password: str) -> Optional[User]:
        """验证用户"""
        user = await User.filter(username=username).first()
        if not user:
            return None
        
        if not verify_password(password, user.password):
            return None
        
        return user
    
    @staticmethod
    async def login(user: User) -> Dict[str, Any]:
        """用户登录"""
        # 生成访问令牌
        access_token = create_access_token(
            subject=user.id,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return {
            "accessToken": access_token,
            "token_type": "bearer"
        }
    
    @staticmethod
    async def logout(user_id: int) -> bool:
        """用户登出"""
        # 可以在这里实现令牌黑名单等逻辑
        return True
    
    @staticmethod
    async def validate_captcha(session_code: str, user_captcha: str) -> bool:
        """验证验证码"""
        if not session_code or not user_captcha:
            return False
        
        return session_code.lower() == user_captcha.lower()
    
    @staticmethod
    async def change_password(user_id: int, old_password: str, new_password: str) -> bool:
        """修改密码"""
        user = await User.filter(id=user_id).first()
        if not user:
            raise CustomException(ErrorCode.ERR_11001)
        
        if not verify_password(old_password, user.password):
            raise CustomException(ErrorCode.ERR_10004)
        
        return await UserService.reset_password(user_id, new_password) 