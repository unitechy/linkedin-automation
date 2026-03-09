import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from config import LINKEDIN_EMAIL, LINKEDIN_PASSWORD, MESSAGE_TEMPLATE

def human_delay(min_sec=3, max_sec=8):
    time.sleep(random.uniform(min_sec, max_sec))

def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    # Remove headless so you can see what's happening and handle any CAPTCHAs
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    return driver

def login(driver):
    driver.get("https://www.linkedin.com/login")
    human_delay(2, 4)

    email_field = driver.find_element(By.ID, "username")
    email_field.send_keys(LINKEDIN_EMAIL)
    human_delay(1, 2)

    password_field = driver.find_element(By.ID, "password")
    password_field.send_keys(LINKEDIN_PASSWORD)
    human_delay(1, 2)

    password_field.send_keys(Keys.RETURN)
    human_delay(4, 7)

    # Check if login succeeded
    if "feed" not in driver.current_url and "checkpoint" not in driver.current_url:
        raise Exception("Login may have failed. Check browser window.")

    print("Logged in successfully.")

def send_message(driver, first_name, linkedin_url):
    try:
        driver.get(linkedin_url)
        human_delay(3, 6)

        # Click the Message button on the profile
        wait = WebDriverWait(driver, 10)
        message_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Message')]"))
        )
        message_button.click()
        human_delay(2, 4)

        # Type the message
        message_box = wait.until(
            EC.presence_of_element_located((By.XPATH, "//div[@role='textbox']"))
        )
        message = MESSAGE_TEMPLATE.format(first_name=first_name)

        # Type character by character for more human-like behavior
        for char in message:
            message_box.send_keys(char)
            time.sleep(random.uniform(0.02, 0.07))

        human_delay(2, 4)

        # Send the message
        send_button = driver.find_element(By.XPATH, "//button[@type='submit' and contains(@class,'msg-form__send-button')]")
        send_button.click()
        human_delay(3, 5)

        print(f"✓ Message sent to {first_name}")
        return True

    except Exception as e:
        print(f"✗ Failed to send to {first_name}: {e}")
        return False
