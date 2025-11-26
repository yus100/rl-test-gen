#!/bin/bash
# Setup script for RL Test Generation Environment

echo "=========================================="
echo "RL Test Gen Environment Setup"
echo "=========================================="

# check python version
echo ""
echo "Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# create virtual environment
echo ""
echo "Creating virtual environment..."
python -m venv venv

# activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# install requirements
echo ""
echo "Installing requirements..."
pip install -r requirements.txt

# check docker
echo ""
echo "Checking Docker..."
if command -v docker &> /dev/null; then
    echo "✓ Docker is installed"
    if docker ps &> /dev/null; then
        echo "✓ Docker daemon is running"
    else
        echo "✗ Docker daemon is not running. Please start Docker."
        exit 1
    fi
else
    echo "✗ Docker is not installed. Please install Docker first."
    exit 1
fi

# build docker image
echo ""
echo "Building test runner Docker image..."
docker build -f Dockerfile.testrunner -t testrunner:latest .

# create problems directory if it doesn't exist
echo ""
echo "Setting up directories..."
mkdir -p problems
echo "✓ Created 'problems' directory for dataset"

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Place your problem JSON files in the 'problems' directory"
echo ""
echo "3. Run the example:"
echo "   python example_usage.py"
echo ""

