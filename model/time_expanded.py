"""
Step 4: the integer optimization model, solved in Python with HiGHS (free).

    variables   x[a] in {0, 1} for every arc a of the time-expanded network
                (1 = the visitor takes that move: leave i at slot s, ride j, free at s2)

    minimize    sum_a (walk_a + wait_a) * x[a]

    subject to  (1) start:      exactly one arc leaves the entrance at slot 0
                (2) flow:       at every (ride, slot) node, arcs out <= arcs in
                                (you can only leave a place you have arrived at;
                                 the route may end anywhere)
                (3) visit once: every chosen ride has exactly one arc into it
                (4) close:      no arc finishing after close exists (built into the network)

Because every arc moves forward in time, the chosen arcs always form one path through the
day: no loops are possible, so no extra "subtour" constraints are needed.

The LP relaxation replaces x[a] in {0, 1} by 0 <= x[a] <= 1. Its optimum is a lower bound
on the integer optimum; the gap between them shows how tight the formulation is.

The Julia/JuMP + Gurobi version of this exact model is model/step4_model.ipynb.

    python model/time_expanded.py                  # 10 rides, 9:00 AM
    python model/time_expanded.py --start 13:00 --rides SM TRON PP SDMT HM POTC
"""

import argparse
import time
from collections import defaultdict

import highspy
import numpy as np

from data import RIDES, START, load_inputs
from network import build_arcs


def solve(arcs, rides, relax=False, time_limit=300, verbose=False):
    h = highspy.Highs()
    h.setOptionValue("output_flag", verbose)
    h.setOptionValue("time_limit", float(time_limit))
    n = len(arcs)
    inf = highspy.kHighsInf
    cost = np.array([a.cost for a in arcs])
    h.addVars(n, np.zeros(n), np.ones(n))
    h.changeColsCost(n, np.arange(n, dtype=np.int32), cost)
    if not relax:
        h.changeColsIntegrality(n, np.arange(n, dtype=np.int32),
                                np.array([highspy.HighsVarType.kInteger] * n))

    out_of, into = defaultdict(list), defaultdict(list)
    into_ride = defaultdict(list)
    for k, a in enumerate(arcs):
        out_of[(a.i, a.s)].append(k)
        into[(a.j, a.s2)].append(k)
        into_ride[a.j].append(k)

    def add_row(lo, hi, idx, vals):
        h.addRow(lo, hi, len(idx), np.array(idx, dtype=np.int32), np.array(vals, dtype=float))

    # (1) start: one unit of flow leaves the entrance at slot 0
    add_row(1, 1, out_of[(START, 0)], [1] * len(out_of[(START, 0)]))
    # (2) flow: out - in <= 0 at every ride node
    for node in set(into) | {k for k in out_of if k[0] != START}:
        o, i = out_of.get(node, []), into.get(node, [])
        add_row(-inf, 0, o + i, [1] * len(o) + [-1] * len(i))
    # (3) visit once
    for r in rides:
        add_row(1, 1, into_ride[r], [1] * len(into_ride[r]))

    t = time.time()
    h.run()
    secs = time.time() - t
    info = h.getInfo()
    x = np.array(h.getSolution().col_value)
    status = h.modelStatusToString(h.getModelStatus())
    return {"obj": info.objective_function_value, "x": x, "seconds": secs, "status": status,
            "bound": getattr(info, "mip_dual_bound", info.objective_function_value)}


def route_from(arcs, x):
    """Follow the chosen arcs from the entrance to get the ride order."""
    by_node = {(a.i, a.s): a for a, v in zip(arcs, x) if v > 0.5}
    order, node = [], (START, 0)
    while node in by_node:
        a = by_node[node]
        order.append(a.j)
        node = (a.j, a.s2)
    return order


def main():
    from benchmarks import exact_dp
    from simulate import describe, simulate

    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="9:00")
    ap.add_argument("--month", default=None)
    ap.add_argument("--rides", nargs="*", default=None)
    ap.add_argument("--slot", type=int, default=5, help="slot length in minutes")
    a = ap.parse_args()
    hh, mm = map(int, a.start.split(":"))
    start = hh * 60 + mm

    inp = load_inputs(rides=a.rides)
    rides = inp.rides
    arcs, *_ = build_arcs(inp, rides, start, 2025, a.month, a.slot)
    print(f"{len(rides)} rides, start {a.start}: {len(arcs)} arc variables")

    ip = solve(arcs, rides)
    lp = solve(arcs, rides, relax=True)
    order = route_from(arcs, ip["x"])
    frac = int(np.sum((lp["x"] > 1e-6) & (lp["x"] < 1 - 1e-6)))
    print(f"Integer model : {ip['obj']:.1f} min  ({ip['status']}, {ip['seconds']:.1f}s)")
    print(f"LP relaxation : {lp['obj']:.1f} min  ({lp['seconds']:.1f}s, {frac} fractional arcs)")
    print(f"LP gap        : {100 * (ip['obj'] - lp['obj']) / ip['obj']:.1f}%")

    dp_order = exact_dp(inp, rides, start, 2025, a.month)
    ip_res = simulate(inp, order, start, 2025, a.month)
    dp_res = simulate(inp, dp_order, start, 2025, a.month)
    print(f"\nCheck vs exact method (scored without slot rounding, 2025 waits):")
    print(f"  integer model walk+wait {ip_res.walk_plus_wait:.1f}   exact best {dp_res.walk_plus_wait:.1f}")
    print(f"  same order: {order == dp_order}")
    print(f"\nRoute (scored on 2026 waits):\n{describe(simulate(inp, order, start, 2026, a.month), RIDES)}")


if __name__ == "__main__":
    main()
