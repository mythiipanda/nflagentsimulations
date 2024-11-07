import os
from typing import List, Dict, Optional
from datetime import datetime
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
    record: str
    last_week: str
    game_result: str
    beaten_teams: str
    analysis: str
    up_next: str
    week: int
    power_ranking: int


class NFLPowerRankingsScraper:
    def __init__(self):
        self.strainer = bs4.SoupStrainer(["h2", "p"])
        self.current_power_ranking = 1

    def clean_text(self, text: str) -> str:
        return ' '.join(text.strip().split())

    def extract_record(self, text: str) -> str:
        match = re.search(r'\((.*?)\)', text)
        return match.group(1) if match else "N/A"

    def parse_team_section(self, header, week) -> Optional[TeamRanking]:
        try:
            header_text = header.text
            rank_match = re.match(r'(\d+)\.\s*(.*)', header_text)
            if rank_match:
                rank = int(rank_match.group(1))
                name_record = rank_match.group(2)
            else:
                rank = None
                name_record = header_text

            name = name_record.split('(')[0].strip()
            record = self.extract_record(name_record)

            paragraphs = []
            current = header.next_sibling
            while current and current.name != 'h2':
                if current.name == 'p':
                    paragraphs.append(current)
                current = current.next_sibling

            last_week = "N/A"
            game_result = "N/A"
            beaten_teams = "N/A"
            analysis = "N/A"
            up_next = "N/A"

            for p in paragraphs:
                text = p.get_text().strip()
                if text.startswith('Last week'):
                    last_week = text
                elif text.startswith('Sunday') or text.startswith('Monday') or text.startswith('Thursday'):
                    game_result = text
                elif text.startswith('Who have they beaten?'):
                    beaten_teams = text
                elif text.startswith('Up next'):
                    up_next = text
                elif len(text) > 50:  # Likely the analysis paragraph
                    analysis = text

            team_ranking = TeamRanking(
                rank=rank,
                name=name,
                record=record,
                last_week=last_week,
                game_result=game_result,
                beaten_teams=beaten_teams,
                analysis=analysis,
                up_next=up_next,
                week=week,
                power_ranking=self.current_power_ranking
            )

            self.current_power_ranking += 1
            return team_ranking
        except (AttributeError, TypeError, ValueError, IndexError) as e:
            print(f"Warning: Could not parse team section: {e}, Header text: {header.text}")
            return None

    def scrape_rankings(self, html_content: str, week: int) -> List[TeamRanking]:
        soup = BeautifulSoup(html_content, 'html.parser', parse_only=self.strainer)
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
            for doc in documents:
                doc['content_type'] = 'nfl_power_ranking'
                doc['timestamp'] = datetime.utcnow()
            self.collection.insert_many(documents)

    def similarity_search(self, query_vector: List[float], k: int = 6, fetch_k: int = 12):
        pipeline = [
            {
                "$search": {
                    "index": "default",
                    "knnBeta": {
                        "vector": query_vector,
                        "path": "vector",
                        "k": fetch_k,
                        "filter": {
                            "text": {
                                "path": "content_type",
                                "query": "nfl_power_ranking"
                            }
                        }
                    }
                }
            },
            {
                "$addFields": {
                    "score": {
                        "$meta": "searchScore"
                    }
                }
            },
            {
                "$sort": {
                    "score": -1
                }
            },
            {
                "$limit": k
            }
        ]
        
        results = list(self.collection.aggregate(pipeline))
        return [Document(page_content=doc['content'], metadata={"score": doc.get('score', 0)}) 
                for doc in results]


class EnhancedRAG:
    def __init__(self, api_key: str, mongo_uri: str, db_name: str = "rag_db", collection_name: str = "rag_test"):
        self.client = Cerebras(api_key=api_key)
        self.embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-large-en-v1.5")
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

    def format_team_ranking(self, ranking: TeamRanking) -> str:
        return (
            f"NFL POWER RANKING ENTRY\n"
            f"-------------------------\n"
            f"Power Ranking: {ranking.power_ranking}\n"
            f"Week: {ranking.week}\n"
            f"Team: {ranking.name}\n"
            f"Record: {ranking.record}\n"
            f"Previous Rank: {ranking.last_week}\n"
            f"Recent Game: {ranking.game_result}\n"
            f"Teams Beaten: {ranking.beaten_teams}\n"
            f"Analysis: {ranking.analysis}\n"
            f"Next Game: {ranking.up_next}\n"
            f"-------------------------\n"
        )

    def load_and_process_documents(self, rankings: List[TeamRanking]):
        try:
            docs = [Document(page_content=self.format_team_ranking(ranking)) for ranking in rankings if ranking]
            
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
                separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
            )
            splits = splitter.split_documents(docs)
            
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
        enhanced_prompt = """Given the following context about NFL Power Rankings, please provide a detailed and accurate answer to the question. Focus on the most relevant and recent information from the context.

Context:
{context}

Question: {question}

Instructions:
1. Use only information explicitly stated in the context
2. If specific numbers or rankings are mentioned, include them
3. If the information isn't in the context, state that explicitly
4. Provide supporting details from the context when available

Answer:"""

        def format_docs(docs: List[Document]) -> str:
            formatted_docs = []
            for i, doc in enumerate(docs, 1):
                score = doc.metadata.get('score', 0)
                formatted_docs.append(
                    f"[Document {i} - Relevance: {score:.2f}]\n{doc.page_content}\n"
                )
            return "\n\n".join(formatted_docs)

        def rag_chain_with_verification(question: Dict[str, str]):
            hyde_doc = self.generate_hypothetical_document(question["input"])
            hyde_document = Document(page_content=hyde_doc)
            
            query_vector = self.embeddings.embed_query(question["input"])
            
            context_docs = self.vectorstore.similarity_search(
                query_vector, 
                k=6, 
                fetch_k=12
            )
            
            all_docs = [hyde_document] + context_docs
            context = format_docs(all_docs)
            
            final_prompt = enhanced_prompt.format(
                context=context,
                question=question["input"]
            )
            
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are an NFL expert assistant. Provide accurate information based solely on the given context."},
                    {"role": "user", "content": final_prompt}
                ],
                model="llama3.1-8b"
            )
            
            return response.choices[0].message.content

        return rag_chain_with_verification


if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("CEREBRAS_API_KEY")
    mongo_uri = os.getenv("MONGODB_URI")
    
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
            
            if rankings:
                splits = rag.load_and_process_documents(rankings)
                if splits:
                    rag_chain = rag.create_rag_chain()
                    
                    # Example query
                    query = {"input": "What is the Lions' power ranking in week 8 of 2024?"}
                    response = rag_chain(query)
                    print("\nQuery:", query["input"])
                    print("\nResponse:", response)
                else:
                    print("Warning: Document processing failed.")
            else:
                print("Warning: No team rankings could be extracted from the HTML.")
        
        except FileNotFoundError:
            print(f"Error: File not found - {local_file_path}")
        except Exception as e:
            print(f"An error occurred: {e}")