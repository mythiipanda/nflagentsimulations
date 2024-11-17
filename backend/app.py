# app.py

import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from crew_test import NflCrew  # Import NflCrew
from threading import Thread
import os

# Load environment variables
load_dotenv()
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

# Configure logging
logging.basicConfig(level=logging.DEBUG)

nfl_crew = NflCrew()  # Initialize NflCrew object

def process_prompt(prompt, session_id, result_dict):
    try:
        logging.debug("Processing prompt...")
        inputs = {"query": prompt}
        response = nfl_crew.crew().kickoff(inputs=inputs)
        logging.debug(f"Raw Response: {response}")

        # Convert response to string if necessary
        if isinstance(response, dict):
            response_text = response.get('content', 'No content returned.')
        else:
            response_text = str(response)

        result_dict['response'] = response_text
        logging.debug(f"Processed Response: {result_dict['response']}")
    except Exception as e:
        result_dict['error'] = f"Error processing message: {str(e)}"
        logging.error(result_dict['error'])

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    session_id = data.get('sessionId')
    prompt = data.get('prompt')

    if not session_id:
        logging.error("Session ID is missing.")
        return jsonify({"error": "Session ID is required"}), 400

    if not prompt:
        logging.error("Prompt is missing.")
        return jsonify({"error": "Prompt is required"}), 400

    result_dict = {}
    thread = Thread(target=process_prompt, args=(prompt, session_id, result_dict))
    thread.start()
    thread.join()

    if 'error' in result_dict:
        logging.error(f"Error in chat endpoint: {result_dict['error']}")
        return jsonify({"error": result_dict['error']}), 500

    logging.debug("Returning response to frontend.")
    return jsonify({"content": result_dict['response']})

@app.route('/public/<path:filename>')
def serve_file(filename):
    return send_from_directory('public', filename)

if __name__ == '__main__':
    # Create public directory if it doesn't exist
    os.makedirs('public', exist_ok=True)
    # Enable debug mode for better error messages
    app.run(port=5000, debug=True)