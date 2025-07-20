"""
PUBG预测历史数据库模块
处理SQLite数据库连接、初始化和操作
"""

import sqlite3
import os
from typing import List, Dict, Tuple
import logging
import math

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 数据库表结构常量
CREATE_HISTORY_TABLE_SQL = '''
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sumpeople INTEGER NOT NULL CHECK (sumpeople BETWEEN 50 AND 100),
        sumkill INTEGER NOT NULL CHECK (sumkill BETWEEN 0 AND 50),
        sumfall INTEGER NOT NULL CHECK (sumfall BETWEEN 0 AND 50),
        sumdist_ride INTEGER NOT NULL,
        sumdist_walk INTEGER NOT NULL,
        teamsize INTEGER NOT NULL CHECK (teamsize BETWEEN 1 AND 4),
        survival_time INTEGER NOT NULL,
        damage INTEGER NOT NULL,
        assist INTEGER NOT NULL,
        result FLOAT NOT NULL,
        confidence TEXT NOT NULL,
        tactics TEXT
    )
'''

class HistoryDatabase:
    """预测历史数据库管理类"""

    def __init__(self, db_path: str = "history_service.db"):
        """
        初始化数据库连接

        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.init_database()

    def _get_connection(self):
        """获取数据库连接的上下文管理器"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """初始化数据库表结构"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # 创建预测历史表
                cursor.execute(CREATE_HISTORY_TABLE_SQL)

                conn.commit()
                logger.info("数据库表结构初始化完成")

        except sqlite3.Error as e:
            logger.error(f"数据库初始化失败: {e}")
            raise
    
    def save_prediction(self, prediction_data: Dict, result_data: Dict, tactics: str = None) -> int:
        """
        保存预测结果到数据库

        Args:
            prediction_data: 预测输入数据
            result_data: 预测结果数据
            tactics: 游戏策略（可选，默认为None）

        Returns:
            插入记录的ID
        """
        try:
            # 映射和验证数据
            insert_data = self._map_prediction_data(prediction_data, result_data, tactics)

            with self._get_connection() as conn:
                cursor = conn.cursor()

                # 插入数据
                cursor.execute('''
                    INSERT INTO history (
                        sumpeople, sumkill, sumfall, sumdist_ride, sumdist_walk,
                        teamsize, survival_time, damage, assist, result, confidence, tactics
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', tuple(insert_data.values()))

                record_id = cursor.lastrowid
                conn.commit()

                logger.info(f"预测记录保存成功，ID: {record_id}")
                return record_id

        except sqlite3.Error as e:
            logger.error(f"保存预测记录失败: {e}")
            raise
        except (KeyError, ValueError) as e:
            logger.error(f"数据格式错误: {e}")
            raise

    def _map_prediction_data(self, prediction_data: Dict, result_data: Dict, tactics: str = None) -> Dict:
        """映射预测数据到数据库字段"""
        return {
            'sumpeople': int(prediction_data['game_size']),
            'sumkill': int(prediction_data['player_kills']),
            'sumfall': int(prediction_data['player_dbno']),
            'sumdist_ride': int(prediction_data['player_dist_ride']),
            'sumdist_walk': int(prediction_data['player_dist_walk']),
            'teamsize': int(prediction_data['party_size']),
            'survival_time': int(prediction_data['player_survive_time']),
            'damage': int(prediction_data['player_dmg']),
            'assist': int(prediction_data['player_assists']),
            'result': float(result_data['percentage']),
            'confidence': str(result_data['confidence']),
            'tactics': tactics
        }

    def update_tactics(self, record_id: int, tactics: str) -> bool:
        """
        更新指定记录的tactics字段

        Args:
            record_id: 记录ID
            tactics: 新的策略内容

        Returns:
            bool: 更新是否成功
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # 更新tactics字段
                cursor.execute('''
                    UPDATE history
                    SET tactics = ?
                    WHERE id = ?
                ''', (tactics, record_id))

                conn.commit()

                if cursor.rowcount > 0:
                    logger.info(f"记录ID {record_id} 的tactics字段更新成功")
                    return True
                else:
                    logger.warning(f"记录ID {record_id} 不存在或更新失败")
                    return False

        except sqlite3.Error as e:
            logger.error(f"更新tactics字段失败: {e}")
            return False

    def save_ai_advice(self, advice_content: str) -> int:
        """
        保存AI建议到数据库

        Args:
            advice_content: AI生成的建议内容

        Returns:
            插入记录的ID
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # 创建一个专门用于AI建议的记录，使用默认值填充必需字段
                ai_advice_data = (
                    50,  # sumpeople - 使用最小允许值50表示这是AI建议记录
                    0,   # sumkill
                    0,   # sumfall
                    0,   # sumdist_ride
                    0,   # sumdist_walk
                    1,   # teamsize - 使用最小允许值1
                    0,   # survival_time
                    0,   # damage
                    0,   # assist
                    0.0, # result
                    "AI建议",  # confidence - 标识这是AI建议
                    advice_content  # tactics - 存储AI建议内容
                )

                cursor.execute('''
                    INSERT INTO history (
                        sumpeople, sumkill, sumfall, sumdist_ride, sumdist_walk,
                        teamsize, survival_time, damage, assist, result, confidence, tactics
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', ai_advice_data)

                record_id = cursor.lastrowid
                conn.commit()

                logger.info(f"AI建议保存成功，ID: {record_id}")
                return record_id

        except sqlite3.Error as e:
            logger.error(f"保存AI建议失败: {e}")
            raise

    def get_history_paginated(self, page: int = 1, per_page: int = 10) -> Tuple[List[Dict], Dict]:
        """
        获取分页的预测历史记录
        
        Args:
            page: 页码（从1开始）
            per_page: 每页记录数
            
        Returns:
            (历史记录列表, 分页信息字典)
        """
        try:
            # 参数验证
            if page < 1:
                page = 1
            if per_page < 1:
                per_page = 10
            if per_page > 100:
                per_page = 100
                
            offset = (page - 1) * per_page
            
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # 获取总记录数
                cursor.execute('SELECT COUNT(*) FROM history')
                total_items = cursor.fetchone()[0]

                # 计算分页信息
                total_pages = math.ceil(total_items / per_page) if total_items > 0 else 1
                has_prev = page > 1
                has_next = page < total_pages

                # 获取当前页数据
                cursor.execute('''
                    SELECT * FROM history
                    ORDER BY id DESC
                    LIMIT ? OFFSET ?
                ''', (per_page, offset))

                rows = cursor.fetchall()

                # 转换为字典列表（使用列表推导式优化）
                history = [dict(row) for row in rows]
                
                # 分页信息
                pagination_info = {
                    'current_page': page,
                    'per_page': per_page,
                    'total_pages': total_pages,
                    'total_items': total_items,
                    'has_prev': has_prev,
                    'has_next': has_next,
                    'prev_page': page - 1 if has_prev else None,
                    'next_page': page + 1 if has_next else None
                }
                
                logger.info(f"获取分页历史记录成功，页码: {page}, 数量: {len(history)}")
                return history, pagination_info
                
        except sqlite3.Error as e:
            logger.error(f"获取分页历史记录失败: {e}")
            raise
    
    def get_history(self, limit: int = 50, offset: int = 0) -> List[Dict]:
        """
        获取预测历史记录（保持向后兼容）

        Args:
            limit: 返回记录数量限制
            offset: 偏移量

        Returns:
            预测历史记录列表
        """
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute('''
                    SELECT * FROM history
                    ORDER BY id DESC
                    LIMIT ? OFFSET ?
                ''', (limit, offset))

                rows = cursor.fetchall()
                history = [dict(row) for row in rows]

                logger.info(f"获取历史记录成功，数量: {len(history)}")
                return history

        except sqlite3.Error as e:
            logger.error(f"获取历史记录失败: {e}")
            raise
    
    def get_history_count(self) -> int:
        """
        获取历史记录总数

        Returns:
            历史记录总数
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM history')
                return cursor.fetchone()[0]

        except sqlite3.Error as e:
            logger.error(f"获取历史记录总数失败: {e}")
            raise

    def get_statistics(self) -> Dict:
        """
        获取预测统计信息

        Returns:
            统计信息字典
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # 获取基本统计
                cursor.execute('''
                    SELECT
                        COUNT(*) as total_predictions,
                        AVG(result) as avg_win_rate,
                        MAX(result) as max_win_rate,
                        MIN(result) as min_win_rate,
                        COUNT(CASE WHEN confidence = 'high' THEN 1 END) as high_confidence,
                        COUNT(CASE WHEN confidence = 'medium' THEN 1 END) as medium_confidence,
                        COUNT(CASE WHEN confidence = 'low' THEN 1 END) as low_confidence
                    FROM history
                ''')

                stats = cursor.fetchone()

                result = {
                    'total_predictions': stats[0],
                    'avg_win_rate': round(stats[1], 2) if stats[1] else 0,
                    'max_win_rate': stats[2] if stats[2] else 0,
                    'min_win_rate': stats[3] if stats[3] else 0,
                    'confidence_distribution': {
                        'high': stats[4],
                        'medium': stats[5],
                        'low': stats[6]
                    }
                }

                logger.info("获取统计信息成功")
                return result

        except sqlite3.Error as e:
            logger.error(f"获取统计信息失败: {e}")
            raise
    
    def delete_history(self, record_id: int) -> bool:
        """
        删除指定的历史记录

        Args:
            record_id: 记录ID

        Returns:
            删除是否成功
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM history WHERE id = ?', (record_id,))

                if cursor.rowcount > 0:
                    conn.commit()
                    logger.info(f"删除历史记录成功，ID: {record_id}")
                    return True
                else:
                    logger.warning(f"未找到要删除的记录，ID: {record_id}")
                    return False

        except sqlite3.Error as e:
            logger.error(f"删除历史记录失败: {e}")
            raise
    
    def close(self):
        """关闭数据库连接（SQLite自动管理连接，此方法为兼容性保留）"""
        logger.info("数据库连接已关闭")


# 全局数据库实例
history_db = None

def get_history_database() -> HistoryDatabase:
    """获取历史数据库实例"""
    global history_db
    if history_db is None:
        # 数据库文件放在app目录下
        db_path = os.path.join(os.path.dirname(__file__), '..', 'history_service.db')
        history_db = HistoryDatabase(db_path)
    return history_db
