const { MongoClient, ObjectId } = require("mongodb");
const { BufferMemory } = require("langchain/memory");
const { MongoDBChatMessageHistory } = require("@langchain/mongodb");
const { ConversationChain } = require("langchain/chains");
const { OpenAI } = require('openai');

class ChatMemoryService {
  constructor() {
    this.client = new MongoClient(process.env.MONGODB_ATLAS_URI || "", {
      driverInfo: { name: "langchainjs" }
    });
    this.openai = new OpenAI({
      apiKey: process.env.REACT_APP_OpenAI_API_KEY,
      baseURL: "https://api.cerebras.ai/v1",
    });
    this.sessionChains = new Map();
  }

  async connect() {
    await this.client.connect();
    this.collection = this.client.db("nfl_chat").collection("conversations");
    console.log("Connected to MongoDB");
  }

  async getOrCreateConversationChain(sessionId) {
    if (!this.sessionChains.has(sessionId)) {
      const memory = new BufferMemory({
        chatHistory: new MongoDBChatMessageHistory({
          collection: this.collection,
          sessionId,
        }),
        returnMessages: true,
        memoryKey: "history",
      });

      const chain = new ConversationChain({
        memory: memory,
        llm: this.openai,
      });

      this.sessionChains.set(sessionId, chain);
    }

    return this.sessionChains.get(sessionId);
  }

  async processMessage(sessionId, message) {
    const chain = await this.getOrCreateConversationChain(sessionId);
    const response = await chain.invoke({ input: message });
    return response;
  }

  async getChatHistory(sessionId) {
    const chain = await this.getOrCreateConversationChain(sessionId);
    return await chain.memory.chatHistory.getMessages();
  }

  async clearChatHistory(sessionId) {
    const chain = await this.getOrCreateConversationChain(sessionId);
    await chain.memory.chatHistory.clear();
    this.sessionChains.delete(sessionId);
  }

  async close() {
    await this.client.close();
  }
}

module.exports = new ChatMemoryService();
