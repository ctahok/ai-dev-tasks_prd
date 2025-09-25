"""
RAG (Retrieval-Augmented Generation) System for Court Documents
Handles document embeddings, vector storage, and similarity search
"""

import os
import json
import logging
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import hashlib
from datetime import datetime

logger = logging.getLogger(__name__)

class RAGSystem:
    """RAG system for court document search and retrieval"""

    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        """
        Initialize RAG system

        Args:
            model_name: Name of the sentence transformer model to use
        """
        self.model_name = model_name
        self.model = None
        self.chroma_client = None
        self.collection = None
        self.collection_name = "court_documents"

        # Initialize components
        self._initialize_model()
        self._initialize_chroma()

    def _initialize_model(self):
        """Initialize the sentence transformer model"""
        try:
            logger.info(f"Loading model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            # Fallback to a simpler model
            try:
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("Fallback model loaded successfully")
            except Exception as e2:
                logger.error(f"Error loading fallback model: {str(e2)}")
                raise

    def _initialize_chroma(self):
        """Initialize ChromaDB client and collection"""
        try:
            # Initialize ChromaDB with persistent storage
            persist_directory = "./chroma_db"
            os.makedirs(persist_directory, exist_ok=True)

            self.chroma_client = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(anonymized_telemetry=False)
            )

            # Create or get collection
            self.collection = self.chroma_client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Azerbaijani court documents collection"}
            )

            logger.info("ChromaDB initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {str(e)}")
            raise

    def add_document(self, doc_id: str, doc_data: Dict[str, Any]):
        """
        Add a document to the RAG system

        Args:
            doc_id: Unique identifier for the document
            doc_data: Document data including metadata and text content
        """
        try:
            # Generate embeddings for the document
            embeddings, texts = self._generate_embeddings(doc_data)

            if not embeddings or not texts:
                logger.warning(f"No embeddings generated for document {doc_id}")
                return

            # Prepare metadata for ChromaDB
            metadata = self._prepare_metadata(doc_data, doc_id)

            # Add to collection
            self.collection.add(
                ids=[f"{doc_id}_{i}" for i in range(len(texts))],
                embeddings=embeddings,
                documents=texts,
                metadatas=[metadata] * len(texts)
            )

            logger.info(f"Added document {doc_id} to RAG system with {len(texts)} chunks")

        except Exception as e:
            logger.error(f"Error adding document {doc_id}: {str(e)}")

    def search_documents(self, query: str, n_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for documents using semantic similarity

        Args:
            query: Search query
            n_results: Number of results to return

        Returns:
            List of relevant documents with similarity scores
        """
        try:
            if not self.model or not self.collection:
                logger.error("RAG system not properly initialized")
                return []

            # Generate embedding for the query
            query_embedding = self.model.encode([query]).tolist()

            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=n_results,
                include=['documents', 'metadatas', 'distances']
            )

            # Process and format results
            formatted_results = []
            if results['ids'] and results['ids'][0]:
                for i, doc_id in enumerate(results['ids'][0]):
                    result = {
                        'id': doc_id,
                        'document_id': results['metadatas'][0][i].get('document_id', ''),
                        'similarity_score': 1 - results['distances'][0][i],  # Convert distance to similarity
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i]
                    }
                    formatted_results.append(result)

            return formatted_results

        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            return []

    def _generate_embeddings(self, doc_data: Dict[str, Any]) -> Tuple[List[List[float]], List[str]]:
        """
        Generate embeddings for document content

        Args:
            doc_data: Document data

        Returns:
            Tuple of (embeddings, texts)
        """
        try:
            texts = []

            # Get text content
            text_content = doc_data.get('text_content', '')
            metadata = doc_data.get('metadata', {})

            # Split text into chunks
            chunks = self._split_text(text_content, chunk_size=500, overlap=50)

            # Add metadata information as additional context
            metadata_text = self._format_metadata_for_embedding(metadata)
            if metadata_text:
                chunks.append(metadata_text)

            # Generate embeddings
            if chunks:
                embeddings = self.model.encode(chunks).tolist()
                return embeddings, chunks

            return [], []

        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            return [], []

    def _split_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Split text into overlapping chunks

        Args:
            text: Text to split
            chunk_size: Size of each chunk
            overlap: Overlap between chunks

        Returns:
            List of text chunks
        """
        if not text:
            return []

        words = text.split()
        chunks = []

        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)

        return chunks

    def _format_metadata_for_embedding(self, metadata: Dict[str, Any]) -> str:
        """
        Format metadata for embedding

        Args:
            metadata: Document metadata

        Returns:
            Formatted metadata string
        """
        formatted_parts = []

        # Key metadata fields to include
        key_fields = [
            'court_name', 'case_number', 'judge', 'case_type',
            'district', 'decision_type', 'applicant'
        ]

        for field in key_fields:
            if field in metadata and metadata[field]:
                formatted_parts.append(f"{field}: {metadata[field]}")

        # Add parties
        if 'parties' in metadata and metadata['parties']:
            parties_str = ', '.join(metadata['parties'][:3])  # Limit to first 3 parties
            formatted_parts.append(f"parties: {parties_str}")

        return ' | '.join(formatted_parts)

    def _prepare_metadata(self, doc_data: Dict[str, Any], doc_id: str) -> Dict[str, Any]:
        """
        Prepare metadata for ChromaDB storage

        Args:
            doc_data: Document data
            doc_id: Document ID

        Returns:
            Metadata dictionary for ChromaDB
        """
        metadata = doc_data.get('metadata', {})

        chroma_metadata = {
            'document_id': doc_id,
            'filename': doc_data.get('filename', ''),
            'processed_at': doc_data.get('processed_at', ''),
            'court_name': metadata.get('court_name', ''),
            'case_number': metadata.get('case_number', ''),
            'judge': metadata.get('judge', ''),
            'case_type': metadata.get('case_type', ''),
            'district': metadata.get('district', ''),
            'decision_type': metadata.get('decision_type', ''),
            'year': metadata.get('year', '')
        }

        return chroma_metadata

    def remove_document(self, doc_id: str):
        """
        Remove a document from the RAG system

        Args:
            doc_id: Document ID to remove
        """
        try:
            # Find all chunks for this document
            existing_ids = self.collection.get()['ids']
            doc_ids_to_delete = [id for id in existing_ids if id.startswith(f"{doc_id}_")]

            if doc_ids_to_delete:
                self.collection.delete(ids=doc_ids_to_delete)
                logger.info(f"Removed document {doc_id} from RAG system")
            else:
                logger.warning(f"No chunks found for document {doc_id}")

        except Exception as e:
            logger.error(f"Error removing document {doc_id}: {str(e)}")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get RAG system statistics

        Returns:
            Dictionary with system statistics
        """
        try:
            count = self.collection.count()
            return {
                'total_documents': count,
                'model_name': self.model_name,
                'collection_name': self.collection_name
            }
        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}")
            return {'error': str(e)}

    def retrain(self):
        """
        Retrain the RAG system (placeholder for future implementation)
        """
        logger.info("Retrain functionality to be implemented")
        pass

    def optimize(self):
        """
        Optimize the RAG system for better performance
        """
        try:
            # This could include index optimization, model fine-tuning, etc.
            logger.info("Optimizing RAG system...")

            # For now, just log the current state
            stats = self.get_stats()
            logger.info(f"Current RAG system stats: {stats}")

        except Exception as e:
            logger.error(f"Error optimizing RAG system: {str(e)}")
