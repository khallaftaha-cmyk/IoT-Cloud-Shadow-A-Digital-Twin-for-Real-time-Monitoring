# ============================================
# Stage 1: Builder — install Python dependencies
# ============================================
FROM python:3.11-slim AS builder

WORKDIR /project

# Install build tools needed for compiling C extensions (psycopg2, argon2)
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# --prefix=/install puts all packages in a separate directory so we can
# copy ONLY the packages (not gcc/build tools) into the production image
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ============================================
# Stage 2: Production — lean runtime image
# ============================================
FROM python:3.11-slim

WORKDIR /project

# Only runtime libraries needed (libpq for PostgreSQL, curl for healthcheck)
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

# Create a non-root user so the app doesn't run as root
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Copy installed Python packages from builder stage
COPY --from=builder /install /usr/local
# Copy application source code
COPY . /project

# Switch to non-root user
USER appuser

EXPOSE 8000

# Docker uses this to check if the container is healthy
# If /health returns non-200 for 3 consecutive checks, container is marked unhealthy
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
