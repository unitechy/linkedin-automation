import os
from dotenv import load_dotenv

load_dotenv()

LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")

DAILY_LIMIT = 12  # stays between 10–15

# Read message template from separate file
with open("message.txt", "r") as f:
    MESSAGE_TEMPLATE = f.read().strip()
