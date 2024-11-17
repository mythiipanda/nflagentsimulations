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
        # self.chrome_options.add_argument("--headless")
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
            for year in range(2006, 2025):
                url = f"https://premium.pff.com/nfl/positions/{year}/REGPO/passing?position=QB"
                self.driver.get(url)
                time.sleep(5)  # Wait for the page to load

                # Find and click the CSV download button
                try:
                    csv_button = self.driver.find_element(By.CSS_SELECTOR, "button.g-btn.kyber-button.ml-auto.mr-2.g-btn--icon-left.g-btn--secondary.g-btn--inverse.g-btn--md")
                    csv_button.click()
                    time.sleep(5)  # Wait for the download to complete
                except Exception as e:
                    print(f"Failed to click CSV download button for year {year}: {e}")

        except Exception as e:
            raise Exception(f"Failed to scrape QB grades: {e}")

    def close(self):
        if self.driver:
            self.driver.quit()

def save_to_chromadb():
    try:
        loader = CSVLoader("./backend/data/qb_grades.csv")
        docs = loader.load()
        embedding_function = FastEmbedEmbeddings(model_name="BAAI/bge-large-en-v1.5")
        vectorstore = Chroma.from_documents(docs, embedding=embedding_function, persist_directory="./backend/chroma_db")
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
