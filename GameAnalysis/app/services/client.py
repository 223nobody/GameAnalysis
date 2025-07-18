"""
AI服务客户端接口和实现。
为不同的AI提供商提供统一接口。
"""

from abc import ABC, abstractmethod
from typing import Optional

from app.config.config import AIConfig, QuestionRequest, QuestionResponses, validate_question_request
from app.services.deepseek import DeepSeekClient


class AIService(ABC):
    """AI服务的抽象基类。"""

    @abstractmethod
    async def generate_question(self, req: QuestionRequest) -> QuestionResponses:
        """使用AI服务生成题目。"""
        pass


class AIServiceImpl(AIService):
    """支持多个提供商的AI服务实现。"""

    def __init__(self, config: AIConfig):
        """
        使用配置初始化AI服务。

        Args:
            config: 包含API密钥和设置的AI配置
        """
        self.deepseek: Optional[DeepSeekClient] = None

        # 初始化可用的客户端
        if config.deepseek_key:
            self.deepseek = DeepSeekClient(config.deepseek_key, config.timeout)

    async def generate_question(self, req: QuestionRequest) -> QuestionResponses:
        """
        使用指定的AI模型生成题目。

        Args:
            req: 题目生成请求

        Returns:
            QuestionResponses: 生成的题目

        Raises:
            ValueError: 如果模型不受支持或未配置
        """
        # 验证并设置默认值
        req = validate_question_request(req)

        # 路由到适当的服务
        if req.model == "deepseek" or req.model == "":
            if not self.deepseek:
                raise ValueError("DeepSeek API密钥未配置")
            return await self.deepseek.generate(req)

        else:
            raise ValueError("不支持的AI模型")


def create_ai_service(config: AIConfig) -> AIService:
    """
    创建AI服务实例的工厂函数。

    Args:
        config: AI配置

    Returns:
        AIService: 配置好的AI服务实例
    """
    return AIServiceImpl(config)
