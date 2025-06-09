#!/usr/bin/env python3

import subprocess
import os
import sys
from pathlib import Path

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

    # Step 1: Import CSV (Excel converted)
    run_script(str(etl_dir / "import_csv.py"))

    # Step 2: Import OpenAlex
    run_script(str(etl_dir / "import_openalex.py"))

    # Step 3: Export to CSV
    run_script(str(etl_dir / "export_csv.py"))

    # Step 4: Generate HTML
    run_script(str(etl_dir / "generate_html.py"))

    # Step 5: Deploy to web server
    print("📂 Deploying output to /var/www/renew-publications")
    output_html = output_dir / "output.html"
    output_csv = output_dir / "publications.csv"

    if not output_html.exists() or not output_csv.exists():
        print("❌ Output files not found. Make sure all ETL steps completed successfully.")
        sys.exit(1)

    os.makedirs(web_root, exist_ok=True)
    subprocess.run(["cp", str(output_html), str(web_root / "index.html")], check=True)
    subprocess.run(["cp", str(output_csv), str(web_root / "publications.csv")], check=True)

    print("✅ Deployment complete.")
    print("🌐 Visit https://publication.renew-platforms.dk to view the results.")

if __name__ == "__main__":
    main()
