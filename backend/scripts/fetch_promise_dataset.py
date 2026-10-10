"""Script to download and parse the PROMISE NFR requirement dataset."""
import os
import re
import io
import sys
import urllib.request
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data")
CSV_PATH = os.path.join(DATA_DIR, "promise_nfr.csv")

PROMISE_URLS = [
    ("https://raw.githubusercontent.com/AleksandarMitrevski/se-requirements-classification/master/0-datasets/PROMISE_exp/PROMISE_exp.arff", "arff"),
]


def parse_arff_to_dataframe(arff_text: str) -> pd.DataFrame:
    """Parse ARFF format text into a pandas DataFrame."""
    rows = []
    in_data = False

    for line in arff_text.splitlines():
        l = line.strip()
        if not l or l.startswith("%"):
            continue
        if l.upper().startswith("@DATA"):
            in_data = True
            continue

        if in_data:
            parts = l.rsplit(",", 1)
            if len(parts) == 2:
                label = parts[1].strip()
                text_part = parts[0].strip()
                if "," in text_part:
                    text_part = text_part.split(",", 1)[1].strip()
                text_part = text_part.strip("'\" \t")
                if len(text_part) > 5:
                    rows.append({"text": text_part, "label": label})

    return pd.DataFrame(rows)


def fetch_promise_dataset() -> str:
    """Download and prepare PROMISE NFR dataset."""
    os.makedirs(DATA_DIR, exist_ok=True)

    if os.path.exists(CSV_PATH) and os.path.getsize(CSV_PATH) > 500:
        print(f"PROMISE NFR dataset ready at: {CSV_PATH}")
        return CSV_PATH

    print("Attempting to download PROMISE NFR dataset from remote repositories...")
    download_success = False

    for url, file_type in PROMISE_URLS:
        try:
            print(f"Fetching from {url}...")
            req = urllib.request.Request(
                url, headers={"User-Agent": "Mozilla/5.0 (Software Engineering Assistant)"}
            )
            with urllib.request.urlopen(req, timeout=15) as response:
                content_bytes = response.read()
                content_str = content_bytes.decode("utf-8", errors="ignore")

                if len(content_str) > 500:
                    if file_type == "arff":
                        df = parse_arff_to_dataframe(content_str)
                    else:
                        df = pd.read_csv(io.StringIO(content_str))

                    if len(df) > 50:
                        df.to_csv(CSV_PATH, index=False)
                        print(f"Successfully downloaded and saved PROMISE NFR dataset ({len(df)} records) to {CSV_PATH}")
                        download_success = True
                        break
        except Exception as e:
            print(f"Could not download from {url}: {e}")

    if not download_success:
        print(
            "\n[ERROR] The PROMISE NFR dataset could not be downloaded due to network connectivity or remote URL unavailability.\n"
            "Per engineering guidelines, synthetic data has NOT been generated.\n"
            "Please place a valid PROMISE NFR CSV file at: " + CSV_PATH
        )
        return ""

    return CSV_PATH


if __name__ == "__main__":
    fetch_promise_dataset()
