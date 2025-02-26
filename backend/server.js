const express = require('express');
const path = require('path');
const bodyParser = require('body-parser');

const app = express();
const PORT = process.env.PORT || 8080;

// Middleware
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, '../frontend')));

// Mock API endpoint for image generation
// In a real application, this would call the Ablo image model
app.post('/api/generate-image', (req, res) => {
  const { prompt } = req.body;
  
  // Log the prompt for debugging
  console.log('Received prompt:', prompt);
  
  // Simulate API delay
  setTimeout(() => {
    // Return a placeholder image URL
    // In a real application, this would be the URL of the generated image
    res.json({
      imageUrl: 'https://source.unsplash.com/random/800x600/?'+encodeURIComponent(prompt),
      prompt: prompt
    });
  }, 2000);
});

// Serve the frontend
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '../frontend/index.html'));
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
}); 