from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pickle
import time

# Set up the WebDriver
driver = webdriver.Chrome()

# Open the login page
driver.get("https://www.pff.com/login")

# Wait for the page to load (optional)
time.sleep(2)

# Fill in your credentials (replace with your email and password)
email_input = driver.find_element(By.ID, "login-form_email")
password_input = driver.find_element(By.ID, "login-form_password")

email_input.send_keys("wjsutton1@gmail.com")
password_input.send_keys("DraftSimulator102")

# Wait for you to complete the reCAPTCHA manually
print("Please complete the CAPTCHA and login manually, then press Enter...")
input()  # Wait until the user presses Enter

# Save cookies after successful login
with open("cookies.pkl", "wb") as file:
    pickle.dump(driver.get_cookies(), file)

print("Cookies saved successfully.")
driver.quit()
