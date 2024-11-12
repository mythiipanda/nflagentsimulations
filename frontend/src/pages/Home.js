import React from 'react'
import { Link } from 'react-router-dom'
import { BarChart2, MessageSquare } from 'lucide-react'

const Home = () => {
  return (
    <div className="container mx-auto px-4 py-16">
      <div className="text-center">
        <h1 className="text-5xl font-bold mb-6 text-blue-600 dark:text-blue-400">
          AI-Powered NFL Draft Insights
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-300 mb-12 max-w-2xl mx-auto">
          Make smarter draft decisions with our advanced simulation and player analysis tools,
          powered by cutting-edge artificial intelligence. Gain a competitive edge with
          data-driven insights.
        </p>
        <div className="flex flex-col md:flex-row gap-6 justify-center">
          <Link
            to="/draft-simulation"
            className="inline-flex items-center px-6 py-3 rounded-full text-lg bg-blue-600 text-white hover:bg-blue-700 transition-colors duration-200"
          >
            <BarChart2 className="mr-2" size={24} />
            Try Draft Simulation
          </Link>
          <Link
            to="/analysis-chat"
            className="inline-flex items-center px-6 py-3 rounded-full text-lg border-2 border-blue-600 text-blue-600 hover:bg-blue-600 hover:text-white transition-colors duration-200"
          >
            <MessageSquare className="mr-2" size={24} />
            View AI Analysis
          </Link>
        </div>
      </div>
    </div>
  )
}

export default Home