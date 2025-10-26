from typing import List, Dict, Any, Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config
class Retriever:
    """Retrieves relevant documents for queries using semantic search"""

    def __init__(self, embedding_manager, vector_store):
        self.embedding_manager = embedding_manager
        self.vector_store = vector_store
        print("✓ Retriever initialized")
    def retrieve(self, query: str, top_k: int = None, filter_dict: Optional[Dict[str, Any]] = None,
                 return_scores: bool = False) -> str:
        """Retrieve relevant documents for a query"""
        top_k = top_k or config.TOP_K

        print(f"Embedding query: '{query[:50]}...'")
        query_embedding = self.embedding_manager.embed_text(query)

        # Search pinecone for relevant docs
        print(f"Searching for top {top_k} similar documents...")
        matches = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            filter_dict=filter_dict,
            include_metadata=True
        )

        if not matches:
            print("⚠️  No matching documents found")
            return "No relevant information found."

        print(f"✓ Found {len(matches)} relevant documents")
        context = self.format_context(matches, include_scores=return_scores)
        return context
    def retrieve_with_metadata(self, query: str, top_k: int = None,
                               filter_dict: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Retrieve documents with full metadata"""
        top_k = top_k or config.TOP_K

        query_embedding = self.embedding_manager.embed_text(query)
        matches = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            filter_dict=filter_dict,
            include_metadata=True
        )
        return matches
    def format_context(self, matches: List[Dict[str, Any]], include_scores: bool = False) -> str:
        """Format search results into context string for LLM"""
        if not matches:
            return "No relevant information found."

        context_parts = []
        for i, match in enumerate(matches, 1):
            text = match.get('text', '')
            score = match.get('score', 0)
            metadata = match.get('metadata', {})

            source = metadata.get('source', 'Unknown')
            doc_type = metadata.get('doc_type', 'document')
            category = metadata.get('category', '')

            # Make source more readable
            source_display = source.split('/')[-1] if '/' in source else source

            # Build context entry
            context_entry = f"--- Context {i}"
            if include_scores:
                context_entry += f" (Relevance: {score:.2f})"
            context_entry += " ---\n"
            context_entry += f"{text}\n"
            context_entry += f"[Source: {category}/{source_display} ({doc_type})]\n"

            # FIXED: Remove duplicate append (was on line 59)
            context_parts.append(context_entry)

        full_context = "\n".join(context_parts)
        return full_context
    def get_relevant_sources(self, query: str, top_k: int = None) -> List[str]:
        """Get list of source files for a query (useful for citations)"""
        matches = self.retrieve_with_metadata(query, top_k)
        sources = []
        for match in matches:
            source = match.get('metadata', {}).get('source', '')
            if source and source not in sources:
                sources.append(source)
        return sources 
    def search_by_category(self, query: str, category: str, top_k: int = None) -> str:
        """Search only within a specific category (blog/help)"""
        filter_dict = {'category': category}
        return self.retrieve(
            query=query,
            top_k=top_k,
            filter_dict=filter_dict
        )
    def search_by_doc_type(self, query: str, doc_type: str, top_k: int = None) -> str:
        """Search only within a specific document type (markdown/pdf/json)"""
        filter_dict = {'doc_type': doc_type}
        return self.retrieve(query=query, top_k=top_k, filter_dict=filter_dict)
                            