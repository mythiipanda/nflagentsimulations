import React from 'react';

const StatsCard = ({ title, stats }) => (
  <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4 w-full">
    <h3 className="text-xl font-bold mb-4 dark:text-gray-300">{title}</h3>
    <div className="grid grid-cols-2 gap-4">
      {Object.entries(stats).map(([key, value]) => (
        <div key={key} className="flex flex-col">
          <span className="text-sm text-gray-500 dark:text-gray-400">{key}</span>
          <span className="text-2xl font-bold dark:text-gray-300">
            {typeof value === 'number' ? value.toFixed(1) : value}
          </span>
        </div>
      ))}
    </div>
  </div>
);

export default StatsCard;