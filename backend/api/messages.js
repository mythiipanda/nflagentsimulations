const express = require('express');
const router = express.Router();
const { getOpenAIResponse } = require("../cerebrasClient");

router.post('/', async (req, res) => {
  const { prompt } = req.body;
  
  try {
    const aiResponse = await getOpenAIResponse(prompt);
    res.json({ response: aiResponse });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'An error occurred' });
  }
});

module.exports = router;
