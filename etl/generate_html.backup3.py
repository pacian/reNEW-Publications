# etl/generate_html.py
import json
from jinja2 import Template
from datetime import datetime
from collections import Counter
import os

def generate_html():
    with open("output/publications.json", encoding="utf-8") as f:
        data = json.load(f)

    # Check for skipped entries
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

    data.sort(key=parse_date, reverse=True)

    for pub in data:
        try:
            dt = parse_date(pub)
            pub["formatted_date"] = dt.strftime("%B %Y")
            pub["year_only"] = dt.year
        except:
            pub["formatted_date"] = pub.get("date", "")
            pub["year_only"] = ""

    year_counts = Counter(pub["year_only"] for pub in data if pub["year_only"])
    years = sorted(year_counts.keys(), reverse=True)
    last_export = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    template = Template("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>reNEW Publications – Copenhagen Node</title>
      <style>
        :root {
          --bg: #ffffff;
          --text: #052d4f;
          --input-bg: #ffffff;
        }
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: var(--bg); color: var(--text); }
        header { background-color: #000; color: #fff; padding: 2em; text-align: center; position: relative; }
        header img { height: 72px; position: absolute; left: 2em; top: 1.5em; }
        .container { padding: 2em; }
        .source-note { font-weight: bold; margin-bottom: 1em; }
        .warning { background: #ffdddd; color: #a00; padding: 1em; border: 1px solid #a00; margin-bottom: 1em; }
        label, select, input, button { margin-right: 1em; margin-bottom: 1em; padding: 0.5em; font-size: 1em; background-color: var(--input-bg); color: inherit; border: 1px solid #ccc; }
        table { width: 100%; border-collapse: collapse; margin-top: 1em; }
        th, td { border: 1px solid #ccc; padding: 8px; text-align: left; vertical-align: top; }
        th { background-color: #f0f0f0; }
        footer { text-align: center; padding: 2em; color: #666; font-size: 0.9em; }
        .match-count { margin: 1em 0; font-weight: bold; }
        .theme-toggle { position: absolute; top: 1.5em; right: 1.5em; padding: 0.4em 0.8em; }
        @media (max-width: 768px) {
          header h1 { font-size: 1.4em; }
          .container { padding: 1em; }
          table, th, td { font-size: 0.9em; }
        }
      </style>
      <script>
        function resetFilters() {
          document.getElementById("yearFilter").value = "all";
          document.getElementById("sourceFilter").value = "all";
          document.getElementById("keywordInput").value = "";
          filterAll();
        }

        function highlightMatch(text, keyword) {
          if (!keyword) return text;
          const regex = new RegExp("(" + keyword + ")", "gi");
          return text.replace(regex, "<mark>$1</mark>");
        }

        function toggleColumn(index, visible) {
          const rows = document.querySelectorAll("table tr");
          rows.forEach(row => {
            if (row.cells.length > index) {
              row.cells[index].style.display = visible ? "" : "none";
            }
          });
        }

        function toggleTheme() {
          const html = document.documentElement;
          const isDark = html.style.getPropertyValue('--bg') === '#121212';
          html.style.setProperty('--bg', isDark ? '#ffffff' : '#121212');
          html.style.setProperty('--text', isDark ? '#052d4f' : '#dddddd');
          html.style.setProperty('--input-bg', isDark ? '#ffffff' : '#333333');
        }

        function filterAll() {
          const year = document.getElementById("yearFilter").value;
          const source = document.getElementById("sourceFilter").value;
          const keyword = document.getElementById("keywordInput").value.toLowerCase();
          const rows = document.querySelectorAll("tbody tr");
          let visibleCount = 0;

          rows.forEach(row => {
            const y = row.getAttribute("data-year");
            const s = row.getAttribute("data-source");
            const cells = row.querySelectorAll("td");
            let keywordMatch = false;

            cells.forEach(cell => {
              const text = cell.textContent || cell.innerText;
              if (keyword && text.toLowerCase().includes(keyword)) {
                keywordMatch = true;
                cell.innerHTML = highlightMatch(text, keyword);
              } else {
                cell.innerHTML = text;
              }
            });

            const show = (year === "all" || y === year) && (source === "all" || s === source) && (keyword === "" || keywordMatch);
            row.style.display = show ? "" : "none";
            if (show) visibleCount++;
          });

          document.getElementById("matchCount").textContent = `Showing ${visibleCount} of ${rows.length} results`;
        }
      </script>
    </head>
    <body>
      <header>
        <img src="/assets/logo.png" alt="reNEW Logo">
        <h1>reNEW Publications – Copenhagen Node</h1>
        <button class="theme-toggle" onclick="toggleTheme()">Toggle Theme</button>
      </header>
      <div class="container">
        <div class="source-note">
          <strong>Data source: EuropePMC | Filter: reNEW – CPH / UCPH / University of Copenhagen / DanStem</strong>
        </div>

        {% if skipped_count > 0 %}
        <div class="warning">
          ⚠ {{ skipped_count }} entries were skipped due to missing title or date.
        </div>
        {% endif %}

        <label for="yearFilter">Filter by Year:</label>
        <select id="yearFilter" onchange="filterAll()">
          <option value="all">All years ({{ data|length }})</option>
          {% for y in years %}<option value="{{ y }}">{{ y }} ({{ year_counts[y] }})</option>{% endfor %}
        </select>

        <label for="sourceFilter">Filter by Source:</label>
        <select id="sourceFilter" onchange="filterAll()">
          <option value="all">All sources</option>
          <option value="EuropePMC">EuropePMC</option>
          <option value="Excel">Excel</option>
        </select>

        <label for="keywordInput">Search:</label>
        <input type="text" id="keywordInput" placeholder="Enter keyword..." onkeyup="filterAll()">
        <button onclick="resetFilters()">Reset</button>

        <div class="match-count" id="matchCount">Showing {{ data|length }} of {{ data|length }} results</div>

        <fieldset>
          <legend>Toggle Columns:</legend>
          <label><input type="checkbox" checked onchange="toggleColumn(0, this.checked)"> Authors</label>
          <label><input type="checkbox" checked onchange="toggleColumn(1, this.checked)"> Title</label>
          <label><input type="checkbox" checked onchange="toggleColumn(2, this.checked)"> Journal</label>
          <label><input type="checkbox" checked onchange="toggleColumn(3, this.checked)"> Pub Date</label>
          <label><input type="checkbox" checked onchange="toggleColumn(4, this.checked)"> DOI</label>
          <label><input type="checkbox" checked onchange="toggleColumn(5, this.checked)"> Source</label>
        </fieldset>

        <table>
          <thead>
            <tr>
              <th>Authors</th>
              <th>Title</th>
              <th>Journal</th>
              <th>Pub Date</th>
              <th>DOI</th>
              <th>Source</th>
            </tr>
          </thead>
          <tbody>
            {% for pub in data %}
              <tr data-year="{{ pub.year_only }}" data-source="{{ pub.source }}">
                <td>{{ pub.authors }}</td>
                <td>{{ pub.title }}</td>
                <td>{{ pub.journal }}</td>
                <td>{{ pub.formatted_date }}</td>
                <td>{% if pub.doi %}<a href="https://doi.org/{{ pub.doi }}" target="_blank">{{ pub.doi }}</a>{% endif %}</td>
                <td>{{ pub.source }}</td>
              </tr>
            {% endfor %}
          </tbody>
        </table>
      </div>
      <footer>
        &copy; {{ now.year }} Novo Nordisk Foundation Center for Stem Cell Medicine – reNEW Copenhagen.<br>
        Last export: {{ last_export }}
      </footer>
    </body>
    </html>
    """)

    rendered = template.render(
        data=data,
        now=datetime.now(),
        years=years,
        year_counts=year_counts,
        last_export=last_export,
        skipped_count=skipped_count
    )

    with open("output/output.html", "w", encoding="utf-8") as f:
        f.write(rendered)

if __name__ == "__main__":
    generate_html()
