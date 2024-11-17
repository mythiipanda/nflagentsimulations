# crew_test.py

import logging
from typing import Any
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import WebsiteSearchTool, SerperDevTool, ScrapeWebsiteTool, FileWriterTool
from dotenv import load_dotenv
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
import os
import agentops

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)

@CrewBase
class NflCrew:
    """NFL Analysis Crew responsible for comprehensive data collection, analysis, and content creation using the latest information as of November 16, 2024, Week 11 of the 2024-2025 NFL Season."""

    def __init__(self):
        agentops.init(os.getenv("AGENTOPS_API_KEY"))
        openai_api_key = os.getenv("OPENAI_API_KEY")
        openai_model_name = os.getenv("OPENAI_MODEL_NAME")
        gemini_model_name = os.getenv("GEMINI_MODEL_NAME")
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not openai_api_key or not openai_model_name:
            raise ValueError("Environment variables OPENAI_API_KEY and OPENAI_MODEL_NAME must be set")

        self.llm = LLM(
            api_key=openai_api_key,
            model=openai_model_name,
            temperature=0.7
        )
        self.planningllm = LLM(
            api_key=openai_api_key,
            model="cerebras/llama3.1-70b",
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
            ScrapeWebsiteTool(),
            FileWriterTool()
        ]

    @agent
    def researcher(self) -> Agent:
        return Agent(
            role="NFL Research Specialist",
            goal="Gather and compile the most recent NFL data from multiple reputable sources, including news updates, player statistics, and historical records up to November 16, 2024, Week 11 of the 2024-2025 NFL Season. Present the information in a clear and organized manner tailored to the user's query.",
            backstory="A meticulous researcher with extensive experience in collecting and verifying up-to-date sports data, specializing in NFL coverage and analytics.",
            memory=True,
            tools=[WebsiteSearchTool(), ScrapeWebsiteTool(), SerperDevTool()],
            llm=self.llm
        )

    @agent
    def stats_analyst(self) -> Agent:
        return Agent(
            role="Statistical Analyst",
            goal="Analyze the most recently gathered NFL data to extract meaningful statistical insights, focusing on both traditional metrics and advanced analytics relevant to November 16, 2024, Week 11 of the 2024-2025 NFL Season. Deliver the findings in an easy-to-understand format tailored to the user's request.",
            backstory="A data scientist specializing in sports analytics, with expertise in advanced NFL metrics such as DVOA, EPA, and situational analysis using the latest available data.",
            memory=True,
            tools=[WebsiteSearchTool(), ScrapeWebsiteTool(), SerperDevTool()],
            llm=self.llm,
            allow_code_execution=True
        )

    @agent
    def game_analyst(self) -> Agent:
        return Agent(
            role="Game Analysis Specialist",
            goal="Examine the most recent game situations, strategic decisions, and team tendencies from November 16, 2024, Week 11 of the 2024-2025 NFL Season. Provide contextual and tactical insights that directly address the user's question using up-to-date information.",
            backstory="A former NFL coach with deep understanding of game planning, situational football, and strategic analysis, utilizing the latest game data and trends.",
            memory=True,
            tools=[WebsiteSearchTool(), ScrapeWebsiteTool(), SerperDevTool()],
            llm=self.llm
        )

    @agent
    def writer(self) -> Agent:
        return Agent(
            role="Content Writer",
            goal="Transform the latest NFL analysis and data into clear, engaging, and informative content suitable for the user's needs as of November 16, 2024, Week 11 of the 2024-2025 NFL Season. Ensure the final output is well-structured, accurate, and easy to comprehend.",
            backstory="An experienced sports journalist skilled in translating the most recent technical analysis into compelling narratives.",
            tools=[FileWriterTool()],
            memory=True,
            llm=self.llm
        )

    @agent
    def reviewer(self) -> Agent:
        return Agent(
            role="Quality Assurance Reviewer",
            goal="Review and validate the outputs from other agents to ensure accuracy, coherence, and clarity based on the latest NFL information up to November 16, 2024, Week 11 of the 2024-2025 NFL Season. Provide constructive feedback or necessary corrections to meet high-quality standards for the user.",
            backstory="A detail-oriented professional with a background in sports journalism and analytics, ensuring all content meets the highest quality standards using the most recent data.",
            tools=[FileWriterTool()],
            memory=True,
            llm=self.llm
        )

    @task
    def research_task(self) -> Task:
        logging.debug("Starting research_task")
        return Task(
            description="Collect the latest NFL data related to: '{query}', including recent news, player statistics, and historical records up to November 16, 2024, Week 11 of the 2024-2025 NFL Season. Use only the most recent and reliable sources to ensure information is current. **Stop as soon as you have found the answer.**",
            expected_output="A detailed research document with organized raw data and initial findings based on the latest information.",
            agent=self.researcher(),
            llm=self.llm
        )

    @task
    def statistical_analysis_task(self) -> Task:
        logging.debug("Starting statistical_analysis_task")
        return Task(
            description="Analyze the collected NFL data up to November 16, 2024, Week 11 of the 2024-2025 NFL Season to identify and interpret statistical patterns and trends relevant to: '{query}'. Utilize both traditional metrics and advanced analytics to ensure comprehensive insights. **Stop as soon as you have found the answer.**",
            expected_output="Statistical analysis report with key metrics, trends, and supporting data based on the most recent NFL information.",
            context=[self.research_task()],
            agent=self.stats_analyst(),
            llm=self.llm
        )

    @task
    def game_analysis_task(self) -> Task:
        logging.debug("Starting game_analysis_task")
        return Task(
            description="Examine game situations and strategic elements from November 16, 2024, Week 11 of the 2024-2025 NFL Season related to: '{query}'. Incorporate the latest statistical findings to provide in-depth tactical insights. **Stop as soon as you have found the answer.**",
            expected_output="Detailed game analysis report with strategic insights and situational breakdowns based on the latest NFL data.",
            context=[self.statistical_analysis_task()],
            agent=self.game_analyst(),
            llm=self.llm
        )

    @task
    def synthesis_task(self) -> Task:
        logging.debug("Starting synthesis_task")
        return Task(
            description="Integrate all recent research, statistical analysis, and game analysis into a comprehensive and cohesive report for: '{query}', based on the latest NFL information available up to November 16, 2024, Week 11 of the 2024-2025 NFL Season. Ensure clarity and actionable insights throughout. **Stop as soon as you have found the answer.**",
            expected_output="A cohesive analysis that combines all perspectives into actionable insights using the most recent data.",
            context=[self.research_task(), self.statistical_analysis_task(), self.game_analysis_task()],
            agent=self.writer(),
            llm=self.llm
        )

    @task
    def review_task(self) -> Task:
        logging.debug("Starting review_task")
        return Task(
            description="Review the synthesized report for accuracy, clarity, and coherence based on the latest NFL information up to November 16, 2024, Week 11 of the 2024-2025 NFL Season. Provide feedback or corrections as necessary to ensure the highest quality standards are met. **Stop as soon as you have found the answer.**",
            expected_output="A verified and polished analysis report ready for dissemination, ensuring all information is current and accurate.",
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
            agents = [self.researcher(), self.stats_analyst(), self.game_analyst(), self.writer(), self.reviewer()],
            process=Process.sequential,
            verbose=True,
            planning=True,
            planning_llm=self.planningllm,
            max_rpm=15,
            memory=True,
            embedder=dict(
                provider="huggingface",
                config=dict(
                    model="sentence-transformers/all-MiniLM-L6-v2"
                )
            ),
        )
if __name__ == "__main__":
    n_iterations = 2
    inputs = {"query": "Who are the top NFL contenders this season?"}
    filename = "your_model.pkl"

    try:
        NflCrew().crew().train(
        n_iterations=n_iterations, 
        inputs=inputs, 
        filename=filename
        )

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")