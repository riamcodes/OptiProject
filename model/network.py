"""
Step 4 (data side): build the time-expanded network.

The day is cut into slots of `slot` minutes starting at the start time. A node is
(place, slot) = "standing at this place, free to move, at this slot". Places are the
entrance and the rides.

An arc (i, s) -> (j, s2) means: leave place i at slot s, walk to ride j, wait in line,
ride, and be free again at slot s2. Because the departure time is fixed by s, the arrival
time at j is known, so its wait can be looked up in advance and stored on the arc. That
is what keeps the optimization model linear even though waits change through the day.

    s2 = ceil((depart + walk + wait + ride) / slot)   (rounded up to the next slot)

Arcs that would finish after park close are not created, so every route in the network
ends before close. Every arc moves forward in time (s2 > s), so the network has no cycles.

Used by:
  - time_expanded.py       (solves the model in Python with HiGHS)
  - export_for_julia.py    (writes arcs.csv for the Julia/JuMP notebook)
"""

import math
from dataclasses import dataclass

from data import START


@dataclass(frozen=True)
class Arc:
    i: str          # from place (START or ride code)
    s: int          # departure slot
    j: str          # ride visited
    s2: int         # slot when free again after riding j
    walk: float     # walking minutes on this arc
    wait: float     # predicted wait at j for this arrival time (minutes)

    @property
    def cost(self):
        return self.walk + self.wait


def build_arcs(inp, rides, start_min=None, year=2025, month=None, slot=5):
    t0 = inp.open_min if start_min is None else start_min
    n_slots = int((inp.close_min - t0) // slot)       # last usable slot index
    arcs = []
    reachable = {(START, 0)}
    frontier = [(START, 0)]
    # Only create arcs out of nodes that can actually be reached from the start.
    while frontier:
        nxt = []
        for (i, s) in frontier:
            depart = t0 + s * slot
            for j in rides:
                if j == i:
                    continue
                walk = inp.walk_min[i][j]
                arrive = depart + walk
                wait = inp.wait(j, arrive, year, month)
                done = arrive + wait + inp.duration[j]
                s2 = math.ceil((done - t0) / slot - 1e-9)
                if s2 > n_slots:
                    continue
                arcs.append(Arc(i, s, j, s2, walk, wait))
                if (j, s2) not in reachable:
                    reachable.add((j, s2))
                    nxt.append((j, s2))
        frontier = nxt
    return arcs, t0, slot, n_slots


if __name__ == "__main__":
    from data import load_inputs
    inp = load_inputs()
    arcs, t0, slot, n = build_arcs(inp, inp.rides)
    nodes = {(a.i, a.s) for a in arcs} | {(a.j, a.s2) for a in arcs}
    print(f"{len(inp.rides)} rides, {slot}-min slots, {n} slots: {len(nodes)} nodes, {len(arcs)} arcs")
