# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import logging
from typing import List, Optional, Type

from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from src.config.tools import SELECTED_RAG_PROVIDER
from src.rag import Document, Resource, Retriever, build_retriever

logger = logging.getLogger(__name__)


class RetrieverInput(BaseModel):
    keywords: str = Field(description="search keywords to look up")


class RetrieverTool(BaseTool):
    name: str = "local_search_tool"
    description: str = "Useful for retrieving information from the file with `rag://` uri prefix, it should be higher priority than the web search or writing code. Input should be a search keywords."
    args_schema: Type[BaseModel] = RetrieverInput

    retriever: Retriever = Field(default_factory=Retriever)
    resources: list[Resource] = Field(default_factory=list)

    def _run(
        self,
        keywords: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> list[Document]:
        logger.info(
            f"Retriever tool query: {keywords}", extra={"resources": self.resources}
        )
        
        # Filter out virtual global resources for actual retrieval
        # Virtual resources (global://) are used to signal Planner, but actual retrieval
        # should search all databases when no specific resources are provided
        actual_resources = [r for r in self.resources if not r.uri.startswith("global://")]
        
        if not actual_resources and any(r.uri.startswith("global://") for r in self.resources):
            # If only virtual global resources exist, perform global search (empty resources list)
            logger.info("Virtual global resource detected, performing global knowledge base search")
            actual_resources = []
        
        documents = self.retriever.query_relevant_documents(keywords, actual_resources)
        if not documents:
            return "No results found from the local knowledge base."
        return [doc.to_dict() for doc in documents]

    async def _arun(
        self,
        keywords: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> list[Document]:
        return self._run(keywords, run_manager.get_sync())


def get_retriever_tool(resources: List[Resource]) -> RetrieverTool | None:
    """
    Get retriever tool for RAG search.
    
    Args:
        resources: List of resources to search. If empty or contains only virtual global resources,
                  will search global knowledge base.
        
    Returns:
        RetrieverTool instance or None if RAG_PROVIDER is not configured
    """
    # Check if RAG_PROVIDER is configured
    import os
    rag_provider = os.getenv("RAG_PROVIDER")
    
    if not rag_provider:
        logger.info("RAG_PROVIDER not configured, skipping retriever tool creation")
        return None
    
    # Check if we have virtual global resources
    has_virtual_global = any(r.uri.startswith("global://") for r in resources) if resources else False
    actual_resources = [r for r in resources if not r.uri.startswith("global://")] if resources else []
    
    # Log resource information
    if has_virtual_global and not actual_resources:
        logger.info("Virtual global resource detected, will search entire knowledge base")
    elif not resources:
        logger.info("No specific resources provided, will search global knowledge base")
    else:
        logger.info(f"Creating retriever tool for {len(actual_resources)} actual resources: {[r.uri for r in actual_resources]}")
    
    # Build retriever - pass actual resources (excluding virtual ones)
    # If only virtual resources exist, pass empty list to trigger global search
    retriever_resources = actual_resources if actual_resources else []
    retriever = build_retriever(retriever_resources)

    if not retriever:
        logger.warning("No retriever could be built - check RAG_PROVIDER configuration")
        return None
    
    logger.info(f"Successfully created retriever tool with {retriever.__class__.__name__}")
    # Pass original resources list (including virtual) to the tool for logging purposes
    return RetrieverTool(retriever=retriever, resources=resources if resources else [])
