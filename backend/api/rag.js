const express = require('express');
const { exec } = require('child_process');
const router = express.Router();

router.post('/', async (req, res) => {
  const { question } = req.body;
  if (!question) {
    return res.status(400).json({ error: 'Question is required' });
  }

  try {
    const pythonProcess = exec(`python ragLangChain.py "${question}"`, (error, stdout, stderr) => {
      if (error) {
        console.error(`exec error: ${error}`);
        return res.status(500).json({ error: 'Error executing Python script' });
      }
      if (stderr) {
        console.error(`stderr: ${stderr}`);
        return res.status(500).json({ error: 'Error in Python script' });
      }
      try {
        const response = JSON.parse(stdout);
        res.json(response);
      } catch (jsonError) {
        console.error(`JSON parse error: ${jsonError}`);
        res.status(500).json({ error: 'Error parsing Python response' });
      }
    });
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ error: 'Error processing request' });
  }
});

module.exports = router;
