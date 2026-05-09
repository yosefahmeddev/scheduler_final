SCENARIOS: dict = {
    "A": {
        "label"  : "Scenario A — Basic Mixed Workload",
        "quantum": 3,
        "procs"  : [
            {"pid": "P1", "at": 0, "bt": 6},
            {"pid": "P2", "at": 1, "bt": 4},
            {"pid": "P3", "at": 2, "bt": 2},
            {"pid": "P4", "at": 4, "bt": 8},
            {"pid": "P5", "at": 5, "bt": 3},
        ],
    },
    "B": {
        "label"  : "Scenario B — Short-Job Heavy",
        "quantum": 2,
        "procs"  : [
            {"pid": "P1", "at": 0, "bt": 1},
            {"pid": "P2", "at": 0, "bt": 2},
            {"pid": "P3", "at": 1, "bt": 1},
            {"pid": "P4", "at": 2, "bt": 3},
            {"pid": "P5", "at": 3, "bt": 1},
            {"pid": "P6", "at": 3, "bt": 2},
        ],
    },
    "C": {
        "label"  : "Scenario C — Fairness Case",
        "quantum": 4,
        "procs"  : [
            {"pid": "P1", "at": 0, "bt": 12},
            {"pid": "P2", "at": 0, "bt": 12},
            {"pid": "P3", "at": 0, "bt": 12},
            {"pid": "P4", "at": 0, "bt": 12},
        ],
    },
    "D": {
        "label"  : "Scenario D — Long-Job Sensitivity",
        "quantum": 4,
        "procs"  : [
            {"pid": "P1", "at": 0, "bt": 20},
            {"pid": "P2", "at": 1, "bt": 2},
            {"pid": "P3", "at": 2, "bt": 3},
            {"pid": "P4", "at": 3, "bt": 1},
            {"pid": "P5", "at": 4, "bt": 2},
        ],
    },
}
