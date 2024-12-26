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
TEAM_NAME = "arizona-cardinals"
TEAM_DB_DIR = "arizona-cardinals"
TEAM_DB_FILE = os.path.join(TEAM_DB_DIR, "team_data.db")
MAIN_DB_PATH = "nfl_draft.db"

# Agent Initialization
agent_name = "Player Ranker"
agent_role = "Rank players on the Arizona Cardinals based on their overall grade."
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
    ],
    memory_file=agent_memory_file,
    cerebras_client=cerebras_client,
)

# Task Prompt
prompt = f"""
You are Player Ranker, a stats analyst for the {TEAM_NAME}.

Your task is to rank the players on the team based on their overall grade from the available data. Do not come up with any information that is not available in the data. Do not use any other tools, such as custom python code.

Here's how you should approach the task:

1. **Get the Roster:** Use the `get_team_roster` tool to get the current roster of the arizona-cardinals.
2. **Rank the players:** Use the `get_ranked_players` tool **once** to retrieve the players within each position group according to their overall grade. The `get_ranked_players` tool will handle all position groups internally.
3. **Present the output from `get_ranked_players` as your final response.**

**Important Instructions:**

*   **Thoughts:** You can have thoughts, which are your internal reasoning steps.
*   **Actions:** Actions involve using a tool. You should only use the tools provided.
*   **Observations:** Observations are the direct results of using a tool. **Do not generate an observation unless you have actually received output from a tool.** Observations should simply state the output from the tool, without any interpretation or modification. Only make observations for tools calls. Do not make observations for text responses, such as presenting a final answer.

Format your response clearly, listing each position and the players ranked by their overall grade in descending order (highest grade first).
"""

# Execute the task
if __name__ == "__main__":
    logging.info(f"Starting agent: {agent_name}")
    logging.info(f"Task: {agent_role}")
    logging.info(f"Team: {TEAM_NAME}")

    response = agent._react_loop(prompt, db_path=MAIN_DB_PATH, team_db_path=TEAM_DB_FILE, max_iterations=5)

    logging.info(f"Agent Response:\n{response}")

    # Save agent memory (if enabled)
    agent.save_memory()

    print(f"Agent response:\n{response}")