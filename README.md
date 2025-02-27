# AI Image Generator with Dual API Support

This project is an AI image generator that can use either a Node.js backend or a Python Flask backend to generate images from text prompts.

## Project Structure

```
├── app.py                            # Python backend with Flask API
├── setup_flask_api.sh                # Setup script for Flask API dependencies
├── react-ai-image-generator/         # React frontend
│   ├── src/                          # React source code
│   ├── server.js                     # Node.js backend server
│   └── package.json                  # NPM dependencies
```

## Setup and Installation

### 1. Python Flask API Setup

To set up the Python Flask API, run:

```bash
# Make the setup script executable (if needed)
chmod +x setup_flask_api.sh

# Run the setup script
./setup_flask_api.sh
```

This will install the required dependencies such as Flask, Flask-CORS, and other packages needed for the Python backend.

### 2. React Frontend Setup

To set up the React frontend, run:

```bash
cd react-ai-image-generator
npm install
```

## Running the Application

You have two options for running the backend: the Node.js backend or the Python Flask backend.

### Option 1: Running with Node.js Backend Only

```bash
cd react-ai-image-generator
npm run dev:all
```

This will start both the React frontend and the Node.js backend server.

### Option 2: Running with Python Flask Backend

1. Start the Python Flask API:

```bash
python3 app.py --serve --port 5001
```

2. In a separate terminal, start the React frontend:

```bash
cd react-ai-image-generator
npm run dev
```

## Using the Application

1. Open your browser and navigate to http://localhost:5173
2. Enter a text prompt in the input field
3. Use the toggle switch to choose between:
   - Node.js API (default)
   - Python Flask API
4. Click the "Generate Image" button
5. View, save, or share the generated image

## API Endpoints

### Node.js API

- **POST /api/generate-image**
  - Request: `{ "prompt": "your text prompt" }`
  - Response: `{ "imageUrl": "url-to-image", "prompt": "prompt used", "generatedAt": "timestamp" }`

### Python Flask API

- **POST /api/generate-image**
  - Request: `{ "prompt": "your text prompt", "provider": "together" }`
  - Response: `{ "imageUrl": "url-to-image", "prompt": "prompt used", "generatedAt": "timestamp", "provider": "provider-used" }`

- **GET /api/images/{image_name}**
  - Serves the generated images

## Environment Variables

The Python backend requires several API keys in a `.env` file:
- `NILAI_API_KEY` (for prompt generation)
- Either `TOGETHER_API_KEY` or `ABLO_KEY` (depending on chosen provider)
- For Story Protocol uploads: `PINATA_JWT`, `WALLET_PRIVATE_KEY`, and `RPC_PROVIDER_URL` 