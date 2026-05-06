# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import base64
import logging
import os
from typing import List

from elasticsearch import Elasticsearch

from src.rag.retriever import Chunk, Document, Resource, Retriever

logger = logging.getLogger(__name__)


class ElasticsearchProvider(Retriever):
    """
    ElasticsearchProvider implements a unified knowledge base pattern.
    Instead of exposing individual indices, it provides a single virtual resource
    that searches across all configured indices simultaneously.
    
    Compatible with Elasticsearch 7.x using text-based search.
    """

    # Virtual resource ID for the unified knowledge base
    UNIFIED_RESOURCE_ID = "es_global_search"
    UNIFIED_RESOURCE_TITLE = "Elasticsearch 全库搜索"
    UNIFIED_RESOURCE_DESCRIPTION = "搜索包含新闻、帖子、实体等在内的所有数据库"
    
    # Common text fields across different indices
    COMMON_TEXT_FIELDS = [
        "title",
        "content",
        "body",
        "text",
        "description",
        "summary",
        "weibo_content",
        "news_content",
        "post_content",
        "comment_content",
        "forum_content",
        "message",
        "article",
        "name",
        "bio",
        "profile"
    ]

    def __init__(self):
        """
        Initialize Elasticsearch client with HTTP basic authentication.
        Configures target indices for unified search.
        """
        # Read configuration from environment
        host = os.getenv("ELASTICSEARCH_HOST")
        if not host:
            raise ValueError("ELASTICSEARCH_HOST is not set")
        
        user = os.getenv("ELASTICSEARCH_USER")
        if not user:
            raise ValueError("ELASTICSEARCH_USER is not set")
        
        password = os.getenv("ELASTICSEARCH_PASSWORD")
        if not password:
            raise ValueError("ELASTICSEARCH_PASSWORD is not set")
        
        # Read target indices (supports wildcards)
        indices_str = os.getenv("ELASTICSEARCH_TARGET_INDICES")
        if not indices_str:
            # Default target indices if not configured
            logger.warning("ELASTICSEARCH_TARGET_INDICES not set, using default indices")
            self.target_indices = [
                "2_cn_news_library",
                "2_cn_post_library",
                "3_cn_targetmap_*",
                "2_cn_comment_library",
                "2_cn_forum_library",
                "2_cn_interactive_library"
            ]
        else:
            self.target_indices = [idx.strip() for idx in indices_str.split(",")]
        
        # Ensure HTTP protocol is used
        if not host.startswith("http://") and not host.startswith("https://"):
            host = f"http://{host}"
        
        # Manual Basic Auth encoding
        credentials = f"{user}:{password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        # Initialize Elasticsearch client with HTTP and disabled cert verification
        # Disable all automatic health checks and sniffing for restricted environments
        self.client = Elasticsearch(
            hosts=[host],
            headers={"Authorization": f"Basic {encoded_credentials}"},
            verify_certs=False,
            ssl_show_warn=False,
            sniff_on_start=False,           # Don't sniff on startup
            sniff_on_connection_fail=False, # Don't sniff on connection failure
            sniffer_timeout=None,           # Disable sniffer timeout
            sniff_timeout=None,             # Disable sniff timeout
            # === 核心修改点：增强连接鲁棒性 ===
            request_timeout=60,             # 给服务器 60秒 时间（从 30 秒增加）
            max_retries=3,                  # 失败了再试 3 次（从 1 次增加）
            retry_on_timeout=True           # 超时也要重试！（从 False 改为 True）
        )
        # 🪄 魔法代码：欺骗客户端已完成验证，跳过 "GET /" 检查
        self.client.transport.verified_elasticsearch = True
        
        # Suppress the verification warning by setting a flag
        import warnings
        from elasticsearch import ElasticsearchWarning
        warnings.filterwarnings('ignore', category=ElasticsearchWarning)
        
        # Skip health check due to limited permissions
        logger.info("ES Client initialized (Health check skipped)")
        logger.info(f"Unified search configured for indices: {self.target_indices}")

    def list_resources(self, query: str | None = None) -> List[Resource]:
        """
        Return a single unified resource representing the entire Elasticsearch cluster.
        This allows users to search across all indices without needing to know
        the underlying data structure.
        
        Args:
            query: Ignored in unified mode
            
        Returns:
            List containing a single unified Resource object
        """
        unified_resource = Resource(
            uri=f"elasticsearch://{self.UNIFIED_RESOURCE_ID}",
            title=self.UNIFIED_RESOURCE_TITLE,
            description=self.UNIFIED_RESOURCE_DESCRIPTION
        )
        
        logger.info("Returning unified Elasticsearch resource")
        return [unified_resource]

    def query_relevant_documents(
        self, query: str, resources: List[Resource] = []
    ) -> List[Document]:
        """
        Query relevant documents across all configured indices using unified search.
        Uses multi_match to handle different field names across indices.
        
        Args:
            query: The search query string
            resources: Ignored in unified mode (always searches all target indices)
            
        Returns:
            List of Document objects with relevant content from all indices
        """
        # In unified mode, we always search across all target indices
        # regardless of the resources parameter
        target_indices = self.target_indices
        
        # Build multi_match query that works across different field names
        search_body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": self.COMMON_TEXT_FIELDS,
                    "type": "best_fields",
                    "operator": "or",
                    "lenient": True  # Ignore field mapping errors
                }
            },
            "_source": {
                "excludes": ["photo", "avatar", "base64", "image", "thumbnail", "picture"]
            },
            "highlight": {
                "fields": {
                    "*": {
                        "pre_tags": ["<em>"],
                        "post_tags": ["</em>"],
                        "fragment_size": 150,
                        "number_of_fragments": 3
                    }
                }
            },
            "size": 30,  # Increased size for better coverage
            "sort": [
                {"_score": {"order": "desc"}}  # Sort by relevance
            ]
        }
        
        logger.info(f"Unified search across indices: {target_indices}")
        logger.info(f"Query: {query}")
        
        try:
            # Execute unified search across all target indices
            response = self.client.search(
                index=",".join(target_indices),
                body=search_body
            )
            
            hits = response.get("hits", {}).get("hits", [])
            total_hits = response.get("hits", {}).get("total", {})
            
            if isinstance(total_hits, dict):
                total_count = total_hits.get("value", 0)
            else:
                total_count = total_hits
            
            logger.info(f"Elasticsearch unified search: {len(hits)} hits returned (total: {total_count})")
            
            # Convert hits to Document objects
            documents = []
            for hit in hits:
                doc_id = hit.get("_id")
                index_name = hit.get("_index")
                source = hit.get("_source", {})
                highlight = hit.get("highlight", {})
                score = hit.get("_score", 0.0)
                
                # Try to extract content from various possible fields
                content = None
                for field in self.COMMON_TEXT_FIELDS:
                    if field in source and source[field]:
                        content = str(source[field])
                        break
                
                # Prefer highlighted content if available
                if highlight:
                    highlighted_texts = []
                    for field, snippets in highlight.items():
                        highlighted_texts.extend(snippets)
                    if highlighted_texts:
                        content = "\n...\n".join(highlighted_texts)
                
                # Fallback: use first non-empty string field
                if not content:
                    for key, value in source.items():
                        if isinstance(value, str) and len(value) > 10:
                            content = value
                            break
                
                # Last resort: stringify the entire source
                if not content:
                    content = str(source)
                
                # Extract title from various possible fields
                title = None
                for title_field in ["title", "name", "news_title", "post_title", "subject"]:
                    if title_field in source and source[title_field]:
                        title = str(source[title_field])
                        break
                
                if not title:
                    title = f"Document from {index_name}"
                
                # Create document with chunk
                document = Document(
                    id=f"{index_name}:{doc_id}",  # Include index name for uniqueness
                    title=title,
                    url=source.get("url") or source.get("link"),
                    chunks=[Chunk(content=content, similarity=score)]
                )
                documents.append(document)
            
            logger.info(f"Returning {len(documents)} documents from unified search")
            return documents
            
        except Exception as e:
            logger.error(f"Error in Elasticsearch unified search: {e}")
            import traceback
            traceback.print_exc()
            return []
