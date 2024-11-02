import os
from typing import List, Dict
from dotenv import load_dotenv
import bs4
from langchain import hub
from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from cerebras.cloud.sdk import Cerebras
from langchain_core.documents import Document
from bs4 import BeautifulSoup, SoupStrainer
import re
from dataclasses import dataclass

@dataclass
class TeamRanking:
    rank: int
    name: str
    sos_to_date: float
    sos_remaining: float
    projected_wins: float
    playoff_chance: float
    division_chance: float
    conference_chance: float
    superbowl_chance: float
    summary: str

class NFLPowerRankingsScraper:
    def __init__(self):
        # Target both the team headers and the stats sections
        self.strainer = bs4.SoupStrainer(["h3", "ul", "p"])
    
    def clean_text(self, text: str) -> str:
        """Clean text by removing extra whitespace and newlines"""
        return ' '.join(text.strip().split())
    
    def extract_number(self, text: str) -> float:
        """Extract number from text, handling percentages and decimals"""
        match = re.search(r'[\d.]+', text)
        return float(match.group()) if match else 0.0
    
    def parse_team_section(self, header, stats_list, summary) -> TeamRanking:
        """Parse a single team section into a TeamRanking object"""
        # Extract rank and team name from header
        rank_match = re.search(r'(\d+)', header.get('id', '0'))
        rank = int(rank_match.group(1)) if rank_match else 0
        name = header.find('b').text.strip()
        
        # Initialize default values
        stats = {
            'sos_to_date': 0.0,
            'sos_remaining': 0.0,
            'projected_wins': 0.0,
            'playoff_chance': 0.0,
            'division_chance': 0.0,
            'conference_chance': 0.0,
            'superbowl_chance': 0.0
        }
        
        # Extract stats from list items
        if stats_list:
            for li in stats_list.find_all('li'):
                text = li.text.strip().lower()
                if 'strength of schedule to date' in text:
                    stats['sos_to_date'] = self.extract_number(text)
                elif 'strength of schedule remaining' in text:
                    stats['sos_remaining'] = self.extract_number(text)
                elif 'projected win total' in text:
                    stats['projected_wins'] = self.extract_number(text)
                elif 'chance of making the playoffs' in text:
                    stats['playoff_chance'] = self.extract_number(text)
                elif 'chance of winning the division' in text:
                    stats['division_chance'] = self.extract_number(text)
                elif 'chance of winning the conference' in text:
                    stats['conference_chance'] = self.extract_number(text)
                elif 'chance of winning the super bowl' in text:
                    stats['superbowl_chance'] = self.extract_number(text)
        
        return TeamRanking(
            rank=rank,
            name=name,
            sos_to_date=stats['sos_to_date'],
            sos_remaining=stats['sos_remaining'],
            projected_wins=stats['projected_wins'],
            playoff_chance=stats['playoff_chance'],
            division_chance=stats['division_chance'],
            conference_chance=stats['conference_chance'],
            superbowl_chance=stats['superbowl_chance'],
            summary=self.clean_text(summary.text) if summary else ""
        )
    
    def scrape_rankings(self, url: str) -> List[TeamRanking]:
        """Scrape and parse the NFL power rankings"""
        # Load the webpage
        loader = WebBaseLoader(
            web_paths=(url,),
            bs_kwargs={"parse_only": self.strainer}
        )
        raw_doc = loader.load()[0]
        
        # Parse the HTML
        soup = BeautifulSoup(raw_doc.page_content, 'html.parser')
        
        # Find all team sections
        rankings = []
        current_header = None
        current_stats = None
        
        for element in soup.find_all(['h3', 'ul', 'p']):
            if element.name == 'h3':
                # If we have a complete set, process it
                if current_header and current_stats:
                    summary = element.find_previous('p')
                    rankings.append(self.parse_team_section(current_header, current_stats, summary))
                current_header = element
                current_stats = None
            elif element.name == 'ul' and current_header:
                current_stats = element
        
        # Don't forget the last team
        if current_header and current_stats:
            summary = soup.find_all('p')[-1]
            rankings.append(self.parse_team_section(current_header, current_stats, summary))
        
        # Sort by rank
        rankings.sort(key=lambda x: x.rank)
        return rankings

class EnhancedRAG:
    def __init__(self, api_key: str):
        self.client = Cerebras(api_key=api_key)
        self.embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-base-en-v1.5")
        self.vectorstore = None

    def generate_hypothetical_document(self, question: str) -> str:
        """
        Implement HyDE: Generate a hypothetical document that would answer the question
        """
        hyde_prompt = """Given the following question, generate a detailed hypothetical document 
        that would contain the answer to the question. Make it detailed and specific.
        
        Question: {question}
        
        Hypothetical Document:"""
        
        response = self.client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": hyde_prompt.format(question=question)
            }],
            model="llama3.1-8b"
        )
        return response.choices[0].message.content

    def load_and_process_documents(self, url: str, bs4_strainer=None):
        """
        Load and process documents with advanced splitting techniques
        """
        # Load documents
        loader = WebBaseLoader(
            web_paths=(url,),
            bs_kwargs={"parse_only": bs4_strainer} if bs4_strainer else {}
        )
        docs = loader.load()
        
        # Advanced splitting with optimal chunk sizing
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            length_function=len,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
        splits = splitter.split_documents(docs)
        
        # Create vector store
        self.vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=self.embeddings
        )
        
        return splits

    def create_enhanced_retriever(self, k: int = 6):
        """
        Create an enhanced retriever with MMR search
        """
        return self.vectorstore.as_retriever(
            search_type="mmr",  # Use MMR for diversity
            search_kwargs={
                "k": k,
                "fetch_k": k * 2,  # Fetch more docs initially for better diversity
                "lambda_mult": 0.7  # Balance between relevance and diversity
            }
        )

    def create_rag_chain(self):
        """
        Create an enhanced RAG chain with HyDE
        """
        retriever = self.create_enhanced_retriever()
        prompt = hub.pull("rlm/rag-prompt")

        def format_docs(docs: List[Document]) -> str:
            return "\n\n".join(f"Document {i+1}:\n{doc.page_content}" 
                             for i, doc in enumerate(docs))

        # Create the chain with HyDE
        def rag_chain_with_hyde(question: Dict[str, str]):
            # Generate hypothetical document
            hyde_doc = self.generate_hypothetical_document(question["input"])
            
            # Add hypothetical document to retriever context
            hyde_document = Document(page_content=hyde_doc)
            context_docs = retriever.get_relevant_documents(question["input"])
            all_docs = [hyde_document] + context_docs
            
            # Format context and generate response
            context = format_docs(all_docs)
            
            # Generate final response using Cerebras
            final_prompt = prompt.invoke({
                "context": context,
                "question": question["input"]
            }).to_string()
            
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": final_prompt}],
                model="llama3.1-8b"
            )
            
            return response.choices[0].message.content

        return rag_chain_with_hyde

# Example usage
if __name__ == "__main__":
    load_dotenv()
    
    # Initialize RAG system
    rag = EnhancedRAG(api_key=os.getenv("CEREBRAS_API_KEY"))
    
    # Load and process documents
    bs4_strainer = bs4.SoupStrainer(class_=("m-article__content"))
    rag.load_and_process_documents(
        "https://www.pff.com/news/nfl-week-9-power-rankings-time-to-panic-in-dallas",
        bs4_strainer
    )
    
    # Create and use the RAG chain
    rag_chain = rag.create_rag_chain()
    response = rag_chain({"input": "Based on the article, list the top 9 NFL teams in week 9 by projected win total."})
    print("Response:", response)
