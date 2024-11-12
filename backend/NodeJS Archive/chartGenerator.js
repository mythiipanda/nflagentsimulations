const { spawn } = require("child_process");
const path = require("path");

async function generateChart(generatedCode) {
  return new Promise((resolve, reject) => {
    const pythonProcess = spawn("python", [
      path.join(__dirname, "chart_script.py"),
      generatedCode,
    ]);

    pythonProcess.stdout.on("data", (data) => {
      const imagePath = data.toString().trim();
      const timestamp = new Date().getTime(); // Add a timestamp to the URL
      const fullUrl = `http://localhost:5000/public/${path.basename(imagePath)}?t=${timestamp}`;
      resolve(fullUrl);
    });

    pythonProcess.stderr.on("data", (data) => {
      reject(`Error generating chart: ${data.toString()}`);
    });
  });
}

module.exports = { generateChart };