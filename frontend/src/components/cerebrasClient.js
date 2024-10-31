import OpenAI from 'openai';
import { MongoClient, ObjectId } from "mongodb";
// import { BufferMemory } from "langchain/memory";
// import { ConversationChain } from "langchain/chains";
// import { MongoDBChatMessageHistory } from "@langchain/mongodb";
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
// const mongoClient = new MongoClient(process.env.REACT_APP_MONGODB_ATLAS_URI || "", {
//   driverInfo: { name: "langchainjs" },
// });
// await mongoClient.connect();
// // const collection = mongoClient.db("langchain").collection("memory");
// // const sessionId = new ObjectId().toString();
// // const memory = new BufferMemory({
// //   chatHistory: new MongoDBChatMessageHistory({
// //     collection,
// //     sessionId,
// //   }),
// // });
// // const chain = new ConversationChain({ llm: client, memory });
// // const res1 = await chain.invoke({ input: "Hi! I'm Jim." });
// // console.log(res1);
// // const res2 = await chain.invoke({ input: "What did I just say my name was?" });
// // console.log({ res2 });
// // console.log(await memory.chatHistory.getMessages());
// // await memory.chatHistory.clear();
