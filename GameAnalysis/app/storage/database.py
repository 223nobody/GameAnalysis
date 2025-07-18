"""
PUBG预测历史数据库模块
处理SQLite数据库连接、初始化和操作
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Tuple
import logging
import math

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    
    def init_database(self):
        """初始化数据库表结构"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 创建预测历史表
                cursor.execute('''
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
                        url TEXT,
                        tactics TEXT NOT NULL
                    )
                ''')
                
                conn.commit()
                logger.info("数据库表初始化成功")
                
        except sqlite3.Error as e:
            logger.error(f"数据库初始化失败: {e}")
            raise
    
    def save_prediction(self, prediction_data: Dict, result_data: Dict, tactics: str = "稳健策略") -> int:
        """
        保存预测结果到数据库

        Args:
            prediction_data: 预测输入数据
            result_data: 预测结果数据
            tactics: 游戏策略

        Returns:
            插入记录的ID
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 映射字段名
                insert_data = {
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
                    'url': None,
                    'tactics': tactics
                }

                # 插入数据
                cursor.execute('''
                    INSERT INTO history (
                        sumpeople, sumkill, sumfall, sumdist_ride, sumdist_walk,
                        teamsize, survival_time, damage, assist, result, confidence, url, tactics
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    insert_data['sumpeople'], insert_data['sumkill'], insert_data['sumfall'],
                    insert_data['sumdist_ride'], insert_data['sumdist_walk'], insert_data['teamsize'],
                    insert_data['survival_time'], insert_data['damage'], insert_data['assist'],
                    insert_data['result'], insert_data['confidence'], insert_data['url'], insert_data['tactics']
                ))
                
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
    
    def get_history_paginated(self, page: int = 1, per_page: int = 20) -> Tuple[List[Dict], Dict]:
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
                per_page = 20
            if per_page > 100:
                per_page = 100
                
            offset = (page - 1) * per_page
            
            with sqlite3.connect(self.db_path) as conn:
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
                
                # 转换为字典列表
                history = []
                for row in rows:
                    record = dict(row)
                    history.append(record)
                
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
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM history
                    ORDER BY id DESC
                    LIMIT ? OFFSET ?
                ''', (limit, offset))
                
                rows = cursor.fetchall()
                
                # 转换为字典列表
                history = []
                for row in rows:
                    record = dict(row)
                    history.append(record)
                
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
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM history')
                count = cursor.fetchone()[0]
                return count
                
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
            with sqlite3.connect(self.db_path) as conn:
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
            with sqlite3.connect(self.db_path) as conn:
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
