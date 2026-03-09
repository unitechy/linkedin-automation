# LinkedIn Message Automation

A Python script that automates personalized LinkedIn messaging at scale. Reads contacts from a CSV, sends messages via Selenium, and tracks send status to avoid duplicates.

## Features

- 📊 **CSV-based contact tracking** — Never message the same person twice
- 🤖 **Human-like behavior** — Random delays and character-by-character typing
- 📝 **Personalized messages** — Uses `{first_name}` placeholder
- ⏱️ **Rate limiting** — Configurable daily limits (10-15 messages/day)
- 🔄 **Status tracking** — Tracks `pending`, `sent`, `failed`, and `skip` statuses
- 🌐 **Visible browser** — Handle CAPTCHAs manually when they appear

## Prerequisites

- Python 3.8 or higher
- Chrome browser installed
- LinkedIn account

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/unitechy/linkedin-automation.git
   cd linkedin-automation
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your credentials**
   ```bash
   cp .env.example .env
   ```

4. **Edit `.env`** and add your LinkedIn credentials:
   ```env
   LINKEDIN_EMAIL=your_email@example.com
   LINKEDIN_PASSWORD=your_password
   ```

   ⚠️ **Never commit `.env` to git or share it publicly!**

## Usage

### 1. Customize Your Message

Edit `message.txt` to change your outreach message. Use `{first_name}` as a placeholder for personalization:

```text
Hey {first_name}, hope you're well!

Wanted to share something exciting...
```

### 2. Add Your Contacts

Edit `connections.csv` with your LinkedIn connections:

```csv
first_name,linkedin_url,status,date_sent,notes
John,https://www.linkedin.com/in/john-doe/,pending,,
Sarah,https://www.linkedin.com/in/sarah-smith/,pending,,
```

**Column definitions:**
- `first_name` — Used for personalization in message
- `linkedin_url` — Full LinkedIn profile URL
- `status` — `pending` / `sent` / `failed` / `skip`
- `date_sent` — Auto-filled by script
- `notes` — Optional manual notes

### 3. Run the Script

```bash
python main.py
```

### What Happens When You Run

1. Chrome browser opens and navigates to LinkedIn
2. Script logs in with your credentials
3. If a CAPTCHA appears, solve it manually in the browser
4. Script processes up to 12 pending contacts (configurable in `config.py`)
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

## Configuration

Edit `config.py` to adjust settings:

```python
DAILY_LIMIT = 12  # Number of messages to send per day
```

## Project Structure

```
linkedin-automation/
├── main.py                  # Entry point
├── messenger.py             # LinkedIn login + message sending logic
├── tracker.py               # CSV read/write logic
├── config.py                # Credentials and limits
├── message.txt              # Your message template (edit this!)
├── connections.csv          # Your contact list (edit this!)
├── .env.example             # Environment template
├── requirements.txt         # Python dependencies
├── .gitignore               # Excludes sensitive files
└── README.md                # This file
```

## CSV Status Reference

| Status   | Meaning                       |
|----------|-------------------------------|
| `pending` | Not yet messaged              |
| `sent`    | Successfully sent             |
| `failed`  | Script error — retry manually |
| `skip`    | Manually marked to skip       |

## Important Notes

### CAPTCHA / Security Check
LinkedIn occasionally shows a CAPTCHA on login. The script runs in a visible browser window so you can intervene manually if needed.

### Detection Prevention
- **Do not run headless** — Headless Chrome increases detection risk
- **Random delays** — 45-120 seconds between messages
- **Human-like typing** — Character-by-character message input
- **Daily limits** — Stays between 10-15 messages per day

### LinkedIn URL Format
URLs must be full profile URLs: `https://www.linkedin.com/in/username/`

### LinkedIn DOM Changes
LinkedIn periodically changes its DOM structure. If the script breaks, you may need to update the XPath selectors in `messenger.py`.

## Troubleshooting

### Script fails to find Message button
LinkedIn may have changed their button selectors. Check the current button XPath and update `messenger.py`:
```python
message_button = wait.until(
    EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Message')]"))
)
```

### Login fails
- Check that your credentials in `.env` are correct
- Ensure you can log in manually in a browser first
- Look for CAPTCHA or security verification prompts

### Chrome not found
Ensure Chrome browser is installed on your system.

## License

This project is provided as-is for educational purposes.

## Disclaimer

This tool is for personal use and educational purposes. Always respect LinkedIn's Terms of Service and API usage policies. Excessive automated messaging may result in account restrictions. Use responsibly.
