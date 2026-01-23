FROM python:3.12-slim-bookworm

WORKDIR /app

# Install system dependencies for OpenCV Headless
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libxcb1 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uv/bin/uv

# Copy requirements
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN /uv/bin/uv sync --frozen --no-dev

# Copy application code
COPY app /app/app

# Set path to use venv
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Expose the API port
EXPOSE 8000

# Start the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
