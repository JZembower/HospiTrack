# File: Dockerfile
FROM python:3.11-slim

# Set a working directory
WORKDIR /app

# System packages useful for geocoding/http, optional depending on your code
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first for layer caching
COPY requirements_fastapi.txt /app/requirements_fastapi.txt

# Install Python deps
RUN pip install --no-cache-dir -r /app/requirements_fastapi.txt

# Optional: install debugpy so VS Code can attach for debugging
RUN pip install --no-cache-dir debugpy

# Copy app source
COPY . /app

# Environment variables (change at runtime with docker run -e or compose)
ENV PYTHONUNBUFFERED=1 \
    HOSPITRACK_DATA_PATH=/app/data \
    HOST=0.0.0.0 \
    PORT=8000

EXPOSE 8000 5678

# Default command: use Gunicorn + Uvicorn workers for production-like behavior.
# If you want to run with uvicorn directly for development, override CMD at runtime.
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "main:app", "-w", "2", "-b", "0.0.0.0:8000", "--log-level", "info"]