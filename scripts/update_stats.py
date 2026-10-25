#!/usr/bin/env python3
"""Update individual GitHub profile stat cards from public contribution data."""

import argparse
import json
from datetime import date
from html import escape
from pathlib import Path
from urllib.request import Request, urlopen

STATS_URL = "https://streak-stats.demolab.com/?user=ayrzDev&type=json"


def date_range(start, end):
    first, last = date.fromisoformat(start), date.fromisoformat(end)
    if first > last:
        raise ValueError("Streak dates are reversed")
    left, right = first.strftime("%b %-d"), last.strftime("%b %-d")
    if first.year != last.year:
        left += f", {first.year}"
    if last.year != date.today().year:
        right += f", {last.year}"
    return f"{left} – {right}"


def card(label, value, detail, accent, background, icon):
    if type(value) is not int or value < 0:
        raise ValueError(f"Invalid value for {label}")
    number = f"{value:,}"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="177" height="100" viewBox="0 0 177 100" role="img" aria-labelledby="title desc">
  <title id="title">{escape(label)}</title>
  <desc id="desc">{escape(f'{label}: {number}. {detail}')}</desc>
  <rect x="0.5" y="0.5" width="176" height="99" rx="7" fill="{background}" stroke="#344255"/>
  <g font-family="Arial,Helvetica,sans-serif">
    <text x="14" y="35" fill="{accent}" font-size="23">{icon}</text>
    <text x="61" y="36" fill="{accent}" font-size="23" font-weight="700">{number}</text>
    <text x="14" y="62" fill="#dbe4ee" font-size="12">{escape(label)}</text>
    <text x="14" y="79" fill="{accent}" font-size="10">{escape(detail)}</text>
  </g>
  <path d="M12 95 165 82" fill="none" stroke="{accent}" stroke-width="2" stroke-linecap="round"/>
</svg>
'''


def update(data, output_dir):
    first = data.get("firstContribution")
    total_detail = (date.fromisoformat(first).strftime("%b %-d, %Y") + " – Present") if first else "Public GitHub activity"
    definitions = [
        ("contributions", "Total Contributions", data["totalContributions"], total_detail, "#58a6ff", "#152133", "⑂"),
    ]
    for key, filename, label, accent, background, icon in [
        ("currentStreak", "current", "Current Streak", "#d35be7", "#211a2c", "♨"),
        ("longestStreak", "longest", "Longest Streak", "#ffbf32", "#15202d", "♜"),
    ]:
        streak = data[key]
        detail = date_range(streak["start"], streak["end"]) if streak["length"] else "No active streak"
        definitions.append((filename, label, streak["length"], detail, accent, background, icon))
    # Validate and render every card before changing any files.
    cards = {f"stats-{name}.svg": card(label, value, detail, accent, background, icon)
             for name, label, value, detail, accent, background, icon in definitions}
    output_dir.mkdir(parents=True, exist_ok=True)
    for filename, svg in cards.items():
        target = output_dir / filename
        if not target.exists() or target.read_text(encoding="utf-8") != svg:
            target.write_text(svg, encoding="utf-8")
            print(f"Updated {filename}")


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
