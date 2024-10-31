// server.js
require('dotenv').config();
const express = require('express');
const cors = require('cors');
const { getCompletion, listModels, retrieveModel } = require('./cerebrasClient');
const ChatMemoryService = require('./chatMemoryService');

const app = express();
const PORT = process.env.PORT || 5000;

// Initialize ChatMemoryService
const chatMemoryService = new ChatMemoryService();

// Connect to MongoDB when the server starts
(async () => {
  try {
    await chatMemoryService.connect();
  } catch (error) {
    console.error('Failed to connect to MongoDB:', error);
    process.exit(1);
  }
})();

// Enable CORS
app.use(cors({
  origin: 'http://localhost:3000',
  methods: ['GET', 'POST'],
  credentials: true
}));

app.use(express.json());

app.post('/api/chat', async (req, res) => {
  const { sessionId, prompt } = req.body;
  if (!sessionId) {
    return res.status(400).json({ error: 'Session ID is required' });
  }

  try {
    const response = await getCompletion(sessionId, prompt);
    res.json(response);
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ error: 'Error getting completion' });
  }
});

// Graceful shutdown
process.on('SIGINT', async () => {
  try {
    await chatMemoryService.close();
    process.exit(0);
  } catch (error) {
    console.error('Error during shutdown:', error);
    process.exit(1);
  }
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});