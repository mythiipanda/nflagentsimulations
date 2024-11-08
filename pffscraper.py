from selenium import webdriver
from selenium.webdriver.common.by import By
import pickle
import time
from bs4 import BeautifulSoup
import pandas as pd  # Add pandas import

# Set up Selenium
driver = webdriver.Chrome()
driver.get("https://www.pff.com")  # Load the main page or a public URL on the site first

# Load your previously saved cookies
cookies = pickle.load(open("cookies.pkl", "rb"))
for cookie in cookies:
    driver.add_cookie(cookie)

# Navigate to the desired page after adding cookies
driver.get("https://www.pff.com/nfl/grades/position/qb")

# Allow time for content to load
time.sleep(3)

# Now proceed to scrape the page content
page_source = driver.page_source  # Get the HTML content
soup = BeautifulSoup(page_source, "html.parser")

# Find all player rows
player_rows = soup.find_all("div", class_="kyber-table-body__row")

# Initialize a list to store player data
player_data = []

# Process each player row
for row in player_rows:
    # Extract specific cell data based on observed structure
    cells = row.find_all("div", class_="kyber-table-body-cell")
    
    # Assign data from cells based on headers provided (adjust indices as necessary)
    rank = cells[0].text.strip()
    player_name = cells[1].text.strip()
    team = cells[2].find("a").text.strip() if cells[2].find("a") else "N/A"
    jersey_number = cells[3].text.strip()
    off_grade = cells[4].text.strip()
    pass_grade = cells[5].text.strip()
    run_grade = cells[6].text.strip()
    recv_grade = cells[7].text.strip()
    pblk_grade = cells[8].text.strip()
    rblk_grade = cells[9].text.strip()
    off_snaps = cells[10].text.strip()
    off_pass = cells[11].text.strip()
    off_run = cells[12].text.strip()
    off_recv = cells[13].text.strip()
    off_pblk = cells[14].text.strip()
    off_rblk = cells[15].text.strip()
    age = cells[16].text.strip()
    rs = cells[17].text.strip()
    ht = cells[18].text.strip()
    wt = cells[19].text.strip()
    sp = cells[20].text.strip()
    college = cells[21].text.strip()
    
    # Append the extracted data to the list
    player_data.append({
        "Rank": rank,
        "Player": player_name,
        "Team": team,
        "Jersey #": jersey_number,
        "Off Grade": off_grade,
        "Pass Grade": pass_grade,
        "Run Grade": run_grade,
        "Recv Grade": recv_grade,
        "Pblk Grade": pblk_grade,
        "Rblk Grade": rblk_grade,
        "Off Snaps": off_snaps,
        "Off Pass": off_pass,
        "Off Run": off_run,
        "Off Recv": off_recv,
        "Off Pblk": off_pblk,
        "Off Rblk": off_rblk,
        "Age": age,
        "RS": rs,
        "HT": ht,
        "WT": wt,
        "SP": sp,
        "College": college
    })

# Convert the list to a DataFrame
df = pd.DataFrame(player_data)

# Save the DataFrame to a CSV file
df.to_csv("player_data.csv", index=False)

# Clean up
driver.quit()
