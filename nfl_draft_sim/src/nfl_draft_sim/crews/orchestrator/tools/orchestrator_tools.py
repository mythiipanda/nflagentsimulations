from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
from src.nfl_draft_sim.utils.helpers import save_data
import pandas as pd
from src.nfl_draft_sim.tools.nfl_data_tools import NflDataTool
from src.nfl_draft_sim.utils.helpers import ensure_dir
import os

class DatabaseQueryToolInput(BaseModel):
     database_query: str = Field(..., description="The query you need to execute against the database.")

class DatabaseQueryTool(BaseTool):
    name = "NFL Database Query Tool"
    description = "Used to query the NFL draft database including picks, trades, rosters, etc."
    args_schema: Type[BaseModel] = DatabaseQueryToolInput

    def __init__(self, database):
        super().__init__()
        self.database = database

    def _run(self, database_query: str) -> str:
        if database_query == "get_all_picks":
           return self.database.get_all_picks()
        elif database_query == "get_all_trades":
            return self.database.get_all_trades()
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
            ensure_dir("src/nfl_draft_sim/crews/orchestrator")
            file_path = f"src/nfl_draft_sim/crews/orchestrator/{filename}"
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
            data = self.nfl_data_tool.run(year, data_type)
            filename = f"src/nfl_draft_sim/crews/{self.orchestrator_crew_name}/{data_type}_{year}.csv"
            ensure_dir(f"src/nfl_draft_sim/crews/{self.orchestrator_crew_name}")
            data.to_csv(filename, index=False)
            return f"Data saved to file {filename}"
        except Exception as e:
             return f"Could not pull data: {e}"
