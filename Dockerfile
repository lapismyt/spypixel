FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install uv
RUN pip install uv

# Install dependencies
RUN uv sync --frozen

# Copy application code
COPY spypixel/ ./spypixel/

# Expose port
EXPOSE 23232

# Run the application
CMD ["uv", "run", "uvicorn", "spypixel.app:app", "--host", "0.0.0.0", "--port", "23232"]
