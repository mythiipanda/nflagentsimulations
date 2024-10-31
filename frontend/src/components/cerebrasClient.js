"use server";
import Cerebras from '@cerebras/cerebras_cloud_sdk';
const client = new Cerebras({
  apiKey: 'csk-j268v64kxec4vtrym852hfc98kr54v6cc8kxwne5d2wdt9we',
});

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