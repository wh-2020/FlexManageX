from typing import Any, Dict, Optional, Union
from fastapi.responses import JSONResponse
from fastapi import status
import time


class ResponseModel:
    """统一响应模型"""

    @staticmethod
    def success(
            data: Any = None,
            message: str = "OK",
            originUrl: str = None,
            elapsed_ms: Optional[float] = None,
            status_code: int = status.HTTP_200_OK
    ) -> Dict[str, Any]:
        """成功响应"""
        response = {
            "code": 0,
            "message": message,
            "data": data
        }

        if originUrl:
            response["originUrl"] = originUrl

        if elapsed_ms is not None:
            response["elapsed_ms"] = elapsed_ms

        return response

    @staticmethod
    def error(
            message: str = "操作失败",
            code: int = 1,
            originUrl: str = None,
            elapsed_ms: Optional[float] = None,
            status_code: int = status.HTTP_400_BAD_REQUEST
    ) -> Dict[str, Any]:
        """错误响应"""
        if status_code == status.HTTP_401_UNAUTHORIZED:
            code = 401  # 确保未授权错误 code 为 401

        response = {
            "code": code,
            "message": message,
            "data": None
        }

        if originUrl:
            response["originUrl"] = originUrl

        if elapsed_ms is not None:
            response["elapsed_ms"] = elapsed_ms

        return response


class CustomJSONResponse(JSONResponse):
    """自定义JSON响应"""

    def __init__(
            self,
            content: Any,
            status_code: int = status.HTTP_200_OK,
            headers: Optional[Dict[str, str]] = None,
            media_type: Optional[str] = None,
            background: Optional[Any] = None,
    ) -> None:
        super().__init__(content, status_code, headers, media_type, background)