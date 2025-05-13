import os
import logging
import asyncio
from typing import List, Dict, Any, Optional
import httpx
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

logger = logging.getLogger(__name__)

class VectorDBService:
    def __init__(self, client):
        self.client = client
        self.collection_name = "documents"
        self.collection = self._get_or_create_collection()
        self.embedding_model = self._load_embedding_model()
        logger.info(f"Vector DB Service initialized with collection: {self.collection_name}")

    def _load_embedding_model(self):
        """Load the embedding model for text embeddings"""
        try:
            # Using sentence-transformers for embeddings
            model_name = "sentence-transformers/all-MiniLM-L6-v2"
            logger.info(f"Loading embedding model: {model_name}")
            return SentenceTransformer(model_name)
        except Exception as e:
            logger.error(f"Failed to load embedding model: {str(e)}", exc_info=True)
            raise

    def _get_or_create_collection(self):
        """Get or create the document collection"""
        try:
            # Create embedding function
            sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            
            # Get or create collection
            try:
                collection = self.client.get_collection(
                    name=self.collection_name,
                    embedding_function=sentence_transformer_ef
                )
                logger.info(f"Retrieved existing collection: {self.collection_name}")
            except Exception:
                collection = self.client.create_collection(
                    name=self.collection_name,
                    embedding_function=sentence_transformer_ef
                )
                logger.info(f"Created new collection: {self.collection_name}")
            
            return collection
        except Exception as e:
            logger.error(f"Failed to get or create collection: {str(e)}", exc_info=True)
            raise

    async def add_documents(self, documents: List[Dict[str, str]]):
        """
        Add documents to the vector database.
        
        Args:
            documents: List of document dictionaries with 'id', 'text', and 'metadata' keys
        """
        try:
            # Prepare documents for insertion
            ids = [doc["id"] for doc in documents]
            texts = [doc["text"] for doc in documents]
            metadatas = [doc.get("metadata", {}) for doc in documents]
            
            # Add documents to collection
            self.collection.add(
                ids=ids,
                documents=texts,
                metadatas=metadatas
            )
            logger.info(f"Added {len(documents)} documents to vector database")
            
        except Exception as e:
            logger.error(f"Failed to add documents: {str(e)}", exc_info=True)
            raise

    async def query(self, query_text: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """
        Query the vector database for documents similar to the query text.
        
        Args:
            query_text: The text to search for
            n_results: Number of results to return
            
        Returns:
            List of document dictionaries with text and metadata
        """
        try:
            # Query the collection
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            
            # Format results
            documents = []
            if results and results["documents"]:
                for i, doc in enumerate(results["documents"][0]):
                    documents.append({
                        "text": doc,
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "id": results["ids"][0][i] if results["ids"] else f"doc_{i}",
                        "distance": results["distances"][0][i] if "distances" in results and results["distances"] else None
                    })
            
            logger.info(f"Retrieved {len(documents)} documents for query: {query_text[:50]}...")
            return documents
            
        except Exception as e:
            logger.error(f"Error querying vector database: {str(e)}", exc_info=True)
            raise

    async def shutdown(self):
        """Clean up resources"""
        logger.info("Shutting down vector database service")
        # ChromaDB client doesn't require explicit cleanup

async def get_vector_db():
    """
    Initialize and return the vector database service.
    """
    try:
        # Get connection details from environment variables
        host = os.environ.get("VECTOR_DB_HOST", "localhost")
        port = os.environ.get("VECTOR_DB_PORT", "8080")
        
        # Initialize ChromaDB client
        logger.info(f"Connecting to ChromaDB at {host}:{port}")
        
        # Try to connect to the ChromaDB server
        try:
            # First try HTTP client (for server mode)
            client = chromadb.HttpClient(host=host, port=port)
            # Test connection
            client.heartbeat()
            logger.info("Connected to ChromaDB server successfully")
        except Exception as e:
            logger.warning(f"Failed to connect to ChromaDB server: {str(e)}")
            logger.info("Falling back to persistent client")
            
            # Fall back to persistent client
            persist_directory = os.environ.get("CHROMA_PERSIST_DIRECTORY", "./vector_db/data")
            client = chromadb.PersistentClient(path=persist_directory)
            logger.info(f"Using persistent ChromaDB client with directory: {persist_directory}")
        
        return VectorDBService(client)
        
    except Exception as e:
        logger.error(f"Failed to initialize vector database: {str(e)}", exc_info=True)
        raise 