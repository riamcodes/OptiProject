"""
Step 3: the two benchmark strategies, plus an exact reference.

closest_next   - from the current location, go to the nearest unvisited ride.
shortest_wait  - go to the unvisited ride with the shortest predicted wait on arrival
                 (accounting for the walk there).
exact_dp       - dynamic program over (rides done, last ride) that finds the order with
                 the least walking + waiting under the planning waits. Used to check the
                 integer-optimization model; it is not the project's main method.

Each strategy only *chooses* an order using the planning data (2025 by default).
Score the order with simulate() on whichever year you want to evaluate.
"""

from data import START


def closest_next(inp, rides, start_min=None, year=2025, month=None):
    here, left, order = START, list(rides), []
    while left:
        nxt = min(left, key=lambda r: inp.walk_min[here][r])
        order.append(nxt)
        left.remove(nxt)
        here = nxt
    return order


def shortest_wait(inp, rides, start_min=None, year=2025, month=None):
    t = inp.open_min if start_min is None else start_min
    here, left, order = START, list(rides), []
    while left:
        def predicted(r):
            return inp.wait(r, t + inp.walk_min[here][r], year, month)
        nxt = min(left, key=predicted)
        arrive = t + inp.walk_min[here][nxt]
        t = arrive + inp.wait(nxt, arrive, year, month) + inp.duration[nxt]
        order.append(nxt)
        left.remove(nxt)
        here = nxt
    return order


def exact_dp(inp, rides, start_min=None, year=2025, month=None):
    """Minimize walking + waiting exactly.

    State: (set of rides done, last ride). Because total ride time is fixed, minimizing
    walk + wait is the same as minimizing the finish time, and an earlier finish at a
    state is never worse (waits are averages and there is no reason to idle), so keeping
    the earliest finish per state is exact.
    """
    t0 = inp.open_min if start_min is None else start_min
    idx = {r: k for k, r in enumerate(rides)}
    best = {}
    for r in rides:
        a = t0 + inp.walk_min[START][r]
        best[(1 << idx[r], r)] = (a + inp.wait(r, a, year, month) + inp.duration[r], [r])
    for _ in range(len(rides) - 1):
        nxt = {}
        for (mask, last), (t, route) in best.items():
            for r in rides:
                if mask >> idx[r] & 1:
                    continue
                a = t + inp.walk_min[last][r]
                f = a + inp.wait(r, a, year, month) + inp.duration[r]
                key = (mask | 1 << idx[r], r)
                if key not in nxt or f < nxt[key][0]:
                    nxt[key] = (f, route + [r])
        best = nxt
    return min(best.values())[1]
