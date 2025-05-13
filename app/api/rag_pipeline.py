import logging
from typing import List, Dict, Any, Tuple, Optional
import asyncio

logger = logging.getLogger(__name__)

class RAGPipeline:
    def __init__(self, llm_service, vector_db_service):
        self.llm_service = llm_service
        self.vector_db_service = vector_db_service
        logger.info("RAG Pipeline initialized")

    async def generate_response(
        self, 
        query: str, 
        temperature: float = 0.7,
        max_tokens: int = 1024,
        n_results: int = 3
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Generate a response using the RAG pipeline.
        
        Args:
            query: The user query
            temperature: Temperature for LLM generation
            max_tokens: Maximum tokens to generate
            n_results: Number of documents to retrieve
            
        Returns:
            Tuple of (generated_response, retrieved_documents)
        """
        try:
            # Step 1: Retrieve relevant documents
            logger.info(f"Retrieving documents for query: {query[:50]}...")
            documents = await self.vector_db_service.query(query, n_results=n_results)
            
            if not documents:
                logger.warning("No documents retrieved, falling back to direct LLM response")
                response = await self.llm_service.generate(
                    query, 
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response, []
            
            # Step 2: Format the prompt with retrieved context
            context = self._format_context(documents)
            
            # Step 3: Generate response with context-enhanced prompt
            prompt = self._create_rag_prompt(query, context)
            
            # Step 4: Generate the final response
            response = await self.llm_service.generate(
                prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                system_prompt="You are a helpful assistant. Use the provided context to answer the question. If the context doesn't contain relevant information, say so and answer based on your knowledge."
            )
            
            logger.info(f"Generated RAG response for query: {query[:50]}...")
            return response, documents
            
        except Exception as e:
            logger.error(f"Error in RAG pipeline: {str(e)}", exc_info=True)
            raise

    def _format_context(self, documents: List[Dict[str, Any]]) -> str:
        """Format retrieved documents into context string"""
        context_parts = []
        
        for i, doc in enumerate(documents):
            # Extract document text and metadata
            text = doc["text"]
            metadata = doc.get("metadata", {})
            source = metadata.get("source", f"Document {i+1}")
            
            # Format document with source
            context_parts.append(f"[Document {i+1}] {source}:\n{text}\n")
        
        return "\n".join(context_parts)

    def _create_rag_prompt(self, query: str, context: str) -> str:
        """Create a prompt that includes the retrieved context"""
        return f"""
Context information:
{context}

Given the context information and not prior knowledge, answer the following question:
{query}
""" 