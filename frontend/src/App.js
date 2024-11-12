import React, { useState } from 'react'
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import Home from './pages/Home'
import AnalysisChat from './pages/AnalysisChat'
import StatsPage from './pages/StatsPage'

function App() {
  const [isDarkMode, setIsDarkMode] = useState(false)

  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode)
  }

  return (
    <Router>
      <Layout toggleDarkMode={toggleDarkMode} isDarkMode={isDarkMode}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/analysis-chat" element={<AnalysisChat />} />
          <Route path="/stats" element={<StatsPage />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App