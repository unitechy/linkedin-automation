# LinkedIn Message Automation — Claude Code Workflow

## Overview
A Python script that reads a CSV of LinkedIn connections, sends personalized messages using Selenium, and updates the CSV with send status. Runs 10–15 messages per day with random delays to avoid detection.

---

## Project Structure

```
linkedin_automation/
├── main.py                  # Entry point
├── messenger.py             # LinkedIn login + message sending logic
├── tracker.py               # CSV read/write logic
├── config.py                # Credentials, limits (reads message from message.txt)
├── message.txt              # Your message template (edit here!)
├── connections.csv          # Your input/tracking file
├── .env.example             # Environment template
├── requirements.txt         # Python dependencies
└── .env                     # Your credentials (create from .env.example)
```

---

## Step 1: requirements.txt

```
selenium
webdriver-manager
pandas
python-dotenv
```

---

## Step 2: .env file (create this manually, never commit to git)

```
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password
```

---

## Step 3: message.txt

Edit your message template here. Use `{first_name}` as a placeholder — it gets replaced with each contact's first name from the CSV.

```text
Hey {first_name}, hope you're well!

Wanted to share something that might be relevant depending on what's on your plate for 2026 — especially if compliance readiness, data ownership, or observability costs are part of the conversation.

We just launched Glassbox — a single-tenant deployment model for Last9. The infrastructure sits entirely within your own AWS sub-account, you retain full data and compliance control, no egress surprises, and a clean license + infra cost structure with no usage-driven blowouts. Our team handles deployment, operations, and upgrades end-to-end.

Particularly relevant if you're running Datadog, New Relic, or managing your own OSS stack and feeling the operational weight of it.

Happy to share more if it's relevant to where you're headed — just say the word!
```

---

## Step 4: config.py

```python
import os
from dotenv import load_dotenv

load_dotenv()

LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")

DAILY_LIMIT = 12  # stays between 10–15

# Read message template from separate file
with open("message.txt", "r") as f:
    MESSAGE_TEMPLATE = f.read().strip()
```

---

## Step 5: connections.csv

## Step 4: connections.csv

Create this file with the following columns. Add your LinkedIn connections manually or export from LinkedIn (Settings > Data Privacy > Get a copy of your data).

```csv
first_name,linkedin_url,status,date_sent,notes
Rahul,https://www.linkedin.com/in/rahul-example/,pending,,
Priya,https://www.linkedin.com/in/priya-example/,pending,,
```

**Column definitions:**
- `first_name` — used for personalization in message
- `linkedin_url` — full profile URL of the connection
- `status` — `pending` / `sent` / `failed` / `skip`
- `date_sent` — auto-filled by script
- `notes` — optional manual notes

---

## Step 6: tracker.py

```python
import pandas as pd
from datetime import date

CSV_PATH = "connections.csv"

def load_contacts():
    df = pd.read_csv(CSV_PATH)
    return df

def get_pending(df, limit):
    pending = df[df["status"] == "pending"].head(limit)
    return pending

def mark_sent(df, index):
    df.at[index, "status"] = "sent"
    df.at[index, "date_sent"] = str(date.today())
    save(df)

def mark_failed(df, index):
    df.at[index, "status"] = "failed"
    save(df)

def save(df):
    df.to_csv(CSV_PATH, index=False)
```

---

## Step 7: messenger.py

```python
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
```

---

## Step 8: main.py

```python
from tracker import load_contacts, get_pending, mark_sent, mark_failed
from messenger import init_driver, login, send_message
from config import DAILY_LIMIT
import time
import random

def main():
    df = load_contacts()
    pending = get_pending(df, DAILY_LIMIT)

    if pending.empty:
        print("No pending contacts to message today.")
        return

    print(f"Found {len(pending)} contacts to message today.")

    driver = init_driver()
    login(driver)

    sent_count = 0

    for idx, row in pending.iterrows():
        print(f"\nProcessing: {row['first_name']} — {row['linkedin_url']}")
        success = send_message(driver, row["first_name"], row["linkedin_url"])

        if success:
            mark_sent(df, idx)
            sent_count += 1
        else:
            mark_failed(df, idx)

        # Random delay between messages (45 sec to 2 min)
        if sent_count < len(pending):
            wait = random.uniform(45, 120)
            print(f"Waiting {round(wait)}s before next message...")
            time.sleep(wait)

    driver.quit()
    print(f"\nDone. {sent_count} messages sent today.")

if __name__ == "__main__":
    main()
```

---

## How to Run

### Prerequisites
- Python 3.8 or higher
- Chrome browser installed
- LinkedIn account

### Step-by-Step Instructions

```bash
# 1. Navigate to the project directory
cd /Applications/XAMPP/xamppfiles/htdocs/Selenium

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Create your .env file from the example
cp .env.example .env

# 4. Edit .env and add your actual LinkedIn credentials
# Use any text editor to open .env and replace:
#   - your_email@example.com with your LinkedIn email
#   - your_password with your LinkedIn password
# IMPORTANT: Never commit .env to git or share it publicly

# 5. (Optional) Customize your message in message.txt
# Edit message.txt to change your outreach message
# Keep {first_name} as a placeholder for personalization

# 6. Populate connections.csv with your contacts
# Edit connections.csv and replace the example entries with real LinkedIn connections
# Format: first_name,linkedin_url,status,date_sent,notes
# Example:
#   John,https://www.linkedin.com/in/john-doe/,pending,,
#   Sarah,https://www.linkedin.com/in/sarah-smith/,pending,,

# 7. Run the script
python main.py
```

### What Happens When You Run
1. Chrome browser will open and navigate to LinkedIn
2. Script will automatically log in with your credentials
3. If a CAPTCHA appears, solve it manually in the browser
4. Script will process up to 12 pending contacts (configurable in `config.py`)
5. For each contact:
   - Opens their LinkedIn profile
   - Clicks the Message button
   - Types and sends the personalized message
   - Waits 45-120 seconds before the next message
6. CSV file is updated with `sent` or `failed` status
7. Browser closes when complete

### Daily Usage
Run `python main.py` once per day. The script automatically:
- Picks only contacts with `pending` status
- Limits to `DAILY_LIMIT` contacts (default: 12)
- Updates status to `sent` or `failed`
- Skips already processed contacts

---

## CSV Status Reference

| Status | Meaning |
|--------|---------|
| `pending` | Not yet messaged |
| `sent` | Successfully sent |
| `failed` | Script error — retry manually |
| `skip` | Manually marked to skip |

---

## Important Notes for Claude Code

1. **CAPTCHA / Security Check** — LinkedIn occasionally shows a CAPTCHA on login. The script runs in a visible browser window so you can intervene manually if needed.

2. **Session reuse** — If you want to avoid logging in every time, ask Claude Code to add cookie-based session persistence.

3. **LinkedIn URL format** — URLs must be full profile URLs: `https://www.linkedin.com/in/username/`. Short or vanity URLs work fine.

4. **Daily run** — Run `python main.py` once per day. It automatically picks the next batch of `pending` contacts up to the daily limit.

5. **Do not run headless** — Headless Chrome increases detection risk on LinkedIn. Keep the browser visible.

6. **Message button XPath** — LinkedIn periodically changes its DOM. If the script breaks, ask Claude Code to update the XPath selectors in `messenger.py`.

7. **Editing your message** — Edit `message.txt` directly to change your outreach message. Keep `{first_name}` as the placeholder for personalization.
