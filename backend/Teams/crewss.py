import os
import csv
import sqlite3
from pathlib import Path
from typing import Dict, List, Any
from crewai import Agent, Crew, Process, Task, LLM
from crewai.knowledge.source.base_knowledge_source import BaseKnowledgeSource
from crewai_tools import CodeInterpreterTool, FileWriterTool, BaseTool, tool
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import pandas as pd
from textwrap import dedent
from langchain_groq import ChatGroq
from langchain_community.tools.sql_database.tool import (
    InfoSQLDatabaseTool,
    ListSQLDatabaseTool,
    QuerySQLCheckerTool,
    QuerySQLDataBaseTool,
)
from langchain_community.utilities.sql_database import SQLDatabase
load_dotenv()

class CSVKnowledgeSource(BaseKnowledgeSource):
    """A knowledge source that stores and queries CSV file content using embeddings."""
    file_paths: List[Path] = Field(description="List of csv files to load.")

    def load_content(self) -> Dict[Path, str]:
        """Load and preprocess CSV file content."""
        content_dict = {}
        for file_path in self.file_paths:
            with open(file_path, "r", encoding="utf-8") as csvfile:
                reader = csv.reader(csvfile)
                content = ""
                for row in reader:
                    content += " ".join(row) + "\n"
                content_dict[file_path] = content
        return content_dict

    def add(self) -> None:
        """
        Add CSV file content to the knowledge source, chunk it, compute embeddings,
        and save the embeddings.
        """
        content = self.load_content()
        for _, text in content.items():
            chunks = self._chunk_text(text)
            self.chunks.extend(chunks)
            
        self._save_documents()

    def _chunk_text(self, text: str) -> List[str]:
        """Utility method to split text into chunks."""
        return [
            text[i : i + self.chunk_size]
            for i in range(0, len(text), self.chunk_size - self.chunk_overlap)
        ]

def create_sql_tools(db_path: Path):
    """Creates the SQL tools with a given db path."""
    db = SQLDatabase.from_uri(f"sqlite:///{db_path}")

    @tool("list_tables")
    def list_tables() -> str:
        """List the available tables in the database"""
        return ListSQLDatabaseTool(db=db).invoke("")

    @tool("tables_schema")
    def tables_schema(tables: str) -> str:
        """
        Input is a comma-separated list of tables, output is the schema and sample rows
        for those tables. Be sure that the tables actually exist by calling `list_tables` first!
        Example Input: table1, table2, table3
        """
        tool = InfoSQLDatabaseTool(db=db)
        return tool.invoke(tables)

    @tool("execute_sql")
    def execute_sql(sql_query: str) -> str:
        """Execute a SQL query against the database. Returns the result"""
        return QuerySQLDataBaseTool(db=db).invoke(sql_query)

    @tool("check_sql")
    def check_sql(sql_query: str) -> str:
        """
        Use this tool to double check if your query is correct before executing it. Always use this
        tool before executing a query with `execute_sql`.
        """
        llm = ChatGroq(
            model="llama-3.3-70b-specdec"
        )
        return QuerySQLCheckerTool(db=db, llm=llm).invoke({"query": sql_query})
    
    return list_tables, tables_schema, execute_sql, check_sql

class PFFAnalyzer:
    def __init__(self, year=2023):
        self.year = year
        self.team_list = [
            "arizona-cardinals",
            "atlanta-falcons",
            "baltimore-ravens",
            "buffalo-bills",
            "carolina-panthers",
            "chicago-bears",
            "cincinnati-bengals",
            "cleveland-browns",
            "dallas-cowboys",
            "denver-broncos",
            "detroit-lions",
            "green-bay-packers",
            "houston-texans",
            "indianapolis-colts",
            "jacksonville-jaguars",
            "kansas-city-chiefs",
            "las-vegas-raiders",
            "los-angeles-rams",
            "los-angeles-chargers",
            "miami-dolphins",
            "minnesota-vikings",
            "new-england-patriots",
            "new-orleans-saints",
            "new-york-giants",
            "new-york-jets",
            "philadelphia-eagles",
            "pittsburgh-steelers",
            "san-francisco-49ers",
            "seattle-seahawks",
            "tampa-bay-buccaneers",
            "tennessee-titans",
            "washington-commanders"
        ]
        self.llm = LLM(api_key=os.getenv("OPENAI_API_KEY"), model=os.getenv("OPENAI_MODEL_NAME"))
        self.embedder = dict(provider="huggingface", config=dict(model="sentence-transformers/all-MiniLM-L6-v1.5"))

    def create_team_crew(self, team_name):
        db_file_path = Path(f"{team_name}/{team_name}.db")
        list_tables, tables_schema, execute_sql, check_sql = create_sql_tools(db_file_path)
        
        data_analyst = Agent(
            role="Data Analyst",
            goal=f"Analyze the {team_name}'s football data and generate actionable insights. Your analysis should be clear, concise, and focus on providing data-driven recommendations. Focus on providing context along with your analysis.",
            backstory=dedent("""You are a highly skilled data analyst with expertise in sports analytics, specifically football. You are adept at extracting key trends from complex datasets and providing clear and actionable recommendations. You are also skilled at using code to further your analysis."""),
            allow_code_execution=True,
            llm=self.llm,
            tools=[CodeInterpreterTool(), list_tables, tables_schema, execute_sql, check_sql],
            memory=True,
            embedder=self.embedder,
            context={"db_file_path": db_file_path}
        )

        report_writer = Agent(
            role="Report Writer",
            goal=f"Create clear and concise reports summarizing the insights and findings for {team_name}. The report should include actionable summaries and use markdown for structuring the output.",
            backstory=dedent("""You are a skilled content writer with a talent for transforming complex data into clear, concise, and easily understandable narrative reports. You are an expert at using markdown to structure information."""),
            llm=self.llm,
            tools=[FileWriterTool()],
            memory=True,
            context={"db_file_path": db_file_path}
        )
        
        scout_analyst = Agent(
            role="Scouting Expert",
            goal=f"Based on the performance of the {team_name}, determine what are the positions that need more work. Your report should highlight areas needing improvement and suggest draft targets, all based on the data provided.",
            backstory=dedent("""You are an expert in the sport of football, specializing in identifying positions that need improvement based on the data given. Your expertise is in translating data insights into actionable player recommendations."""),
            llm=self.llm,
            memory=True,
            context={"db_file_path": db_file_path}
        )

        sql_agent = Agent(
            role="SQL Developer",
            goal=f"You are a SQL developer, your task is to write SQL queries to get the data requested by the Data Analyst. You should not give any conclusions about the results. Make sure to double check your queries with `check_sql` before running them.",
            backstory=dedent("""You are an expert in writing efficient and complex SQL queries. Your background is in database administration and data retrieval. You have strong attention to detail and always check the syntax of your queries."""),
            llm=self.llm,
            tools=[list_tables, tables_schema, check_sql, execute_sql],
            memory=True,
            allow_delegation=False,
            context={"db_file_path": db_file_path}
        )

        expected_files = [
            f"{team_name}_schedule_{self.year}.csv",
            f"{team_name}_offense_{self.year}.csv",
            f"{team_name}_passing_{self.year}.csv",
            f"{team_name}_receiving_{self.year}.csv",
            f"{team_name}_rushing_{self.year}.csv",
            f"{team_name}_offense-blocking_{self.year}.csv",
            f"{team_name}_offense-pass-blocking_{self.year}.csv",
            f"{team_name}_offense-run-blocking_{self.year}.csv",
            f"{team_name}_defense_{self.year}.csv",
            f"{team_name}_defense-run_{self.year}.csv",
            f"{team_name}_defense-pass-rush_{self.year}.csv",
            f"{team_name}_defense-coverage_{self.year}.csv",
            f"{team_name}_special-teams_{self.year}.csv",
            f"{team_name}_kick-returning_{self.year}.csv",
            f"{team_name}_kicking_{self.year}.csv",
            f"{team_name}_punting_{self.year}.csv",
            f"{team_name}_kickoffs_{self.year}.csv",
        ]

        extract_data_task = Task(
            description=dedent(f"""Use the `SQLite Query Tool` to query the database at '{db_file_path}' and to answer the following questions. 
              The tables are named after the csv file names and the columns are the headers of those tables, with spaces replaced by underscores. 
              Prioritize the overall grades for defense, offense, and special teams (`DEF`, `OFF`, `SPEC`). 
              Analyze individual player data, filtering out players with a low count in the `#G` or `G` column if those columns are not present in the table. 
              Also, for each file, find the top 5 players in their overall grade.
              Make sure to filter the SQL queries so that only useful information is returned and not all of the table data. Provide the SQL query to the data analyst."""),
            expected_output=f"SQL query that will return the required data from the '{db_file_path}' database to answer the questions. Include the SQL query in your response.",
            agent=sql_agent
        )

        query_draft_prospects_task = Task(
            description=dedent(f"""Use the `SQLite Query Tool` to query the `nfl_draft_2024` table in the database at '{db_file_path}' to find the top draft prospects for the {team_name}. 
              The table contains columns such as `rank`, `position`, `name`, and `average_grade`. 
              Identify the top 5 prospects for each position that the team needs to improve based on the analysis of the team's performance.
              Make sure to filter the SQL queries so that only useful information is returned and not all of the table data. Provide the SQL query to the data analyst."""),
            expected_output=f"SQL query that will return the top draft prospects for the {team_name} from the 'nfl_draft_2024' table. Include the SQL query in your response.",
            agent=sql_agent
        )

        query_team_performance_task = Task(
            description=dedent(f"""Use the `SQLite Query Tool` to query the `nfl_teams_2023` table in the database at '{db_file_path}' to get the overall performance of the {team_name} for the year {self.year}. 
              The table contains columns such as `team`, `offense_grade`, `defense_grade`, and `special_teams_grade`. 
              Make sure to filter the SQL queries so that only the relevant information for the {team_name} is returned. Provide the SQL query to the data analyst."""),
            expected_output=f"SQL query that will return the overall performance of the {team_name} for the year {self.year} from the 'nfl_teams_2023' table. Include the SQL query in your response.",
            agent=sql_agent
        )

        analyze_data_task = Task(
            description=dedent(f"""Use the SQL queries provided by the SQL developer to get the data needed to analyze the {team_name}'s performance. The analysis should prioritize overall team grades, but provide insights into individual players. 
            Use Python code if needed to create plots and analyze the information.
            Provide textual analysis that can easily be used by the report writer."""),
            expected_output=f"Insights and actionable data from the {team_name} data, including plots if applicable. The analysis should prioritize overall team grades, but provide insights into individual players. The analysis should be in a textual format to pass it to the report writer.",
            agent=data_analyst,
            context=[extract_data_task, query_draft_prospects_task, query_team_performance_task]
        )
        
        scouting_report_task = Task(
            description=dedent(f"""Based on the analysis, create a scouting report stating the team's overall performance, what positions they need to draft next season to improve their performance, and any other valuable insights for the team. 
            The CSV files are {', '.join(expected_files)}."""),
            expected_output="A list of positions that the team needs to look at for the next draft, along with any other valuable information.",
            agent=scout_analyst,
            context=[analyze_data_task]
        )

        generate_report_task = Task(
            description=dedent(f"""Review the insights from the analysis and the scouting report, and create a detailed report on {team_name}'s statistics and performance.
            The report should include actionable data and visual information using markdown for easy reading. Make sure to include your findings and conclusions as well, along with the recommendations provided by the scouting report. 
            The report must be well-structured, with clear headings, bullet points, and paragraphs for easy reading."""),
            expected_output=f"A detailed report in markdown format with conclusions of the {team_name} performance. The report must include actionable information and also graphical if applicable.",
            agent=report_writer,
            context=[analyze_data_task, scouting_report_task]
        )

        return Crew(
            agents=[sql_agent, data_analyst, report_writer, scout_analyst],
            tasks=[extract_data_task, query_draft_prospects_task, query_team_performance_task, analyze_data_task, scouting_report_task, generate_report_task],
            process=Process.sequential,
            verbose=True,
            memory=True,
            embedder=self.embedder
        )
        
    def create_sqlite_db_and_load(self, team_name):
        db_path = Path(f"{team_name}/{team_name}.db")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        csv_files = [
            Path(f"{team_name}/{team_name}_schedule_{self.year}.csv"),
            Path(f"{team_name}/{team_name}_offense_{self.year}.csv"),
            Path(f"{team_name}/{team_name}_passing_{self.year}.csv"),
            Path(f"{team_name}/{team_name}_receiving_{self.year}.csv"),
            Path(f"{team_name}/{team_name}_rushing_{self.year}.csv"),
            Path(f"{team_name}/{team_name}_offense-blocking_{self.year}.csv"),
            Path(f"{team_name}/{team_name}_offense-pass-blocking_{self.year}.csv"),
            Path(f"{team_name}/{team_name}_offense-run-blocking_{self.year}.csv"),
            Path(f"{team_name}/{team_name}_defense_{self.year}.csv"),
            Path(f"{team_name}/{team_name}_defense-run_{self.year}.csv"),
            Path(f"{team_name}/{team_name}_defense-pass-rush_{self.year}.csv"),
            Path(f"{team_name}/{team_name}_defense-coverage_{self.year}.csv"),
            Path(f"{team_name}/{team_name}_special-teams_{self.year}.csv"),
            Path(f"{team_name}/{team_name}_kick-returning_{self.year}.csv"),
            Path(f"{team_name}/{team_name}_kicking_{self.year}.csv"),
            Path(f"{team_name}/{team_name}_punting_{self.year}.csv"),
            Path(f"{team_name}/{team_name}_kickoffs_{self.year}.csv"),
        ]

        for csv_file in csv_files:
            if csv_file.exists():
                df = pd.read_csv(csv_file)
                df.to_sql(csv_file.stem, conn, if_exists='replace', index=False)
            else:
                print(f"Could not find {csv_file}")

        # Load the nfl_draft_2024.csv into the database
        draft_file = Path("nfl_draft_2024.csv")
        if draft_file.exists():
            df = pd.read_csv(draft_file)
            df.columns = [col.replace("/", "_per_").replace("%", "_percentage").replace(".", "").replace("#", "hashtag").replace(" ", "_") for col in df.columns]
            df.to_sql("nfl_draft_2024", conn, if_exists="replace", index=False)
        else:
            print(f"Could not find {draft_file}")

        # Load the nfl_teams_2023.csv into the database
        team_stats_file = Path(f"nfl_teams_{self.year}.csv")
        if team_stats_file.exists():
            df = pd.read_csv(team_stats_file)
            df.columns = [col.replace("/", "_per_").replace("%", "_percentage").replace(".", "").replace("#", "hashtag").replace(" ", "_") for col in df.columns]
            df.to_sql("nfl_teams_2023", conn, if_exists="replace", index=False)
        else:
            print(f"Could not find {team_stats_file}")

        conn.close()

    def run_all_teams(self):
        for team_name in self.team_list:
            print(f"Starting analysis for {team_name}...")
            self.create_sqlite_db_and_load(team_name)
            crew = self.create_team_crew(team_name)
            result = crew.kickoff()
            print(f"Analysis for {team_name} complete.")
            print("Final Result:", result)
            print("-------------------------")
    
    def run_team(self, team_name):
        print(f"Starting analysis for {team_name}...")
        self.create_sqlite_db_and_load(team_name)
        crew = self.create_team_crew(team_name)
        result = crew.kickoff()
        print(f"Analysis for {team_name} complete.")
        print("Final Result:", result)
        print("-------------------------")

    def train_crew(self, n_iterations, inputs, filename):
        try:
            crew = self.create_team_crew("arizona-cardinals")
            crew.train(n_iterations=n_iterations, inputs=inputs, filename=filename)
            print(f"Crew training complete. Model saved to {filename}.")
        except Exception as e:
            raise Exception(f"An error occurred while training the crew: {e}")

if __name__ == "__main__":
    analyzer = PFFAnalyzer()
    # analyzer.train_crew(n_iterations=2, inputs={"team": "Arizona Cardinals"}, filename="cardinals.pkl")
    analyzer.run_team("arizona-cardinals")