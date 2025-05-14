#!/bin/bash

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "kubectl is not installed. Please install Kubernetes command-line tool first."
    exit 1
fi

# Check if Kubernetes is running
if ! kubectl cluster-info &> /dev/null; then
    echo "Kubernetes cluster not available. Please start your local Kubernetes cluster (Minikube, k3d, or Docker Desktop Kubernetes)."
    exit 1
fi

# Create namespace if it doesn't exist
kubectl apply -f k8s/base/namespace.yaml

# Apply kustomizations for dev environment
echo "Deploying application to local Kubernetes cluster..."
kubectl apply -k k8s/overlays/dev

# Wait for frontend pods to be ready
echo "Waiting for frontend pods to be ready..."
kubectl wait --namespace rag-chatbot --for=condition=ready pod --selector=app=frontend --timeout=300s || true

# Get the name of the frontend pod
FRONTEND_POD=$(kubectl get pods -n rag-chatbot -l app=frontend -o jsonpath="{.items[0].metadata.name}")

# Port-forward services to access them locally
echo "Setting up port-forwarding..."
if [ -n "$FRONTEND_POD" ]; then
    kubectl port-forward -n rag-chatbot pod/$FRONTEND_POD 3000:3000 &
    FRONTEND_PID=$!
    echo "Frontend running at: http://localhost:3000"
else
    echo "Warning: Frontend pod not found. Port forwarding for frontend will not be set up."
    FRONTEND_PID=""
fi

# Try to set up port forwarding for other services, but don't fail if they're not ready
kubectl port-forward -n rag-chatbot svc/llm-service 8000:8000 &
API_PID=$!
echo "API running at: http://localhost:8000"

echo "Application is now running locally with Kubernetes!"
echo ""
echo "Note: Some services might not be available if their pods are not ready."
echo "Press Ctrl+C to stop port-forwarding and clean up..."

# Function to clean up port-forwarding
function cleanup {
    echo "Stopping port-forwarding..."
    if [ -n "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID || true
    fi
    kill $API_PID || true
    echo "Done!"
}

# Setup trap to catch SIGINT (Ctrl+C)
trap cleanup INT

# Wait for user to cancel
wait 