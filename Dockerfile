# PathwayIQ Production Docker Configuration
# Multi-stage build optimized for production deployment

# Stage 1: Frontend Build
FROM node:18-alpine AS frontend-build
WORKDIR /app/frontend

# Install dependencies
COPY frontend/package*.json ./
COPY frontend/yarn.lock ./
RUN yarn install --frozen-lockfile

# Copy source and build
COPY frontend/ .
RUN yarn build

# Stage 2: Backend Dependencies
FROM python:3.11-slim AS backend-deps

# Install system dependencies for audio processing and build tools
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    python3-dev \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Set up Python environment
WORKDIR /app/backend
COPY backend/requirements.txt .

# Install Python dependencies with wheel building
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --wheel-dir=/wheelhouse wheel && \
    pip wheel --no-cache-dir --wheel-dir=/wheelhouse -r requirements.txt && \
    pip install --no-cache-dir --find-links=/wheelhouse -r requirements.txt

# Stage 3: Production Runtime
FROM python:3.11-slim AS production

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 pathwayiq

# Set working directory
WORKDIR /app

# Copy Python dependencies from deps stage
COPY --from=backend-deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-deps /usr/local/bin /usr/local/bin

# Copy backend application
COPY backend/ ./backend/

# Copy frontend build
COPY --from=frontend-build /app/frontend/build ./frontend/build

# Copy production configuration
COPY backend/.env.production ./backend/.env

# Change ownership to non-root user
RUN chown -R pathwayiq:pathwayiq /app

# Switch to non-root user
USER pathwayiq

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/api/health || exit 1

# Production startup command
CMD ["python", "-m", "uvicorn", "backend.server:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "2"]