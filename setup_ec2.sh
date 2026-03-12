#!/bin/bash

# QA Garden EC2 Setup Script
# This script installs all necessary dependencies for running AgentStack on a fresh Ubuntu/Debian EC2 instance.

set -e

echo "🚀 Starting QA Garden EC2 Setup..."

# 1. Update system packages
echo "Updating system packages..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv git curl wget

# 2. Install Playwright system dependencies
echo "Installing Playwright system dependencies..."
# This installs the libraries needed for Chromium to run on Linux
sudo npx playwright install-deps chromium

# 3. Create/Update Virtual Environment
echo "Setting up Python virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate

# 4. Install Python requirements
echo "Installing Python requirements..."
pip install --upgrade pip
pip install -r requirements.txt
playwright install chromium

# 5. Setup Environment Variables
echo "Setting up .env file..."
if [ ! -f "qagarden_agents/.env" ]; then
    cp qagarden_agents/.env.example qagarden_agents/.env
    echo "⚠️ Created qagarden_agents/.env from example. Please update it with your API keys."
fi

# 6. Install PM2 for process management
echo "Installing PM2..."
if ! command -v pm2 &> /dev/null; then
    sudo apt-get install -y nodejs npm
    sudo npm install -g pm2
fi

echo "✅ EC2 Setup Complete!"
echo "👉 To start the ecosystem: pm2 start qagarden_agents/main.py --interpreter python3 -- --run https://example.com"
echo "👉 To view logs: pm2 logs"
