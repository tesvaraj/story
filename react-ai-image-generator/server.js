const express = require('express');
const path = require('path');
const bodyParser = require('body-parser');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 8080;

// Middleware
app.use(bodyParser.json());

// Enable CORS for development
if (process.env.NODE_ENV !== 'production') {
  app.use(cors());
  console.log('CORS enabled for development');
}

// Collection of reliable high-quality image URLs
const reliableImageCollection = [
  'https://images.pexels.com/photos/1619317/pexels-photo-1619317.jpeg', // Beach
  'https://images.pexels.com/photos/2559941/pexels-photo-2559941.jpeg', // Space
  'https://images.pexels.com/photos/2662116/pexels-photo-2662116.jpeg', // Forest
  'https://images.pexels.com/photos/417074/pexels-photo-417074.jpeg',  // Mountain
  'https://images.pexels.com/photos/531880/pexels-photo-531880.jpeg',  // City
  'https://images.pexels.com/photos/1402787/pexels-photo-1402787.jpeg', // Underwater
  'https://images.pexels.com/photos/325185/pexels-photo-325185.jpeg',  // Desert
  'https://images.pexels.com/photos/1624496/pexels-photo-1624496.jpeg', // Sci-fi
  'https://images.pexels.com/photos/1482476/pexels-photo-1482476.jpeg', // Fantasy
  'https://images.pexels.com/photos/3075993/pexels-photo-3075993.jpeg', // Abstract
  'https://images.pexels.com/photos/147411/italy-mountains-dawn-daybreak-147411.jpeg', // Landscape
  'https://images.pexels.com/photos/247431/pexels-photo-247431.jpeg',  // Wildlife
  'https://images.pexels.com/photos/164175/pexels-photo-164175.jpeg',  // Architecture
  'https://images.pexels.com/photos/1323550/pexels-photo-1323550.jpeg', // Food
  'https://images.pexels.com/photos/1529881/pexels-photo-1529881.jpeg', // Portrait
];

// Select a reliable image based on the prompt
function getImageForPrompt(prompt) {
  // Convert prompt to lowercase for easier matching
  const promptLower = prompt.toLowerCase();
  
  // Define categories and their keywords for better image selection
  const categories = {
    beach: ['beach', 'ocean', 'sea', 'coast', 'wave', 'sand', 'tropical'],
    space: ['space', 'galaxy', 'star', 'cosmos', 'planet', 'astronaut', 'universe'],
    forest: ['forest', 'tree', 'nature', 'wood', 'jungle', 'green', 'plant'],
    mountain: ['mountain', 'hill', 'peak', 'valley', 'cliff', 'hiking', 'highland'],
    city: ['city', 'urban', 'building', 'skyline', 'downtown', 'street', 'skyscraper'],
    underwater: ['underwater', 'ocean', 'sea', 'marine', 'fish', 'coral', 'aquatic'],
    desert: ['desert', 'sand', 'dune', 'arid', 'cactus', 'dry', 'barren'],
    scifi: ['sci-fi', 'robot', 'future', 'futuristic', 'tech', 'mechanical', 'cyborg'],
    fantasy: ['fantasy', 'magical', 'dragon', 'myth', 'fairy', 'enchanted', 'wizard'],
    abstract: ['abstract', 'pattern', 'geometric', 'modern', 'minimal', 'artistic'],
    landscape: ['landscape', 'scenic', 'panorama', 'vista', 'horizon', 'outdoor'],
    wildlife: ['animal', 'wildlife', 'creature', 'wild', 'bird', 'mammal', 'predator'],
    architecture: ['building', 'structure', 'architectural', 'monument', 'tower', 'design'],
    food: ['food', 'meal', 'cuisine', 'dish', 'cooking', 'restaurant', 'gourmet'],
    portrait: ['person', 'face', 'portrait', 'human', 'people', 'man', 'woman', 'child']
  };
  
  // Find which category the prompt fits into
  let selectedCategory = null;
  let highestMatch = 0;
  
  for (const [category, keywords] of Object.entries(categories)) {
    const matchCount = keywords.filter(keyword => promptLower.includes(keyword)).length;
    if (matchCount > highestMatch) {
      highestMatch = matchCount;
      selectedCategory = category;
    }
  }
  
  // Map categories to image indices
  const categoryToImageIndex = {
    beach: 0,
    space: 1,
    forest: 2,
    mountain: 3,
    city: 4,
    underwater: 5,
    desert: 6,
    scifi: 7,
    fantasy: 8,
    abstract: 9,
    landscape: 10,
    wildlife: 11,
    architecture: 12,
    food: 13,
    portrait: 14
  };
  
  // Get image index from the mapped category or use random selection as fallback
  const imageIndex = selectedCategory 
    ? categoryToImageIndex[selectedCategory] 
    : Math.floor(Math.random() * reliableImageCollection.length);
  
  console.log(`Prompt "${prompt}" matched with category: ${selectedCategory || 'random'}`);
  return reliableImageCollection[imageIndex];
}

// Mock API endpoint for image generation
app.post('/api/generate-image', async (req, res) => {
  const { prompt } = req.body;
  
  // Log the prompt for debugging
  console.log('Received prompt:', prompt);
  
  // Return error if no prompt provided
  if (!prompt || prompt.trim() === '') {
    return res.status(400).json({ error: 'Prompt is required' });
  }
  
  try {
    // Get an appropriate image URL based on the prompt
    const imageUrl = getImageForPrompt(prompt);
    
    // Add a cache-busting parameter to ensure the image is reloaded
    const finalImageUrl = `${imageUrl}?cb=${Date.now()}`;
    
    // Add a slight delay to simulate AI processing
    setTimeout(() => {
      res.json({
        imageUrl: finalImageUrl,
        prompt: prompt,
        generatedAt: new Date().toISOString()
      });
    }, 1500);
  } catch (error) {
    console.error('Error generating image:', error);
    // Use a reliable fallback image
    res.status(500).json({ 
      error: 'Failed to generate image',
      imageUrl: 'https://images.pexels.com/photos/1619317/pexels-photo-1619317.jpeg?cb=' + Date.now()
    });
  }
});

// Serve static files from the React app
if (process.env.NODE_ENV === 'production') {
  app.use(express.static(path.join(__dirname, 'dist')));

  // Handle React routing, return all requests to React app
  app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'dist', 'index.html'));
  });
}

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
  console.log(`API endpoint available at http://localhost:${PORT}/api/generate-image`);
}); 