# Multi-stage build for QueryMind SQL-RAG System
FROM python:3.11-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt /tmp/
RUN pip install --no-cache-dir --user -r /tmp/requirements.txt

# Production stage
FROM python:3.11-slim AS production

# Security: Create non-root user
RUN groupadd -r querymind && useradd -r -g querymind querymind

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy Python packages from builder
COPY --from=builder /root/.local /home/querymind/.local

# Create app directory and set permissions
WORKDIR /app
RUN chown -R querymind:querymind /app

# Copy application code
COPY --chown=querymind:querymind backend/ ./backend/
COPY --chown=querymind:querymind frontend/ ./frontend/

# Switch to non-root user
USER querymind

# Add local Python packages to PATH
ENV PATH=/home/querymind/.local/bin:$PATH
ENV PYTHONPATH=/app/backend

# Health check (Azure Container Apps compatible)
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

# Production server with optimized workers
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
