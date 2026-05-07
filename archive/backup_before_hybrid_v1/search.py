# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import logging
import os
from typing import List, Optional

from langchain_community.tools import (
    BraveSearch,
    DuckDuckGoSearchResults,
    GoogleSerperRun,
    SearxSearchRun,
    WikipediaQueryRun,
)
from langchain_community.tools.arxiv import ArxivQueryRun
from langchain_community.utilities import (
    ArxivAPIWrapper,
    BraveSearchWrapper,
    GoogleSerperAPIWrapper,
    SearxSearchWrapper,
    WikipediaAPIWrapper,
)

from src.config import SELECTED_SEARCH_ENGINE, SearchEngine, load_yaml_config
from src.tools.decorators import create_logged_tool
from src.tools.infoquest_search.infoquest_search_results import InfoQuestSearchResults
from src.tools.tavily_search.tavily_search_results_with_images import (
    TavilySearchWithImages,
)

logger = logging.getLogger(__name__)


# # Create a wrapper for GoogleSerperRun to fix the _arun signature issue
# class GoogleSerperRunWrapper(GoogleSerperRun):
#     """Wrapper for GoogleSerperRun to fix _arun signature compatibility."""
    
#     async def _arun(
#         self,
#         *args,
#         **kwargs
#     ) -> str:
#         """Override _arun to handle parameter passing correctly."""
#         # langchain_core may pass 'args' as a keyword argument containing the actual args
#         # or pass 'args' as a list/tuple in kwargs
#         if 'args' in kwargs:
#             # If 'args' is in kwargs, it might be a list/tuple containing the actual arguments
#             args_from_kwargs = kwargs.pop('args')
#             if isinstance(args_from_kwargs, (list, tuple)) and len(args_from_kwargs) > 0:
#                 query = args_from_kwargs[0]
#             elif isinstance(args_from_kwargs, dict):
#                 # If args is a dict, extract query from it
#                 query = args_from_kwargs.get('query', '')
#             else:
#                 query = args_from_kwargs
#         elif args and len(args) > 0:
#             # Normal positional argument
#             query = args[0]
#         elif 'query' in kwargs:
#             # Query passed as keyword argument
#             query = kwargs.pop('query')
#         else:
#             # Last resort: check if tool_input was passed as a string in kwargs
#             # or if there's a single value in kwargs
#             if len(kwargs) == 1:
#                 # If there's only one kwarg, it might be the query
#                 query = next(iter(kwargs.values()))
#             else:
#                 raise ValueError(f"Missing required argument 'query'. Received args={args}, kwargs={kwargs}")
        
#         # Filter out unsupported kwargs
#         filtered_kwargs = {k: v for k, v in kwargs.items() if k not in ['args']}
        
#         # Extract run_manager if present
#         run_manager = filtered_kwargs.pop('run_manager', None)
        
#         # Call parent's _arun with correct parameters
#         try:
#             if run_manager is not None:
#                 return await super()._arun(query, run_manager=run_manager)
#             else:
#                 return await super()._arun(query)
#         except TypeError:
#             # If parent doesn't accept run_manager, try without it
#             return await super()._arun(query)


# Create logged versions of the search tools
LoggedTavilySearch = create_logged_tool(TavilySearchWithImages)
LoggedInfoQuestSearch = create_logged_tool(InfoQuestSearchResults)
LoggedDuckDuckGoSearch = create_logged_tool(DuckDuckGoSearchResults)
LoggedBraveSearch = create_logged_tool(BraveSearch)
LoggedSerperSearch = create_logged_tool(GoogleSerperRun)
# LoggedSerperSearch = create_logged_tool(GoogleSerperRunWrapper)
LoggedArxivSearch = create_logged_tool(ArxivQueryRun)
LoggedSearxSearch = create_logged_tool(SearxSearchRun)
LoggedWikipediaSearch = create_logged_tool(WikipediaQueryRun)


def get_search_config():
    config = load_yaml_config("conf.yaml")
    search_config = config.get("SEARCH_ENGINE", {})
    return search_config


# Get the selected search tool
def get_web_search_tool(max_search_results: int):
    search_config = get_search_config()

    print(f"SELECTED_SEARCH_ENGINE: {SELECTED_SEARCH_ENGINE}")

    if SELECTED_SEARCH_ENGINE == SearchEngine.TAVILY.value:
        # Get all Tavily search parameters from configuration with defaults
        include_domains: Optional[List[str]] = search_config.get("include_domains", [])
        exclude_domains: Optional[List[str]] = search_config.get("exclude_domains", [])
        include_answer: bool = search_config.get("include_answer", False)
        search_depth: str = search_config.get("search_depth", "advanced")
        include_raw_content: bool = search_config.get("include_raw_content", True)
        include_images: bool = search_config.get("include_images", True)
        include_image_descriptions: bool = include_images and search_config.get(
            "include_image_descriptions", True
        )

        logger.info(
            f"Tavily search configuration loaded: include_domains={include_domains}, "
            f"exclude_domains={exclude_domains}, include_answer={include_answer}, "
            f"search_depth={search_depth}, include_raw_content={include_raw_content}, "
            f"include_images={include_images}, include_image_descriptions={include_image_descriptions}"
        )

        return LoggedTavilySearch(
            name="web_search",
            max_results=max_search_results,
            include_answer=include_answer,
            search_depth=search_depth,
            include_raw_content=include_raw_content,
            include_images=include_images,
            include_image_descriptions=include_image_descriptions,
            include_domains=include_domains,
            exclude_domains=exclude_domains,
        )
    elif SELECTED_SEARCH_ENGINE == SearchEngine.INFOQUEST.value:
        time_range = search_config.get("time_range", -1)
        site = search_config.get("site", "")
        logger.info(
            f"InfoQuest search configuration loaded: time_range={time_range}, site={site}"
        )
        return LoggedInfoQuestSearch(
            name="web_search",
            time_range=time_range,
            site=site,
        )
    elif SELECTED_SEARCH_ENGINE == SearchEngine.DUCKDUCKGO.value:
        return LoggedDuckDuckGoSearch(
            name="web_search",
            num_results=max_search_results,
        )
    elif SELECTED_SEARCH_ENGINE == SearchEngine.BRAVE_SEARCH.value:
        return LoggedBraveSearch(
            name="web_search",
            search_wrapper=BraveSearchWrapper(
                api_key=os.getenv("BRAVE_SEARCH_API_KEY", ""),
                search_kwargs={"count": max_search_results},
            ),
        )
    elif SELECTED_SEARCH_ENGINE == SearchEngine.SERPER.value:
        # return LoggedSerperSearch(
        return GoogleSerperRun( 
            name="web_search",
            api_wrapper=GoogleSerperAPIWrapper(
                k=max_search_results,
                serper_api_key=os.getenv("SERPER_API_KEY", ""),
            ),
        )
    elif SELECTED_SEARCH_ENGINE == SearchEngine.ARXIV.value:
        return LoggedArxivSearch(
            name="web_search",
            api_wrapper=ArxivAPIWrapper(
                top_k_results=max_search_results,
                load_max_docs=max_search_results,
                load_all_available_meta=True,
            ),
        )
    elif SELECTED_SEARCH_ENGINE == SearchEngine.SEARX.value:
        return LoggedSearxSearch(
            name="web_search",
            wrapper=SearxSearchWrapper(
                k=max_search_results,
            ),
        )
    elif SELECTED_SEARCH_ENGINE == SearchEngine.WIKIPEDIA.value:
        wiki_lang = search_config.get("wikipedia_lang", "en")
        wiki_doc_content_chars_max = search_config.get(
            "wikipedia_doc_content_chars_max", 4000
        )
        return LoggedWikipediaSearch(
            name="web_search",
            api_wrapper=WikipediaAPIWrapper(
                lang=wiki_lang,
                top_k_results=max_search_results,
                load_all_available_meta=True,
                doc_content_chars_max=wiki_doc_content_chars_max,
            ),
        )
    else:
        raise ValueError(f"Unsupported search engine: {SELECTED_SEARCH_ENGINE}")
