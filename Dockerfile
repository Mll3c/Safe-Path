# Use lightweight Python image
FROM python:3.14

# Prevent Python from writing pyc files and enable real-time logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies needed for dev
RUN apt-get update --fix-missing && \
    apt-get install -y --no-install-recommends \
    build-essential libpq-dev netcat-openbsd \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Copy project source code
COPY . .

