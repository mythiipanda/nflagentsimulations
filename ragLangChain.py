import os
from typing import List, Dict, Optional
from dotenv import load_dotenv
import bs4
from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from cerebras.cloud.sdk import Cerebras
from langchain_core.documents import Document
from bs4 import BeautifulSoup, SoupStrainer
import re
from dataclasses import dataclass
from pymongo import MongoClient
from pymongo.collection import Collection
import numpy as np
from bson.binary import Binary
import pickle


@dataclass
class TeamRanking:
    rank: int
    name: str
    opponent: str
    summary: str
    week: int


class NFLPowerRankingsScraper:
    def __init__(self):
        self.strainer = bs4.SoupStrainer(["h2", "p"])

    def clean_text(self, text: str) -> str:
        return ' '.join(text.strip().split())

    def extract_opponent(self, text: str) -> str:
        text = text.lower()
        match = re.search(r"beat\s(.*?)\s\d+-\d+", text)
        if match:
            return match.group(1).strip()
        match = re.search(r"lost to\s(.*?)\s\d+-\d+", text)
        if match:
            return match.group(1).strip()
        return "N/A"

    def parse_team_section(self, header, week) -> Optional[TeamRanking]:
        try:
            rank = int(header.text.split('.')[0])
            name = header.text.split('. ')[1].split('(')[0].strip()
            summary_paragraph = header.find_next_sibling('p')
            summary = self.clean_text(summary_paragraph.text) if summary_paragraph else ""
            opponent = self.extract_opponent(summary_paragraph.text) if summary_paragraph else "N/A"

            return TeamRanking(rank=rank, name=name, opponent=opponent, summary=summary, week=week)
        except (AttributeError, TypeError, ValueError, IndexError) as e:
            print(f"Warning: Could not parse team section: {e}, Header text: {header.text}")
            return None

    def scrape_rankings(self, html_content: str, week: int) -> List[TeamRanking]:
        soup = BeautifulSoup(html_content, 'html.parser')
        rankings = []
        for header in soup.find_all('h2'):
            team_ranking = self.parse_team_section(header, week)
            if team_ranking:
                rankings.append(team_ranking)
        return rankings


class MongoDBVectorStore:
    def __init__(self, collection: Collection):
        self.collection = collection

    def add_documents(self, documents: List[Dict]):
        if documents:
            self.collection.insert_many(documents)

    def similarity_search(self, query_vector: List[float], k: int = 6, fetch_k: int = 12, lambda_mult: float = 0.7):
        # MongoDB Atlas Vector Search aggregation pipeline
        pipeline = [
            {
                "$search": {
                    "index": "default",  # Make sure this matches your Atlas Search index name
                    "knnBeta": {
                        "vector": query_vector,
                        "path": "vector",
                        "k": fetch_k
                    }
                }
            },
            {"$limit": k}
        ]
        
        results = list(self.collection.aggregate(pipeline))
        return [Document(page_content=doc['content']) for doc in results]


class EnhancedRAG:
    def __init__(self, api_key: str, mongo_uri: str, db_name: str = "rag_db", collection_name: str = "documents"):
        self.client = Cerebras(api_key=api_key)
        self.embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-base-en-v1.5")
        self.mongo_client = MongoClient(mongo_uri)
        self.db = self.mongo_client[db_name]
        self.collection = self.db[collection_name]
        self.vectorstore = MongoDBVectorStore(self.collection)

    def generate_hypothetical_document(self, question: str) -> str:
        hyde_prompt = """Given the following question, generate a detailed hypothetical document 
        that would contain the answer to the question. Make it detailed and specific.
        
        Question: {question}
        
        Hypothetical Document:"""
        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content": hyde_prompt.format(question=question)}],
            model="llama3.1-8b"
        )
        return response.choices[0].message.content

    def load_and_process_documents(self, documents: List[Document]):
        try:
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=100,
                length_function=len,
                separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
            )
            splits = splitter.split_documents(documents)
            
            # Create documents with embeddings for MongoDB
            mongo_docs = []
            for doc in splits:
                embedding = self.embeddings.embed_query(doc.page_content)
                mongo_doc = {
                    'content': doc.page_content,
                    'vector': embedding,
                    'metadata': doc.metadata
                }
                mongo_docs.append(mongo_doc)
            
            self.vectorstore.add_documents(mongo_docs)
            return splits
        except Exception as e:
            print(f"An error occurred during embedding or splitting: {e}")
            return None

    def create_rag_chain(self):
        prompt = hub.pull("rlm/rag-prompt")

        def format_docs(docs: List[Document]) -> str:
            return "\n\n".join(f"Document {i+1}:\n{doc.page_content}" for i, doc in enumerate(docs))

        def rag_chain_with_hyde(question: Dict[str, str]):
            hyde_doc = self.generate_hypothetical_document(question["input"])
            hyde_document = Document(page_content=hyde_doc)
            
            # Get embedding for the query
            query_vector = self.embeddings.embed_query(question["input"])
            
            # Retrieve relevant documents using vector similarity
            context_docs = self.vectorstore.similarity_search(
                query_vector, 
                k=6, 
                fetch_k=12, 
                lambda_mult=0.7
            )
            
            all_docs = [hyde_document] + context_docs
            context = format_docs(all_docs)
            final_prompt = prompt.invoke({"context": context, "question": question["input"]}).to_string()
            
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": final_prompt}], 
                model="llama3.1-8b"
            )
            return response.choices[0].message.content

        return rag_chain_with_hyde


if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("CEREBRAS_API_KEY")
    mongo_uri = os.getenv("MONGODB_ATLAS_URI")
    
    if not api_key or not mongo_uri:
        print("Error: Missing required environment variables (CEREBRAS_API_KEY or MONGODB_URI)")
    else:
        rag = EnhancedRAG(api_key=api_key, mongo_uri=mongo_uri)
        local_file_path = 'NFL Power Rankings Week 8_ Are Packers, Steelers, Seahawks contenders_.html'
        try:
            with open(local_file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
            scraper = NFLPowerRankingsScraper()
            rankings = scraper.scrape_rankings(html_content, week=8)
            docs = [Document(page_content=f"Week 8: {ranking.name}\nOpponent: {ranking.opponent}\nSummary: {ranking.summary}") for ranking in rankings if ranking]
            if docs:
                rag.load_and_process_documents(docs)
                rag_chain = rag.create_rag_chain()
                response = rag_chain({"input": "What are the strengths and weaknesses of the Detroit Lions?"})
                print("Response:", response)
            else:
                print("Warning: No team rankings could be extracted from the HTML.")
        except FileNotFoundError:
            print(f"Error: File not found - {local_file_path}")
        except Exception as e:
            print(f"An error occurred: {e}")