// backend/cerebrasClient.js
const OpenAI = require('openai');
const { MongoClient } = require('mongodb');

const client = new OpenAI({
  apiKey: process.env.REACT_APP_OpenAI_API_KEY,
  baseURL: "https://api.cerebras.ai/v1",
});

async function getCompletion(prompt) {
  const completion = await client.chat.completions.create({
    messages: [{ role: 'user', content: prompt }],
    model: 'llama3.1-8b',
  });
  return completion?.choices[0]?.message;
}

async function listModels() {
  return await client.models.list();
}

async function retrieveModel(modelId) {
  return await client.models.retrieve(modelId);
}

module.exports = { getCompletion, listModels, retrieveModel };
