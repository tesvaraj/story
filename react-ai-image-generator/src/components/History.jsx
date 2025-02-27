import { useState } from 'react';
import PropTypes from 'prop-types';
import '../styles/History.css';

const History = ({ imageHistory, onSelectImage }) => {
  const [showHistory, setShowHistory] = useState(false);

  if (imageHistory.length === 0) {
    return null;
  }

  // Function to format the date if available
  const formatDate = (dateString) => {
    if (!dateString) return '';
    
    try {
      const date = new Date(dateString);
      const now = new Date();
      const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24));
      
      if (diffDays === 0) {
        return 'Today';
      } else if (diffDays === 1) {
        return 'Yesterday';
      } else if (diffDays < 7) {
        return `${diffDays} days ago`;
      } else {
        return date.toLocaleDateString();
      }
    } catch (e) {
      return '';
    }
  };

  return (
    <div className="history-container">
      <div 
        className="history-header" 
        onClick={() => setShowHistory(!showHistory)}
        role="button"
        tabIndex={0}
        aria-expanded={showHistory}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            setShowHistory(!showHistory);
            e.preventDefault();
          }
        }}
      >
        <h2>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 3H5L5.4 5M7 13H17L21 5H5.4M7 13L5.4 5M7 13L4.70711 15.2929C4.07714 15.9229 4.52331 17 5.41421 17H17M17 17C15.8954 17 15 17.8954 15 19C15 20.1046 15.8954 21 17 21C18.1046 21 19 20.1046 19 19C19 17.8954 18.1046 17 17 17ZM9 19C9 20.1046 8.10457 21 7 21C5.89543 21 5 20.1046 5 19C5 17.8954 5.89543 17 7 17C8.10457 17 9 17.8954 9 19Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          Recently Generated ({imageHistory.length})
        </h2>
        <span className={`arrow-icon ${showHistory ? 'up' : 'down'}`}></span>
      </div>
      
      {showHistory && (
        <div className="history-grid">
          {imageHistory.map((item, index) => (
            <div 
              key={index} 
              className="history-item"
              onClick={() => onSelectImage(item.imageUrl, item.prompt, item.generatedAt)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  onSelectImage(item.imageUrl, item.prompt, item.generatedAt);
                  e.preventDefault();
                }
              }}
            >
              <div className="history-image-container">
                <img src={item.imageUrl} alt={item.prompt} />
              </div>
              <p className="history-prompt">{item.prompt}</p>
              {item.generatedAt && (
                <p className="history-date">{formatDate(item.generatedAt)}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

History.propTypes = {
  imageHistory: PropTypes.arrayOf(
    PropTypes.shape({
      imageUrl: PropTypes.string.isRequired,
      prompt: PropTypes.string.isRequired,
      generatedAt: PropTypes.string
    })
  ).isRequired,
  onSelectImage: PropTypes.func.isRequired,
};

export default History; 