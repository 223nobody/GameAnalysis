"""
PUBG游戏建议生成服务。
基于DeepSeek AI生成专业的PUBG游戏策略建议。
"""

import json
import asyncio
from typing import Dict, Any
import httpx
from dataclasses import dataclass

from config.config import AIConfig


@dataclass
class AdviceRequest:
    """AI建议生成请求结构。"""
    keyword: str = "PUBG游戏建议"  # 固定关键字
    model: str = "deepseek"  # 固定使用deepseek模型


@dataclass
class AdviceResponse:
    """AI建议生成响应结构。"""
    content: str  # 生成的建议内容


DEEPSEEK_ENDPOINT = "https://ai.forestsx.top/v1"


class PubgAdviceService:
    """PUBG游戏建议生成服务。"""

    def __init__(self, api_key: str, timeout: int = 30):
        """
        初始化PUBG建议服务。

        Args:
            api_key: DeepSeek API密钥
            timeout: 请求超时时间（秒）
        """
        self.api_key = api_key
        self.timeout = timeout
        self.base_url = DEEPSEEK_ENDPOINT

    def _build_prompt(self) -> str:
        """
        构建PUBG游戏建议生成的提示词。

        Returns:
            str: 格式化的提示词
        """
        prompt = f"""
# 背景
你是一位职业级PUBG电竞选手，拥有超过5000小时实战经验。你需要为新玩家提供深度游戏策略建议。

# 任务
基于以下要求，撰写一份PUBG游戏进阶指南：
1. 篇幅约500字
2. 严格分4个大类（核心能力/战术决策/战斗细节/心态配合）
3. 每个大类下分3-5个具体建议点
4. 使用markdown符号分层（例：**1. 标题** → 具体说明）
5. 语言精炼专业，避免口语化词汇

# 内容要求
- 枪法训练：包含压枪、移动靶、近战技巧
- 战术决策：涵盖选点/转移/信息收集/劝架时机
- 战斗细节：强调投掷物/攻守楼/决赛圈处理
- 心态配合：突出耐心/沟通/复盘价值
- 禁用任何免责声明（如"仅供参考"）

# 输出示例（结构参照）
**1. 核心能力：锤炼硬实力**  
  *   **压枪控镜**：练习M416配3倍镜扫射...  
  *   **听声辨位**：通过耳机判断枪声方向...  
（后续结构类同）
"""
        return prompt.strip()

    async def generate_advice(self, request: AdviceRequest) -> AdviceResponse:
        """
        使用DeepSeek API生成PUBG游戏建议。

        Args:
            request: 建议生成请求

        Returns:
            AdviceResponse: 生成的建议内容

        Raises:
            ValueError: 如果API调用失败
        """
        prompt = self._build_prompt()

        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": "你是一位职业级PUBG电竞选手和游戏策略专家，专门为玩家提供专业的游戏建议和策略指导。请直接返回建议内容，不要使用markdown代码块包装。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,  # 稍高的温度以获得更有创意的建议
            "max_tokens": 1500   # 增加token数量以支持更详细的建议
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        max_retries = 3
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        json=payload,
                        headers=headers
                    )
                    response.raise_for_status()

                    result = response.json()
                    content = result["choices"][0]["message"]["content"]

                    return AdviceResponse(content=content.strip())

            except (httpx.HTTPError, KeyError, json.JSONDecodeError) as e:
                if attempt == max_retries - 1:
                    raise ValueError(f"AI建议生成失败（尝试{max_retries}次）：{e}")

                # 重试前等待
                await asyncio.sleep((attempt + 1) * 2)
                continue


def create_pubg_advice_service(config: AIConfig) -> PubgAdviceService:
    """
    创建PUBG建议服务实例的工厂函数。

    Args:
        config: AI配置

    Returns:
        PubgAdviceService: 配置好的PUBG建议服务实例
    """
    return PubgAdviceService(config.deepseek_key, config.timeout)
