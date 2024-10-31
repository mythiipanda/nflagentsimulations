"use server";
import OpenAI from 'openai';
export async function getCompletion(prompt) {
  const completion = await client.chat.completions.create({
    messages: [{ role: 'user', content: prompt }],
    model: 'llama3.1-8b',
  });

  return completion?.choices[0]?.message;
}

export async function listModels() {
  const models = await client.models.list();
  return models;
}

export async function retrieveModel(modelId) {
  const model = await client.models.retrieve(modelId);
  return model;
}
const client = new OpenAI({
  apiKey: process.env.REACT_APP_OpenAI_API_KEY,
  baseURL: "https://api.cerebras.ai/v1",
  dangerouslyAllowBrowser: true,
})