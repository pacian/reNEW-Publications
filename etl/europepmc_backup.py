# etl/europepmc.py
import requests
import json

FROM_DATE = "2024-06-01"
TO_DATE = "2025-05-01"
OUTPUT_PATH = "output/publications.json"

def fetch_publications():
    query = (
        '"Novo Nordisk Foundation Center for Stem Cell Medicine" AND '
        '(AFF:CPH OR AFF:UCPH OR AFF:"University of Copenhagen") AND '
        f'FIRST_PDATE:[{FROM_DATE} TO {TO_DATE}]'
    )
    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    params = {
        "query": query,
        "format": "json",
        "pageSize": 1000
    }

    results = []
    print("🔎 Searching EuropePMC...")
    response = requests.get(url, params=params)
    data = response.json()

    for record in data.get("resultList", {}).get("result", []):
        results.append({
            "title": record.get("title"),
            "authors": record.get("authorString"),
            "journal": record.get("journalTitle"),
            "year": record.get("pubYear"),
            "date": record.get("firstPublicationDate") or record.get("pubYear"),
            "doi": record.get("doi"),
        })

    print(f"✅ Found {len(results)} publications")
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    fetch_publications()
