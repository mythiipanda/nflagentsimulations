import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Header from './components/Header';
import Home from './pages/Home';
import AnalysisChat from './pages/AnalysisChat';
import StatsPage from './pages/StatsPage'; // Import the new StatsPage component

function App() {
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('theme') || 'dark';
  });

  useEffect(() => {
    document.documentElement.classList.toggle('dark-mode', theme === 'dark');
    localStorage.setItem('theme', theme);
  }, [theme]);

  return (
    <Router>
      <div className={`min-h-screen ${theme}`}>
        <div className="bg-white dark:bg-[#0a0a1f] text-black dark:text-white min-h-screen">
          <Header theme={theme} setTheme={setTheme} />
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/analysis-chat" element={<AnalysisChat theme={theme} />} />
            <Route path="/statistics" element={<StatsPage />} /> {/* Add the new route */}
            {/* Add other routes here */}
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;