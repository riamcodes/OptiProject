"""
Export the time-expanded network for the Julia/JuMP model.

Writes model/julia_inputs/arcs.csv, one row per possible move:
    from, from_slot, to, to_slot, walk_min, wait_min, cost_min
"leave `from` at slot `from_slot`, walk to ride `to`, wait, ride, and be free again
at slot `to_slot`". `from` is ENTRANCE or a ride code. Slot 0 = the start time,
each slot = 5 minutes. Also writes rides.csv (the rides that must each be visited once).

    python model/export_for_julia.py                          # 10 rides, 9:00 AM, 2025 waits
    python model/export_for_julia.py --start 13:00 --rides SM TRON PP SDMT HM POTC
"""

import argparse
import csv
import os

from data import RIDES, load_inputs
from network import build_arcs

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "julia_inputs")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="9:00")
    ap.add_argument("--year", type=int, default=2025)
    ap.add_argument("--month", default=None)
    ap.add_argument("--rides", nargs="*", default=None)
    ap.add_argument("--slot", type=int, default=5)
    a = ap.parse_args()
    hh, mm = map(int, a.start.split(":"))

    inp = load_inputs(rides=a.rides)
    arcs, t0, slot, n_slots = build_arcs(inp, inp.rides, hh * 60 + mm, a.year, a.month, a.slot)
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "arcs.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["from", "from_slot", "to", "to_slot", "walk_min", "wait_min", "cost_min"])
        for arc in arcs:
            w.writerow([arc.i, arc.s, arc.j, arc.s2, round(arc.walk, 3), round(arc.wait, 3), round(arc.cost, 3)])
    with open(os.path.join(OUT, "rides.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["code", "name"])
        for r in inp.rides:
            w.writerow([r, RIDES[r]])
    print(f"Wrote {len(arcs)} arcs for {len(inp.rides)} rides (start {a.start}, {a.year} waits, "
          f"{slot}-min slots, {n_slots} slots) to {OUT}")


if __name__ == "__main__":
    main()
