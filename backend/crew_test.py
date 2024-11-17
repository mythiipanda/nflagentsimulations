import logging
from typing import Any
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import WebsiteSearchTool, SerperDevTool, ScrapeWebsiteTool, FileWriterTool
from dotenv import load_dotenv
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from llama_index.core import VectorStoreIndex
import os
import agentops

# Load environment variables
load_dotenv()
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
# Configure logging
logging.basicConfig(level=logging.DEBUG)

@CrewBase
class NflCrew:
    """NFL Analysis Crew responsible for comprehensive data collection, analysis, and content creation 
    using the latest information for Week 11 of the 2024-2025 NFL Season."""

    def __init__(self):
        # Initialize APIs and validate configuration
        agentops.init(os.getenv("AGENTOPS_API_KEY"))
        openai_api_key = os.getenv("OPENAI_API_KEY")
        openai_model_name = os.getenv("OPENAI_MODEL_NAME")
        gemini_model_name = os.getenv("GEMINI_MODEL_NAME")
        gemini_api_key = os.getenv("GEMINI_API_KEY")

        if not openai_api_key or not openai_model_name:
            raise ValueError("Environment variables OPENAI_API_KEY and OPENAI_MODEL_NAME must be set")

        self.llm = LLM(api_key=openai_api_key, model=openai_model_name, temperature=0.7)
        self.planningllm = LLM(api_key=openai_api_key, model=openai_model_name, temperature=0.7)

        # Tools
        self.tools = [
            WebsiteSearchTool(config=dict(
                llm=dict(provider="openai", config=dict(api_key=openai_api_key, model=openai_model_name, temperature=0.5)),
                embedder=dict(provider="huggingface", config=dict(model="sentence-transformers/all-MiniLM-L6-v2"))
            )),
            SerperDevTool(),
            ScrapeWebsiteTool(),
            FileWriterTool()
        ]

        # Database/Knowledge Graph for faster data retrieval
        self.index = VectorStoreIndex.from_documents([])  # Placeholder for NFL documents

    @agent
    def researcher(self) -> Agent:
        return Agent(
            role="NFL Research Specialist",
            goal="Collect the latest NFL data related to: '{query}', including recent news, player statistics, and historical records up to November 16, 2024, Week 11 of the 2024-2025 NFL Season. Use only the most recent and reliable sources to ensure information is current. **Stop as soon as you have found the answer.**",
            backstory="An experienced researcher with a passion for NFL data accuracy and completeness.",
            memory=True,
            tools=[WebsiteSearchTool(), ScrapeWebsiteTool(), SerperDevTool()],
            llm=self.llm,
            verbose=True
        )

    @agent
    def stats_analyst(self) -> Agent:
        return Agent(
            role="Statistical Analyst",
            goal="Analyze NFL data using traditional metrics and advanced analytics, writing and executing code for deeper insights.",
            backstory="A data scientist with expertise in advanced metrics like DVOA, EPA, and more.",
            memory=True,
            tools=[WebsiteSearchTool(), ScrapeWebsiteTool(), SerperDevTool()],
            llm=self.llm,
            allow_code_execution=True,
            verbose=True
        )

    @agent
    def game_analyst(self) -> Agent:
        return Agent(
            role="Game Analysis Specialist",
            goal="Provide strategic insights on NFL game situations and team tendencies, contextualized for Week 11.",
            backstory="A former coach skilled in tactical NFL analysis, with deep insights into team strategies.",
            memory=True,
            tools=[WebsiteSearchTool(), ScrapeWebsiteTool(), SerperDevTool()],
            llm=self.llm,
            verbose=True
        )

    @agent
    def writer(self) -> Agent:
        return Agent(
            role="Content Writer",
            goal="Translate NFL insights into engaging and informative content for various audiences.",
            backstory="A journalist adept at presenting complex NFL data as accessible narratives.",
            tools=[FileWriterTool()],
            memory=True,
            llm=self.llm,
            verbose=True
        )

    @agent
    def reviewer(self) -> Agent:
        return Agent(
            role="Quality Assurance Reviewer",
            goal="Validate all outputs for accuracy, including verifying player-team relationships and factual correctness.",
            backstory="A detail-oriented expert ensuring NFL content accuracy and coherence.",
            tools=[FileWriterTool(), WebsiteSearchTool(), ScrapeWebsiteTool()],
            memory=True,
            llm=self.llm,
            verbose=True
        )

    @task
    def research_task(self) -> Task:
        logging.debug("Starting research_task")
        return Task(
            description="Research the latest NFL data for '{query}', including statistics, team updates, and news.",
            expected_output="A research document with the latest NFL data organized for analysis.",
            agent=self.researcher(),
            llm=self.llm
        )

    @task
    def statistical_analysis_task(self) -> Task:
        logging.debug("Starting statistical_analysis_task")
        return Task(
            description="Analyze NFL data for '{query}' using metrics like EPA, DVOA, and situational data. Execute code if necessary.",
            expected_output="A detailed statistical analysis report with actionable insights.",
            context=[self.research_task()],
            agent=self.stats_analyst(),
            llm=self.llm
        )

    @task
    def game_analysis_task(self) -> Task:
        logging.debug("Starting game_analysis_task")
        return Task(
            description="Provide insights into game strategies and team tendencies for '{query}', using analysis results.",
            expected_output="A game analysis report with tactical breakdowns.",
            context=[self.statistical_analysis_task()],
            agent=self.game_analyst(),
            llm=self.llm
        )

    @task
    def synthesis_task(self) -> Task:
        logging.debug("Starting synthesis_task")
        return Task(
            description="Integrate research, statistical, and game analyses into a comprehensive report for '{query}'.",
            expected_output="A cohesive and comprehensive NFL report.",
            context=[self.research_task(), self.statistical_analysis_task(), self.game_analysis_task()],
            agent=self.writer(),
            llm=self.llm
        )

    @task
    def review_task(self) -> Task:
        logging.debug("Starting review_task")
        return Task(
            description="Review the report for factual and contextual accuracy, checking player-team mappings and recent updates.",
            expected_output="A verified and polished NFL report.",
            context=[self.synthesis_task()],
            agent=self.reviewer(),
            llm=self.llm
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            tasks=[
                self.research_task(),
                self.statistical_analysis_task(),
                self.game_analysis_task(),
                self.synthesis_task(),
                self.review_task()
            ],
            agents=[
                self.researcher(),
                self.stats_analyst(),
                self.game_analyst(),
                self.writer(),
                self.reviewer()
            ],
            process=Process.sequential,
            verbose=True,
            planning=True,
            planning_llm=self.planningllm,
            max_rpm=10,
            memory=True,
            embedder=dict(provider="huggingface", config=dict(model="sentence-transformers/all-MiniLM-L6-v2"))
        )

if __name__ == "__main__":
    inputs = {"query": "Analyze the games for NFL week 11 and provide predictions."}
    filename = "nfl_model.pkl"

    try:
        NflCrew().crew().train(n_iterations=2, inputs=inputs, filename=filename)
    except Exception as e:
        logging.error(f"Error occurred: {e}")
