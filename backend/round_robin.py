# ─────────────────────────────────────────────────────────────────────────────
# Round Robin (RR) Scheduling Algorithm
#
#   1. Maintain a queue of processes that have arrived.
#   2. Take the process at the FRONT of the queue.
#   3. Let it run for at most Q time units (the "quantum").
#   4. If it finishes within Q  →  record its finish time.
#   5. If it does NOT finish    →  put it at the BACK of the queue.
#   6. Repeat until every process is done.
# ─────────────────────────────────────────────────────────────────────────────

import copy

def run_round_robin(processes: list, quantum: int) -> tuple:
    """
    Parameters
    ----------
    processes : list[Process]   already-validated Process objects
    quantum   : int             CPU time units per slice

    Returns
    -------
    gantt          : list of dicts  {pid, start, end, color_index}
    metrics        : list of dicts  per-process results
    queue_snapshot : list of dicts  processes still waiting at the end
    """

    ps = copy.deepcopy(processes)

    gantt        = []
    queue        = []
    arrived      = set()
    t            = 0
    done_count   = 0
    total        = len(ps)

    # ── Helper: add processes that have arrived by `now` ──────────────────
    def enqueue_arrived(now: int):
        new = [
            p for p in ps
            if p.arrival_time <= now
            and p.pid not in arrived
            and p.remaining_time > 0
        ]
        # Earlier arrivals go in first; tie-break by original index
        new.sort(key=lambda p: (p.arrival_time, p.index))
        for p in new:
            queue.append(p)
            arrived.add(p.pid)

    enqueue_arrived(0)   # seed with anything arriving at time 0

    # ── Main simulation loop ──────────────────────────────────────────────
    iterations = 0
    while done_count < total and iterations < 10_000:
        iterations += 1

        if not queue:
            # CPU is idle — jump to the next process arrival
            waiting = [p for p in ps if p.pid not in arrived and p.remaining_time > 0]
            if not waiting:
                break
            next_p = min(waiting, key=lambda p: p.arrival_time)
            gantt.append({"pid": "IDLE", "start": t, "end": next_p.arrival_time, "color_index": -1})
            t = next_p.arrival_time
            enqueue_arrived(t)
            continue

        # Take process from the front of the queue
        current = queue.pop(0)

        # Record the very first time this process reaches the CPU
        if current.response_time == -1:
            current.response_time = t - current.arrival_time

        # How long does this time slice actually run?
        exec_time = min(quantum, current.remaining_time)

        gantt.append({
            "pid"        : current.pid,
            "start"      : t,
            "end"        : t + exec_time,
            "color_index": current.index,
        })

        t                      += exec_time
        current.remaining_time -= exec_time

        # Enqueue newly arrived processes BEFORE re-queuing the current one
        # (correct Round Robin ordering)
        enqueue_arrived(t)

        if current.remaining_time > 0:
            queue.append(current)          # not done → back of the queue
        else:
            current.finish_time      = t
            current.turnaround_time  = t - current.arrival_time
            current.waiting_time     = current.turnaround_time - current.burst_time
            current.done             = True
            done_count              += 1

    # ── Package results ───────────────────────────────────────────────────
    metrics        = [p.to_dict() for p in ps if p.done]
    queue_snapshot = [p.to_dict() for p in ps if not p.done]

    return gantt, metrics, queue_snapshot
