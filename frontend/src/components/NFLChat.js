import React, { useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';

export default function NFLChat({
  chatHistory,
  userInput,
  setUserInput,
  sendMessage,
  isLoading,
}) {
  const chatContainerRef = useRef(null);

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [chatHistory, isLoading]);

  return (
    <div className="flex flex-col h-full bg-white dark:bg-gray-900 rounded-lg shadow-lg overflow-hidden">
      <div
        ref={chatContainerRef}
        className="flex-1 overflow-y-auto p-4 space-y-4"
      >
        {chatHistory.map((entry, index) => (
          <div
            key={index}
            className={`p-3 rounded-lg ${
              entry.role === 'assistant'
                ? 'bg-gray-100 dark:bg-gray-800'
                : 'bg-blue-500 dark:bg-blue-600 text-white'
            }`}
          >
            <p className="text-sm font-semibold mb-1">
              {entry.role === 'assistant' ? 'AI Assistant' : 'You'}
            </p>
            <div className="prose dark:prose-invert max-w-none">
              <ReactMarkdown>{entry.message.textContent || 'No content available'}</ReactMarkdown>
            </div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              {entry.timestamp}
            </p>
          </div>
        ))}
        {isLoading && (
          <div className="p-3 rounded-lg bg-gray-100 dark:bg-gray-800">
            <p className="text-sm font-semibold mb-1 text-gray-900 dark:text-white">AI Assistant</p>
            <div className="animate-pulse space-y-2">
              <div className="h-4 bg-gray-300 dark:bg-gray-600 rounded w-3/4"></div>
              <div className="h-4 bg-gray-300 dark:bg-gray-600 rounded w-1/2"></div>
            </div>
          </div>
        )}
      </div>
      <div className="p-4 bg-gray-100 dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-3">
          <textarea
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey && !isLoading) {
                e.preventDefault();
                sendMessage();
              }
            }}
            rows="1"
            placeholder="Type your message..."
            className="flex-grow p-2 rounded-lg border border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white resize-none"
          ></textarea>
          <button
            onClick={sendMessage}
            disabled={isLoading}
            className="px-4 py-2 rounded-full bg-blue-500 text-white hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 transition-colors duration-200"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}