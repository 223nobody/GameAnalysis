"""
AI生成题目端点的题目控制器。
处理题目生成和批量操作。
"""

import time
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from app.config.config import QuestionRequest, validate_question_request
from app.services.client import AIService
from app.storage.database import Database
from app.api.response import success_response, error_response


class QuestionGenerationRequest(BaseModel):
    """AI题目生成的请求模型。"""
    keyword: str = Field(..., description="关键字")
    model: str = Field("tongyi", description="AI模型")
    language: str = Field("go", description="编程语言")
    count: int = Field(3, ge=3, le=10, description="题目数量")
    type: int = Field(1, ge=1, le=3, description="题目类型")


class BatchInsertRequest(BaseModel):
    """批量插入题目的请求模型。"""
    questions: List[Dict[str, Any]] = Field(..., description="题目列表")


class QuestionController:
    """题目相关操作的控制器。"""

    def __init__(self, ai_service: AIService, database: Database):
        """
        初始化题目控制器。

        Args:
            ai_service: AI服务实例
            database: 数据库实例
        """
        self.ai_service = ai_service
        self.database = database
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        """设置API路由。"""
        self.router.post("/CreateByAI")(self.generate_question)
        self.router.post("/batch-insert")(self.add_questions)
    
    async def generate_question(self, request: QuestionGenerationRequest):
        """
        使用AI服务生成题目。

        Args:
            request: 题目生成请求

        Returns:
            生成的题目响应
        """
        start_time = time.time()

        try:
            # 转换为内部请求格式
            ai_request = QuestionRequest(
                keyword=request.keyword,
                model=request.model,
                language=request.language,
                count=request.count,
                type=request.type
            )

            # 验证请求
            ai_request = validate_question_request(ai_request)

            # 使用AI服务生成题目
            response = await self.ai_service.generate_question(ai_request)

            # 注意：根据要求排除日志功能

            return success_response({
                "aiRes": {
                    "questions": [
                        {
                            "title": q.title,
                            "answers": q.answers,
                            "rights": q.rights
                        }
                        for q in response.questions
                    ]
                }
            })

        except ValueError as e:
            raise error_response(f"参数错误: {str(e)}", 400)
        except Exception as e:
            raise error_response(f"生成失败: {str(e)}", 500)
    
    async def add_questions(self, request: BatchInsertRequest):
        """
        批量插入题目到数据库。

        Args:
            request: 批量插入请求

        Returns:
            成功响应
        """
        try:
            # 验证题目格式
            for i, question in enumerate(request.questions):
                required_fields = ["type", "title", "language", "answers", "rights"]
                for field in required_fields:
                    if field not in question:
                        raise ValueError(f"题目 {i+1} 缺少必需字段: {field}")

                # 验证题目类型
                if question["type"] not in [1, 2, 3]:
                    raise ValueError(f"题目 {i+1} 类型无效")

                # 验证答案格式
                if not isinstance(question["answers"], list):
                    raise ValueError(f"题目 {i+1} 选项格式错误")

                if not isinstance(question["rights"], list):
                    raise ValueError(f"题目 {i+1} 答案格式错误")

            # 批量插入题目
            await self.database.batch_insert_questions(request.questions)

            return success_response(None, "添加成功")

        except ValueError as e:
            raise error_response(f"参数错误: {str(e)}", 400)
        except Exception as e:
            raise error_response(f"存储失败: {str(e)}", 500)


def create_question_controller(ai_service: AIService, database: Database) -> APIRouter:
    """
    创建题目控制器路由的工厂函数。

    Args:
        ai_service: AI服务实例
        database: 数据库实例

    Returns:
        配置好的APIRouter
    """
    controller = QuestionController(ai_service, database)
    return controller.router
