from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.api import api_router
from app.core.config import settings
from app.db.init_db import init_db, close_db
from app.core.redis import redis_client
from app.utils.exceptions import CustomException, ErrorCode
from app.utils.response import ResponseModel
from app.utils.middleware import RequestMiddleware
import logging
from fastapi.encoders import jsonable_encoder
import json
from tortoise.contrib.fastapi import register_tortoise
from tortoise import Tortoise

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 自定义 JSON 编码器，确保中文字符正确显示
class ChineseJSONResponse(JSONResponse):
    def render(self, content) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,  # 不转义中文字符
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")

# 创建FastAPI应用
app = FastAPI(
    title="木头管理系统 API",
    description="后端API接口",
    version="0.0.1",
    default_response_class=ChineseJSONResponse,  # 使用自定义的响应类
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加请求中间件
app.add_middleware(RequestMiddleware)

# 注册路由
app.include_router(api_router, prefix="/api")


# 异常处理
@app.exception_handler(CustomException)
async def custom_exception_handler(request: Request, exc: CustomException):
    """自定义异常处理"""
    return ChineseJSONResponse(
        status_code=exc.status_code,
        content=ResponseModel.error(
            message=exc.detail,
            code=1,
            originUrl=request.url.path,
            status_code=exc.status_code
        ),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """请求验证异常处理"""
    errors = exc.errors()
    error_messages = []
    for error in errors:
        error_messages.append(f"{error['loc'][-1]}: {error['msg']}")

    return ChineseJSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ResponseModel.error(
            message="; ".join(error_messages),
            code=1,
            originUrl=request.url.path,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        ),
    )


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("应用程序启动中...")
    
    # 初始化数据库连接
    logger.info("初始化数据库连接...")
    await Tortoise.init(
        db_url=settings.DATABASE_URL,
        modules={"models": ["app.models"]},
    )
    
    # 生成数据库架构
    logger.info("生成数据库架构...")
    await Tortoise.generate_schemas()
    
    # 确保数据库已初始化
    logger.info("数据库初始化完成")
    
    # 连接Redis
    await redis_client.connect()
    
    logger.info("应用程序启动完成")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("应用程序关闭中...")
    
    # 关闭数据库连接
    logger.info("关闭数据库连接...")
    await Tortoise.close_connections()
    
    # 关闭Redis连接
    await redis_client.disconnect()
    
    logger.info("应用程序已关闭")


@app.get("/")
async def root():
    """根路径"""
    return {"message": "欢迎使用API"}


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok"}
