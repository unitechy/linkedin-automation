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
