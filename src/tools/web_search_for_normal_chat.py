# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
普通对话的联网检索处理器
用于在普通对话模式下启用联网搜索功能
"""

import json
import logging
from datetime import datetime
from typing import List, Tuple, Optional

import openai

from src.config import load_yaml_config
from src.tools.tavily_search.tavily_search_api_wrapper import EnhancedTavilySearchAPIWrapper

logger = logging.getLogger(__name__)


class NormalChatWebSearcher:
    """普通对话的联网检索处理器"""

    def __init__(self):
        """初始化搜索器"""
        self.search_wrapper = EnhancedTavilySearchAPIWrapper()
        self._init_llm_client()

    def _init_llm_client(self):
        """初始化 LLM 客户端"""
        import os
        conf_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "conf.yaml"
        )
        config = load_yaml_config(conf_path)
        basic_model = config.get("BASIC_MODEL", {})

        self.client = openai.OpenAI(
            api_key=basic_model.get("api_key", "123456"),
            base_url=basic_model.get("base_url", "http://172.16.16.199:30500/v1"),
        )
        self.model = basic_model.get("model", "glm-4.7-flash")

    async def process(
        self,
        user_query: str,
        history_messages: List[Tuple[str, str]]
    ) -> str:
        """
        处理联网检索的完整流程

        Args:
            user_query: 用户当前问题
            history_messages: 历史对话列表 [(question, answer), ...]

        Returns:
            最终答案
        """
        logger.info(f"[NormalChatWebSearch] Processing query: {user_query}")

        # 1. 意图识别 - 提取关键词
        keywords = await self._extract_keywords(user_query, history_messages)
        logger.info(f"[NormalChatWebSearch] Extracted keywords: {keywords}")

        # 2. 联网搜索
        search_results = await self._web_search(keywords)
        logger.info(f"[NormalChatWebSearch] Search results count: {len(search_results)}")

        # 3. 生成最终答案
        final_answer = await self._generate_answer(
            user_query,
            history_messages,
            search_results
        )

        return final_answer

    async def _extract_keywords(
        self,
        query: str,
        history_messages: List[Tuple[str, str]]
    ) -> str:
        """
        调用 LLM 提取搜索关键词

        Args:
            query: 用户当前问题
            history_messages: 历史对话

        Returns:
            关键词列表（逗号分隔）
        """
        # 获取今天的日期，用于提升搜索时效性
        today_date = datetime.now().strftime("%Y年%m月%d日")

        # 构建历史对话上下文
        history_context = ""
        for q, a in history_messages[-5:]:  # 取最近5轮对话
            if q:
                history_context += f"用户: {q}\n"
            if a:
                history_context += f"助手: {a}\n"

        prompt = f"""你需要从用户的问题中提取搜索关键词。

今天是: {today_date}

历史对话:
{history_context}

用户当前问题: {query}

要求:
1. 根据用户问题和历史对话，判断用户真正想要查询的信息
2. 提取多个关键词或短语，用逗号分隔
3. 只输出关键词，不要输出其他内容
4. 如果用户问题已经足够清晰，直接提取问题中的核心名词/实体
5. 考虑到今天是 {today_date}，可以适当添加日期相关的关键词以提升搜索结果的时效性

关键词:"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个关键词提取助手。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=100,
            )
            keywords = response.choices[0].message.content.strip()
            return keywords
        except Exception as e:
            logger.error(f"[NormalChatWebSearch] Error extracting keywords: {e}")
            # 如果出错，直接返回原问题作为关键词
            return query

    async def _web_search(self, keywords: str) -> str:
        """
        调用 Tavily API 进行搜索

        Args:
            keywords: 搜索关键词

        Returns:
            格式化的搜索结果字符串
        """
        try:
            results = await self.search_wrapper.raw_results_async(
                query=keywords,
                max_results=20,
                search_depth="advanced",
            )

            # 格式化搜索结果
            formatted_results = self._format_search_results(results)
            return formatted_results
        except Exception as e:
            logger.error(f"[NormalChatWebSearch] Error in web search: {e}")
            return ""

    def _format_search_results(self, results: dict) -> str:
        """
        格式化搜索结果为字符串

        Args:
            results: Tavily API 返回的结果

        Returns:
            格式化后的字符串
        """
        formatted = []
        results_list = results.get("results", [])

        for i, result in enumerate(results_list, 1):
            title = result.get("title", "")
            url = result.get("url", "")
            content = result.get("content", "")

            formatted.append(f"【搜索结果 {i}】")
            formatted.append(f"标题: {title}")
            formatted.append(f"链接: {url}")
            formatted.append(f"内容: {content}")
            formatted.append("")

        return "\n".join(formatted)

    def extract_reference_sources(self, search_results: str) -> List[dict]:
        """
        从搜索结果中提取标题和链接，用于附在答案后面

        Args:
            search_results: 格式化的搜索结果字符串

        Returns:
            [{'title': xxx, 'url': xxx}, ...]
        """
        import re

        sources = []
        # 使用正则表达式提取标题和链接
        # 匹配 "标题: xxx" 和 "链接: xxx"
        title_pattern = r"标题: (.+)"
        url_pattern = r"链接: (.+)"

        lines = search_results.split("\n")
        current_title = ""
        current_url = ""

        for line in lines:
            title_match = re.match(title_pattern, line.strip())
            url_match = re.match(url_pattern, line.strip())

            if title_match:
                current_title = title_match.group(1).strip()
            elif url_match:
                current_url = url_match.group(1).strip()
                # 当同时有标题和链接时，添加到 sources 列表
                if current_title and current_url:
                    sources.append({
                        'title': current_title,
                        'url': current_url
                    })
                    current_title = ""
                    current_url = ""

        return sources

    async def _generate_answer(
        self,
        user_query: str,
        history_messages: List[Tuple[str, str]],
        search_results: str
    ) -> str:
        """
        调用 LLM 生成最终答案

        Args:
            user_query: 用户当前问题
            history_messages: 历史对话
            search_results: 联网搜索结果

        Returns:
            最终答案
        """
        # 构建历史对话上下文
        history_context = ""
        for q, a in history_messages:
            if q:
                history_context += f"用户: {q}\n"
            if a:
                history_context += f"助手: {a}\n"

        # 构建完整上下文
        system_prompt = """你是一个智能助手。请根据以下信息回答用户的问题。

要求:
1. 结合搜索结果和历史对话来回答
2. 如果搜索结果中有相关信息，请优先使用搜索结果
3. 回答要准确、简洁、有帮助
4. 如果搜索结果中没有相关信息，请根据你的知识库回答"""

        user_prompt = f"""历史对话:
{history_context}

用户当前问题: {user_query}

联网搜索结果:
{search_results}

请根据以上信息回答用户的问题:"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                stream=True,
            )

            # 流式返回
            full_answer = ""
            for chunk in response:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        full_answer += delta.content
                        yield "event: message\ndata: {}\n\n".format(
                            json.dumps({'status': 'streaming', 'chunk': delta.content}, ensure_ascii=False)
                        )

            # 发送完成状态
            yield "event: message\ndata: {}\n\n".format(
                json.dumps({'status': 'completed', 'full_content': full_answer}, ensure_ascii=False)
            )

        except Exception as e:
            logger.error(f"[NormalChatWebSearch] Error generating answer: {e}")
            yield f"event: error\ndata: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"


async def process_normal_chat_with_web_search(
    user_query: str,
    history_messages: List[Tuple[str, str]]
) -> str:
    """
    处理普通对话的联网检索（同步版本，返回完整答案）

    用于需要完整答案而非流式输出的场景

    Args:
        user_query: 用户当前问题
        history_messages: 历史对话列表

    Returns:
        最终答案
    """
    searcher = NormalChatWebSearcher()

    # 1. 意图识别 - 提取关键词
    keywords = await searcher._extract_keywords(user_query, history_messages)
    logger.info(f"[NormalChatWebSearch] Extracted keywords: {keywords}")

    # 2. 联网搜索
    search_results = await searcher._web_search(keywords)
    logger.info(f"[NormalChatWebSearch] Search results obtained")

    # 3. 构建完整上下文并调用 LLM（非流式）
    history_context = ""
    for q, a in history_messages:
        if q:
            history_context += f"用户: {q}\n"
        if a:
            history_context += f"助手: {a}\n"

    system_prompt = """你是一个智能助手。请根据以下信息回答用户的问题。

要求:
1. 结合搜索结果和历史对话来回答
2. 如果搜索结果中有相关信息，请优先使用搜索结果
3. 回答要准确、简洁、有帮助
4. 如果搜索结果中没有相关信息，请根据你的知识库回答"""

    user_prompt = f"""历史对话:
{history_context}

用户当前问题: {user_query}

联网搜索结果:
{search_results}

请根据以上信息回答用户的问题:"""

    try:
        response = searcher.client.chat.completions.create(
            model=searcher.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            stream=False,
        )

        final_answer = response.choices[0].message.content
        return final_answer

    except Exception as e:
        logger.error(f"[NormalChatWebSearch] Error generating answer: {e}")
        return f"抱歉，处理您的请求时发生错误: {str(e)}"
