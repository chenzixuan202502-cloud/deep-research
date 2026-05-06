# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import logging
from src.rag.retriever import Document, Resource, Retriever

logger = logging.getLogger(__name__)


class CompositeRetriever(Retriever):
    """
    CompositeRetriever combines multiple retrievers to provide unified access.
    It merges results from all retrievers and deduplicates by URI and ID.
    """

    def __init__(self, retrievers: list[Retriever]):
        """
        Initialize the composite retriever with a list of retrievers.
        
        Args:
            retrievers: List of Retriever instances to combine
        """
        self.retrievers = retrievers
        logger.info(f"CompositeRetriever initialized with {len(retrievers)} providers")

    def list_resources(self, query: str | None = None) -> list[Resource]:
        """
        List resources from all retrievers and deduplicate by URI.
        
        Args:
            query: Optional query string to filter resources
            
        Returns:
            Deduplicated list of resources from all retrievers
        """
        all_resources = []
        seen_uris = set()
        
        for i, retriever in enumerate(self.retrievers):
            try:
                resources = retriever.list_resources(query)
                logger.info(f"Provider {i+1} ({retriever.__class__.__name__}) returned {len(resources)} resources")
                
                for resource in resources:
                    if resource.uri not in seen_uris:
                        all_resources.append(resource)
                        seen_uris.add(resource.uri)
            except Exception as e:
                logger.error(f"Error listing resources from provider {i+1} ({retriever.__class__.__name__}): {e}")
        
        logger.info(f"Total unique resources after deduplication: {len(all_resources)}")
        return all_resources

    def query_relevant_documents(
        self, query: str, resources: list[Resource] = []
    ) -> list[Document]:
        """
        Query relevant documents from all retrievers and deduplicate by ID.
        
        Args:
            query: Search query string
            resources: Optional list of resources to search within
            
        Returns:
            Deduplicated list of documents from all retrievers
        """
        all_documents = []
        seen_ids = set()
        
        logger.info(f"CompositeRetriever querying {len(self.retrievers)} providers with query: '{query}'")
        if resources:
            logger.info(f"Resources filter: {[r.uri for r in resources]}")
        else:
            logger.info("No resource filter specified, querying all providers")
        
        for i, retriever in enumerate(self.retrievers):
            try:
                documents = retriever.query_relevant_documents(query, resources)
                logger.info(f"Provider {i+1} ({retriever.__class__.__name__}) returned {len(documents)} documents")
                
                for doc in documents:
                    if doc.id not in seen_ids:
                        all_documents.append(doc)
                        seen_ids.add(doc.id)
            except Exception as e:
                logger.error(f"Error querying documents from provider {i+1} ({retriever.__class__.__name__}): {e}")
        
        logger.info(f"Total unique documents after deduplication: {len(all_documents)}")
        return all_documents
