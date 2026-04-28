import React, { useState } from 'react';
import ChatModal from './components/ChatModal';
import './App.css';

function App() {
  const [isChatOpen, setIsChatOpen] = useState(false);

  return (
    <div className="App">
      <header className="App-header">
        <h1>Life Insurance Handbook Assistant</h1>
        <p>Ask questions about life insurance based on the IRDA handbook</p>
        <button 
          className="chat-button"
          onClick={() => setIsChatOpen(true)}
        >
          Open Chat
        </button>
      </header>
      {isChatOpen && (
        <ChatModal onClose={() => setIsChatOpen(false)} />
      )}
    </div>
  );
}

export default App;
