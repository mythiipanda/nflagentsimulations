// utils.js
export const parseCSV = (csvString) => {
    const lines = csvString.trim().split('\n');
    const headers = lines[0].split(',');
    return lines.slice(1).map(line => {
      const values = line.split(',');
      return headers.reduce((obj, header, index) => {
        obj[header] = isNaN(values[index]) ? values[index] : parseFloat(values[index]);
        return obj;
      }, {});
    });
  };
  
  export const calculateTeamStats = (passData) => {
    const stats = {};
    
    passData.forEach(player => {
      if (!stats[player.team]) {
        stats[player.team] = {
          attempts: 0,
          completions: 0,
          yards: 0,
          pressures: 0,
          blitzes: 0,
          plays: 0
        };
      }
      
      stats[player.team].attempts += player.pass_attempts || 0;
      stats[player.team].pressures += player.times_pressured || 0;
      stats[player.team].blitzes += player.times_blitzed || 0;
      stats[player.team].plays += player.pass_attempts || 0;
    });
  
    return Object.entries(stats).map(([team, data]) => ({
      team,
      completionRate: (data.completions / data.attempts) * 100,
      yardsPerPlay: data.yards / data.plays,
      conversionRate: data.conversions / data.plays * 100,
      pressureRate: (data.pressures / data.attempts) * 100,
      blitzRate: (data.blitzes / data.attempts) * 100
    }));
  };
  
  export const calculateLeagueSummary = (passData) => ({
    "Avg Pass Attempts": passData.reduce((acc, curr) => acc + curr.pass_attempts, 0) / passData.length,
    "Avg Completion %": passData.reduce((acc, curr) => acc + curr.cmp_percent, 0) / passData.length,
    "Avg Yards/Attempt": passData.reduce((acc, curr) => acc + (curr.yds / curr.pass_attempts), 0) / passData.length,
    "Pressure Rate": passData.reduce((acc, curr) => acc + curr.pressure_pct, 0) / passData.length
  });