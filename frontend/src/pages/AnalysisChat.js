import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { v4 as uuidv4 } from 'uuid'
import NFLChat from '../components/NFLChat'

const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:5000'

function AnalysisChat() {
  const [chatHistory, setChatHistory] = useState([])
  const [userInput, setUserInput] = useState('')
  const [sessionId] = useState(uuidv4())
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    const initialMessage = {
      role: 'assistant',
      message: {
        textContent:
          "Welcome to the NFL Analytics Chat! Ask me anything about player stats, team performance, game outcomes, and more.",
      },
      timestamp: new Date().toLocaleTimeString(),
    }
    setChatHistory([initialMessage])
  }, [])

  const sendMessage = async () => {
    if (userInput.trim() === '' || isLoading) return

    const newUserMessage = {
      role: 'user',
      message: { textContent: userInput },
      timestamp: new Date().toLocaleTimeString(),
    }
    setChatHistory((prev) => [...prev, newUserMessage])
    setUserInput('')
    setIsLoading(true)

    const instruction = `
    You are an expert NFL analyst.
    `

    const prompt = `${instruction}\n\n${userInput}`

    try {
      const response = await axios.post(`${backendUrl}/api/chat`, { prompt, sessionId })
      setChatHistory((prev) => [
        ...prev,
        {
          role: 'assistant',
          message: {
            textContent: response.data.content,
          },
          timestamp: new Date().toLocaleTimeString(),
        },
      ])
    } catch (error) {
      console.error('Error getting completion:', error)
      setChatHistory((prev) => [
        ...prev,
        {
          role: 'assistant',
          message: { textContent: 'Sorry, I encountered an error. Please try again.' },
          timestamp: new Date().toLocaleTimeString(),
        },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-4 text-blue-600 dark:text-blue-400">
        AI-Powered NFL Analysis Chat
      </h1>
      <p className="text-lg text-gray-600 dark:text-gray-300 mb-6">
        Get insights and answers to your NFL questions. Ask about player stats, team performance,
        draft predictions, and more.
      </p>
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
        <NFLChat
          chatHistory={chatHistory}
          userInput={userInput}
          setUserInput={setUserInput}
          sendMessage={sendMessage}
          isLoading={isLoading}
        />
      </div>
    </div>
  )
}

export default AnalysisChat