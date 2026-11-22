# Magic Kingdom Hourly Wait Times (12 attractions)

This folder has two data files for the same 12 attractions:

| File | Source | Period | Use |
|---|---|---|---|
| `magic_kingdom_hourly_waits_2025_2026.csv` | Wartezeiten.APP | 2025 full year; 2026 through Nov 10 | **Main dataset.** Build estimates on 2025, test on 2026, and use monthly averages for crowd scenarios. |
| `magic_kingdom_hourly_waits.csv` | Chart the Magic | ~152 days, roughly Jun–Oct 2026 | Backup and cross-check. |

Use one file as the main source and don't mix the two. They record waits slightly differently and cover different periods.

---

# File 1: `magic_kingdom_hourly_waits_2025_2026.csv` (Wartezeiten.APP)

**Compiled:** November 10, 2026

## What it contains

One row per attraction per year (24 rows: 12 attractions × 2025 and 2026). Each row has:

- **Average posted wait in minutes for each hour of the day** (`h07` = 7:00–7:59 AM … `h23` = 11 PM, plus `h00`/`h01` for after-midnight events), averaged over all days of that year that the site recorded.
- **Average posted wait for each month** (`avg_Jan` … `avg_Dec`), useful for defining low, medium and high crowd scenarios (for example, September is quiet and February–March are busy).

## Source

Wartezeiten.APP (wartezeiten.app), an independent theme-park wait-time site. Each attraction has a statistics page with archives back to July 2022. Every row's `source_url` is the page its numbers came from:

- 2026 rows: the attraction's current page (`…/attraction/<ride>.html`), whose year tables cover January 1 to November 10, 2026.
- 2025 rows: an archive page from 2025 (`…/attraction/<ride>/archive/<month>-2025.html`), whose year tables cover all of 2025.

The site states that all information is provided without warranty and may be incomplete. Its free API is for live data only, and using it requires a visible link to https://www.wartezeiten.app/en/. Credit the site when you use these numbers: *Wartezeiten.APP, Magic Kingdom attraction statistics, accessed November 10, 2026.*

## How it was built

1. The page for each attraction and year was downloaded with a web-scraping tool (Firecrawl) used by an AI assistant (Claude).
2. A Python script read two tables from each page, "Average wait time by hours per year" and "Average wait time by months per year", and converted values such as "approx. 27,09 minutes" to `27.09`. No other changes were made.
3. Spot check: the 2026 Space Mountain values (9 AM = 27.09, noon = 44.37) match the site's page as read separately.

## Gaps (rides closed for refurbishment)

| Attraction | 2025 | 2026 |
|---|---|---|
| Big Thunder Mountain Railroad | **No data** (closed all year) | May–Nov only |
| Buzz Lightyear's Space Ranger Spin | Jan–Aug only | Apr–Nov only |
| Tiana's Bayou Adventure | Feb–Dec | Jan–Nov (closed Nov 2, 2026 for refurbishment) |
| Jungle Cruise | Jan–Nov | Jan–Nov |

The `months_with_data` column lists the exact months for every row. Because Big Thunder has no 2025 data, it can't be part of an "estimate on 2025, test on 2026" comparison. Either swap it for another attraction or leave it out of that test.

## Limitations

- Posted waits, not actual time in line.
- Year-level averages hide differences between days. Holidays and busy days can be much higher.
- 2026 is a partial year (through November 10).
- Hours when the park was open for special events (early entry, evening parties) are included in the hourly averages.

---

# File 2: `magic_kingdom_hourly_waits.csv` (Chart the Magic)

**File:** `magic_kingdom_hourly_waits.csv`
**Project:** A Whole New Route — MIT 15.C57 Optimization, Fall 2026 (Yue Yu, Jenny Yu, Ria Mukherji)
**Compiled:** November 9, 2026

## What this file contains

Typical **posted standby wait times, in minutes**, for 12 attractions at Walt Disney World's Magic Kingdom, for each hour from 9 AM to 9 PM. Each value is an *average* over many days, not a reading from a single day.

Example: `Space Mountain, 12PM = 38` means the posted wait for Space Mountain around noon was typically about 38 minutes.

In our model, these values are the time-dependent waiting times w_i(t_i).

## Original source

All wait-time numbers come from **Chart the Magic** (chartthemagic.com), an independent Walt Disney World planning site not affiliated with Disney.

- Index page: http://chartthemagic.com/best-time-to-ride
- Each attraction's own page (URL in the `source_url` column) shows a table of typical waits by hour.
- Methodology: https://chartthemagic.com/methodology

**How Chart the Magic produced the numbers (as described on their site):**

- They recorded each attraction's **posted** standby wait every **10 minutes** during park open hours.
- Posted waits come from ThemeParks.wiki, an open API that aggregates the waits Disney displays on its signs and app.
- Logging began in **June 2026**. The figures cover about **152 days**, so roughly June–October 2026. The site does not state exact start and end dates.
- Each hourly value is the average of the readings that fell in that hour. Each attraction has about 15,000–17,500 readings in total, which works out to roughly 900 readings behind each hourly value.
- Gaps in their data collection are left as gaps and are not filled in.

**License:** Chart the Magic publishes its data under **CC BY 4.0**, which allows reuse with credit. Please cite: *Chart the Magic, "Best Time to Ride," chartthemagic.com, accessed November 9, 2026.*

## How we built this file

1. We opened Chart the Magic's "Best Time to Ride" page, which lists 31 Magic Kingdom attractions.
2. We chose 12 attractions: popular rides spread across the park's lands whose waits vary noticeably during the day.
3. We opened each attraction's page and copied its hour-by-hour wait table (9 AM–9 PM) and its reported number of readings and days.
4. We entered the values into a CSV **by hand, without changes**: no rounding, adjusting or recalculating.
5. We checked that the file loads correctly: 12 rows, 18 columns, and plausible minimum and maximum waits for each ride.

We did **not** use Chart the Magic's downloadable open-data CSVs (chartthemagic.com/open-data). This file was transcribed from the public ride pages.

**AI use disclosure:** The data was gathered and transcribed with help from an AI assistant (Claude), which read the public web pages and entered the numbers into the CSV. The team is responsible for checking the values against the source pages.

## Columns

| Column | Meaning |
|---|---|
| `ride` | Attraction name as shown on Chart the Magic |
| `land` | Area of Magic Kingdom where the ride is located. **Added by us from general park knowledge, not from the source.** Check against an official park map. |
| `data_points` | Number of posted-wait readings Chart the Magic reports for this ride |
| `days` | Number of days covered, as reported by Chart the Magic (152 for all rides) |
| `9AM` … `9PM` | Typical posted wait in minutes for that hour |
| `source_url` | Page the numbers were copied from |

## Attractions included

Space Mountain, TRON Lightcycle / Run, Buzz Lightyear's Space Ranger Spin, Seven Dwarfs Mine Train, Peter Pan's Flight, The Many Adventures of Winnie the Pooh, it's a small world, Haunted Mansion, Big Thunder Mountain Railroad, Tiana's Bayou Adventure, Pirates of the Caribbean, Jungle Cruise.

## Limitations

- **Posted, not actual, waits.** Chart the Magic notes that posted waits often run longer than the real time spent in line.
- **Averages, not individual days.** Any single day, especially a holiday or special event, can differ a lot from these values. With this file alone, models cannot be estimated on some days and tested on others.
- **Seasonal coverage.** The data covers summer and fall 2026 only, with no winter holidays or spring break.
- **Hourly resolution.** Waits are given per hour. Values between hours need an assumption, for example using the wait for the hour of arrival or interpolating between hours.
- **Transcription.** The numbers were copied from web pages, so errors are possible. Spot-check a few rides against their `source_url` before relying on the file.

## Not included (collected separately)

- Walking times between attractions and from the park entrance
- Ride durations
- Park operating hours for the modeled day
