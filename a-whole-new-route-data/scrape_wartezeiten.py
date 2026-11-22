"""
Scrape hourly and monthly average posted wait times for Magic Kingdom
attractions from Wartezeiten.APP (https://www.wartezeiten.app/en/).

For each attraction and year, the script opens the attraction's statistics
page in a headless browser (the site loads its tables with JavaScript),
reads two tables:
    "Average wait time by hours per year"   -> h07 ... h23, h00, h01
    "Average wait time by months per year"  -> avg_Jan ... avg_Dec
and writes one CSV row per attraction-year.

Values on the site look like "approx. 27,09 minutes" (decimal comma);
they are converted to 27.09 and otherwise left unchanged.

Usage
-----
    pip install -r requirements.txt
    playwright install chromium
    python scrape_wartezeiten.py --years 2025 2026 --out magic_kingdom_hourly_waits_2025_2026.csv

    # Re-parse previously saved pages without downloading anything:
    python scrape_wartezeiten.py --years 2025 2026 --offline --cache-dir html_cache

Data source: Wartezeiten.APP. The site states that all information is
provided without warranty and may be incomplete. Please credit the site
and keep the request rate low (the script waits between pages).
"""

import argparse
import csv
import datetime as dt
import html as htmllib
import os
import re
import time

BASE = "https://www.wartezeiten.app/en/magickingdompark/attraction"

# (site slug, display name, land)
RIDES = [
    ("space-mountain", "Space Mountain", "Tomorrowland"),
    ("tron-lightcycle-run", "TRON Lightcycle / Run", "Tomorrowland"),
    ("buzz-lightyears-space-ranger-spin", "Buzz Lightyear's Space Ranger Spin", "Tomorrowland"),
    ("seven-dwarfs-mine-train", "Seven Dwarfs Mine Train", "Fantasyland"),
    ("peter-pan-s-flight", "Peter Pan's Flight", "Fantasyland"),
    ("the-many-adventures-of-winnie-the-pooh", "The Many Adventures of Winnie the Pooh", "Fantasyland"),
    ("it-s-a-small-world", "it's a small world", "Fantasyland"),
    ("haunted-mansion", "Haunted Mansion", "Liberty Square"),
    ("big-thunder-mountain-railroad", "Big Thunder Mountain Railroad", "Frontierland"),
    ("tiana-s-bayou-adventure", "Tiana's Bayou Adventure", "Frontierland"),
    ("pirates-of-the-caribbean", "Pirates of the Caribbean", "Adventureland"),
    ("jungle-cruise", "Jungle Cruise", "Adventureland"),
]

HOURS = ["07:00", "08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00",
         "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00", "22:00",
         "23:00", "00:00", "01:00"]
MONTH_KEYS = ["Jan.", "Feb.", "Mar.", "Apr.", "May", "Jun.", "Jul.", "Aug.",
              "Sep.", "Oct.", "Nov.", "Dec."]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# The site fills these <div>s with the yearly tables via AJAX.
HOURS_DIV = "ajax_stunden_jahr"
MONTHS_DIV = "ajax_monate_jahr"


# ----------------------------------------------------------------------------
# Parsing
# ----------------------------------------------------------------------------
def parse_minutes(text):
    """'approx. 27,09 minutes' -> 27.09 ; returns None if no number."""
    m = re.search(r"([\d.,]+)\s*minutes", text)
    if not m:
        return None
    return float(m.group(1).replace(".", "").replace(",", "."))


def parse_div_table(page_html, div_id):
    """Return {label: minutes} from the 2-column table inside <div id=div_id>."""
    start = page_html.find(f'id="{div_id}"')
    if start < 0:
        return {}
    t0 = page_html.find("<table", start)
    t1 = page_html.find("</table>", t0)
    if t0 < 0 or t1 < 0:
        return {}
    out = {}
    for row in re.findall(r"<tr>(.*?)</tr>", page_html[t0:t1], re.S):
        cells = [htmllib.unescape(re.sub(r"<[^>]+>", "", c)).strip()
                 for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.S)]
        if len(cells) == 2:
            val = parse_minutes(cells[1])
            if val is not None:
                out[cells[0]] = val
    return out


def parse_page(page_html):
    """Return (hourly dict, monthly dict) for the year shown on the page."""
    return parse_div_table(page_html, HOURS_DIV), parse_div_table(page_html, MONTHS_DIV)


# ----------------------------------------------------------------------------
# Downloading
# ----------------------------------------------------------------------------
def candidate_urls(slug, year, today):
    """Pages that contain the yearly tables for `year`, most complete first.

    Any month page of a year shows that year's yearly tables, but a month in
    which the ride was closed shows no tables, so we try months from the end
    of the year backwards. For the current year we start with the live page.
    """
    urls = []
    if year == today.year:
        urls.append(f"{BASE}/{slug}.html")
        last = today.month
    else:
        last = 12
    for month in range(last, 0, -1):
        urls.append(f"{BASE}/{slug}/archive/{month}-{year}.html")
    return urls


def cache_path(cache_dir, url):
    name = url.split("/attraction/")[1].replace("/", "__")
    return os.path.join(cache_dir, name)


def fetch_rendered(browser, url, timeout_ms=30000):
    """Open `url` in a headless browser, wait for the yearly tables, return HTML."""
    page = browser.new_page()
    try:
        page.goto(url, timeout=timeout_ms, wait_until="domcontentloaded")
        try:
            page.wait_for_selector(f"#{HOURS_DIV} table", timeout=15000)
            page.wait_for_selector(f"#{MONTHS_DIV} table", timeout=15000)
        except Exception:
            pass  # e.g. "no wait times for this attraction in the selected period"
        return page.content()
    finally:
        page.close()


def get_year_tables(slug, year, today, browser, cache_dir, offline, delay):
    for url in candidate_urls(slug, year, today):
        path = cache_path(cache_dir, url)
        if os.path.exists(path):
            page_html = open(path, encoding="utf-8").read()
        elif offline:
            continue
        else:
            page_html = fetch_rendered(browser, url)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(page_html)
            time.sleep(delay)
        hours, months = parse_page(page_html)
        if hours:
            return hours, months, url
    return {}, {}, ""


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--years", nargs="+", type=int, default=[2025, 2026])
    ap.add_argument("--out", default="magic_kingdom_hourly_waits_2025_2026.csv")
    ap.add_argument("--cache-dir", default="html_cache", help="where downloaded pages are saved")
    ap.add_argument("--offline", action="store_true", help="only parse pages already in --cache-dir")
    ap.add_argument("--delay", type=float, default=3.0, help="seconds to wait between page downloads")
    ap.add_argument("--as-of", default=None, help="treat this date (YYYY-MM-DD) as today; default: real date")
    args = ap.parse_args()

    os.makedirs(args.cache_dir, exist_ok=True)
    today = dt.date.fromisoformat(args.as_of) if args.as_of else dt.date.today()

    browser = pw = None
    if not args.offline:
        from playwright.sync_api import sync_playwright
        pw = sync_playwright().start()
        browser = pw.chromium.launch(headless=True)

    header = (["ride", "land", "year", "data_status", "months_with_data"]
              + ["h" + h[:2] for h in HOURS]
              + ["avg_" + m for m in MONTHS]
              + ["source_url"])
    rows = []
    try:
        for slug, name, land in RIDES:
            for year in args.years:
                hours, months, url = get_year_tables(slug, year, today, browser,
                                                     args.cache_dir, args.offline, args.delay)
                months_with_data = [MONTHS[i] for i, k in enumerate(MONTH_KEYS) if k in months]
                if not hours:
                    status = "no data (ride closed all year)"
                else:
                    partial = year == today.year
                    status = f"partial year (to {today:%b} {today.day}, {year})" if partial else "full year"
                    expected = today.month if partial else 12
                    if len(months_with_data) < expected:
                        status += "; ride closed some months"
                rows.append([name, land, year, status, " ".join(months_with_data)]
                            + [hours.get(h, "") for h in HOURS]
                            + [months.get(k, "") for k in MONTH_KEYS]
                            + [url])
                print(f"{name:40s} {year}  {status}")
    finally:
        if browser:
            browser.close()
            pw.stop()

    with open(args.out, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(header)
        writer.writerows(rows)
    print(f"\nWrote {len(rows)} rows to {args.out}")


if __name__ == "__main__":
    main()
