// backend/cerebrasClient.js
const OpenAI = require('openai');
const ChatMemoryService = require('./chatMemoryService');

const client = new OpenAI({
  apiKey: process.env.REACT_APP_OpenAI_API_KEY,
  baseURL: "https://api.cerebras.ai/v1",
});

const chatMemoryService = new ChatMemoryService();

async function getCompletion(sessionId, prompt) {
  return await chatMemoryService.processMessage(sessionId, prompt);
}

async function listModels() {
  return await client.models.list();
}

async function retrieveModel(modelId) {
  return await client.models.retrieve(modelId);
}

module.exports = { getCompletion, listModels, retrieveModel };
