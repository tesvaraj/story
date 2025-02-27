import { useState, useEffect } from 'react'
import './App.css'
import Header from './components/Header'
import ImageGenerator from './components/ImageGenerator'
import ImageResult from './components/ImageResult'
import History from './components/History'

function App() {
  const [prompt, setPrompt] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [imageUrl, setImageUrl] = useState('')
  const [error, setError] = useState('')
  const [isDarkMode, setIsDarkMode] = useState(false)
  const [generatedAt, setGeneratedAt] = useState(null)
  const [imageHistory, setImageHistory] = useState(() => {
    const savedHistory = localStorage.getItem('imageHistory')
    return savedHistory ? JSON.parse(savedHistory) : []
  })

  // Initialize dark mode based on user preference
  useEffect(() => {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    const savedMode = localStorage.getItem('darkMode')
    
    if (savedMode !== null) {
      setIsDarkMode(savedMode === 'true')
    } else if (prefersDark) {
      setIsDarkMode(true)
    }
  }, [])

  // Apply dark mode class to body when changed
  useEffect(() => {
    if (isDarkMode) {
      document.body.classList.add('dark-mode')
    } else {
      document.body.classList.remove('dark-mode')
    }
    
    localStorage.setItem('darkMode', isDarkMode)
  }, [isDarkMode])

  // Save image history to localStorage
  useEffect(() => {
    localStorage.setItem('imageHistory', JSON.stringify(imageHistory))
  }, [imageHistory])

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

  const handleImageGenerated = (newImageUrl, newPrompt, newGeneratedAt) => {
    setImageUrl(newImageUrl)
    setPrompt(newPrompt)
    setGeneratedAt(newGeneratedAt)
    
    // Add to history only if it's a new image
    if (newImageUrl && newPrompt) {
      const newHistoryItem = { 
        imageUrl: newImageUrl, 
        prompt: newPrompt,
        generatedAt: newGeneratedAt
      }
      
      // Check if this exact combination already exists to prevent duplicates
      const exists = imageHistory.some(
        item => item.imageUrl === newImageUrl && item.prompt === newPrompt
      )
      
      if (!exists) {
        // Add to the beginning of the array, limit to last 10 images
        setImageHistory(prev => [newHistoryItem, ...prev].slice(0, 10))
      }
    }
  }

  const handleToggleDarkMode = () => {
    setIsDarkMode(prev => !prev)
  }

  const handleSaveToHistory = (url, promptText) => {
    // Create a clone to trigger notification animation
    const historyItem = { 
      imageUrl: url, 
      prompt: promptText,
      generatedAt: generatedAt
    }
    
    // Check if already exists
    const exists = imageHistory.some(
      item => item.imageUrl === url && item.prompt === promptText
    )
    
    if (!exists) {
      setImageHistory(prev => [historyItem, ...prev].slice(0, 10))
    }
    
    // Show saved notification
    const savedNotification = document.getElementById('saved-notification')
    if (savedNotification) {
      savedNotification.classList.add('show')
      setTimeout(() => {
        savedNotification.classList.remove('show')
      }, 2000)
    }
  }

  const handleHistoryItemSelect = (historyImageUrl, historyPrompt, historyGeneratedAt) => {
    setImageUrl(historyImageUrl)
    setPrompt(historyPrompt)
    setGeneratedAt(historyGeneratedAt)
    
    // Scroll to result
    document.getElementById('result-section')?.scrollIntoView({ behavior: 'smooth' })
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
    <div className="app">
      <Header isDarkMode={isDarkMode} onToggleDarkMode={handleToggleDarkMode} />
      
      <h1 className="app-title">AI Image Generator</h1>
      <p className="app-description">
        Turn your ideas into stunning visuals in seconds. Just describe what you want to see, and our AI will create it for you!
      </p>
      
      <ImageGenerator 
        onImageGenerated={handleImageGenerated} 
        isLoading={isLoading}
        setIsLoading={setIsLoading}
      />
      
      <div id="result-section">
        {imageUrl && !isLoading && (
          <ImageResult 
            imageUrl={imageUrl} 
            prompt={prompt}
            generatedAt={generatedAt}
            onSaveToHistory={handleSaveToHistory}
          />
        )}
      </div>
      
      <History 
        imageHistory={imageHistory}
        onSelectImage={handleHistoryItemSelect}
      />
      
      <div id="saved-notification" className="notification">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M9 16.2L4.8 12L3.4 13.4L9 19L21 7L19.6 5.6L9 16.2Z" fill="currentColor"/>
        </svg>
        Image saved to history!
      </div>
      
      <footer className="footer">
        <p>© {new Date().getFullYear()} AI Image Generator</p>
      </footer>
    </div>
  )
}

export default App
