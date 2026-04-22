from flask import Flask, render_template_string, Blueprint, request, jsonify
import random

# ==========================================
# 1. Booking Module (Blueprint)
# ==========================================
booking_bp = Blueprint('booking', __name__)

# In-memory storage for bookings: { slot_number: "User Name" }
bookings_db = {}

@booking_bp.route('/book', methods=['POST'])
def book_slot():
    data = request.json
    slot_num = data.get('slot')
    user_name = data.get('user')
    
    if not slot_num or not user_name:
        return jsonify({"error": "Missing slot or user name"}), 400
    
    try:
        slot_num = int(slot_num)
        # Basic validation to ensure slot is within the 1-30 range
        if slot_num < 1 or slot_num > 30:
            return jsonify({"error": "Invalid slot number"}), 400
            
        bookings_db[slot_num] = user_name
        return jsonify({"message": f"Slot {slot_num} reserved for {user_name}"}), 200
    except ValueError:
        return jsonify({"error": "Slot must be a number"}), 400

@booking_bp.route('/bookings', methods=['GET'])
def get_bookings():
    # Return a list of slot numbers that are booked
    return jsonify(list(bookings_db.keys())), 200

# ==========================================
# 2. Main Application
# ==========================================
app = Flask(__name__)
app.register_blueprint(booking_bp)

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>ParkSense AI — Smart Parking System</title>
  <style>
    :root {
      --park-bg: #0d1117;
      --park-surface: #161b22;
      --park-card: #1c2333;
      --park-border: rgba(255,255,255,0.08);
      --park-green: #2ea043;
      --park-red: #da3633;
      --park-blue: #388bfd;
      --park-amber: #e3b341;
      --park-purple: #8957e5;
      --park-text: #e6edf3;
      --park-muted: #7d8590;
      --park-ev: #3fb950;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { background: var(--park-bg); color: var(--park-text); font-family: system-ui, sans-serif; padding: 20px; min-height: 100vh; }
    #psd { max-width: 1100px; margin: 0 auto; }

    .hdr { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
    .hdr-left { display: flex; align-items: center; gap: 10px; }
    .logo { width: 36px; height: 36px; background: linear-gradient(135deg, #388bfd, #8957e5); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 18px; font-weight: bold; color: white; }
    .hdr h1 { font-size: 20px; font-weight: 600; }
    .hdr-badge { font-size: 11px; background: rgba(46,160,67,0.2); color: var(--park-ev); border: 1px solid rgba(46,160,67,0.3); padding: 3px 10px; border-radius: 20px; }
    .ai-badge { font-size: 11px; background: rgba(137,87,229,0.2); color: #a371f7; border: 1px solid rgba(137,87,229,0.3); padding: 3px 10px; border-radius: 20px; margin-left: 6px; }
    .time-display { font-size: 13px; color: var(--park-muted); display: flex; align-items: center; gap: 6px; }
    .pulse-dot { width: 8px; height: 8px; background: var(--park-green); border-radius: 50%; animation: pulse 2s infinite; }
    @keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.5;transform:scale(0.8)} }

    .metrics { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px; }
    .metric-card { background: var(--park-card); border: 1px solid var(--park-border); border-radius: 10px; padding: 14px; position: relative; overflow: hidden; }
    .metric-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; }
    .mc-total::before { background: var(--park-blue); }
    .mc-occupied::before { background: var(--park-red); }
    .mc-empty::before { background: var(--park-green); }
    .mc-ev::before { background: var(--park-purple); }
    .metric-label { font-size: 11px; color: var(--park-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; }
    .metric-val { font-size: 28px; font-weight: 600; line-height: 1; }
    .metric-sub { font-size: 11px; color: var(--park-muted); margin-top: 4px; }
    .metric-icon { position: absolute; right: 12px; top: 12px; font-size: 20px; opacity: 0.25; }

    .main-grid { display: grid; grid-template-columns: 1fr 320px; gap: 16px; margin-bottom: 16px; }
    .panel { background: var(--park-card); border: 1px solid var(--park-border); border-radius: 10px; }
    .panel-hdr { padding: 12px 16px; border-bottom: 1px solid var(--park-border); display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px; }
    .panel-title { font-size: 13px; font-weight: 600; display: flex; align-items: center; gap: 8px; }
    .panel-body { padding: 16px; }

    .lot-container { position: relative; }
    .lot-road { background: #1a1f2e; border-radius: 8px; padding: 12px; }
    .road-entry { text-align: center; font-size: 10px; color: var(--park-muted); margin-bottom: 8px; letter-spacing: 0.1em; }
    .parking-rows { display: flex; flex-direction: column; gap: 8px; }
    .slot-row { display: flex; gap: 5px; align-items: center; }
    .row-id { font-size: 10px; color: var(--park-muted); width: 20px; flex-shrink: 0; }
    .slots-left, .slots-right { display: flex; gap: 5px; flex: 1; }
    .lane { width: 28px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; }
    .lane-line { width: 2px; height: 40px; background: repeating-linear-gradient(to bottom, #f0d060 0px, #f0d060 6px, transparent 6px, transparent 12px); border-radius: 1px; }
    .slot { width: 40px; height: 42px; border-radius: 5px; cursor: pointer; transition: all 0.2s; position: relative; display: flex; flex-direction: column; align-items: center; justify-content: center; border: 1.5px solid transparent; font-size: 9px; font-weight: 600; }
    .slot:hover { transform: scale(1.07); }
    .slot.empty { background: rgba(46,160,67,0.15); border-color: rgba(46,160,67,0.5); color: var(--park-green); }
    .slot.occupied { background: rgba(218,54,51,0.15); border-color: rgba(218,54,51,0.4); color: var(--park-red); cursor: not-allowed; }
    .slot.selected { background: rgba(56,139,253,0.25); border-color: var(--park-blue); color: var(--park-blue); box-shadow: 0 0 0 2px rgba(56,139,253,0.3); }
    .slot.ev-slot { border-style: dashed; }
    .slot.ev-slot.empty { border-color: rgba(63,185,80,0.7); }
    .slot.ev-slot.selected { border-color: var(--park-blue); border-style: solid; }
    .slot-num { font-size: 8px; opacity: 0.7; }
    .slot-icon { font-size: 14px; line-height: 1; }
    .slot-ev-tag { font-size: 7px; background: rgba(63,185,80,0.2); color: var(--park-ev); padding: 1px 3px; border-radius: 2px; margin-top: 1px; }
    .ai-overlay { position: absolute; top: 8px; right: 8px; background: rgba(137,87,229,0.15); border: 1px solid rgba(137,87,229,0.3); border-radius: 6px; padding: 4px 8px; font-size: 10px; color: #a371f7; }
    .detection-bar { margin-top: 8px; background: rgba(137,87,229,0.1); border: 1px solid rgba(137,87,229,0.2); border-radius: 6px; padding: 8px 12px; display: flex; align-items: center; gap: 8px; }
    .det-label { font-size: 11px; color: var(--park-muted); flex: 1; }
    .det-conf { font-size: 11px; color: #a371f7; }
    .conf-bar { flex: 1; height: 3px; background: rgba(255,255,255,0.1); border-radius: 2px; }
    .conf-fill { height: 100%; border-radius: 2px; background: linear-gradient(to right, #8957e5, #388bfd); transition: width 0.5s; }

    @keyframes scanline { 0%{transform:translateY(-90px)} 100%{transform:translateY(90px)} }
    .scanning-overlay { position: absolute; top: 0; left: 0; right: 0; bottom: 0; pointer-events: none; overflow: hidden; border-radius: 8px; display: none; }
    .scan-line { width: 100%; height: 2px; background: linear-gradient(to right, transparent, rgba(137,87,229,0.6), transparent); animation: scanline 1.5s linear infinite; }
    .scanning-overlay.active { display: block; }

    .controls-panel { display: flex; flex-direction: column; gap: 12px; }
    .slot-select { width: 100%; background: #0d1117; color: var(--park-text); border: 1px solid var(--park-border); border-radius: 6px; padding: 8px 10px; font-size: 13px; outline: none; }
    .slot-select:focus { border-color: var(--park-blue); }

    .nav-card { background: rgba(56,139,253,0.08); border: 1px solid rgba(56,139,253,0.2); border-radius: 8px; padding: 10px; margin-top: 10px; display: none; }
    .nav-title { font-size: 11px; color: var(--park-blue); margin-bottom: 8px; }
    .nav-route { display: flex; align-items: center; gap: 4px; flex-wrap: wrap; margin: 6px 0; }
    .nav-step { font-size: 11px; background: rgba(56,139,253,0.15); color: var(--park-blue); padding: 3px 8px; border-radius: 4px; }
    .nav-arrow { font-size: 12px; color: var(--park-muted); }
    .nav-dist { font-size: 13px; font-weight: 600; color: var(--park-text); }
    .nav-time { font-size: 11px; color: var(--park-muted); }

    .ev-alert { background: rgba(63,185,80,0.1); border: 1px solid rgba(63,185,80,0.3); border-radius: 8px; padding: 10px; margin-top: 10px; display: none; }
    .ev-alert.show { display: block; }
    .ev-alert-title { font-size: 12px; color: var(--park-ev); margin-bottom: 4px; font-weight: 600; }
    .ev-alert-body { font-size: 11px; color: var(--park-muted); }

    .btn { display: inline-flex; align-items: center; gap: 6px; padding: 8px 14px; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer; transition: all 0.2s; border: 1px solid; background: none; }
    .btn-primary { background: rgba(56,139,253,0.15); color: var(--park-blue); border-color: rgba(56,139,253,0.3); }
    .btn-primary:hover { background: rgba(56,139,253,0.25); }
    .btn-ghost { background: rgba(255,255,255,0.04); color: var(--park-muted); border-color: var(--park-border); }
    .btn-ghost:hover { background: rgba(255,255,255,0.08); color: var(--park-text); }
    .btn-scan { background: rgba(137,87,229,0.15); color: #a371f7; border-color: rgba(137,87,229,0.3); }
    .btn-scan:hover { background: rgba(137,87,229,0.25); }
    .action-row { display: flex; gap: 8px; flex-wrap: wrap; }

    .legend { display: flex; gap: 12px; flex-wrap: wrap; }
    .legend-item { display: flex; align-items: center; gap: 5px; font-size: 11px; color: var(--park-muted); }
    .leg-dot { width: 10px; height: 10px; border-radius: 2px; }

    .feed-container { margin-top: 12px; background: rgba(0,0,0,0.3); border-radius: 8px; padding: 10px; height: 90px; overflow-y: auto; }
    .feed-item { font-size: 11px; color: var(--park-muted); padding: 2px 0; display: flex; align-items: center; gap: 6px; }
    .feed-time { color: #388bfd; font-family: monospace; font-size: 10px; flex-shrink: 0; }
    .feed-dot { width: 5px; height: 5px; border-radius: 50%; flex-shrink: 0; }

    .insights-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
    .insight-card { background: var(--park-card); border: 1px solid var(--park-border); border-radius: 10px; padding: 14px; }
    .insight-title { font-size: 11px; color: var(--park-muted); margin-bottom: 8px; }
    .insight-val { font-size: 22px; font-weight: 600; }
    .insight-desc { font-size: 11px; color: var(--park-muted); margin-top: 4px; }
    .progress-bar { height: 6px; background: rgba(255,255,255,0.08); border-radius: 3px; margin-top: 8px; }
    .progress-fill { height: 100%; border-radius: 3px; transition: width 0.5s; }
    .occupancy-fill { background: linear-gradient(to right, var(--park-green), var(--park-amber), var(--park-red)); }
    .fuel-fill { background: linear-gradient(to right, #3fb950, #2ea043); }
    #heatmap { display: flex; gap: 3px; align-items: flex-end; height: 60px; }

    @media (max-width: 768px) {
      .main-grid { grid-template-columns: 1fr; }
      .metrics { grid-template-columns: repeat(2, 1fr); }
      .insights-row { grid-template-columns: repeat(2, 1fr); }
    }
  </style>
</head>
<body>
<div id="psd">

  <div class="hdr">
    <div class="hdr-left">
      <div class="logo">P</div>
      <div>
        <h1>ParkSense AI</h1>
        <div style="display:flex;align-items:center;gap:4px;margin-top:3px">
          <span class="hdr-badge">&#9679; Live</span>
          <span class="ai-badge">YOLO v8 Active</span>
        </div>
      </div>
    </div>
    <div style="text-align:right">
      <div class="time-display"><span class="pulse-dot"></span><span id="clock">00:00:00</span></div>
      <div style="font-size:11px;color:var(--park-muted);margin-top:3px">Sector 4 — City Mall Parking</div>
    </div>
  </div>

  <div class="metrics">
    <div class="metric-card mc-total">
      <div class="metric-label">Total Slots</div>
      <div class="metric-val" id="m-total">30</div>
      <div class="metric-sub">Across 5 rows</div>
      <div class="metric-icon">P</div>
    </div>
    <div class="metric-card mc-occupied">
      <div class="metric-label">Occupied</div>
      <div class="metric-val" id="m-occ" style="color:var(--park-red)">--</div>
      <div class="metric-sub" id="m-occ-pct">--% capacity</div>
      <div class="metric-icon">&#128663;</div>
    </div>
    <div class="metric-card mc-empty">
      <div class="metric-label">Available</div>
      <div class="metric-val" id="m-empty" style="color:var(--park-green)">--</div>
      <div class="metric-sub">Slots open now</div>
      <div class="metric-icon">&#10003;</div>
    </div>
    <div class="metric-card mc-ev">
      <div class="metric-label">EV Charging</div>
      <div class="metric-val" id="m-ev" style="color:var(--park-purple)">6</div>
      <div class="metric-sub" id="m-ev-sub">Stations total</div>
      <div class="metric-icon">&#9889;</div>
    </div>
  </div>

  <div class="main-grid">
    <div class="panel">
      <div class="panel-hdr">
        <span class="panel-title">&#128205; Live Parking Layout — Row A–E</span>
        <div class="legend">
          <div class="legend-item"><div class="leg-dot" style="background:rgba(46,160,67,0.5);border:1px solid var(--park-green)"></div>Empty</div>
          <div class="legend-item"><div class="leg-dot" style="background:rgba(218,54,51,0.5)"></div>Occupied</div>
          <div class="legend-item"><div class="leg-dot" style="background:rgba(56,139,253,0.5)"></div>Selected</div>
          <div class="legend-item"><div class="leg-dot" style="background:transparent;border:1px dashed var(--park-ev)"></div>EV</div>
        </div>
      </div>
      <div class="panel-body">
        <div class="lot-container">
          <div class="scanning-overlay" id="scan-overlay"><div class="scan-line"></div></div>
          <div class="lot-road">
            <div class="road-entry">&#8595; ENTRANCE</div>
            <div class="parking-rows" id="parking-grid"></div>
            <div class="road-entry" style="margin-top:8px;margin-bottom:0">EXIT &#8593;</div>
          </div>
          <div class="ai-overlay" id="ai-status">AI Ready</div>
        </div>
        <div class="detection-bar">
          <div class="det-label">YOLO Detection Confidence</div>
          <div class="conf-bar"><div class="conf-fill" id="conf-fill" style="width:94%"></div></div>
          <div class="det-conf" id="conf-val">94%</div>
        </div>
        <div id="feed-log" class="feed-container"></div>
      </div>
    </div>

    <div class="controls-panel">
      <div class="panel">
        <div class="panel-hdr"><span class="panel-title">&#128269; Select a Slot</span></div>
        <div class="panel-body">
          <select class="slot-select" id="slot-select" onchange="selectSlotFromDropdown(this.value)">
            <option value="">-- Choose available slot --</option>
          </select>
          <div class="nav-card" id="nav-card">
            <div class="nav-title">&#9654; Route Guidance</div>
            <div class="nav-route" id="nav-route"></div>
            <div style="display:flex;justify-content:space-between;margin-top:6px">
              <div><div class="nav-dist" id="nav-dist">--</div><div class="nav-time" id="nav-time">Est. time</div></div>
              <div style="text-align:right"><div class="nav-dist" id="nav-slot">--</div><div class="nav-time">Slot ID</div></div>
            </div>
          </div>
          <div class="ev-alert" id="ev-alert">
            <div class="ev-alert-title">&#9889; EV Charging Available</div>
            <div class="ev-alert-body">This slot supports up to 22kW AC charging. Connect your vehicle after parking.</div>
          </div>
        </div>
      </div>

      <div class="panel">
        <div class="panel-hdr"><span class="panel-title">&#9881; Controls</span></div>
        <div class="panel-body">
          <div class="action-row">
            <button class="btn btn-scan" onclick="runAIScan()">&#128247; AI Scan</button>
            <button class="btn btn-primary" onclick="refreshData()">&#8635; Refresh</button>
            <button class="btn btn-ghost" onclick="resetSelection()">&#215; Clear</button>
          </div>
          <div style="margin-top:10px;font-size:11px;color:var(--park-muted)">
            Auto-refresh: <span id="countdown" style="color:var(--park-text);font-weight:600">30s</span>
          </div>
        </div>
      </div>

      <div class="panel">
        <div class="panel-hdr"><span class="panel-title">&#128293; Occupancy Heatmap</span></div>
        <div class="panel-body">
          <div id="heatmap"></div>
          <div style="display:flex;justify-content:space-between;font-size:10px;color:var(--park-muted);margin-top:4px">
            <span>Row A</span><span>B</span><span>C</span><span>D</span><span>Row E</span>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class="insights-row">
    <div class="insight-card">
      <div class="insight-title">&#127981; Occupancy Rate</div>
      <div class="insight-val" id="occ-rate" style="color:var(--park-amber)">--</div>
      <div class="insight-desc">Real-time lot utilization</div>
      <div class="progress-bar"><div class="progress-fill occupancy-fill" id="occ-bar" style="width:0%"></div></div>
    </div>
    <div class="insight-card">
      <div class="insight-title">&#9981; Fuel Saved</div>
      <div class="insight-val" id="fuel-saved" style="color:var(--park-green)">--</div>
      <div class="insight-desc">vs avg 8-min search time</div>
      <div class="progress-bar"><div class="progress-fill fuel-fill" id="fuel-bar" style="width:0%"></div></div>
    </div>
    <div class="insight-card">
      <div class="insight-title">&#128204; Peak Hours Prediction</div>
      <div class="insight-val" style="color:var(--park-blue)">1–3h</div>
      <div class="insight-desc">AI forecast: high load expected</div>
    </div>
    <div class="insight-card">
      <div class="insight-title">&#127760; CO&#x2082; Reduction</div>
      <div class="insight-val" id="co2-val" style="color:var(--park-ev)">--</div>
      <div class="insight-desc">Estimated daily per 100 users</div>
    </div>
  </div>

</div>

<script>
  const EV_SLOTS = new Set([3, 6, 12, 17, 23, 28]);
  const ROWS = ['A','B','C','D','E'];
  const SLOTS_PER_ROW = 6;
  const TOTAL = 30;

  let occupied = new Set();
  let selectedSlot = null;
  let countdown = 30;

  // --- NEW BOOKING LOGIC ---
  async function syncBookings() {
    try {
      const response = await fetch('/bookings');
      const bookedSlots = await response.json();
      bookedSlots.forEach(slot => occupied.add(slot));
    } catch (e) {
      console.error("Failed to sync bookings", e);
    }
  }

  async function bookCurrentSlot() {
    if (!selectedSlot) return;
    const userName = prompt("Enter your name to reserve this slot:");
    if (!userName) return;

    try {
      const response = await fetch('/book', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ slot: selectedSlot, user: userName })
      });
      if (response.ok) {
        addFeedEntry(`Slot ${slotId(selectedSlot)} booked by ${userName}`, '#388bfd');
        await syncBookings();
        buildGrid();
        updateMetrics();
      }
    } catch (e) {
      alert("Booking failed");
    }
  }
  // ------------------------

  function initOccupied() {
    occupied.clear();
    const base = [2,5,7,8,10,14,15,18,20,22,24,27,29];
    const delta = Math.floor(Math.random() * 5) - 2;
    let pool = [...base];
    for (let i = 0; i < Math.abs(delta); i++) {
      if (delta > 0) {
        let r;
        do { r = Math.floor(Math.random() * TOTAL) + 1; } while (pool.includes(r));
        pool.push(r);
      } else {
        pool.splice(Math.floor(Math.random() * pool.length), 1);
      }
    }
    pool.forEach(n => { if (n >= 1 && n <= TOTAL) occupied.add(n); });
  }

  function slotId(n) {
    const row = ROWS[Math.floor((n - 1) / SLOTS_PER_ROW)];
    const num = ((n - 1) % SLOTS_PER_ROW) + 1;
    return `${row}${num}`;
  }

  function buildGrid() {
    const grid = document.getElementById('parking-grid');
    grid.innerHTML = '';
    for (let r = 0; r < 5; r++) {
      const rowEl = document.createElement('div');
      rowEl.className = 'slot-row';
      const rowId = document.createElement('div');
      rowId.className = 'row-id';
      rowId.textContent = ROWS[r];
      rowEl.appendChild(rowId);
      const leftSlots = document.createElement('div');
      leftSlots.className = 'slots-left';
      for (let s = 1; s <= 3; s++) leftSlots.appendChild(makeSlot(r * SLOTS_PER_ROW + s));
      const lane = document.createElement('div');
      lane.className = 'lane';
      lane.innerHTML = '<div class="lane-line"></div>';
      const rightSlots = document.createElement('div');
      rightSlots.className = 'slots-right';
      for (let s = 4; s <= 6; s++) rightSlots.appendChild(makeSlot(r * SLOTS_PER_ROW + s));
      rowEl.appendChild(leftSlots);
      rowEl.appendChild(lane);
      rowEl.appendChild(rightSlots);
      grid.appendChild(rowEl);
    }
  }

  function makeSlot(n) {
    const el = document.createElement('div');
    el.className = 'slot';
    el.id = `slot-${n}`;
    const isEV = EV_SLOTS.has(n);
    const isOcc = occupied.has(n);
    const isSel = selectedSlot === n;
    if (isSel) el.classList.add('selected');
    else if (isOcc) el.classList.add('occupied');
    else el.classList.add('empty');
    if (isEV) el.classList.add('ev-slot');
    const icon = isOcc ? '&#128663;' : isSel ? '&#128204;' : isEV ? '&#9889;' : '&#9632;';
    el.innerHTML = `<div class="slot-icon">${icon}</div><div class="slot-num">${slotId(n)}</div>${isEV && !isOcc ? '<div class="slot-ev-tag">EV</div>' : ''}`;
    if (!isOcc) el.onclick = () => selectSlot(n);
    return el;
  }

  function updateMetrics() {
    const occ = occupied.size;
    const empty = TOTAL - occ;
    const pct = Math.round(occ / TOTAL * 100);
    document.getElementById('m-total').textContent = TOTAL;
    document.getElementById('m-occ').textContent = occ;
    document.getElementById('m-occ-pct').textContent = `${pct}% capacity`;
    document.getElementById('m-empty').textContent = empty;
    const evFree = [...EV_SLOTS].filter(s => !occupied.has(s)).length;
    document.getElementById('m-ev').textContent = EV_SLOTS.size;
    document.getElementById('m-ev-sub').textContent = `${evFree} available now`;
    document.getElementById('occ-rate').textContent = `${pct}%`;
    document.getElementById('occ-bar').style.width = pct + '%';
    const fuelSaved = (empty > 5) ? (Math.round((8 - 1.5) * 0.08 * 10) / 10) : (Math.round(1.2 * 10) / 10);
    document.getElementById('fuel-saved').textContent = `${fuelSaved.toFixed(1)}L`;
    document.getElementById('fuel-bar').style.width = Math.min(fuelSaved * 60, 100) + '%';
    const co2 = Math.max(0, Math.round((8 - (empty > 5 ? 1.5 : 6)) * 0.23 * 100));
    document.getElementById('co2-val').textContent = `${co2}g`;
    updateDropdown();
    updateHeatmap();
  }

  function updateDropdown() {
    const sel = document.getElementById('slot-select');
    const cur = sel.value;
    sel.innerHTML = '<option value="">-- Choose available slot --</option>';
    for (let n = 1; n <= TOTAL; n++) {
      if (!occupied.has(n)) {
        const opt = document.createElement('option');
        opt.value = n;
        opt.textContent = `Slot ${slotId(n)}${EV_SLOTS.has(n) ? ' ⚡ EV' : ''}`;
        sel.appendChild(opt);
      }
    }
    if (cur && !occupied.has(parseInt(cur))) sel.value = cur;
  }

  function updateHeatmap() {
    const hm = document.getElementById('heatmap');
    hm.innerHTML = '';
    for (let r = 0; r < 5; r++) {
      let rowOcc = 0;
      for (let s = 1; s <= 6; s++) { if (occupied.has(r * 6 + s)) rowOcc++; }
      const pct = rowOcc / 6;
      const bar = document.createElement('div');
      bar.style.cssText = `flex:1;border-radius:4px 4px 0 0;transition:height 0.5s,background 0.5s;height:${Math.max(pct * 56 + 4, 4)}px;background:${pct > 0.7 ? 'var(--park-red)' : pct > 0.4 ? 'var(--park-amber)' : 'var(--park-green)'}`;
      hm.appendChild(bar);
    }
  }

  function selectSlot(n) {
    if (occupied.has(n)) return;
    selectedSlot = n;
    buildGrid();
    document.getElementById('slot-select').value = n;
    showNavigation(n);
    document.getElementById('nav-card').style.display = 'block';
    if (EV_SLOTS.has(n)) document.getElementById('ev-alert').classList.add('show');
    else document.getElementById('ev-alert').classList.remove('show');
    addFeedEntry(`Slot ${slotId(n)} selected`, '#388bfd');
  }

  function selectSlotFromDropdown(val) {
    if (!val) { resetSelection(); return; }
    selectSlot(parseInt(val));
  }

  function showNavigation(n) {
    const row = ROWS[Math.floor((n - 1) / 6)];
    const col = ((n - 1) % 6) + 1;
    const dist = (Math.floor((n - 1) / 6) * 12 + col * 4 + Math.floor(Math.random() * 10)).toString();
    const directions = ['Enter from gate', `Head to row ${row}`, col <= 3 ? 'Stay left' : 'Stay right'];
    const route = document.getElementById('nav-route');
    route.innerHTML = '';
    directions.forEach((d, i) => {
      if (i > 0) route.innerHTML += '<span class="nav-arrow">&#8594;</span>';
      route.innerHTML += `<span class="nav-step">${d}</span>`;
    });
    document.getElementById('nav-dist').textContent = dist + 'm';
    document.getElementById('nav-time').textContent = `~${Math.max(1, Math.round(parseInt(dist) / 60))} min walk`;
    document.getElementById('nav-slot').textContent = slotId(n);
  }

  function resetSelection() {
    selectedSlot = null;
    document.getElementById('slot-select').value = '';
    document.getElementById('nav-card').style.display = 'none';
    document.getElementById('ev-alert').classList.remove('show');
    buildGrid();
  }

  function addFeedEntry(msg, color = '#7d8590') {
    const feed = document.getElementById('feed-log');
    const t = new Date().toTimeString().slice(0, 8);
    const item = document.createElement('div');
    item.className = 'feed-item';
    item.innerHTML = `<span class="feed-time">${t}</span><span class="feed-dot" style="background:${color}"></span><span>${msg}</span>`;
    feed.insertBefore(item, feed.firstChild);
    if (feed.children.length > 15) feed.removeChild(feed.lastChild);
  }

  function runAIScan() {
    const overlay = document.getElementById('scan-overlay');
    const status = document.getElementById('ai-status');
    overlay.classList.add('active');
    status.textContent = 'AI Scanning...';
    addFeedEntry('YOLO v8 scan initiated', '#a371f7');
    let conf = 65;
    const tick = setInterval(() => {
      conf = Math.min(conf + Math.floor(Math.random() * 6) + 3, 97);
      document.getElementById('conf-fill').style.width = conf + '%';
      document.getElementById('conf-val').textContent = conf + '%';
    }, 200);
    setTimeout(() => {
      clearInterval(tick);
      overlay.classList.remove('active');
      status.textContent = 'AI Ready';
      refreshData(true);
      addFeedEntry(`Scan complete — ${occupied.size} vehicles detected`, '#3fb950');
    }, 2200);
  }

  // MODIFIED: refreshData is now async to allow syncing from backend
  async function refreshData(fromScan = false) {
    initOccupied();
    await syncBookings(); // Merge backend bookings into simulated occupancy
    if (selectedSlot && occupied.has(selectedSlot)) resetSelection();
    buildGrid();
    updateMetrics();
    countdown = 30;
    if (!fromScan) addFeedEntry(`Data refreshed — ${TOTAL - occupied.size} slots available`, '#2ea043');
  }

  function updateClock() {
    document.getElementById('clock').textContent = new Date().toTimeString().slice(0, 8);
  }

  // Initial Boot
  (async () => {
    initOccupied();
    await syncBookings();
    buildGrid();
    updateMetrics();
    addFeedEntry('ParkSense AI system initialized', '#a371f7');
    addFeedEntry('Connected to live sensor feed', '#3fb950');
    updateClock();
    setInterval(updateClock, 1000);
    setInterval(async () => {
      countdown--;
      document.getElementById('countdown').textContent = countdown + 's';
      if (countdown <= 0) await refreshData();
    }, 1000);
  })();

  // Optional: add a keyboard listener or hook to trigger booking
  // Since we can't change the layout, we'll add a simple listener to the Window
  // to let the user press 'B' to book the currently selected slot.
  window.addEventListener('keydown', (e) => {
    if (e.key.toLowerCase() === 'b') bookCurrentSlot();
  });
</script>
<div style="position:fixed; bottom:10px; right:10px; font-size:10px; color:var(--park-muted); opacity:0.6;">
  Tip: Select a slot and press 'B' to book it.
</div>
</body>
</html>"""


@app.route("/")
def index():
    return render_template_string(HTML)


if __name__ == "__main__":
    print("=" * 50)
    print("  ParkSense AI — Smart Parking System")
    print("=" * 50)
    print("  Server running at: http://127.0.0.1:5000")
    print("  Press Ctrl+C to stop")
    print("=" * 50)
    app.run(debug=True, port=5000)