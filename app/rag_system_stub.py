"""
Stub RAG System for initial setup
Provides basic functionality without heavy ML dependencies
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class RAGSystem:
    """Stub RAG system for initial testing without ML dependencies"""

    def __init__(self, model_name: str = ""):
        """Initialize stub RAG system"""
        self.model_name = model_name
        self.documents = {}  # Simple in-memory storage
        logger.info("RAG system initialized in stub mode")

    def add_document(self, doc_id: str, document_data: Dict[str, Any]) -> bool:
        """Add document to the system"""
        try:
            self.documents[doc_id] = document_data
            logger.info(f"Document {doc_id} added to RAG system")
            return True
        except Exception as e:
            logger.error(f"Error adding document: {str(e)}")
            return False

    def remove_document(self, doc_id: str) -> bool:
        """Remove document from the system"""
        try:
            if doc_id in self.documents:
                del self.documents[doc_id]
                logger.info(f"Document {doc_id} removed from RAG system")
                return True
            return False
        except Exception as e:
            logger.error(f"Error removing document: {str(e)}")
            return False

    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Simple text search without embeddings"""
        try:
            results = []
            for doc_id, doc_data in self.documents.items():
                # Simple text matching
                if query.lower() in str(doc_data).lower():
                    result = doc_data.copy()
                    result['id'] = doc_id
                    result['similarity_score'] = 0.8  # Placeholder score
                    results.append(result)
            
            return results[:limit]
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            return []

    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        return {
            "total_documents": len(self.documents),
            "embedding_model": "stub_mode",
            "vector_store": "in_memory"
        }