#!/usr/bin/env python3
"""Refresh the profile's three original SVG activity cards."""
import argparse
import json
from datetime import date
from html import escape
from pathlib import Path
from urllib.request import Request, urlopen

STATS_URL = "https://streak-stats.demolab.com/?user=ayrzDev&type=json"

def short_date(value):
    return value.strftime("%b") + " " + str(value.day)

def date_range(start, end):
    first, last = date.fromisoformat(start), date.fromisoformat(end)
    if first > last:
        raise ValueError("Streak dates are reversed")
    left, right = short_date(first), short_date(last)
    if first.year != last.year:
        left += ", " + str(first.year)
    if last.year != date.today().year:
        right += ", " + str(last.year)
    return left + " – " + right

def card(label, value, detail):
    if type(value) is not int or value < 0:
        raise ValueError("Invalid activity value")
    number = f"{value:,}"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="250" height="120" viewBox="0 0 250 120" role="img" aria-labelledby="title desc">
<title id="title">{escape(label)}</title><desc id="desc">{escape(label + ': ' + number + '. ' + detail)}</desc>
<rect x=".5" y=".5" width="249" height="119" rx="10" fill="#111823" stroke="#2a3547"/>
<rect x="19" y="16" width="20" height="3" rx="1.5" fill="#8193ff"/>
<g font-family="Segoe UI,Arial,sans-serif">
<text x="18" y="58" font-size="32" font-weight="650" letter-spacing="-.8" fill="#eef3fa">{number}</text>
<text x="19" y="82" font-size="12" fill="#acbbcf">{escape(label)}</text>
<text x="19" y="103" font-size="10" fill="#74869f">{escape(detail)}</text>
</g></svg>
'''

def update(data, output_dir):
    first = data.get("firstContribution")
    detail = short_date(date.fromisoformat(first)) + ", " + str(date.fromisoformat(first).year) + " – present" if first else "GitHub contributions"
    definitions = [("contributions", "Total contributions", data["totalContributions"], detail)]
    for key, name, label in [("currentStreak", "current", "Current streak"), ("longestStreak", "longest", "Longest streak")]:
        streak = data[key]
        detail = date_range(streak["start"], streak["end"]) if streak["length"] else "No active streak"
        definitions.append((name, label, streak["length"], detail))
    rendered = {"stats-" + name + ".svg": card(label, value, detail) for name, label, value, detail in definitions}
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, svg in rendered.items():
        destination = output_dir / name
        if not destination.exists() or destination.read_text(encoding="utf-8") != svg:
            destination.write_text(svg, encoding="utf-8")
            print("Updated " + name)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-json", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[1] / "assets")
    args = parser.parse_args()
    if args.input_json:
        data = json.loads(args.input_json.read_text(encoding="utf-8"))
    else:
        request = Request(STATS_URL, headers={"Accept": "application/json", "User-Agent": "ayrzDev-profile-stats"})
        with urlopen(request, timeout=20) as response:
            data = json.load(response)
    update(data, args.output_dir)

if __name__ == "__main__":
    main()
