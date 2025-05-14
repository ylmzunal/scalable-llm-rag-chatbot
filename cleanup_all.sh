#!/bin/bash

# Set colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting cleanup process...${NC}"

# Kill any port-forwarding processes
echo -e "${GREEN}Killing port-forwarding processes...${NC}"
pkill -f "kubectl port-forward"

# Delete all Kubernetes resources
echo -e "${GREEN}Deleting Kubernetes resources...${NC}"
kubectl delete -f k8s/local/deployment.yaml || true
echo -e "${GREEN}Kubernetes resources deleted.${NC}"

# Clean up Docker images
echo -e "${GREEN}Cleaning up Docker images...${NC}"
docker image rm -f rag-chatbot/frontend:dev rag-chatbot/llm-service:dev || true
echo -e "${GREEN}Docker images removed.${NC}"

# Clean up vector DB data
echo -e "${GREEN}Cleaning up vector DB data...${NC}"
if [ -d "vector_db/data" ]; then
    rm -rf vector_db/data
    echo -e "${GREEN}Vector DB data removed.${NC}"
else
    echo -e "${YELLOW}No vector DB data found.${NC}"
fi

# Clean up any temporary files
echo -e "${GREEN}Cleaning up temporary files...${NC}"
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name ".pytest_cache" -type d -exec rm -rf {} +
find . -name "*.log" -delete
echo -e "${GREEN}Temporary files removed.${NC}"

echo -e "${YELLOW}Cleanup complete!${NC}" 