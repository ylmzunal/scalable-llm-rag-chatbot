#!/bin/bash

# Print header
echo "=== Complete Cleanup Script ==="

# Function to confirm action
confirm() {
    read -p "$1 (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        return 0
    else
        return 1
    fi
}

# 1. Clean up Kubernetes resources
if confirm "Do you want to delete all Kubernetes resources?"; then
    echo "Deleting Kubernetes resources..."
    kubectl delete -k k8s/overlays/dev || true
    echo "Kubernetes resources deleted."
fi

# 2. Clean up Docker images
if confirm "Do you want to delete all Docker images related to the project?"; then
    echo "Deleting Docker images..."
    
    # Get container IDs using project images
    CONTAINERS=$(docker ps -a | grep -E 'rag-chatbot|scalable-llm-rag-chatbot' | awk '{print $1}')
    
    # Stop and remove containers if any
    if [ ! -z "$CONTAINERS" ]; then
        echo "Stopping and removing containers..."
        docker stop $CONTAINERS || true
        docker rm $CONTAINERS || true
    fi
    
    # Remove project images
    echo "Removing project images..."
    docker rmi rag-chatbot/frontend:dev -f || true
    docker rmi rag-chatbot/frontend:debug -f || true
    docker rmi rag-chatbot/llm-service:dev -f || true
    docker rmi scalable-llm-rag-chatbot-frontend:latest -f || true
    
    # Remove dangling images
    echo "Removing dangling images..."
    docker image prune -f
    
    echo "Docker images deleted."
fi

# 3. Clean up port-forwarding processes
if confirm "Do you want to kill any port-forwarding processes?"; then
    echo "Killing port-forwarding processes..."
    pkill -f "kubectl port-forward" || true
    echo "Port-forwarding processes killed."
fi

echo -e "\nCleanup complete!" 