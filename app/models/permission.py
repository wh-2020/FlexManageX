from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator

class Permission(models.Model):
    """权限模型"""
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    code = fields.CharField(max_length=50, unique=True)
    type = fields.CharField(max_length=255)
    parent_id = fields.IntField(null=True, source_field="parentId")
    path = fields.CharField(max_length=255, null=True)
    redirect = fields.CharField(max_length=255, null=True)
    icon = fields.CharField(max_length=255, null=True)
    component = fields.CharField(max_length=255, null=True)
    layout = fields.CharField(max_length=255, null=True)
    keep_alive = fields.IntField(null=True, source_field="keepAlive")
    method = fields.CharField(max_length=255, null=True)
    description = fields.CharField(max_length=255, null=True)
    show = fields.BooleanField(default=True)
    enable = fields.BooleanField(default=True)
    order = fields.IntField(null=True)
    
    class Meta:
        table = "permission"
    
    def __str__(self):
        return self.name

# 创建Pydantic模型
Permission_Pydantic = pydantic_model_creator(Permission, name="Permission")
PermissionIn_Pydantic = pydantic_model_creator(Permission, name="PermissionIn", exclude_readonly=True) 