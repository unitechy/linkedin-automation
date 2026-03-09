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
