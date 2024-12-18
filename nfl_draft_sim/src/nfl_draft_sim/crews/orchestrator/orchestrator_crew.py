import logging
from typing import Any, List, Dict
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff
from crewai_tools import WebsiteSearchTool, SerperDevTool, ScrapeWebsiteTool, FileReadTool, FileWriterTool
from src.nfl_draft_sim.tools.nfl_data_tools import NflDataTool
from src.nfl_draft_sim.tools.csv_tools import CsvSearchTool
from src.nfl_draft_sim.crews.orchestrator.tools.orchestrator_tools import DatabaseQueryTool, SaveDataTool, PullAndSaveDataTool
from dotenv import load_dotenv
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from llama_index.core import VectorStoreIndex
import os
import agentops
from src.nfl_draft_sim.utils.helpers import set_api_key
from src.nfl_draft_sim.config.prompts import agent_manager, task_manager
import nfl_data_py as nfl
import pandas as pd

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Universal database to track rosters, draft picks, and other relevant information
class NflDraftDatabase:
    def __init__(self, teams: List[str]):
        self.teams = teams
        self.rosters = {team: [] for team in teams}
        self.draft_picks = {team: [] for team in teams}
        self.trades = []

    def add_pick(self, team: str, pick: Dict[str, Any]):
        self.draft_picks[team].append(pick)

    def add_trade(self, trade: Dict[str, Any]):
        self.trades.append(trade)

    def get_team_roster(self, team: str) -> List[Dict[str, Any]]:
        return self.rosters[team]

    def get_team_picks(self, team: str) -> List[Dict[str, Any]]:
        return self.draft_picks[team]

    def get_all_picks(self) -> Dict[str, List[Dict[str, Any]]]:
        return self.draft_picks

    def get_all_trades(self) -> List[Dict[str, Any]]:
        return self.trades

@CrewBase
class NflDraftOrchestrator:
    """Orchestrator Crew responsible for managing the NFL draft process, including tracking trades and picks made by each team."""
    agents_config = 'src/nfl_draft_sim/config/prompts.yaml'
    tasks_config = 'src/nfl_draft_sim/config/prompts.yaml'

    def __init__(self, teams: List[str]):
        # Initialize APIs and validate configuration
        set_api_key("AGENTOPS_API_KEY", "AGENTOPS_API_KEY")
        set_api_key("OPENAI_API_KEY", "OPENAI_API_KEY")
        agentops.init(os.getenv("AGENTOPS_API_KEY"))
        openai_model_name = os.getenv("OPENAI_MODEL_NAME")

        if not openai_model_name:
            raise ValueError("Environment variable OPENAI_MODEL_NAME must be set")

        self.llm = LLM(model=openai_model_name, temperature=0.7)
        self.teams = teams
        self.draft_order = list(teams)  # Initial draft order
        self.database = NflDraftDatabase(teams)
        self.nfl_data_tool = NflDataTool()
        self.csv_search_tool = CsvSearchTool()
        self.database_query_tool = DatabaseQueryTool(self.database)
        self.save_data_tool = SaveDataTool()
        self.pull_and_save_data_tool = PullAndSaveDataTool(self.nfl_data_tool, "orchestrator")

    @before_kickoff
    def before_kickoff_function(self, inputs):
        logging.debug("Before kickoff: Pulling and saving data for the current year")
        self.pull_and_save_data_tool.run(year=2023, data_type='rosters')
        self.pull_and_save_data_tool.run(year=2023, data_type='stats')
        self.pull_and_save_data_tool.run(year=2023, data_type='draft')
        return inputs

    @after_kickoff
    def after_kickoff_function(self, result):
        logging.debug("After kickoff: Logging final draft results")
        logging.info("Draft process completed:")
        logging.info(self.database.get_all_picks())
        logging.info("Trades made during the draft:")
        logging.info(self.database.get_all_trades())
        return result

    @agent
    def draft_manager(self) -> Agent:
          prompt = self.agents_config["agent_manager"]
          return Agent(
                role=prompt["role_desc"],
                goal=prompt["goal_desc"],
                backstory=prompt["backstory_desc"],
                memory=True,
                tools=[self.csv_search_tool, self.database_query_tool, self.save_data_tool],
                llm=self.llm,
                verbose=True
          )

    @task
    def manage_draft_task(self) -> Task:
        prompt = self.tasks_config["task_manager"]
        logging.debug("Starting manage_draft_task")
        return Task(
            description=prompt["desc"],
            expected_output=prompt["exp_output"],
            agent=self.draft_manager(),
            llm=self.llm,
            context=[self.draft_manager]
        )

    @crew
    def orchestrator_crew(self) -> Crew:
        return Crew(
            tasks=[self.manage_draft_task()],
            agents=[self.draft_manager()],
            process=Process.sequential,
            verbose=True,
            planning=True,
            planning_llm=self.llm,
            max_rpm=10,
            memory=True,
            embedder=dict(provider="huggingface", config=dict(model="sentence-transformers/all-MiniLM-L6-v2"))
        )
