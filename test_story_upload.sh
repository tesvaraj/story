#!/bin/bash

# Test script for generating images and uploading to Story Protocol

echo "Generating an image and uploading to Story Protocol..."
echo ""

# Run the Python app with the upload flag
python3 app.py "cyberpunk city with neon lights" --variations 1 --upload

echo ""
echo "Test complete!" 