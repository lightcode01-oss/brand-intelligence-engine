# =============================================================================
# Nomen API — Production Multi-Stage Dockerfile
# Stage 1: builder  — compiles dependencies in an isolated layer
# Stage 2: runner   — minimal runtime image (no build tools)
# =============================================================================

# ---- Stage 1: dependency builder ----
FROM python:3.12-slim AS builder

WORKDIR /build
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install build dependencies (removed in runner stage)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    libssl-dev \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create isolated virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies with pip cache disabled
COPY apps/api/requirements.txt .
RUN pip install --upgrade pip --no-cache-dir \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir \
        gunicorn==22.0.0 \
        uvicorn[standard]==0.30.1 \
        pytest-asyncio==0.23.7 \
        aiosqlite==0.20.0

# ---- Stage 2: production runner ----
FROM python:3.12-slim AS runner

LABEL org.opencontainers.image.title="Nomen API"
LABEL org.opencontainers.image.description="Nomen Brand Intelligence Platform — FastAPI Backend"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.vendor="Nomen AI"
LABEL org.opencontainers.image.licenses="MIT"

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH="/app"

# Runtime-only native libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy compiled virtualenv from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application source code
COPY apps/api/ /app/

# Create unprivileged runtime user
RUN groupadd --system --gid 10001 appgroup \
    && useradd --system --uid 10001 --gid appgroup --no-create-home appuser \
    && chown -R appuser:appgroup /app

USER appuser

EXPOSE 8000

# Healthcheck using internal endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default: Gunicorn with Uvicorn workers for production throughput
CMD ["gunicorn", "app.main:app", \
    "--worker-class", "uvicorn.workers.UvicornWorker", \
    "--workers", "2", \
    "--bind", "0.0.0.0:8000", \
    "--timeout", "120", \
    "--graceful-timeout", "30", \
    "--keep-alive", "5", \
    "--access-logfile", "-", \
    "--error-logfile", "-", \
    "--log-level", "info"]
