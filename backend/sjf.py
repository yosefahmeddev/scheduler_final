# backend/sjf.py
# ─────────────────────────────────────────────────────────────────────────────
# Shortest Job First (SJF) — Non-Preemptive
#
# Plain-English explanation:
#   1. Look at every process that has arrived so far.
#   2. Pick the one with the SHORTEST burst time.
#   3. Run it all the way to completion — no interruptions.
#   4. Repeat until every process is done.
#
# Tie-breaking: if two processes share the same burst time,
# the one that arrived earlier runs first.
# ─────────────────────────────────────────────────────────────────────────────

import copy


def run_sjf(processes: list) -> tuple:
    """
    Parameters
    ----------
    processes : list[Process]   already-validated Process objects

    Returns
    -------
    gantt   : list of dicts  {pid, start, end, color_index}
    metrics : list of dicts  per-process results
    """

    ps = copy.deepcopy(processes)

    gantt      = []
    t          = 0
    done_count = 0
    total      = len(ps)

    iterations = 0
    while done_count < total and iterations < 10_000:
        iterations += 1

        # All processes that have arrived and are not yet done
        ready = [p for p in ps if p.arrival_time <= t and not p.done]

        if not ready:
            # CPU is idle — jump to the next arrival
            future = [p for p in ps if not p.done]
            if not future:
                break
            next_p = min(future, key=lambda p: p.arrival_time)
            gantt.append({"pid": "IDLE", "start": t, "end": next_p.arrival_time, "color_index": -1})
            t = next_p.arrival_time
            continue

        # Pick the process with the shortest burst time
        current = min(ready, key=lambda p: (p.burst_time, p.arrival_time, p.index))

        # Response time = first CPU access − arrival (in SJF this = t − arrival)
        current.response_time = t - current.arrival_time

        gantt.append({
            "pid"        : current.pid,
            "start"      : t,
            "end"        : t + current.burst_time,
            "color_index": current.index,
        })

        t                   += current.burst_time
        current.finish_time      = t
        current.turnaround_time  = t - current.arrival_time
        current.waiting_time     = current.turnaround_time - current.burst_time
        current.done             = True
        done_count              += 1

    metrics = [p.to_dict() for p in ps]
    return gantt, metrics
