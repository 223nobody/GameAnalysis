"""
问题服务API的配置管理模块。
处理环境变量和应用程序设置。
"""

import os
from typing import List, Optional
from dataclasses import dataclass
from dotenv import load_dotenv


# 题目类型常量
SINGLE_SELECT = 1
MULTI_SELECT = 2
CODING = 3


@dataclass
class AIConfig:
    """AI服务配置。"""
    deepseek_key: str
    timeout: int = 30  # 超时时间（秒）


@dataclass
class QuestionRequest:
    """AI题目生成请求结构。"""
    keyword: str
    model: Optional[str] = None  # "deepseek"，默认为"deepseek"
    language: Optional[str] = None  # 编程语言，默认为"go"
    count: Optional[int] = None  # 题目数量，默认为3
    type: Optional[int] = None  # 题目类型，默认为1


@dataclass
class QuestionResponse:
    """单个题目的响应结构。"""
    title: str
    answers: List[str]
    rights: List[str]


@dataclass
class QuestionResponses:
    """多个题目的响应结构。"""
    questions: List[QuestionResponse]


@dataclass
class QuestionRequest1:
    """手动创建/更新题目的请求结构。"""
    id: Optional[int] = None
    type: int = SINGLE_SELECT
    title: str = ""
    language: str = ""
    answers: List[str] = None
    rights: List[str] = None

    def __post_init__(self):
        if self.answers is None:
            self.answers = []
        if self.rights is None:
            self.rights = []


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


def validate_question_request(req: QuestionRequest) -> QuestionRequest:
    """
    验证题目请求并设置默认值。

    Args:
        req: 要验证的题目请求

    Returns:
        QuestionRequest: 应用默认值后的验证请求

    Raises:
        ValueError: 如果验证失败
    """
    if not req.keyword:
        raise ValueError("关键字不能为空")

    # 设置默认值
    if not req.language:
        req.language = "go"
    if not req.type:
        req.type = SINGLE_SELECT
    if not req.count:
        req.count = 3
    if not req.model:
        req.model = "deepseek"

    # 验证值
    if req.model not in ["deepseek"]:
        raise ValueError("不支持的AI模型")

    if req.language not in ["go", "java", "python", "javascript", "c++", "css", "html"]:
        raise ValueError("不支持的编程语言")

    if req.count < 3 or req.count > 10:
        raise ValueError("题目数量必须在3-10之间")

    if req.type not in [SINGLE_SELECT, MULTI_SELECT, CODING]:
        raise ValueError("无效的题目类型")

    return req


def validate_question_request1(req: QuestionRequest1) -> None:
    """
    验证手动创建题目的请求。

    Args:
        req: 要验证的题目请求

    Raises:
        ValueError: 如果验证失败
    """
    if not req.title:
        raise ValueError("题目标题不能为空")

    if req.type not in [SINGLE_SELECT, MULTI_SELECT, CODING]:
        raise ValueError("无效的题目类型")

    if len(req.answers) != 4:
        raise ValueError("必须提供4个选项")

    # 验证单选/多选题的答案选项
    if req.type in [SINGLE_SELECT, MULTI_SELECT]:
        valid_options = {"A", "B", "C", "D"}
        for answer in req.rights:
            if answer not in valid_options:
                raise ValueError("存在无效选项标识")

        # 检查重复项
        if len(set(req.rights)) != len(req.rights):
            raise ValueError("答案选项不能重复")

        # 单选题必须有且仅有一个答案
        if req.type == SINGLE_SELECT and len(req.rights) != 1:
            raise ValueError("单选题必须有且仅有一个正确答案")

        # 多选题必须有2-4个答案
        if req.type == MULTI_SELECT and (len(req.rights) < 2 or len(req.rights) > 4):
            raise ValueError("多选题正确答案数量需在2-4个之间")
