from pydantic import BaseModel, Field
from typing import Optional, List, Any

# 权限创建请求
class PermissionCreate(BaseModel):
    name: str
    code: str = Field(..., min_length=2, max_length=50)
    type: str
    parent_id: Optional[int] = None
    path: Optional[str] = None
    redirect: Optional[str] = None
    icon: Optional[str] = None
    component: Optional[str] = None
    layout: Optional[str] = None
    keep_alive: Optional[int] = None
    method: Optional[str] = None
    description: Optional[str] = None
    show: bool = True
    enable: bool = True
    order: Optional[int] = None

# 权限更新请求
class PermissionUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[int] = None
    path: Optional[str] = None
    redirect: Optional[str] = None
    icon: Optional[str] = None
    component: Optional[str] = None
    layout: Optional[str] = None
    keep_alive: Optional[int] = None
    method: Optional[str] = None
    description: Optional[str] = None
    show: Optional[bool] = None
    enable: Optional[bool] = None
    order: Optional[int] = None

# 权限查询参数
class PermissionQuery(BaseModel):
    page: int = 1
    page_size: int = 10
    name: Optional[str] = None
    code: Optional[str] = None
    type: Optional[str] = None
    enable: Optional[bool] = None

# 权限树节点
class PermissionNode(BaseModel):
    id: int
    name: str
    code: str
    type: str
    parent_id: Optional[int] = None
    path: Optional[str] = None
    redirect: Optional[str] = None
    icon: Optional[str] = None
    component: Optional[str] = None
    layout: Optional[str] = None
    keep_alive: Optional[int] = None
    method: Optional[str] = None
    description: Optional[str] = None
    show: bool
    enable: bool
    order: Optional[int] = None
    children: List["PermissionNode"] = [] 