"""Optional source re-download. Never replaces an existing original.
The original CSV and downloaded ZIP are already included in this package.
"""
from pathlib import Path
import datetime
import hashlib
import json
import urllib.request
import zipfile
import io

ROOT = Path(__file__).resolve().parents[1]
REF = "alitaqishah/ai-jobs-market-2025-2026-salaries"
URL = "https://www.kaggle.com/api/v1/datasets/download/" + REF + "?datasetVersionNumber=1"
EXPECTED = "6ae7bc7bf724250cd8c977f86b620128318070a23cb0b17340e58d2321f7864e"
if __name__ == "__main__":
    target = ROOT / "raw/ai_jobs_market_2025_2026.csv"
    if target.exists():
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual != EXPECTED:
            raise SystemExit("Existing raw CSV differs from the pinned source. It was not replaced.")
        print("Original version 1 CSV is already present and its SHA-256 matches. No download needed.")
    else:
        with urllib.request.urlopen(URL, timeout=60) as response:
            data = response.read()
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            csv_data = archive.read("ai_jobs_market_2025_2026.csv")
        if hashlib.sha256(csv_data).hexdigest() != EXPECTED:
            raise SystemExit("Downloaded version differs from the pinned original. No files written.")
        target.parent.mkdir(exist_ok=True)
        target.write_bytes(csv_data)
        (target.parent / "ai_jobs_market_2025_2026_original.zip").write_bytes(data)
        print("Downloaded and verified the original CSV and ZIP.")
