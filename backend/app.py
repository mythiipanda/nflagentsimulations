# app.py
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv
import openai
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from pymongo import MongoClient
from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from uuid import uuid4
import io
import contextlib
import traceback
import numpy as np
matplotlib.use('Agg')
# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

# Initialize OpenAI client for Cerebras
openai_client = openai.Client(
    base_url="https://api.cerebras.ai/v1",
    api_key=os.getenv("CEREBRAS_API_KEY")
)

# MongoDB setup
mongo_client = MongoClient(os.getenv("MONGODB_ATLAS_URI"))
db = mongo_client.nfl_chat
collection = db.conversations

class ChartGenerationError(Exception):
    pass

class ChatMemoryService:
    def __init__(self):
        self.llm = ChatOpenAI(
            openai_api_key=os.getenv("CEREBRAS_API_KEY"),
            base_url="https://api.cerebras.ai/v1",
            model_name="llama3.1-8b",
            temperature=0.7
        )
        self.session_chains = {}
        
    def get_or_create_conversation_chain(self, session_id):
        if session_id not in self.session_chains:
            message_history = MongoDBChatMessageHistory(
                connection_string=os.getenv("MONGODB_ATLAS_URI"),
                database_name="nfl_chat",
                collection_name="conversations",
                session_id=session_id
            )
            
            memory = ConversationBufferMemory(
                memory_key="history",
                chat_memory=message_history,
                return_messages=True
            )
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are an NFL analytics expert. Provide detailed analysis with stats and data."),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{input}")
            ])
            
            self.session_chains[session_id] = {
                "memory": memory,
                "prompt": prompt
            }
            
        return self.session_chains[session_id]

    async def process_message(self, session_id, message):
        chain = self.get_or_create_conversation_chain(session_id)
        memory = chain["memory"]
        prompt = chain["prompt"]
        
        # Format the prompt with the conversation history
        messages = prompt.format_messages(
            history=memory.chat_memory.messages,
            input=message
        )
        
        # Get response from the LLM
        response = await self.llm.ainvoke(messages)
        content = response.content
        
        # Extract Python code if present
        python_code = None
        if "```python" in content:
            code_start = content.find("```python") + 9
            code_end = content.find("```", code_start)
            if code_end != -1:
                python_code = content[code_start:code_end].strip()
                content = content.replace(content[code_start-9:code_end+3], "").strip()
        
        # Generate chart if Python code exists
        image_url = None
        if python_code:
            try:
                image_url = await self.generate_chart(python_code)
            except ChartGenerationError as e:
                print(f"Error generating chart: {str(e)}")
                content += f"\nError generating chart: {str(e)}"
            except Exception as e:
                print(f"Unexpected error generating chart: {str(e)}")
                content += "\nUnexpected error generating chart"
        
        # Store the message in memory
        memory.save_context({"input": message}, {"output": content})
        
        return {
            "textContent": content,
            "pythonCode": python_code,
            "imageUrl": image_url
        }

    async def generate_chart(self, python_code):
        # Create a unique filename for the chart
        filename = f"chart_{uuid4()}.png"
        filepath = os.path.join("public", filename)
        
        # Capture stdout and stderr
        stdout = io.StringIO()
        stderr = io.StringIO()
        
        try:
            # Clear any existing plots
            plt.clf()
            
            # Ensure the code is properly formatted
            formatted_code = python_code.replace('\\n', '\n').replace('\\t', '\t')
            
            # Set up the environment for code execution
            namespace = {
                'pd': pd,
                'plt': plt,
                'np': np,
                'os': os,
                'io': io,
                'uuid4': uuid4
            }
            
            # Execute the code with output capturing
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                exec(formatted_code, namespace)
            
            # Check if a figure was created
            if plt.get_fignums():
                # Save the plot with tight layout and high DPI
                plt.savefig(filepath, bbox_inches='tight', dpi=300)
                plt.close()
                
                # Return the URL for the saved image
                return f"/public/{filename}"
            else:
                raise ChartGenerationError("No plot was generated by the code")
            
        except Exception as e:
            # Get the full traceback
            tb = traceback.format_exc()
            
            # Clean up any partially created files
            if os.path.exists(filepath):
                os.remove(filepath)
            
            # Close any open plots
            plt.close('all')
            
            # Raise a more informative error
            error_msg = (f"Code execution error: {str(e)}\n"
                        f"Stdout: {stdout.getvalue()}\n"
                        f"Stderr: {stderr.getvalue()}\n"
                        f"Traceback: {tb}")
            raise ChartGenerationError(error_msg)
        
        finally:
            # Clean up
            stdout.close()
            stderr.close()
            plt.close('all')

    def get_chat_history(self, session_id):
        chain = self.get_or_create_conversation_chain(session_id)
        return [msg.content for msg in chain["memory"].chat_memory.messages]

    def clear_chat_history(self, session_id):
        if session_id in self.session_chains:
            chain = self.session_chains[session_id]
            chain["memory"].clear()
            del self.session_chains[session_id]

# Initialize ChatMemoryService
chat_service = ChatMemoryService()

@app.route('/api/chat', methods=['POST'])
async def chat():
    data = request.json
    session_id = data.get('sessionId')
    prompt = data.get('prompt')
    
    if not session_id:
        return jsonify({"error": "Session ID is required"}), 400
    
    try:
        response = await chat_service.process_message(session_id, prompt)
        return jsonify(response)
    except Exception as e:
        error_msg = f"Error processing message: {str(e)}"
        print(error_msg)
        return jsonify({"error": error_msg}), 500

@app.route('/public/<path:filename>')
def serve_file(filename):
    return send_from_directory('public', filename)

if __name__ == '__main__':
    # Create public directory if it doesn't exist
    os.makedirs('public', exist_ok=True)
    # Enable debug mode for better error messages
    app.run(port=5000, debug=True)