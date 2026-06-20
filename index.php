<?php

require_once 'api/auth.php';
?>
<!DOCTYPE html>
<!-- Static HTML dashboard page served by PHP. -->
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Carbon Footprint Dashboard</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: Arial, sans-serif; background: #f0f4f0; color: #1a1a1a; padding: 24px; }
    h1 { font-size: 28px; margin-bottom: 4px; }
    .subtitle { color: #666; margin-bottom: 24px; }
    .kpi-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }
    .card { background: white; border-radius: 14px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.07); }
    .kpi-label { font-size: 13px; color: #888; margin-bottom: 8px; }
    .kpi-value { font-size: 30px; font-weight: bold; color: #01696f; }
    .kpi-note  { font-size: 13px; color: #999; margin-top: 6px; }
    .progress-wrap { background: #e5e5e5; border-radius: 999px; height: 10px; margin-top: 10px; overflow: hidden; }
    .progress-bar  { height: 100%; background: #01696f; transition: width 1s ease; }
    .grid-2 { display: grid; grid-template-columns: 2fr 1fr; gap: 16px; margin-bottom: 24px; }
    .grid-bot { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    .card h3 { font-size: 16px; margin-bottom: 14px; }
    canvas { max-height: 280px; }
    table { width: 100%; border-collapse: collapse; }
    th, td { text-align: left; padding: 10px 12px; border-bottom: 1px solid #eee; font-size: 14px; }
    th { color: #888; font-weight: 600; font-size: 13px; }
    .badge { display:inline-block; padding:2px 8px; border-radius:999px; font-size:12px; font-weight:600; }
    .badge-transport { background:#d1fae5; color:#065f46; }
    .badge-energy    { background:#fef3c7; color:#92400e; }
    .badge-food      { background:#ffe4e6; color:#9f1239; }
    .badge-waste     { background:#e0e7ff; color:#3730a3; }
    .badge-shopping  { background:#fce7f3; color:#831843; }
    form { display: grid; gap: 10px; }
    input, select, textarea {
      padding: 10px 12px;
      border: 1px solid #ddd;
      border-radius: 10px;
      font-size: 14px;
      width: 100%;
    }
    button {
      padding: 12px;
      background: #01696f;
      color: white;
      border: none;
      border-radius: 10px;
      font-size: 15px;
      font-weight: 600;
      cursor: pointer;
    }
    button:hover { background: #0c4e54; }
    @media (max-width: 900px) { .grid-2, .grid-bot { grid-template-columns: 1fr; } }
  </style>
</head>
<body>

  <h1>🌱 Carbon Footprint Dashboard</h1>
  <p class="subtitle">Track, analyze, and reduce your CO₂ emissions</p>

  <div class="kpi-grid">
    <div class="card">
      <div class="kpi-label">📅 Current Month (kg CO₂e)</div>
      <div class="kpi-value" id="kpiCurrent">—</div>
      <div class="kpi-note" id="kpiChange"></div>
    </div>
    <div class="card">
      <div class="kpi-label">📆 Year to Date (kg CO₂e)</div>
      <div class="kpi-value" id="kpiYTD">—</div>
    </div>
    <div class="card">
      <div class="kpi-label">🎯 Monthly Target (kg CO₂e)</div>
      <div class="kpi-value" id="kpiTarget">—</div>
    </div>
    <div class="card">
      <div class="kpi-label">📊 Target Progress</div>
      <div class="kpi-value" id="kpiStatus">—</div>
      <div class="progress-wrap"><div class="progress-bar" id="progressBar" style="width:0%"></div></div>
    </div>
  </div>

  <div class="grid-2">
    <div class="card">
      <h3>📈 Monthly Trend (Last 6 Months)</h3>
      <canvas id="trendChart"></canvas>
    </div>
    <div class="card">
      <h3>🍩 Breakdown by Category</h3>
      <canvas id="categoryChart"></canvas>
    </div>
  </div>

  <div class="grid-bot">
    <div class="card">
      <h3>➕ Add New Emission</h3>
      <form id="addForm">
        <select name="category" required>
          <option value="">— Select Category —</option>
          <option value="transport">🚗 Transport</option>
          <option value="energy">⚡ Energy</option>
          <option value="food">🥩 Food</option>
          <option value="waste">🗑️ Waste</option>
          <option value="shopping">🛍️ Shopping</option>
        </select>
        <input type="text" name="subcategory" placeholder="Subcategory (e.g. Car, Flight)">
        <input type="number" step="0.01" min="0" name="amount" placeholder="Amount in kg CO₂e" required>
        <input type="date" name="date" required>
        <textarea name="notes" placeholder="Optional notes" rows="2"></textarea>
        <button type="submit">Add Entry ✅</button>
      </form>
    </div>
    <div class="card">
      <h3>🕒 Recent Entries</h3>
      <table>
        <thead><tr><th>Date</th><th>Category</th><th>kg CO₂e</th></tr></thead>
        <tbody id="recentTable"><tr><td colspan="3" style="text-align:center;color:#aaa">Loading…</td></tr></tbody>
      </table>
    </div>
  </div>

<script>
let trendChart, catChart;

async function api(action) {
  const r = await fetch(`api/emissions.php?action=${action}`);
  return r.json();
}

async function loadSummary() {
  const d = await api('summary');
  document.getElementById('kpiCurrent').textContent = d.current_month.toFixed(1) + ' kg';
  document.getElementById('kpiYTD').textContent = d.year_to_date.toFixed(1) + ' kg';
  document.getElementById('kpiTarget').textContent = d.monthly_target.toFixed(1) + ' kg';

  const diff = d.current_month - d.previous_month;
  const pct  = d.previous_month ? ((diff / d.previous_month) * 100).toFixed(1) : 0;
  document.getElementById('kpiChange').textContent =
    `${diff >= 0 ? '▲' : '▼'} ${Math.abs(diff).toFixed(1)} kg (${pct}%) vs last month`;

  const prog = Math.min((d.current_month / d.monthly_target) * 100, 100).toFixed(0);
  document.getElementById('kpiStatus').textContent =
    d.current_month <= d.monthly_target ? '✅ On Track' : '⚠️ Above Target';
  document.getElementById('progressBar').style.width = prog + '%';
  document.getElementById('progressBar').style.background =
    d.current_month <= d.monthly_target ? '#01696f' : '#da7101';
}

async function loadTrend() {
  const d = await api('trend');
  if (trendChart) trendChart.destroy();
  trendChart = new Chart(document.getElementById('trendChart'), {
    type: 'line',
    data: {
      labels: d.map(x => x.month),
      datasets: [{ label: 'kg CO₂e', data: d.map(x => parseFloat(x.total_kg)),
        borderColor:'#01696f', backgroundColor:'rgba(1,105,111,0.12)',
        fill: true, tension: 0.4, pointRadius: 5 }]
    },
    options: { responsive: true, plugins: { legend: { display: false } } }
  });
}

async function loadCategory() {
  const d = await api('by_category');
  if (catChart) catChart.destroy();
  catChart = new Chart(document.getElementById('categoryChart'), {
    type: 'doughnut',
    data: {
      labels: d.map(x => x.category),
      datasets: [{ data: d.map(x => parseFloat(x.total_kg)),
        backgroundColor: ['#01696f','#437a22','#da7101','#006494','#a12c7b'],
        hoverOffset: 8 }]
    },
    options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
  });
}

async function loadRecent() {
  const d = await api('list');
  document.getElementById('recentTable').innerHTML = d.slice(0, 10).map(r => `
    <tr>
      <td>${r.date}</td>
      <td><span class="badge badge-${r.category}">${r.category}</span></td>
      <td>${parseFloat(r.amount).toFixed(1)}</td>
    </tr>`).join('');
}

document.getElementById('addForm').addEventListener('submit', async e => {
  e.preventDefault();
  const payload = Object.fromEntries(new FormData(e.target).entries());
  await fetch('api/emissions.php', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify(payload)
  });
  e.target.reset();
  await init();
});

async function init() {
  await Promise.all([loadSummary(), loadTrend(), loadCategory(), loadRecent()]);
}
init();
</script>
</body>
</html>
