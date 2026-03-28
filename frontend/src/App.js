import React, { useState } from 'react';
import Home from './Home';
import Chat from './Chat';
import './App.css';

function App() {
  const [currentPage, setCurrentPage] = useState('home');

  const renderPage = () => {
    switch(currentPage) {
      case 'home':
        return <Home onNavigate={setCurrentPage} />;
      case 'chat':
        return <Chat onBack={() => setCurrentPage('home')} />;
      default:
        return <Home onNavigate={setCurrentPage} />;
    }
  };

  return (
    <div className="App">
      {renderPage()}
    </div>
  );
}

export default App;