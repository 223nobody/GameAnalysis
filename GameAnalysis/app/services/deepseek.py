"""
DeepSeek AI服务客户端实现。
处理与DeepSeek API的通信以生成题目。
"""

import json
import asyncio
from typing import Dict, Any, List
import httpx

from app.config.config import (
    QuestionRequest, QuestionResponses, QuestionResponse,
    SINGLE_SELECT, MULTI_SELECT, CODING
)


DEEPSEEK_ENDPOINT = "https://ai.forestsx.top/v1"


class DeepSeekClient:
    """DeepSeek AI API的客户端。"""

    def __init__(self, api_key: str, timeout: int = 30):
        """
        初始化DeepSeek客户端。

        Args:
            api_key: DeepSeek API密钥
            timeout: 请求超时时间（秒）
        """
        self.api_key = api_key
        self.timeout = timeout
        self.base_url = DEEPSEEK_ENDPOINT

    def _build_prompt(self, req: QuestionRequest) -> str:
        """
        基于请求构建DeepSeek API的提示词。

        Args:
            req: 题目生成请求

        Returns:
            str: 格式化的提示词
        """
        prompt_parts = [
            f"请生成【{req.count}】道关于【{req.keyword}】的编程题，要求如下：",
            f"- 编程语言：{req.language}",
            f"- 题目类型：{self._get_question_type_text(req.type)}"
        ]

        if req.type == SINGLE_SELECT:
            prompt_parts.append("- 必须且仅有一个正确答案，答案字母需从A/B/C/D中选择")
        elif req.type == MULTI_SELECT:
            prompt_parts.append("- 正确答案数量需在2-4个之间，答案字母必须按A、B、C、D顺序排列且没有重复字母出现")
        else:
            prompt_parts.append("- 不需要生成选项和答案，同时必须将answers和rights设为null")

        prompt_parts.append("\n请严格遵循以下JSON格式：")

        # 根据题目类型添加示例
        if req.type == SINGLE_SELECT:
            example = '''[
    {
        "title": "关于Golang并发的说法哪个正确？",
        "answers": [
            "A: channel只能传递基本数据类型",
            "B: sync.Mutex适用于读多写少场景",
            "C: WaitGroup的Add()必须在goroutine外调用",
            "D: map的并发读写需要加锁"
        ],
        "rights": ["D"]
    }
]'''
        elif req.type == MULTI_SELECT:
            example = '''[
    {
        "title": "下面有关Python列表操作相关说法正确的是？",
        "answers": [
            "A: 列表推导式比for循环效率更高",
            "B: 切片操作会创建新对象",
            "C: append()会直接修改原列表",
            "D: 列表可以作为字典的键"
        ],
        "rights": ["A","B"]
    }
]'''
        else:
            example = '''[
    {
        "title": "请设计C语言中的DFS算法应该怎么写？",
        "answers": null,
        "rights": null
    }
]'''
        
        prompt_parts.append(example)
        
        prompt_parts.extend([
            "\n❗❗必须遵守：",
            "1. 多选题答案必须按A、B、C、D顺序排列",
            "2. 单选题必须只能有一个答案",
            "3. 答案字母必须唯一",
            "4. 选项前缀严格按顺序生成",
            "5. 保证题目和选项不重复",
            "6. 生成题目title必须是提问句,以？结尾"
        ])
        
        return "\n".join(prompt_parts)
    
    def _get_question_type_text(self, question_type: int) -> str:
        """获取人类可读的题目类型文本。"""
        if question_type == MULTI_SELECT:
            return "多选题"
        elif question_type == SINGLE_SELECT:
            return "单选题"
        return "编程题"

    def _parse_response(self, content: str, req: QuestionRequest) -> QuestionResponses:
        """
        解析DeepSeek API响应。

        Args:
            content: 原始响应内容
            req: 用于验证的原始请求

        Returns:
            QuestionResponses: 解析后的题目

        Raises:
            ValueError: 如果响应格式无效
        """
        content = content.strip()

        # 处理可能包含markdown代码块的响应
        if content.startswith("```json"):
            # 提取JSON内容
            start = content.find("```json") + 7
            end = content.rfind("```")
            if end > start:
                content = content[start:end].strip()
        elif content.startswith("```"):
            # 处理其他类型的代码块
            start = content.find("```") + 3
            end = content.rfind("```")
            if end > start:
                content = content[start:end].strip()

        if not content.startswith("[") or not content.endswith("]"):
            raise ValueError("响应内容不是有效的JSON数组")

        try:
            items = json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"响应解析失败: {e}")

        if len(items) != req.count:
            raise ValueError(f"题目数量错误，预期 {req.count} 道，实际 {len(items)} 道")

        questions = []
        for item in items:
            # 验证必需字段
            if "title" not in item:
                raise ValueError("缺少题目标题")

            answers = item.get("answers", [])
            rights = item.get("rights", [])

            # 验证非编程题的答案和选项
            if req.type in [SINGLE_SELECT, MULTI_SELECT]:
                if len(answers) != 4:
                    raise ValueError("选择题必须有4个选项")

                # 验证选项前缀
                for i, answer in enumerate(answers):
                    expected_prefix = f"{chr(ord('A') + i)}:"
                    if not answer.startswith(expected_prefix):
                        raise ValueError(f"选项 {i+1} 前缀错误，应以 '{expected_prefix}' 开头")

                # 验证答案
                if len(set(rights)) != len(rights):
                    raise ValueError("答案重复")

                if req.type == MULTI_SELECT:
                    sorted_rights = sorted(rights)
                    if sorted_rights != rights:
                        raise ValueError(f"答案必须按字母顺序排列，当前顺序：{rights}")

            questions.append(QuestionResponse(
                title=item["title"],
                answers=answers,
                rights=rights
            ))

        return QuestionResponses(questions=questions)
    
    async def generate(self, req: QuestionRequest) -> QuestionResponses:
        """
        使用DeepSeek API生成题目。

        Args:
            req: 题目生成请求

        Returns:
            QuestionResponses: 生成的题目

        Raises:
            ValueError: 如果请求无效或API调用失败
        """
        if not req.keyword:
            raise ValueError("关键字不能为空")

        if req.type != CODING and not req.language:
            raise ValueError("编程语言必须指定")

        if req.count > 10:
            raise ValueError("单次生成题目数量不能超过10道")

        prompt = self._build_prompt(req)

        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个非常专业的编程题库生成助手，严格遵循用户的格式要求，请直接返回JSON格式，不要使用markdown代码块"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 2000
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

                    return self._parse_response(content, req)

            except (httpx.HTTPError, KeyError, json.JSONDecodeError) as e:
                if attempt == max_retries - 1:
                    raise ValueError(f"API请求失败（尝试{max_retries}次）：{e}")

                # 重试前等待
                await asyncio.sleep((attempt + 1) * 2)
                continue
