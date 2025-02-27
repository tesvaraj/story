#!/bin/bash

echo "Setting up Flask API dependencies..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is required but not installed."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "ERROR: pip3 is required but not installed."
    exit 1
fi

# Install required packages
echo "Installing required Python packages..."
pip3 install flask flask-cors pillow together dotenv requests

echo "Creating generated_images directory if it doesn't exist..."
mkdir -p generated_images

echo "Setup complete! You can now run the API server with:"
echo "python3 app.py --serve --port 5001"
echo ""
echo "The API will be available at:"
echo "http://localhost:5001/api/generate-image" 