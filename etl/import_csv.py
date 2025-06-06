# etl/import_csv.py
import json
import pandas as pd
from datetime import datetime

EXCEL_FILE = "/root/renew-publications/reNEW_PUB.xlsx"
JSON_FILE = "output/publications.json"
SKIP_LOG = "output/skipped_entries.json"

def normalize_excel_row(row):
    def safe_str(value):
        return str(value).strip() if pd.notna(value) else ""

    return {
        "title": safe_str(row.get("Title of the contribution in original language", "")),
        "authors": safe_str(row.get("Contributors-5", "")),
        "journal": safe_str(row.get("Journal > Journal-6", "")),
        "date": convert_date(row.get("Current publication status > Date-3", "")),
        "doi": clean_doi(row.get("Electronic version(s) of this work > DOI (Digital Object Identifier)-12", "")),
        "source": "Excel"
    }

def convert_date(raw_date):
    try:
        if isinstance(raw_date, datetime):
            return raw_date.strftime("%Y-%m-%d")
        return datetime.strptime(str(raw_date), "%d/%m/%Y").strftime("%Y-%m-%d")
    except:
        return ""

def clean_doi(doi):
    if isinstance(doi, str) and doi.startswith("10."):
        return doi.strip()
    return ""

def load_existing():
    try:
        with open(JSON_FILE, encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def deduplicate(items):
    seen = set()
    unique = []
    for item in items:
        key = item.get("doi") or (item.get("title", "").lower(), item.get("date", ""))
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique

def main():
    print(f"📥 Loading Excel from {EXCEL_FILE}")
    existing = load_existing()

    df = pd.read_excel(EXCEL_FILE)
    excel_data = []
    skipped = []

    for _, row in df.iterrows():
        norm = normalize_excel_row(row)
        if norm["title"] and norm["date"]:
            excel_data.append(norm)
        else:
            skipped.append(norm)

    print(f"🧹 Normalized {len(excel_data)} Excel records, Skipped: {len(skipped)}")

    merged = deduplicate(existing + excel_data)

    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)

    with open(SKIP_LOG, "w", encoding="utf-8") as f:
        json.dump(skipped, f, indent=2, ensure_ascii=False)

    print(f"✅ Imported {len(excel_data)} Excel entries, merged total: {len(merged)}")
    print(f"⚠️ Skipped {len(skipped)} entries (see output/skipped_entries.json)")

if __name__ == "__main__":
    main()
