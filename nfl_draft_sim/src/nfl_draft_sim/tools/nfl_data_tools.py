import nfl_data_py as nfl
import pandas as pd
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type

class NflDataToolInput(BaseModel):
    year: int = Field(..., description="The year for which data is to be pulled.")
    data_type: str = Field(..., description="The type of data to pull (rosters, stats, draft).")
class NflDataTool(BaseTool):
    name = "Nfl Data Tool"
    description = "Used to pull data from nfl_data_py. Valid data_types include: 'rosters', 'stats', and 'draft'."
    args_schema: Type[BaseModel] = NflDataToolInput
    
    def _run(self, year: int, data_type: str) -> pd.DataFrame:
      try:
        if data_type == 'rosters':
              return nfl.import_rosters([year])
        elif data_type == 'stats':
            return nfl.import_weekly_data([year])
        elif data_type == 'draft':
            return nfl.import_draft_picks([year])
        else:
              raise ValueError("Invalid data type. Choose from 'rosters', 'stats', or 'draft'.")
      except Exception as e:
            return f"Error performing search: {str(e)}"
