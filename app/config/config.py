"""
PUBG游戏分析应用的配置管理模块。
处理环境变量和应用程序设置。
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass
class AIConfig:
    """AI服务配置。"""
    deepseek_key: str
    timeout: int = 30  # 超时时间（秒）


def load_config() -> AIConfig:
    """
    从环境变量加载配置。

    Returns:
        AIConfig: 包含API密钥和设置的配置对象

    Raises:
        ValueError: 如果DeepSeek API密钥未配置
    """
    # 如果存在.env文件则加载
    load_dotenv()

    deepseek_key = os.getenv("DEEPSEEK_API_KEY", "")
    timeout = int(os.getenv("API_TIMEOUT", "30"))

    # DeepSeek API密钥必须配置
    if not deepseek_key:
        raise ValueError("必须配置DeepSeek API密钥（DEEPSEEK_API_KEY）")

    return AIConfig(
        deepseek_key=deepseek_key,
        timeout=timeout
    )
