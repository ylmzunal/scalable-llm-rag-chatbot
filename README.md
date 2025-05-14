# Scalable LLM RAG Chatbot with Kubernetes

This project demonstrates a scalable LLM-based RAG (Retrieval-Augmented Generation) chatbot deployed on Kubernetes infrastructure. It uses Mistral-7B as the base model and vLLM for efficient serving.

## Project Components

- **LLM Service**: Mistral-7B model served using vLLM for efficient inference
- **Vector Database**: ChromaDB for storing document embeddings for retrieval
- **RAG Pipeline**: Enhances LLM responses with relevant context from the vector database
- **Web Interface**: Next.js frontend for interacting with the chatbot
- **Kubernetes Deployment**: Scalable infrastructure with autoscaling capabilities
- **Load Testing**: Locust configuration for performance testing

## Prerequisites

- Docker Desktop with Kubernetes enabled or any Kubernetes cluster
- kubectl
- Python 3.10+

## Setup Instructions

1. Clone this repository
2. Build the Docker images:
   ```bash
   ./build_local_images.sh
   ```
3. Deploy to Kubernetes:
   ```bash
   ./run_local_k8s.sh
   ```
4. Access the application:
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - Vector DB: http://localhost:8080

## Architecture

```
                                 ┌───────────────┐
                                 │   Next.js UI  │
                                 └───────┬───────┘
                                         │
                                         ▼
┌───────────────┐              ┌───────────────┐
│  ChromaDB     │◄────────────►│  FastAPI      │
└───────────────┘              └───────┬───────┘
                                       │
                                       ▼
                               ┌───────────────┐
                               │  LLM Service  │
                               │  (Mistral-7B) │
                               └───────────────┘
```

## Kubernetes Configuration

The application is deployed using Kubernetes with Kustomize for environment-specific configurations:

- `k8s/base/`: Base Kubernetes resources
- `k8s/overlays/dev/`: Development environment configuration
- `k8s/overlays/prod/`: Production environment configuration

See the [Kubernetes README](k8s/README.md) for detailed information on the Kubernetes setup.

## Load Testing

The project includes Locust configuration for load testing the deployed application. This helps measure performance metrics such as:

- Response time under various loads
- Maximum throughput
- System stability under heavy traffic
- Resource utilization patterns

## License

MIT 