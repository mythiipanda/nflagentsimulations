# pff_tool.py

from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings

class PFFScraperInput(BaseModel):
    """Input schema for PFF scraping tools."""
    query: str = Field(..., description="Query to search in ChromaDB")

class RetrieveFromChromaDBTool(BaseTool):
    name: str = "Retrieve from ChromaDB"
    description: str = "Retrieves data from ChromaDB based on a query"
    args_schema: Type[BaseModel] = PFFScraperInput

    def _run(self, query: str) -> str:
        try:
            embedding_function = FastEmbedEmbeddings(model_name="BAAI/bge-large-en-v1.5")
            vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embedding_function)
            retriever = vectorstore.similarity_search(query)
            return retriever
        except Exception as e:
            return f"Error retrieving from ChromaDB: {str(e)}"

# Usage example:
"""
from crewai import Agent
from pff_tool import RetrieveFromChromaDBTool

researcher = Agent(
    role="NFL Research Specialist",
    goal="Gather NFL statistics",
    backstory="Sports data analyst specialized in NFL statistics",
    tools=[RetrieveFromChromaDBTool()],
    llm=llm
)
"""