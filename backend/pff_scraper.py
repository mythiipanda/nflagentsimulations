# pff_scraper.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle
import pandas as pd
import os
import time
from bs4 import BeautifulSoup
from langchain_community.vectorstores import Chroma
# from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_community.document_loaders import CSVLoader

class PFFScraper:
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.driver = None

    def __enter__(self):
        self.init_driver()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def init_driver(self):
        try:
            self.driver = webdriver.Chrome(options=self.chrome_options)
            if not self.load_cookies():
                raise Exception("Failed to load cookies")
        except Exception as e:
            raise Exception(f"Failed to initialize WebDriver: {e}")

    def load_cookies(self):
        try:
            cookies = pickle.load(open("cookies.pkl", "rb"))
            self.driver.get("https://www.pff.com")
            for cookie in cookies:
                self.driver.add_cookie(cookie)
            time.sleep(5)
            return True
        except:
            return False

    def scrape_qb_grades(self):
        try:
            self.driver.get("https://www.pff.com/nfl/grades/position/qb")
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "kyber-table-body__row"))
            )
            
            rows = self.driver.find_elements(By.CLASS_NAME, "kyber-table-body__row")
            data = []
            
            for row in rows:
                cells = row.find_elements(By.CLASS_NAME, "kyber-table-body-cell")
                data.append({
                    "Rank": cells[0].text,
                    "Name": cells[1].text,
                    "Team": cells[2].text,
                    "Grade": cells[4].text,
                    "Pass_Grade": cells[5].text,
                    "Run_Grade": cells[6].text
                })
                
            df = pd.DataFrame(data)
            df.to_csv("qb_grades.csv", index=False)
            return df.to_dict('records')
        except Exception as e:
            raise Exception(f"Failed to scrape QB grades: {e}")

    def close(self):
        if self.driver:
            self.driver.quit()

def save_to_chromadb():
    try:
        loader = CSVLoader("qb_grades.csv")
        docs = loader.load()
        embedding_function = FastEmbedEmbeddings(model_name="BAAI/bge-large-en-v1.5")
        vectorstore = Chroma.from_documents(docs, embedding=embedding_function, persist_directory="./chroma_db")
        vectorstore.persist()
        query = "Patrick Mahomes"
        docs = vectorstore.similarity_search(query)
        print(docs[0].page_content)
        print("Data saved to ChromaDB")
    except Exception as e:
        print(f"Error saving to ChromaDB: {str(e)}")

if __name__ == "__main__":
    with PFFScraper() as scraper:
        scraper.scrape_qb_grades()
    save_to_chromadb()
