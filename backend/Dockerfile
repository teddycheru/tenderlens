# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=300 \
    DEBIAN_FRONTEND=noninteractive

# Configure apt to be more resilient with network issues
RUN echo 'Acquire::Retries "3";' > /etc/apt/apt.conf.d/80-retries && \
    echo 'Acquire::http::Timeout "120";' >> /etc/apt/apt.conf.d/80-retries && \
    echo 'Acquire::https::Timeout "120";' >> /etc/apt/apt.conf.d/80-retries

# Install system dependencies with better error handling
RUN apt-get update --fix-missing && \
    apt-get install -y --no-install-recommends --allow-unauthenticated \
    gcc \
    g++ \
    postgresql-client \
    curl \
    git \
    ca-certificates \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --default-timeout=100 --retries 5 --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch \
    && pip install --default-timeout=100 --retries 5 --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Make startup script executable
RUN chmod +x start.sh

# Expose default port for FastAPI
EXPOSE 8000

# Default command (overridden in docker-compose for backend, Celery, Flower)
# Use PORT env var for Render (defaults to 8000 for local development)
CMD ["./start.sh"]

