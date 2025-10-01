#!/bin/bash
# Setup script for NeuroGym on Raspberry Pi 5
# This script installs Docker and sets up the NeuroGym service

set -e

echo "================================"
echo "NeuroGym Raspberry Pi 5 Setup"
echo "================================"
echo ""

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ]; then
    echo "Warning: This script is designed for Raspberry Pi"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update system
echo "Step 1: Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker if not already installed
if ! command -v docker &> /dev/null; then
    echo "Step 2: Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
else
    echo "Step 2: Docker already installed, skipping..."
fi

# Install Docker Compose plugin
echo "Step 3: Installing Docker Compose..."
sudo apt-get install -y docker-compose-plugin

# Clone repository if not in it
if [ ! -f "pyproject.toml" ]; then
    echo "Step 4: Cloning NeuroGym repository..."
    git clone https://github.com/neurogym/neurogym.git
    cd neurogym
else
    echo "Step 4: Already in NeuroGym directory..."
fi

# Build Docker image
echo "Step 5: Building Docker image (this may take several minutes)..."
docker compose build

# Create necessary directories
echo "Step 6: Creating directories..."
mkdir -p logs config

# Test the service
echo "Step 7: Testing the service..."
docker compose up -d
sleep 5

# Check if service is running
if docker compose ps | grep -q "running"; then
    echo "✓ Service is running!"
    
    # Test health endpoint
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✓ Health check passed!"
    else
        echo "⚠ Health check failed, but container is running"
    fi
else
    echo "✗ Service failed to start"
    docker compose logs
    exit 1
fi

echo ""
echo "================================"
echo "Setup Complete!"
echo "================================"
echo ""
echo "The NeuroGym API is now running at:"
echo "  - Local: http://localhost:8000"
echo "  - Network: http://$(hostname -I | awk '{print $1}'):8000"
echo ""
echo "Interactive documentation:"
echo "  - Swagger UI: http://localhost:8000/docs"
echo "  - ReDoc: http://localhost:8000/redoc"
echo ""
echo "Useful commands:"
echo "  - View logs: docker compose logs -f"
echo "  - Stop service: docker compose down"
echo "  - Restart service: docker compose restart"
echo ""
echo "To run as a system service (auto-start on boot):"
echo "  sudo cp deployment/neurogym.service /etc/systemd/system/"
echo "  sudo systemctl enable neurogym.service"
echo ""
echo "⚠ Note: You may need to log out and log back in for Docker"
echo "   group membership to take effect if this was a fresh install."
echo ""
