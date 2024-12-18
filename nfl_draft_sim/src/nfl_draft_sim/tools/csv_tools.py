import pandas as pd
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type

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
