# Use official Python image with Debian (comes with OpenSSL, not LibreSSL)
FROM python:3.11-slim

# Prevent interactive prompts during build
ENV DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app

# Install OpenSSL + certificates + build tools + git
RUN apt-get update && apt-get install -y --no-install-recommends \
        openssl \
        ca-certificates \
        build-essential \
        libssl-dev \
        git \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY requirements.txt .

# Install Python dependencies (this will now link to OpenSSL correctly)
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI with uvicorn (default command, can be overridden in docker-compose)
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
