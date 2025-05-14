# Kubernetes Configuration for RAG Chatbot

This directory contains the Kubernetes configuration files for deploying the RAG Chatbot application.

## Directory Structure

- `base/`: Contains the base Kubernetes resources that are common across all environments
- `overlays/`: Contains environment-specific customizations
  - `dev/`: Development environment configuration
  - `prod/`: Production environment configuration

## Deployment

### Prerequisites

- Docker Desktop with Kubernetes enabled or any other Kubernetes cluster
- kubectl command-line tool

### Building Images

To build the Docker images for local development:

```bash
./build_local_images.sh
```

### Deploying to Local Kubernetes

To deploy the application to your local Kubernetes cluster:

```bash
./run_local_k8s.sh
```

This will:
1. Create the necessary namespace
2. Apply all Kubernetes resources
3. Set up port forwarding to access the services

### Accessing the Application

Once deployed, you can access the application at:
- Frontend: http://localhost:3000
- API: http://localhost:8000
- Vector DB: http://localhost:8080

## Configuration

The application is configured using Kustomize overlays:

- `dev` overlay: Used for local development
  - Reduces replica count to 1
  - Configures the LLM service to use CPU instead of GPU
  - Sets image pull policy to Never for local images

- `prod` overlay: Used for production deployment
  - Configures resources for production workloads
  - Uses proper image registry paths 