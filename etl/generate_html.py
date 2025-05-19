# etl/generate_html.py
import json
from jinja2 import Template
from datetime import datetime
from collections import Counter

def generate_html():
    with open("output/publications.json", encoding="utf-8") as f:
        data = json.load(f)

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
        body {
          font-family: Arial, sans-serif;
          margin: 0;
          padding: 0;
          background-color: var(--bg);
          color: var(--text);
        }
        header {
          background-color: #000000;
          padding: 2em;
          display: flex;
          align-items: center;
          justify-content: center;
          position: relative;
        }
        header img {
          height: 72px;
          position: absolute;
          left: 2em;
        }
        header h1 {
          margin: 0;
          font-size: 2em;
          color: #ffffff;
          text-align: center;
        }
        .container {
          padding: 2em;
        }
        .source-note {
          font-weight: bold;
          font-size: 0.95em;
          color: #333;
        }
        input, select, button {
          margin: 0.5em 1em 0.5em 0;
          padding: 0.5em;
          font-size: 1em;
          color: inherit;
          background-color: var(--input-bg);
          border: 1px solid #ccc;
        }
        button {
          cursor: pointer;
        }
        table {
          border-collapse: collapse;
          width: 100%;
        }
        th, td {
          border: 1px solid #ccc;
          padding: 8px;
          text-align: left;
          vertical-align: top;
        }
        th {
          background-color: #f0f0f0;
        }
        a {
          color: #00a0c6;
          text-decoration: none;
        }
        a:hover {
          text-decoration: underline;
        }
        mark {
          background-color: yellow;
        }
        .match-count {
          margin: 1em 0;
          font-weight: bold;
        }
        .theme-toggle {
          position: absolute;
          top: 1.5em;
          right: 1.5em;
          padding: 0.4em 0.8em;
        }
        footer {
          margin-top: 3em;
          padding: 1em;
          text-align: center;
          font-size: 0.9em;
          color: #666;
        }
        @media (max-width: 768px) {
          header h1 {
            font-size: 1.4em;
          }
          .container {
            padding: 1em;
          }
          table, th, td {
            font-size: 0.9em;
          }
        }
      </style>
      <script>
        function resetFilters() {
          document.getElementById("yearFilter").value = "all";
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

        function filterAll() {
          const year = document.getElementById("yearFilter").value;
          const keyword = document.getElementById("keywordInput").value.toLowerCase();
          const rows = document.querySelectorAll("tbody tr");
          let visibleCount = 0;

          rows.forEach(row => {
            const yearMatch = year === "all" || row.getAttribute("data-year") === year;
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

            const show = yearMatch && (keyword === "" || keywordMatch);
            row.style.display = show ? "" : "none";
            if (show) visibleCount++;
          });

          document.getElementById("matchCount").textContent = "Showing " + visibleCount + " of " + rows.length + " results";
        }

        function toggleTheme() {
          const html = document.documentElement;
          const isDark = html.style.getPropertyValue('--bg') === '#121212';
          html.style.setProperty('--bg', isDark ? '#ffffff' : '#121212');
          html.style.setProperty('--text', isDark ? '#052d4f' : '#dddddd');
          html.style.setProperty('--input-bg', isDark ? '#ffffff' : '#333333');
        }

        if ('serviceWorker' in navigator) {
          window.addEventListener('load', () => {
            navigator.serviceWorker.register('/sw.js');
          });
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

        <a href="/publications.csv" download><strong>⬇ Download CSV</strong></a><br><br>

        <label for="yearFilter">Filter by Year:</label>
        <select id="yearFilter" onchange="filterAll()">
          <option value="all">All years ({{ data | length }})</option>
          {% for y in years %}
            <option value="{{ y }}">{{ y }} ({{ year_counts[y] }})</option>
          {% endfor %}
        </select>

        <label for="keywordInput">Search:</label>
        <input type="text" id="keywordInput" placeholder="Enter keyword..." onkeyup="filterAll()">

        <button onclick="resetFilters()">Reset</button>

        <div class="match-count" id="matchCount">Showing {{ data | length }} of {{ data | length }} results</div>

        <fieldset>
          <legend>Toggle Columns:</legend>
          <label><input type="checkbox" checked onchange="toggleColumn(0, this.checked)"> Authors</label>
          <label><input type="checkbox" checked onchange="toggleColumn(1, this.checked)"> Title</label>
          <label><input type="checkbox" checked onchange="toggleColumn(2, this.checked)"> Journal</label>
          <label><input type="checkbox" checked onchange="toggleColumn(3, this.checked)"> Pub Date</label>
          <label><input type="checkbox" checked onchange="toggleColumn(4, this.checked)"> DOI</label>
        </fieldset>

        <table>
          <thead>
            <tr>
              <th>Authors</th>
              <th>Publication Title</th>
              <th>Journal</th>
              <th>Pub Date</th>
              <th>Article DOI</th>
            </tr>
          </thead>
          <tbody>
            {% for pub in data %}
              <tr data-year="{{ pub.year_only }}">
                <td>{{ pub.authors or '' }}</td>
                <td>{{ pub.title or '' }}</td>
                <td>{{ pub.journal or '' }}</td>
                <td>{{ pub.formatted_date or '' }}</td>
                <td>{% if pub.doi %}<a href="https://doi.org/{{ pub.doi }}" target="_blank">{{ pub.doi }}</a>{% endif %}</td>
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
        last_export=last_export
    )

    with open("output/output.html", "w", encoding="utf-8") as f:
        f.write(rendered)

if __name__ == "__main__":
    generate_html()
