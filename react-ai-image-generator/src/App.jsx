import { useState } from 'react'
import './App.css'

function App() {
  const [prompt, setPrompt] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [imageUrl, setImageUrl] = useState('')
  const [error, setError] = useState('')

  const handlePromptChange = (e) => {
    setPrompt(e.target.value)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!prompt.trim()) {
      setError('Please enter a description for your image.')
      return
    }
    
    setError('')
    setIsLoading(true)
    
    try {
      const response = await generateImage(prompt)
      setImageUrl(response.imageUrl)
    } catch (err) {
      console.error('Error generating image:', err)
      setError('An error occurred while generating your image. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleDownload = () => {
    if (imageUrl) {
      const a = document.createElement('a')
      a.href = imageUrl
      a.download = 'generated-image.png'
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
    }
  }

  // Function to call the image generation API
  async function generateImage(prompt) {
    // Replace with your actual API endpoint
    const apiUrl = '/api/generate-image'
    
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ prompt }),
    })
    
    if (!response.ok) {
      throw new Error('Failed to generate image')
    }
    
    return await response.json()
  }

  return (
    <div className="container">
      <h1>AI Image Generator</h1>
      <p className="description">Describe the image you want to generate, and our AI will create it for you!</p>
      
      <div className="input-container">
        <form onSubmit={handleSubmit}>
          <textarea 
            id="prompt-input"
            value={prompt}
            onChange={handlePromptChange}
            placeholder="Example: I want a picture of me holding Nike shoes in Paris."
            rows={4}
          />
          <button type="submit" disabled={isLoading}>
            Generate Image
          </button>
        </form>
        {error && <p className="error">{error}</p>}
      </div>
      
      {isLoading && (
        <div className="loading">
          <div className="spinner"></div>
          <p>Creating your image...</p>
        </div>
      )}
      
      {imageUrl && !isLoading && (
        <div className="result-container">
          <h2>Your Generated Image</h2>
          <img src={imageUrl} alt="Generated image" className="generated-image" />
          <button onClick={handleDownload} className="download-btn">
            Download Image
          </button>
        </div>
      )}
    </div>
  )
}

export default App
