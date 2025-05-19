import json
import csv
import os

def export_csv():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    json_path = os.path.join(base_dir, "output", "publications.json")
    csv_path = os.path.join(base_dir, "output", "publications.csv")

    with open(json_path, encoding="utf-8") as f:
        records = json.load(f)

    with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Authors", "Title", "Journal", "Pub Date", "DOI", "Source"])

        for pub in records:
            writer.writerow([
                pub.get("authors", ""),
                pub.get("title", ""),
                pub.get("journal", ""),
                pub.get("date", ""),
                pub.get("doi", ""),
                pub.get("source", "EuropePMC")
            ])

    print(f"✅ CSV exported to: {csv_path}")

if __name__ == "__main__":
    export_csv()
