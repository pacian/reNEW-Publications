# ~/renew-publications/etl/generate_html.py
import json
from jinja2 import Template
from datetime import datetime
from collections import Counter
import os

def generate_html():
    with open("output/publications.json", encoding="utf-8") as f:
        data = json.load(f)

    skipped_count = 0
    if os.path.exists("output/skipped_entries.json"):
        with open("output/skipped_entries.json", encoding="utf-8") as f:
            skipped = json.load(f)
            skipped_count = len(skipped)

    def parse_date(item):
        try:
            return datetime.strptime(item.get("date", ""), "%Y-%m-%d")
        except:
            try:
                return datetime.strptime(item.get("date", ""), "%Y")
            except:
                return datetime.min

    data = [d for d in data if parse_date(d) != datetime.min and "AuthorExternal person" not in d.get("authors", "")]
    data.sort(key=parse_date, reverse=True)

    for pub in data:
        dt = parse_date(pub)
        pub["formatted_date"] = dt.strftime("%B %Y")
        pub["year_only"] = dt.year

    year_counts = Counter(pub["year_only"] for pub in data if pub["year_only"])
    years = sorted(year_counts.keys(), reverse=True)
    journals = sorted(set(pub.get("journal", "") for pub in data if pub.get("journal")))
    last_export = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    template = Template("""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>reNEW Publication Registry – Copenhagen Node</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --primary: #007C7C;
      --accent: #00A9A5;
      --light-bg: #f2f7f5;
      --dark-bg: #121212;
      --dark-border: #333;
      --dark-text: #ddd;
    }

    body {
      font-family: 'Inter', sans-serif;
      margin: 0;
      background: var(--light-bg);
      color: #052d4f;
    }

    body.dark {
      background: var(--dark-bg);
      color: var(--dark-text);
    }

    header {
      display: flex;
      align-items: center;
      background: white;
      padding: 1.5rem;
      box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }

    body.dark header {
      background: #1e1e1e;
    }

    header img {
      height: 120px;
    }

    header h1 {
      font-size: 2.5rem;
      margin-left: 2rem;
      color: var(--primary);
    }

    .theme-toggle {
      margin-left: auto;
      padding: 0.5rem 1rem;
      background: #eee;
      border-radius: 6px;
      cursor: pointer;
      border: 1px solid #ccc;
    }

    body.dark .theme-toggle {
      background: #333;
      color: #fff;
    }

    main {
      max-width: 1300px;
      margin: 2rem auto;
      background: white;
      padding: 2rem;
      border-radius: 12px;
    }

    body.dark main {
      background: #1e1e1e;
    }

    .filter-bar {
      display: flex;
      flex-wrap: wrap;
      gap: 1rem;
      margin-bottom: 1rem;
    }

    .field-filter {
      margin-bottom: 1rem;
    }

    select, input {
      padding: 0.5rem;
      font-size: 1rem;
    }

    .match-count {
      margin: 1rem 0;
      font-weight: bold;
    }

    .csv-download {
      display: inline-block;
      margin-bottom: 1rem;
      padding: 0.6rem 1.2rem;
      background-color: var(--primary);
      color: white;
      text-decoration: none;
      border-radius: 6px;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 1rem;
      table-layout: fixed;
    }

    th, td {
      padding: 0.75rem;
      border: 1px solid #ccc;
      word-wrap: break-word;
      vertical-align: top;
    }

    th:nth-child(1), td:nth-child(1) { width: 20%; }
    th:nth-child(2), td:nth-child(2) { width: 30%; }
    th:nth-child(3), td:nth-child(3) { width: 15%; }
    th:nth-child(4), td:nth-child(4) { width: 10%; }
    th:nth-child(5), td:nth-child(5) { width: 15%; }
    th:nth-child(6), td:nth-child(6) { width: 10%; }

    .toggle-columns {
      border: 1px solid #ccc;
      padding: 1rem;
      margin: 1rem 0;
      border-radius: 6px;
      display: flex;
      gap: 1rem;
    }

    footer {
      text-align: center;
      font-size: 0.9rem;
      color: #777;
      margin-top: 2rem;
    }

    input.column-filter {
      width: 95%;
      margin-top: 0.3rem;
    }
  </style>
</head>
<body>
  <header>
    <img src="/assets/logo.png" alt="reNEW Logo">
    <h1>reNEW Publication Registry – Copenhagen Node</h1>
    <button class="theme-toggle" onclick="toggleTheme()">Toggle Theme</button>
  </header>

  <main>
    {% if skipped_count > 0 %}
    <div style="color: red;"><strong>⚠ {{ skipped_count }} entries were skipped due to missing title or date.</strong></div>
    {% endif %}

    <a href="/publications.csv" class="csv-download">📥 Download CSV</a>

    <div class="filter-bar">
      <select id="fieldSelect">
        <option value="all">All Fields</option>
        <option value="title">Title</option>
        <option value="authors">Authors</option>
        <option value="journal">Journal</option>
        <option value="date">Pub Date</option>
        <option value="doi">DOI</option>
        <option value="source">Source</option>
      </select>
      <input type="text" id="keywordInput" placeholder="Enter keyword..." onkeyup="filterAll()">
      <select id="yearFilter" onchange="filterAll()">
        <option value="all">All Years ({{ data|length }})</option>
        {% for y in years %}<option value="{{ y }}">{{ y }} ({{ year_counts[y] }})</option>{% endfor %}
      </select>
      <select id="sourceFilter" onchange="filterAll()">
        <option value="all">All Sources</option>
        <option value="EuropePMC">EuropePMC</option>
        <option value="OpenAlex">OpenAlex</option>
        <option value="Excel">Excel</option>
      </select>
      <select id="journalFilter" onchange="filterAll()">
        <option value="all">All Journals</option>
        {% for j in journals %}<option value="{{ j }}">{{ j }}</option>{% endfor %}
      </select>
      <button onclick="resetFilters()">Reset</button>
    </div>

    <div class="toggle-columns">
      <label><input type="checkbox" checked onchange="toggleColumn(0, this.checked)"> Authors</label>
      <label><input type="checkbox" checked onchange="toggleColumn(1, this.checked)"> Title</label>
      <label><input type="checkbox" checked onchange="toggleColumn(2, this.checked)"> Journal</label>
      <label><input type="checkbox" checked onchange="toggleColumn(3, this.checked)"> Pub Date</label>
      <label><input type="checkbox" checked onchange="toggleColumn(4, this.checked)"> DOI</label>
      <label><input type="checkbox" checked onchange="toggleColumn(5, this.checked)"> Source</label>
    </div>

    <div class="match-count" id="matchCount">Showing {{ data|length }} of {{ data|length }} results</div>

    <table>
      <thead>
        <tr>
          <th>Authors<br><input class="column-filter" onkeyup="filterColumn(0, this.value)"></th>
          <th>Title<br><input class="column-filter" onkeyup="filterColumn(1, this.value)"></th>
          <th>Journal<br><input class="column-filter" onkeyup="filterColumn(2, this.value)"></th>
          <th>Pub Date<br><input class="column-filter" onkeyup="filterColumn(3, this.value)"></th>
          <th>DOI<br><input class="column-filter" onkeyup="filterColumn(4, this.value)"></th>
          <th>Source<br><input class="column-filter" onkeyup="filterColumn(5, this.value)"></th>
        </tr>
      </thead>
      <tbody>
        {% for pub in data %}
        <tr data-year="{{ pub.year_only }}" data-source="{{ pub.source }}" data-journal="{{ pub.journal }}">
          <td><strong>{{ pub.authors }}</strong></td>
          <td><strong>{{ pub.title }}</strong></td>
          <td>{{ pub.journal }}</td>
          <td>{{ pub.formatted_date }}</td>
          <td>{% if pub.doi %}<a href="https://doi.org/{{ pub.doi }}" target="_blank">{{ pub.doi }}</a>{% endif %}</td>
          <td>{{ pub.source }}</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>

    <p><strong>Data Source:</strong> EuropePMC | OpenAlex | CURIS (Excel)</p>

    <footer>
      <br>&copy; {{ now.year }} Novo Nordisk Foundation Center for Stem Cell Medicine – reNEW Copenhagen<br>
      Last export: {{ last_export }}
    </footer>
  </main>

  <script>
    function toggleTheme() {
      document.body.classList.toggle("dark");
    }

    function toggleColumn(index, show) {
      const rows = document.querySelectorAll("tr");
      rows.forEach(row => {
        if (row.cells.length > index) {
          row.cells[index].style.display = show ? "" : "none";
        }
      });
    }

    function resetFilters() {
      document.getElementById("yearFilter").value = "all";
      document.getElementById("sourceFilter").value = "all";
      document.getElementById("journalFilter").value = "all";
      document.getElementById("keywordInput").value = "";
      document.getElementById("fieldSelect").value = "all";
      filterAll();
    }

    function filterAll() {
      const keyword = document.getElementById("keywordInput").value.toLowerCase();
      const field = document.getElementById("fieldSelect").value;
      const year = document.getElementById("yearFilter").value;
      const source = document.getElementById("sourceFilter").value;
      const journal = document.getElementById("journalFilter").value.toLowerCase();
      const rows = document.querySelectorAll("tbody tr");
      let count = 0;

      rows.forEach(row => {
        const y = row.dataset.year;
        const s = row.dataset.source;
        const j = (row.dataset.journal || "").toLowerCase();
        const cells = row.querySelectorAll("td");
        let match = false;

        if (keyword.includes(":")) {
          const parts = keyword.split(":");
          const kfield = parts[0];
          const kvalue = parts[1];
          const map = {
            title: 1, author: 0, authors: 0, journal: 2, date: 3, pubdate: 3, doi: 4, source: 5
          };
          if (map[kfield] !== undefined && cells[map[kfield]].innerText.toLowerCase().includes(kvalue)) match = true;
        } else if (field === "all") {
          match = Array.from(cells).some(c => c.innerText.toLowerCase().includes(keyword));
        } else {
          const fieldIndex = { authors: 0, title: 1, journal: 2, date: 3, doi: 4, source: 5 }[field];
          if (fieldIndex !== undefined && cells[fieldIndex].innerText.toLowerCase().includes(keyword)) match = true;
        }

        const show =
          (year === "all" || y === year) &&
          (source === "all" || s === source) &&
          (journal === "all" || j.includes(journal)) &&
          (keyword === "" || match);

        row.style.display = show ? "" : "none";
        if (show) count++;
      });

      document.getElementById("matchCount").textContent = `Showing ${count} of ${rows.length} results`;
    }

    function filterColumn(index, value) {
      const rows = document.querySelectorAll("tbody tr");
      value = value.toLowerCase();
      rows.forEach(row => {
        const cell = row.cells[index];
        if (cell && !cell.innerText.toLowerCase().includes(value)) {
          row.style.display = "none";
        }
      });
    }
  </script>
</body>
</html>
""")

    rendered = template.render(
        data=data,
        now=datetime.now(),
        years=years,
        year_counts=year_counts,
        journals=journals,
        last_export=last_export,
        skipped_count=skipped_count
    )

    with open("output/output.html", "w", encoding="utf-8") as f:
        f.write(rendered)

if __name__ == "__main__":
    generate_html()
