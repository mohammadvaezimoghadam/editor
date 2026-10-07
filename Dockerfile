# Multi-stage / lightweight Python 3.12 image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app:/app/tests" \
    PORT=8000

# Set work directory
WORKDIR /app

# Install system dependencies (curl for healthcheck) with fallback and retries
RUN apt-get update --fix-missing && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app/

# Install wagtail-ai in editable mode
RUN pip install --no-cache-dir -e .

# Create directories for static, media, and SQLite DB
RUN mkdir -p /app/test-static /app/test-media /app/data

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

# Expose port
EXPOSE 8000

# Run entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
