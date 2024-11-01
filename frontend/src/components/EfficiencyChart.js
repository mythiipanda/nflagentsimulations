import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const EfficiencyChart = ({ data }) => (
  <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4 w-full">
    <h3 className="text-xl font-bold mb-4 dark:text-gray-300">Team Efficiency Metrics</h3>
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="team" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="completionRate" stroke="#8884d8" />
        <Line type="monotone" dataKey="yardsPerPlay" stroke="#82ca9d" />
        <Line type="monotone" dataKey="conversionRate" stroke="#ffc658" />
      </LineChart>
    </ResponsiveContainer>
  </div>
);

export default EfficiencyChart;