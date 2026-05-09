def compute_averages(metrics: list[dict]) -> tuple:
    """
    Given a list of process result dicts, return (avg_wt, avg_tat, avg_rt).
    All values are rounded to 2 decimal places.
    """
    n = len(metrics)
    if n == 0:
        return 0.0, 0.0, 0.0

    avg_wt  = round(sum(p["waiting_time"]    for p in metrics) / n, 2)
    avg_tat = round(sum(p["turnaround_time"] for p in metrics) / n, 2)
    avg_rt  = round(sum(p["response_time"]   for p in metrics) / n, 2)

    return avg_wt, avg_tat, avg_rt


def generate_analysis(rr_avgs: tuple, sjf_avgs: tuple, processes: list, quantum: int) -> list:
    """
    Return the 6 required analysis Q&A as a list of
    {"question": str, "answer": str} dicts.
    """
    rr_wt,  rr_tat,  rr_rt  = rr_avgs
    sjf_wt, sjf_tat, sjf_rt = sjf_avgs

    wt_winner = "Round Robin" if rr_wt <= sjf_wt else "SJF"
    rt_winner = "Round Robin" if rr_rt <= sjf_rt else "SJF"

    has_long  = any(p.burst_time >= 10 for p in processes)
    all_equal = len(set(p.burst_time for p in processes)) == 1

    if quantum <= 2:
        q_effect = (f"Q={quantum} is very small — the CPU switches between processes "
                    f"very frequently. Very fair, but high context-switch overhead.")
    elif quantum <= 5:
        q_effect = (f"Q={quantum} is balanced — good response time with "
                    f"manageable context-switch overhead.")
    else:
        q_effect = (f"Q={quantum} is large — Round Robin starts to behave like FCFS. "
                    f"Later processes wait longer before their first turn.")

    if sjf_wt < rr_wt and sjf_tat < rr_tat:
        rec = ("SJF — it produced lower average wait and turnaround times for this workload. "
               "Use Round Robin for interactive or real-time systems.")
    else:
        rec = ("Round Robin — it gave more balanced response times and fairer "
               "CPU distribution across all processes.")

    return [
        {
            "question": "1. Which algorithm gave lower average waiting time?",
            "answer"  : f"{wt_winner}  (RR: {rr_wt}, SJF: {sjf_wt})",
        },
        {
            "question": "2. Which algorithm gave lower average response time?",
            "answer"  : f"{rt_winner}  (RR: {rr_rt}, SJF: {sjf_rt})",
        },
        {
            "question": "3. Did Round Robin appear fairer across all processes?",
            "answer"  : (
                "With equal burst times both algorithms behave similarly."
                if all_equal else
                "Yes — Round Robin gave every process a turn in rotation, preventing starvation."
            ),
        },
        {
            "question": "4. Did SJF complete short jobs more efficiently?",
            "answer"  : (
                "Yes — SJF prioritised short jobs, but the long process suffered a big delay."
                if has_long else
                "Yes — SJF always chose the shortest job, minimising average waiting time."
            ),
        },
        {
            "question": f"5. How did quantum Q={quantum} affect Round Robin?",
            "answer"  : q_effect,
        },
        {
            "question": "6. Which algorithm would you recommend for this workload?",
            "answer"  : rec,
        },
    ]


def generate_conclusion(rr_avgs: tuple, sjf_avgs: tuple, processes: list, quantum: int) -> list:
    """
    Return 3 conclusion cards as a list of
    {"title": str, "color": str, "body": str} dicts.
    """
    rr_wt,  _, _ = rr_avgs
    sjf_wt, _, _ = sjf_avgs
    has_long = any(p.burst_time >= 10 for p in processes)

    rr_body = (
        f"{'Better average waiting time.' if rr_wt <= sjf_wt else 'Higher average wait than SJF.'} "
        f"Distributes CPU time equally with Q={quantum}. "
        f"No process is ever starved. Ideal for interactive, time-sharing systems."
    )

    sjf_body = (
        f"{'Optimal average waiting time.' if sjf_wt <= rr_wt else 'Average wait is higher than RR.'} "
        f"Always picks the shortest available job. "
        + (
            "Long processes risk starvation when many short jobs keep arriving."
            if has_long else
            "No starvation observed in this workload."
        )
    )

    if quantum <= 2:
        q_body = "Quantum too small — too many context switches, high overhead."
    elif quantum <= 6:
        q_body = "Balanced quantum — good response time with manageable overhead."
    else:
        q_body = "Large quantum — Round Robin loses responsiveness and approaches FCFS behaviour."

    return [
        {"title": "Round Robin",                "color": "#5c7cfa", "body": rr_body},
        {"title": "SJF (Non-preemptive)",       "color": "#40c975", "body": sjf_body},
        {"title": f"Quantum Effect  Q={quantum}", "color": "#f5a623", "body": q_body},
    ]
