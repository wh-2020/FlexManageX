"""
 @Author: Jason
 @Email: feisuqa@gmail.com
 @FileName: middleware
 @DateTime: 2025/3/9 11:35
 @SoftWare: PyCharm
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
from typing import Callable
import json


class RequestMiddleware(BaseHTTPMiddleware):
    """请求中间件"""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable):
        """处理请求"""
        # 记录开始时间
        start_time = time.time()

        # 保存原始路径
        request.state.originUrl = request.url.path

        # 处理请求
        response = await call_next(request)

        # 计算耗时（毫秒）
        elapsed_ms = round((time.time() - start_time) * 1000, 2)

        # 如果是JSON响应，添加原始路径和耗时
        if response.headers.get("content-type") == "application/json":
            try:
                body = b""
                async for chunk in response.body_iterator:
                    body += chunk

                response_data = json.loads(body.decode())

                # 添加原始路径和耗时
                if "originUrl" not in response_data:
                    response_data["originUrl"] = request.state.originUrl

                if "elapsed_ms" not in response_data:
                    response_data["elapsed_ms"] = elapsed_ms

                # 将数据转换为JSON字符串
                json_content = json.dumps(response_data)
                
                # 创建新的响应，不要手动设置 Content-Length，让 Response 自动处理
                new_response = Response(
                    content=json_content,
                    status_code=response.status_code,
                    media_type="application/json"
                )
                
                # 复制原始响应的头部，但不包括 content-length
                for name, value in response.headers.items():
                    if name.lower() != "content-length":
                        new_response.headers[name] = value
                
                return new_response
            except Exception as e:
                # 记录异常但继续处理
                print(f"处理响应时出错: {str(e)}")
                pass

        return response


from starlette.responses import Response