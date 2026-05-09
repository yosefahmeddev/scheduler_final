from backend.process import Process


def validate(raw_processes: list[dict], quantum_raw) -> tuple:
    """
    Parameters
    ----------
    raw_processes : list of dicts with keys "pid", "at", "bt"
    quantum_raw   : the quantum value from the form (int or string)

    Returns
    -------
    (True,  processes, quantum)   on success
    (False, None,      message)   on failure
    """

    # validate quantum
    try:
        quantum = int(quantum_raw)
    except (ValueError, TypeError):
        return False, None, "Quantum must be a whole number (e.g. 3)."

    if quantum < 1:
        return False, None, f"Invalid quantum '{quantum_raw}': must be ≥ 1."
    if quantum > 100:
        return False, None, "Quantum is too large. Maximum allowed is 100."

    #at least one process must exist
    if not raw_processes:
        return False, None, "Please add at least one process."

    seen_pids = set()
    processes = []

    for i, row in enumerate(raw_processes):
        pid    = str(row.get("pid", "")).strip()
        at_str = str(row.get("at",  "")).strip()
        bt_str = str(row.get("bt",  "")).strip()

        # PID must not be empty
        if not pid:
            return False, None, f"Row {i + 1}: Process ID cannot be empty."

        # PID must be unique
        if pid in seen_pids:
            return False, None, f"Duplicate Process ID '{pid}'. All PIDs must be unique."
        seen_pids.add(pid)

        # Arrival time must be a non-negative integer
        try:
            at = int(at_str)
        except ValueError:
            return False, None, f"{pid}: Arrival time must be a whole number."
        if at < 0:
            return False, None, f"{pid}: Arrival time cannot be negative."

        # Burst time must be a positive integer
        try:
            bt = int(bt_str)
        except ValueError:
            return False, None, f"{pid}: Burst time must be a whole number."
        if bt < 1:
            return False, None, f"{pid}: Burst time must be at least 1."
        if bt > 999:
            return False, None, f"{pid}: Burst time is too large (max 999)."

        processes.append(Process(pid, at, bt, index=i))

    return True, processes, quantum
