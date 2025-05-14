#!/bin/bash

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "kubectl is not installed. Please install Kubernetes command-line tool first."
    exit 1
fi

# Check if Kubernetes is running
if ! kubectl cluster-info &> /dev/null; then
    echo "Kubernetes cluster not available. Please start your local Kubernetes cluster."
    exit 1
fi

# Build Docker images
echo "Building Docker images..."
./build_local_images.sh

# Apply Kubernetes configuration
echo "Deploying to Kubernetes..."
kubectl apply -f k8s/simple_deployment.yaml

# Wait for pods to be ready
echo "Waiting for pods to be ready..."
kubectl wait --namespace rag-chatbot --for=condition=ready pod --selector=app=frontend --timeout=300s || true
kubectl wait --namespace rag-chatbot --for=condition=ready pod --selector=app=llm-service --timeout=300s || true

echo ""
echo "Application is now running!"
echo "Frontend: http://localhost:30300"
echo "API: http://localhost:30800"
echo ""
echo "Press Ctrl+C to stop and clean up..."

# Wait for user to cancel
read -n 1 -s -r -p "Press any key to stop and clean up..."
echo ""

# Clean up
echo "Cleaning up..."
kubectl delete -f k8s/simple_deployment.yaml 