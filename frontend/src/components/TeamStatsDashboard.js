import React, { useState, useEffect } from 'react';
import StatsCard from './StatsCard';
import BarChartComponent from './BarChartComponent';
import EfficiencyChart from './EfficiencyChart';
import { parseCSV, calculateTeamStats, calculateLeagueSummary } from './utils';

const TeamStatsDashboard = () => {
  const [activeTab, setActiveTab] = useState('offense');
  const [documents, setDocuments] = useState([]);

  useEffect(() => {
    const fetchCSV = async (fileName) => {
      const response = await fetch(`/data/${fileName}`);
      const text = await response.text();
      return { source: fileName, document_content: text };
    };

    const loadDocuments = async () => {
      const files = ['player_stats_pass.csv', 'player_stats_def.csv', 'player_stats_rec.csv', 'player_stats_rush.csv'];
      const docs = await Promise.all(files.map(fetchCSV));
      setDocuments(docs);
    };

    loadDocuments();
  }, []);

  const [passDoc, defDoc, recDoc, rushDoc] = documents.map(doc => {
    const source = doc.source.split('/').pop();
    return {
      type: source.includes('pass') ? 'pass' : 
            source.includes('def') ? 'def' :
            source.includes('rec') ? 'rec' : 'rush',
      data: parseCSV(doc.document_content)
    };
  });

  const teamStats = calculateTeamStats(passDoc?.data || []);
  const leagueSummary = calculateLeagueSummary(passDoc?.data || []);

  const renderContent = () => {
    switch (activeTab) {
      case 'offense':
        return (
          <div className="space-y-4">
            <BarChartComponent 
              data={teamStats}
              dataKeys={['completionRate', 'yardsPerPlay']}
              title="Offensive Production"
            />
            <BarChartComponent 
              data={teamStats}
              dataKeys={['blitzRate', 'pressureRate']}
              title="Pressure Metrics"
            />
          </div>
        );
      case 'defense':
        return (
          <BarChartComponent 
            data={defDoc?.data || []}
            dataKeys={['comb', 'sk', 'int']}
            title="Defensive Statistics"
          />
        );
      case 'efficiency':
        return <EfficiencyChart data={teamStats} />;
      default:
        return null;
    }
  };

  return (
    <div className="p-4 space-y-8">
      <StatsCard title="League Summary" stats={leagueSummary} />
      
      <div className="border-b border-gray-200 dark:border-gray-700">
        <div className="flex space-x-4">
          {['offense', 'defense', 'efficiency'].map((tab) => (
            <button
              key={tab}
              className={`py-2 px-4 border-b-2 ${
                activeTab === tab 
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400' 
                  : 'border-transparent text-gray-500 dark:text-gray-400'
              }`}
              onClick={() => setActiveTab(tab)}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>
      </div>

      <div className="mt-4">
        {renderContent()}
      </div>
    </div>
  );
};

export default TeamStatsDashboard;