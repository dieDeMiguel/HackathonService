FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY pyproject.toml uv.lock ./

# Install uv
RUN pip install uv

# Install dependencies
RUN uv sync --frozen

# Copy source code
COPY src/ ./src/

# Expose port
EXPOSE 8000

# Run the application
CMD ["uv", "run", "uvicorn", "src.ragger.api:app", "--host", "0.0.0.0", "--port", "8000"]
