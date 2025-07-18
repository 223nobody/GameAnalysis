"""
API响应工具模块，用于统一的响应格式化。
"""

from typing import Any, Dict
from fastapi import HTTPException
from fastapi.responses import JSONResponse


def success_response(data: Any = None, message: str = "success") -> JSONResponse:
    """
    创建成功的JSON响应。

    Args:
        data: 响应数据
        message: 成功消息

    Returns:
        成功格式的JSONResponse
    """
    return JSONResponse(
        status_code=200,
        content={
            "code": 0,
            "msg": message,
            "data": data
        }
    )


def error_response(message: str, status_code: int = 400, error_code: int = -1) -> HTTPException:
    """
    创建错误的HTTP异常。

    Args:
        message: 错误消息
        status_code: HTTP状态码
        error_code: 应用错误代码

    Returns:
        错误格式的HTTPException
    """
    return HTTPException(
        status_code=status_code,
        detail={
            "code": error_code,
            "msg": message,
            "data": None
        }
    )
