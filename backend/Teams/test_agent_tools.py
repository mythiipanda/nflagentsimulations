import unittest
import sqlite3
import os
from agent import Agent
import tools
from dotenv import load_dotenv
from cerebras.cloud.sdk import Cerebras
import shutil
import logging
from datetime import datetime
from unittest.mock import patch, MagicMock
from typing import List

# Load environment variables
load_dotenv()

# Generate a unique log filename with timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_filename = f"test_logs_{timestamp}.txt"

# Set up logging to a unique .txt file
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(message)s'
)

# Define the test database path
TEST_DATABASE_PATH = "test_nfl_draft.db"
TEST_TEAM_DATABASE_DIR = "test_team_databases"
TEST_TEAM = "arizona-cardinals"

class TestTools(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logging.info("Setting up TestTools class")
        cls.conn = None  # Initialize conn to None

        # Define test_team and test_player as class attributes
        cls.test_team = "arizona-cardinals"
        cls.test_player = "Marvin Harrison Jr."

        # Set up a clean test database
        cls.setup_test_database()

        # Add a valid player to the test database for testing
        cls.add_test_player(cls.test_player)

        # Add a sample draft order entry for testing
        cls.add_draft_order_entry()

    @classmethod
    def setup_test_database(cls):
        # Ensure the main test database is removed before creating a new copy
        if os.path.exists(TEST_DATABASE_PATH):
            try:
                os.remove(TEST_DATABASE_PATH)
                logging.info(f"Removed existing test database: {TEST_DATABASE_PATH}")
            except Exception as e:
                logging.warning(f"Could not delete {TEST_DATABASE_PATH}: {e}")
                print(f"Warning: Could not delete {TEST_DATABASE_PATH} due to: {e}")
                print("Attempting to proceed anyway...")

        try:
            with sqlite3.connect(os.path.join(os.path.dirname(__file__), "nfl_draft.db")) as original_conn:
                with sqlite3.connect(TEST_DATABASE_PATH) as test_conn:
                    original_conn.backup(test_conn)
            logging.info("Test database setup completed")

            # Log the structure of the main test database
            cls.log_database_structure(cls.conn, "Main Test Database")
        except Exception as e:
            logging.error(f"Error during database setup: {e}")
            print(f"Error during database setup: {e}")
            raise

        # Create the directory for team databases if it doesn't exist
        os.makedirs(TEST_TEAM_DATABASE_DIR, exist_ok=True)
        logging.info(f"Ensured test team database directory exists: {TEST_TEAM_DATABASE_DIR}")

        # Copy the team database to the test directory
        team_db_path = os.path.join(TEST_TEAM_DATABASE_DIR, TEST_TEAM)
        os.makedirs(team_db_path, exist_ok=True)  # Create team directory
        team_db_file = os.path.join(team_db_path, "team_data.db")

        if os.path.exists(team_db_file):
            try:
                os.remove(team_db_file)
                logging.info(f"Removed existing team database: {team_db_file}")
            except Exception as e:
                logging.warning(f"Could not delete {team_db_file}: {e}")
                print(f"Warning: Could not delete {team_db_file} due to: {e}")
                print("Attempting to proceed anyway...")

        try:
            with sqlite3.connect(os.path.join(os.path.dirname(__file__), TEST_TEAM, "team_data.db")) as original_conn:
                with sqlite3.connect(team_db_file) as test_conn:
                    original_conn.backup(test_conn)
            logging.info(f"Copied team database to: {team_db_file}")

            # Log the structure of the team database
            team_conn = sqlite3.connect(team_db_file)
            cls.log_database_structure(team_conn, f"Team Database ({cls.test_team})")
            team_conn.close()
        except Exception as e:
            logging.warning(f"Could not copy {team_db_file}: {e}")
            print(f"Warning: Could not copy {team_db_file} due to: {e}")
            print("Attempting to proceed anyway...")

    @classmethod
    def log_database_structure(cls, connection, description):
        """Logs the structure of the given SQLite database connection."""
        logging.info(f"Database Structure: {description}")
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for table in tables:
            table_name = table[0]
            logging.info(f"  Table: {table_name}")
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            for column in columns:
                cid, name, type_, notnull, dflt_value, pk = column
                logging.info(f"    Column ID: {cid}, Name: {name}, Type: {type_}, Not Null: {notnull}, Default: {dflt_value}, Primary Key: {pk}")
        cursor.close()

    @classmethod
    def add_test_player(cls, player_name):
        # Add a valid player to the test database for testing
        try:
            conn = sqlite3.connect(TEST_DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO available_players (name, position, height, weight, college)
                VALUES (?, ?, ?, ?, ?)
            """, (player_name, 'WR', '6-3', 205, 'Ohio State'))
            conn.commit()
            conn.close()
            logging.info(f"Added test player '{player_name}' to available_players table.")
        except Exception as e:
            logging.error(f"Error adding test player to available_players: {e}")
            raise

    @classmethod
    def add_draft_order_entry(cls):
        # Add a sample draft order entry for testing
        try:
            conn = sqlite3.connect(TEST_DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO draft_order (round, pick, team) VALUES (?, ?, ?)", (1, 1, TEST_TEAM))
            conn.commit()
            conn.close()
            logging.info("Added sample entry to draft_order table.")
        except Exception as e:
            logging.error(f"Error adding entry to draft_order: {e}")
            raise

    @classmethod
    def tearDownClass(cls):
        logging.info("Tearing down TestTools class")
        if hasattr(cls, 'conn') and cls.conn:
            cls.conn.close()
            logging.info("Closed test database connection")

        # Clean up the test database
        if os.path.exists(TEST_DATABASE_PATH):
            try:
                os.remove(TEST_DATABASE_PATH)
                logging.info(f"Removed test database: {TEST_DATABASE_PATH}")
            except Exception as e:
                logging.error(f"Error cleaning up test database: {e}")

        # Clean up the test team database directory
        if os.path.exists(TEST_TEAM_DATABASE_DIR):
            try:
                shutil.rmtree(TEST_TEAM_DATABASE_DIR)
                logging.info(f"Removed test team database directory: {TEST_TEAM_DATABASE_DIR}")
            except Exception as e:
                logging.error(f"Error cleaning up test team database directory: {e}")

    def test_get_team_roster(self):
        logging.info(f"Testing get_team_roster for team: {self.test_team}")
        team_db_path = os.path.join(TEST_TEAM_DATABASE_DIR, TEST_TEAM, "team_data.db")
        roster_str = tools.get_team_roster(self.test_team, team_db_path)
        self.assertIn(self.test_team, roster_str)
        logging.info("test_get_team_roster passed")

    def test_get_player_stats(self):
        logging.info(f"Testing get_player_stats for player: {self.test_player}")
        team_db_path = os.path.join(TEST_TEAM_DATABASE_DIR, TEST_TEAM, "team_data.db")
        stats_str = tools.get_player_stats(self.test_player, TEST_DATABASE_PATH, team_db_path)
        self.assertIn(self.test_player, stats_str)
        logging.info("test_get_player_stats passed")

    def test_get_draft_order(self):
        logging.info("Testing get_draft_order")
        order_str = tools.get_draft_order(TEST_DATABASE_PATH)
        self.assertIsNotNone(order_str)
        logging.info("test_get_draft_order passed")

    def test_get_remaining_needs(self):
        logging.info(f"Testing get_remaining_needs for team: {self.test_team}")
        team_db_path = os.path.join(TEST_TEAM_DATABASE_DIR, TEST_TEAM, "team_data.db")
        needs_str = tools.get_remaining_needs(self.test_team, team_db_path)
        self.assertIn("placeholder", needs_str)
        logging.info("test_get_remaining_needs passed")

    def test_make_draft_pick(self):
        logging.info(f"Testing make_draft_pick for team: {self.test_team} and player: {self.test_player}")
        team_db_path = os.path.join(TEST_TEAM_DATABASE_DIR, TEST_TEAM, "team_data.db")
        pick_result = tools.make_draft_pick(TEST_TEAM, self.test_player, TEST_DATABASE_PATH, team_db_path)
        self.        self.assertIn(self.test_player, pick_result)
        logging.info("test_make_draft_pick passed")

class TestAgent(unittest.TestCase):
    def setUp(self):
        logging.info("Setting up TestAgent instance")
        # Load Cerebras API key from environment variables
        cerebras_api_key = os.getenv("CEREBRAS_API_KEY")
        if not cerebras_api_key:
            logging.error("CEREBRAS_API_KEY environment variable not set.")
            raise ValueError("CEREBRAS_API_KEY environment variable not set.")
        # Create a Cerebras client instance
        cerebras_client = Cerebras(api_key=cerebras_api_key)

        # Create a test agent with the tools and pass the Cerebras client
        self.agent = Agent("Test Agent", "Tester", team=TEST_TEAM, tools=[
            tools.get_team_roster,
            tools.get_player_stats,
            tools.get_draft_order,
            tools.get_remaining_needs,
            tools.make_draft_pick
        ], cerebras_client=cerebras_client)

        self.test_player = "Kyler Murray"
        self.team_db_path = os.path.join(TEST_TEAM_DATABASE_DIR, TEST_TEAM, "team_data.db")
        logging.info("TestAgent instance setup completed")
    
    @patch('agent.Agent.generate_thought')
    def test_react_loop_get_player_stats(self, mock_generate_thought):
        logging.info(f"Testing react_loop_get_player_stats for player: {self.test_player}")
        mock_generate_thought.return_value = f"I should use get_player_stats to get the stats for {self.test_player}."
        prompt = f"What are the stats for {self.test_player}?"
        response = self.agent._react_loop(prompt, db_path=TEST_DATABASE_PATH, team_db_path=self.team_db_path)
        self.assertIn("Player:", response)  # Check if player name is in the response
        logging.info("test_react_loop_get_player_stats passed")

    @patch('agent.Agent.generate_thought')
    def test_react_loop_get_draft_order(self, mock_generate_thought):
        logging.info("Testing react_loop_get_draft_order")
        mock_generate_thought.return_value = "I should use get_draft_order to get the current draft order."
        prompt = "What is the current draft order?"
        response = self.agent._react_loop(prompt, db_path=TEST_DATABASE_PATH)
        self.assertIn("Current draft order", response)
        logging.info("test_react_loop_get_draft_order passed")

    @patch('agent.Agent.generate_thought')
    def test_react_loop_get_remaining_needs(self, mock_generate_thought):
        logging.info(f"Testing react_loop_get_remaining_needs for team: {TEST_TEAM}")
        mock_generate_thought.return_value = f"I should use get_remaining_needs to get the remaining needs for {TEST_TEAM}."
        prompt = f"What are the remaining needs for {TEST_TEAM}?"
        response = self.agent._react_loop(prompt, db_path=TEST_DATABASE_PATH, team_db_path=self.team_db_path)
        self.assertIn("placeholder", response)
        logging.info("test_react_loop_get_remaining_needs passed")
    
    @patch('agent.Agent.generate_thought')
    def test_react_loop_get_team_roster(self, mock_generate_thought):
        logging.info(f"Testing react_loop_get_team_roster with team: {TEST_TEAM}")
        mock_generate_thought.return_value = f"I should use get_team_roster to get the roster for {TEST_TEAM}."
        prompt = f"What is the roster for {TEST_TEAM}?"
        response = self.agent._react_loop(prompt, db_path=TEST_DATABASE_PATH, team_db_path=self.team_db_path)
        self.assertIn(TEST_TEAM, response)
        logging.info("test_react_loop_get_team_roster passed")
    

    @patch('agent.Agent.generate_thought')
    def test_react_loop_make_draft_pick(self, mock_generate_thought):
        logging.info(f"Testing react_loop_make_draft_pick for team: {TEST_TEAM} and player: {self.test_player}")
        mock_generate_thought.return_value = f"I should use make_draft_pick to draft {self.test_player}."
        prompt = f"Draft {self.test_player} for {TEST_TEAM}."
        response = self.agent._react_loop(prompt, db_path=TEST_DATABASE_PATH, team_db_path=self.team_db_path)
        self.assertIn(self.test_player, response)
        logging.info("test_react_loop_make_draft_pick passed")
if __name__ == "__main__":
    logging.info("Starting unittest")
    unittest.main()
    logging.info("Unittest completed")