FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv first
RUN pip install uv

# Copy project files and source code (needed for uv sync to work)
COPY pyproject.toml uv.lock README.md ./
COPY src/ ./src/

# Install dependencies (now that source code is available)
RUN uv sync --frozen

# Expose port
EXPOSE 8000

# Run the application
CMD ["uv", "run", "uvicorn", "src.ragger.api:app", "--host", "0.0.0.0", "--port", "8000"]
