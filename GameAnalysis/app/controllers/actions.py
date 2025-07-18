"""
题目管理和统计的操作控制器。
处理CRUD操作和数据检索。
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.config.config import QuestionRequest1, validate_question_request1
from app.storage.database import Database
from app.api.response import success_response, error_response


class PageRequest(BaseModel):
    """分页请求模型。"""
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(10, ge=1, le=100, description="每页大小")
    search: str = Field("", description="搜索关键词")


class DeleteRequest(BaseModel):
    """批量删除请求模型。"""
    ids: List[int] = Field(..., min_items=1, description="要删除的ID列表")


class ActionsController:
    """题目管理操作的控制器。"""

    def __init__(self, database: Database):

        self.database = database
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """设置API路由。"""
        self.router.get("/summary")(self.summary)
        self.router.delete("/batch-delete")(self.batch_delete)

    async def _handle_pagination(
        self,
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=100),
        search: str = Query(""),
        question_type: Optional[int] = None
    ):
        """
        处理分页题目检索。

        Args:
            page: 页码
            page_size: 每页项目数
            search: 搜索词
            question_type: 按题目类型过滤

        Returns:
            分页响应
        """
        try:
            # 添加调试日志
            print(f"DEBUG: _handle_pagination called with page={page}, page_size={page_size}, search='{search}', question_type={question_type}")
            print(f"DEBUG: Database instance: {self.database}")

            questions, total = await self.database.get_questions_paginated(
                page=page,
                page_size=page_size,
                search=search,
                question_type=question_type
            )

            print(f"DEBUG: Database returned total={total}, questions_count={len(questions)}")
            print(f"DEBUG: First few questions: {questions[:2] if questions else 'None'}")

            response_data = {
                "total": total,
                "questions": questions
            }

            print(f"DEBUG: Response data: {response_data}")

            return success_response(response_data)

        except Exception as e:
            print(f"DEBUG: Exception in _handle_pagination: {e}")
            import traceback
            traceback.print_exc()
            raise error_response(f"获取数据失败: {str(e)}", 500)
    
    async def summary(
        self,
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=100),
        search: str = Query("")
    ):
        """获取所有题目（分页）。"""
        return await self._handle_pagination(page, page_size, search)

    
    async def batch_delete(self, request: DeleteRequest):
        """
        批量删除题目。

        Args:
            request: 包含题目ID的删除请求

        Returns:
            删除成功响应
        """
        try:
            deleted_count = await self.database.batch_delete_questions(request.ids)

            return success_response({
                "deleted_ids": request.ids,
                "message": "删除成功",
                "deleted_count": deleted_count
            })

        except Exception as e:
            raise error_response(f"删除操作失败: {str(e)}", 500)


def create_actions_controller(database: Database) -> APIRouter:
    """
    创建操作控制器路由的工厂函数。

    Args:
        database: 数据库实例

    Returns:
        配置好的APIRouter
    """
    controller = ActionsController(database)
    return controller.router
