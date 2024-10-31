import React from 'react';
import NFLChat from '../components/NFLChat';

function AnalysisChat({ theme }) {
  return (
    <div className={theme === 'dark' ? 'dark' : ''}>
      <NFLChat theme={theme} />
    </div>
  );
}
export default AnalysisChat;
