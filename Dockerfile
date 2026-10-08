ARG REGISTRY=""
FROM ${REGISTRY}python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app:/app/src:/app/tests" \
    PORT=8000

# Install requirements with fallback chain (exact pattern from tafakormag)
COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=1000 -r requirements.txt || \
    (echo "Primary PyPI registry failed/unreachable. Trying Tsinghua mirror..." && \
     pip install --no-cache-dir --default-timeout=1000 -r requirements.txt --index-url https://pypi.tuna.tsinghua.edu.cn/simple/) || \
    (echo "Tsinghua mirror failed/unreachable. Falling back to devneeds mirror..." && \
     pip install --no-cache-dir --default-timeout=1000 -r requirements.txt --index-url https://pypi.devneeds.ir/simple/)

# Copy project files
COPY . .

# Create persistent and static directories
RUN mkdir -p /app/test-static /app/test-media /app/data

# Entrypoint setup
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
