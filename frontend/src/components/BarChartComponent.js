import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const BarChartComponent = ({ data, dataKeys, title }) => (
  <div className="bg-white rounded-lg shadow-md p-4 w-full">
    <h3 className="text-xl font-bold mb-4">{title}</h3>
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="team" />
        <YAxis />
        <Tooltip />
        <Legend />
        {dataKeys.map((key, index) => (
          <Bar 
            key={key} 
            dataKey={key} 
            fill={`hsl(${index * 40}, 70%, 50%)`}
          />
        ))}
      </BarChart>
    </ResponsiveContainer>
  </div>
);

export default BarChartComponent;