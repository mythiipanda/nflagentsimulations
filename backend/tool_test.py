# tool_test.py

import os
from dotenv import load_dotenv
from pff_tool import RetrieveFromChromaDBTool

# Load environment variables
load_dotenv()

# Instantiate the tool
tool = RetrieveFromChromaDBTool()

# Define the input for the tool
input_data = {
    "query": "Patrick Mahomes"
}

# Run the tool and print the result
try:
    result = tool._run(**input_data)
    print(result)
except Exception as e:
    print(f"Error: {e}")