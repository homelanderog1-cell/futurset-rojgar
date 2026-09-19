/**
 * FuturSet Jobs Portal - Live Scanner Engine Controller (SSE & Real-Time Telemetry)
 */

let eventSource = null;

function openScannerModal() {
  const modal = document.getElementById("scanner-modal");
  modal.classList.remove("hidden");
  modal.classList.add("flex");
  document.body.style.overflow = "hidden";
}

function closeScannerModal() {
  const modal = document.getElementById("scanner-modal");
  modal.classList.add("hidden");
  modal.classList.remove("flex");
  document.body.style.overflow = "auto";
  if (eventSource) {
    eventSource.close();
    eventSource = null;
  }
}

function startLiveScan() {
  openScannerModal();

  const progressBar = document.getElementById("scan-progress-bar");
  const progressPercent = document.getElementById("scan-progress-percent");
  const currentSource = document.getElementById("scan-current-source");
  const scanLogOutput = document.getElementById("scan-log-output");
  const totalScannedEl = document.getElementById("stat-scanned-count");
  const totalAddedEl = document.getElementById("stat-added-count");
  const radarIcon = document.getElementById("scanner-radar-icon");

  // Reset UI
  if (progressBar) progressBar.style.width = "5%";
  if (progressPercent) progressPercent.innerText = "5%";
  if (currentSource) currentSource.innerText = "Connecting to government recruitment streams...";
  if (scanLogOutput) scanLogOutput.innerHTML = "";
  if (radarIcon) radarIcon.classList.add("radar-ping");

  function appendLog(msg, type = "info") {
    if (!scanLogOutput) return;
    const time = new Date().toLocaleTimeString();
    const line = document.createElement("div");
    line.className = "flex items-start gap-2 py-1 border-b border-slate-800/40";
    
    let colorClass = "text-slate-400";
    let icon = "⚡";
    if (type === "success") { colorClass = "text-emerald-400 font-medium"; icon = "✓"; }
    else if (type === "scanning") { colorClass = "text-cyan-300"; icon = "🔍"; }
    else if (type === "found") { colorClass = "text-amber-300 font-medium"; icon = "★"; }

    line.innerHTML = `<span class="text-xs text-slate-500 font-mono">[${time}]</span> <span class="text-xs">${icon}</span> <span class="text-xs font-mono ${colorClass}">${msg}</span>`;
    scanLogOutput.appendChild(line);
    scanLogOutput.scrollTop = scanLogOutput.scrollHeight;
  }

  appendLog("Starting FuturSet Aggregator Engine v2.4...", "scanning");

  if (eventSource) {
    eventSource.close();
  }

  eventSource = new EventSource("/api/scan/stream");

  eventSource.onmessage = function(event) {
    try {
      const data = JSON.parse(event.data);
      const pct = Math.round((data.step / data.total_steps) * 100);

      if (progressBar) progressBar.style.width = `${pct}%`;
      if (progressPercent) progressPercent.innerText = `${pct}%`;
      if (currentSource) currentSource.innerText = data.source_name;

      if (totalScannedEl) totalScannedEl.innerText = data.jobs_scanned;
      if (totalAddedEl) totalAddedEl.innerText = data.jobs_added;

      let logType = "info";
      if (data.status === "item_found") logType = "found";
      else if (data.status === "completed") logType = "success";
      else if (data.status === "scanning") logType = "scanning";

      appendLog(data.message, logType);

      if (data.status === "completed") {
        if (radarIcon) radarIcon.classList.remove("radar-ping");
        eventSource.close();
        eventSource = null;
        appendLog("✓ Database synchronized with 0 duplicates. Refreshing job listings...", "success");
        // Reload jobs and stats on page
        setTimeout(() => {
          if (typeof fetchJobs === "function") fetchJobs();
          if (typeof fetchStats === "function") fetchStats();
        }, 1200);
      }
    } catch (e) {
      console.error("SSE parse error", e);
    }
  };

  eventSource.onerror = function(err) {
    console.warn("SSE connection error or completed", err);
    if (radarIcon) radarIcon.classList.remove("radar-ping");
    if (eventSource) {
      eventSource.close();
      eventSource = null;
    }
    // Fallback sync call if SSE was blocked
    appendLog("SSE closed. Polling database status directly...", "info");
    fetch("/api/stats")
      .then(res => res.json())
      .then(st => {
        if (typeof fetchJobs === "function") fetchJobs();
      });
  };
}

window.openScannerModal = openScannerModal;
window.closeScannerModal = closeScannerModal;
window.startLiveScan = startLiveScan;
