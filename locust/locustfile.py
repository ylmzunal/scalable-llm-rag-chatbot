import time
import json
import random
from locust import HttpUser, task, between

# Sample questions for load testing
SAMPLE_QUESTIONS = [
    "What is the capital of France?",
    "How does a transformer neural network work?",
    "Explain the concept of retrieval-augmented generation.",
    "What are the benefits of Kubernetes for scaling applications?",
    "How can I implement horizontal pod autoscaling in Kubernetes?",
    "What is the difference between a StatefulSet and a Deployment in Kubernetes?",
    "Explain the concept of a service mesh.",
    "What are the best practices for securing a Kubernetes cluster?",
    "How does vLLM optimize LLM inference?",
    "What is the role of a vector database in a RAG system?"
]

class ChatbotUser(HttpUser):
    """
    Simulates a user interacting with the chatbot API.
    """
    wait_time = between(3, 10)  # Wait between 3-10 seconds between tasks
    
    def on_start(self):
        """
        Initialize the user session.
        """
        self.client.headers = {'Content-Type': 'application/json'}
        self.conversation_history = []
    
    @task(10)
    def ask_question(self):
        """
        Send a random question to the chatbot API.
        Weight: 10 (higher priority)
        """
        # Select a random question
        question = random.choice(SAMPLE_QUESTIONS)
        
        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": question})
        
        # Keep only the last 5 messages to avoid large payloads
        if len(self.conversation_history) > 5:
            self.conversation_history = self.conversation_history[-5:]
        
        # Prepare request payload
        payload = {
            "messages": self.conversation_history,
            "use_rag": True,
            "temperature": 0.7,
            "max_tokens": 1024
        }
        
        # Send request and measure response time
        start_time = time.time()
        with self.client.post("/chat", json=payload, catch_response=True) as response:
            duration = time.time() - start_time
            
            if response.status_code == 200:
                try:
                    # Parse response
                    data = response.json()
                    
                    # Check if response contains expected fields
                    if "response" in data:
                        # Add assistant response to conversation history
                        self.conversation_history.append({"role": "assistant", "content": data["response"]})
                        
                        # Log response time for monitoring
                        response.metadata["response_time"] = duration
                        
                        # Mark as success
                        response.success()
                    else:
                        response.failure(f"Invalid response format: {data}")
                except json.JSONDecodeError:
                    response.failure("Response could not be decoded as JSON")
            else:
                response.failure(f"Request failed with status code: {response.status_code}")
    
    @task(3)
    def health_check(self):
        """
        Check the health endpoint.
        Weight: 3 (lower priority)
        """
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed with status code: {response.status_code}")
    
    @task(1)
    def ask_without_rag(self):
        """
        Send a question without using RAG.
        Weight: 1 (lowest priority)
        """
        # Select a random question
        question = random.choice(SAMPLE_QUESTIONS)
        
        # Prepare request payload without RAG
        payload = {
            "messages": [{"role": "user", "content": question}],
            "use_rag": False,
            "temperature": 0.7,
            "max_tokens": 1024
        }
        
        # Send request
        with self.client.post("/chat", json=payload, catch_response=True) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "response" in data:
                        response.success()
                    else:
                        response.failure(f"Invalid response format: {data}")
                except json.JSONDecodeError:
                    response.failure("Response could not be decoded as JSON")
            else:
                response.failure(f"Request failed with status code: {response.status_code}") 