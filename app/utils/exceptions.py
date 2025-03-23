from fastapi import HTTPException, status
from enum import Enum

class ErrorCode(str, Enum):
    # 通用错误
    ERR_10000 = "系统错误"
    ERR_10001 = "参数错误"
    ERR_10002 = "未授权"
    ERR_10003 = "验证码错误"
    ERR_10004 = "密码错误"
    ERR_10005 = "权限不足"
    
    # 用户相关错误
    ERR_11001 = "用户不存在"
    ERR_11002 = "用户已存在"
    ERR_11003 = "无权查看其他用户信息"
    ERR_11004 = "无权修改其他用户信息"
    ERR_11005 = "角色不存在"
    ERR_11006 = "非法操作"
    
    # 角色相关错误
    ERR_12001 = "角色不存在"
    ERR_12002 = "角色已存在"
    
    # 权限相关错误
    ERR_13001 = "权限不存在"
    ERR_13002 = "权限已存在"


class CustomException(HTTPException):
    def __init__(self, error_code: ErrorCode, detail: str = None, status_code: int = status.HTTP_400_BAD_REQUEST):
        # 让 error_code 适应 401 情况
        if error_code == ErrorCode.ERR_10002 or status_code == status.HTTP_401_UNAUTHORIZED:
            self.code = 401
        else:

            self.error_code = error_code

        super().__init__(
            status_code=status_code,
            detail=detail or error_code.value
        )