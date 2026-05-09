# CPU Scheduling Comparison — Round Robin vs SJF
### Operating Systems Course | Project C5 | FastAPI + HTML/CSS/JS

---

## How to Run  (3 steps)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the server
uvicorn backend.main:app --reload

# 3. Open your browser at
http://localhost:8000
```

---

## Project Structure

```
scheduler_final/
│
├── requirements.txt          ← pip install -r requirements.txt
│
├── backend/                  ← Python / FastAPI (server-side logic)
│   ├── __init__.py           ← makes backend/ a Python package
│   ├── main.py               ← FastAPI app, all API routes
│   ├── process.py            ← Process class (one process's data)
│   ├── validator.py          ← validates all input before simulation
│   ├── round_robin.py        ← Round Robin scheduling algorithm
│   ├── sjf.py                ← SJF (non-preemptive) algorithm
│   ├── metrics.py            ← averages + analysis/conclusion text
│   └── scenarios.py          ← pre-defined test cases A – E
│
└── frontend/                 ← HTML / CSS / JS (browser-side)
    ├── index.html            ← the page the browser loads
    ├── css/
    │   └── style.css         ← ALL styles (no inline CSS in HTML)
    └── js/
        └── app.js            ← ALL interactivity and rendering
```

---

## How the Two Sides Talk

```
Browser (frontend)                    Server (backend)
──────────────────                    ────────────────
Page loads
  → fetch GET /scenario/A    ──────►  returns scenario data as JSON
  → fills the form

User clicks ▶ Run
  → fetch POST /simulate     ──────►  validates input
     { quantum, processes }           runs RoundRobin + SJF
                                      computes averages
                             ◄──────  returns JSON with all results
  → draws Gantt charts
  → fills metrics tables
  → shows comparison cards
  → shows conclusion panel
```

---

## API Endpoints

| Method | URL | What it does |
|---|---|---|
| GET | `/` | Serves the HTML page |
| GET | `/scenario/{key}` | Returns scenario A/B/C/D/E data |
| POST | `/simulate` | Runs simulation, returns all results |

---

## File Roles (plain English)

| File | Role |
|---|---|
| `backend/main.py` | Receives requests, calls the right functions, returns JSON |
| `backend/process.py` | A container class for one process and its results |
| `backend/validator.py` | Rejects bad input before anything runs |
| `backend/round_robin.py` | The RR algorithm — queue rotation, time slicing |
| `backend/sjf.py` | The SJF algorithm — always picks shortest burst |
| `backend/metrics.py` | Averages WT/TAT/RT, writes analysis text |
| `backend/scenarios.py` | Stores the 5 preset test cases |
| `frontend/index.html` | The page layout — no styles, no logic |
| `frontend/css/style.css` | Every colour, size, and visual rule |
| `frontend/js/app.js` | Sends API requests, draws Gantt SVGs, builds tables |
