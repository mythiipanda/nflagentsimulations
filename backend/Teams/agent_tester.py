import os
import logging
from dotenv import load_dotenv
from cerebras.cloud.sdk import Cerebras
from agent import Agent
import tools

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Cerebras client
cerebras_api_key = os.getenv("CEREBRAS_API_KEY")
if not cerebras_api_key:
    raise ValueError("CEREBRAS_API_KEY environment variable not set.")
cerebras_client = Cerebras(api_key=cerebras_api_key)

# Team and Database Information
TEAM_NAME = "chicago-bears"
TEAM_DB_DIR = "chicago-bears"
TEAM_DB_FILE = os.path.join(TEAM_DB_DIR, "team_data.db")
MAIN_DB_PATH = "global_database.db"

# Agent Initialization
agent_name = "NFL Analyst"
agent_role = "Analyze the Chicago Bears and determine areas for improvement in the upcoming draft."
agent_memory_file = f"{TEAM_NAME}_memory.txt"

# Updated tools list to include new tools
# Define the agent
agent = Agent(
    name=agent_name,
    role=agent_role,
    team=TEAM_NAME,
    tools=[
        tools.get_team_roster,
        tools.get_player_stats,
        tools.get_ranked_players,
        tools.get_position_stats,
        tools.compare_players,
        tools.get_position_group,
        tools.query_team_stats,
    ],
    memory_file=agent_memory_file,
    cerebras_client=cerebras_client,
)

# Task Prompt
prompt = f"""
You are an NFL analyst for the {TEAM_NAME}. Evaluate the team's current roster, performance, and overall stats. Based on your assessment, identify the key positions that the team should target in the upcoming draft to improve their roster. Provide a concise report of your findings.
"""

# Execute the task
if __name__ == "__main__":
    logging.info(f"Starting agent: {agent_name}")
    logging.info(f"Task: {agent_role}")
    logging.info(f"Team: {TEAM_NAME}")

    response = agent._react_loop(prompt, db_path=MAIN_DB_PATH, team_db_path=TEAM_DB_FILE, max_iterations=10)

    logging.info(f"Agent Response:\n{response}")

    # Save agent memory (if enabled)
    agent.save_memory()

    print(f"Agent response:\n{response}")