"""
Step 2: score any visiting order.

simulate() walks through an order of attractions starting at the entrance:
    arrive = depart + walk
    wait   = posted wait at arrival time (from the chosen year / month)
    depart = arrive + wait + ride duration
and returns the totals. The benchmarks, the optimization model and the app all use
this one function, so every strategy is scored the same way.
"""

from dataclasses import dataclass

from data import START


@dataclass
class Result:
    order: list
    walk: float       # total walking minutes (incl. from the entrance)
    wait: float       # total waiting minutes
    ride: float       # total ride minutes
    finish: float     # time the last ride ends (min after midnight)
    start: float
    feasible: bool    # True if everything ends before park close
    stops: list       # per stop: (code, arrive, wait, depart)

    @property
    def walk_plus_wait(self):
        return self.walk + self.wait

    @property
    def total(self):
        return self.finish - self.start


def simulate(inp, order, start_min=None, year=2025, month=None):
    t = inp.open_min if start_min is None else start_min
    start = t
    here = START
    walk = wait = ride = 0.0
    stops = []
    for code in order:
        w_k = inp.walk_min[here][code]
        arrive = t + w_k
        q = inp.wait(code, arrive, year, month)
        d = inp.duration[code]
        t = arrive + q + d
        walk += w_k
        wait += q
        ride += d
        stops.append((code, arrive, q, t))
        here = code
    return Result(list(order), walk, wait, ride, t, start, t <= inp.close_min, stops)


def fmt_time(m):
    h, mi = divmod(int(round(m)), 60)
    return f"{(h - 1) % 12 + 1}:{mi:02d} {'AM' if h < 12 else 'PM'}"


def describe(res, names=None):
    lines = []
    for code, arrive, q, depart in res.stops:
        name = names[code] if names else code
        lines.append(f"  {fmt_time(arrive):>8}  {name:<40} wait {q:5.1f}  done {fmt_time(depart)}")
    lines.append(f"  walk {res.walk:.0f} + wait {res.wait:.0f} = {res.walk_plus_wait:.0f} min;"
                 f" finish {fmt_time(res.finish)}{'' if res.feasible else '  (AFTER CLOSE)'}")
    return "\n".join(lines)
