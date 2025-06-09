import requests
import json
import os

OUTPUT_FILE = "output/publications.json"
OPENALEX_API = "https://api.openalex.org/works"
QUERY = 'title.search:reNEW'
HEADERS = {"User-Agent": "mailto:richard.dennis@sund.ku.dk"}
AFFILIATION_KEYWORDS = ["CPH", "UCPH", "University of Copenhagen"]

def fetch_openalex():
    new_pubs = []
    per_page = 200
    cursor = "*"
    total_fetched = 0

    while True:
        url = f"{OPENALEX_API}?filter={QUERY}&per-page={per_page}&cursor={cursor}"
        print(f"Fetching: {url}")
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f"❌ Error fetching data: {response.status_code}")
            break
        data = response.json()
        results = data.get('results', [])
        total_fetched += len(results)
        for item in results:
            authors = "; ".join([auth.get('author', {}).get('display_name', '') for auth in item.get('authorships', [])])
            title = item.get('title', '').strip()
            journal = item.get('host_venue', {}).get('display_name', '')
            pub_date = item.get('publication_date', '')
            doi = item.get('doi')
            affiliations = " ".join([inst.get('display_name', '') for auth in item.get('authorships', []) for inst in auth.get('institutions', [])])
            if any(keyword.lower() in affiliations.lower() for keyword in AFFILIATION_KEYWORDS):
                pub = {
                    "Authors": authors,
                    "Title": title,
                    "Journal": journal,
                    "Pub Date": pub_date,
                    "DOI": doi,
                    "Source": "OpenAlex"
                }
                if title and pub_date:
                    new_pubs.append(pub)
        cursor = data.get('meta', {}).get('next_cursor')
        if not cursor:
            break

    print(f"✅ Fetched {total_fetched} OpenAlex publications (before filtering)")
    print(f"✅ Filtered to {len(new_pubs)} publications with CPH/UCPH/University of Copenhagen affiliation")
    return new_pubs

def merge_and_tag(new_pubs):
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            existing = json.load(f)
    else:
        existing = []

    openalex_titles = {pub['Title'].lower().strip() for pub in new_pubs}
    updated_existing = [e for e in existing if e.get('Title', '').lower().strip() not in openalex_titles]
    combined = updated_existing + new_pubs

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)

    print(f"✅ Added {len(new_pubs)} OpenAlex records. Total records: {len(combined)}")

if __name__ == "__main__":
    pubs = fetch_openalex()
    merge_and_tag(pubs)
