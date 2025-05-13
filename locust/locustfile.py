import time
import json
import random
from locust import HttpUser, task, between

# Sample questions tailored for the SimpleMLLService's pre-defined responses
SAMPLE_QUESTIONS = [
    "What is LLM?",
    "Explain LLM",
    "What is a large language model?",
    "What is RAG?",
    "What is retrieval augmented generation?",
    "How does RAG work?",
    "What is Kubernetes?",
    "Explain Kubernetes",
    "Kubernetes scaling",
    "What is AI?",
    "What is a chatbot?",
    "What is this project?",
    "How does this work?"
]

class ChatbotUser(HttpUser):
    """
    Simulates a user interacting with the chatbot API.
    """
    wait_time = between(1, 3)  # Wait between 1-3 seconds between tasks (faster for local testing)
    
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
                        
                        # No need to manually track response time, Locust does this automatically
                        
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