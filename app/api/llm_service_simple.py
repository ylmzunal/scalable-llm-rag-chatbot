import logging
from typing import Optional, List, Dict, Any
import asyncio
import random

logger = logging.getLogger(__name__)

class SimpleLLMService:
    """A mock LLM service that returns pre-defined responses for testing purposes."""
    
    def __init__(self):
        logger.info("Initializing Simple LLM Service")
        self.responses = {
            # LLM related
            "what is llm": "LLM stands for Large Language Model. It's a type of artificial intelligence model trained on vast amounts of text data to generate human-like text, understand context, and perform various language tasks.",
            "what is a llm": "LLM stands for Large Language Model. It's a type of artificial intelligence model trained on vast amounts of text data to generate human-like text, understand context, and perform various language tasks.",
            "what is a large language model": "A Large Language Model (LLM) is a type of artificial intelligence model trained on vast amounts of text data to generate human-like text, understand context, and perform various language tasks.",
            "explain llm": "LLM stands for Large Language Model. It's a type of artificial intelligence model trained on vast amounts of text data to generate human-like text, understand context, and perform various language tasks.",
            
            # RAG related
            "what is rag": "RAG stands for Retrieval-Augmented Generation. It's a technique that enhances language models by first retrieving relevant information from a knowledge base and then using that information to generate more accurate and informed responses.",
            "what is retrieval augmented generation": "Retrieval-Augmented Generation (RAG) is a technique that enhances language models by first retrieving relevant information from a knowledge base and then using that information to generate more accurate and informed responses.",
            "explain rag": "RAG (Retrieval-Augmented Generation) is a technique that enhances language models by first retrieving relevant information from a knowledge base and then using that information to generate more accurate and informed responses.",
            "how does rag work": "RAG (Retrieval-Augmented Generation) works by combining information retrieval with text generation. When a query is received, the system first searches a knowledge base to find relevant documents or information. These retrieved documents are then provided as context to the language model, which generates a response based on both the query and the retrieved information. This approach helps ground the model's responses in factual information and reduces hallucinations.",
            
            # Kubernetes related
            "what is kubernetes": "Kubernetes is an open-source container orchestration platform that automates the deployment, scaling, and management of containerized applications. It helps manage applications across clusters of hosts and provides mechanisms for application deployment, maintenance, and scaling.",
            "explain kubernetes": "Kubernetes is an open-source container orchestration platform that automates the deployment, scaling, and management of containerized applications. It helps manage applications across clusters of hosts and provides mechanisms for application deployment, maintenance, and scaling.",
            "kubernetes scaling": "Kubernetes provides several mechanisms for scaling applications: Horizontal Pod Autoscaling adjusts the number of pods based on CPU or memory usage, Vertical Pod Autoscaling adjusts resource requests and limits, and Cluster Autoscaling adjusts the number of nodes in the cluster. These features enable applications to automatically scale based on demand, ensuring efficient resource utilization.",
            
            # Chatbot/AI related
            "what is ai": "AI (Artificial Intelligence) refers to systems or machines that mimic human intelligence to perform tasks and can iteratively improve themselves based on the information they collect. In the context of this chatbot, AI is used to understand natural language queries and generate informative responses.",
            "what is chatbot": "A chatbot is a software application designed to simulate human-like conversation through text or voice interactions. Chatbots use natural language processing (NLP) and artificial intelligence to understand user queries and provide relevant responses. This RAG chatbot specifically uses retrieval-augmented generation to provide more accurate and informed answers.",
            "what is a chatbot": "A chatbot is a software application designed to simulate human-like conversation through text or voice interactions. Chatbots use natural language processing (NLP) and artificial intelligence to understand user queries and provide relevant responses. This RAG chatbot specifically uses retrieval-augmented generation to provide more accurate and informed answers.",
            
            # Project specific
            "what is this project": "This is a Scalable LLM RAG Chatbot with Kubernetes - a Master's Project Demo. It demonstrates the implementation of a Retrieval-Augmented Generation (RAG) chatbot that utilizes a language model, integrates with a vector database for knowledge retrieval, and is designed to be deployed on Kubernetes for scalability.",
            "how does this work": "This RAG chatbot works by combining a language model with a vector database. When you ask a question, the system retrieves relevant information from its knowledge base and uses that to inform the model's response. The entire system is designed to be deployed on Kubernetes, allowing it to scale based on demand.",
        }
        
    async def generate(
        self, 
        prompt: str, 
        temperature: float = 0.7, 
        max_tokens: int = 1024,
        system_prompt: Optional[str] = None
    ) -> str:
        """Generate a response based on pre-defined answers or a generic response."""
        # Simulate processing time
        await asyncio.sleep(random.uniform(0.5, 1.5))
        
        # Normalize prompt for matching
        normalized_prompt = prompt.lower().strip()
        
        # Look for matching responses
        for key, response in self.responses.items():
            if key in normalized_prompt:
                logger.info(f"Found matching response for: {normalized_prompt}")
                return response
        
        # Default response
        logger.info(f"No specific response for: {normalized_prompt}")
        return f"I don't have specific information about '{prompt}', but I can help with information about LLMs, RAG, or Kubernetes. Please ask me about these topics."

    async def shutdown(self):
        """Clean up resources."""
        logger.info("Shutting down Simple LLM service")
        # No actual resources to clean up

async def get_llm_engine():
    """Initialize and return the Simple LLM engine."""
    try:
        logger.info("Initializing Simple LLM engine")
        return SimpleLLMService()
        
    except Exception as e:
        logger.error(f"Failed to initialize Simple LLM engine: {str(e)}", exc_info=True)
        raise 