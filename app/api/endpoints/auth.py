from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.user import UserLogin, Token, UserCreate, PasswordUpdate
from app.services.auth import AuthService
from app.services.user import UserService
from app.utils.response import ResponseModel
from app.utils.exceptions import CustomException, ErrorCode
from app.utils.dependencies import get_current_active_user, check_preview
from app.core.config import settings
from captcha.image import ImageCaptcha
import random
import string
import io
import base64

router = APIRouter()


@router.post("/login", name="用户登录")
async def login(user_data: UserLogin, request: Request):
    """用户登录"""
    # 预览环境下可快速登录，不用验证码
    # if settings.IS_PREVIEW and user_data.is_quick:
    if settings.IS_PREVIEW:
        user = await AuthService.authenticate_user(user_data.username, user_data.password)
        if not user:
            raise CustomException(ErrorCode.ERR_10004)
        token_data = await AuthService.login(user)
        return ResponseModel.success(token_data, originUrl=request.url.path)

    # 验证验证码
    if not user_data.captcha:
        raise CustomException(ErrorCode.ERR_10003)

    # 验证用户
    user = await AuthService.authenticate_user(user_data.username, user_data.password)
    if not user:
        raise CustomException(ErrorCode.ERR_10004)

    token_data = await AuthService.login(user)
    return ResponseModel.success(token_data, originUrl=request.url.path)


@router.post("/register", name="用户注册")
async def register(user_data: UserCreate, request: Request):
    """用户注册"""
    # 检查是否为预览环境
    if not settings.IS_PREVIEW:
        check_preview()

    user = await UserService.create_user(user_data)
    return ResponseModel.success({"id": user.id, "username": user.username}, originUrl=request.url.path)


@router.get("/refresh-token", name="刷新用户 Token")
async def refresh_token(request: Request, current_user=Depends(get_current_active_user)):
    """刷新令牌"""
    token_data = await AuthService.login(current_user)
    return ResponseModel.success(token_data, originUrl=request.url.path)

@router.post("/logout", name="账号退出登录")
async def logout(request: Request, current_user=Depends(get_current_active_user)):
    """用户登出"""
    await AuthService.logout(current_user.id)
    return ResponseModel.success(message="登出成功", originUrl=request.url.path)


@router.get("/captcha", name="生成验证码")
async def create_captcha(request: Request):
    """生成验证码"""
    # 生成随机验证码
    captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

    # 创建验证码图片
    image = ImageCaptcha(width=160, height=60)
    captcha_image = image.generate(captcha_text)

    # 转换为base64
    captcha_bytes = io.BytesIO()
    captcha_image.seek(0)  # 确保从头开始读取
    captcha_bytes.write(captcha_image.read())
    captcha_bytes.seek(0)
    captcha_base64 = base64.b64encode(captcha_bytes.read()).decode('utf-8')

    return ResponseModel.success({
        "captcha": captcha_base64,
        "code": captcha_text
    }, originUrl=request.url.path)


@router.post("/password", name="用户修改密码")
async def change_password(
        password_data: PasswordUpdate,
        current_user=Depends(get_current_active_user),
):
    """修改密码"""
    # 检查是否为预览环境
    if not settings.IS_PREVIEW:
        check_preview()

    # 修改密码
    result = await AuthService.change_password(
        current_user.id,
        password_data.old_password,
        password_data.new_password
    )

    if result:
        # 修改密码后退出登录
        await AuthService.logout(current_user.id)
        return ResponseModel.success(message="密码修改成功", originUrl=request.url.path)

    raise CustomException(ErrorCode.ERR_10004)