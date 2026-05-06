# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import logging
import os

from src.config.tools import RAGProvider
from src.rag.composite_provider import CompositeRetriever
from src.rag.dify import DifyProvider
from src.rag.milvus import MilvusProvider
from src.rag.moi import MOIProvider
from src.rag.qdrant import QdrantProvider
from src.rag.ragflow import RAGFlowProvider
from src.rag.retriever import Retriever
from src.rag.vikingdb_knowledge_base import VikingDBKnowledgeBaseProvider

logger = logging.getLogger(__name__)


def build_retriever(resources: list = None) -> Retriever | None:
    """
    Build a retriever based on the RAG_PROVIDER environment variable and resources.
    Supports multiple providers separated by commas.
    
    Args:
        resources: Optional list of Resource objects to determine which providers to use.
                  If empty or None, all configured providers will be initialized for global search.
    
    Returns:
        A single Retriever instance, or CompositeRetriever if multiple providers are configured.
        Returns None if no provider is configured or initialization fails.
    """
    rag_provider_env = os.getenv("RAG_PROVIDER")
    
    if not rag_provider_env:
        logger.info("RAG_PROVIDER not configured, cannot build retriever")
        return None
    
    # Split by comma to support multiple providers
    all_provider_names = [name.strip() for name in rag_provider_env.split(",")]
    
    # If resources are provided and not empty, filter providers based on resource URIs
    if resources and len(resources) > 0:
        required_providers = set()
        for resource in resources:
            uri = resource.uri
            if uri.startswith("rag://"):
                # RAGFlow resource
                if RAGProvider.RAGFLOW.value in all_provider_names:
                    required_providers.add(RAGProvider.RAGFLOW.value)
                    logger.debug(f"Detected RAGFlow resource: {resource.title}")
            elif uri.startswith("elasticsearch://"):
                # Elasticsearch resource
                if RAGProvider.ELASTICSEARCH.value in all_provider_names:
                    required_providers.add(RAGProvider.ELASTICSEARCH.value)
                    logger.debug(f"Detected Elasticsearch resource: {resource.title}")
            # Add more provider type detection as needed for other providers
            # For example: dify://, moi://, vikingdb://, etc.
        
        if not required_providers:
            logger.info("No matching providers found for the given resources, will use all configured providers")
            provider_names = all_provider_names
        else:
            provider_names = list(required_providers)
            logger.info(f"Filtered providers based on {len(resources)} resources: {provider_names}")
    else:
        # No resources specified or empty list, use all configured providers for global search
        provider_names = all_provider_names
        logger.info(f"No specific resources, initializing all configured providers for global search: {provider_names}")
    
    available_retrievers = []
    
    for provider_name in provider_names:
        try:
            if provider_name == RAGProvider.ELASTICSEARCH.value:
                from src.rag.elasticsearch import ElasticsearchProvider
                retriever = ElasticsearchProvider()
                available_retrievers.append(retriever)
                logger.info(f"Successfully initialized {provider_name}")
            elif provider_name == RAGProvider.RAGFLOW.value:
                retriever = RAGFlowProvider()
                available_retrievers.append(retriever)
                logger.info(f"Successfully initialized {provider_name}")
            elif provider_name == RAGProvider.DIFY.value:
                retriever = DifyProvider()
                available_retrievers.append(retriever)
                logger.info(f"Successfully initialized {provider_name}")
            elif provider_name == RAGProvider.MOI.value:
                retriever = MOIProvider()
                available_retrievers.append(retriever)
                logger.info(f"Successfully initialized {provider_name}")
            elif provider_name == RAGProvider.VIKINGDB_KNOWLEDGE_BASE.value:
                retriever = VikingDBKnowledgeBaseProvider()
                available_retrievers.append(retriever)
                logger.info(f"Successfully initialized {provider_name}")
            elif provider_name == RAGProvider.MILVUS.value:
                retriever = MilvusProvider()
                available_retrievers.append(retriever)
                logger.info(f"Successfully initialized {provider_name}")
            elif provider_name == RAGProvider.QDRANT.value:
                retriever = QdrantProvider()
                available_retrievers.append(retriever)
                logger.info(f"Successfully initialized {provider_name}")
            else:
                logger.warning(f"Unknown RAG provider: {provider_name}")
        except Exception as e:
            logger.error(f"Failed to initialize {provider_name}: {e}", exc_info=True)
            # Continue to next provider instead of failing completely
    
    # Check if we have any available retrievers
    if not available_retrievers:
        logger.warning(f"No RAG providers could be initialized from: {provider_names}")
        return None
    
    # Return single retriever or composite
    if len(available_retrievers) == 1:
        logger.info(f"Using single retriever: {available_retrievers[0].__class__.__name__}")
        return available_retrievers[0]
    else:
        logger.info(f"Using CompositeRetriever with {len(available_retrievers)} providers")
        return CompositeRetriever(available_retrievers)
