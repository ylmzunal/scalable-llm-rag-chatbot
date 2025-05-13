#!/bin/bash

# Activate virtual environment
source llmkubernetes/bin/activate

# Start vector database and frontend using docker-compose
echo "Starting vector database and frontend..."
docker-compose -f docker-compose.local.yml up -d

# Wait for vector database to be ready
echo "Waiting for vector database to be ready..."
sleep 10

# Start the API server
echo "Starting API server..."
PYTHONPATH=$(pwd) uvicorn app.api.main_local:app --host 0.0.0.0 --port 8000 --reload 