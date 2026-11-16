#!/usr/bin/env python3
"""stats_card.py — draw the terminal-style stats card for the profile README.

Filter: reads the GraphQL JSON from bin/stats.graphql on stdin, writes one SVG
to stdout. Usage: stats_card.py dark|light < stats.json > card.svg

Only totals are drawn. No repo, org or file name ever reaches the SVG, so the
card can count private work without showing any of it.
"""
import json
import sys
from datetime import date
from html import escape

THEMES = {
    "dark": {"bg": "#0d1117", "bar": "#161b22", "border": "#30363d",
             "text": "#e6edf3", "muted": "#7d8590", "accent": "#3fb950",
             "spark": "#3fb950"},
    "light": {"bg": "#ffffff", "bar": "#f6f8fa", "border": "#d0d7de",
              "text": "#1f2328", "muted": "#656d76", "accent": "#1a7f37",
              "spark": "#2da44e"},
}

W, PAD, LINE = 520, 24, 24
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"


def streak(days):
    """Current run of days with at least one contribution, ending today or yesterday."""
    run = 0
    for i, d in enumerate(reversed(days)):
        if d["contributionCount"] > 0:
            run += 1
        elif i == 0:
            continue  # today may not have started yet
        else:
            break
    return run


def main():
    theme = THEMES[sys.argv[1] if len(sys.argv) > 1 else "dark"]
    c = json.load(sys.stdin)["data"]["viewer"]["contributionsCollection"]
    cal = c["contributionCalendar"]
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    weekly = [sum(d["contributionCount"] for d in w["contributionDays"]) for w in cal["weeks"]]

    rows = [
        ("contributions", cal["totalContributions"]),
        ("commits", c["totalCommitContributions"]),
        ("pull requests", c["totalPullRequestContributions"]),
        ("issues", c["totalIssueContributions"]),
        ("reviews", c["totalPullRequestReviewContributions"]),
        ("current streak", f"{streak(days)} days"),
    ]

    y = 44 + 2 * LINE
    out = []
    out.append(f'<text x="{PAD}" y="{44 + LINE}" fill="{theme["accent"]}">$</text>'
               f'<text x="{PAD + 16}" y="{44 + LINE}" fill="{theme["text"]}">git stats --since="1 year ago"</text>')
    for label, val in rows:
        v = f"{val:,}" if isinstance(val, int) else val
        dots = "." * (34 - len(label) - len(v))
        out.append(f'<text x="{PAD}" y="{y}" fill="{theme["muted"]}">{escape(label)} {dots} '
                   f'<tspan fill="{theme["text"]}" font-weight="600">{escape(v)}</tspan></text>')
        y += LINE

    # weekly sparkline: one bar per week, height scaled to the busiest week
    y += 8
    sh, peak = 40, max(weekly) or 1
    bw = (W - 2 * PAD) / len(weekly)
    for i, n in enumerate(weekly):
        h = max(1.5, n / peak * sh)
        out.append(f'<rect x="{PAD + i * bw:.1f}" y="{y + sh - h:.1f}" width="{bw - 1.5:.1f}" '
                   f'height="{h:.1f}" rx="1" fill="{theme["spark"]}" opacity="{0.35 + 0.65 * n / peak:.2f}"/>')
    y += sh + 20
    out.append(f'<text x="{PAD}" y="{y}" fill="{theme["muted"]}" font-size="11">'
               f'weekly contributions · updated {date.today().isoformat()}</text>')
    H = y + 20

    sys.stdout.write(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'font-family="{FONT}" font-size="13" role="img" aria-label="GitHub stats for the last year">'
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10" fill="{theme["bg"]}" stroke="{theme["border"]}"/>'
        f'<path d="M0.5 32 V10.5 a10 10 0 0 1 10 -10 H{W - 10.5} a10 10 0 0 1 10 10 V32 Z" fill="{theme["bar"]}"/>'
        f'<line x1="0.5" y1="32" x2="{W - 0.5}" y2="32" stroke="{theme["border"]}"/>'
        f'<circle cx="20" cy="16" r="6" fill="#ff5f57"/><circle cx="40" cy="16" r="6" fill="#febc2e"/>'
        f'<circle cx="60" cy="16" r="6" fill="#28c840"/>'
        f'<text x="{W / 2}" y="20" text-anchor="middle" fill="{theme["muted"]}" font-size="12">justin@github: ~</text>'
        + "".join(out) + "</svg>\n"
    )


if __name__ == "__main__":
    main()
