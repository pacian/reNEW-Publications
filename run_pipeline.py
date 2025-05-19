import os
from etl.europepmc import fetch_publications
from etl.generate_html import generate_html

os.makedirs("output", exist_ok=True)

fetch_publications()
print("📄 Generating HTML...")
generate_html()
print("✅ Done. See output/output.html")
