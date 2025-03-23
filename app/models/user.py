from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
from datetime import datetime

class User(models.Model):
    """用户模型"""
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, unique=True)
    password = fields.CharField(max_length=255)
    enable = fields.BooleanField(default=True)
    create_time = fields.DatetimeField(auto_now_add=True, source_field="createTime")
    update_time = fields.DatetimeField(auto_now=True, source_field="updateTime")
    
    # 关联关系
    roles = fields.ManyToManyField(
        "models.Role", 
        related_name="users", 
        through="user_roles_role",
        forward_key="roleId",  # 指定中间表中的角色ID字段
        backward_key="userId"  # 指定中间表中的用户ID字段
    )
    
    class Meta:
        table = "user"
        ordering = ["id"]
    
    def __str__(self):
        return self.username

class Profile(models.Model):
    """用户资料模型"""
    id = fields.IntField(pk=True)
    gender = fields.IntField(null=True)
    avatar = fields.CharField(max_length=255, default="https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif?imageView2/1/w/80/h/80")
    email = fields.CharField(max_length=255, null=True)
    phone = fields.CharField(max_length=20, null=True)
    nick_name = fields.CharField(max_length=10, null=True, source_field="nickName")
    
    # 关联关系
    user = fields.OneToOneField(
        "models.User",
        related_name="profile",
        on_delete=fields.CASCADE,
        source_field="userId",  # 指定数据库中的字段名
        target_field="id"  # 指定目标字段
    )
    class Meta:
        table = "profile"
    
    def __str__(self):
        return f"{self.user.username}'s profile"

# 创建Pydantic模型
User_Pydantic = pydantic_model_creator(User, name="User", exclude=("password",))
UserIn_Pydantic = pydantic_model_creator(User, name="UserIn", exclude_readonly=True)
Profile_Pydantic = pydantic_model_creator(
    Profile,
    name="Profile",
    exclude_readonly=True,
    include=("userid",),  # 这里确保正确包含 userId
)
ProfileIn_Pydantic = pydantic_model_creator(Profile, name="ProfileIn", exclude_readonly=True) 
