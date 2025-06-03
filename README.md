# reNEW Publications – Copenhagen Node

This project harvests publications for the **Novo Nordisk Foundation Center for Stem Cell Medicine – reNEW**, formats them into a human-readable HTML publication viewer, and supports multi-source data curation (EuropePMC, Excel).

---

## 🚀 Key Features
- Multi-source publication harvesting (EuropePMC + Excel)
- Responsive HTML output with filtering and search
- Column visibility toggle and dark/light theme switch
- CSV export and placeholder for CSV upload
- Year group headers for publication clarity
- Source badges for visual cues
- Backup scripts and outputs for safety

---

## 📌 Usage Instructions
```bash
# Clone the repository
git clone https://github.com/pacian/reNEW-Publications.git
cd reNEW-Publications

# Setup Python virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run ETL scripts
python etl/import_csv.py
python etl/export_csv.py
python etl/generate_html.py

# Deploy output
sudo cp output/output.html /var/www/renew-publications/index.html
sudo cp output/publications.csv /var/www/renew-publications/publications.csv

---

© Novo Nordisk Foundation Center for Stem Cell Medicine – reNEW Copenhagen
