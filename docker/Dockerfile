FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir uv

# Copy requirements first
COPY requirements.txt .

# Install dependencies
RUN uv pip install -r requirements.txt --system

# Copy the rest of the application
COPY . .

# Set PYTHONPATH to include the app directory
ENV PYTHONPATH=/app

# Run the application with hot-reload and debug mode
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-dir", "/app/src", "--log-level", "debug"]
