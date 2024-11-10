import os
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import WebsiteSearchTool, SerperDevTool, ScrapeWebsiteTool
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import agentops

# Load environment variables
load_dotenv()
agentops.init(os.getenv("AGENTOPS_API_KEY"))

@CrewBase
class NflCrew():
    """NFL Analysis Crew"""

    def __init__(self):
        openai_api_key = os.getenv("OPENAI_API_KEY")
        openai_model_name = os.getenv("OPENAI_MODEL_NAME")

        if not openai_api_key or not openai_model_name:
            raise ValueError("Environment variables OPENAI_API_KEY and OPENAI_MODEL_NAME must be set")

        self.llm = LLM(
    		api_key=os.getenv("GEMINI_API_KEY"),
            model=os.getenv("OPENAI_MODEL_NAME"),
            temperature=0.7
        )
        self.tools = [
            WebsiteSearchTool(
                config=dict(
                    llm=dict(
                        provider="openai",
                        config=dict(
                            api_key=openai_api_key,
                            model=openai_model_name,
                            temperature=0.5,
                            top_p=0.9,
                            stream=False
                        ),
                    ),
                    embedder=dict(
                        provider="huggingface",
                        config=dict(
                            model="sentence-transformers/all-MiniLM-L6-v2"
                        ),
                    ),
                )
            ),
            SerperDevTool(),
            ScrapeWebsiteTool()
        ]

    @agent
    def lead_analyst(self) -> Agent:
        return Agent(
            role="Lead NFL Analyst",
            goal="Coordinate research efforts and synthesize insights from multiple data sources to provide comprehensive NFL analysis.",
            backstory="A veteran NFL analyst with expertise in statistical analysis, game film analysis, and historical trends.",
            memory=True,
            tools=self.tools,
            llm=self.llm
        )

    @agent
    def stats_analyst(self) -> Agent:
        return Agent(
            role="Statistical Analyst",
            goal="Process and analyze NFL statistical data to identify trends, patterns, and significant insights.",
            backstory="A data scientist with expertise in advanced NFL metrics, including DVOA and EPA.",
            memory=True,
            tools=self.tools,
            llm=self.llm
        )

    @agent
    def team_scout(self) -> Agent:
        return Agent(
            role="Team Scout",
            goal="Evaluate team performances, analyze matchups, and provide detailed scouting reports.",
            backstory="An ex-NFL scout specializing in player evaluation, film study, and talent assessment.",
            memory=True,
            tools=self.tools,
            llm=self.llm
        )
    @agent
    def manager(self) -> Agent:
        return Agent(
			role="Project Manager",
			goal="Understand and process the client's request: '{query}' and efficiently manage the crew to ensure high-quality task completion. For context, we are right now in week 10 of the NFL. Make sure all information is up to date with the 2024-2025 season.",
			backstory="An experienced project manager skilled in overseeing complex projects and guiding teams to success.",
			allow_delegation=True,
			llm=self.llm
		)
    @agent
    def writer(self) -> Agent:
        return Agent(
            role="Content Writer",
            goal="Transform research findings and insights into engaging and informative reports for the client.",
            backstory="A skilled writer with experience in sports journalism and content creation.",
            llm=self.llm
        )

    @task
    def statistical_analysis_task(self) -> Task:
        return Task(
            description="Gather comprehensive NFL statistics related to the request: '{query}'.",
            expected_output="A detailed statistical analysis report with key insights and trends.",
            agent=self.stats_analyst(),
            llm=self.llm
        )

    @task
    def scouting_analysis_task(self) -> Task:
        return Task(
            description="Analyze team performances related to the request: '{query}', and produce in-depth scouting reports.",
            expected_output="Detailed team analysis and scouting insights, structured as comprehensive scouting reports.",
            agent=self.team_scout(),
            llm=self.llm
        )

    @task
    def synthesis_task(self) -> Task:
        return Task(
            description="Synthesize research, statistical data, and scouting reports into cohesive insights for meaningful NFL analysis on: '{query}'.",
            expected_output="A cohesive analysis report that integrates statistical and scouting perspectives.",
            context=[self.statistical_analysis_task(), self.scouting_analysis_task()],
            agent=self.writer(),
            llm=self.llm
        )

    @crew
    def crew(self) -> Crew:
        # Define the list of tasks if not set globally
        tasks = [self.statistical_analysis_task(), self.scouting_analysis_task(), self.synthesis_task()]
        return Crew(
            agents=[self.lead_analyst(), self.stats_analyst(), self.team_scout(), self.writer()],
            tasks=tasks,
            process=Process.hierarchical,
            manager_agent=self.manager(),
            verbose=True,
            planning=True,
            planning_llm=self.llm
        )
