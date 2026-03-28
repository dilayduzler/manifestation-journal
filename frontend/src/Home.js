import React from 'react';
import './Home.css';

function Home({ onNavigate }) {
  return (
    <div className="home-container">
      <div className="home-header">
        <h1>APP NAME TBD</h1>
      </div>

      <div className="home-buttons">
        <button className="home-btn chat-btn" onClick={() => onNavigate('chat')}>
          <span className="btn-icon">🔮</span>
          <span className="btn-title">Chat</span>
        </button>

        <button className="home-btn notes-btn" onClick={() => onNavigate('notes')}>
          <span className="btn-icon">🖋</span>
          <span className="btn-title">Journal</span>
        </button>

        <button className="home-btn help-btn" onClick={() => onNavigate('help')}>
          <span className="btn-icon">❓</span>
          <span className="btn-title">Help</span>
        </button>
        
        <button className="theme-btn">⚙️</button>
      </div>
    </div>
  );
}

export default Home;