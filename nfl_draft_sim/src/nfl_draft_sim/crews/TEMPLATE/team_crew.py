import logging
from typing import List
from crewai import Agent, Crew, Process, Task, LLM, CrewBase, agent, crew, task
from src.nfl_draft_sim.tools.csv_tools import CsvSearchTool
from src.nfl_draft_sim.crews.orchestrator.tools.orchestrator_tools import DatabaseQueryTool
from src.nfl_draft_sim.crews.TEMPLATE.tools.team_tools import TeamDatabaseTool, TeamDataSaveTool
from src.nfl_draft_sim.config.prompts import agent_evaluator, agent_negotiator, agent_picker, task_eval, task_trade, task_pick
from src.nfl_draft_sim.utils.helpers import ensure_dir
import os
import agentops
from src.nfl_draft_sim.utils.helpers import set_api_key

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)

@CrewBase
class NflTeamCrew:
    """Team Crew responsible for evaluating players, making trades, and selecting picks for the NFL draft."""

    agents_config = 'src/nfl_draft_sim/config/prompts.yaml'
    tasks_config = 'src/nfl_draft_sim/config/prompts.yaml'

    def __init__(self, team_name: str, orchestrator):
        set_api_key("AGENTOPS_API_KEY", "AGENTOPS_API_KEY")
        set_api_key("OPENAI_API_KEY", "OPENAI_API_KEY")
        agentops.init(os.getenv("AGENTOPS_API_KEY"))
        openai_model_name = os.getenv("OPENAI_MODEL_NAME")
        if not openai_model_name:
            raise ValueError("Environment variable OPENAI_MODEL_NAME must be set")
        self.team_name = team_name
        self.orchestrator = orchestrator
        self.llm = LLM(model=openai_model_name, temperature=0.7)
        self.database = orchestrator.database
        self.csv_search_tool = CsvSearchTool()
        self.team_database_tool = TeamDatabaseTool(self.database, team_name)
        self.team_data_save_tool = TeamDataSaveTool(team_name)

    @agent
    def player_evaluator(self) -> Agent:
      prompt = self.agents_config["agent_evaluator"]
      return Agent(
            role=prompt["role_desc"].format(team_name = self.team_name),
            goal=prompt["goal_desc"].format(team_name = self.team_name),
            backstory=prompt["backstory_desc"].format(team_name = self.team_name),
            memory=True,
            tools=[self.csv_search_tool, self.team_database_tool, self.team_data_save_tool],
            llm=self.llm,
            verbose=True
      )

    @agent
    def trade_negotiator(self) -> Agent:
      prompt = self.agents_config["agent_negotiator"]
      return Agent(
            role=prompt["role_desc"].format(team_name = self.team_name),
            goal=prompt["goal_desc"].format(team_name = self.team_name),
            backstory=prompt["backstory_desc"].format(team_name = self.team_name),
            memory=True,
            tools=[self.team_database_tool, self.team_data_save_tool],
            llm=self.llm,
            verbose=True
      )

    @agent
    def draft_picker(self) -> Agent:
      prompt = self.agents_config["agent_picker"]
      return Agent(
            role=prompt["role_desc"].format(team_name = self.team_name),
            goal=prompt["goal_desc"].format(team_name = self.team_name),
            backstory=prompt["backstory_desc"].format(team_name = self.team_name),
            memory=True,
            tools=[self.team_database_tool, self.team_data_save_tool],
            llm=self.llm,
            verbose=True
      )
    @task
    def evaluate_players_task(self) -> Task:
      prompt = self.tasks_config["task_eval"]
      logging.debug(f"Starting evaluate_players_task for team {self.team_name}")
      return Task(
            description=prompt["desc"].format(team_name=self.team_name),
            expected_output=prompt["exp_output"],
            agent=self.player_evaluator(),
            llm=self.llm
      )

    @task
    def negotiate_trades_task(self) -> Task:
      prompt = self.tasks_config["task_trade"]
      logging.debug(f"Starting negotiate_trades_task for team {self.team_name}")
      return Task(
            description=prompt["desc"].format(team_name=self.team_name),
            expected_output=prompt["exp_output"],
            agent=self.trade_negotiator(),
            llm=self.llm
      )

    @task
    def select_pick_task(self) -> Task:
      prompt = self.tasks_config["task_pick"]
      logging.debug(f"Starting select_pick_task for team {self.team_name}")
      return Task(
            description=prompt["desc"].format(team_name=self.team_name),
            expected_output=prompt["exp_output"],
            agent=self.draft_picker(),
            llm=self.llm
      )

    @crew
    def team_crew(self) -> Crew:
        return Crew(
            tasks=[
                self.evaluate_players_task(),
                self.negotiate_trades_task(),
                self.select_pick_task()
            ],
            agents=[
                self.player_evaluator(),
                self.trade_negotiator(),
                self.draft_picker()
            ],
            process=Process.sequential,
            verbose=True,
            planning=True,
            planning_llm=self.llm,
            max_rpm=10,
            memory=True,
             embedder=dict(provider="huggingface", config=dict(model="sentence-transformers/all-MiniLM-L6-v2"))
        )
