"""
Quick comparison: plan with 2025 waits, score on 2025 and 2026.

    python model/run_baseline.py                 # all 10 study rides, 9:00 AM start
    python model/run_baseline.py --start 11:00 --month Feb
"""

import argparse

from benchmarks import closest_next, exact_dp, shortest_wait
from data import RIDES, load_inputs
from simulate import describe, simulate


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="9:00", help="start time, e.g. 9:00 or 13:30")
    ap.add_argument("--month", default=None, help="crowd scenario month, e.g. Feb or Sep")
    ap.add_argument("--speed", type=float, default=4.5, help="walking speed in km/h")
    ap.add_argument("--rides", nargs="*", default=None, help="ride codes, e.g. SM TRON PP")
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()

    h, m = map(int, a.start.split(":"))
    start = h * 60 + m
    inp = load_inputs(rides=a.rides, walk_speed_kmh=a.speed)
    rides = inp.rides

    strategies = {
        "Closest-next-ride": closest_next,
        "Shortest-wait-next": shortest_wait,
        "Exact best (DP)": exact_dp,
    }
    results = {}
    for name, fn in strategies.items():
        order = fn(inp, rides, start, year=2025, month=a.month)
        results[name] = {y: simulate(inp, order, start, year=y, month=a.month) for y in (2025, 2026)}

    print(f"{len(rides)} rides, start {a.start}, month {a.month or 'all-year'}, {a.speed} km/h"
          " (entrance distances PROVISIONAL)\n")
    print(f"{'Strategy':<20} {'Year':>5} {'Walk':>6} {'Wait':>6} {'Walk+Wait':>10} {'Total':>7}  Feasible")
    for name, by_year in results.items():
        for y, r in by_year.items():
            print(f"{name:<20} {y:>5} {r.walk:6.0f} {r.wait:6.0f} {r.walk_plus_wait:10.0f}"
                  f" {r.total:7.0f}  {'yes' if r.feasible else 'NO'}")
    print()
    best = results["Exact best (DP)"]
    for name in ("Closest-next-ride", "Shortest-wait-next"):
        for y in (2025, 2026):
            b, o = results[name][y].walk_plus_wait, best[y].walk_plus_wait
            print(f"Exact best vs {name:<19} {y}: {100 * (b - o) / b:+5.1f}% walk+wait saved")
    if a.verbose:
        for name, by_year in results.items():
            print(f"\n{name} (scored on 2026):\n{describe(by_year[2026], RIDES)}")


if __name__ == "__main__":
    main()
