FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir fastapi==0.104.1 uvicorn==0.23.2 pydantic==2.4.2 httpx python-dotenv chromadb sentence-transformers

# Copy application code
COPY app/ /app/app/
COPY vector_db/ /vector_db/

# Set environment variables
ENV PYTHONPATH=/app
ENV USE_CPU=true
ENV CUDA_VISIBLE_DEVICES=""

# Expose port
EXPOSE 8000

# Command to run the application with CORS enabled
CMD ["uvicorn", "app.api.main_local:app", "--host", "0.0.0.0", "--port", "8000"] 