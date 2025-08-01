# AI Investment vs CEO Demographics Platform
# Docker container for complete deployment

FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY analytics/ ./analytics/
COPY data/ ./data/
COPY web/ ./web/
COPY *.md ./

# Copy nginx configuration
COPY docker/nginx.conf /etc/nginx/sites-available/default

# Copy supervisor configuration
COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Create necessary directories
RUN mkdir -p /var/log/supervisor /var/log/nginx

# Expose ports
EXPOSE 80 8000

# Health check
HEALTHCHEK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

# Start supervisor
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

# Metadata
LABEL maintainer="Tatsuru Kikuchi <tatsuru.kikuchi@gmail.com>"
LABEL description="AI Investment vs CEO Demographics Research Platform"
LABEL version="1.0.0"
LABEL repository="https://github.com/Tatsuru-Kikuchi/AI-Investment-CEO"