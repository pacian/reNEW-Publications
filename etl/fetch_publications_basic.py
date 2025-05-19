# fetch_publications_basic.py
import requests
import json
import os

FROM_DATE = "2021-05-01"
TO_DATE = "2025-05-01"
OUTPUT_FILE = "../output/publications.json"

QUERY_VARIANTS = [
    # 1. Exact institutional name with no affiliation filtering
    '"Novo Nordisk Foundation Center for Stem Cell Medicine" AND FIRST_PDATE:[{FROM_DATE} TO {TO_DATE}]',

    # 2. Use AFF field only
    'AFF:"Novo Nordisk Foundation Center for Stem Cell Medicine" AND FIRST_PDATE:[{FROM_DATE} TO {TO_DATE}]',

    # 3. Broad query with institution keyword
    '"Stem Cell Medicine" AND AFF:"University of Copenhagen" AND FIRST_PDATE:[{FROM_DATE} TO {TO_DATE}]',
]

def fetch_publications():
    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    page_size = 1000
    records = {}

    for variant in QUERY_VARIANTS:
        query = variant.format(FROM_DATE=FROM_DATE, TO_DATE=TO_DATE)
        print(f"\n🔎 Trying query: {query}")
        page = 1
        total_new = 0

        while True:
            params = {
                "query": query,
                "format": "json",
                "pageSize": page_size,
                "page": page,
                "sort": "FIRST_PDATE desc"
            }
            try:
                r = requests.get(url, params=params, timeout=20)
                r.raise_for_status()
                results = r.json().get("resultList", {}).get("result", [])
            except Exception as e:
                print(f"❌ Page {page} failed: {e}")
                break

            if not results:
                print(f"✅ No more records for this query on page {page}")
                break

            new = 0
            for record in results:
                pmid = record.get("id")
                if pmid and pmid not in records:
                    records[pmid] = {
                        "pmid": pmid,
                        "title": record.get("title"),
                        "authors": record.get("authorString"),
                        "journal": record.get("journalTitle"),
                        "year": record.get("pubYear"),
                        "date": record.get("firstPublicationDate") or record.get("pubYear"),
                        "doi": record.get("doi"),
                        "has_data_links": record.get("hasDataLinks") == "Y"
                    }
                    new += 1

            print(f"→ Page {page}: {len(results)} results, {new} new")
            total_new += new
            page += 1

        print(f"✅ Query completed with {total_new} new records.\n")

        if total_new > 0:
            break  # Stop at first query that returns results

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(list(records.values()), f, indent=2, ensure_ascii=False)

    print(f"💾 Final saved count: {len(records)} unique records → {OUTPUT_FILE}")

if __name__ == "__main__":
    fetch_publications()
