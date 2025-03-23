from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator

class Role(models.Model):
    """角色模型"""
    id = fields.IntField(pk=True)
    code = fields.CharField(max_length=50, unique=True)
    name = fields.CharField(max_length=50, unique=True)
    enable = fields.BooleanField(default=True)
    
    # 关联关系
    permissions = fields.ManyToManyField(
        "models.Permission", 
        related_name="roles", 
        through="role_permissions_permission",
        forward_key="permissionId",  # 指定中间表中的权限ID字段
        backward_key="roleId"  # 指定中间表中的角色ID字段
    )
    
    class Meta:
        table = "role"
    
    def __str__(self):
        return self.name

# 创建Pydantic模型
Role_Pydantic = pydantic_model_creator(Role, name="Role")
RoleIn_Pydantic = pydantic_model_creator(Role, name="RoleIn", exclude_readonly=True) 