from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv
from crew_test import NflCrew  # Import NflCrew
from threading import Thread

# Load environment variables
load_dotenv()
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

nfl_crew = NflCrew()  # Initialize NflCrew object

def process_prompt(prompt, session_id, result_dict):
    try:
        # Use the NflCrew object to process the prompt
        inputs = {"query": prompt}
        response = nfl_crew.crew().kickoff(inputs=inputs)
        # Store the response text directly
        result_dict['response'] = str(response)
    except Exception as e:
        result_dict['error'] = f"Error processing message: {str(e)}"

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    session_id = data.get('sessionId')
    prompt = data.get('prompt')

    if not session_id:
        return jsonify({"error": "Session ID is required"}), 400

    result_dict = {}
    thread = Thread(target=process_prompt, args=(prompt, session_id, result_dict))
    thread.start()
    thread.join()

    if 'error' in result_dict:
        return jsonify({"error": result_dict['error']}), 500

    # Return the text response directly
    return jsonify({"content": result_dict['response']})

@app.route('/public/<path:filename>')
def serve_file(filename):
    return send_from_directory('public', filename)

if __name__ == '__main__':
    # Create public directory if it doesn't exist
    os.makedirs('public', exist_ok=True)
    # Enable debug mode for better error messages
    app.run(port=5000, debug=True)