# Dockerfile for NeuroGym on Raspberry Pi 5 (ARM64)
# Optimized for ARM64 architecture with lightweight base image

FROM python:3.11-slim-bookworm

# Set working directory
WORKDIR /app

# Install system dependencies for scientific computing
# Keep it minimal for Raspberry Pi
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy only necessary files first (for better caching)
COPY pyproject.toml MANIFEST.in README.md LICENSE NOTICE ./
COPY neurogym ./neurogym

# Install Python dependencies
# Use CPU-only PyTorch to save space on Raspberry Pi
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -e .[rl] && \
    pip install --no-cache-dir fastapi uvicorn[standard] pydantic

# Expose port for web service
EXPOSE 8000

# Create a non-root user for security
RUN useradd -m -u 1000 neurogym && \
    chown -R neurogym:neurogym /app

USER neurogym

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Default command runs the web service
CMD ["uvicorn", "neurogym.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
