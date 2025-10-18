import React, { useState, useEffect, useRef } from 'react';
import ChatWindow from './components/ChatWindow';
import InputBar from './components/InputBar';
import { askQuestion } from './api';

/**
 * Main App Component
 * Root component managing the medical FAQ chatbot interface
 */
function App() {
  // State for managing chat messages
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      text: "Hello! I'm your AI Medical Assistant. I can help answer your medical questions based on reliable health information. How can I assist you today?",
      timestamp: new Date(),
    }
  ]);

  // State for loading/typing indicator
  const [isLoading, setIsLoading] = useState(false);

  // State for error handling
  const [error, setError] = useState(null);

  // Reference for auto-scrolling
  const messagesEndRef = useRef(null);

  /**
   * Scroll to bottom of chat when new messages arrive
   */
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  /**
   * Handle sending a new message
   * @param {string} userMessage - The user's question
   */
  const handleSendMessage = async (userMessage) => {
    // Clear any previous errors
    setError(null);

    // Add user message to chat
    const userMessageObj = {
      id: Date.now(),
      type: 'user',
      text: userMessage,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessageObj]);
    setIsLoading(true);

    try {
      // Call backend API
      const response = await askQuestion(userMessage);

      // Add bot response to chat
      const botMessageObj = {
        id: Date.now() + 1,
        type: 'bot',
        text: response.answer,
        sources: response.sources || [],
        confidence: response.confidence,
        latency: response.latency,
        cached: response.cached,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, botMessageObj]);
    } catch (err) {
      // Handle errors gracefully
      console.error('Error fetching response:', err);
      
      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot',
        text: err.message || 'Sorry, I encountered an error while processing your question. Please try again.',
        isError: true,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessage]);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Handle clearing the chat
   */
  const handleClearChat = () => {
    setMessages([
      {
        id: 1,
        type: 'bot',
        text: "Hello! I'm your AI Medical Assistant. I can help answer your medical questions based on reliable health information. How can I assist you today?",
        timestamp: new Date(),
      }
    ]);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-sky-50 via-blue-50 to-indigo-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-5xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              {/* Medical Icon */}
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-md">
                <svg 
                  className="w-6 h-6 text-white" 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path 
                    strokeLinecap="round" 
                    strokeLinejoin="round" 
                    strokeWidth={2} 
                    d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" 
                  />
                </svg>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  Medical FAQ Bot
                </h1>
                <p className="text-sm text-gray-500">
                  AI-Powered Health Assistant
                </p>
              </div>
            </div>
            
            {/* Clear Chat Button */}
            <button
              onClick={handleClearChat}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Clear Chat
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
        <div className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden" style={{ height: 'calc(100vh - 180px)' }}>
          {/* Chat Window */}
          <ChatWindow 
            messages={messages} 
            isLoading={isLoading}
            messagesEndRef={messagesEndRef}
          />
          
          {/* Input Bar */}
          <InputBar 
            onSendMessage={handleSendMessage} 
            isLoading={isLoading}
          />
        </div>

        {/* Disclaimer */}
        <div className="mt-4 text-center">
          <p className="text-xs text-gray-500">
            ⚠️ This bot provides general health information only and is not a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider.
          </p>
        </div>
      </main>
    </div>
  );
}

export default App;
