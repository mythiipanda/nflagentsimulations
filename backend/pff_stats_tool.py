from typing import Type, Optional
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import pandas as pd
from pathlib import Path

DATA_DIR = Path("./data/")

class DefenseToolInput(BaseModel):
    year: int = Field(..., description="Year to filter defense data by")
    player: Optional[str] = Field(None, description="Player name to filter by")

class DefenseTool(BaseTool):
    name: str = "Defense Data Tool"
    description: str = "Provides detailed Pro Football Focus (PFF) defensive statistics filtered by year and optionally by player name."
    args_schema: Type[BaseModel] = DefenseToolInput

    def _run(self, year: int, player: Optional[str] = None) -> str:
        df = pd.read_csv(DATA_DIR / "processed_defense_summary.csv")
        result = df[df.year == year]
        if player:
            result = result[result.player == player]
        
        if result.empty:
            return f"No defensive statistics found for year {year}" + (f" and player {player}" if player else "") + "."

        # Convert the entire DataFrame to string without truncation
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            return result.to_string(index=False)

class FieldGoalToolInput(BaseModel):
    year: int = Field(..., description="Year to filter field goal data by")
    player: Optional[str] = Field(None, description="Player name to filter by")

class FieldGoalTool(BaseTool):
    name: str = "Field Goal Data Tool" 
    description: str = "Retrieves PFF field goal statistics filtered by year and optionally by player name."
    args_schema: Type[BaseModel] = FieldGoalToolInput

    def _run(self, year: int, player: Optional[str] = None) -> str:
        df = pd.read_csv(DATA_DIR / "processed_field_goal_summary.csv")
        result = df[df.year == year]
        if player:
            result = result[result.player == player]
        
        if result.empty:
            return f"No field goal statistics found for year {year}" + (f" and player {player}" if player else "") + "."

        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            return result.to_string(index=False)

class OffenseBlockingToolInput(BaseModel):
    year: int = Field(..., description="Year to filter offense blocking data by")
    player: Optional[str] = Field(None, description="Player name to filter by")

class OffenseBlockingTool(BaseTool):
    name: str = "Offense Blocking Data Tool"
    description: str = "Provides PFF offensive blocking metrics filtered by year and optionally by player name."
    args_schema: Type[BaseModel] = OffenseBlockingToolInput

    def _run(self, year: int, player: Optional[str] = None) -> str:
        df = pd.read_csv(DATA_DIR / "processed_offense_blocking_summary.csv")
        result = df[df.year == year]
        if player:
            result = result[result.player == player]
        
        if result.empty:
            return f"No offensive blocking statistics found for year {year}" + (f" and player {player}" if player else "") + "."

        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            return result.to_string(index=False)

class PassingToolInput(BaseModel):
    year: int = Field(..., description="Year to filter passing data by")
    player: Optional[str] = Field(None, description="Player name to filter by")

class PassingTool(BaseTool):
    name: str = "Passing Data Tool"
    description: str = "Loads PFF passing statistics filtered by year and optionally by player name."
    args_schema: Type[BaseModel] = PassingToolInput

    def _run(self, year: int, player: Optional[str] = None) -> str:
        df = pd.read_csv(DATA_DIR / "processed_passing_summary.csv")
        result = df[df.year == year]
        if player:
            result = result[result.player == player]
        
        if result.empty:
            return f"No passing statistics found for year {year}" + (f" and player {player}" if player else "") + "."

        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            return result.to_string(index=False)

class PuntingToolInput(BaseModel):
    year: int = Field(..., description="Year to filter punting data by")
    player: Optional[str] = Field(None, description="Player name to filter by")

class PuntingTool(BaseTool):
    name: str = "Punting Data Tool"
    description: str = "Retrieves PFF punting statistics filtered by year and optionally by player name."
    args_schema: Type[BaseModel] = PuntingToolInput

    def _run(self, year: int, player: Optional[str] = None) -> str:
        df = pd.read_csv(DATA_DIR / "processed_punting_summary.csv")
        result = df[df.year == year]
        if player:
            result = result[result.player == player]
        
        if result.empty:
            return f"No punting statistics found for year {year}" + (f" and player {player}" if player else "") + "."

        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            return result.to_string(index=False)

class ReceivingToolInput(BaseModel):
    year: int = Field(..., description="Year to filter receiving data by")
    player: Optional[str] = Field(None, description="Player name to filter by")

class ReceivingTool(BaseTool):
    name: str = "Receiving Data Tool"
    description: str = "Provides PFF receiving statistics filtered by year and optionally by player name."
    args_schema: Type[BaseModel] = ReceivingToolInput

    def _run(self, year: int, player: Optional[str] = None) -> str:
        df = pd.read_csv(DATA_DIR / "processed_receiving_summary.csv")
        result = df[df.year == year]
        if player:
            result = result[result.player == player]
        
        if result.empty:
            return f"No receiving statistics found for year {year}" + (f" and player {player}" if player else "") + "."

        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            return result.to_string(index=False)

class RushingToolInput(BaseModel):
    year: int = Field(..., description="Year to filter rushing data by")
    player: Optional[str] = Field(None, description="Player name to filter by")

class RushingTool(BaseTool):
    name: str = "Rushing Data Tool"
    description: str = "Retrieves PFF rushing statistics filtered by year and optionally by player name."
    args_schema: Type[BaseModel] = RushingToolInput

    def _run(self, year: int, player: Optional[str] = None) -> str:
        df = pd.read_csv(DATA_DIR / "processed_rushing_summary.csv")
        result = df[df.year == year]
        if player:
            result = result[result.player == player]
        
        if result.empty:
            return f"No rushing statistics found for year {year}" + (f" and player {player}" if player else "") + "."

        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            return result.to_string(index=False)