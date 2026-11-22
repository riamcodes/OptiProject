# A Whole New Route: Data

Data collection for **A Whole New Route**, an itinerary-optimization project for MIT 15.C57 Optimization (Fall 2026) by Yue Yu, Jenny Yu and Ria Mukherji. We choose the order in which a visitor rides a set of Magic Kingdom attractions to minimize total waiting plus walking time.

## Contents

| Path | What it is |
|---|---|
| `scrape_wartezeiten.py` | Script that collects average posted wait times by hour and by month for 12 Magic Kingdom attractions from Wartezeiten.APP |
| `data/magic_kingdom_hourly_waits_2025_2026.csv` | **Main dataset.** Output of the script (accessed Nov 10, 2026): 12 attractions × {2025, 2026} |
| `data/magic_kingdom_hourly_waits.csv` | Cross-check dataset: hourly averages from Chart the Magic (~152 days, Jun–Oct 2026), transcribed manually from the site's ride pages |
| `data/DATA_README.md` | Detailed description of both datasets: columns, collection steps, gaps and limitations |
| `data/walking/` | Walking distances and times between the 12 attractions (OpenStreetMap network, Nov 21, 2026), a Google Maps validation summary and a README |
| `data/ride_durations.csv` | Duration of each attraction in minutes from TouringPlans, including mandatory pre-shows and exit time (Disney does not publish official ride lengths) |

## Reproducing the main dataset

```bash
pip install -r requirements.txt
playwright install chromium
python scrape_wartezeiten.py --years 2025 2026 --out magic_kingdom_hourly_waits_2025_2026.csv
```

How it works:

1. For each attraction and year, the script opens the attraction's statistics page on Wartezeiten.APP in a headless browser. The site fills its tables with JavaScript, so a plain HTTP request is not enough.
2. It reads two tables: **average wait by hour of day** and **average wait by month**, for that year.
3. It converts values such as "approx. 27,09 minutes" to `27.09`. No other changes are made.
4. Years in which a ride was closed for some months are flagged in `data_status` and `months_with_data`.

Notes:

- Downloaded pages are saved in `html_cache/`. Use `--offline` to re-parse them without downloading again.
- The site's 2026 statistics keep updating, so a new run gives slightly different 2026 values. Use `--as-of 2026-11-10` with the original cached pages to reproduce our exact file.
- The script waits 3 seconds between pages (`--delay`). Please keep the request rate low.

## Data sources and credit

- **Wartezeiten.APP**, Magic Kingdom attraction statistics, https://www.wartezeiten.app/en/magickingdompark/ (accessed Nov 10, 2026). The site states that all information is provided without warranty and may be incomplete.
- **Chart the Magic**, "Best Time to Ride," http://chartthemagic.com/best-time-to-ride (accessed Nov 9, 2026), CC BY 4.0.
- **OpenStreetMap** pedestrian network (Nov 21, 2026) for walking distances, © OpenStreetMap contributors, ODbL. See `data/walking/README.md`.
- **TouringPlans**, Magic Kingdom Attraction Durations, https://touringplans.com/magic-kingdom/attractions/duration (accessed Nov 22, 2026).

All values are **posted** standby waits (what Disney displays), not measured time in line.

## AI use

An AI assistant (Claude) helped identify data sources, collect the data and write the collection script. The team reviewed the outputs.
