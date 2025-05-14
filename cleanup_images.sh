#!/bin/bash

# Print header
echo "=== Cleaning up Docker images ==="

# Remove the debug image
echo "Removing debug frontend image..."
docker rmi rag-chatbot/frontend:debug -f || true

# Remove old rag-chatbot images
echo "Removing old project images..."
docker rmi scalable-llm-rag-chatbot-frontend:latest -f || true

# Remove all dangling images
echo "Removing dangling images..."
docker image prune -f

# List remaining project images
echo -e "\nRemaining project images:"
docker images | grep -E 'rag-chatbot|scalable-llm-rag-chatbot'

echo -e "\nCleanup complete!"
echo "To remove all project images, run: docker rmi rag-chatbot/frontend:dev rag-chatbot/llm-service:dev -f" 