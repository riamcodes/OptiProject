# Model code

| File | Step | What it does |
|---|---|---|
| `data.py` | 1 | Loads waits, walking times and ride durations into one `Inputs` object (10 study rides) |
| `simulate.py` | 2 | Scores any visiting order: walk, wait, ride time, finish time, park-close check |
| `benchmarks.py` | 3 | Closest-next-ride, shortest-wait-next, and an exact dynamic-programming check |
| `run_baseline.py` | — | Plans with 2025 waits and scores on 2025 and 2026 |

```bash
pip install openpyxl
python model/run_baseline.py --verbose
python model/run_baseline.py --start 13:00 --month Feb --speed 3.5
python model/run_baseline.py --rides SM TRON PP SDMT HM POTC
```

## Modeling choices

- **Times** are minutes after midnight. The park is open 9:00 AM to 10:00 PM by default.
- **Waits:** each hourly average is placed at the half-hour (the 10:00 value is at 10:30), with linear interpolation in between. `--month` scales a ride's profile by that month's average relative to its yearly average.
- **Planning vs. testing:** every strategy chooses its order with 2025 waits; orders are scored on 2025 and on 2026.
- **Walking** uses the OpenStreetMap matrix at 4.5 km/h (adjustable).

## To do

- **Entrance distances are provisional.** The walking workbook has no entrance row, so `data.py` estimates entrance-to-ride distances as straight-line distance × the median detour factor of the OpenStreetMap matrix (about 1.26), measured from an approximate Town Square point. Replace these with OpenStreetMap network distances.
- Step 4: the integer optimization model (time-expanded network) and its LP relaxation. The exact DP in `benchmarks.py` is there to check it.
