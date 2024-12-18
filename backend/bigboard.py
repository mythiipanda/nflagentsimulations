import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

# Initialize the WebDriver (assuming you are using Chrome)
driver = webdriver.Chrome()

# Open the website
driver.get('https://jacklich10.com/bigboard/nfl/')

# Select 2023 as the draft year
year_select = Select(driver.find_element(By.ID, 'year'))
year_select.select_by_value('2023')

# Wait for the page to load
time.sleep(5)

# Select 200 rows per page
page_size_select = Select(driver.find_element(By.CLASS_NAME, 'rt-page-size-select'))
page_size_select.select_by_value('200')

# Wait for the page to load
time.sleep(5)

# Initialize a list to store the data
data = []

# Function to extract data from the table
def extract_data():
    rows = driver.find_elements(By.CLASS_NAME, 'rt-tr-group')
    for row in rows:
        cells = row.find_elements(By.CLASS_NAME, 'rt-td')
        row_data = [cell.text for cell in cells]
        data.append(row_data)

# Extract data from the first page
extract_data()

# Navigate to the next page
next_button = driver.find_element(By.CLASS_NAME, 'rt-next-button')
next_button.click()

# Wait for the page to load
time.sleep(5)

# Extract data from the second page
extract_data()

# Navigate to the next page
next_button = driver.find_element(By.CLASS_NAME, 'rt-next-button')
next_button.click()

# Wait for the page to load
time.sleep(5)

# Extract data from the third page
extract_data()

# Close the WebDriver
driver.quit()

# Convert the data to a DataFrame
df = pd.DataFrame(data)

# Save the DataFrame to a CSV file
df.to_csv('nfl_draft_2023.csv', index=False)

print("Data has been saved to nfl_draft_2023.csv")