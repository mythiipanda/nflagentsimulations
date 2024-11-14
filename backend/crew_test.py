import os
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import WebsiteSearchTool, SerperDevTool, ScrapeWebsiteTool, FileWriterTool, tool
from dotenv import load_dotenv
import agentops
from backend.pff_tool import PFFScraperTool
# Load environment variables
load_dotenv()

@CrewBase
class NflCrew():
    """NFL Analysis Crew"""

    def __init__(self):
        agentops.init(os.getenv("AGENTOPS_API_KEY"))
        openai_api_key = os.getenv("OPENAI_API_KEY")
        openai_model_name = os.getenv("OPENAI_MODEL_NAME")
        groq_api_key = os.getenv("GEMINI_API_KEY")

        if not openai_api_key or not openai_model_name:
            raise ValueError("Environment variables OPENAI_API_KEY and OPENAI_MODEL_NAME must be set")

        self.llm = LLM(
            api_key=openai_api_key,
            model=openai_model_name,
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
    def researcher(self) -> Agent:
        return Agent(
            role="NFL Research Specialist",
            goal="Gather and compile comprehensive NFL data from multiple sources, including news, statistics, and historical records.",
            backstory="A meticulous researcher with extensive experience in sports data collection and verification, specializing in NFL coverage and analytics.",
            memory=True,
            tools=[WebsiteSearchTool(), ScrapeWebsiteTool(), SerperDevTool()],
            llm=self.llm
        )

    @agent
    def stats_analyst(self) -> Agent:
        return Agent(
            role="Statistical Analyst",
            goal="Process raw data into meaningful statistical insights, focusing on both traditional and advanced metrics.",
            backstory="A data scientist specializing in sports analytics, with expertise in advanced NFL metrics like DVOA, EPA, and situational analysis.",
            memory=True,
            tools=[WebsiteSearchTool(), ScrapeWebsiteTool(), SerperDevTool()],
            llm=self.llm,
            allow_code_execution=True
        )

    @agent
    def game_analyst(self) -> Agent:
        return Agent(
            role="Game Analysis Specialist",
            goal="Analyze game situations, strategic decisions, and team tendencies to provide contextual insights.",
            backstory="A former NFL coach with deep understanding of game planning, situational football, and strategic analysis.",
            memory=True,
            tools=[WebsiteSearchTool(), ScrapeWebsiteTool(), SerperDevTool()],
            llm=self.llm
        )

    @agent
    def writer(self) -> Agent:
        return Agent(
            role="Content Writer",
            goal="Transform complex analysis into clear, engaging, and informative content.",
            backstory="An experienced sports journalist skilled in translating technical analysis into compelling narratives.",
            tools=[FileWriterTool()],  # Ensure tools is a list
            memory=True,
            llm=self.llm
        )

    @task
    def research_task(self) -> Task:
        return Task(
            description="Collect comprehensive NFL data related to: '{query}', including recent news, historical data, and relevant statistics. Only use the latest and most reliable sources.",
            expected_output="A detailed research document with organized raw data and initial findings.",
            agent=self.researcher(),
            llm=self.llm
        )

    @task
    def statistical_analysis_task(self) -> Task:
        return Task(
            description="Analyze the collected data to identify statistical patterns and trends relevant to: '{query}'. Only use the latest and most reliable sources.",
            expected_output="Statistical analysis report with key metrics, trends, and supporting data.",
            context=[self.research_task()],
            agent=self.stats_analyst(),
            llm=self.llm
        )

    @task
    def game_analysis_task(self) -> Task:
        return Task(
            description="Analyze game situations and strategic elements related to: '{query}', incorporating statistical findings. Only use the latest and most reliable sources.",
            expected_output="Detailed game analysis report with strategic insights and situational breakdowns.",
            context=[self.statistical_analysis_task()],
            agent=self.game_analyst(),
            llm=self.llm
        )

    @task
    def synthesis_task(self) -> Task:
        return Task(
            description="Integrate all research, statistics, and game analysis into comprehensive insights for: '{query}'. Only use the latest and most reliable sources.",
            expected_output="A cohesive analysis that combines all perspectives into actionable insights.",
            context=[self.research_task(), self.statistical_analysis_task(), self.game_analysis_task()],
            agent=self.writer(),
            llm=self.llm
        )

    @crew
    def crew(self) -> Crew:
        tasks = [
            self.research_task(),
            self.statistical_analysis_task(),
            self.game_analysis_task(),
            self.synthesis_task()
        ]
        return Crew(
            agents=[
                self.researcher(),
                self.stats_analyst(),
                self.game_analyst(),
                self.writer()
            ],
            tasks=tasks,
            process=Process.sequential
            # verbose=True,
            # planning=True,
            # planning_llm=self.llm
        )

# Debugging information
if __name__ == "__main__":
    try:
        NflCrew1 = NflCrew()
        inputs = {"query": "Test query"}
        result = NflCrew1.crew().kickoff(inputs=inputs)
        print(result)
    except Exception as e:
        print(f"An error occurred: {e}")