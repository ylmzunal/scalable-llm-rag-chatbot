# Scalable LLM RAG Chatbot with Kubernetes

A scalable RAG (Retrieval-Augmented Generation) chatbot built with Next.js, FastAPI, and deployed on Kubernetes.

## Features

- **RAG Architecture**: Combines retrieval-based and generative approaches for more accurate responses
- **Scalable Infrastructure**: Kubernetes-based deployment for scalability and resilience
- **Modern UI**: Clean, responsive interface built with Next.js and TailwindCSS
- **API Backend**: FastAPI service for handling LLM interactions
- **Vector Database**: ChromaDB for efficient similarity search

## Prerequisites

- Docker Desktop with Kubernetes enabled
- kubectl command-line tool
- Node.js (for local development)
- Python 3.10+ (for local development)

## Quick Start

### Running with Kubernetes

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/scalable-llm-rag-chatbot.git
   cd scalable-llm-rag-chatbot
   ```

2. Run the application:
   ```bash
   ./run_kubernetes.sh
   ```

   This script will:
   - Build the Docker images
   - Deploy the application to Kubernetes
   - Set up port forwarding

3. Access the application:
   - Frontend: http://localhost:30300
   - API: http://localhost:30800

4. Clean up when done:
   ```bash
   ./cleanup_all.sh
   ```

## Project Structure

```
.
├── app/                      # Application code
│   ├── api/                  # FastAPI backend
│   └── frontend/             # Next.js frontend
├── k8s/                      # Kubernetes configurations
│   └── local/                # Local development configuration
├── vector_db/               # Vector database files
├── Dockerfile               # Backend service Dockerfile
├── Dockerfile.frontend      # Frontend Dockerfile
├── build_local_images.sh    # Script to build Docker images
├── run_kubernetes.sh        # Script to deploy to Kubernetes
└── cleanup_all.sh           # Cleanup script
```

## Development

### Local Development

For local development without Kubernetes, you can run the frontend and backend separately:

#### Backend (FastAPI)

```bash
cd app/api
python -m uvicorn main_local:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend (Next.js)

```bash
cd app/frontend
npm install
npm run dev
```

## License

[MIT License](LICENSE) 