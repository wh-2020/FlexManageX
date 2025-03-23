from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Any

# 用户创建请求
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    enable: bool = True
    roleIds: Optional[List[int]] = None

# 用户更新请求
class UserUpdate(BaseModel):
    enable: Optional[bool] = None

# 用户登录请求
class UserLogin(BaseModel):
    username: str
    password: str
    captcha: Optional[str] = None
    is_quick: Optional[bool] = False

# 用户资料更新请求
class ProfileUpdate(BaseModel):
    gender: Optional[int] = None
    avatar: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    feishu_id: Optional[str] = None
    project_id: Optional[str] = None
    nick_name: Optional[str] = None

# 密码更新请求
class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6)

# 密码重置请求
class PasswordReset(BaseModel):
    password: str = Field(..., min_length=6)

# 用户角色添加请求
class UserRoleAdd(BaseModel):
    role_ids: List[int]

# 用户查询参数
class UserQuery(BaseModel):
    page: int = 1
    page_size: int = 10
    username: Optional[str] = None
    enable: Optional[bool] = None

# 令牌响应
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# 用户详情响应
class UserDetail(BaseModel):
    id: int
    username: str
    enable: bool
    roles: List[Any]
    permissions: List[Any]
    profile: Optional[Any] = None 