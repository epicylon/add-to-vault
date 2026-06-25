# Build stage: install dependencies into a virtual environment
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies (needed for compiling some Python packages)
RUN apt-get update && apt-get install -y --no-install-recommends     gcc     libffi-dev     && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip &&     pip install --no-cache-dir -r requirements.txt

# Runtime stage: only copy what we need
FROM python:3.11-slim

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Don't run as root
RUN useradd -m appuser && mkdir -p /app/data /app/vault && chown -R appuser:appuser /app
USER appuser

# Copy application code
COPY --chown=appuser:appuser ./app ./app

# Clean Python cache
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

