# Scalable LLM RAG Chatbot with Kubernetes

This project demonstrates a scalable LLM-based RAG (Retrieval-Augmented Generation) chatbot deployed on Kubernetes infrastructure. It uses Mistral-7B as the base model and vLLM for efficient serving.

## Project Components

- **LLM Service**: Mistral-7B model served using vLLM for efficient inference
- **Vector Database**: Stores document embeddings for retrieval
- **RAG Pipeline**: Enhances LLM responses with relevant context from the vector database
- **Web Interface**: Simple UI for interacting with the chatbot
- **Kubernetes Deployment**: Scalable infrastructure with autoscaling capabilities
- **Load Testing**: Locust configuration for performance testing

## Prerequisites

- Docker
- Kubernetes cluster (minikube, kind, or cloud provider)
- kubectl
- Helm
- Python 3.9+

## Setup Instructions

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Deploy to Kubernetes: `kubectl apply -f k8s/`
4. Run load tests: `locust -f locust/locustfile.py`

## Architecture

```
                                 ┌───────────────┐
                                 │   Web UI      │
                                 └───────┬───────┘
                                         │
                                         ▼
┌───────────────┐              ┌───────────────┐
│  Vector DB    │◄────────────►│  API Gateway  │
└───────────────┘              └───────┬───────┘
                                       │
                                       ▼
                               ┌───────────────┐
                               │  LLM Service  │
                               │  (Mistral-7B) │
                               └───────────────┘
```

## Load Testing

The project includes Locust configuration for load testing the deployed application. This helps measure performance metrics such as:

- Response time under various loads
- Maximum throughput
- System stability under heavy traffic
- Resource utilization patterns

## License

MIT 