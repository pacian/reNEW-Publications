# reNEW Publications – Copenhagen Node

This project harvests publications for the **Novo Nordisk Foundation Center for Stem Cell Medicine – reNEW**, formats them into a human-readable HTML publication viewer, and supports multi-source data curation (EuropePMC, Excel).

---

## 📁 Project Structure

renew-publications/
├── etl/
│ ├── europepmc.py
│ ├── import_csv.py
│ ├── export_csv.py
│ ├── generate_html.py
│ └── generate_html.backup*.py
├── output/
│ ├── publications.json
│ ├── publications.csv
│ ├── output.html
│ └── output.backup*.html
├── assets/
│ ├── logo.png
│ └── badges/
├── run_pipeline.py
├── sw.js
├── venv/
└── reNEW_PUB.xlsx



## 🚀 Key Features
- EuropePMC and Excel harvesting
- Responsive HTML output
- Year and source filters
- Keyword search and reset button
- Column toggle and theme switcher
- CSV export and upload (future)
- Year group headers
- Source badges

---

## 🔗 Access the Viewer
[https://publication.renew-platforms.dk](https://publication.renew-platforms.dk)

---

© Novo Nordisk Foundation Center for Stem Cell Medicine – reNEW Copenhagen
