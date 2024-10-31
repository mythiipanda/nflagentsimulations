import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';
import { Send, User, Bot } from 'lucide-react';

export default function NFLChat() {
  const [chatHistory, setChatHistory] = useState([]);
  const [userInput, setUserInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(uuidv4()); // Generate a unique sessionId
  const chatContainerRef = useRef(null);

  useEffect(() => {
    // Add the starting message to the chat history
    setChatHistory([
      {
        role: 'assistant',
        message: {
          content: 'Welcome to the NFL Analytics Chat! I\'m here to help you explore and analyze NFL data. Feel free to ask me anything about player stats, team performance, game outcomes, and more. Let\'s dive in!',
        },
      },
    ]);
  }, []);

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [chatHistory]);

  const sendMessage = async () => {
    if (userInput.trim() === '' || isLoading) return;

    setIsLoading(true);
    const newUserMessage = { role: 'user', message: { content: userInput } };
    setChatHistory((prev) => [...prev, newUserMessage]);
    setUserInput('');

    const instruction = "You are an expert NFL analyst. Please assist by backing your insights with specific data, stats, and examples. Respond only to NFL-related prompts, offering valuable insights and clarifying complex details wherever necessary to create an engaging and fact-supported analysis.";
    const prompt = `${instruction}\n\n${userInput}`;

    try {
      // Include sessionId in the API request payload
      const response = await axios.post('http://localhost:5000/api/chat', { prompt, sessionId });
      const assistantMessage = response.data;
      
      setChatHistory((prev) => [...prev, { role: 'assistant', message: assistantMessage }]);
    } catch (error) {
      console.error('Error getting completion:', error);
      setChatHistory((prev) => [
        ...prev,
        { role: 'assistant', message: { content: 'Sorry, I encountered an error. Please try again.' } },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100">
      <div className="bg-white dark:bg-gray-800 p-4 shadow-md">
        <h1 className="text-2xl font-bold text-center">NFL Analytics Chat</h1>
      </div>
      <div ref={chatContainerRef} className="flex-1 overflow-y-auto p-4 space-y-4">
        {chatHistory.map((entry, index) => (
          <div
            key={index}
            className={`flex ${
              entry.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            <div
              className={`flex items-start space-x-2 max-w-xs md:max-w-md lg:max-w-lg xl:max-w-xl`}
            >
              {entry.role === 'assistant' && (
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center">
                  <Bot className="h-5 w-5 text-white" />
                </div>
              )}
              <div
                className={`rounded-lg p-3 ${
                  entry.role === 'user'
                    ? 'bg-blue-500 text-white'
                    : 'bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 shadow-md'
                }`}
              >
                {entry.message.content}
              </div>
              {entry.role === 'user' && (
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-300 dark:bg-gray-600 flex items-center justify-center">
                  <User className="h-5 w-5 text-gray-600 dark:text-gray-300" />
                </div>
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white dark:bg-gray-700 rounded-lg p-3 shadow-md animate-pulse">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-75"></div>
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-150"></div>
              </div>
            </div>
          </div>
        )}
      </div>
      <div className="bg-white dark:bg-gray-800 p-4 shadow-md">
        <div className="flex items-center space-x-2">
          <input
            type="text"
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
              }
            }}
            placeholder="Ask about NFL analytics..."
            className="flex-1 p-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
          />
          <button
            onClick={sendMessage}
            disabled={isLoading}
            className="bg-blue-500 text-white p-2 rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 transition-colors duration-200"
          >
            <Send className="h-5 w-5" />
          </button>
        </div>
      </div>
    </div>
  );
}