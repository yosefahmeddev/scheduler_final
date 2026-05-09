const PROCESS_COLORS = [
  "#5c7cfa", "#40c975", "#f5a623", "#f05555",
  "#b06bff", "#2dcec3", "#ff6eb4", "#ffb347",
];

const IDLE_COLOR = "#2e3050";


async function loadScenario(key) {
  if (key === "custom") {
    clearTable();
    document.getElementById("quantumInput").value = "3";
    hideValidation();
    return;
  }

  try {
    const res = await fetch(`/scenario/${key}`);
    const data = await res.json();

    // Set the quantum input
    document.getElementById("quantumInput").value = data.quantum;

    // Rebuild the process table with the scenario's processes
    clearTable();
    data.procs.forEach(p => addRow(p.pid, p.at, p.bt));

  } catch (err) {
    showValidation("Could not load scenario. Is the server running?", "error");
  }
}

// Auto-generated PID names in order
const PID_NAMES = ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9", "P10"];

function getNextPid() {
  // Find the first PID name not already used in the table
  const used = getTableData().map(r => r.pid);
  return PID_NAMES.find(id => !used.includes(id)) || `P${used.length + 1}`;
}

function addRow(pid = null, at = 0, bt = 4) {
  const tbody = document.getElementById("procBody");
  const row = document.createElement("tr");
  const index = tbody.rows.length;           // row number = colour index
  const color = PROCESS_COLORS[index % PROCESS_COLORS.length];
  const usedPid = pid ?? getNextPid();

  row.innerHTML = `
    <td>
      <span class="proc-dot" style="background:${color}"></span>
      <input type="text"   value="${usedPid}" style="color:${color};font-weight:700;width:45px">
    </td>
    <td><input type="number" value="${at}" min="0"  style="width:50px"></td>
    <td><input type="number" value="${bt}" min="1"  style="width:50px"></td>
    <td>
      <button class="btn-delete" onclick="deleteRow(this)">✕</button>
    </td>
  `;
  tbody.appendChild(row);
}

function deleteRow(btn) {
  btn.closest("tr").remove();
}

function clearTable() {
  document.getElementById("procBody").innerHTML = "";
}

function getTableData() {
  const rows = document.querySelectorAll("#procBody tr");
  return Array.from(rows).map(row => {
    const inputs = row.querySelectorAll("input");
    return {
      pid: inputs[0].value.trim(),
      at: parseInt(inputs[1].value) || 0,
      bt: parseInt(inputs[2].value) || 1,
    };
  });
}

function switchTab(name, clickedBtn) {
  // Deactivate all tab buttons and panes
  document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
  document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));

  // Activate the clicked one
  clickedBtn.classList.add("active");
  document.getElementById("pane-" + name).classList.add("active");
}


function showValidation(msg, type) {
  const el = document.getElementById("valMsg");
  el.textContent = msg;
  el.className = `val-msg show ${type}`;  // .show.error  or  .show.success
}

function hideValidation() {
  const el = document.getElementById("valMsg");
  el.className = "val-msg";  // removes .show
}

async function runSimulation() {
  const quantum = parseInt(document.getElementById("quantumInput").value);
  const processes = getTableData();

  // Build the request body matching SimulateRequest in backend/main.py
  const body = { quantum, processes };

  try {
    const res = await fetch("/simulate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      // The backend returned a 422 validation error
      const err = await res.json();
      showValidation((err.detail || "Validation error."), "error");
      return;
    }

    const data = await res.json();
    showValidation("Simulation complete.", "success");

    // Render all sections with the returned data
    renderQueue(data.rr.queue_snapshot);
    renderGantt(data.rr.gantt, "rrGantt");
    renderGantt(data.sjf.gantt, "sjfGantt");
    renderMetrics(data.rr.metrics, data.rr.averages, "rrMetrics");
    renderMetrics(data.sjf.metrics, data.sjf.averages, "sjfMetrics");
    renderComparison(data.rr.averages, data.sjf.averages);
    renderConclusion(data.analysis, data.conclusion);

  } catch (err) {
    showValidation("Could not reach the server.", "error");
  }
}


function renderQueue(snapshot) {
  const container = document.getElementById("rrQueue");

  if (!snapshot || snapshot.length === 0) {
    container.innerHTML = '<span class="queue-empty">Queue empty at end of simulation</span>';
    return;
  }

  let html = '<span class="queue-head">HEAD</span>';

  snapshot.forEach((p, i) => {
    const color = PROCESS_COLORS[p.index % PROCESS_COLORS.length];
    if (i > 0) html += '<span class="queue-arrow">→</span>';
    html += `
      <span class="queue-item">
        <span class="proc-dot" style="background:${color}"></span>
        <span style="color:${color};font-weight:700">${p.pid}</span>
        <span class="q-rem">rem:${p.remaining_time ?? ""}</span>
      </span>`;
  });

  html += '<span class="queue-tail">TAIL</span>';
  container.innerHTML = html;
}


function renderGantt(segments, containerId) {
  const wrap = document.getElementById(containerId);

  if (!segments || segments.length === 0) {
    wrap.innerHTML = '<div class="gantt-placeholder">No data</div>';
    return;
  }

  const UNIT = 28;    // pixels per time unit
  const BAR_Y = 12;    // y-position of the top of each bar
  const BAR_H = 32;    // height of each bar
  const TICK_Y = BAR_Y + BAR_H;
  const totalTime = segments[segments.length - 1].end;
  const W = Math.max(500, totalTime * UNIT + 50);
  const H = 72;

  // Build the SVG string
  let svg = `<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg">`;

  // Draw each segment as a rounded rectangle + label
  segments.forEach(seg => {
    const x = 20 + seg.start * UNIT;
    const w = (seg.end - seg.start) * UNIT;

    const fill = seg.pid === "IDLE" ? IDLE_COLOR
      : PROCESS_COLORS[seg.color_index % PROCESS_COLORS.length];
    const tCol = seg.pid === "IDLE" ? "#555980" : "#ffffff";
    const alpha = seg.pid === "IDLE" ? 0.6 : 0.92;

    svg += `<rect x="${x}" y="${BAR_Y}" width="${w - 1}" height="${BAR_H}"
              rx="4" fill="${fill}" opacity="${alpha}"/>`;

    // Only draw the label if the block is wide enough to fit it
    if (w > 18) {
      svg += `<text x="${x + w / 2}" y="${BAR_Y + BAR_H / 2 + 1}"
                text-anchor="middle" dominant-baseline="central"
                fill="${tCol}" font-family="Courier New,monospace"
                font-size="10" font-weight="500">${seg.pid}</text>`;
    }
  });

  // Draw the time axis (tick marks + numbers)
  const step = Math.max(1, Math.floor(totalTime / 15));
  for (let i = 0; i <= totalTime; i += step) {
    const x = 20 + i * UNIT;
    svg += `<line x1="${x}" y1="${TICK_Y}" x2="${x}" y2="${TICK_Y + 4}"
              stroke="#555980" stroke-width="0.5"/>`;
    svg += `<text x="${x}" y="${TICK_Y + 14}" text-anchor="middle"
              fill="#555980" font-family="Courier New,monospace" font-size="9">${i}</text>`;
  }
  // Always show the final time value
  const xEnd = 20 + totalTime * UNIT;
  svg += `<line x1="${xEnd}" y1="${TICK_Y}" x2="${xEnd}" y2="${TICK_Y + 4}"
            stroke="#555980" stroke-width="0.5"/>`;
  svg += `<text x="${xEnd}" y="${TICK_Y + 14}" text-anchor="middle"
            fill="#555980" font-family="Courier New,monospace" font-size="9">${totalTime}</text>`;

  svg += "</svg>";
  wrap.innerHTML = svg;
}

function renderMetrics(metrics, averages, containerId) {
  const wrap = document.getElementById(containerId);

  let html = `
    <div class="metrics-table-wrap">
      <table class="metrics-table">
        <thead>
          <tr>
            <th>PID</th><th>Arrival</th><th>Burst</th>
            <th>Finish</th><th>WT</th><th>TAT</th><th>RT</th>
          </tr>
        </thead>
        <tbody>`;

  metrics.forEach(p => {
    const color = PROCESS_COLORS[p.index % PROCESS_COLORS.length];
    html += `
      <tr>
        <td style="color:${color};font-weight:700">${p.pid}</td>
        <td>${p.arrival_time}</td>
        <td>${p.burst_time}</td>
        <td>${p.finish_time}</td>
        <td>${p.waiting_time}</td>
        <td>${p.turnaround_time}</td>
        <td>${p.response_time}</td>
      </tr>`;
  });

  html += `
          <tr class="avg-row">
            <td>AVERAGES</td>
            <td>—</td><td>—</td><td>—</td>
            <td>${averages.avg_wt}</td>
            <td>${averages.avg_tat}</td>
            <td>${averages.avg_rt}</td>
          </tr>
        </tbody>
      </table>
    </div>`;

  wrap.innerHTML = html;
}


function renderComparison(rrAvg, sjfAvg) {
  const grid = document.getElementById("compareGrid");

  const metrics = [
    { label: "Avg Waiting Time", rr: rrAvg.avg_wt, sjf: sjfAvg.avg_wt },
    { label: "Avg Turnaround Time", rr: rrAvg.avg_tat, sjf: sjfAvg.avg_tat },
    { label: "Avg Response Time", rr: rrAvg.avg_rt, sjf: sjfAvg.avg_rt },
  ];

  grid.innerHTML = metrics.map(m => {
    const rrWins = m.rr <= m.sjf;
    const tie = m.rr === m.sjf;
    const max = Math.max(m.rr, m.sjf, 0.01);
    const rrPct = ((m.rr / max) * 100).toFixed(0);
    const sjfPct = ((m.sjf / max) * 100).toFixed(0);
    const winner = tie ? "Tie" : rrWins ? "▲ RR wins" : "▲ SJF wins";
    const wCol = tie ? "#f5a623" : rrWins ? "#5c7cfa" : "#40c975";
    const border = tie ? "#f5a623" : rrWins ? "#5c7cfa" : "#40c975";

    return `
      <div class="metric-card" style="border-left-color:${border}">
        <div class="metric-card-title">${m.label}</div>

        <div class="mbar-row">
          <span class="mbar-label" style="color:#5c7cfa">RR</span>
          <div class="mbar-track">
            <div class="mbar-fill" style="width:${rrPct}%;background:#5c7cfa"></div>
          </div>
          <span class="mbar-val">${m.rr}</span>
        </div>

        <div class="mbar-row">
          <span class="mbar-label" style="color:#40c975">SJF</span>
          <div class="mbar-track">
            <div class="mbar-fill" style="width:${sjfPct}%;background:#40c975"></div>
          </div>
          <span class="mbar-val">${m.sjf}</span>
        </div>

        <div class="winner-tag" style="color:${wCol}">${winner}</div>
      </div>`;
  }).join("");
}

function renderConclusion(analysis, conclusion) {
  // 6 Q&A items in a 2-column grid
  const qaGrid = document.getElementById("qaGrid");
  qaGrid.innerHTML = analysis.map(item => `
    <div class="qa-card">
      <div class="qa-question">${item.question}</div>
      <div class="qa-answer">${item.answer}</div>
    </div>`).join("");

  // 3 summary cards
  const cards = document.getElementById("conclusionCards");
  cards.innerHTML = conclusion.map(c => `
    <div class="conc-card" style="border-top-color:${c.color}">
      <div class="conc-title" style="color:${c.color}">${c.title}</div>
      <div class="conc-body">${c.body}</div>
    </div>`).join("");

  // Make the whole panel visible
  document.getElementById("conclusionPanel").style.display = "block";
}

document.addEventListener("DOMContentLoaded", () => {
  loadScenario("A");   // load Scenario A as the default
});
