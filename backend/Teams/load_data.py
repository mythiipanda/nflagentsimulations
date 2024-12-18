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
            cookies = pickle.load(open("backend/cookies.pkl", "rb"))
            self.driver.get("https://www.pff.com")
            for cookie in cookies:
                self.driver.add_cookie(cookie)
            time.sleep(5)
            return True
        except:
            return False

    def scrape_team_page(self, team_name='arizona-cardinals', year=2023, page_type='schedule'):
      """
        Scrapes the specified type of page (schedule, offense, defense, etc) for a team
      """
      try:
          url = f"https://premium.pff.com/nfl/teams/{year}/REGPO/{team_name}/{page_type}"
          self.driver.get(url)
          time.sleep(5)  # Wait for the page to load

          # Extract the table using BeautifulSoup
          soup = BeautifulSoup(self.driver.page_source, 'html.parser')
          table = soup.find('div', class_='kyber-table__table')
          if not table:
            print(f"Could not find table on page {page_type} for {team_name} in {year}.")
            return None

            # Extract table headers
          header_row = table.find('div', class_='kyber-table-header__rows')
          header_cells = header_row.find_all('div', class_='kyber-table-header__column')
          headers = [cell.find('span').get_text(strip=True) for cell in header_cells if cell.find('span')]


          # Extract sticky column data
          body = table.find('div', class_='kyber-table-body')
          sticky_rows_container = body.find('div', class_='kyber-table-body__sticky-rows-container')
          sticky_rows = sticky_rows_container.find_all('div', class_='kyber-table-body__row') if sticky_rows_container else []
          
          # Extract data from the scrolling rows.
          scrolling_rows = body.find('div', class_='kyber-table-body__scrolling-rows')
          data_rows = scrolling_rows.find_all('div', class_='kyber-table-body__row') if scrolling_rows else []

          data = []
          if sticky_rows and data_rows:
            for sticky_row, data_row in zip(sticky_rows, data_rows):
                sticky_cells = sticky_row.find_all('div', class_='kyber-table-body-cell')
                sticky_data = [cell.get_text(strip=True) for cell in sticky_cells]
            
                data_cells = data_row.find_all('div', class_='kyber-table-body-cell')
                data_data = [cell.get_text(strip=True) for cell in data_cells]

                #Skip empty rows
                if not sticky_data and not data_data:
                  continue
                  
                row_data = sticky_data + data_data
                
                # Pad/Truncate row_data to match number of headers
                if len(row_data) < len(headers):
                   row_data.extend([''] * (len(headers) - len(row_data)))
                elif len(row_data) > len(headers):
                    row_data = row_data[:len(headers)]
                
                data.append(row_data)
          elif data_rows: #Handle case of no sticky rows
            for data_row in data_rows:
                data_cells = data_row.find_all('div', class_='kyber-table-body-cell')
                data_data = [cell.get_text(strip=True) for cell in data_cells]
                
                  #Skip empty rows
                if not data_data:
                  continue

                 # Pad/Truncate row_data to match number of headers
                if len(data_data) < len(headers):
                  data_data.extend([''] * (len(headers) - len(data_data)))
                elif len(data_data) > len(headers):
                  data_data = data_data[:len(headers)]
                  
                data.append(data_data)

          df = pd.DataFrame(data, columns=headers)

          # Save to a CSV file
          output_file = f"./backend/Teams/{team_name}/{team_name}_{page_type}_{year}.csv"
          os.makedirs(os.path.dirname(output_file), exist_ok=True)
          df.to_csv(output_file, index=False)
          print(f"Data saved to {output_file}")
          return df

      except Exception as e:
          print(f"Failed to scrape {page_type} for {team_name} in {year}: {e}")
          return None

    def close(self):
        if self.driver:
            self.driver.quit()


if __name__ == "__main__":
    year = 2023
    page_types = [
        'schedule', 'offense', 'passing', 'receiving',
        'rushing', 'offense-blocking',
        'offense-pass-blocking', 'offense-run-blocking', 'defense', 'defense-run',
        'defense-pass-rush', 'defense-coverage', 'special-teams', 'kick-returning',
        'kicking', 'punting', 'kickoffs'
    ]

    with PFFScraper() as scraper:
       
      teams = [
          "arizona-cardinals",
          "atlanta-falcons",
          "baltimore-ravens",
          "buffalo-bills",
          "carolina-panthers",
          "chicago-bears",
          "cincinnati-bengals",
          "cleveland-browns",
          "dallas-cowboys",
          "denver-broncos",
          "detroit-lions",
          "green-bay-packers",
          "houston-texans",
          "indianapolis-colts",
          "jacksonville-jaguars",
          "kansas-city-chiefs",
          "las-vegas-raiders",
          "los-angeles-rams",
          "los-angeles-chargers",
          "miami-dolphins",
          "minnesota-vikings",
          "new-england-patriots",
          "new-orleans-saints",
          "new-york-giants",
          "new-york-jets",
          "philadelphia-eagles",
          "pittsburgh-steelers",
          "san-francisco-49ers",
          "seattle-seahawks",
          "tampa-bay-buccaneers",
          "tennessee-titans",
          "washington-commanders"
      ]

      for team in teams:
        for page_type in page_types:
          scraper.scrape_team_page(team_name=team, year=year, page_type=page_type)