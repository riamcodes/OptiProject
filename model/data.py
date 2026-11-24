"""
Step 1: load all model inputs into one place.

Everything the model needs comes from `a-whole-new-route-data/data/`:
  - hourly and monthly average posted waits (Wartezeiten.APP), 2025 and 2026
  - walking distances between attractions (OpenStreetMap), converted to minutes
  - ride durations (TouringPlans)

Times are minutes after midnight (9:00 AM = 540).

Usage:
    from data import load_inputs
    inp = load_inputs()                      # 10-ride study, base settings
    inp.walk_min["SM"]["TRON"]               # walking minutes
    inp.wait("SM", 600, year=2025)           # predicted wait arriving 10:00 AM
"""

import csv
import math
import os
from dataclasses import dataclass, field

import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "a-whole-new-route-data", "data")

# Short code used in the walking workbook -> full name used in the other files
RIDES = {
    "SM": "Space Mountain",
    "TRON": "TRON Lightcycle / Run",
    "BUZZ": "Buzz Lightyear's Space Ranger Spin",
    "SDMT": "Seven Dwarfs Mine Train",
    "PP": "Peter Pan's Flight",
    "POOH": "The Many Adventures of Winnie the Pooh",
    "IASW": "it's a small world",
    "HM": "Haunted Mansion",
    "BTMR": "Big Thunder Mountain Railroad",
    "TIANA": "Tiana's Bayou Adventure",
    "POTC": "Pirates of the Caribbean",
    "JC": "Jungle Cruise",
}

# Final study set: Buzz and Big Thunder are excluded (closed for long refurbishments).
STUDY_RIDES = ["SM", "TRON", "SDMT", "PP", "POOH", "IASW", "HM", "TIANA", "POTC", "JC"]

START = "ENTRANCE"

# Approximate access-point coordinates, from walking/validation_summary.md
COORDS = {
    "SM": (28.4187622, -81.5783241), "TRON": (28.4199514, -81.5772546),
    "BUZZ": (28.418202, -81.5802262), "SDMT": (28.4203578, -81.5805181),
    "PP": (28.4203952, -81.5818461), "POOH": (28.4202086, -81.5802121),
    "IASW": (28.4204094, -81.5820316), "HM": (28.4201572, -81.5828859),
    "BTMR": (28.4197246, -81.5845775), "TIANA": (28.4196285, -81.5849644),
    "POTC": (28.4181032, -81.584234), "JC": (28.4180394, -81.5834779),
}
# Park entrance used for the routed entrance distances (walking/entrance_distances.csv)
ENTRANCE_COORD = (28.4163, -81.5812)

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
HOUR_COLS = ["h07", "h08", "h09", "h10", "h11", "h12", "h13", "h14", "h15", "h16",
             "h17", "h18", "h19", "h20", "h21", "h22", "h23"]


def _haversine_m(a, b):
    r = 6371000.0
    la1, lo1, la2, lo2 = map(math.radians, (*a, *b))
    h = (math.sin((la2 - la1) / 2) ** 2
         + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2)
    return 2 * r * math.asin(math.sqrt(h))


def load_walking_distances():
    """Return {code: {code: metres}} from the 'Distance (m)' sheet."""
    wb = openpyxl.load_workbook(os.path.join(DATA, "walking", "Magic_Kingdom_Walking.xlsx"),
                                data_only=True)
    ws = wb["Distance (m)"]
    rows = list(ws.iter_rows(values_only=True))
    header_i = next(i for i, r in enumerate(rows) if r and r[0] == "Attraction")
    codes = [c for c in rows[header_i][1:] if c]
    dist = {}
    for r in rows[header_i + 1: header_i + 1 + len(codes)]:
        code = r[0].split(":")[0].strip()
        dist[code] = {codes[k]: float(r[k + 1]) for k in range(len(codes))}
    return dist


def add_entrance(dist):
    """Entrance-to-ride walking distances.

    Uses walking/entrance_distances.csv: OpenStreetMap foot-routing distances
    (routing.openstreetmap.de, OSRM, accessed Nov 24, 2026) from the park entrance
    (28.4163, -81.5812) to each ride's access point. Rides missing from that file fall
    back to straight-line distance x the median detour factor of the walking matrix.
    """
    ratios = sorted(dist[a][b] / _haversine_m(COORDS[a], COORDS[b])
                    for a in dist for b in dist if a < b and dist[a][b] > 50)
    detour = ratios[len(ratios) // 2]
    routed = {}
    path = os.path.join(DATA, "walking", "entrance_distances.csv")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            routed = {r["ride_code"]: float(r["distance_m"]) for r in csv.DictReader(fh)}
    dist[START] = {c: routed.get(c, _haversine_m(ENTRANCE_COORD, COORDS[c]) * detour) for c in COORDS}
    dist[START][START] = 0.0
    for c in COORDS:
        dist[c][START] = dist[START][c]
    return detour


def load_durations():
    by_name = {}
    with open(os.path.join(DATA, "ride_durations.csv"), encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            by_name[row["ride"]] = float(row["duration_min"])
    return {code: by_name[name] for code, name in RIDES.items()}


def load_wait_tables():
    """Return {(code, year): {"hourly": {hour: minutes}, "monthly": {month: minutes}}}."""
    name_to_code = {v: k for k, v in RIDES.items()}
    out = {}
    path = os.path.join(DATA, "magic_kingdom_hourly_waits_2025_2026.csv")
    with open(path, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            code = name_to_code[row["ride"]]
            hourly = {int(h[1:]): float(row[h]) for h in HOUR_COLS if row[h]}
            monthly = {m: float(row["avg_" + m]) for m in MONTHS if row["avg_" + m]}
            out[(code, int(row["year"]))] = {"hourly": hourly, "monthly": monthly}
    return out


@dataclass
class Inputs:
    rides: list
    walk_min: dict          # {from: {to: minutes}}, includes START
    duration: dict          # {code: minutes}
    waits: dict             # {(code, year): {"hourly": ..., "monthly": ...}}
    open_min: int = 9 * 60
    close_min: int = 22 * 60
    walk_speed_kmh: float = 4.5
    entrance_detour: float = field(default=0.0)

    def wait(self, code, t, year=2025, month=None):
        """Expected posted wait (min) when arriving at `code` at time t (min after midnight).

        Each hourly value is the average over that clock hour, so it is placed at the
        half-hour (the 10:00 value sits at 10:30) and values in between are linearly
        interpolated. Before the first / after the last hour, the nearest value is used.
        If `month` is given, the profile is scaled by that month's average relative to
        the ride's average over all months (crowd scenarios).
        """
        tab = self.waits[(code, year)]["hourly"]
        hours = sorted(tab)
        x = t / 60.0 - 0.5
        if x <= hours[0]:
            w = tab[hours[0]]
        elif x >= hours[-1]:
            w = tab[hours[-1]]
        else:
            h0 = max(h for h in hours if h <= x)
            h1 = min(h for h in hours if h > x)
            w = tab[h0] + (tab[h1] - tab[h0]) * (x - h0) / (h1 - h0)
        if month:
            monthly = self.waits[(code, year)]["monthly"]
            if month in monthly:
                w *= monthly[month] / (sum(monthly.values()) / len(monthly))
        return w


def load_inputs(rides=None, walk_speed_kmh=4.5, open_min=9 * 60, close_min=22 * 60):
    dist = load_walking_distances()
    detour = add_entrance(dist)
    m_per_min = walk_speed_kmh * 1000 / 60
    walk_min = {a: {b: d / m_per_min for b, d in row.items()} for a, row in dist.items()}
    return Inputs(
        rides=list(rides or STUDY_RIDES),
        walk_min=walk_min,
        duration=load_durations(),
        waits=load_wait_tables(),
        open_min=open_min,
        close_min=close_min,
        walk_speed_kmh=walk_speed_kmh,
        entrance_detour=detour,
    )


if __name__ == "__main__":
    inp = load_inputs()
    print(f"Rides: {', '.join(inp.rides)}")
    print("Walking from entrance (min):",
          {r: round(inp.walk_min[START][r], 1) for r in inp.rides})
    print("Durations (min):", {r: inp.duration[r] for r in inp.rides})
    print("Space Mountain predicted wait (2025):",
          {f"{h}:00": round(inp.wait('SM', h * 60, 2025), 1) for h in range(9, 22, 2)})
