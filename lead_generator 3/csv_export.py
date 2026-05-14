import os
import pandas as pd
from datetime import datetime


CSV_FILE = "leads.csv"


def save_to_csv(data: list[dict]) -> str:
    """
    Save lead data to leads.csv using pandas.

    Appends to the file if it already exists (no duplicate rows).
    Creates the file with a header if it does not exist yet.

    Args:
        data: List of dicts, e.g.:
              [{"name": "КРОК", "website": "https://croc.ru", "email": "info@croc.ru"}, ...]

    Returns:
        Absolute path to the saved CSV file.
    """
    if not data:
        print("No data provided — nothing to save.")
        return ""

    df_new = pd.DataFrame(data)

    # Add a timestamp column so you know when each row was scraped
    df_new["scraped_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if os.path.exists(CSV_FILE):
        df_existing = pd.read_csv(CSV_FILE, dtype=str)

        # Combine and drop exact duplicate rows
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        df_combined.drop_duplicates(inplace=True)
    else:
        df_combined = df_new

    df_combined.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")  # utf-8-sig for Excel compatibility

    abs_path = os.path.abspath(CSV_FILE)
    print(f"Saved {len(df_combined)} rows → {abs_path}")
    return abs_path


def load_from_csv() -> pd.DataFrame:
    """
    Load and return the leads CSV as a DataFrame.

    Returns:
        DataFrame with all leads, or an empty DataFrame if the file doesn't exist.
    """
    if not os.path.exists(CSV_FILE):
        print(f"File not found: {CSV_FILE}")
        return pd.DataFrame()

    df = pd.read_csv(CSV_FILE, dtype=str, encoding="utf-8-sig")
    print(f"Loaded {len(df)} rows from {CSV_FILE}")
    return df


# ---------------------------------------------------------------------------
# Quick test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    sample_data = [
        {"name": "КРОК",       "website": "https://www.croc.ru",      "email": "info@croc.ru"},
        {"name": "Kaspersky",  "website": "https://www.kaspersky.ru", "email": "press@kaspersky.com"},
        {"name": "Контур",     "website": "https://www.kontur.ru",    "email": "support@kontur.ru"},
        {"name": "КРОК",       "website": "https://www.croc.ru",      "email": "info@croc.ru"},   # duplicate
    ]

    save_to_csv(sample_data)

    print("\n--- leads.csv preview ---")
    df = load_from_csv()
    print(df.to_string(index=False))