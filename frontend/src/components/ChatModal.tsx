import React, { useState, useRef, useEffect } from 'react';
import './ChatModal.css';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

const API_BASE_URL = 'http://localhost:8000';

const ChatModal: React.FC<{ onClose: () => void }> = ({ onClose }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isInitialized, setIsInitialized] = useState(false);
  const [conversationId] = useState<string>(() => 
    `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  );
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Initialize vector store on mount
    initializeVectorStore();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const initializeVectorStore = async () => {
    try {
      setIsLoading(true);
      const response = await fetch(`${API_BASE_URL}/initialize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setIsInitialized(true);
        setMessages([{
          role: 'assistant',
          content: 'Hello! I\'m ready to help you with questions about life insurance. How can I assist you today?',
          timestamp: new Date(),
        }]);
      } else {
        const error = await response.json();
        setMessages([{
          role: 'assistant',
          content: `Error initializing: ${error.detail || 'Unknown error'}. Please make sure the PDF file is available.`,
          timestamp: new Date(),
        }]);
      }
    } catch (error) {
      setMessages([{
        role: 'assistant',
        content: `Error connecting to server: ${error}. Please make sure the backend is running.`,
        timestamp: new Date(),
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || isLoading || !isInitialized) return;

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: input,
          conversation_id: conversationId,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        const assistantMessage: Message = {
          role: 'assistant',
          content: data.response,
          timestamp: new Date(),
        };
        console.log("sources",data.sources);
        setMessages(prev => [...prev, assistantMessage]);
      } else {
        const error = await response.json();
        const errorMessage: Message = {
          role: 'assistant',
          content: `Error: ${error.detail || 'Unknown error occurred'}`,
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      const errorMessage: Message = {
        role: 'assistant',
        content: `Error: ${error}. Please check your connection.`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="chat-modal-overlay" onClick={onClose}>
      <div className="chat-modal" onClick={(e) => e.stopPropagation()}>
        <div className="chat-modal-header">
          <h2>Life Insurance Assistant</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        
        <div className="chat-messages">
          {messages.map((msg, index) => (
            <div key={index} className={`message ${msg.role}`}>
              <div className="message-content">
                {msg.content}
              </div>
              <div className="message-timestamp">
                {msg.timestamp.toLocaleTimeString()}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="message assistant">
              <div className="message-content">
                <span className="typing-indicator">Thinking...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="chat-input-container">
          <input
            type="text"
            className="chat-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={isInitialized ? "Type your question..." : "Initializing..."}
            disabled={!isInitialized || isLoading}
          />
          <button
            className="send-button"
            onClick={sendMessage}
            disabled={!input.trim() || isLoading || !isInitialized}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatModal;
