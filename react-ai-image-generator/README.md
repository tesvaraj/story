# AI Image Generator

A modern React application built with Vite that generates images based on text prompts using an AI model.

## Features

- User-friendly interface with a clean, modern design
- Text-to-image generation based on user prompts
- Image download functionality
- Responsive design that works on mobile and desktop

## Technology Stack

- React 19
- Vite
- Express (for the backend API)
- Modern CSS with animations and responsive design

## Getting Started

### Prerequisites

- Node.js 18+ installed
- npm or yarn

### Installation

1. Clone the repository:
```
git clone <repository-url>
cd ai-image-generator
```

2. Install dependencies:
```
npm install
```

### Running the Application

#### Development Mode

To run the application in development mode with hot reloading:

1. Start the backend server:
```
npm run server
```

2. In a separate terminal, start the Vite development server:
```
npm run dev
```

3. Open your browser and navigate to `http://localhost:5173`

#### Production Mode

To build and run the application in production mode:

1. Build the React application:
```
npm run build
```

2. Start the production server:
```
npm start
```

3. Open your browser and navigate to `http://localhost:8080`

## How to Use

1. Enter a descriptive prompt in the text field, describing the image you want to generate.
2. Click the "Generate Image" button and wait for the AI to process your request.
3. Once the image is generated, you can view it and download it using the download button.

## Note

This application uses a mock API that returns random images from Unsplash based on keywords. In a real implementation, this would be connected to an actual AI image generation service.

## License

MIT
