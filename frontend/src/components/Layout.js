import React, { ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { Sun, Moon } from 'lucide-react'


export default function Layout({ children, toggleDarkMode, isDarkMode }) { // Removed type annotation
  return (
    <div className={`min-h-screen flex flex-col ${isDarkMode ? 'dark' : ''}`}>
      <header className="bg-white dark:bg-gray-800 shadow-md">
        <nav className="container mx-auto px-4 py-4 flex justify-between items-center">
          <Link to="/" className="text-2xl font-bold text-blue-600 dark:text-blue-400">
            NFL Insights
          </Link>
          <ul className="flex space-x-4">
            <li>
              <Link to="/" className="text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400">
                Home
              </Link>
            </li>
            <li>
              <Link to="/analysis-chat" className="text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400">
                Analysis Chat
              </Link>
            </li>
            <li>
              <Link to="/stats" className="text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400">
                Team Stats
              </Link>
            </li>
            <li>
              <button onClick={toggleDarkMode} className="text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400">
                {isDarkMode ? <Sun size={20} /> : <Moon size={20} />}
              </button>
            </li>
          </ul>
        </nav>
      </header>
      <main className="flex-grow bg-gray-100 dark:bg-gray-900">
        {children}
      </main>
      <footer className="bg-white dark:bg-gray-800 shadow-md">
        <div className="container mx-auto px-4 py-4 text-center text-gray-600 dark:text-gray-300">
          © 2024 NFL Insights. All rights reserved.
        </div>
      </footer>
    </div>
  )
}
