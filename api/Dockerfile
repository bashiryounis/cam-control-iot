# Use official Python slim image
FROM python:3.12-slim

# Install system dependencies for OpenCV and other packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libgl1 \
    libglib2.0-0 \
    libgtk-3-0 \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install minio client (mc)
RUN curl https://dl.min.io/client/mc/release/linux-amd64/mc \
    --create-dirs \
    -o /usr/local/bin/mc && \
    chmod +x /usr/local/bin/mc

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:${PATH}"

# Set working directory
WORKDIR /app

# Copy poetry files and install dependencies
COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-root

# Copy the rest of the application
COPY . .

# Set Python environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Expose port
EXPOSE 8000

# Run app
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
