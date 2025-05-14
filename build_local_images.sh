#!/bin/bash

# Build the LLM service image
echo "Building LLM service image..."
docker build -t rag-chatbot/llm-service:dev -f Dockerfile .

# Build the frontend image
echo "Building frontend image..."
docker build -t rag-chatbot/frontend:dev -f Dockerfile.frontend .

echo "Images built successfully!"
echo "You can now run ./run_local_k8s.sh to deploy to local Kubernetes" 