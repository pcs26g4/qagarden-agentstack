# production-ready Dockerfile for QA Garden AgentStack Deployment
FROM python:3.11-slim

# Install system dependencies for Playwright and general build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpangocairo-1.0-0 \
    libx11-xcb1 \
    libxcursor1 \
    libxi6 \
    libxtst6 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy the entire project
COPY . /app

# Install dependencies from the master requirements file
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers and their system dependencies
RUN playwright install --with-deps chromium

# Expose ports for all agents (Wrappers: 9001-9005, Backends: 8001-8005)
EXPOSE 9001 9002 9003 9004 9005 8001 8002 8003 8004 8005

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV MANAGED_MODE=true

# Start the full-stack ecosystem using the main orchestrator
CMD ["python", "qagarden_agents/main.py"]
