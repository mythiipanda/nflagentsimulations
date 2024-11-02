const { MongoClient } = require("mongodb");
const { BufferMemory } = require("langchain/memory");
const { MongoDBChatMessageHistory } = require("@langchain/mongodb");
const { ConversationChain } = require("langchain/chains");
const { ChatOpenAI } = require("@langchain/openai");
const { generateChart } = require("./chartGenerator");
class ChatMemoryService {
  constructor() {
    this.client = new MongoClient(process.env.MONGODB_ATLAS_URI || "", {
      driverInfo: { name: "langchainjs" }
    });

    // Initialize ChatOpenAI with Cerebras configuration
    this.llm = new ChatOpenAI({
      openAIApiKey: process.env.OPENAI_API_KEY,
      configuration: {
        basePath: "https://api.cerebras.ai/v1",
      },
      modelName: "llama3.1-8b", // or your specific model
      temperature: 0.7,
    });

    this.sessionChains = new Map();
    this.isConnected = false;
  }

  async ensureConnection() {
    if (!this.isConnected) {
      await this.connect();
    }
  }

  async connect() {
    if (!this.isConnected) {
      await this.client.connect();
      this.collection = this.client.db("nfl_chat").collection("conversations");
      this.isConnected = true;
      console.log("Connected to MongoDB");
    }
  }

  async getOrCreateConversationChain(sessionId) {
    await this.ensureConnection();

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
        llm: this.llm,
        memory: memory,
      });

      this.sessionChains.set(sessionId, chain);
    }

    return this.sessionChains.get(sessionId);
  }

  async processMessage(sessionId, message) {
    await this.ensureConnection();
    const chain = await this.getOrCreateConversationChain(sessionId);
    const response = await chain.call({ input: message });

    // Log the response to debug
    console.log('Response:', response);

    let content;
    if (typeof response.response === 'string') {
      try {
        const parsedResponse = JSON.parse(response.response);
        if (Array.isArray(parsedResponse)) {
          content = parsedResponse[0]?.kwargs?.content;
        } else {
          content = parsedResponse.kwargs?.content;
        }
      } catch (error) {
        content = response.response;
      }
    }

    // Check if the message contains a Python code snippet for a chart
    const codeSnippetMatch = content.match(/```python([\s\S]*?)```/);
    let pythonCode = null;
    let textContent = content;
    if (codeSnippetMatch) {
      pythonCode = codeSnippetMatch[1].trim();
      textContent = content.replace(/```python[\s\S]*?```/, '').trim();
    }

    let imageUrl = null;
    if (pythonCode) {
      try {
        imageUrl = await generateChart(pythonCode);
      } catch (error) {
        console.error("Error generating chart:", error);
        textContent += `\nError generating chart`;
      }
    }

    return { textContent, pythonCode, imageUrl };
  }

  async getChatHistory(sessionId) {
    await this.ensureConnection();
    const chain = await this.getOrCreateConversationChain(sessionId);
    const messages = await chain.memory.chatHistory.getMessages();
    // Extract and return only the content from each message
    return messages.map(message => message.kwargs.content);
  }

  async clearChatHistory(sessionId) {
    await this.ensureConnection();
    const chain = await this.getOrCreateConversationChain(sessionId);
    await chain.memory.chatHistory.clear();
    this.sessionChains.delete(sessionId);
  }

  async close() {
    if (this.isConnected) {
      await this.client.close();
      this.isConnected = false;
    }
  }
}

module.exports = ChatMemoryService;
