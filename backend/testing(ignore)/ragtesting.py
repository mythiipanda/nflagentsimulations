import logging
from datetime import datetime, timezone
from typing import Any, Dict, List
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import WebsiteSearchTool, SerperDevTool, ScrapeWebsiteTool, FileWriterTool
from dotenv import load_dotenv
from llama_index.core import Document
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import chromadb
import os
from pff_stats_tool import (
    DefenseTool,
    FieldGoalTool,
    OffenseBlockingTool,
    PassingTool,
    PuntingTool,
    ReceivingTool,
    RushingTool
)

# Load environment variables
load_dotenv()
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Define embedding model
embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Initialize persistent Chroma client
PERSIST_DIR = "local_chromadb"
chroma_client = chromadb.PersistentClient(path=PERSIST_DIR)
chroma_collection = chroma_client.get_or_create_collection("nfl_data")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)


def store_data(data: str, metadata: Dict[str, Any]):
    """Store the entire task output in ChromaDB."""
    if not data.strip():
        logging.warning("No data to store.")
        return

    document = Document(text=data, metadata=metadata)
    try:
        vector_store.add_documents([document])
        vector_store.persist()
        logging.info("Data stored in ChromaDB.")
    except Exception as e:
        logging.error(f"Error storing data: {e}")


@CrewBase
class NflCrew:
    """NFL Analysis Crew for Week 11 of the 2024-2025 NFL Season."""

    def __init__(self):
        # Load API keys and models
        openai_api_key = os.getenv("OPENAI_API_KEY")
        openai_model_name = os.getenv("OPENAI_MODEL_NAME", "gpt-4")

        if not openai_api_key:
            raise ValueError("Environment variable OPENAI_API_KEY must be set")

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
            FileWriterTool(),
            DefenseTool(),
            FieldGoalTool(),
            OffenseBlockingTool(),
            PassingTool(),
            PuntingTool(),
            ReceivingTool(),
            RushingTool()
        ]

    @agent
    def researcher(self) -> Agent:
        return Agent(
            role="NFL Research Specialist",
            goal="Collect the latest NFL data related to: '{query}', including recent news, player statistics, and historical records.",
            backstory="An experienced researcher with a passion for NFL data accuracy and completeness.",
            memory=True,
            tools=self.tools,
            llm=self.llm,
            verbose=True
        )

    @task
    def research_task(self) -> Task:
        def post_process(output: str):
            """Store the task output in ChromaDB."""
            logging.debug("Storing research task output...")
            metadata = {"source": "research_task", "timestamp": datetime.now(timezone.utc).isoformat()}
            store_data(output, metadata)

        return Task(
            description="Research the latest NFL data for '{query}', including statistics, team updates, and news.",
            expected_output="A research document with the latest NFL data organized for analysis.",
            agent=self.researcher(),
            callback=post_process,
            llm=self.llm
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            tasks=[self.research_task()],
            agents=[self.researcher()],
            process=Process.sequential,
            verbose=True,
            planning=True,
            planning_llm=self.planningllm
        )


if __name__ == "__main__":
    inputs = {"query": "Provide Darnell Dockett's 2007 stats"}
    nfl_crew = NflCrew()

    try:
        nfl_crew.crew().kickoff(inputs=inputs)
        logging.info("Crew completed successfully!")
    except Exception as e:
        logging.error(f"Error occurred: {e}")

    # Optional: Verify stored data in ChromaDB
    print(f"Number of documents in collection: {chroma_collection.count()}")
