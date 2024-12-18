from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type

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
            ensure_dir(f"src/nfl_draft_sim/crews/{self.team_name}")
            file_path = f"src/nfl_draft_sim/crews/{self.team_name}/{filename}"
            with open(file_path, 'w') as f:
              f.write(data_str)
            return f"Data written to {filename}"
        except Exception as e:
            return f"Could not write to file: {e}"
