import React, { useState, useEffect } from 'react';

export default function NFLChat({ theme }) {
  const [chatHistory, setChatHistory] = useState([]);
  const [currentMessage, setCurrentMessage] = useState('');

  const handleSendMessage = () => {
    if (currentMessage.trim()) {
      setChatHistory([...chatHistory, currentMessage]);
      setCurrentMessage('');
    }
  };

  useEffect(() => {
    console.log('Chat history updated:', chatHistory);
  }, [chatHistory]);

  return (
    <div className="h-screen flex flex-col justify-center items-center bg-gray-100 dark:bg-gray-900">
      <div className="w-full max-w-2xl h-5/6 bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4">
        <div className="flex flex-col h-full">
          <div className="flex-1 overflow-y-auto">
            {chatHistory.map((message, index) => (
              <div key={index} className="py-2">
                <span className="text-gray-600 dark:text-gray-300">{message}</span>
              </div>
            ))}
          </div>
          <div className="flex items-center p-2 border-t border-gray-200 dark:border-gray-700">
            <input
              type="text"
              value={currentMessage}
              onChange={(e) => setCurrentMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              className="w-full p-2 text-gray-600 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Type your message..."
            />
            <button
              onClick={handleSendMessage}
              className="ml-2 p-2 text-white bg-blue-500 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}