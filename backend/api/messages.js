const express = require('express');
const router = express.Router();
const { getMessages, sendMessage } = require('../../frontend/src/components/cerebrasClient');

router.get('/:channel', async (req, res) => {
  try {
    const messages = await getMessages(req.params.channel);
    res.json(messages);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

router.post('/:channel', async (req, res) => {
  try {
    const message = await sendMessage(req.params.channel, req.body.message);
    res.json(message);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

module.exports = router;
