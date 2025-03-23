from pydantic import BaseModel, Field
from typing import Optional, List, Any

# 角色创建请求
class RoleCreate(BaseModel):
    code: str = Field(..., min_length=2, max_length=50)
    name: str = Field(..., min_length=2, max_length=50)
    enable: bool = True

# 角色更新请求
class RoleUpdate(BaseModel):
    name: Optional[str] = None
    enable: Optional[bool] = None

# 角色权限添加请求
class RolePermissionAdd(BaseModel):
    permission_ids: List[int]

# 角色查询参数
class RoleQuery(BaseModel):
    page: int = 1
    page_size: int = 10
    code: Optional[str] = None
    name: Optional[str] = None
    enable: Optional[bool] = None

# 角色详情响应
class RoleDetail(BaseModel):
    id: int
    code: str
    name: str
    enable: bool
    permissions: List[Any] 