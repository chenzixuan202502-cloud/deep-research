# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import json
import logging
import os
from typing import Dict, List, Optional

import aiohttp
import requests
from langchain_tavily._utilities import TAVILY_API_URL
from langchain_tavily.tavily_search import (
    TavilySearchAPIWrapper as OriginalTavilySearchAPIWrapper,
)

from src.config import load_yaml_config
from src.tools.search_postprocessor import SearchResultPostProcessor


def get_search_config():
    config = load_yaml_config("conf.yaml")
    search_config = config.get("SEARCH_ENGINE", {})
    return search_config


# 添加日志记录器
logger = logging.getLogger(__name__)


class EnhancedTavilySearchAPIWrapper(OriginalTavilySearchAPIWrapper):
    def __init__(self, **kwargs):
        # 调用父类初始化
        super().__init__(**kwargs)
        # 在调用父类后记录 API key（此时父类已设置好属性）
        try:
            #api_key = self.tavily_api_key.get_secret_value()
            api_key = "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"
            if api_key:
                masked_key = api_key[:10] + "****" if len(api_key) > 14 else "***"
                logger.info(f"[Tavily] API Key (masked): {masked_key}, length: {len(api_key)}")
            else:
                logger.warning(f"[Tavily] API Key is EMPTY!")
        except Exception as e:
            logger.error(f"[Tavily] Error getting API key: {e}")
            # 尝试从环境变量获取
            env_key = os.getenv("TAVILY_API_KEY", "NOT_SET")
            logger.info(f"[Tavily] TAVILY_API_KEY from env: {env_key[:10]}****{env_key[-4:] if len(env_key) > 14 else ''}")

    def raw_results(
        self,
        query: str,
        max_results: Optional[int] = 5,
        search_depth: Optional[str] = "advanced",
        include_domains: Optional[List[str]] = [],
        exclude_domains: Optional[List[str]] = [],
        include_answer: Optional[bool] = False,
        include_raw_content: Optional[bool] = False,
        include_images: Optional[bool] = False,
        include_image_descriptions: Optional[bool] = False,
    ) -> Dict:
        #api_key = self.tavily_api_key.get_secret_value()
        api_key = "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"
        masked_key = api_key[:10] + "****" if len(api_key) > 14 else "***"
        params = {
            "api_key": api_key,
            "query": query,
            "max_results": max_results,
            "search_depth": search_depth,
            "include_domains": include_domains,
            "exclude_domains": exclude_domains,
            "include_answer": include_answer,
            "include_raw_content": include_raw_content,
            "include_images": include_images,
            "include_image_descriptions": include_image_descriptions,
        }
        
        # 记录请求信息（脱敏 API key）
        logger.info(f"[Tavily] ===== REQUEST DETAILS =====")
        logger.info(f"[Tavily] URL: {TAVILY_API_URL}/search")
        logger.info(f"[Tavily] API Key (masked): {masked_key}")
        logger.info(f"[Tavily] Query: {query}")
        logger.info(f"[Tavily] Max Results: {max_results}")
        logger.info(f"[Tavily] Search Depth: {search_depth}")
        logger.info(f"[Tavily] Include Answer: {include_answer}")
        logger.info(f"[Tavily] Include Raw Content: {include_raw_content}")
        logger.info(f"[Tavily] Include Images: {include_images}")
        logger.info(f"[Tavily] Include Domains: {include_domains}")
        logger.info(f"[Tavily] Exclude Domains: {exclude_domains}")
        logger.info(f"[Tavily] ===========================")
        
        response = requests.post(
            # type: ignore
            f"{TAVILY_API_URL}/search",
            json=params,
        )
        
        # 记录响应信息
        logger.info(f"[Tavily] Response Status: {response.status_code}")
        logger.info(f"[Tavily] Response Headers: {dict(response.headers)}")
        
        response.raise_for_status()
        return response.json()

    async def raw_results_async(
        self,
        query: str,
        max_results: Optional[int] = 5,
        search_depth: Optional[str] = "advanced",
        include_domains: Optional[List[str]] = [],
        exclude_domains: Optional[List[str]] = [],
        include_answer: Optional[bool] = False,
        include_raw_content: Optional[bool] = False,
        include_images: Optional[bool] = False,
        include_image_descriptions: Optional[bool] = False,
    ) -> Dict:
        """Get results from the Tavily Search API asynchronously."""

        # 获取并脱敏 API key
        #api_key = self.tavily_api_key.get_secret_value()
        api_key = "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"
        masked_key = api_key[:10] + "****" if len(api_key) > 14 else "***"
        
        # Function to perform the API call
        async def fetch() -> str:
            params = {
                "api_key": api_key,
                "query": query,
                "max_results": max_results,
                "search_depth": search_depth,
                "include_domains": include_domains,
                "exclude_domains": exclude_domains,
                "include_answer": include_answer,
                "include_raw_content": include_raw_content,
                "include_images": include_images,
                "include_image_descriptions": include_image_descriptions,
            }
            
            # 记录异步请求信息（脱敏 API key）
            logger.info(f"[Tavily Async] ===== REQUEST DETAILS =====")
            logger.info(f"[Tavily Async] URL: {TAVILY_API_URL}/search")
            logger.info(f"[Tavily Async] API Key (masked): {masked_key}")
            logger.info(f"[Tavily Async] Query: {query}")
            logger.info(f"[Tavily Async] Max Results: {max_results}")
            logger.info(f"[Tavily Async] Search Depth: {search_depth}")
            logger.info(f"[Tavily Async] ===========================")
            
            async with aiohttp.ClientSession(trust_env=True) as session:
                async with session.post(f"{TAVILY_API_URL}/search", json=params) as res:
                    logger.info(f"[Tavily Async] Response Status: {res.status}")
                    if res.status == 200:
                        data = await res.text()
                        return data
                    else:
                        error_text = await res.text()
                        logger.error(f"[Tavily Async] Error Response: {error_text}")
                        raise Exception(f"Error {res.status}: {res.reason}")

        results_json_str = await fetch()
        return json.loads(results_json_str)

    def clean_results_with_images(
        self, raw_results: Dict[str, List[Dict]]
    ) -> List[Dict]:
        results = raw_results["results"]
        """Clean results from Tavily Search API."""
        clean_results = []
        for result in results:
            clean_result = {
                "type": "page",
                "title": result["title"],
                "url": result["url"],
                "content": result["content"],
                "score": result["score"],
            }
            if raw_content := result.get("raw_content"):
                clean_result["raw_content"] = raw_content
            clean_results.append(clean_result)
        images = raw_results["images"]
        for image in images:
            clean_result = {
                "type": "image_url",
                "image_url": {"url": image["url"]},
                "image_description": image["description"],
            }
            clean_results.append(clean_result)

        search_config = get_search_config()
        clean_results = SearchResultPostProcessor(
            min_score_threshold=search_config.get("min_score_threshold"),
            max_content_length_per_page=search_config.get(
                "max_content_length_per_page"
            ),
        ).process_results(clean_results)

        return clean_results
