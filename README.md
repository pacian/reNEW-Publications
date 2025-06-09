# reNEW Publications Registry – Copenhagen Node

This project harvests publications for the **Novo Nordisk Foundation Center for Stem Cell Medicine – reNEW Copenhagen**, formats them into a human-readable HTML publication viewer, and supports multi-source data curation (EuropePMC, Excel).

---

## 🚀 Key Features

* Multi-source publication harvesting (EuropePMC + Excel + OpenAlex)
* Responsive HTML output with year filtering and keyword search
* Column visibility toggle and dark/light theme switch
* CSV export and downloadable publications list
* Backup scripts and outputs for safety
* Markdown-friendly output for downstream integration
* Netdata monitoring integration at `/netdata` with optional authentication

---

## 📁 Directory Structure

```
renew-publications/
├── etl/
│   ├── europepmc.py                # Fetch publications from EuropePMC
│   ├── europepmc_backup.py         # Backup of EuropePMC fetcher
│   ├── import_csv.py               # Import publications from Excel
│   ├── import_openalex.py          # Harvest OpenAlex structured metadata
│   ├── export_csv.py               # Merge and export final CSV
│   ├── generate_html.py            # Render interactive HTML table
├── output/
│   ├── output.html                 # Final publication view
│   ├── publications.csv            # CSV export for download
│   ├── publications.json           # Consolidated JSON metadata
│   └── skipped_entries.json        # Logging of skipped or malformed entries
├── reNEW_PUB.xlsx                  # Excel source file (manually uploaded)
├── run_pipeline.py                 # One-line ETL orchestrator
├── assets/                         # Branding assets (e.g., logo.png)
├── README.md
├── requirements.txt
└── venv/                           # Python virtual environment
```

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

# Full Automation
Run the entire ETL pipeline with:
```bash
python run_pipeline.py

# Or run components manually
python etl/import_csv.py
python etl/import_openalex.py
python etl/export_csv.py
python etl/generate_html.py

# Deploy output
sudo cp output/output.html /var/www/renew-publications/index.html
sudo cp output/publications.csv /var/www/renew-publications/publications.csv
```

---

## 🔐 Monitoring (Optional)

Netdata is served at [https://publication.renew-platforms.dk/netdata](https://publication.renew-platforms.dk/netdata). Access may be protected with a username and password defined in `/etc/nginx/.htpasswd`.

---

© 2025 Novo Nordisk Foundation Center for Stem Cell Medicine – reNEW Copenhagen
