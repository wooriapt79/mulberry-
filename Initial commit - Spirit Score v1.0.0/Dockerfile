FROM python:3.11-slim

LABEL maintainer="CTO Koda <koda@mulberry.team>"
LABEL description="Mulberry Spirit Score System"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    redis-tools \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY database/ ./database/
COPY config/ ./config/

# Copy environment template
COPY .env.example .env.example

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/')" || exit 1

# Run application
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
