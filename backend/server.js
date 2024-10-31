// backend/server.js
require('dotenv').config();
const express = require('express');
const cors = require('cors');
const { getCompletion, listModels, retrieveModel } = require('./cerebrasClient');
const app = express();
const PORT = process.env.PORT || 5000;

// Enable CORS
app.use(cors({
  origin: 'http://localhost:3000', // Allow only frontend origin
  methods: ['GET', 'POST'],        // Allow specific methods
  credentials: true                // Allow credentials
}));

app.use(express.json());

app.post('/api/chat', async (req, res) => {
  const { prompt } = req.body;
  try {
    const response = await getCompletion(prompt);
    res.json(response);
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ error: 'Error getting completion' });
  }
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});