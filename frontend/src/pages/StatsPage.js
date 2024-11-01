import React, { useEffect, useState } from 'react';
import TeamStatsDashboard from '../components/TeamStatsDashboard';

const StatsPage = () => {
  const [documents, setDocuments] = useState([]);

  useEffect(() => {
    // Fetch the CSV data from the server or local files
    const fetchData = async () => {
      const passResponse = await fetch('/data/player_stats_pass.csv');
      const defResponse = await fetch('/data/player_stats_def.csv');
      const recResponse = await fetch('/data/player_stats_rec.csv');
      const rushResponse = await fetch('/data/player_stats_rush.csv');

      const passText = await passResponse.text();
      const defText = await defResponse.text();
      const recText = await recResponse.text();
      const rushText = await rushResponse.text();

      setDocuments([
        { source: '/data/player_stats_pass.csv', document_content: passText },
        { source: '/data/player_stats_def.csv', document_content: defText },
        { source: '/data/player_stats_rec.csv', document_content: recText },
        { source: '/data/player_stats_rush.csv', document_content: rushText },
      ]);
    };

    fetchData();
  }, []);

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-4 dark:text-gray-300">Team Statistics Dashboard</h1>
      <TeamStatsDashboard documents={documents} />
    </div>
  );
};

export default StatsPage;