"""
题目服务的数据库操作模块。
处理SQLite数据库连接和CRUD操作。
"""

import json
import sqlite3
from typing import List, Dict, Any, Optional, Tuple
from contextlib import asynccontextmanager
import aiosqlite




CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    type INTEGER NOT NULL,
    language TEXT NOT NULL,
    answers TEXT NOT NULL,
    rights TEXT NOT NULL
);
"""


class Database:
    """SQLite操作的数据库包装器。"""

    def __init__(self, db_path: str):
        """
        初始化数据库连接。

        Args:
            db_path: SQLite数据库文件路径
        """
        self.db_path = db_path

    async def init_db(self) -> None:
        """初始化数据库并创建表。"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(CREATE_TABLE_SQL)
            await db.commit()

    async def close(self) -> None:
        """关闭数据库连接（兼容性占位符）。"""
        pass
    
    @asynccontextmanager
    async def get_connection(self):
        """获取数据库连接上下文管理器。"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            yield db

    async def select(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        执行SELECT查询并返回结果。

        Args:
            query: SQL查询字符串
            params: 查询参数

        Returns:
            表示行的字典列表
        """
        async with self.get_connection() as db:
            cursor = await db.execute(query, params)
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """
        执行SELECT查询并返回单个结果。

        Args:
            query: SQL查询字符串
            params: 查询参数

        Returns:
            表示单行的字典或None
        """
        async with self.get_connection() as db:
            cursor = await db.execute(query, params)
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def execute(self, query: str, params: tuple = ()) -> int:
        """
        执行INSERT/UPDATE/DELETE查询。

        Args:
            query: SQL查询字符串
            params: 查询参数

        Returns:
            受影响的行数
        """
        async with self.get_connection() as db:
            cursor = await db.execute(query, params)
            await db.commit()
            return cursor.rowcount

    async def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """
        使用多个参数集执行查询。

        Args:
            query: SQL查询字符串
            params_list: 参数元组列表

        Returns:
            受影响的行数
        """
        async with self.get_connection() as db:
            cursor = await db.executemany(query, params_list)
            await db.commit()
            return cursor.rowcount
    

    
    async def batch_insert_questions(self, questions: List[Dict[str, Any]]) -> None:
        """
        批量插入多个题目。

        Args:
            questions: 题目字典列表

        Raises:
            ValueError: 如果批量插入失败
        """
        query = """
        INSERT INTO questions (type, title, language, answers, rights)
        VALUES (?, ?, ?, ?, ?)
        """

        params_list = []
        for q in questions:
            answers_json = json.dumps(q["answers"], ensure_ascii=False)
            rights_json = json.dumps(q["rights"], ensure_ascii=False)

            params_list.append((
                q["type"],
                q["title"],
                q["language"],
                answers_json,
                rights_json
            ))

        async with self.get_connection() as db:
            await db.executemany(query, params_list)
            await db.commit()

    async def batch_delete_questions(self, question_ids: List[int]) -> int:
        """
        根据ID批量删除题目。

        Args:
            question_ids: 要删除的题目ID列表

        Returns:
            删除的行数
        """
        if not question_ids:
            return 0

        placeholders = ",".join("?" * len(question_ids))
        query = f"DELETE FROM questions WHERE id IN ({placeholders})"

        return await self.execute(query, tuple(question_ids))
    
    async def get_questions_paginated(
        self,
        page: int = 1,
        page_size: int = 10,
        search: str = "",
        question_type: Optional[int] = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        获取分页题目，支持可选的搜索和类型过滤。

        Args:
            page: 页码（从1开始）
            page_size: 每页项目数
            search: 标题搜索词
            question_type: 按题目类型过滤

        Returns:
            (题目列表, 总数)的元组
        """
        # 构建WHERE条件
        conditions = []
        params = []

        if question_type is not None:
            conditions.append("type = ?")
            params.append(question_type)

        if search:
            conditions.append("title LIKE ?")
            params.append(f"%{search}%")

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        # 获取总数
        count_query = f"SELECT COUNT(*) as count FROM questions {where_clause}"
        count_result = await self.get(count_query, tuple(params))
        total = count_result["count"] if count_result else 0

        # 获取分页数据
        offset = (page - 1) * page_size
        data_query = f"""
        SELECT id, title, type
        FROM questions {where_clause}
        ORDER BY id DESC
        LIMIT ? OFFSET ?
        """

        params.extend([page_size, offset])
        questions = await self.select(data_query, tuple(params))

        return questions, total
    



async def init_database(db_path: str) -> Database:
    """
    初始化数据库并返回Database实例。

    Args:
        db_path: SQLite数据库文件路径

    Returns:
        初始化的Database实例
    """
    db = Database(db_path)
    await db.init_db()
    return db
