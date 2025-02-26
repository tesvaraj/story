import { useState } from 'react';
import PropTypes from 'prop-types';
import '../styles/ImageGenerator.css';

const ImageGenerator = ({ onImageGenerated, isLoading, setIsLoading }) => {
  const [prompt, setPrompt] = useState('');
  const [error, setError] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);

  const promptSuggestions = [
    "A futuristic cityscape with flying cars",
    "An underwater kingdom with mermaids",
    "A magical forest with glowing plants",
    "A cat astronaut floating in space",
    "A steampunk-inspired train station"
  ];

  const handlePromptChange = (e) => {
    setPrompt(e.target.value);
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!prompt.trim()) {
      setError('Please enter a description for your image.');
      return;
    }
    
    setError('');
    setIsLoading(true);
    
    try {
      const response = await generateImage(prompt);
      onImageGenerated(response.imageUrl, prompt);
    } catch (err) {
      console.error('Error generating image:', err);
      setError('An error occurred while generating your image. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const useSuggestion = (suggestion) => {
    setPrompt(suggestion);
    setShowSuggestions(false);
  };

  // Function to call the image generation API
  async function generateImage(prompt) {
    const apiUrl = '/api/generate-image';
    
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ prompt }),
    });
    
    if (!response.ok) {
      throw new Error('Failed to generate image');
    }
    
    return await response.json();
  }

  return (
    <div className="generator-container">
      <form onSubmit={handleSubmit} className="generator-form">
        <div className="input-wrapper">
          <textarea 
            id="prompt-input"
            value={prompt}
            onChange={handlePromptChange}
            placeholder="Describe the image you want to create..."
            rows={3}
            className={error ? 'error' : ''}
            disabled={isLoading}
          />
          <button 
            type="button" 
            className="suggestion-btn"
            onClick={() => setShowSuggestions(!showSuggestions)}
            disabled={isLoading}
            aria-label="Show suggestions"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 16C13.1046 16 14 15.1046 14 14C14 12.8954 13.1046 12 12 12C10.8954 12 10 12.8954 10 14C10 15.1046 10.8954 16 12 16Z" fill="currentColor"/>
              <path d="M12 9C13.1046 9 14 8.10457 14 7C14 5.89543 13.1046 5 12 5C10.8954 5 10 5.89543 10 7C10 8.10457 10.8954 9 12 9Z" fill="currentColor"/>
              <path d="M12 23C13.1046 23 14 22.1046 14 21C14 19.8954 13.1046 19 12 19C10.8954 19 10 19.8954 10 21C10 22.1046 10.8954 23 12 23Z" fill="currentColor"/>
            </svg>
          </button>
        </div>
        
        {showSuggestions && (
          <div className="suggestions">
            <h3>Try these ideas:</h3>
            <ul>
              {promptSuggestions.map((suggestion, index) => (
                <li key={index}>
                  <button 
                    type="button"
                    onClick={() => useSuggestion(suggestion)}
                  >
                    {suggestion}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}
        
        {error && <p className="error-message">{error}</p>}
        
        <button 
          type="submit" 
          className="generate-btn"
          disabled={isLoading || !prompt.trim()}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M23 19C23 19.5304 22.7893 20.0391 22.4142 20.4142C22.0391 20.7893 21.5304 21 21 21H3C2.46957 21 1.96086 20.7893 1.58579 20.4142C1.21071 20.0391 1 19.5304 1 19V8C1 7.46957 1.21071 6.96086 1.58579 6.58579C1.96086 6.21071 2.46957 6 3 6H7L9 3H15L17 6H21C21.5304 6 22.0391 6.21071 22.4142 6.58579C22.7893 6.96086 23 7.46957 23 8V19Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M12 17C14.2091 17 16 15.2091 16 13C16 10.7909 14.2091 9 12 9C9.79086 9 8 10.7909 8 13C8 15.2091 9.79086 17 12 17Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          Generate Image
        </button>
      </form>
      
      {isLoading && (
        <div className="loader">
          <div className="loader-spinner"></div>
          <p>Creating your masterpiece<span>.</span><span>.</span><span>.</span></p>
        </div>
      )}
    </div>
  );
};

ImageGenerator.propTypes = {
  onImageGenerated: PropTypes.func.isRequired,
  isLoading: PropTypes.bool.isRequired,
  setIsLoading: PropTypes.func.isRequired
};

export default ImageGenerator; 