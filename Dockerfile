FROM nvidia/cuda:12.1.0-devel-ubuntu22.04

# Set working directory
WORKDIR /app

# Install Python and other dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    python3-dev \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ /app/
COPY vector_db/ /vector_db/

# Set environment variables
ENV PYTHONPATH=/app
ENV MODEL_ID="mistralai/Mistral-7B-v0.1"
ENV CUDA_VISIBLE_DEVICES=0

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"] 