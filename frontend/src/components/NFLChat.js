import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';
import { Send, User, Bot } from 'lucide-react';

export default function NFLChat({ theme }) {
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
    const instruction = `
    You are an expert NFL analyst. Please assist by backing your insights with specific data, stats, and examples. Respond only to NFL-related prompts, offering valuable insights and clarifying complex details wherever necessary to create an engaging and fact-supported analysis.
    
    If you are prompted to generate a graph or a chart, generate Python code that customizes a chart in matplotlib based on the user's requirements. The code should:
    1. Create a dataframe from the provided data using pandas (import pandas as pd).
    2. Use matplotlib for plotting (import matplotlib.pyplot as plt).
    3. Focus only on modifying the chart appearance or adding specific features as requested.
    4. Do not include code for displaying the chart (e.g., plt.show()).
    5. Ensure the code is executable as a standalone script.
    6. Save the chart to a file using plt.savefig() with the file path "./public/custom_chart.png".
    
    Return only the generated code.
    `;
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
    <div className={`flex flex-col h-screen bg-transparent text-gray-900 dark:text-gray-100 ${theme === 'dark' ? 'dark' : ''}`}>
    <div ref={chatContainerRef} className="flex-1 overflow-y-auto p-4 space-y-4 bg-transparent">
      {chatHistory.map((entry, index) => (
        <div
          key={index}
          className={`flex ${entry.role === 'user' ? 'justify-end' : 'justify-start'}`}
        >
          <div className={`flex items-start space-x-2 max-w-xs md:max-w-md lg:max-w-lg xl:max-w-xl`}>
            
            {entry.role === 'assistant' && (
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center">
                <Bot className="h-5 w-5 text-white" />
              </div>
            )}
            
            {/* Conditional rendering for image or text content */}
            {entry.message.imageUrl ? (
              <img src={entry.message.imageUrl} alt="Generated Chart" className="w-full max-w-md rounded-lg shadow-md" />
            ) : (
              <div
                className={`rounded-lg p-2 ${
                  entry.role === 'user'
                    ? 'bg-blue-500 text-white'
                    : 'bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 shadow-md'
                }`}
              >
                {entry.message.content}
              </div>
            )}
            
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
          <div className="bg-white dark:bg-gray-700 rounded-lg p-2 shadow-md animate-pulse">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
              <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-75"></div>
              <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-150"></div>
            </div>
          </div>
        </div>
      )}
    </div>

      <div className="bg-transparent p-4 shadow-md">
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
            className="px-8 py-3 rounded-full text-lg bg-blue-500 text-white hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 transition-colors duration-200"
          >
            <Send className="h-5 w-5" />
          </button>
        </div>
      </div>
    </div>
  );
}