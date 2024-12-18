import os
import logging
import time
import pickle
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

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
                logging.warning("No cookies.pkl file found or unable to load cookies.")
        except Exception as e:
            logging.error(f"Failed to initialize WebDriver: {e}")
            raise

    def load_cookies(self):
        try:
            self.driver.get("https://www.pff.com")
            if os.path.exists("cookies.pkl"):
                cookies = pickle.load(open("cookies.pkl", "rb"))
                for cookie in cookies:
                    if 'sameSite' in cookie and cookie['sameSite'] == 'None':
                        cookie['sameSite'] = 'Strict'  # Adjust if necessary
                    self.driver.add_cookie(cookie)
                return True
            else:
                return False
        except Exception as e:
            logging.error(f"Failed to load cookies: {e}")
            return False

    def scrape_main_page(self, year=2023):
        """
        Scrapes the main page for the specified year, correctly handling the table structure.
        """
        try:
            url = f"https://premium.pff.com/nfl/teams/{year}/REGPO"
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "kyber-table__table"))
            )
            time.sleep(5)  # Wait for the page to load fully

            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            table = soup.find("div", class_="kyber-table__table")

            if not table:
                logging.error(f"Could not find table on main page for {year}.")
                return None

            # Extract header groups
            header_groups_container = table.find(
                "div", class_="kyber-table-header__groups-container"
            )
            header_groups = []
            current_group = ""
            for group in header_groups_container.find_all(
                "div", class_="kyber-table-header__group", recursive=False
            ):
                if "kyber-table-header__group--empty" in group.get("class", []):
                    header_groups.append(current_group)
                else:
                    current_group = group.get_text(strip=True)
                    header_groups.append(current_group)

            # Extract table headers
            header_row = table.find("div", class_="kyber-table-header__rows")
            header_cells = header_row.find_all("div", class_="kyber-table-header__column")
            headers = [cell.find("span").get_text(strip=True) if cell.find("span") else "" for cell in header_cells]

            # Combine header groups with headers
            combined_headers = []
            group_index = 0
            for header in headers:
                if group_index < len(header_groups):
                    group = header_groups[group_index]
                    if group and header:
                        combined_headers.append(f"{group} {header}")
                    elif group:
                        combined_headers.append(group)
                    else:
                        combined_headers.append(header)
                    group_index += 1
            
            # Process data rows, targeting rows with specific class
            data = []
            rows = table.find_all("div", class_="kyber-table-body__row", recursive=False)
            for row in rows:
              if not row.find("div", class_="kyber-table-body-cell"):
                continue
              cells = row.find_all("div", class_="kyber-table-body-cell")
              row_data = [cell.get_text(strip=True) for cell in cells]

              # Skip filler rows and header rows
              if not row_data or all(not item.strip() for item in row_data) or row_data[0] == 'Rank':
                continue
                
              # Pad row_data with empty strings to match the number of headers
              row_data.extend([""] * (len(combined_headers) - len(row_data)))
              data.append(row_data)

            # Create DataFrame with combined headers, skipping the first two rows
            df = pd.DataFrame(data, columns=combined_headers)
            # df = df.iloc[2:] # Removing this line because we're already skipping rows
            df = df.reset_index(drop=True)
            
            # Save to a CSV file
            output_file = f"./nfl_teams_{year}.csv"
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            df.to_csv(output_file, index=False)
            logging.info(f"Data saved to {output_file}")
            return df

        except Exception as e:
            logging.error(f"Failed to scrape main page for {year}: {e}")
            return None

    def close(self):
        if self.driver:
            self.driver.quit()

if __name__ == "__main__":
    year = 2023
    with PFFScraper() as scraper:
        scraper.scrape_main_page(year=year)