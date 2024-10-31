import React from 'react';

const Home = () => {
  return (
    <main className="container mx-auto px-4 py-16">
      <div className="max-w-4xl mx-auto text-center">
        <h1 className="text-6xl font-bold tracking-tight mb-8">
          AI-Powered
          <br />
          NFL Draft Analytics
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-300 mb-12">
          Advanced draft simulation and player analysis powered by artificial intelligence.
          Make better decisions with data-driven insights.
        </p>
        <div className="flex justify-center gap-4">
          <button className="px-8 py-3 rounded-full text-lg bg-white dark:bg-gray-800 text-black dark:text-white hover:bg-gray-100 dark:hover:bg-gray-700">
            Try Draft Simulation
          </button>
          <button className="px-8 py-3 rounded-full text-lg border-2 border-current hover:bg-gray-100 dark:hover:bg-gray-800">
            View Analysis
          </button>
        </div>
      </div>
    </main>
  );
};

export default Home;
