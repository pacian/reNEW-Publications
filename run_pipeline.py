# run_pipeline.py
import os
import sys
import subprocess
from pathlib import Path
import shutil

# Direct function imports
from etl.import_csv import import_from_excel
from etl.export_csv import export_to_csv
from etl.generate_html import generate_html
from etl.europepmc import fetch_publications

def run_script(script_path):
    print(f"🔄 Running: {script_path}")
    result = subprocess.run([sys.executable, script_path])
    if result.returncode != 0:
        print(f"❌ Error running {script_path}")
        sys.exit(1)
    print(f"✅ Completed: {script_path}")

def main():
    project_root = Path(__file__).resolve().parent
    etl_dir = project_root / "etl"
    output_dir = project_root / "output"
    web_root = Path("/var/www/renew-publications")

    print("🚀 Starting reNEW publication pipeline...")

    # Step 1: Import CSV (Excel)
    print("📥 Importing Excel...")
    import_from_excel()

    # Step 2: Import OpenAlex
    run_script(str(etl_dir / "import_openalex.py"))

    # Step 3: Fetch from EuropePMC
    print("🔍 Fetching from EuropePMC...")
    fetch_publications()

    # Step 4: Export combined data to CSV
    print("📤 Exporting to CSV...")
    export_to_csv()

    # Step 5: Generate HTML
    print("🧾 Generating HTML...")
    generate_html()

    # Step 6: Deploy to web root
    print("📂 Deploying output to /var/www/renew-publications")
    os.makedirs(web_root, exist_ok=True)

    output_html = output_dir / "output.html"
    output_csv = output_dir / "publications.csv"

    if not output_html.exists() or not output_csv.exists():
        print("❌ Output files missing. ETL step may have failed.")
        sys.exit(1)

    shutil.copy(output_html, web_root / "index.html")
    shutil.copy(output_csv, web_root / "publications.csv")

    print("✅ Pipeline complete.")
    print("🌐 View live at: https://publication.renew-platforms.dk")

if __name__ == "__main__":
    main()
