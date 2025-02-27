#!/bin/bash

# Script to set up the environment for Story Protocol integration

echo "=================================================================================="
echo "Setting up environment for Story Protocol integration"
echo "=================================================================================="

# Check if .env file exists
if [ ! -f .env ]; then
  echo "Error: .env file not found."
  echo "Please create a .env file with the necessary API keys."
  exit 1
fi

# Verify required environment variables
required_vars=("WALLET_PRIVATE_KEY" "PINATA_JWT" "PINATA_API" "PINATA_API_SECRET" "RPC_PROVIDER_URL")
missing_vars=()

for var in "${required_vars[@]}"; do
  if ! grep -q "^$var=" .env; then
    missing_vars+=("$var")
  fi
done

if [ ${#missing_vars[@]} -gt 0 ]; then
  echo "Error: The following required environment variables are missing from .env:"
  for var in "${missing_vars[@]}"; do
    echo "  - $var"
  done
  echo ""
  echo "Please add these variables to your .env file."
  exit 1
fi

echo "Environment variables check: PASSED"

# Install Node.js dependencies if needed
if [ ! -f story-integration/node_modules/.bin/story ]; then
  echo "Installing Story Protocol Node.js dependencies..."
  cd story-integration
  npm install
  cd ..
else
  echo "Node.js dependencies already installed"
fi

# Verify that the uploader script is executable
echo "Testing Story Protocol uploader script..."
node story-integration/storyUploader.js --test || {
  echo "Error: Unable to initialize Story Protocol uploader."
  echo "Please check your environment variables and try again."
  exit 1
}

echo "=================================================================================="
echo "Setup complete! You're ready to upload images to Story Protocol."
echo "=================================================================================="
echo ""
echo "To upload an image, run:"
echo "  python3 app.py \"your concept here\" --upload"
echo ""
echo "Example:"
echo "  python3 app.py \"mountain sunset with lake\" --upload"
echo "" 