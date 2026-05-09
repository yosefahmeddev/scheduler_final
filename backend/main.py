# backend/main.py
# ─────────────────────────────────────────────────────────────────────────────
# FastAPI server — the backend of the whole application.
#
# What it does:
#   - Runs a local web server at  http://localhost:8000
#   - Serves the frontend HTML/CSS/JS files to the browser
#   - Exposes two API endpoints the frontend calls via fetch():
#
#       GET  /scenario/{key}   →  returns a pre-built test scenario
#       POST /simulate         →  runs RR + SJF, returns all results as JSON
#
# How to start:
#   uvicorn backend.main:app --reload
# ─────────────────────────────────────────────────────────────────────────────

import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses   import FileResponse
from pydantic import BaseModel

from backend.validator   import validate
from backend.round_robin import run_round_robin
from backend.sjf         import run_sjf
from backend.metrics     import compute_averages, generate_analysis, generate_conclusion
from backend.scenarios   import SCENARIOS

app = FastAPI(
    title       = "CPU Scheduler API",
    description = "Round Robin vs SJF — OS Course Project C5",
    version     = "1.0.0",
)
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


class ProcessInput(BaseModel):
    pid: str # process name  e.g. "P1"
    at : int # arrival time
    bt : int # burst time

class SimulateRequest(BaseModel):
    quantum  : int # time quantum for Round Robin
    processes: list[ProcessInput]  # list of processes from the table

@app.get("/")
def serve_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


@app.get("/scenario/{key}")
def get_scenario(key: str):

    key = key.upper()
    if key not in SCENARIOS:
        raise HTTPException(status_code=404, detail=f"Scenario '{key}' not found.")
    return SCENARIOS[key]


@app.post("/simulate")
def simulate(body: SimulateRequest):
    # Step 1 — convert to plain dicts
    raw = [{"pid": p.pid, "at": str(p.at), "bt": str(p.bt)} for p in body.processes]

    # Step 2 — validate
    ok, processes, result = validate(raw, body.quantum)
    if not ok:
        raise HTTPException(status_code=422, detail=result)
    quantum = result

    # Step 3 — Round Robin
    rr_gantt, rr_metrics, rr_queue = run_round_robin(processes, quantum)

    # Step 4 — SJF
    sjf_gantt, sjf_metrics = run_sjf(processes)

    # Step 5 — averages
    rr_avgs  = compute_averages(rr_metrics)
    sjf_avgs = compute_averages(sjf_metrics)

    # Step 6 — analysis text
    analysis   = generate_analysis(rr_avgs, sjf_avgs, processes, quantum)
    conclusion = generate_conclusion(rr_avgs, sjf_avgs, processes, quantum)

    # Step 7 — return JSON
    return {
        "rr": {
            "gantt"         : rr_gantt,
            "metrics"       : rr_metrics,
            "queue_snapshot": rr_queue,
            "averages"      : {"avg_wt": rr_avgs[0], "avg_tat": rr_avgs[1], "avg_rt": rr_avgs[2]},
        },
        "sjf": {
            "gantt"  : sjf_gantt,
            "metrics": sjf_metrics,
            "averages": {"avg_wt": sjf_avgs[0], "avg_tat": sjf_avgs[1], "avg_rt": sjf_avgs[2]},
        },
        "analysis"  : analysis,
        "conclusion": conclusion,
    }
