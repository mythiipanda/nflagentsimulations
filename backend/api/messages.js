const express = require('express');
const router = express.Router();
const { getCompletion } = require("../cerebrasClient");

router.post('/', async (req, res) => {
  const { sessionId, prompt } = req.body;
  
  try {
    const aiResponse = await getCompletion(sessionId, prompt);
    res.json({ response: aiResponse.content });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'An error occurred' });
  }
});

module.exports = router;
