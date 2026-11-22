# Magic Kingdom Walking

`Magic_Kingdom_Walking.xlsx` has two sheets:
- **Distance (m):** estimated walking distances for 12 attractions.
- **Walking time (min):** distance divided by 75 m/min, assuming **4.5 km/h**. Change B3 to adjust speed.

Distances use shortest paths through the [OpenStreetMap](https://www.openstreetmap.org/copyright) pedestrian network dated 21 November 2026, with WGS84 geodesic segment lengths. Each attraction uses one approximate public access point for both entrance and exit. These are estimates, not Disney measurements.

`validation_summary.md` explains the Google Maps cross-check and reports all 12 comparisons. Crowds, temporary closures and internal attraction movement are excluded.

© OpenStreetMap contributors, ODbL. Buzz Lightyear and Big Thunder Mountain are included; exclude them for the original 10-ride study.
