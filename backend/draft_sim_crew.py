import logging
from typing import Any, List, Dict
from crewai import Agent, Crew, Process, Task, LLM
from crewai.flow.flow import Flow, listen, start
from crewai.tools import BaseTool
from crewai.project import CrewBase, agent, task, crew, before_kickoff, after_kickoff
from dotenv import load_dotenv
import os
import agentops
import nfl_data_py as nfl
import pandas as pd
from pydantic import BaseModel, Field
from typing import Type

# Load environment variables
load_dotenv()
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        logging.info(f"Created directory: {directory}")

def save_data(data: pd.DataFrame, filename: str):
    data.to_csv(filename, index=False)

def set_api_key(api_key_name, env_variable):
    api_key = os.getenv(env_variable)
    if not api_key:
        raise ValueError(f"Environment variable {env_variable} must be set.")
    os.environ[api_key_name] = api_key

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

# Custom tool to pull data from nfl_data_py
class NflDataToolInput(BaseModel):
    year: int = Field(..., description="The year for which data is to be pulled.")
    data_type: str = Field(..., description="The type of data to pull (rosters, stats).")

class NflDataTool(BaseTool):
    name: str = "Nfl Data Tool"
    description = "Used to pull data from nfl_data_py. Valid data_types include: 'rosters', 'stats'."
    args_schema: Type[BaseModel] = NflDataToolInput

    def _run(self, year: int, data_type: str) -> pd.DataFrame:
        try:
            if data_type == 'rosters':
                return nfl.import_rosters([year])
            elif data_type == 'stats':
                return nfl.import_weekly_data([year])
            else:
                raise ValueError("Invalid data type. Choose from 'rosters' or 'stats'.")
        except Exception as e:
            return f"Error performing search: {str(e)}"

class CsvSearchToolInput(BaseModel):
    query: str = Field(..., description="The search query.")
    position: str = Field(None, description="The player position filter")
    csv_file: str = Field("./nfl_draft_2024.csv", description="The path to the csv file")

class CsvSearchTool(BaseTool):
    name = "NFL Prospect Search Tool"
    description = "Used to search and filter player information from nfl_draft_2024.csv."
    args_schema: Type[BaseModel] = CsvSearchToolInput

    def _run(self, query: str, position: str = None, csv_file: str = "./nfl_draft_2024.csv") -> str:
        try:
            df = pd.read_csv(csv_file)

            # Filtering by position if provided
            if position:
                df = df[df['position'].str.contains(position, na=False, case=False)]

            # Simple search logic by checking if any column contains the query string
            search_results = df[df.apply(lambda row: row.astype(str).str.contains(query, na=False, case=False).any(), axis=1)]
            if not search_results.empty:
                return search_results.to_string()
            else:
                return "No relevant prospects found based on the criteria"
        except Exception as e:
            return f"Error performing search: {str(e)}"

class DatabaseQueryToolInput(BaseModel):
    database_query: str = Field(..., description="The query you need to execute against the database.")
    database: Any = Field(..., description="The database object to query against.")

class DatabaseQueryTool(BaseTool):
    name = "NFL Database Query Tool"
    description = "Used to query the NFL draft database including picks, trades, rosters, etc."
    args_schema: Type[BaseModel] = DatabaseQueryToolInput

    def _run(self, database_query: str, database: Any) -> str:
        if database_query == "get_all_picks":
            return database.get_all_picks()
        elif database_query == "get_all_trades":
            return database.get_all_trades()
        else:
            return f"Unknown query {database_query}"

class SaveDataToolInput(BaseModel):
    data_str: str = Field(..., description="The data in string format to be saved.")
    filename: str = Field(..., description="Filename to use for the saved data, which will be inside crews/orchestrator")

class SaveDataTool(BaseTool):
    name = "Save Data Tool"
    description = "Saves the given data to a file in the teams folders"
    args_schema: Type[BaseModel] = SaveDataToolInput

    def _run(self, data_str: str, filename: str) -> str:
        try:
            ensure_dir("src/crews/orchestrator")
            file_path = f"src/crews/orchestrator/{filename}"
            with open(file_path, 'w') as f:
                f.write(data_str)
            return f"Data written to {filename}"
        except Exception as e:
            return f"Could not write to file: {e}"

class PullAndSaveDataToolInput(BaseModel):
    year: int = Field(..., description="The year to pull data.")
    data_type: str = Field(..., description="The type of data to pull from the NFL_Data_Tool. The types available are `rosters`, `stats` or `draft`.")

class PullAndSaveDataTool(BaseTool):
    name = "Pull and Save NFL Data Tool"
    description = "Pulls and saves NFL data using the NflDataTool in a specific format for a specific year. Types: `rosters`, `stats`, or `draft`."
    args_schema: Type[BaseModel] = PullAndSaveDataToolInput

    def __init__(self, nfl_data_tool, orchestrator_crew_name):
        super().__init__()
        self.nfl_data_tool = nfl_data_tool
        self.orchestrator_crew_name = orchestrator_crew_name

    def _run(self, year: int, data_type: str) -> str:
        try:
            data = self.nfl_data_tool.run(year=year, data_type=data_type)
            filename = f"src/crews/{self.orchestrator_crew_name}/{data_type}_{year}.csv"
            ensure_dir(f"src/crews/{self.orchestrator_crew_name}")
            data.to_csv(filename, index=False)
            return f"Data saved to file {filename}"
        except Exception as e:
            return f"Could not pull data: {e}"

class TeamDataToolInput(BaseModel):
    data_query: str = Field(..., description="The query you want to perform against the team database.")

class TeamDatabaseTool(BaseTool):
    name = "Team Database Query Tool"
    description = "Used to query the NFL draft database including rosters, picks and trades from the team's point of view."
    args_schema: Type[BaseModel] = TeamDataToolInput

    def __init__(self, database, team_name):
        super().__init__()
        self.database = database
        self.team_name = team_name

    def _run(self, data_query: str) -> str:
        if data_query == "get_team_roster":
            return self.database.get_team_roster(self.team_name)
        elif data_query == "get_team_picks":
            return self.database.get_team_picks(self.team_name)
        else:
            return f"Unknown query {data_query}"

class TeamDataSaveToolInput(BaseModel):
    data_str: str = Field(..., description="The data to be saved.")
    filename: str = Field(..., description="The filename for the data.")

class TeamDataSaveTool(BaseTool):
    name = "Team Data Save Tool"
    description = "Saves data to a team specific file"
    args_schema: Type[BaseModel] = TeamDataSaveToolInput

    def __init__(self, team_name):
        super().__init__()
        self.team_name = team_name

    def _run(self, data_str: str, filename: str) -> str:
        try:
            ensure_dir(f"src/crews/{self.team_name}")
            file_path = f"src/crews/{self.team_name}/{filename}"
            with open(file_path, 'w') as f:
                f.write(data_str)
            return f"Data written to {filename}"
        except Exception as e:
            return f"Could not write to file: {e}"

class TeamCommunicationFlow(Flow):
    """Handles communication between team crews and the orchestrator, including reporting results and
    coordinating any necessary actions related to the draft."""

    def __init__(self, team_name, orchestrator):
        self.team_name = team_name
        self.orchestrator = orchestrator

    @start()
    def announce_start(self):
        logging.info(f"Team {self.team_name} started their draft process.")
        return {"message": f"Team {self.team_name} is starting their draft process"}

    @listen(announce_start)
    def report_results(self, output):
        # Report back to the orchestrator, add information to the database
        logging.info(f"Team {self.team_name} is reporting back on their process")
        return {"message": f"Team {self.team_name} is reporting their process results"}

class TeamTradeFlow(Flow):
    """Manages the trade proposal from a specific team to another."""

    def __init__(self, from_team, to_team, orchestrator):
        self.from_team = from_team
        self.to_team = to_team
        self.orchestrator = orchestrator

    @start()
    def create_trade_proposal(self):
        logging.info(f"Team {self.from_team} is proposing a trade to team {self.to_team}.")
        return {"message": f"Team {self.from_team} is proposing a trade to team {self.to_team}."}

    @listen(create_trade_proposal)
    def receive_trade_proposal(self, output):
        # Action: check if trade proposal is valid, then trade.
        logging.info(f"Team {self.to_team} is analyzing the trade proposal from team {self.from_team}.")
        return {"message": f"Team {self.to_team} is analyzing the trade proposal from team {self.from_team}."}

class NflDraftFlow(Flow):
    def __init__(self, teams: List[str]):
        self.teams = teams
        self.orchestrator = NflDraftOrchestrator(teams)
        self.team_crews = {team: NflTeamCrew(team, self.orchestrator) for team in teams}
        self.team_communication_flows = {
            team: TeamCommunicationFlow(team, self.orchestrator) for team in teams
        }
        self.trade_flows = {}  # trade flows will be created as necessary

    @start()
    def initiate_draft(self):
        logging.info("Initiating NFL draft simulation...")
        # Initiate orchestrator to setup env and get data
        self.orchestrator.orchestrator_crew().kickoff(inputs={"message": "Starting the NFL Draft Process"})
        return {"message": "Draft Started"}

    @listen(initiate_draft)
    def process_draft_rounds(self, initiator_output):
        for pick_number in range(len(self.teams)):
            # Simulate the draft process for each pick
            logging.info(f"Processing round {pick_number + 1}")
            for team in self.teams:
                logging.info(f"Team {team} is making pick {pick_number + 1}")
                team_crew = self.team_crews[team]
                team_communication_flow = self.team_communication_flows[team]
                team_crew_results = team_communication_flow.kickoff()
                team_crew.team_crew().kickoff(inputs={"team_name": team, "pick_number": pick_number + 1})

                # Update the universal database with the pick
                pick = {"team": team, "pick_number": pick_number + 1, "player": team_crew.select_pick_task().output}
                self.orchestrator.database.add_pick(team, pick)

                # This should be called by agents instead, so teams can propose trades at any time
                # trade_flow = TeamTradeFlow(from_team=team, to_team=self.teams[pick_number % len(self.teams)], orchestrator=self.orchestrator)
                # trade_results = trade_flow.kickoff()
                # self.orchestrator.database.add_trade(trade_results)

        return {"message": "Draft Completed"}

class NflTeamCrew(CrewBase):
    """Team Crew responsible for evaluating players, making trades, and selecting picks for the NFL draft."""

    def __init__(self, team_name: str, orchestrator):
        set_api_key("AGENTOPS_API_KEY", "AGENTOPS_API_KEY")
        set_api_key("OPENAI_API_KEY", "OPENAI_API_KEY")
        agentops.init(os.getenv("AGENTOPS_API_KEY"))  # Initialize agentops
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

    
    def player_evaluator(self) -> Agent:
        return Agent(
            role=f"Player Evaluator for {self.team_name}",
            goal=f"Evaluate NFL prospects for {self.team_name}",
            backstory=f"Expert in evaluating NFL prospects for {self.team_name}",
            memory=True,
            tools=[self.csv_search_tool, self.team_database_tool, self.team_data_save_tool],
            llm=self.llm,
            verbose=True
        )

    
    def trade_negotiator(self) -> Agent:
        return Agent(
            role=f"Trade Negotiator for {self.team_name}",
            goal=f"Negotiate trades for {self.team_name}",
            backstory=f"Skilled in negotiating trades for {self.team_name}",
            memory=True,
            tools=[self.team_database_tool, self.team_data_save_tool],
            llm=self.llm,
            verbose=True
        )

    
    def draft_picker(self) -> Agent:
        return Agent(
            role=f"Draft Picker for {self.team_name}",
            goal=f"Select draft picks for {self.team_name}",
            backstory=f"Responsible for making draft picks for {self.team_name}",
            memory=True,
            tools=[self.team_database_tool, self.team_data_save_tool],
            llm=self.llm,
            verbose=True
        )

    
    def evaluate_players_task(self) -> Task:
        return Task(
            description=f"Evaluate NFL prospects for {self.team_name}",
            expected_output="List of evaluated prospects",
            agent=self.player_evaluator(),
            llm=self.llm
        )

    
    def negotiate_trades_task(self) -> Task:
        return Task(
            description=f"Negotiate trades for {self.team_name}",
            expected_output="List of proposed trades",
            agent=self.trade_negotiator(),
            llm=self.llm
        )

    
    def select_pick_task(self) -> Task:
        return Task(
            description=f"Select draft picks for {self.team_name}",
            expected_output="Selected draft picks",
            agent=self.draft_picker(),
            llm=self.llm
        )

    
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

class NflDraftOrchestrator(CrewBase):
    """Orchestrator Crew responsible for managing the NFL draft process, including tracking trades and picks made by each team."""

    def __init__(self, teams: List[str]):
        # Initialize APIs and validate configuration
        set_api_key("AGENTOPS_API_KEY", "AGENTOPS_API_KEY")
        set_api_key("OPENAI_API_KEY", "OPENAI_API_KEY")
        agentops.init(os.getenv("AGENTOPS_API_KEY"))  # Initialize agentops
        openai_model_name = os.getenv("OPENAI_MODEL_NAME")

        if not openai_model_name:
            raise ValueError("Environment variable OPENAI_MODEL_NAME must be set")

        self.llm = LLM(model=openai_model_name, temperature=0.7)
        self.teams = teams
        self.draft_order = list(teams)  # Initial draft order
        self.database = NflDraftDatabase(teams)
        self.nfl_data_tool = NflDataTool()
        self.csv_search_tool = CsvSearchTool()
        self.database_query_tool = DatabaseQueryTool()
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

    
    def draft_manager(self) -> Agent:
        return Agent(
            role="Draft Manager",
            goal="Manage the NFL draft process",
            backstory="Responsible for coordinating the draft process and ensuring all teams follow the rules",
            memory=True,
            tools=[self.csv_search_tool, self.database_query_tool, self.save_data_tool],
            llm=self.llm,
            verbose=True
        )

    
    def manage_draft_task(self) -> Task:
        return Task(
            description="Manage the NFL draft process",
            expected_output="Final draft results",
            agent=self.draft_manager(),
            llm=self.llm,
            context=[self.draft_manager]
        )

    
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

# Example usage
if __name__ == "__main__":
    teams = [
            "Arizona Cardinals", "Atlanta Falcons", "Baltimore Ravens", "Buffalo Bills", "Carolina Panthers",
            "Chicago Bears", "Cincinnati Bengals", "Cleveland Browns", "Dallas Cowboys", "Denver Broncos",
            "Detroit Lions", "Green Bay Packers", "Houston Texans", "Indianapolis Colts", "Jacksonville Jaguars",
            "Kansas City Chiefs", "Las Vegas Raiders", "Los Angeles Chargers", "Los Angeles Rams", "Miami Dolphins",
            "Minnesota Vikings", "New England Patriots", "New Orleans Saints", "New York Giants", "New York Jets",
            "Philadelphia Eagles", "Pittsburgh Steelers", "San Francisco 49ers", "Seattle Seahawks", "Tampa Bay Buccaneers",
            "Tennessee Titans", "Washington Commanders"
        ]
    draft_flow = NflDraftFlow(teams)
    draft_flow.initiate_draft()
