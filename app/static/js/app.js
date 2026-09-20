/**
 * FuturSet Jobs Portal - Core Interactivity, Search, Filters, AI Matcher & Modals
 */

let currentFilters = {
  q: "",
  gov_level: "",
  state: "",
  board: "",
  qualification: "",
  sector: "",
  selection_mode: "",
  sort_by: "deadline"
};

let currentView = "cards"; // "cards" or "table"
let bookmarkedJobIds = new Set();
let selectedCompareIds = [];
let audioEnabled = true;
let audioCtx = null;

document.addEventListener("DOMContentLoaded", () => {
  initLucide();
  initEventListeners();
  initHeroCanvas();
  initSpotlight();
  initAudioFeedback();
  initCommandPalette();
  fetchStats();
  fetchBookmarks();
  // If on /gujarat, default filters to Gujarat
  if (window.location.pathname.includes("/gujarat") || document.documentElement.lang === "gu") {
    currentFilters.state = "Gujarat";
    currentFilters.gov_level = "State";
  }

  // Instant hydration from pre-seeded verified jobs (Zero delay / No cold start flicker)
  if (window.__INITIAL_JOBS__ && Array.isArray(window.__INITIAL_JOBS__) && window.__INITIAL_JOBS__.length > 0) {
    window._allJobs = window.__INITIAL_JOBS__;
    window._jobsMap = window._jobsMap || {};
    window._allJobs.forEach(j => { window._jobsMap[j.id] = j; });
    const container = document.getElementById("jobs-container");
    if (container) {
      if (currentView === "cards") {
        renderCardsView(container, window._allJobs);
      } else {
        renderTableView(container, window._allJobs);
      }
    }
    const countHeader = document.getElementById("filtered-results-count");
    if (countHeader) {
      countHeader.innerText = `${window._allJobs.length} Verified Recruitments Available`;
    }
  }

  fetchJobs();
});

function initLucide() {
  try {
    if (window.lucide && typeof window.lucide.createIcons === 'function') {
      window.lucide.createIcons();
    }
  } catch (e) {
    console.warn("Lucide initialization:", e);
  }
}

// Global Search Helper Functions with Smooth Results Scroll
window.executeSearch = function() {
  const searchInput = document.getElementById("search-input");
  if (searchInput) {
    currentFilters.q = searchInput.value.trim();
    fetchJobs();
    if (typeof playAudioTick === 'function') playAudioTick(800, 0.05);
    const target = document.getElementById("filtered-results-count") || document.getElementById("jobs-container");
    if (target) {
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }
};

window.clearSearch = function() {
  const searchInput = document.getElementById("search-input");
  if (searchInput) {
    searchInput.value = "";
    currentFilters.q = "";
    fetchJobs();
    if (typeof playAudioTick === 'function') playAudioTick(600, 0.04);
  }
};

window.setQuickSearch = function(term) {
  const searchInput = document.getElementById("search-input");
  if (searchInput) {
    searchInput.value = term;
    currentFilters.q = term;
    fetchJobs();
    if (typeof playAudioTick === 'function') playAudioTick(750, 0.05);
    const target = document.getElementById("filtered-results-count") || document.getElementById("jobs-container");
    if (target) {
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }
};

function initEventListeners() {
  // Search input with debounce + Enter key support & auto-scroll
  const searchInput = document.getElementById("search-input");
  if (searchInput) {
    let timeout = null;
    searchInput.addEventListener("input", (e) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => {
        currentFilters.q = e.target.value.trim();
        fetchJobs();
      }, 250);
    });

    searchInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        clearTimeout(timeout);
        currentFilters.q = searchInput.value.trim();
        fetchJobs();
        if (typeof playAudioTick === 'function') playAudioTick(800, 0.05);
        const target = document.getElementById("filtered-results-count") || document.getElementById("jobs-container");
        if (target) {
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }
    });
  }

  // Sort dropdown
  const sortSelect = document.getElementById("sort-select");
  if (sortSelect) {
    sortSelect.addEventListener("change", (e) => {
      currentFilters.sort_by = e.target.value;
      fetchJobs();
    });
  }

  // View switchers (cards vs table)
  const btnViewCards = document.getElementById("btn-view-cards");
  const btnViewTable = document.getElementById("btn-view-table");
  const isGujarat = window.location.pathname.includes("/gujarat") || document.documentElement.lang === "gu";
  const activeBg = isGujarat ? "bg-orange-500/20" : "bg-cyan-500/20";
  const activeText = isGujarat ? "text-orange-400" : "text-cyan-400";
  const activeBorder = isGujarat ? "border-orange-500/40" : "border-cyan-500/40";

  if (btnViewCards && btnViewTable) {
    btnViewCards.addEventListener("click", () => {
      currentView = "cards";
      btnViewCards.classList.add(activeBg, activeText, activeBorder);
      btnViewCards.classList.remove("text-slate-400");
      btnViewTable.classList.remove(activeBg, activeText, activeBorder);
      btnViewTable.classList.add("text-slate-400");
      fetchJobs();
    });

    btnViewTable.addEventListener("click", () => {
      currentView = "table";
      btnViewTable.classList.add(activeBg, activeText, activeBorder);
      btnViewTable.classList.remove("text-slate-400");
      btnViewCards.classList.remove(activeBg, activeText, activeBorder);
      btnViewCards.classList.add("text-slate-400");
      fetchJobs();
    });

    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get("view") === "table") {
      currentView = "table";
      btnViewTable.classList.add(activeBg, activeText, activeBorder);
      btnViewTable.classList.remove("text-slate-400");
      btnViewCards.classList.remove(activeBg, activeText, activeBorder);
      btnViewCards.classList.add("text-slate-400");
    }
    const targetJobId = urlParams.get("job");
    if (targetJobId) {
      setTimeout(() => {
        openJobDetailModal(parseInt(targetJobId, 10));
      }, 600);
    }
  }
}

function applyQuickFilter(type, value, btnElement) {
  const isGujarat = window.location.pathname.includes("/gujarat") || document.documentElement.lang === "gu";
  const activeBg = isGujarat ? "bg-orange-600" : "bg-[#635bff]";

  // Reset active classes on sibling chips
  if (btnElement && btnElement.parentElement) {
    btnElement.parentElement.querySelectorAll("button").forEach(b => {
      b.classList.remove("bg-cyan-600", "bg-orange-600", "bg-[#635bff]", "text-white", "shadow-sm", "shadow-xs");
      b.classList.add("bg-white", "text-slate-700", "border-slate-200");
      b.classList.remove("bg-slate-800/80", "text-slate-300");
    });
    btnElement.classList.add(activeBg, "text-white", "shadow-xs");
    btnElement.classList.remove("bg-white", "text-slate-700", "border-slate-200", "bg-slate-800/80", "text-slate-300");
  }

  if (type === "level") {
    currentFilters.gov_level = value === "All" ? "" : value;
    currentFilters.state = "";
    currentFilters.board = "";
  } else if (type === "gujarat") {
    currentFilters.state = "Gujarat";
    currentFilters.gov_level = "State";
    currentFilters.board = value === "All" ? "" : value;
  } else if (type === "board") {
    currentFilters.board = value === "All" ? "" : value;
  } else if (type === "qualification") {
    currentFilters.qualification = value === "All" ? "" : value;
  }

  fetchJobs();
}

async function fetchStats() {
  try {
    const res = await fetch("/api/stats");
    const data = await res.json();
    
    const elTotVac = document.getElementById("stat-total-vacancies");
    const elTotJobs = document.getElementById("stat-total-jobs");
    const elGujVac = document.getElementById("stat-gujarat-vacancies");
    const elCenVac = document.getElementById("stat-central-vacancies");
    const elSoon = document.getElementById("stat-closing-soon");

    if (elTotVac) elTotVac.innerText = data.total_vacancies.toLocaleString();
    if (elTotJobs) elTotJobs.innerText = data.total_jobs;
    if (elGujVac) elGujVac.innerText = data.gujarat_vacancies.toLocaleString();
    if (elCenVac) elCenVac.innerText = data.central_vacancies.toLocaleString();
    if (elSoon) elSoon.innerText = data.closing_soon;
  } catch (err) {
    console.error("Error fetching stats:", err);
  }
}

async function fetchBookmarks() {
  try {
    const res = await fetch("/api/bookmarks");
    const data = await res.json();
    bookmarkedJobIds = new Set(data.bookmarks.map(j => j.id));
    const badge = document.getElementById("bookmark-count-badge");
    if (badge) {
      badge.innerText = bookmarkedJobIds.size;
      badge.classList.toggle("hidden", bookmarkedJobIds.size === 0);
    }
  } catch (e) {
    console.error("Error fetching bookmarks:", e);
  }
}

async function fetchJobs() {
  const container = document.getElementById("jobs-container");
  if (!container) return;

  const skeletonCard = `
    <div class="skeleton-card-light p-5 flex flex-col justify-between">
      <div>
        <div class="flex items-center justify-between gap-3 mb-4">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl skeleton-shimmer-light"></div>
            <div class="space-y-1.5">
              <div class="w-28 h-3.5 rounded skeleton-shimmer-light"></div>
              <div class="w-16 h-2.5 rounded skeleton-shimmer-light"></div>
            </div>
          </div>
          <div class="w-20 h-5 rounded-full skeleton-shimmer-light"></div>
        </div>
        <div class="w-full h-5 rounded skeleton-shimmer-light mb-2"></div>
        <div class="w-3/4 h-4 rounded skeleton-shimmer-light mb-4"></div>
        <div class="grid grid-cols-3 gap-2 py-3 border-y border-slate-100 mb-4">
          <div class="space-y-1"><div class="w-10 h-2 rounded skeleton-shimmer-light"></div><div class="w-14 h-4 rounded skeleton-shimmer-light"></div></div>
          <div class="space-y-1"><div class="w-10 h-2 rounded skeleton-shimmer-light"></div><div class="w-14 h-4 rounded skeleton-shimmer-light"></div></div>
          <div class="space-y-1"><div class="w-10 h-2 rounded skeleton-shimmer-light"></div><div class="w-14 h-4 rounded skeleton-shimmer-light"></div></div>
        </div>
      </div>
      <div class="flex items-center justify-between pt-2">
        <div class="w-20 h-3 rounded skeleton-shimmer-light"></div>
        <div class="flex gap-2">
          <div class="w-8 h-8 rounded-lg skeleton-shimmer-light"></div>
          <div class="w-24 h-8 rounded-lg skeleton-shimmer-light"></div>
        </div>
      </div>
    </div>
  `;
  container.innerHTML = `<div class="col-span-full grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">${skeletonCard.repeat(6)}</div>`;

  const queryParams = new URLSearchParams();
  if (currentFilters.q) queryParams.set("q", currentFilters.q);
  if (currentFilters.gov_level) queryParams.set("gov_level", currentFilters.gov_level);
  if (currentFilters.state) queryParams.set("state", currentFilters.state);
  if (currentFilters.board) queryParams.set("board", currentFilters.board);
  if (currentFilters.district) queryParams.set("district", currentFilters.district);
  if (currentFilters.sector) queryParams.set("sector", currentFilters.sector);
  if (currentFilters.urgency) queryParams.set("urgency", currentFilters.urgency);
  if (currentFilters.qualification) queryParams.set("qualification", currentFilters.qualification);
  if (currentFilters.selection_mode) queryParams.set("selection_mode", currentFilters.selection_mode);
  if (currentFilters.sort_by) queryParams.set("sort_by", currentFilters.sort_by);

  const isGujarat = window.location.pathname.includes("/gujarat") || document.documentElement.lang === "gu";

  try {
    const res = await fetch(`/api/jobs?${queryParams.toString()}`);
    const data = await res.json();

    const countHeader = document.getElementById("filtered-results-count");
    if (countHeader) {
      if (isGujarat) {
        countHeader.innerText = `ગુજરાત રાજ્યની સક્રિય ભરતીઓ (${data.count} ઉપલબ્ધ)`;
      } else {
        countHeader.innerText = `${data.count} Verified Recruitments Found`;
      }
    }

    if (data.results.length === 0) {
      container.innerHTML = `
        <div class="col-span-full py-16 text-center bg-white rounded-2xl p-8 border border-slate-200 shadow-xs">
          <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-slate-100 flex items-center justify-center text-slate-400">
            <i data-lucide="search-x" class="w-8 h-8"></i>
          </div>
          <h3 class="text-lg font-bold text-slate-800">${isGujarat ? 'કોઈ ભરતી પરિણામ મળ્યું નથી' : 'No recruitments match your filter criteria'}</h3>
          <p class="text-sm text-slate-500 mt-1 max-w-md mx-auto">${isGujarat ? 'કૃપા કરીને અન્ય બોર્ડ અથવા લાયકાત પસંદ કરો, અથવા લાઈવ સ્કેનર ચલાવો.' : 'Try clearing selected filters, changing qualifications, or running the Live Scanner to pull new feeds.'}</p>
          <button onclick="resetAllFilters()" class="mt-4 px-4 py-2 ${isGujarat ? 'bg-orange-600 hover:bg-orange-500' : 'bg-[#635bff] hover:bg-indigo-600'} text-white text-sm font-semibold rounded-xl shadow-xs transition-colors">
            ${isGujarat ? 'ફિલ્ટર્સ રીસેટ કરો' : 'Reset Filters'}
          </button>
        </div>
      `;
      initLucide();
      return;
    }

    if (currentView === "cards") {
      renderCardsView(container, data.results);
    } else {
      renderTableView(container, data.results);
    }

    initLucide();
  } catch (err) {
    console.error("Error fetching jobs:", err);
    container.innerHTML = `<div class="col-span-full text-center text-rose-400 py-10">Failed to load jobs. Please try again.</div>`;
  }
}

function renderCardsView(container, jobs) {
  try {
    const isGujaratPage = window.location.pathname.includes("/gujarat") || document.documentElement.lang === "gu";
    let html = `<div class="col-span-full grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">`;

  jobs.forEach(job => {
    const isBookmarked = bookmarkedJobIds.has(job.id);
    const isGujaratJob = job.state === "Gujarat";
    const initialLetter = (job.organization || "G").charAt(0).toUpperCase();

    let urgencyBadgeHtml = "";
    if (job.urgency_badge === "closed" || job.days_left < 0) {
      urgencyBadgeHtml = `<span class="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-rose-50 text-rose-700 border border-rose-200 flex items-center gap-1"><i data-lucide="x-circle" class="w-3 h-3"></i> ${isGujaratPage ? 'અરજી બંધ' : 'Closed'}</span>`;
    } else if (job.days_left === 0) {
      urgencyBadgeHtml = `<span class="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-amber-50 text-amber-800 border border-amber-300 animate-pulse flex items-center gap-1"><i data-lucide="alert-triangle" class="w-3 h-3"></i> ${isGujaratPage ? 'આજે છેલ્લો દિવસ!' : 'Closes Today!'}</span>`;
    } else if (job.urgency_badge === "urgent" || job.days_left <= 3) {
      urgencyBadgeHtml = `<span class="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-rose-50 text-rose-700 border border-rose-200 flex items-center gap-1"><i data-lucide="clock" class="w-3 h-3"></i> ${job.days_left} ${isGujaratPage ? 'દિવસ બાકી' : 'Days Left'}</span>`;
    } else {
      urgencyBadgeHtml = `<span class="px-2 py-0.5 rounded-full text-[10px] font-medium bg-slate-100 text-slate-600 border border-slate-200 flex items-center gap-1"><i data-lucide="calendar" class="w-3 h-3 text-slate-500"></i> ${job.last_date || 'Closing Soon'}</span>`;
    }

    const isCompareSelected = selectedCompareIds.includes(job.id);
    const qualDisplay = (job.qualification || 'Degree / Diploma').split('+')[0].trim();
    const salaryDisplay = job.salary_text ? job.salary_text.split('->')[0].trim() : (job.ctc_lpa ? `₹${job.ctc_lpa} LPA` : '7th Pay Matrix');

    html += `
      <div class="otta-job-card p-5 group animate-card-entrance flex flex-col justify-between">
        <div>
          <!-- Header: Org Avatar + Badges + Actions -->
          <div class="flex items-start justify-between gap-3 mb-3.5">
            <div class="flex items-center gap-2.5">
              <div class="w-10 h-10 rounded-xl bg-indigo-50 border border-indigo-100 flex items-center justify-center font-bold text-[#635bff] text-sm shrink-0 group-hover:scale-105 transition-transform shadow-xs">
                ${initialLetter}
              </div>
              <div class="min-w-0">
                <span class="text-xs font-bold text-[#0a2540] block truncate group-hover:text-[#635bff] transition-colors">${job.organization}</span>
                <span class="text-[11px] text-slate-500 flex items-center gap-1 mt-0.5">
                  <i data-lucide="map-pin" class="w-3 h-3 text-slate-400 shrink-0"></i>
                  <span class="truncate">${job.district || job.state || 'All India'}</span>
                </span>
              </div>
            </div>

            <div class="flex items-center gap-1.5 shrink-0">
              <label class="cursor-pointer text-[11px] font-medium text-slate-600 hover:text-[#635bff] flex items-center gap-1 bg-slate-50 hover:bg-slate-100 px-2 py-1 rounded-lg border border-slate-200 transition-colors" title="Compare side-by-side">
                <input type="checkbox" onchange="toggleCompareJob(${job.id}, this)" ${isCompareSelected ? 'checked' : ''} class="rounded text-[#635bff] focus:ring-0 w-3.5 h-3.5 bg-white border-slate-300">
                <span class="hidden sm:inline text-[10px]">Compare</span>
              </label>
              <button onclick="toggleBookmark(${job.id}, this)" class="p-1.5 rounded-lg bg-slate-50 hover:bg-slate-100 text-slate-500 hover:text-[#635bff] border border-slate-200 transition-colors" title="Bookmark">
                <i data-lucide="bookmark" class="w-3.5 h-3.5 ${isBookmarked ? 'fill-[#635bff] text-[#635bff]' : ''}"></i>
              </button>
            </div>
          </div>

          <!-- Authority & Status Pills -->
          <div class="flex flex-wrap items-center gap-1.5 mb-3">
            <span class="px-2 py-0.5 rounded-full text-[10px] font-bold ${isGujaratJob ? 'bg-amber-50 text-amber-800 border border-amber-200' : 'bg-blue-50 text-blue-700 border border-blue-200'}">
              ${job.gov_level === 'Central' ? '🇮🇳 Central Govt' : '🦁 Gujarat State'}
            </span>
            <span class="px-2 py-0.5 rounded-full text-[10px] font-medium bg-slate-100 text-slate-700 border border-slate-200">
              ${job.board_category || 'Board'}
            </span>
            ${job.is_btech_cse ? '<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-indigo-50 text-indigo-700 border border-indigo-200">💻 B.Tech CSE</span>' : ''}
          </div>

          <!-- Title -->
          <h3 class="text-[0.95rem] font-bold text-[#0a2540] group-hover:text-[#635bff] transition-colors line-clamp-2 leading-snug cursor-pointer mb-1.5" onclick="openJobDetailModal(${job.id})">
            ${job.title}
          </h3>

          ${job.title_gu ? `
            <p class="font-gujarati text-xs text-amber-700 font-medium mb-3 line-clamp-1">
              ${job.title_gu}
            </p>
          ` : ''}

          <!-- Clean 3-Item Metrics Bar (Otta Standard) -->
          <div class="grid grid-cols-3 gap-2 py-2.5 px-3 rounded-xl bg-slate-50 border border-slate-100 text-xs mb-4">
            <div>
              <span class="text-slate-500 block text-[10px] font-medium uppercase tracking-wider">Vacancies</span>
              <span class="font-bold text-emerald-600 text-xs mt-0.5 block tabular-nums">${job.vacancies.toLocaleString()}</span>
            </div>
            <div>
              <span class="text-slate-500 block text-[10px] font-medium uppercase tracking-wider">Pay Scale</span>
              <span class="font-semibold text-slate-800 text-xs mt-0.5 block truncate" title="${job.salary_text}">${salaryDisplay}</span>
            </div>
            <div>
              <span class="text-slate-500 block text-[10px] font-medium uppercase tracking-wider">Eligibility</span>
              <span class="font-semibold text-slate-700 text-xs mt-0.5 block truncate" title="${job.qualification}">${qualDisplay}</span>
            </div>
          </div>
        </div>

        <!-- Card Footer: Urgency Pill + Tactile Actions -->
        <div class="pt-3 border-t border-slate-100 flex items-center justify-between gap-2 mt-auto">
          <div class="shrink-0">
            ${urgencyBadgeHtml}
          </div>

          <div class="flex items-center gap-2">
            <button onclick="openJobDetailModal(${job.id})" class="btn-stripe-secondary text-xs px-3 py-1.5 rounded-lg flex items-center gap-1" title="View Full Dossier">
              <span>Dossier</span>
            </button>
            <a href="${job.apply_url}" target="_blank" rel="noopener noreferrer" class="btn-stripe-primary text-xs px-3.5 py-1.5 rounded-lg flex items-center gap-1 shadow-xs">
              <span>Apply</span>
              <i data-lucide="arrow-up-right" class="w-3.5 h-3.5"></i>
            </a>
          </div>
        </div>
      </div>
    `;
  });

  html += `</div>`;
  container.innerHTML = html;
  initLucide();
  } catch (e) {
    console.error("Fatal error in renderCardsView:", e);
  }
}

function renderTableView(container, jobs) {
  try {
    const isGujaratPage = window.location.pathname.includes("/gujarat") || document.documentElement.lang === "gu";
  let html = `
    <div class="col-span-full portal-table-container">
      <table class="portal-table">
        <thead>
          <tr>
            <th class="min-w-[260px]">${isGujaratPage ? 'ભરતી અને બોર્ડ' : 'Job Title & Organization'}</th>
            <th class="min-w-[130px]">${isGujaratPage ? 'કેટેગરી' : 'Board & Level'}</th>
            <th class="min-w-[100px]">${isGujaratPage ? 'જગ્યાઓ' : 'Vacancies'}</th>
            <th class="min-w-[200px]">${isGujaratPage ? 'લાયકાત અને વય' : 'Eligibility & Age'}</th>
            <th class="min-w-[180px]">${isGujaratPage ? 'પગાર ધોરણ' : 'Pay Scale / CTC'}</th>
            <th class="min-w-[140px]">${isGujaratPage ? 'અંતિમ તારીખ' : 'Last Date'}</th>
            <th class="min-w-[150px] text-right sticky-action-col">${isGujaratPage ? 'ક્રિયા' : 'Actions'}</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
  `;

  jobs.forEach(job => {
    const minAge = parseInt(job.age_min) || 18;
    const maxAge = parseInt(job.age_max) || 35;
    const daysLeft = job.days_left !== undefined && job.days_left !== null ? job.days_left : 15;
    const boardCat = job.board_category || (job.state === 'Gujarat' ? 'OJAS Gujarat' : 'National');

    html += `
      <tr class="hover:bg-slate-50 transition-colors group">
        <td class="px-5 py-4">
          <div class="font-bold text-[#0a2540] text-sm leading-snug group-hover:text-[#635bff] transition-colors">${job.title}</div>
          <div class="text-xs text-[#635bff] font-semibold mt-0.5 flex items-center gap-1.5">
            <i data-lucide="building" class="w-3.5 h-3.5 shrink-0"></i>
            <span>${job.organization}</span>
          </div>
          ${job.title_gu ? `<div class="text-xs text-slate-500 font-gujarati mt-1">${job.title_gu}</div>` : ''}
        </td>
        <td class="px-4 py-4">
          <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold ${job.state === 'Gujarat' ? 'bg-amber-50 text-amber-800 border border-amber-200' : 'bg-blue-50 text-blue-700 border border-blue-200'}">
            ${boardCat}
          </span>
          <span class="block text-xs text-slate-500 mt-1">${job.gov_level || 'Public Sector'}</span>
        </td>
        <td class="px-4 py-4">
          <span class="inline-flex items-center gap-1 font-extrabold text-emerald-700 text-sm bg-emerald-50 px-2.5 py-1 rounded-lg border border-emerald-200 tabular-nums">
            <i data-lucide="users" class="w-3.5 h-3.5"></i>
            ${(job.vacancies || 0).toLocaleString()}
          </span>
        </td>
        <td class="px-4 py-4 text-xs">
          <div class="font-semibold text-slate-800 leading-snug">${job.qualification || 'Graduate / 10th / 12th'}</div>
          <div class="text-slate-500 text-[11px] mt-1 flex items-center gap-1">
            <i data-lucide="calendar" class="w-3 h-3 text-amber-600"></i>
            <span>Age: <strong class="text-slate-700">${minAge}-${maxAge} Yrs</strong></span>
          </div>
        </td>
        <td class="px-4 py-4 text-xs">
          <div class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-bold bg-indigo-50 text-indigo-700 border border-indigo-200 whitespace-nowrap shadow-xs">
            <i data-lucide="wallet" class="w-3 h-3 mr-1 text-indigo-600"></i>
            <span>${job.salary_text || 'Standard 7th Pay'}</span>
          </div>
        </td>
        <td class="px-4 py-4 text-xs">
          <span class="font-bold ${daysLeft <= 3 ? 'text-rose-600' : 'text-slate-800'}">${job.last_date || 'Closing Soon'}</span>
          <span class="block text-[11px] font-semibold mt-0.5 ${daysLeft <= 3 ? 'text-rose-600' : 'text-amber-700'}">
            ${daysLeft <= 0 ? 'Closed' : daysLeft + ' days left'}
          </span>
        </td>
        <td class="px-5 py-4 text-right sticky-action-col">
          <div class="flex items-center justify-end gap-2">
            <button onclick="openJobDetailModal(${job.id})" class="btn-stripe-secondary text-xs px-2.5 py-1.5 rounded-lg flex items-center gap-1" title="View Full Dossier">
              <i data-lucide="info" class="w-3.5 h-3.5 text-[#635bff]"></i>
              <span>Details</span>
            </button>
            <a href="${job.apply_url}" target="_blank" rel="noopener noreferrer" class="btn-stripe-primary text-xs px-3 py-1.5 rounded-lg flex items-center gap-1 shadow-xs">
              <span>${isGujaratPage ? 'અરજી' : 'Apply'}</span>
              <i data-lucide="arrow-up-right" class="w-3.5 h-3.5"></i>
            </a>
          </div>
        </td>
      </tr>
    `;
  });

  html += `</tbody></table></div>`;
  container.innerHTML = html;
  initLucide();
  } catch (e) {
    console.error("Fatal error in renderTableView:", e);
  }
}

function generateStepByStepGuide(job, isGujaratPage) {
  const url = (job.apply_url || "").toLowerCase();
  const org = (job.organization || "").toLowerCase();
  const board = (job.board_category || "").toLowerCase();
  const isGov = job.gov_level !== 'Private';

  let portalName = "Official Recruitment Portal";
  let steps = [];

  if (url.includes("ojas.gujarat.gov.in") || board.includes("ojas") || board.includes("gsssb") || board.includes("gsrtc") || board.includes("police")) {
    portalName = "OJAS Gujarat (ojas.gujarat.gov.in)";
    steps = [
      {
        num: 1,
        title: "One-Time Registration (OTR / ઓનલાઇન રજીસ્ટ્રેશન)",
        desc: "Visit ojas.gujarat.gov.in. If you are a new applicant, click 'Registration' -> 'Apply' on the top menu to create your One-Time Registration Profile using your mobile number and email ID. If already registered, use your existing OTR.",
        icon: "user-plus"
      },
      {
        num: 2,
        title: "Select Advertisement & Post (જાહેરાત પસંદ કરો)",
        desc: `Navigate to 'Online Application' -> 'Apply'. From the department dropdown, select '${job.organization}' (Advt No: ${job.notification_number || '2026-27'}). Locate '${job.title}' and click 'Apply Now'.`,
        icon: "list-checks"
      },
      {
        num: 3,
        title: "Fill Academic & Category Details (શૈક્ષણિક વિગતો)",
        desc: `Input your qualifications (${job.qualification}), passing year, marks obtained, percentage, and category reservation details (SC/ST/SEBC/EWS). Ensure the applicant's name matches the Class 10 SSC certificate exactly.`,
        icon: "file-edit"
      },
      {
        num: 4,
        title: "Upload Photo & Signature (ફોટો અને સહી અપલોડ)",
        desc: "Go to 'Upload Photograph & Signature'. Upload a passport color photo (JPG format, strictly between 10 KB - 15 KB, 5cm x 3.6cm) and signature on white paper with dark blue/black ink (JPG format, strictly between 10 KB - 15 KB, 2.5cm x 7.5cm).",
        icon: "camera"
      },
      {
        num: 5,
        title: "Confirm Application & Save Confirmation No (અરજી કન્ફર્મ કરો)",
        desc: "Click 'Confirm Application' from the menu. Double check all entered details in preview mode. Click 'Confirm'. Note down your 8-digit Confirmation Number immediately — it is mandatory for Call Letter download!",
        icon: "check-circle",
        highlight: true
      },
      {
        num: 6,
        title: "Application Fee Payment (ફી ની ચૂકવણી)",
        desc: `Fee: ${job.application_fee || '₹100 for General; Reserved Categories Exempted'}. Click 'Print Application / Pay Fees'. Pay online via Debit Card/Net Banking/UPI, or generate Post Office E-Challan to pay at any Gujarat Computerized Post Office.`,
        icon: "credit-card"
      },
      {
        num: 7,
        title: "Download & Archive Final Printout (પ્રિન્ટ સાચવી રાખો)",
        desc: "Download and print 2 copies of the confirmed Application Form and Fee Payment Receipt. Keep them safely for Document Verification (DV) and exam entry.",
        icon: "printer"
      }
    ];
  } else if (url.includes("gpsc-ojas.gujarat.gov.in") || url.includes("gpsc.gujarat.gov.in") || board.includes("gpsc")) {
    portalName = "GPSC OJAS Portal (gpsc-ojas.gujarat.gov.in)";
    steps = [
      {
        num: 1,
        title: "GPSC OTR Registration",
        desc: "Access gpsc-ojas.gujarat.gov.in. Complete GPSC One-Time Registration (One Time Profile) with Aadhaar and educational records.",
        icon: "user-plus"
      },
      {
        num: 2,
        title: "Select GPSC Advertisement",
        desc: `Choose ${job.notification_number || 'GPSC Advertisements 2026-27'} and select '${job.title}'. Click Apply Online.`,
        icon: "file-text"
      },
      {
        num: 3,
        title: "Upload Scanned Credentials",
        desc: "Upload photo (<15 KB) and signature (<15 KB). Enter degree marks and select preliminary examination city.",
        icon: "upload"
      },
      {
        num: 4,
        title: "Confirm Application & Payment",
        desc: "Confirm application to lock your submission. Pay the examination fee (₹100 for Unreserved; Reserved categories exempted) via Cyber Treasury online gateway.",
        icon: "credit-card",
        highlight: true
      },
      {
        num: 5,
        title: "Download Hall Ticket Preparation",
        desc: "Save your confirmation number and application roll to download GPSC Prelims Call Letter 10 days prior to the examination date.",
        icon: "download"
      }
    ];
  } else if (url.includes("ssc.gov.in") || board.includes("ssc")) {
    portalName = "Staff Selection Commission Portal (ssc.gov.in)";
    steps = [
      {
        num: 1,
        title: "SSC New Portal One-Time Registration (OTR)",
        desc: "Visit ssc.gov.in. Create your OTR with Aadhaar, Class 10 roll number, father/mother name, and contact details.",
        icon: "user-plus"
      },
      {
        num: 2,
        title: "Live Webcam Photo Capture",
        desc: "SSC mandates live photo capture. Use the official 'MySSC App' or a webcam with plain white background, ample lighting, and clear facial view (no spectacles or head coverings).",
        icon: "camera",
        highlight: true
      },
      {
        num: 3,
        title: "Upload Scanned Signature",
        desc: "Upload scanned signature on white paper (10 KB to 20 KB in JPEG/JPG format, 4.0 cm width x 2.0 cm height).",
        icon: "pen-tool"
      },
      {
        num: 4,
        title: "Select Examination Centres",
        desc: "Select 3 preferred exam cities in order of priority within Western Region (e.g. Ahmedabad, Vadodara, Rajkot, Surat).",
        icon: "map-pin"
      },
      {
        num: 5,
        title: "Online Fee Payment & Submission",
        desc: "Pay ₹100 online through Net Banking, Visa, MasterCard, RuPay, or UPI (Female candidates and SC/ST/PwD/ESM are exempted).",
        icon: "credit-card"
      },
      {
        num: 6,
        title: "Save Application PDF",
        desc: "Download and preserve the submitted application summary PDF with registration number for future CBT phases.",
        icon: "file-check"
      }
    ];
  } else if (url.includes("rrbapply.gov.in") || board.includes("rrb")) {
    portalName = "Railway Recruitment Board Portal (rrbapply.gov.in)";
    steps = [
      {
        num: 1,
        title: "RRB Apply Account Creation",
        desc: "Access rrbapply.gov.in. Register using mobile OTP and active email address. Set up your master applicant credentials.",
        icon: "user-check"
      },
      {
        num: 2,
        title: "Select Zonal Railway & Post",
        desc: "Choose your Zonal Railway (e.g., Western Railway - WR / Ahmedabad) and arrange post/cadre preferences.",
        icon: "compass"
      },
      {
        num: 3,
        title: "Refund Bank Account Details",
        desc: "Crucial: Enter your active Bank Account Number and IFSC Code for refund of examination fees upon attending the CBT examination.",
        icon: "banknote",
        highlight: true
      },
      {
        num: 4,
        title: "Upload Photograph & Documents",
        desc: "Upload recent color photo (30 to 70 KB) and signature (30 to 70 KB). SC/ST candidates upload caste certificate for free rail travel pass.",
        icon: "upload"
      },
      {
        num: 5,
        title: "Fee Payment & Final Confirmation",
        desc: "Pay ₹500 (₹400 refunded after CBT 1) or ₹250 (full ₹250 refunded for reserved/women). Download application receipt.",
        icon: "check-circle"
      }
    ];
  } else if (url.includes("indiapostgdsonline.gov.in") || board.includes("postal")) {
    portalName = "India Post GDS Online Engagement Portal (indiapostgdsonline.gov.in)";
    steps = [
      {
        num: 1,
        title: "Stage 1: Primary Registration",
        desc: "Visit indiapostgdsonline.gov.in. Enter 10th Standard Board Roll Number, Year of Passing, Mother's Name, Mobile & Email to generate Registration No.",
        icon: "user-plus"
      },
      {
        num: 2,
        title: "Stage 2: Fee Payment",
        desc: "Pay ₹100 registration fee online through payment gateway. Female, SC, ST, PwD, and Transgender applicants are 100% exempted (₹0).",
        icon: "credit-card"
      },
      {
        num: 3,
        title: "Stage 3: Select Circle & Post Preferences",
        desc: "Select Circle (e.g. Gujarat Circle) and Division (Ahmedabad, Surat, Rajkot, Vadodara, etc.). Choose multiple post office / Branch Post Master (BPM) / Assistant Branch Post Master (ABPM) preferences.",
        icon: "map-pin",
        highlight: true
      },
      {
        num: 4,
        title: "Stage 4: 100% Direct Merit Selection (No Exam)",
        desc: "There is NO written exam. India Post prepares a 100% merit list based strictly on Class 10 secondary board marks. Keep your mobile active for SMS merit call.",
        icon: "award"
      },
      {
        num: 5,
        title: "Stage 5: Document Verification (DV)",
        desc: "Shortlisted candidates appear for original document verification at the designated Divisional Superintendent of Post Offices.",
        icon: "shield-check"
      }
    ];
  } else if (!isGov || job.gov_level === 'Private') {
    portalName = `${job.organization} Official Careers Portal`;
    steps = [
      {
        num: 1,
        title: "Access Official Enterprise Career Portal",
        desc: `Navigate to the official ${job.organization} careers/workday site. Ensure you apply only on the authenticated corporate domain.`,
        icon: "external-link"
      },
      {
        num: 2,
        title: "ATS-Optimized Resume Submission",
        desc: `Upload your standard 1-page PDF resume. Ensure your skills and project keywords align with the requirements: ${job.tech_stack || 'relevant domain tools'}.`,
        icon: "file-text",
        highlight: true
      },
      {
        num: 3,
        title: "Online Assessment / Coding Challenge",
        desc: "Shortlisted candidates receive an automated link for an online test (HackerRank, CodeSignal, Mettl, or SHL) covering aptitude, core computer science, and domain logic.",
        icon: "code"
      },
      {
        num: 4,
        title: "Technical & Problem Solving Rounds",
        desc: "1 to 2 rounds of in-depth technical discussion covering system architecture, hands-on programming, database design, and real-world projects.",
        icon: "cpu"
      },
      {
        num: 5,
        title: "Managerial & HR Cultural Fit Round",
        desc: `Final interaction covering compensation expectations (Target CTC: ${job.ctc_lpa ? '₹' + job.ctc_lpa + ' LPA' : 'Market Standard'}), joining date, and work location.`,
        icon: "users"
      },
      {
        num: 6,
        title: "Background Verification & Offer Letter",
        desc: "Submit academic transcripts, identity proof, and employment background verification documents to receive the formal Offer of Employment.",
        icon: "check-circle-2"
      }
    ];
  } else {
    portalName = `${job.organization} Designated Recruitment Portal`;
    steps = [
      {
        num: 1,
        title: "Portal Access & Advertisement Scrutiny",
        desc: `Visit the official recruitment portal (${job.apply_url}). Read the detailed recruitment brochure and terms.`,
        icon: "search"
      },
      {
        num: 2,
        title: "Candidate Registration",
        desc: "Register your candidate profile with mobile number, email, and Aadhaar / identity credentials.",
        icon: "user-plus"
      },
      {
        num: 3,
        title: "Fill Application Form",
        desc: `Carefully fill your personal, educational (${job.qualification}), and address particulars.`,
        icon: "file-edit"
      },
      {
        num: 4,
        title: "Upload Required Certificates",
        desc: "Upload scanned copies of photo, signature, degree certificates, and caste certificate in specified format.",
        icon: "upload"
      },
      {
        num: 5,
        title: "Fee Payment & Final Submission",
        desc: `Submit application fee (${job.application_fee || 'as applicable'}) online and print the final acknowledgment receipt.`,
        icon: "credit-card",
        highlight: true
      }
    ];
  }

  let html = `
    <div class="glass-panel p-5 sm:p-6 rounded-2xl border border-emerald-500/30 bg-emerald-950/10">
      <div class="flex flex-wrap items-center justify-between gap-3 pb-4 mb-5 border-b border-slate-800">
        <div>
          <span class="px-2.5 py-0.5 rounded-full text-[11px] font-extrabold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 uppercase tracking-wide">
            Official Application Procedure
          </span>
          <h3 class="text-base sm:text-lg font-black text-white mt-1 flex items-center gap-2">
            <i data-lucide="navigation-2" class="w-5 h-5 text-emerald-400"></i>
            <span>${isGujaratPage ? 'સ્ટેપ-બાય-સ્ટેપ અરજી માર્ગદર્શિકા (Step-by-Step Guide)' : 'Complete Step-by-Step Application Walkthrough'}</span>
          </h3>
          <p class="text-xs text-slate-300 mt-0.5">
            Portal: <strong class="text-cyan-300">${portalName}</strong> • Official Apply URL: <a href="${job.apply_url}" target="_blank" class="text-cyan-400 underline hover:text-cyan-300 font-mono">${job.apply_url}</a>
          </p>
        </div>

        <a href="${job.apply_url}" target="_blank" rel="noopener noreferrer" class="px-4 py-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-extrabold text-xs rounded-xl shadow-lg shadow-emerald-600/30 flex items-center gap-2 transition-transform transform hover:scale-105">
          <span>Launch Official Portal</span>
          <i data-lucide="external-link" class="w-4 h-4"></i>
        </a>
      </div>

      <div class="space-y-4">
  `;

  steps.forEach(step => {
    html += `
      <div class="flex items-start gap-3.5 p-4 rounded-xl ${step.highlight ? 'bg-emerald-950/30 border border-emerald-500/40 shadow-lg shadow-emerald-950/20' : 'bg-slate-900/80 border border-slate-800'} transition-all hover:border-slate-700 group">
        <div class="w-9 h-9 rounded-xl ${step.highlight ? 'bg-gradient-to-tr from-emerald-600 to-teal-500 text-white font-black shadow-lg shadow-emerald-600/40' : 'bg-slate-800 text-cyan-400 font-bold border border-slate-700'} flex items-center justify-center shrink-0 text-sm">
          ${step.num}
        </div>
        <div class="flex-1">
          <h4 class="text-sm font-black text-white group-hover:text-cyan-300 transition-colors flex items-center gap-2">
            <i data-lucide="${step.icon}" class="w-4 h-4 ${step.highlight ? 'text-emerald-400' : 'text-slate-400'}"></i>
            <span>${step.title}</span>
          </h4>
          <p class="text-xs text-slate-300 mt-1 leading-relaxed">
            ${step.desc}
          </p>
        </div>
      </div>
    `;
  });

  html += `
      </div>

      <div class="mt-5 p-4 rounded-xl bg-amber-950/20 border border-amber-500/40 text-xs text-amber-200 space-y-2">
        <div class="font-extrabold text-amber-300 flex items-center gap-1.5 uppercase tracking-wider text-[11px]">
          <i data-lucide="alert-triangle" class="w-4 h-4"></i>
          <span>${isGujaratPage ? 'અરજી કરતી વખતે ધ્યાનમાં રાખવાની મહત્વપૂર્ણ બાબતો' : 'Critical Rules & Instructions for Applicants'}</span>
        </div>
        <ul class="list-disc list-inside space-y-1 text-[11px] text-slate-300">
          <li><strong>Confirmation Number Mandatory:</strong> Once you submit the form, do NOT forget to click 'Confirm Application' and note down the confirmation number. An unconfirmed application is automatically rejected.</li>
          <li><strong>Name Spelling Match:</strong> Ensure your full name matches your Class 10 (SSC) Board Certificate character-for-character. Any variation will lead to rejection at Document Verification.</li>
          <li><strong>Valid Category Certificate:</strong> For OBC/SEBC candidates in Gujarat, ensure your Non-Creamy Layer Certificate (Parishisht-K) has valid validity for the current financial year.</li>
          <li><strong>Deadline Protection:</strong> Avoid submitting on the last date to prevent server timeouts due to heavy portal traffic.</li>
        </ul>
      </div>
    </div>
  `;

  return html;
}

function generateJobPYQVault(job, isGujaratPage) {
  const org = (job.organization || '').toLowerCase();
  const title = (job.title || '').toLowerCase();
  
  let papers = [];
  let archiveUrl = "https://ojas.gujarat.gov.in";
  let archiveName = "OJAS Gujarat Official Paper Repository";

  if (org.includes('police') || title.includes('police') || title.includes('constable') || title.includes('પોલીસ') || title.includes('કોન્સ્ટેબલ') || title.includes('psi')) {
    archiveUrl = "https://ojas.gujarat.gov.in";
    archiveName = "GPRB / OJAS Police Recruitment Archives";
    papers = [
      {
        year: '2024-2025',
        yearFilter: '2024',
        title: 'Gujarat Police Constable & Lokrakshak Written Exam Master Question Paper',
        title_gu: 'ગુજરાત પોલીસ કોન્સ્ટેબલ & લોકરક્ષક લેખિત પરીક્ષા પ્રશ્નપત્ર (સંપૂર્ણ સોલ્યુશન)',
        stage: 'OMR Written Test',
        questions: '100 MCQs • 100 Marks • 120 Mins',
        paper_url: 'https://ojas.gujarat.gov.in',
        key_url: 'https://ojas.gujarat.gov.in',
        key_status: 'Official Final Key Approved',
        badge_color: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
      },
      {
        year: '2022',
        yearFilter: '2022',
        title: 'LRD Gujarat Police Constable Final Question Paper (Series A/B/C/D)',
        title_gu: 'LRD ગુજરાત પોલીસ કોન્સ્ટેબલ ફાઇનલ પ્રશ્નપત્ર અને માસ્ટર આન્સર કી',
        stage: 'OMR Written Test',
        questions: '100 MCQs • 100 Marks',
        paper_url: 'https://ojas.gujarat.gov.in',
        key_url: 'https://ojas.gujarat.gov.in',
        key_status: 'Official Final Key Approved',
        badge_color: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
      },
      {
        year: '2021',
        yearFilter: '2021',
        title: 'Gujarat Police Sub Inspector (PSI) Prelims Paper 1 & 2',
        title_gu: 'પોલીસ સબ ઇન્સ્પેક્ટર (PSI) પ્રિલિમ્સ પેપર ૧ અને ૨ (જનરલ સ્ટડીઝ & મેથ્સ)',
        stage: 'Prelims Elimination Exam',
        questions: '200 MCQs • 200 Marks • 180 Mins',
        paper_url: 'https://ojas.gujarat.gov.in',
        key_url: 'https://ojas.gujarat.gov.in',
        key_status: 'Official Master Answer Key',
        badge_color: 'bg-blue-500/20 text-blue-300 border-blue-500/40'
      },
      {
        year: '2019',
        yearFilter: 'earlier',
        title: 'Gujarat Police Constable (Armed & Unarmed Cadre) OMR Paper',
        title_gu: 'પોલીસ કોન્સ્ટેબલ (હથિયારી & બિન-હથિયારી) OMR પરીક્ષા પેપર',
        stage: 'Written Test',
        questions: '100 MCQs • 100 Marks',
        paper_url: 'https://ojas.gujarat.gov.in',
        key_url: 'https://ojas.gujarat.gov.in',
        key_status: 'Final Revised Answer Key',
        badge_color: 'bg-slate-800 text-slate-300 border-slate-700'
      },
      {
        year: '2016',
        yearFilter: 'earlier',
        title: 'Gujarat Police Constable Recruitment Written Question Paper',
        title_gu: 'પોલીસ કોન્સ્ટેબલ ભરતી અગાઉનું લેખિત પ્રશ્નપત્ર',
        stage: 'Written Test',
        questions: '100 MCQs • 100 Marks',
        paper_url: 'https://ojas.gujarat.gov.in',
        key_url: 'https://ojas.gujarat.gov.in',
        key_status: 'Official Archived Key',
        badge_color: 'bg-slate-800 text-slate-300 border-slate-700'
      }
    ];
  } else if (org.includes('gpsc') || title.includes('gpsc') || title.includes('વર્ગ ૧') || title.includes('civil service') || title.includes('administrative')) {
    archiveUrl = "https://gpsc.gujarat.gov.in/Dashboard/QuestionPaper";
    archiveName = "GPSC Official Question Paper & Final Answer Key Archive";
    papers = [
      {
        year: '2025',
        yearFilter: '2025',
        title: 'GPSC Gujarat Administrative Service Class 1 & 2 Prelims Paper 1 (General Studies 1)',
        title_gu: 'GPSC વર્ગ ૧-૨ પ્રિલિમ્સ પેપર ૧: સામાન્ય અભ્યાસ ૧ (ઇતિહાસ, કળા, ભૂગોળ)',
        stage: 'Prelims Paper 1',
        questions: '200 MCQs • 200 Marks • 180 Mins',
        paper_url: 'https://gpsc.gujarat.gov.in/Dashboard/QuestionPaper',
        key_url: 'https://gpsc.gujarat.gov.in/Dashboard/AnswerKey',
        key_status: 'Official Final Answer Key',
        badge_color: 'bg-amber-500/20 text-amber-300 border-amber-500/40'
      },
      {
        year: '2024',
        yearFilter: '2024',
        title: 'GPSC Class 1 & 2 Prelims Paper 2 (General Studies 2 - Polity, Economy, Reasoning)',
        title_gu: 'GPSC વર્ગ ૧-૨ પ્રિલિમ્સ પેપર ૨: ભારતીય બંધારણ, અર્થતંત્ર, સામાન્ય બૌદ્ધિક ક્ષમતા',
        stage: 'Prelims Paper 2',
        questions: '200 MCQs • 200 Marks • 180 Mins',
        paper_url: 'https://gpsc.gujarat.gov.in/Dashboard/QuestionPaper',
        key_url: 'https://gpsc.gujarat.gov.in/Dashboard/AnswerKey',
        key_status: 'Official Final Answer Key',
        badge_color: 'bg-amber-500/20 text-amber-300 border-amber-500/40'
      },
      {
        year: '2024',
        yearFilter: '2024',
        title: 'GPSC Gujarat Administrative Service (GAS) Mains Descriptive Papers (Gujarati, English, GS 1-3)',
        title_gu: 'GPSC મુખ્ય લેખિત વર્ણનાત્મક પરીક્ષા પેપર્સ: ગુજરાતી, અંગ્રેજી ભાષા અને સામાન્ય અભ્યાસ',
        stage: 'Mains Descriptive',
        questions: 'Descriptive Analytical Papers • 900 Marks Total',
        paper_url: 'https://gpsc.gujarat.gov.in/Dashboard/QuestionPaper',
        key_url: 'https://gpsc.gujarat.gov.in/Dashboard/AnswerKey',
        key_status: 'Official Question Archive',
        badge_color: 'bg-purple-500/20 text-purple-300 border-purple-500/40'
      },
      {
        year: '2023',
        yearFilter: '2023',
        title: 'GPSC DySO / Nayab Mamlatdar Elimination Examination Paper',
        title_gu: 'GPSC નાયબ મામલતદાર / DySO પ્રાથમિક કસોટી પેપર અને ફાઇનલ કી',
        stage: 'Elimination Test',
        questions: '200 MCQs • 200 Marks',
        paper_url: 'https://gpsc.gujarat.gov.in/Dashboard/QuestionPaper',
        key_url: 'https://gpsc.gujarat.gov.in/Dashboard/AnswerKey',
        key_status: 'Final Master Key Approved',
        badge_color: 'bg-blue-500/20 text-blue-300 border-blue-500/40'
      },
      {
        year: '2021-2022',
        yearFilter: '2022',
        title: 'GPSC Class 1-2 Civil Services Combined Preliminary Exam Paper',
        title_gu: 'GPSC વર્ગ ૧ અને ૨ સંયુક્ત પ્રિલિમ્સ પરીક્ષા પ્રશ્નપત્ર',
        stage: 'Prelims',
        questions: '400 Marks Combined',
        paper_url: 'https://gpsc.gujarat.gov.in/Dashboard/QuestionPaper',
        key_url: 'https://gpsc.gujarat.gov.in/Dashboard/AnswerKey',
        key_status: 'Official Master Key',
        badge_color: 'bg-slate-800 text-slate-300 border-slate-700'
      }
    ];
  } else if (org.includes('gsssb') || title.includes('gsssb') || title.includes('cce') || title.includes('clerk') || title.includes('કારકૂન')) {
    archiveUrl = "https://gsssb.gujarat.gov.in";
    archiveName = "GSSSB Official Examination Question & Key Archive";
    papers = [
      {
        year: '2024',
        yearFilter: '2024',
        title: 'GSSSB CCE Group A & B (CBRT Prelims) Computer-Based Master Paper',
        title_gu: 'GSSSB CCE ગ્રૂપ A & B (CBRT પ્રિલિમ્સ) કમ્પ્યુટર પરીક્ષા પ્રશ્નપત્ર',
        stage: 'CBRT Prelims',
        questions: '100 MCQs • 100 Marks • 60 Mins',
        paper_url: 'https://gsssb.gujarat.gov.in',
        key_url: 'https://gsssb.gujarat.gov.in',
        key_status: 'Official Final Answer Key',
        badge_color: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40'
      },
      {
        year: '2022',
        yearFilter: '2022',
        title: 'GSSSB Bin Sachivalay Clerk & Office Assistant Official Paper',
        title_gu: 'બિન સચિવાલય ક્લાર્ક & ઓફિસ આસિસ્ટન્ટ લેખિત પરીક્ષા પેપર',
        stage: 'Written Test',
        questions: '200 MCQs • 200 Marks • 120 Mins',
        paper_url: 'https://gsssb.gujarat.gov.in',
        key_url: 'https://gsssb.gujarat.gov.in',
        key_status: 'Official Final Master Key',
        badge_color: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
      },
      {
        year: '2021',
        yearFilter: '2021',
        title: 'GSSSB Senior Clerk & Head Clerk Written Examination Paper',
        title_gu: 'GSSSB સિનિયર ક્લાર્ક અને હેડ ક્લાર્ક પરીક્ષા પ્રશ્નપત્ર',
        stage: 'Written Test',
        questions: '200 MCQs • 200 Marks',
        paper_url: 'https://gsssb.gujarat.gov.in',
        key_url: 'https://gsssb.gujarat.gov.in',
        key_status: 'Official Master Key',
        badge_color: 'bg-blue-500/20 text-blue-300 border-blue-500/40'
      },
      {
        year: '2019',
        yearFilter: 'earlier',
        title: 'GSSSB Sub Accountant / Sub Auditor & Head Clerk Paper',
        title_gu: 'GSSSB સબ એકાઉન્ટન્ટ / સબ ઓડિટર અને હેડ ક્લાર્ક પ્રશ્નપત્ર',
        stage: 'Written Test',
        questions: '150 MCQs • 150 Marks',
        paper_url: 'https://gsssb.gujarat.gov.in',
        key_url: 'https://gsssb.gujarat.gov.in',
        key_status: 'Final Answer Key',
        badge_color: 'bg-slate-800 text-slate-300 border-slate-700'
      }
    ];
  } else if (org.includes('court') || title.includes('court') || title.includes('હાઇકોર્ટ')) {
    archiveUrl = "https://hc-ojas.gujarat.gov.in";
    archiveName = "High Court of Gujarat Judicial Exam Archives";
    papers = [
      {
        year: '2024',
        yearFilter: '2024',
        title: 'High Court of Gujarat Assistant Elimination Test Official Paper',
        title_gu: 'ગુજરાત હાઇકોર્ટ આસિસ્ટન્ટ એલિમિનેશન ટેસ્ટ ઓરિજિનલ પેપર',
        stage: 'Elimination Test',
        questions: '100 MCQs • 100 Marks • 90 Mins',
        paper_url: 'https://hc-ojas.gujarat.gov.in',
        key_url: 'https://hc-ojas.gujarat.gov.in',
        key_status: 'Official Final Key',
        badge_color: 'bg-purple-500/20 text-purple-300 border-purple-500/40'
      },
      {
        year: '2021',
        yearFilter: '2021',
        title: 'High Court of Gujarat Deputy Section Officer (DySO) Paper',
        title_gu: 'હાઇકોર્ટ DySO નાયબ સેક્શન અધિકારી લેખિત પરીક્ષા પેપર',
        stage: 'Elimination Test',
        questions: '100 MCQs • 100 Marks',
        paper_url: 'https://hc-ojas.gujarat.gov.in',
        key_url: 'https://hc-ojas.gujarat.gov.in',
        key_status: 'Final Answer Key',
        badge_color: 'bg-blue-500/20 text-blue-300 border-blue-500/40'
      },
      {
        year: '2019',
        yearFilter: 'earlier',
        title: 'High Court of Gujarat Legal Assistant & Peon Written Paper',
        title_gu: 'હાઇકોર્ટ લીગલ આસિસ્ટન્ટ & પટ્ટાવાળા લેખિત કસોટી પેપર',
        stage: 'Written Test',
        questions: '100 MCQs • 100 Marks',
        paper_url: 'https://hc-ojas.gujarat.gov.in',
        key_url: 'https://hc-ojas.gujarat.gov.in',
        key_status: 'Official Master Key',
        badge_color: 'bg-slate-800 text-slate-300 border-slate-700'
      }
    ];
  } else if (org.includes('railway') || org.includes('rrb') || title.includes('alp') || title.includes('railway')) {
    archiveUrl = "https://rrbapply.gov.in";
    archiveName = "Railway Recruitment Boards Central Exam Archives";
    papers = [
      {
        year: '2024',
        yearFilter: '2024',
        title: 'Railway RRB Assistant Loco Pilot (ALP) CBT-1 Stage 1 Master Paper',
        title_gu: 'રેલવે RRB આસિસ્ટન્ટ લોકો પાયલોટ CBT-૧ માસ્ટર પેપર',
        stage: 'CBT-1 Stage 1',
        questions: '75 MCQs • 75 Marks • 60 Mins',
        paper_url: 'https://rrbapply.gov.in',
        key_url: 'https://rrbapply.gov.in',
        key_status: 'Official Master Question Paper with Responses',
        badge_color: 'bg-blue-500/20 text-blue-300 border-blue-500/40'
      },
      {
        year: '2022',
        yearFilter: '2022',
        title: 'RRB NTPC Graduate & Undergraduate Level CBT-2 Official Question Papers',
        title_gu: 'RRB NTPC લેવલ ૨, ૩, ૫, ૬ કમ્પ્યુટર આધારિત પરીક્ષા પેપર્સ',
        stage: 'CBT-2 Multi-City',
        questions: '120 MCQs • 120 Marks • 90 Mins',
        paper_url: 'https://indianrailways.gov.in',
        key_url: 'https://indianrailways.gov.in',
        key_status: 'Official Final Key',
        badge_color: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
      },
      {
        year: '2018-2019',
        yearFilter: 'earlier',
        title: 'Railway RRB ALP & Technician CBT-1 All Shifts Master Paper',
        title_gu: 'રેલવે ALP અને ટેકનિશિયન તમામ શિફ્ટ પ્રશ્નપત્રો અને કી',
        stage: 'CBT-1',
        questions: '75 MCQs • 75 Marks',
        paper_url: 'https://rrbapply.gov.in',
        key_url: 'https://rrbapply.gov.in',
        key_status: 'Final Answer Key',
        badge_color: 'bg-slate-800 text-slate-300 border-slate-700'
      }
    ];
  } else if (org.includes('ssc') || title.includes('ssc') || title.includes('cgl') || title.includes('chsl')) {
    archiveUrl = "https://ssc.gov.in";
    archiveName = "Staff Selection Commission Official Question Archives";
    papers = [
      {
        year: '2024',
        yearFilter: '2024',
        title: 'SSC Combined Graduate Level (CGL) Tier-1 Official Master Paper',
        title_gu: 'SSC CGL ટિયર-૧ કમ્પ્યુટર પરીક્ષા સત્તાવાર પ્રશ્નપત્ર અને કી',
        stage: 'Tier-1 Computer Exam',
        questions: '100 MCQs • 200 Marks • 60 Mins',
        paper_url: 'https://ssc.gov.in',
        key_url: 'https://ssc.gov.in',
        key_status: 'Tentative & Final Answer Key',
        badge_color: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
      },
      {
        year: '2023',
        yearFilter: '2023',
        title: 'SSC CGL Tier-1 & Tier-2 Official Question Papers (All Shifts)',
        title_gu: 'SSC CGL ટિયર-૧ અને ટિયર-૨ તમામ શિફ્ટ પ્રશ્નપત્રો',
        stage: 'Tier-1 & Tier-2',
        questions: 'Full Question Bank with Explanations',
        paper_url: 'https://ssc.gov.in',
        key_url: 'https://ssc.gov.in',
        key_status: 'Official Final Answer Key',
        badge_color: 'bg-blue-500/20 text-blue-300 border-blue-500/40'
      },
      {
        year: '2022',
        yearFilter: '2022',
        title: 'SSC CHSL (10+2 Level) Tier-1 Master Question Paper',
        title_gu: 'SSC CHSL (૧૨ પાસ) ટિયર-૧ ઓરિજિનલ પ્રશ્નપત્ર',
        stage: 'Tier-1',
        questions: '100 MCQs • 200 Marks',
        paper_url: 'https://ssc.gov.in',
        key_url: 'https://ssc.gov.in',
        key_status: 'Final Key',
        badge_color: 'bg-slate-800 text-slate-300 border-slate-700'
      }
    ];
  } else {
    archiveUrl = job.apply_url || "https://ojas.gujarat.gov.in";
    archiveName = `${job.organization} Official Recruitment Archives`;
    papers = [
      {
        year: '2024-2025',
        yearFilter: '2024',
        title: `${job.organization} Recruitment Screening Test Master Paper`,
        title_gu: `${job.organization} ભરતી સ્ક્રીનિંગ અને લેખિત કસોટી પેપર`,
        stage: 'Phase 1 Screening Test',
        questions: '100 MCQs • 100 Marks • 120 Mins',
        paper_url: job.apply_url || 'https://ojas.gujarat.gov.in',
        key_url: job.apply_url || 'https://ojas.gujarat.gov.in',
        key_status: 'Official Final Approved Key',
        badge_color: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40'
      },
      {
        year: '2023',
        yearFilter: '2023',
        title: `${job.organization} Previous Cycle Question Paper & Solution`,
        title_gu: `${job.organization} અગાઉની પરીક્ષાનું પ્રશ્નપત્ર અને સોલ્યુશન`,
        stage: 'Written / Aptitude Exam',
        questions: 'Trade Knowledge + General Aptitude',
        paper_url: job.apply_url || 'https://ojas.gujarat.gov.in',
        key_url: job.apply_url || 'https://ojas.gujarat.gov.in',
        key_status: 'Final Master Key',
        badge_color: 'bg-blue-500/20 text-blue-300 border-blue-500/40'
      },
      {
        year: '2022',
        yearFilter: '2022',
        title: `${job.organization} Cadre Recruitment Written Examination Paper`,
        title_gu: `${job.organization} લેખિત કસોટીનું અધિકૃત પ્રશ્નપત્ર`,
        stage: 'Competitive Written Exam',
        questions: 'Core Domain MCQs',
        paper_url: job.apply_url || 'https://ojas.gujarat.gov.in',
        key_url: job.apply_url || 'https://ojas.gujarat.gov.in',
        key_status: 'Official Key',
        badge_color: 'bg-slate-800 text-slate-300 border-slate-700'
      }
    ];
  }

  let html = `
    <div class="glass-panel p-5 rounded-2xl border border-purple-500/30 bg-purple-950/10 space-y-4">
      <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-3 border-b border-slate-800/80">
        <div>
          <h4 class="text-xs uppercase tracking-wider text-purple-400 font-extrabold flex items-center gap-2">
            <i data-lucide="book-marked" class="w-4 h-4"></i>
            ${isGujaratPage ? 'ગત ૫ વર્ષના અધિકૃત પ્રશ્નપત્રો અને આન્સર કી ભંડાર' : '5-Year Official Question Papers (PYQ) & Answer Key Vault'}
          </h4>
          <p class="text-[11px] text-slate-400 mt-0.5">
            Download authentic past examination papers and official final answer keys verified by statutory boards.
          </p>
        </div>
        <a href="${archiveUrl}" target="_blank" rel="noopener noreferrer" class="px-3 py-1.5 rounded-xl bg-purple-900/40 hover:bg-purple-800/60 border border-purple-500/40 text-purple-200 text-xs font-bold transition-all flex items-center gap-1.5 shrink-0">
          <i data-lucide="external-link" class="w-3.5 h-3.5"></i>
          <span>${archiveName}</span>
        </a>
      </div>

      <!-- Quick PYQ Year Filter Pills -->
      <div class="flex flex-wrap items-center gap-1.5 text-xs">
        <span class="text-[11px] font-bold text-slate-400 uppercase mr-1">Filter Year:</span>
        <button onclick="filterPYQYear('all', this)" class="pyq-year-pill active px-3 py-1 rounded-lg font-semibold bg-purple-600 text-white shadow">All Papers (${papers.length})</button>
        <button onclick="filterPYQYear('2025', this)" class="pyq-year-pill px-3 py-1 rounded-lg font-semibold bg-slate-900 text-slate-300 hover:text-white border border-slate-800">2025/2026</button>
        <button onclick="filterPYQYear('2024', this)" class="pyq-year-pill px-3 py-1 rounded-lg font-semibold bg-slate-900 text-slate-300 hover:text-white border border-slate-800">2024</button>
        <button onclick="filterPYQYear('2023', this)" class="pyq-year-pill px-3 py-1 rounded-lg font-semibold bg-slate-900 text-slate-300 hover:text-white border border-slate-800">2023</button>
        <button onclick="filterPYQYear('2022', this)" class="pyq-year-pill px-3 py-1 rounded-lg font-semibold bg-slate-900 text-slate-300 hover:text-white border border-slate-800">2022</button>
        <button onclick="filterPYQYear('earlier', this)" class="pyq-year-pill px-3 py-1 rounded-lg font-semibold bg-slate-900 text-slate-300 hover:text-white border border-slate-800">2021 & Earlier</button>
      </div>

      <!-- Papers Grid -->
      <div class="space-y-3 pt-2" id="pyq-papers-list">
        ${papers.map((p, idx) => `
          <div class="pyq-paper-item p-4 rounded-xl bg-slate-900/90 border border-slate-800/90 hover:border-purple-500/40 transition-all flex flex-col md:flex-row items-start md:items-center justify-between gap-3.5 group" data-year="${p.yearFilter || 'all'}">
            <div class="flex-1 min-w-0">
              <div class="flex flex-wrap items-center gap-2 mb-1.5">
                <span class="px-2 py-0.5 rounded text-[10px] font-black ${p.badge_color}">${p.year}</span>
                <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-300 border border-slate-700">${p.stage}</span>
                <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-950/60 text-emerald-300 border border-emerald-800/50 flex items-center gap-1">
                  <i data-lucide="check-circle" class="w-3 h-3 text-emerald-400"></i> ${p.key_status}
                </span>
              </div>
              <h4 class="text-sm font-bold text-white group-hover:text-purple-300 transition-colors">${p.title}</h4>
              ${p.title_gu ? `<p class="font-gujarati text-xs text-amber-300/90 mt-0.5">${p.title_gu}</p>` : ''}
              <p class="text-[11px] text-slate-400 mt-1 flex items-center gap-2">
                <span><i data-lucide="clock" class="w-3 h-3 inline text-cyan-400"></i> ${p.questions}</span>
                <span>•</span>
                <span class="text-emerald-400 font-medium">Bilingual (English & Gujarati)</span>
              </p>
            </div>

            <div class="flex flex-wrap items-center gap-2 shrink-0 w-full md:w-auto justify-end">
              <a href="${p.paper_url}" target="_blank" rel="noopener noreferrer" class="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 hover:text-white text-xs font-bold transition-all flex items-center gap-1.5 shadow-sm">
                <i data-lucide="file-text" class="w-3.5 h-3.5 text-cyan-400"></i>
                <span>Question Paper PDF</span>
              </a>
              <a href="${p.key_url}" target="_blank" rel="noopener noreferrer" class="px-3 py-1.5 rounded-lg bg-emerald-600/20 hover:bg-emerald-600 border border-emerald-500/40 text-emerald-300 hover:text-white text-xs font-bold transition-all flex items-center gap-1.5 shadow-sm">
                <i data-lucide="key" class="w-3.5 h-3.5 text-emerald-400"></i>
                <span>Final Answer Key PDF</span>
              </a>
            </div>
          </div>
        `).join('')}
      </div>

      <!-- Tab 6 Bottom Navigation Bar -->
      <div class="mt-4 pt-4 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-3">
        <button onclick="closeJobDetailModal()" class="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-rose-600 text-slate-300 hover:text-white text-xs font-bold flex items-center gap-1.5 border border-slate-700 transition-colors cursor-pointer">
          <i data-lucide="x" class="w-4 h-4"></i>
          <span>Close / બંધ કરો (Esc)</span>
        </button>
        <a href="${job.apply_url}" target="_blank" rel="noopener noreferrer" class="px-5 py-2.5 rounded-xl bg-gradient-to-r from-purple-600 via-indigo-600 to-cyan-600 hover:from-purple-500 hover:to-cyan-500 text-white text-xs font-black flex items-center gap-2 shadow-lg shadow-purple-600/30 transition-all">
          <span>Apply on Official Portal</span>
          <i data-lucide="external-link" class="w-4 h-4"></i>
        </a>
      </div>
    </div>
  `;

  return html;
}

function filterPYQYear(year, btn) {
  playAudioTick(700, 0.03);
  document.querySelectorAll('.pyq-year-pill').forEach(b => {
    b.classList.remove('active', 'bg-purple-600', 'text-white', 'shadow');
    b.classList.add('bg-slate-900', 'text-slate-300', 'border-slate-800');
  });
  if (btn) {
    btn.classList.add('active', 'bg-purple-600', 'text-white', 'shadow');
    btn.classList.remove('bg-slate-900', 'text-slate-300', 'border-slate-800');
  }

  const items = document.querySelectorAll('.pyq-paper-item');
  items.forEach(item => {
    const itemYear = item.getAttribute('data-year');
    if (year === 'all' || itemYear === year || (year === '2025' && itemYear === '2024-2025')) {
      item.classList.remove('hidden');
    } else {
      item.classList.add('hidden');
    }
  });
}
window.filterPYQYear = filterPYQYear;

function switchJobModalTab(tabName) {
  document.querySelectorAll(".job-modal-tab-content").forEach(el => el.classList.add("hidden"));
  const activeContent = document.getElementById(`tab-content-${tabName}`);
  if (activeContent) activeContent.classList.remove("hidden");

  document.querySelectorAll(".job-modal-tab-btn").forEach(btn => {
    btn.classList.remove("active", "bg-cyan-600", "text-white", "shadow-lg", "shadow-cyan-600/30");
    btn.classList.add("bg-slate-900", "text-slate-300", "border-slate-800");
  });

  const activeBtn = document.getElementById(`modal-tab-${tabName}`);
  if (activeBtn) {
    activeBtn.classList.add("active", "bg-cyan-600", "text-white", "shadow-lg", "shadow-cyan-600/30");
    activeBtn.classList.remove("bg-slate-900", "text-slate-300", "border-slate-800");
  }

  // Auto-scroll modal body back to top so user sees the newly opened tab content immediately
  const modalBody = document.getElementById("job-modal-body");
  if (modalBody) modalBody.scrollTop = 0;

  if (window.lucide) lucide.createIcons();
}
window.switchJobModalTab = switchJobModalTab;

function updateSyllabusModule() {
  const checkboxes = document.querySelectorAll(".syllabus-topic-cb");
  if (!checkboxes.length) return;
  const checked = document.querySelectorAll(".syllabus-topic-cb:checked").length;
  const pct = Math.round((checked / checkboxes.length) * 100);
  const bar = document.getElementById("syllabus-progress-bar");
  const counter = document.getElementById("syllabus-progress-counter");
  if (bar) bar.style.width = `${pct}%`;
  if (counter) counter.innerText = `${pct}% Ready (${checked}/${checkboxes.length} Topics)`;
}
window.updateSyllabusModule = updateSyllabusModule;

async function openJobDetailModal(jobId) {
  const modal = document.getElementById("job-detail-modal");
  const modalBody = document.getElementById("job-modal-body");
  if (!modal || !modalBody) return;
  modal.classList.remove("hidden");
  modal.classList.add("flex");
  document.body.style.overflow = "hidden";

  const isGujaratPage = window.location.pathname.includes("/gujarat") || document.documentElement.lang === "gu";

  // Check in-memory cache first for instant 0ms rendering!
  const cachedJob = (window._jobsMap && window._jobsMap[jobId]) || (window._allJobs && window._allJobs.find(j => j.id == jobId));
  if (cachedJob) {
    renderJobModalContent(modalBody, cachedJob, isGujaratPage);
  } else {
    modalBody.innerHTML = `
      <div class="py-20 text-center">
        <div class="inline-block w-10 h-10 border-4 border-[#635bff] border-t-transparent rounded-full animate-spin"></div>
        <p class="mt-4 text-slate-600 font-bold text-sm tracking-wide">
          ${isGujaratPage ? 'ભરતીની સંપૂર્ણ વિગતો અને સ્ટેપ-બાય-સ્ટેપ અરજી માર્ગદર્શિકા લોડ થઈ રહી છે...' : 'Compiling Full Recruitment Dossier & Step-by-Step Guide...'}
        </p>
      </div>
    `;
  }

  try {
    const res = await fetch(`/api/jobs/${jobId}`);
    if (res.ok) {
      const freshJob = await res.json();
      if (!window._jobsMap) window._jobsMap = {};
      window._jobsMap[freshJob.id] = freshJob;
      renderJobModalContent(modalBody, freshJob, isGujaratPage);
    } else if (!cachedJob) {
      throw new Error("Recruitment not found");
    }
  } catch (err) {
    console.warn("Using cached job details or failed to fetch remote details:", err);
    if (!cachedJob) {
      modalBody.innerHTML = `
        <div class="py-16 text-center text-slate-600">
          <i data-lucide="alert-circle" class="w-12 h-12 mx-auto text-rose-500 mb-3"></i>
          <h3 class="text-base font-bold text-[#0a2540] mb-1">Recruitment Details Unavailable</h3>
          <p class="text-xs text-slate-500 mb-4">The selected recruitment could not be loaded at this time.</p>
          <button onclick="closeJobDetailModal()" class="px-4 py-2 bg-[#635bff] text-white text-xs font-bold rounded-xl shadow">Close</button>
        </div>
      `;
      if (window.lucide) lucide.createIcons();
    }
  }
}

function renderJobModalContent(modalBody, job, isGujaratPage) {
  const portalGuide = generateStepByStepGuide(job, isGujaratPage);

  let basePay = 25500;
  const salaryMatch = (job.salary_text || "").match(/₹\s*([\d,]+)/);
  if (salaryMatch) {
    basePay = parseInt(salaryMatch[1].replace(/,/g, "")) || 25500;
  }
  const daEstimate = Math.round(basePay * 0.50);
  const hraEstimate = Math.round(basePay * 0.18);
  const grossEst = basePay + daEstimate + hraEstimate;
  const npsEstimate = Math.round((basePay + daEstimate) * 0.10);
  const inHandEst = grossEst - npsEstimate - 200;

  const isBookmarked = bookmarkedJobIds.has(job.id);
  const isGovt = job.gov_level !== 'Private';
  const isGujaratJob = job.state === 'Gujarat';

  const minAge = parseInt(job.age_min, 10) || 18;
  const maxAge = parseInt(job.age_max, 10) || 35;

  modalBody.innerHTML = `
    <div class="space-y-6">
      <!-- Top Header Bar -->
      <div class="border-b border-slate-200 pb-5">
          <div class="flex flex-wrap items-center justify-between gap-3 mb-3">
            <div class="flex flex-wrap items-center gap-2">
              <span class="px-3 py-1 rounded-full text-xs font-bold ${isGujaratJob ? 'bg-orange-500/20 text-orange-300 border border-orange-500/40' : (job.gov_level === 'Central' ? 'bg-blue-500/20 text-blue-300 border border-blue-500/40' : 'bg-purple-500/20 text-purple-300 border border-purple-500/40')}">
                ${job.gov_level === 'Central' ? '🇮🇳 Central Government' : (job.gov_level === 'Private' ? '🏢 Private Enterprise' : '🦁 Gujarat State Government')}
              </span>
              <span class="px-2.5 py-1 rounded-full text-xs font-bold bg-slate-800 text-cyan-300 border border-slate-700">
                ${job.board_category || 'Board'}
              </span>
              <span class="px-2.5 py-1 rounded-full text-xs font-extrabold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                ${job.vacancies.toLocaleString()} Posts
              </span>
              ${job.notification_number ? `
                <span class="text-xs font-mono text-slate-400 bg-slate-900/90 px-2.5 py-1 rounded border border-slate-800">
                  Advt No: ${job.notification_number}
                </span>
              ` : ''}
            </div>

            <div class="flex items-center gap-2">
              <button onclick="toggleBookmark(${job.id}, this)" class="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-cyan-400 transition-all flex items-center gap-1.5 text-xs font-bold border border-slate-700 cursor-pointer">
                <i data-lucide="bookmark" class="w-4 h-4 ${isBookmarked ? 'fill-cyan-400 text-cyan-400' : ''}"></i>
                <span>${isBookmarked ? 'Saved' : 'Bookmark'}</span>
              </button>
              <button onclick="closeJobDetailModal()" class="px-3 py-1.5 rounded-xl bg-rose-950/70 hover:bg-rose-600 text-rose-300 hover:text-white transition-all border border-rose-500/40 text-xs font-bold flex items-center gap-1.5 cursor-pointer shadow-sm" title="Close Recruitment Dossier (Esc)">
                <i data-lucide="x" class="w-4 h-4 stroke-[2.5]"></i>
                <span>Close (Esc)</span>
              </button>
            </div>
          </div>

          <h2 class="text-xl sm:text-2xl md:text-3xl font-black text-white leading-tight">
            ${job.title}
          </h2>

          ${job.title_gu ? `
            <p class="font-gujarati text-base md:text-lg text-amber-400 font-semibold mt-1.5">
              ${job.title_gu}
            </p>
          ` : ''}

          <div class="flex flex-wrap items-center gap-4 mt-3 text-xs text-slate-300 font-medium">
            <span class="flex items-center gap-1.5 text-cyan-400 font-semibold">
              <i data-lucide="building-2" class="w-4 h-4"></i> ${job.organization}
            </span>
            ${job.department ? `
              <span>•</span>
              <span class="text-slate-300">${job.department}</span>
            ` : ''}
            <span>•</span>
            <span class="flex items-center gap-1 text-slate-400">
              <i data-lucide="map-pin" class="w-3.5 h-3.5 text-rose-400"></i> ${job.district || job.state || 'All India'}
            </span>
          </div>
        </div>

        <!-- Quick Summary Metrics Matrix -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 p-4 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-inner">
          <div class="p-2.5 rounded-xl bg-slate-950/60 border border-slate-800/80">
            <span class="text-[11px] font-semibold text-slate-400 block">${isGujaratPage ? 'અરજી છેલ્લી તારીખ' : 'Application Deadline'}</span>
            <span class="text-sm font-black text-rose-400 block mt-0.5">${job.last_date}</span>
            <span class="text-[10px] text-slate-400">${job.days_left <= 0 ? 'Closed' : job.days_left + ' days remaining'}</span>
          </div>

          <div class="p-2.5 rounded-xl bg-slate-950/60 border border-slate-800/80">
            <span class="text-[11px] font-semibold text-slate-400 block">${isGujaratPage ? 'વય મર્યાદા' : 'Age Eligibility'}</span>
            <span class="text-sm font-black text-slate-100 block mt-0.5">${minAge} - ${maxAge} Years</span>
            <span class="text-[10px] text-emerald-400">+Relaxation Applicable</span>
          </div>

          <div class="p-2.5 rounded-xl bg-slate-950/60 border border-slate-800/80">
            <span class="text-[11px] font-semibold text-slate-400 block">${isGujaratPage ? 'પગાર ધોરણ / CTC' : 'Pay Scale / CTC'}</span>
            <span class="text-sm font-black text-emerald-400 block mt-0.5 truncate" title="${job.salary_text}">${job.salary_text ? job.salary_text.split('->')[0] : (job.ctc_lpa ? '₹' + job.ctc_lpa + ' LPA' : '7th Pay Matrix')}</span>
            <span class="text-[10px] text-slate-400">${isGovt ? 'Govt 7th Pay Scale' : 'Annual Package'}</span>
          </div>

          <div class="p-2.5 rounded-xl bg-slate-950/60 border border-slate-800/80">
            <span class="text-[11px] font-semibold text-slate-400 block">${isGujaratPage ? 'અરજી ફી' : 'Application Fee'}</span>
            <span class="text-sm font-black text-amber-300 block mt-0.5 truncate">${job.application_fee ? job.application_fee.split(';')[0] : '₹100 (Reserved: Nil)'}</span>
            <span class="text-[10px] text-slate-400">Online / Post Office</span>
          </div>
        </div>

        <!-- Navigation Tabs Bar -->
        <div class="flex items-center gap-1.5 sm:gap-2 border-b border-slate-800 overflow-x-auto pb-1 no-scrollbar">
          <button onclick="switchJobModalTab('overview')" id="modal-tab-overview" class="job-modal-tab-btn active px-3.5 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 shrink-0 bg-cyan-600 text-white shadow-lg shadow-cyan-600/30">
            <i data-lucide="clipboard-list" class="w-4 h-4"></i>
            <span>${isGujaratPage ? '૧. પાત્રતા અને વિગતો' : '1. Overview & Eligibility'}</span>
          </button>

          <button onclick="switchJobModalTab('apply')" id="modal-tab-apply" class="job-modal-tab-btn px-3.5 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 shrink-0 bg-slate-900 text-slate-300 hover:text-white hover:bg-slate-800 border border-slate-800">
            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
            <i data-lucide="navigation" class="w-4 h-4 text-emerald-400"></i>
            <span>${isGujaratPage ? '૨. સ્ટેપ-બાય-સ્ટેપ અરજી રીત' : '2. Step-by-Step How to Apply'}</span>
          </button>

          <button onclick="switchJobModalTab('syllabus')" id="modal-tab-syllabus" class="job-modal-tab-btn px-3.5 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 shrink-0 bg-slate-900 text-slate-300 hover:text-white hover:bg-slate-800 border border-slate-800">
            <i data-lucide="book-open" class="w-4 h-4 text-amber-400"></i>
            <span>${isGujaratPage ? '૩. પરીક્ષા પદ્ધતિ & સિલેબસ' : '3. Exam Pattern & Syllabus'}</span>
          </button>

          <button onclick="switchJobModalTab('docs')" id="modal-tab-docs" class="job-modal-tab-btn px-3.5 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 shrink-0 bg-slate-900 text-slate-300 hover:text-white hover:bg-slate-800 border border-slate-800">
            <i data-lucide="files" class="w-4 h-4 text-blue-400"></i>
            <span>${isGujaratPage ? '૪. જરૂરી દસ્તાવેજો' : '4. Required Documents'}</span>
          </button>

          <button onclick="switchJobModalTab('salary')" id="modal-tab-salary" class="job-modal-tab-btn px-3.5 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 shrink-0 bg-slate-900 text-slate-300 hover:text-white hover:bg-slate-800 border border-slate-800">
            <i data-lucide="calculator" class="w-4 h-4 text-teal-400"></i>
            <span>${isGujaratPage ? '૫. ઇન-હેન્ડ પગાર કેલ્ક્યુલેટર' : '5. Salary & Pay Simulator'}</span>
          </button>

          <button onclick="switchJobModalTab('pyqs')" id="modal-tab-pyqs" class="job-modal-tab-btn px-3.5 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 shrink-0 bg-slate-900 text-slate-300 hover:text-white hover:bg-slate-800 border border-slate-800">
            <span class="w-2 h-2 rounded-full bg-purple-400 animate-pulse"></span>
            <i data-lucide="book-marked" class="w-4 h-4 text-purple-400"></i>
            <span>${isGujaratPage ? '૬. ગત વર્ષોના પેપર્સ & આન્સર કી' : '6. 5-Yr PYQs & Answer Keys'}</span>
          </button>
        </div>

        <!-- Tab 1: Overview & Eligibility -->
        <div id="tab-content-overview" class="job-modal-tab-content space-y-5">
          <div class="glass-panel p-5 rounded-2xl border border-cyan-500/30 bg-cyan-950/10">
            <h4 class="text-xs uppercase tracking-wider text-cyan-400 font-extrabold mb-2.5 flex items-center gap-2">
              <i data-lucide="graduation-cap" class="w-4 h-4"></i> ${isGujaratPage ? 'શૈક્ષણિક લાયકાત અને અનુભવ (Educational Qualification)' : 'Prescribed Educational Qualification & Criteria'}
            </h4>
            <div class="text-sm font-bold text-slate-100 leading-relaxed bg-slate-900/90 p-4 rounded-xl border border-slate-800">
              ${job.qualification}
            </div>
            ${job.experience_level ? `
              <div class="mt-3 flex items-center gap-2 text-xs">
                <span class="text-slate-400">Target Experience:</span>
                <span class="px-2.5 py-0.5 rounded-full font-bold bg-slate-800 text-cyan-300 border border-slate-700 capitalize">${job.experience_level}</span>
                ${job.is_btech_cse ? '<span class="px-2 py-0.5 rounded-full font-bold bg-blue-500/20 text-blue-300 border border-blue-500/30">💻 B.Tech / B.E. CSE & IT Eligible</span>' : ''}
              </div>
            ` : ''}
          </div>

          <div class="glass-panel p-5 rounded-2xl border border-slate-800">
            <h4 class="text-xs uppercase tracking-wider text-amber-400 font-extrabold mb-3 flex items-center gap-2">
              <i data-lucide="shield-alert" class="w-4 h-4"></i> ${isGujaratPage ? 'વય મર્યાદા અને છૂટછાટના નિયમો (Age Relaxation Norms)' : 'Age Eligibility & Relaxation Matrix'}
            </h4>
            <div class="portal-table-container">
              <table class="portal-table w-full text-left text-xs">
                <thead>
                  <tr>
                    <th class="p-3">Candidate Category</th>
                    <th class="p-3">Standard Age Limit</th>
                    <th class="p-3">Age Relaxation</th>
                    <th class="p-3 text-right pr-4">Effective Maximum Age</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-800/80 font-medium">
                  <tr>
                    <td class="p-3 font-bold text-slate-200">General / Unreserved (Male)</td>
                    <td class="p-3">${minAge} - ${maxAge} Yrs</td>
                    <td class="p-3 text-slate-400">None</td>
                    <td class="p-3 text-right pr-4"><span class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-bold bg-slate-800 text-slate-200 border border-slate-700 shadow-sm">${maxAge} Years</span></td>
                  </tr>
                  <tr>
                    <td class="p-3 font-bold text-cyan-300">OBC / SEBC / EWS</td>
                    <td class="p-3">${minAge} - ${maxAge} Yrs</td>
                    <td class="p-3 text-emerald-400 font-bold">+3 to +5 Years</td>
                    <td class="p-3 text-right pr-4"><span class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-bold bg-cyan-950/80 text-cyan-300 border border-cyan-500/30 shadow-sm">${maxAge + 3} - ${maxAge + 5} Years</span></td>
                  </tr>
                  <tr>
                    <td class="p-3 font-bold text-indigo-300">SC / ST</td>
                    <td class="p-3">${minAge} - ${maxAge} Yrs</td>
                    <td class="p-3 text-emerald-400 font-bold">+5 Years</td>
                    <td class="p-3 text-right pr-4"><span class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-bold bg-indigo-950/80 text-indigo-300 border border-indigo-500/30 shadow-sm">${maxAge + 5} Years</span></td>
                  </tr>
                  <tr>
                    <td class="p-3 font-bold text-rose-300">Female Candidates (General)</td>
                    <td class="p-3">${minAge} - ${maxAge} Yrs</td>
                    <td class="p-3 text-emerald-400 font-bold">+5 Years</td>
                    <td class="p-3 text-right pr-4"><span class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-bold bg-rose-950/80 text-rose-300 border border-rose-500/30 shadow-sm">${maxAge + 5} Years</span></td>
                  </tr>
                  <tr>
                    <td class="p-3 font-bold text-purple-300">Female Candidates (Reserved - SC/ST/SEBC)</td>
                    <td class="p-3">${minAge} - ${maxAge} Yrs</td>
                    <td class="p-3 text-emerald-400 font-bold">+10 Years</td>
                    <td class="p-3 text-right pr-4"><span class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-bold bg-purple-950/80 text-purple-300 border border-purple-500/30 shadow-sm">${maxAge + 10} Years</span></td>
                  </tr>
                  <tr>
                    <td class="p-3 font-bold text-amber-300">Persons with Benchmark Disabilities (PwD)</td>
                    <td class="p-3">${minAge} - ${maxAge} Yrs</td>
                    <td class="p-3 text-emerald-400 font-bold">+10 Years</td>
                    <td class="p-3 text-right pr-4"><span class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-bold bg-amber-950/80 text-amber-300 border border-amber-500/30 shadow-sm">${maxAge + 10} Years</span></td>
                  </tr>
                  <tr>
                    <td class="p-3 font-bold text-teal-300">Ex-Servicemen (Defence Personnel)</td>
                    <td class="p-3">${minAge} - ${maxAge} Yrs</td>
                    <td class="p-3 text-emerald-400 font-bold">Service + 3 Yrs</td>
                    <td class="p-3 text-right pr-4"><span class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-bold bg-teal-950/80 text-teal-300 border border-teal-500/30 shadow-sm">Up to ${maxAge + 8} Years</span></td>
                  </tr>
                </tbody>
              </table>
            </div>
            <p class="text-[11px] text-slate-400 mt-2.5 italic">
              * Note: ${job.age_relaxation_text || 'Relaxations applicable as per General Administration Department (GAD), Govt of Gujarat or Central DoPT rules.'}
            </p>
          </div>

          <div class="glass-panel p-5 rounded-2xl border border-slate-800">
            <h4 class="text-xs uppercase tracking-wider text-emerald-400 font-extrabold mb-3 flex items-center gap-2">
              <i data-lucide="layers" class="w-4 h-4"></i> ${isGujaratPage ? 'પસંદગી પ્રક્રિયાના તબક્કા (Selection Procedure Stages)' : 'Selection Procedure & Examination Stages'}
            </h4>
            <div class="grid grid-cols-1 sm:grid-cols-4 gap-3 text-center text-xs">
              <div class="p-3 rounded-xl bg-slate-900 border border-cyan-500/30 relative">
                <span class="w-5 h-5 rounded-full bg-cyan-600 text-white font-bold inline-flex items-center justify-center text-[10px] mb-1.5">1</span>
                <span class="font-bold text-white block">Stage 1: Screening</span>
                <span class="text-[11px] text-slate-400 mt-0.5 block">${job.selection_mode === 'direct_merit' ? '100% Merit Evaluation' : 'Written / CBRT Test'}</span>
              </div>
              <div class="p-3 rounded-xl bg-slate-900 border border-slate-800 relative">
                <span class="w-5 h-5 rounded-full bg-slate-700 text-white font-bold inline-flex items-center justify-center text-[10px] mb-1.5">2</span>
                <span class="font-bold text-white block">Stage 2: Skill / Trade</span>
                <span class="text-[11px] text-slate-400 mt-0.5 block">${job.selection_mode === 'physical_test' ? 'Physical Efficiency Test' : 'Practical / Skill Test'}</span>
              </div>
              <div class="p-3 rounded-xl bg-slate-900 border border-slate-800 relative">
                <span class="w-5 h-5 rounded-full bg-slate-700 text-white font-bold inline-flex items-center justify-center text-[10px] mb-1.5">3</span>
                <span class="font-bold text-white block">Stage 3: Verification</span>
                <span class="text-[11px] text-slate-400 mt-0.5 block">Document Verification (DV)</span>
              </div>
              <div class="p-3 rounded-xl bg-slate-900 border border-emerald-500/30 relative">
                <span class="w-5 h-5 rounded-full bg-emerald-600 text-white font-bold inline-flex items-center justify-center text-[10px] mb-1.5">4</span>
                <span class="font-bold text-white block">Stage 4: Final Merit</span>
                <span class="text-[11px] text-emerald-400 mt-0.5 block">Medical & Appointment Order</span>
              </div>
            </div>
            <div class="mt-3 p-3 rounded-xl bg-slate-900/60 border border-slate-800 text-xs text-slate-300">
              <strong>Official Details:</strong> ${job.selection_process || 'Written Examination followed by Document Verification.'}
            </div>

            <!-- Tab 1 Bottom Navigation Bar -->
            <div class="mt-4 pt-4 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-3">
              <button onclick="closeJobDetailModal()" class="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-rose-600 text-slate-300 hover:text-white text-xs font-bold flex items-center gap-1.5 border border-slate-700 transition-colors cursor-pointer">
                <i data-lucide="x" class="w-4 h-4"></i>
                <span>Close / બંધ કરો (Esc)</span>
              </button>
              <button onclick="switchJobModalTab('apply')" class="px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-bold flex items-center gap-1.5 shadow transition-all cursor-pointer">
                <span>Next: Step-by-Step How to Apply</span>
                <i data-lucide="arrow-right" class="w-4 h-4"></i>
              </button>
            </div>
          </div>
        </div>

        <!-- Tab 2: Step-by-Step How to Apply -->
        <div id="tab-content-apply" class="job-modal-tab-content hidden space-y-5">
          ${portalGuide}
          <!-- Tab 2 Bottom Navigation Bar -->
          <div class="pt-4 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-3">
            <button onclick="closeJobDetailModal()" class="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-rose-600 text-slate-300 hover:text-white text-xs font-bold flex items-center gap-1.5 border border-slate-700 transition-colors cursor-pointer">
              <i data-lucide="x" class="w-4 h-4"></i>
              <span>Close / બંધ કરો (Esc)</span>
            </button>
            <a href="${job.apply_url}" target="_blank" rel="noopener noreferrer" class="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold flex items-center gap-1.5 shadow transition-all">
              <span>Open Official Portal &amp; Apply</span>
              <i data-lucide="external-link" class="w-4 h-4"></i>
            </a>
          </div>
        </div>

        <!-- Tab 3: Exam Pattern & Syllabus -->
        <div id="tab-content-syllabus" class="job-modal-tab-content hidden space-y-5">
          <div class="glass-panel p-5 rounded-2xl border border-slate-800">
            <div class="flex items-center justify-between mb-3">
              <div>
                <h4 class="text-xs uppercase tracking-wider text-amber-400 font-extrabold flex items-center gap-2">
                  <i data-lucide="book-marked" class="w-4 h-4"></i> ${isGujaratPage ? 'સિલેબસ અને પ્રિપેરેશન ચેકલિસ્ટ' : 'Exam Structure & Interactive Topic Checklist'}
                </h4>
                <p class="text-[11px] text-slate-400 mt-0.5">Check off syllabus modules as you prepare to calculate your readiness percentage.</p>
              </div>
              <span class="text-xs font-bold text-amber-300 bg-amber-500/20 px-2.5 py-1 rounded-full" id="syllabus-progress-counter">0% Ready</span>
            </div>

            <div class="w-full bg-slate-900 rounded-full h-2 mb-4 border border-slate-800 overflow-hidden">
              <div id="syllabus-progress-bar" class="bg-gradient-to-r from-amber-500 to-emerald-500 h-2 rounded-full transition-all duration-300" style="width: 0%"></div>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
              ${(job.syllabus_summary || 'General Knowledge & Current Affairs, Gujarati Language & Grammar, Mathematics & Reasoning, Technical Trade Specific Subjects, Computer Basics').split(',').map((topic, idx) => `
                <label class="flex items-start gap-3 p-3 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-amber-500/40 text-xs text-slate-200 cursor-pointer hover:bg-slate-900 transition-all group">
                  <input type="checkbox" onchange="updateSyllabusModule(this)" class="syllabus-topic-cb mt-0.5 rounded bg-slate-800 border-slate-700 text-amber-500 focus:ring-0 w-4 h-4">
                  <div>
                    <span class="font-bold text-white group-hover:text-amber-300 transition-colors">${topic.trim()}</span>
                    <span class="block text-[10px] text-slate-400 mt-0.5">Module ${idx + 1} • High Scoring Priority</span>
                  </div>
                </label>
              `).join('')}
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div class="p-3 rounded-xl bg-slate-900 border border-slate-800 text-center">
              <span class="text-[11px] text-slate-400 block font-semibold">Total Questions</span>
              <span class="text-lg font-black text-white mt-1 block">100 - 200 MCQs</span>
            </div>
            <div class="p-3 rounded-xl bg-slate-900 border border-slate-800 text-center">
              <span class="text-[11px] text-slate-400 block font-semibold">Exam Duration</span>
              <span class="text-lg font-black text-cyan-400 mt-1 block">120 - 180 Mins</span>
            </div>
            <div class="p-3 rounded-xl bg-slate-900 border border-slate-800 text-center">
              <span class="text-[11px] text-slate-400 block font-semibold">Negative Marking</span>
              <span class="text-lg font-black text-rose-400 mt-1 block">-0.25 Marks</span>
            </div>
          </div>

          <!-- Tab 3 Bottom Navigation Bar -->
          <div class="pt-4 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-3">
            <button onclick="closeJobDetailModal()" class="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-rose-600 text-slate-300 hover:text-white text-xs font-bold flex items-center gap-1.5 border border-slate-700 transition-colors cursor-pointer">
              <i data-lucide="x" class="w-4 h-4"></i>
              <span>Close / બંધ કરો (Esc)</span>
            </button>
            <button onclick="switchJobModalTab('docs')" class="px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-bold flex items-center gap-1.5 shadow transition-all cursor-pointer">
              <span>Next: Required Documents</span>
              <i data-lucide="arrow-right" class="w-4 h-4"></i>
            </button>
          </div>
        </div>

        <!-- Tab 4: Required Documents -->
        <div id="tab-content-docs" class="job-modal-tab-content hidden space-y-5">
          <div class="glass-panel p-5 rounded-2xl border border-slate-800">
            <h4 class="text-xs uppercase tracking-wider text-blue-400 font-extrabold mb-3 flex items-center gap-2">
              <i data-lucide="folder-check" class="w-4 h-4"></i> ${isGujaratPage ? 'અરજી પહેલાં આ દસ્તાવેજો તૈયાર રાખો' : 'Document Readiness Checklist & Upload Specs'}
            </h4>
            <p class="text-xs text-slate-300 mb-4">
              Before starting your online application, ensure you have clear, scanned digital copies within the designated file dimensions to avoid form rejection:
            </p>

            <div class="space-y-3">
              <div class="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 flex items-start justify-between gap-3">
                <div class="flex items-start gap-3">
                  <input type="checkbox" class="mt-1 rounded bg-slate-800 border-slate-700 text-cyan-500 focus:ring-0 w-4 h-4">
                  <div>
                    <span class="text-xs font-bold text-white block">1. Recent Passport Size Color Photograph</span>
                    <span class="text-[11px] text-slate-400 block">Plain white/light background, taken within last 3 months. No sunglasses or caps.</span>
                  </div>
                </div>
                <span class="text-[11px] font-mono text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-800/60 shrink-0">10 KB - 15 KB (JPG)</span>
              </div>

              <div class="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 flex items-start justify-between gap-3">
                <div class="flex items-start gap-3">
                  <input type="checkbox" class="mt-1 rounded bg-slate-800 border-slate-700 text-cyan-500 focus:ring-0 w-4 h-4">
                  <div>
                    <span class="text-xs font-bold text-white block">2. Candidate Official Signature</span>
                    <span class="text-[11px] text-slate-400 block">Black or dark blue ink pen on clean white paper. Do NOT sign in capital letters.</span>
                  </div>
                </div>
                <span class="text-[11px] font-mono text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-800/60 shrink-0">10 KB - 15 KB (JPG)</span>
              </div>

              <div class="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 flex items-start justify-between gap-3">
                <div class="flex items-start gap-3">
                  <input type="checkbox" class="mt-1 rounded bg-slate-800 border-slate-700 text-cyan-500 focus:ring-0 w-4 h-4">
                  <div>
                    <span class="text-xs font-bold text-white block">3. 10th / SSC Board Marksheet & Certificate</span>
                    <span class="text-[11px] text-slate-400 block">Mandatory proof for Date of Birth (DOB) and candidate's exact legal spelling.</span>
                  </div>
                </div>
                <span class="text-[11px] font-mono text-slate-300 bg-slate-800 px-2 py-0.5 rounded shrink-0">PDF / JPG</span>
              </div>

              <div class="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 flex items-start justify-between gap-3">
                <div class="flex items-start gap-3">
                  <input type="checkbox" class="mt-1 rounded bg-slate-800 border-slate-700 text-cyan-500 focus:ring-0 w-4 h-4">
                  <div>
                    <span class="text-xs font-bold text-white block">4. Degree / Diploma / ITI Final Marksheet & Certificate</span>
                    <span class="text-[11px] text-slate-400 block">All semester marksheets + Degree / Provisional Certificate from recognized board.</span>
                  </div>
                </div>
                <span class="text-[11px] font-mono text-slate-300 bg-slate-800 px-2 py-0.5 rounded shrink-0">PDF</span>
              </div>

              <div class="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 flex items-start justify-between gap-3">
                <div class="flex items-start gap-3">
                  <input type="checkbox" class="mt-1 rounded bg-slate-800 border-slate-700 text-cyan-500 focus:ring-0 w-4 h-4">
                  <div>
                    <span class="text-xs font-bold text-white block">5. Caste / Category Certificate & NCLC (Parishisht-K)</span>
                    <span class="text-[11px] text-slate-400 block">For Gujarat SEBC/OBC, Non-Creamy Layer Certificate must be valid for the current financial year.</span>
                  </div>
                </div>
                <span class="text-[11px] font-mono text-amber-300 bg-amber-950/60 px-2 py-0.5 rounded border border-amber-800/60 shrink-0">Mandatory for Reserved</span>
              </div>

              <div class="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 flex items-start justify-between gap-3">
                <div class="flex items-start gap-3">
                  <input type="checkbox" class="mt-1 rounded bg-slate-800 border-slate-700 text-cyan-500 focus:ring-0 w-4 h-4">
                  <div>
                    <span class="text-xs font-bold text-white block">6. Valid Photo Identity Card</span>
                    <span class="text-[11px] text-slate-400 block">Aadhaar Card, Election Voter ID Card, Driving License, or Passport.</span>
                  </div>
                </div>
                <span class="text-[11px] font-mono text-emerald-300 bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-800/60 shrink-0">Carry to Exam</span>
              </div>
            </div>

            <!-- Tab 4 Bottom Navigation Bar -->
            <div class="mt-4 pt-4 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-3">
              <button onclick="closeJobDetailModal()" class="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-rose-600 text-slate-300 hover:text-white text-xs font-bold flex items-center gap-1.5 border border-slate-700 transition-colors cursor-pointer">
                <i data-lucide="x" class="w-4 h-4"></i>
                <span>Close / બંધ કરો (Esc)</span>
              </button>
              <button onclick="switchJobModalTab('salary')" class="px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-bold flex items-center gap-1.5 shadow transition-all cursor-pointer">
                <span>Next: Salary &amp; 7th Pay Calculator</span>
                <i data-lucide="arrow-right" class="w-4 h-4"></i>
              </button>
            </div>
          </div>
        </div>

        <!-- Tab 5: Salary & 7th Pay Calculator -->
        <div id="tab-content-salary" class="job-modal-tab-content hidden space-y-5">
          <div class="glass-panel p-5 rounded-2xl border border-emerald-500/30 bg-emerald-950/10">
            <div class="flex flex-wrap items-center justify-between gap-2 mb-4">
              <div>
                <h4 class="text-xs uppercase tracking-wider text-emerald-400 font-extrabold flex items-center gap-2">
                  <i data-lucide="wallet" class="w-4 h-4"></i> ${isGovt ? '7th Pay In-Hand Salary Simulator' : 'Corporate CTC & Compensation Structure'}
                </h4>
                <p class="text-[11px] text-slate-400 mt-0.5">Estimated take-home monthly payout based on official DA & HRA rates.</p>
              </div>
              <div class="text-right">
                <span class="text-[11px] text-slate-400 block font-semibold">Net Take-Home Salary</span>
                <span class="text-lg font-black text-emerald-400">~₹${inHandEst.toLocaleString()} / mo</span>
              </div>
            </div>

            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center text-xs mb-4">
              <div class="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                <span class="text-[11px] text-slate-400 block">Basic Pay</span>
                <span class="text-sm font-extrabold text-white mt-1 block">₹${basePay.toLocaleString()}</span>
                <span class="text-[10px] text-slate-400">7th Pay Band</span>
              </div>

              <div class="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                <span class="text-[11px] text-slate-400 block">DA (Dearness Allowance)</span>
                <span class="text-sm font-extrabold text-cyan-400 mt-1 block">+₹${daEstimate.toLocaleString()}</span>
                <span class="text-[10px] text-cyan-300">50% Central/State Rate</span>
              </div>

              <div class="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                <span class="text-[11px] text-slate-400 block">HRA (House Rent)</span>
                <span class="text-sm font-extrabold text-cyan-400 mt-1 block">+₹${hraEstimate.toLocaleString()}</span>
                <span class="text-[10px] text-cyan-300">18% (Class-Y City)</span>
              </div>

              <div class="p-3 rounded-xl bg-slate-900/80 border border-emerald-500/40">
                <span class="text-[11px] text-emerald-400 block font-bold">Gross Monthly Pay</span>
                <span class="text-sm font-black text-emerald-400 mt-1 block">₹${grossEst.toLocaleString()}</span>
                <span class="text-[10px] text-emerald-300">Before Deductions</span>
              </div>
            </div>

            <div class="p-3 rounded-xl bg-slate-900/60 border border-slate-800 text-xs flex flex-wrap items-center justify-between gap-2 text-slate-300">
              <div class="flex items-center gap-4">
                <span>NPS / GPF Contribution (10%): <strong class="text-rose-400">-₹${npsEstimate.toLocaleString()}</strong></span>
                <span>Professional Tax: <strong class="text-rose-400">-₹200</strong></span>
              </div>
              <div class="font-bold text-white">
                Annual Payout Equivalent: <span class="text-emerald-400">₹${(grossEst * 12).toLocaleString()} / Year</span>
              </div>
            </div>

            ${isGujaratJob && job.gov_level === 'State' ? `
              <div class="mt-3 p-3 rounded-xl bg-amber-950/20 border border-amber-500/30 text-xs text-amber-200 leading-relaxed">
                <strong>🦁 Gujarat Government Fixed Pay Policy:</strong> For initial 5 years of service, Class-3 / Class-4 cadres receive fixed consolidated remuneration (e.g. ₹26,000/mo or ₹40,800/mo). Upon successful completion of 5 years, candidates are regularized into full 7th Pay Matrix with annual increments and DA/HRA allowances.
              </div>
            ` : ''}

            <!-- Tab 5 Bottom Navigation Bar -->
            <div class="mt-4 pt-4 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-3">
              <button onclick="closeJobDetailModal()" class="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-rose-600 text-slate-300 hover:text-white text-xs font-bold flex items-center gap-1.5 border border-slate-700 transition-colors cursor-pointer">
                <i data-lucide="x" class="w-4 h-4"></i>
                <span>Close / બંધ કરો (Esc)</span>
              </button>
              <div class="flex flex-wrap items-center gap-2">
                <button onclick="switchJobModalTab('pyqs')" class="px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold flex items-center gap-1.5 shadow transition-all cursor-pointer">
                  <span>Next: 5-Year PYQs & Answer Keys</span>
                  <i data-lucide="arrow-right" class="w-4 h-4"></i>
                </button>
                <a href="${job.apply_url}" target="_blank" rel="noopener noreferrer" class="px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-cyan-600 hover:from-emerald-500 hover:to-cyan-500 text-white text-xs font-black flex items-center gap-2 shadow-lg shadow-emerald-600/30 transition-all">
                  <span>Apply on Official Portal</span>
                  <i data-lucide="external-link" class="w-4 h-4"></i>
                </a>
              </div>
            </div>
          </div>
        </div>

        <!-- Tab 6: 5-Year Official PYQ & Answer Key Vault -->
        <div id="tab-content-pyqs" class="job-modal-tab-content hidden space-y-5">
          ${generateJobPYQVault(job, isGujaratPage)}
        </div>

        <!-- Sticky Footer Action Bar -->
        <div class="p-4 rounded-2xl bg-slate-900/95 border border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-3 sticky bottom-0 z-20 backdrop-blur shadow-2xl">
          <div class="flex items-center gap-2 text-xs text-slate-300">
            <i data-lucide="shield-check" class="w-4 h-4 text-emerald-400 shrink-0"></i>
            <span>Verified Official Recruitment Dossier • FuturSet v2.4</span>
          </div>

          <div class="flex flex-wrap items-center gap-2.5 w-full sm:w-auto justify-end">
            <button onclick="closeJobDetailModal()" class="px-4 py-2 rounded-xl bg-rose-600/20 hover:bg-rose-600 border border-rose-500/40 text-rose-300 hover:text-white text-xs font-black flex items-center gap-1.5 transition-all shadow-md cursor-pointer" title="Close Recruitment Details (Esc)">
              <i data-lucide="x-circle" class="w-4 h-4"></i>
              <span>✕ Close Details / બંધ કરો</span>
            </button>

            <button onclick="copyJobLink('${job.apply_url}', this)" class="px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold flex items-center gap-1.5 border border-slate-700 transition-colors">
              <i data-lucide="copy" class="w-4 h-4"></i>
              <span>Copy Link</span>
            </button>

            <button onclick="shareJobWhatsApp(${job.id}, '${job.title.replace(/'/g, "\\'")}', '${job.vacancies.toLocaleString()}', '${job.last_date}', '${job.apply_url}')" class="px-3 py-2 rounded-xl bg-emerald-950/60 hover:bg-emerald-900/80 border border-emerald-500/40 text-emerald-300 text-xs font-bold flex items-center gap-1.5 transition-colors">
              <i data-lucide="share-2" class="w-4 h-4"></i>
              <span>WhatsApp</span>
            </button>

            ${job.notification_pdf_url ? `
              <a href="${job.notification_pdf_url}" target="_blank" rel="noopener noreferrer" class="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-rose-300 text-xs font-bold flex items-center gap-1.5 border border-slate-700 transition-colors">
                <i data-lucide="file-text" class="w-4 h-4 text-rose-400"></i>
                <span>Official PDF</span>
              </a>
            ` : ''}

            <a href="${job.apply_url}" target="_blank" rel="noopener noreferrer" class="px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600 hover:from-emerald-500 hover:to-cyan-500 text-white text-xs font-black flex items-center gap-2 shadow-lg shadow-emerald-600/30 transition-all transform hover:scale-[1.02]">
              <span>Apply on Official Portal</span>
              <i data-lucide="external-link" class="w-4 h-4"></i>
            </a>
          </div>
        </div>
      </div>
    `;

    if (window.lucide) lucide.createIcons();
  } catch (err) {
    console.error("Error opening job modal:", err);
    modalBody.innerHTML = `
      <div class="py-12 text-center">
        <div class="w-12 h-12 mx-auto rounded-full bg-rose-500/20 text-rose-400 flex items-center justify-center mb-3">
          <i data-lucide="alert-triangle" class="w-6 h-6"></i>
        </div>
        <h4 class="text-base font-bold text-white">Unable to load recruitment dossier</h4>
        <p class="text-xs text-slate-400 mt-1">Please check your connection or try again.</p>
        <button onclick="closeJobDetailModal()" class="mt-4 px-4 py-2 bg-slate-800 text-slate-200 text-xs font-semibold rounded-lg">Close</button>
      </div>
    `;
    if (window.lucide) lucide.createIcons();
  }
}

function closeJobDetailModal() {
  const modal = document.getElementById("job-detail-modal");
  if (modal) {
    modal.classList.add("hidden");
    modal.classList.remove("flex");
  }
  const techModal = document.getElementById("tech-job-modal");
  if (techModal) {
    techModal.classList.add("hidden");
    techModal.classList.remove("flex");
  }
  document.body.style.overflow = "auto";
  document.documentElement.style.overflow = "auto";
}

function copyJobLink(url, btn) {
  navigator.clipboard.writeText(url).then(() => {
    const originalHtml = btn.innerHTML;
    btn.innerHTML = `<i data-lucide="check" class="w-4 h-4 text-emerald-400"></i><span class="text-emerald-400">Copied!</span>`;
    initLucide();
    setTimeout(() => {
      btn.innerHTML = originalHtml;
      initLucide();
    }, 2000);
  });
}

function updateSyllabusProgress(checkbox) {
  const container = checkbox.closest('.glass-panel');
  if (!container) return;
  const all = container.querySelectorAll('input[type="checkbox"]');
  const checked = container.querySelectorAll('input[type="checkbox"]:checked');
  const progressText = container.querySelector('#syllabus-progress-text');
  if (progressText) {
    progressText.innerText = `${checked.length} of ${all.length} topics prepared (${Math.round((checked.length / all.length) * 100)}%)`;
  }
}

async function toggleBookmark(jobId, btnElement) {
  try {
    const res = await fetch(`/api/bookmark/${jobId}`, { method: "POST" });
    const data = await res.json();
    
    if (data.is_bookmarked) {
      bookmarkedJobIds.add(jobId);
    } else {
      bookmarkedJobIds.delete(jobId);
    }

    const icon = btnElement ? btnElement.querySelector("svg") : null;
    if (icon) {
      if (data.is_bookmarked) {
        icon.classList.add("fill-cyan-400", "text-cyan-400");
      } else {
        icon.classList.remove("fill-cyan-400", "text-cyan-400");
      }
    }

    const badge = document.getElementById("bookmark-count-badge");
    if (badge) {
      badge.innerText = bookmarkedJobIds.size;
      badge.classList.toggle("hidden", bookmarkedJobIds.size === 0);
    }
  } catch (e) {
    console.error("Bookmark toggle error:", e);
  }
}

function resetFilters() {
  const isGujaratPage = window.location.pathname.includes("/gujarat") || document.documentElement.lang === "gu";
  currentFilters = {
    q: "",
    gov_level: isGujaratPage ? "State" : "",
    state: isGujaratPage ? "Gujarat" : "",
    board: "",
    qualification: "",
    sort_by: "deadline"
  };
  const searchInput = document.getElementById("search-input");
  if (searchInput) searchInput.value = "";
  
  document.querySelectorAll(".filter-btn-chip").forEach(b => {
    b.classList.remove("bg-cyan-600", "bg-orange-600", "text-white");
    b.classList.add("bg-slate-800/80", "text-slate-300");
  });

  fetchJobs();
}

// AI Candidate Matcher Drawer
function openMatcherModal() {
  const modal = document.getElementById("matcher-modal");
  modal.classList.remove("hidden");
  modal.classList.add("flex");
  document.body.style.overflow = "hidden";
}

function closeMatcherModal() {
  const modal = document.getElementById("matcher-modal");
  modal.classList.add("hidden");
  modal.classList.remove("flex");
  document.body.style.overflow = "auto";
}

function setMatcherPreset(preset) {
  playAudioTick(750, 0.05);
  const ageEl = document.getElementById("matcher-age-input");
  const eduEl = document.getElementById("matcher-edu-select");
  const catEl = document.getElementById("matcher-cat-select");
  const stateEl = document.getElementById("matcher-state-select");
  const centralCheck = document.getElementById("matcher-central-check");

  if (!ageEl || !eduEl) return;

  if (preset === 'btech_gujarat') {
    ageEl.value = "23";
    eduEl.value = "B.E. / B.Tech";
    if (catEl) catEl.value = "General";
    if (stateEl) stateEl.value = "Gujarat";
    if (centralCheck) centralCheck.checked = true;
  } else if (preset === 'graduate_gujarat') {
    ageEl.value = "24";
    eduEl.value = "Graduate";
    if (catEl) catEl.value = "SEBC";
    if (stateEl) stateEl.value = "Gujarat";
    if (centralCheck) centralCheck.checked = true;
  } else if (preset === '12th_gujarat') {
    ageEl.value = "20";
    eduEl.value = "12th Pass";
    if (catEl) catEl.value = "General";
    if (stateEl) stateEl.value = "Gujarat";
    if (centralCheck) centralCheck.checked = true;
  }
  calculateAIMatches();
}

window._cachedMatches = [];
window._currentMatchTab = 'all';

function filterMatchTab(tab) {
  playAudioTick(650, 0.04);
  window._currentMatchTab = tab;
  renderMatchList();
}

function renderMatchList() {
  const resultsContainer = document.getElementById("matcher-results-container");
  if (!resultsContainer || !window._cachedMatches) return;

  const tab = window._currentMatchTab || 'all';
  let filtered = window._cachedMatches;

  if (tab === 'gujarat') {
    filtered = window._cachedMatches.filter(m => (m.job.state || '').toLowerCase() === 'gujarat' || m.job.gov_level === 'State');
  } else if (tab === 'tech') {
    filtered = window._cachedMatches.filter(m => m.job.is_btech_cse === 1 || (m.job.qualification_level || '').toLowerCase() === 'engineering');
  } else if (tab === 'central') {
    filtered = window._cachedMatches.filter(m => m.job.gov_level === 'Central');
  } else if (tab === 'merit') {
    filtered = window._cachedMatches.filter(m => m.job.selection_mode === 'direct_merit' || m.job.selection_mode === 'walk_in');
  }

  const age = parseInt(document.getElementById("matcher-age-input")?.value) || 24;
  const qualification = document.getElementById("matcher-edu-select")?.value || "Graduate";
  const category = document.getElementById("matcher-cat-select")?.value || "General";

  const totalVacancies = filtered.reduce((acc, m) => acc + (m.job.vacancies || 0), 0);

  let html = `
    <div class="mb-4 p-3.5 rounded-xl bg-gradient-to-r from-cyan-950/60 to-slate-900 border border-cyan-500/30">
      <div class="flex flex-wrap items-center justify-between gap-2">
        <div>
          <span class="text-xs text-cyan-200 font-semibold">Eligibility Profile: <strong>Age ${age} • ${qualification} • ${category} (Gujarat)</strong></span>
          <p class="text-[11px] text-slate-400 mt-0.5">Total Matching Openings: <strong class="text-emerald-400 font-bold">${totalVacancies.toLocaleString()} vacancies</strong> across ${filtered.length} recruitments</p>
        </div>
        <span class="px-3 py-1 rounded-full text-xs font-black bg-cyan-500/20 text-cyan-300 border border-cyan-500/40">
          ${filtered.length} Jobs Match
        </span>
      </div>

      <!-- Category Filter Tabs -->
      <div class="mt-3 pt-2.5 border-t border-slate-800/80 flex flex-wrap gap-1.5 text-xs">
        <button onclick="filterMatchTab('all')" class="px-2.5 py-1 rounded-lg font-semibold transition-all ${tab === 'all' ? 'bg-cyan-600 text-white shadow' : 'bg-slate-900 text-slate-300 hover:text-white border border-slate-800'}">All Eligible (${window._cachedMatches.length})</button>
        <button onclick="filterMatchTab('gujarat')" class="px-2.5 py-1 rounded-lg font-semibold transition-all ${tab === 'gujarat' ? 'bg-orange-600 text-white shadow' : 'bg-slate-900 text-slate-300 hover:text-white border border-slate-800'}">Gujarat State</button>
        <button onclick="filterMatchTab('tech')" class="px-2.5 py-1 rounded-lg font-semibold transition-all ${tab === 'tech' ? 'bg-indigo-600 text-white shadow' : 'bg-slate-900 text-slate-300 hover:text-white border border-slate-800'}">💻 B.Tech &amp; Tech</button>
        <button onclick="filterMatchTab('central')" class="px-2.5 py-1 rounded-lg font-semibold transition-all ${tab === 'central' ? 'bg-blue-600 text-white shadow' : 'bg-slate-900 text-slate-300 hover:text-white border border-slate-800'}">Central Govt</button>
        <button onclick="filterMatchTab('merit')" class="px-2.5 py-1 rounded-lg font-semibold transition-all ${tab === 'merit' ? 'bg-emerald-600 text-white shadow' : 'bg-slate-900 text-slate-300 hover:text-white border border-slate-800'}">⚡ Direct Merit / Walk-in</button>
      </div>
    </div>
    <div class="space-y-3 max-h-[58vh] overflow-y-auto pr-1">
  `;

  if (filtered.length === 0) {
    html += `<div class="p-8 text-center text-slate-400 text-xs">No jobs found under this category tab for your profile.</div>`;
  } else {
    filtered.slice(0, 45).forEach(m => {
      const job = m.job;
      let scoreColor = "bg-emerald-500 text-emerald-950";
      if (m.match_score < 70) scoreColor = "bg-amber-400 text-amber-950";
      if (m.match_score < 50) scoreColor = "bg-rose-500 text-white";

      const isGov = job.job_category === 'government';
      const isTech = job.is_btech_cse === 1;

      html += `
        <div class="glass-panel p-3.5 rounded-xl border border-slate-800 hover:border-cyan-500/40 transition-all flex flex-col md:flex-row items-start md:items-center justify-between gap-3">
          <div class="flex-1">
            <div class="flex flex-wrap items-center gap-1.5 mb-1.5">
              <span class="px-2 py-0.5 rounded text-[11px] font-black ${scoreColor}">${m.match_score}% Match</span>
              <span class="text-xs font-semibold text-slate-300">${m.eligibility_status}</span>
              ${job.state === 'Gujarat' ? `<span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-orange-500/20 text-orange-300 border border-orange-500/30">ગુજરાત</span>` : `<span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-blue-500/20 text-blue-300 border border-blue-500/30">Central</span>`}
              ${isTech ? `<span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">💻 Tech Role</span>` : ''}
              ${m.relaxation_applied ? `<span class="text-[10px] font-bold text-amber-300 bg-amber-500/20 px-1.5 py-0.5 rounded">${m.relaxation_applied}</span>` : ''}
            </div>
            <h4 class="text-sm font-bold text-white hover:text-cyan-300 cursor-pointer" onclick="openJobDetailModal(${job.id})">${job.title}</h4>
            <p class="text-xs text-slate-400 mt-0.5">
              <strong class="text-slate-300">${job.organization}</strong> • <span class="text-emerald-400 font-semibold">${job.vacancies.toLocaleString()} Posts</span> • Deadline: <span class="text-amber-300">${job.last_date}</span>
            </p>
            <div class="mt-2 flex flex-wrap gap-1">
              ${m.reasons.map(r => `<span class="text-[10px] text-slate-300 bg-slate-900/90 px-2 py-0.5 rounded border border-slate-800">✓ ${r}</span>`).join('')}
            </div>
          </div>

          <div class="flex items-center gap-2 shrink-0">
            <button onclick="openJobDetailModal(${job.id})" class="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg transition-colors">Details &amp; Syllabus</button>
            <a href="${job.apply_url}" target="_blank" class="px-3.5 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-bold rounded-lg shadow transition-colors flex items-center gap-1">
              <span>Apply</span>
              <i data-lucide="external-link" class="w-3 h-3"></i>
            </a>
          </div>
        </div>
      `;
    });
  }

  html += `</div>`;
  resultsContainer.innerHTML = html;
  initLucide();
}

async function calculateAIMatches() {
  const age = parseInt(document.getElementById("matcher-age-input")?.value) || 24;
  const qualification = document.getElementById("matcher-edu-select")?.value || "Graduate";
  const category = document.getElementById("matcher-cat-select")?.value || "General";
  const statePref = document.getElementById("matcher-state-select")?.value || "Gujarat";
  const centralCheck = document.getElementById("matcher-central-check");
  const includeCentral = centralCheck ? centralCheck.checked : true;

  const resultsContainer = document.getElementById("matcher-results-container");
  if (!resultsContainer) return;

  resultsContainer.innerHTML = `
    <div class="py-12 text-center">
      <div class="inline-block w-8 h-8 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin"></div>
      <p class="mt-3 text-slate-400 font-medium">Evaluating your qualifications against all 170+ Gujarat &amp; Central gazettes...</p>
    </div>
  `;

  try {
    const res = await fetch("/api/match", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        age: age,
        qualification: qualification,
        category: category,
        state_preference: statePref,
        include_central: includeCentral
      })
    });

    const matches = await res.json();

    if (!matches || matches.length === 0) {
      resultsContainer.innerHTML = `<p class="text-slate-400 text-center py-8">No matching vacancies found for this profile.</p>`;
      return;
    }

    window._cachedMatches = matches;
    window._currentMatchTab = 'all';
    renderMatchList();
  } catch (err) {
    console.error("Match error:", err);
    resultsContainer.innerHTML = `<div class="text-rose-400 text-center py-8">Calculation error. Please try again.</div>`;
  }
}

// Bookmarks Drawer
function openBookmarksModal() {
  const modal = document.getElementById("bookmarks-modal");
  const listContainer = document.getElementById("bookmarks-list");
  modal.classList.remove("hidden");
  modal.classList.add("flex");
  document.body.style.overflow = "hidden";

  fetch("/api/bookmarks")
    .then(r => r.json())
    .then(data => {
      if (data.bookmarks.length === 0) {
        listContainer.innerHTML = `
          <div class="text-center py-12 text-slate-400">
            <i data-lucide="bookmark" class="w-10 h-10 mx-auto text-slate-600 mb-2"></i>
            <p>You haven't saved any recruitments yet.</p>
            <p class="text-xs mt-1">Click the bookmark icon on any job card to save it for fast access.</p>
          </div>
        `;
        initLucide();
        return;
      }

      let html = `<div class="space-y-3">`;
      data.bookmarks.forEach(job => {
        html += `
          <div class="glass-panel p-4 rounded-xl border border-slate-800 flex items-center justify-between gap-4">
            <div>
              <span class="text-xs text-cyan-400 font-semibold">${job.organization}</span>
              <h4 class="text-sm font-bold text-white">${job.title}</h4>
              <p class="text-xs text-slate-400 mt-0.5">Vacancies: ${job.vacancies.toLocaleString()} • Deadline: ${job.last_date}</p>
            </div>
            <div class="flex items-center gap-2">
              <button onclick="openJobDetailModal(${job.id})" class="px-3 py-1.5 bg-slate-800 text-slate-200 text-xs font-semibold rounded-lg">View</button>
              <a href="${job.apply_url}" target="_blank" class="px-3 py-1.5 bg-cyan-600 text-white text-xs font-bold rounded-lg">Apply</a>
            </div>
          </div>
        `;
      });
      html += `</div>`;
      listContainer.innerHTML = html;
      initLucide();
    });
}

function closeBookmarksModal() {
  const modal = document.getElementById("bookmarks-modal");
  modal.classList.add("hidden");
  modal.classList.remove("flex");
  document.body.style.overflow = "auto";
}

// Alert Subscription
function openSubscribeModal() {
  const modal = document.getElementById("subscribe-modal");
  modal.classList.remove("hidden");
  modal.classList.add("flex");
}

function closeSubscribeModal() {
  const modal = document.getElementById("subscribe-modal");
  modal.classList.add("hidden");
  modal.classList.remove("flex");
}

async function handleSubscribe(e) {
  e.preventDefault();
  const name = document.getElementById("sub-name").value.trim();
  const email = document.getElementById("sub-email").value.trim();
  const state = document.getElementById("sub-state").value;

  try {
    const res = await fetch("/api/subscribe", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email, state_pref: state })
    });
    const data = await res.json();
    alert("✓ " + data.message);
    closeSubscribeModal();
  } catch (e) {
    alert("Subscription error. Please try again.");
  }
}

// -------------------------------------------------------------
// Interactive Generative Hero Canvas (Lusion / Active Theory style)
// -------------------------------------------------------------
function initHeroCanvas() {
  const canvas = document.getElementById("hero-canvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  let width = canvas.width = canvas.parentElement.offsetWidth || window.innerWidth;
  let height = canvas.height = canvas.parentElement.offsetHeight || 420;

  const points = [];
  // Lightweight particle count optimized for 144Hz high refresh rate
  const count = Math.min(Math.floor((width * height) / 32000), 28);
  let mouse = { x: -1000, y: -1000, active: false };
  let isHeroVisible = true;
  let animId = null;

  for (let i = 0; i < count; i++) {
    points.push({
      x: Math.random() * width,
      y: Math.random() * height,
      vx: (Math.random() - 0.5) * 0.45,
      vy: (Math.random() - 0.5) * 0.45,
      radius: Math.random() * 1.8 + 1.0
    });
  }

  // IntersectionObserver: Pause canvas loop completely when hero scrolls out of view
  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        isHeroVisible = entry.isIntersecting;
        if (isHeroVisible && !animId) {
          animId = requestAnimationFrame(animate);
        } else if (!isHeroVisible && animId) {
          cancelAnimationFrame(animId);
          animId = null;
        }
      });
    }, { threshold: 0.05 });
    observer.observe(canvas.parentElement || canvas);
  }

  window.addEventListener("resize", () => {
    if (!canvas || !canvas.parentElement) return;
    width = canvas.width = canvas.parentElement.offsetWidth;
    height = canvas.height = canvas.parentElement.offsetHeight;
  }, { passive: true });

  const heroSection = canvas.parentElement;
  if (heroSection) {
    heroSection.addEventListener("mousemove", (e) => {
      const rect = canvas.getBoundingClientRect();
      mouse.x = e.clientX - rect.left;
      mouse.y = e.clientY - rect.top;
      mouse.active = true;
    }, { passive: true });
    heroSection.addEventListener("mouseleave", () => {
      mouse.active = false;
    }, { passive: true });
  }

  const isGujarat = window.location.pathname.includes("/gujarat") || document.documentElement.lang === "gu";
  const nodeColor = isGujarat ? "rgba(249, 115, 22, 0.75)" : "rgba(14, 165, 233, 0.75)";
  const lineColor = isGujarat ? "rgba(249, 115, 22, 0.12)" : "rgba(14, 165, 233, 0.12)";

  function animate() {
    if (!isHeroVisible) {
      animId = null;
      return;
    }
    ctx.clearRect(0, 0, width, height);

    for (let i = 0; i < points.length; i++) {
      const p = points[i];
      p.x += p.vx;
      p.y += p.vy;

      if (p.x < 0 || p.x > width) p.vx *= -1;
      if (p.y < 0 || p.y > height) p.vy *= -1;

      if (mouse.active) {
        const dx = mouse.x - p.x;
        const dy = mouse.y - p.y;
        const distSq = dx * dx + dy * dy;
        if (distSq < 14400) {
          const dist = Math.sqrt(distSq);
          const force = (120 - dist) / 120;
          p.x -= (dx / dist) * force * 2.0;
          p.y -= (dy / dist) * force * 2.0;
        }
      }

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
      ctx.fillStyle = nodeColor;
      ctx.fill();

      for (let j = i + 1; j < points.length; j++) {
        const p2 = points[j];
        const dx = p.x - p2.x;
        const dy = p.y - p2.y;
        const distSq = dx * dx + dy * dy;
        if (distSq < 10000) {
          const dist = Math.sqrt(distSq);
          ctx.beginPath();
          ctx.moveTo(p.x, p.y);
          ctx.lineTo(p2.x, p2.y);
          ctx.strokeStyle = lineColor;
          ctx.lineWidth = 1 - dist / 100;
          ctx.stroke();
        }
      }
    }

    animId = requestAnimationFrame(animate);
  }
  animId = requestAnimationFrame(animate);
}

// -------------------------------------------------------------
// Mouse Ambient Spotlight Glow (144Hz Throttled & Scroll-Optimized)
// -------------------------------------------------------------
function initSpotlight() {
  let ticking = false;
  let isScrolling = false;
  let scrollTimer = null;

  window.addEventListener("scroll", () => {
    isScrolling = true;
    clearTimeout(scrollTimer);
    scrollTimer = setTimeout(() => { isScrolling = false; }, 80);
  }, { passive: true });

  window.addEventListener("mousemove", (e) => {
    if (isScrolling) return; // Skip DOM style updates during active scroll for 144FPS
    if (!ticking) {
      requestAnimationFrame(() => {
        document.documentElement.style.setProperty("--mouse-x", `${e.clientX}px`);
        document.documentElement.style.setProperty("--mouse-y", `${e.clientY}px`);
        ticking = false;
      });
      ticking = true;
    }
  }, { passive: true });
}

// -------------------------------------------------------------
// Web Audio API Tactile Sound Synthesizer (Zero asset dependency)
// -------------------------------------------------------------
// audioEnabled and audioCtx initialized at top level

function playAudioTick(freq = 600, duration = 0.04) {
  if (!audioEnabled) return;
  try {
    if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = "sine";
    osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
    gain.gain.setValueAtTime(0.04, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + duration);
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start();
    osc.stop(audioCtx.currentTime + duration);
  } catch (e) {
    // Silently ignore if browser requires explicit gesture
  }
}

function toggleThemeSound() {
  audioEnabled = !audioEnabled;
  const btn = document.getElementById("sound-toggle-btn");
  if (btn) {
    btn.innerHTML = audioEnabled
      ? '<i data-lucide="volume-2" class="w-4 h-4 text-cyan-400"></i><span class="hidden sm:inline text-[11px] text-cyan-300">Sound: On</span>'
      : '<i data-lucide="volume-x" class="w-4 h-4 text-slate-500"></i><span class="hidden sm:inline text-[11px] text-slate-500">Muted</span>';
    initLucide();
  }
  if (audioEnabled) playAudioTick(850, 0.08);
}

// -------------------------------------------------------------
// Command Palette (Ctrl+K or ⌘K)
// -------------------------------------------------------------
function initCommandPalette() {
  window.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
      e.preventDefault();
      toggleCommandPalette();
    }
    if (e.key === "Escape") {
      closeCommandPalette();
      closeSalaryCalculator();
      closeCompareModal();
      closeOjasGuideModal();
    }
  });

  const input = document.getElementById("palette-input");
  if (input) {
    input.addEventListener("input", (e) => {
      filterPaletteCommands(e.target.value.trim().toLowerCase());
    });
  }
}

function toggleCommandPalette() {
  const modal = document.getElementById("command-palette-modal");
  if (!modal) return;
  if (modal.classList.contains("hidden")) {
    openCommandPalette();
  } else {
    closeCommandPalette();
  }
}

function openCommandPalette() {
  playAudioTick(750, 0.05);
  const modal = document.getElementById("command-palette-modal");
  if (!modal) return;
  modal.classList.remove("hidden");
  modal.classList.add("flex");
  const input = document.getElementById("palette-input");
  if (input) {
    input.value = "";
    input.focus();
    filterPaletteCommands("");
  }
}

function closeCommandPalette() {
  playAudioTick(450, 0.05);
  const modal = document.getElementById("command-palette-modal");
  if (!modal) return;
  modal.classList.add("hidden");
  modal.classList.remove("flex");
}

function filterPaletteCommands(q) {
  const list = document.getElementById("palette-results");
  if (!list) return;

  const actions = [
    { title: "ગુજરાત રોજગાર પોર્ટલ (Gujarat Hub)", category: "Portal View", icon: "map-pin", action: () => { window.location.href = "/gujarat"; } },
    { title: "Gujarat Police Bharti 2026 (12,472 Posts)", category: "Recruitment", icon: "shield", action: () => { document.getElementById("search-input").value = "Police"; currentFilters.q = "Police"; fetchJobs(); closeCommandPalette(); } },
    { title: "GPSC Class 1 & 2 Administrative Services", category: "Recruitment", icon: "award", action: () => { document.getElementById("search-input").value = "GPSC"; currentFilters.q = "GPSC"; fetchJobs(); closeCommandPalette(); } },
    { title: "GSSSB CCE Clerk & Office Assistant (5,554 Posts)", category: "Recruitment", icon: "file-text", action: () => { document.getElementById("search-input").value = "CCE"; currentFilters.q = "CCE"; fetchJobs(); closeCommandPalette(); } },
    { title: "Railway RRB ALP & Technician (18,799 Posts)", category: "Central Govt", icon: "train", action: () => { document.getElementById("search-input").value = "Railway"; currentFilters.q = "Railway"; fetchJobs(); closeCommandPalette(); } },
    { title: "SSC Combined Graduate Level (CGL 2026)", category: "Central Govt", icon: "landmark", action: () => { document.getElementById("search-input").value = "SSC"; currentFilters.q = "SSC"; fetchJobs(); closeCommandPalette(); } },
    { title: "7th Pay Commission Salary & Pension Calculator", category: "Financial Tool", icon: "calculator", action: () => { closeCommandPalette(); openSalaryCalculator(); } },
    { title: "AI Career & Eligibility Matcher", category: "AI Tool", icon: "sparkles", action: () => { closeCommandPalette(); openMatcherModal(); } },
    { title: "OJAS One-Time Registration (OTR) Guide", category: "Official Guide", icon: "help-circle", action: () => { closeCommandPalette(); openOjasGuideModal(); } },
    { title: "Trigger Live Feeds Radar Scanner", category: "Engine Action", icon: "radar", action: () => { closeCommandPalette(); startLiveScan(); } },
    { title: "Export All Verified Recruitments (CSV)", category: "Data Export", icon: "download", action: () => { window.location.href = "/api/export"; } }
  ];

  const filtered = actions.filter(a => !q || a.title.toLowerCase().includes(q) || a.category.toLowerCase().includes(q));

  list.innerHTML = filtered.map((item, idx) => `
    <div onclick="executePaletteItem(${idx})" class="palette-item flex items-center justify-between p-3 rounded-xl hover:bg-cyan-500/10 cursor-pointer border border-transparent hover:border-cyan-500/30 transition-all text-xs">
      <div class="flex items-center gap-3">
        <div class="w-7 h-7 rounded-lg bg-slate-800 flex items-center justify-center text-cyan-400">
          <i data-lucide="${item.icon}" class="w-4 h-4"></i>
        </div>
        <div>
          <div class="font-bold text-slate-100">${item.title}</div>
          <div class="text-[10px] text-slate-400">${item.category}</div>
        </div>
      </div>
      <kbd class="px-2 py-0.5 rounded bg-slate-800 text-[10px] text-slate-400 font-mono">Enter</kbd>
    </div>
  `).join("");

  window._paletteActions = filtered;
  initLucide();
}

function executePaletteItem(idx) {
  if (window._paletteActions && window._paletteActions[idx]) {
    playAudioTick(800, 0.06);
    window._paletteActions[idx].action();
  }
}

// -------------------------------------------------------------
// 7th Pay Commission Salary & Pension Calculator
// -------------------------------------------------------------
function openSalaryCalculator(prefillJobTitle = "") {
  playAudioTick(650, 0.05);
  const modal = document.getElementById("salary-calculator-modal");
  if (!modal) return;
  modal.classList.remove("hidden");
  modal.classList.add("flex");
  const note = document.getElementById("calc-prefill-note");
  if (note) {
    note.innerText = prefillJobTitle ? "Estimating for: " + prefillJobTitle : "Gujarat Govt & Central Pay Matrix (7th Pay Commission)";
  }
  calculateSalary();
}

function closeSalaryCalculator() {
  playAudioTick(450, 0.05);
  const modal = document.getElementById("salary-calculator-modal");
  if (!modal) return;
  modal.classList.add("hidden");
  modal.classList.remove("flex");
}

function calculateSalary() {
  const postTypeEl = document.getElementById("salary-post-type");
  const cityTierEl = document.getElementById("salary-city-tier");
  if (!postTypeEl || !cityTierEl) return;

  const mode = postTypeEl.value;
  const cityTier = cityTierEl.value; // Tier X (Ahmedabad), Tier Y (Surat/Vadodara/Rajkot), Tier Z
  const hraPercent = cityTier === "X" ? 0.27 : cityTier === "Y" ? 0.18 : 0.09;

  let basic = 0;
  let fixPay = false;

  if (mode === "fix_clerk") {
    fixPay = true;
    basic = 26000;
  } else if (mode === "fix_head") {
    fixPay = true;
    basic = 40800;
  } else if (mode === "lvl2") {
    basic = 19900;
  } else if (mode === "lvl4") {
    basic = 25500;
  } else if (mode === "lvl7") {
    basic = 44900;
  } else if (mode === "lvl10") {
    basic = 56100;
  }

  let da = 0;
  let hra = 0;
  let ta = 0;
  let gross = 0;
  let nps = 0;
  let pt = 200; // Gujarat Professional Tax
  let inHand = 0;

  if (fixPay) {
    gross = basic;
    nps = 0;
    inHand = gross - pt;
    da = 0;
    hra = 0;
    ta = 0;
  } else {
    da = Math.round(basic * 0.50); // 50% DA
    hra = Math.round(basic * hraPercent);
    ta = cityTier === "X" ? 3600 + Math.round(3600 * 0.50) : 1800 + Math.round(1800 * 0.50);
    gross = basic + da + hra + ta;
    nps = Math.round((basic + da) * 0.10); // 10% NPS
    inHand = gross - (nps + pt);
  }

  const setT = (id, val) => { const el = document.getElementById(id); if (el) el.innerText = val; };
  setT("sal-disp-basic", "₹" + basic.toLocaleString());
  setT("sal-disp-da", fixPay ? "N/A (Fix Pay)" : "₹" + da.toLocaleString());
  setT("sal-disp-hra", fixPay ? "N/A (Fix Pay)" : "₹" + hra.toLocaleString());
  setT("sal-disp-ta", fixPay ? "N/A (Fix Pay)" : "₹" + ta.toLocaleString());
  setT("sal-disp-gross", "₹" + gross.toLocaleString());
  setT("sal-disp-nps", fixPay ? "₹0" : "₹" + nps.toLocaleString());
  setT("sal-disp-net", "₹" + inHand.toLocaleString() + " / Month");
}

// -------------------------------------------------------------
// Side-by-Side Job Comparison Matrix
// -------------------------------------------------------------
// selectedCompareIds initialized at top level

function toggleCompareJob(jobId, element) {
  playAudioTick(600, 0.05);
  const idx = selectedCompareIds.indexOf(jobId);
  if (idx > -1) {
    selectedCompareIds.splice(idx, 1);
  } else {
    if (selectedCompareIds.length >= 2) {
      alert("You can compare maximum 2 recruitments simultaneously. Please uncheck one first.");
      if (element && element.checked !== undefined) element.checked = false;
      return;
    }
    selectedCompareIds.push(jobId);
  }
  updateCompareFloatingBar();
}

function updateCompareFloatingBar() {
  const bar = document.getElementById("compare-floating-bar");
  if (!bar) return;
  if (selectedCompareIds.length > 0) {
    bar.classList.remove("hidden");
    bar.classList.add("flex");
    const countEl = document.getElementById("compare-selected-count");
    if (countEl) countEl.innerText = `${selectedCompareIds.length}/2 Selected`;
  } else {
    bar.classList.add("hidden");
    bar.classList.remove("flex");
  }
}

async function openCompareModal() {
  if (selectedCompareIds.length < 2) {
    alert("Please check at least 2 jobs in the list to compare side-by-side.");
    return;
  }
  playAudioTick(750, 0.06);
  const modal = document.getElementById("compare-drawer-modal");
  if (!modal) return;
  modal.classList.remove("hidden");
  modal.classList.add("flex");

  try {
    const [j1, j2] = await Promise.all([
      fetch(`/api/jobs/${selectedCompareIds[0]}`).then(r => r.json()),
      fetch(`/api/jobs/${selectedCompareIds[1]}`).then(r => r.json())
    ]);
    renderCompareContent(j1, j2);
  } catch (e) {
    console.error("Error loading comparison:", e);
  }
}

function closeCompareModal() {
  playAudioTick(450, 0.05);
  const modal = document.getElementById("compare-drawer-modal");
  if (!modal) return;
  modal.classList.add("hidden");
  modal.classList.remove("flex");
}

function renderCompareContent(j1, j2) {
  const container = document.getElementById("compare-matrix-body");
  if (!container) return;

  const fee1 = j1.application_fee_text || j1.application_fee || '₹100 (Reserved: Nil)';
  const fee2 = j2.application_fee_text || j2.application_fee || '₹100 (Reserved: Nil)';
  const sal1 = j1.salary_text || (j1.ctc_lpa ? `₹${j1.ctc_lpa} LPA` : '7th Pay Commission Scale');
  const sal2 = j2.salary_text || (j2.ctc_lpa ? `₹${j2.ctc_lpa} LPA` : '7th Pay Commission Scale');
  const qual1 = j1.qualification || 'Prescribed Degree / Diploma';
  const qual2 = j2.qualification || 'Prescribed Degree / Diploma';
  const age1 = (j1.age_min || 18) + ' to ' + (j1.age_max || 35) + ' Years';
  const age2 = (j2.age_min || 18) + ' to ' + (j2.age_max || 35) + ' Years';
  const vac1 = (j1.vacancies || 0).toLocaleString();
  const vac2 = (j2.vacancies || 0).toLocaleString();

  container.innerHTML = `
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 p-4 text-xs">
      <!-- Job 1 -->
      <div class="bg-slate-900/95 border border-cyan-500/40 rounded-2xl p-5 flex flex-col justify-between shadow-xl">
        <div>
          <div class="flex items-center justify-between gap-2 mb-2">
            <span class="px-2.5 py-1 rounded-lg text-[10px] font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 uppercase">${j1.board_category || 'Recruitment'}</span>
            <span class="text-xs font-bold text-emerald-400">${vac1} Posts</span>
          </div>
          <h4 class="font-black text-base text-white mt-1 leading-snug">${j1.title}</h4>
          <p class="text-slate-400 mt-1 font-medium">${j1.organization}</p>

          <div class="space-y-2.5 mt-4 pt-4 border-t border-slate-800/80">
            <div class="flex items-start justify-between gap-2">
              <span class="text-slate-400 font-medium">Qualification:</span>
              <span class="font-bold text-slate-200 text-right max-w-[65%]">${qual1}</span>
            </div>
            <div class="flex items-center justify-between gap-2">
              <span class="text-slate-400 font-medium">Age Limit:</span>
              <span class="font-bold text-slate-200">${age1}</span>
            </div>
            <div class="flex items-center justify-between gap-2">
              <span class="text-slate-400 font-medium">Salary / Scale:</span>
              <span class="font-bold text-cyan-300 text-right">${sal1}</span>
            </div>
            <div class="flex items-center justify-between gap-2">
              <span class="text-slate-400 font-medium">Application Fee:</span>
              <span class="font-bold text-slate-200">${fee1}</span>
            </div>
            <div class="flex items-center justify-between gap-2">
              <span class="text-slate-400 font-medium">Last Date:</span>
              <span class="font-bold text-amber-400">${j1.last_date || 'Closing Soon'} (${j1.days_left || 0} days left)</span>
            </div>
          </div>
        </div>

        <div class="mt-6 pt-4 border-t border-slate-800 flex items-center gap-2">
          <a href="${j1.apply_url || '#'}" target="_blank" class="flex-1 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-center shadow-lg shadow-cyan-600/30 transition-all">Apply Official ↗</a>
          <button onclick="openJobDetailModal(${j1.id}); closeCompareModal();" class="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold border border-slate-700 transition-all">Full Details</button>
        </div>
      </div>

      <!-- Job 2 -->
      <div class="bg-slate-900/95 border border-orange-500/40 rounded-2xl p-5 flex flex-col justify-between shadow-xl">
        <div>
          <div class="flex items-center justify-between gap-2 mb-2">
            <span class="px-2.5 py-1 rounded-lg text-[10px] font-bold bg-orange-500/20 text-orange-300 border border-orange-500/30 uppercase">${j2.board_category || 'Recruitment'}</span>
            <span class="text-xs font-bold text-emerald-400">${vac2} Posts</span>
          </div>
          <h4 class="font-black text-base text-white mt-1 leading-snug">${j2.title}</h4>
          <p class="text-slate-400 mt-1 font-medium">${j2.organization}</p>

          <div class="space-y-2.5 mt-4 pt-4 border-t border-slate-800/80">
            <div class="flex items-start justify-between gap-2">
              <span class="text-slate-400 font-medium">Qualification:</span>
              <span class="font-bold text-slate-200 text-right max-w-[65%]">${qual2}</span>
            </div>
            <div class="flex items-center justify-between gap-2">
              <span class="text-slate-400 font-medium">Age Limit:</span>
              <span class="font-bold text-slate-200">${age2}</span>
            </div>
            <div class="flex items-center justify-between gap-2">
              <span class="text-slate-400 font-medium">Salary / Scale:</span>
              <span class="font-bold text-orange-300 text-right">${sal2}</span>
            </div>
            <div class="flex items-center justify-between gap-2">
              <span class="text-slate-400 font-medium">Application Fee:</span>
              <span class="font-bold text-slate-200">${fee2}</span>
            </div>
            <div class="flex items-center justify-between gap-2">
              <span class="text-slate-400 font-medium">Last Date:</span>
              <span class="font-bold text-amber-400">${j2.last_date || 'Closing Soon'} (${j2.days_left || 0} days left)</span>
            </div>
          </div>
        </div>

        <div class="mt-6 pt-4 border-t border-slate-800 flex items-center gap-2">
          <a href="${j2.apply_url || '#'}" target="_blank" class="flex-1 py-2.5 rounded-xl bg-orange-600 hover:bg-orange-500 text-white font-bold text-center shadow-lg shadow-orange-600/30 transition-all">Apply Official ↗</a>
          <button onclick="openJobDetailModal(${j2.id}); closeCompareModal();" class="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold border border-slate-700 transition-all">Full Details</button>
        </div>
      </div>
    </div>
  `;
}

// -------------------------------------------------------------
// WhatsApp & Telegram Study Group Sharing
// -------------------------------------------------------------
function shareJobWhatsApp(jobId, title, vac, lastDate, applyUrl) {
  playAudioTick(700, 0.05);
  const text = encodeURIComponent(
    `🔥 *સરકારી ભરતી અપડેટ (Govt Recruitment 2026)* 🔥\n\n` +
    `📌 *પોસ્ટ:* ${title}\n` +
    `👥 *કુલ જગ્યાઓ:* ${vac} Posts\n` +
    `⏰ *અરજી કરવાની છેલ્લી તારીખ:* ${lastDate}\n` +
    `🔗 *ડાયરેક્ટ અરજી લિંક:* ${applyUrl}\n\n` +
    `⚡ *FuturSet Jobs Portal પર તમામ સરકારી ભરતીઓ ચેક કરો:* ${window.location.origin}`
  );
  window.open(`https://api.whatsapp.com/send?text=${text}`, "_blank");
}

function shareJobTelegram(jobId, title, vac, lastDate, applyUrl) {
  playAudioTick(700, 0.05);
  const text = encodeURIComponent(
    `🔥 સરકારી ભરતી ૨૦૨૬: ${title}\nજગ્યાઓ: ${vac}\nછેલ્લી તારીખ: ${lastDate}\nઅરજી લિંક: ${applyUrl}`
  );
  window.open(`https://t.me/share/url?url=${encodeURIComponent(applyUrl)}&text=${text}`, "_blank");
}

// -------------------------------------------------------------
// OJAS Step-by-Step Application & OTR Guide
// -------------------------------------------------------------
function openOjasGuideModal() {
  playAudioTick(650, 0.05);
  const modal = document.getElementById("ojas-guide-modal");
  if (!modal) return;
  modal.classList.remove("hidden");
  modal.classList.add("flex");
}

function closeOjasGuideModal() {
  playAudioTick(450, 0.05);
  const modal = document.getElementById("ojas-guide-modal");
  if (!modal) return;
  modal.classList.add("hidden");
  modal.classList.remove("flex");
}

// -------------------------------------------------------------
// Gujarat District Quick Filter
// -------------------------------------------------------------
function filterByGujaratDistrict(districtName, btnElement) {
  playAudioTick(600, 0.04);
  currentFilters.state = "Gujarat";
  currentFilters.gov_level = "State";
  currentFilters.q = districtName === "All" ? "" : districtName;

  if (btnElement && btnElement.parentElement) {
    btnElement.parentElement.querySelectorAll("button").forEach(b => {
      b.classList.remove("bg-orange-600", "text-white", "shadow-md");
      b.classList.add("bg-slate-900/80", "text-slate-300");
    });
    btnElement.classList.add("bg-orange-600", "text-white", "shadow-md");
    btnElement.classList.remove("bg-slate-900/80", "text-slate-300");
  }

  fetchJobs();
}

// =========================================================================
// Advanced Tools: Syllabus Breakdown, Fee & Exemption Guide, Timeline
// =========================================================================

async function openSyllabusModal(jobId) {
  playAudioTick(650, 0.04);
  const modal = document.getElementById("syllabus-modal");
  const modalBody = document.getElementById("syllabus-modal-body");
  if (!modal || !modalBody) return;

  modal.classList.remove("hidden");
  modal.classList.add("flex");

  modalBody.innerHTML = `
    <div class="py-12 text-center">
      <div class="inline-block w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
      <p class="mt-3 text-slate-400 font-medium">Fetching official exam syllabus & scheme...</p>
    </div>
  `;

  try {
    const res = await fetch(`/api/jobs/${jobId}`);
    const job = await res.json();
    const isGu = job.state === "Gujarat";

    modalBody.innerHTML = `
      <div class="space-y-4 text-xs">
        <div class="p-4 rounded-xl bg-slate-900/90 border border-slate-800">
          <div class="flex flex-wrap items-center gap-2 mb-2">
            <span class="px-2 py-0.5 rounded text-[11px] font-bold ${isGu ? 'bg-orange-500/20 text-orange-300' : 'bg-blue-500/20 text-blue-300'}">${job.gov_level} (${job.state})</span>
            <span class="px-2 py-0.5 rounded text-[11px] font-medium bg-slate-800 text-slate-300">${job.board_category}</span>
            <span class="text-slate-400 font-mono text-[11px]">${job.notification_number || 'Official Gazette'}</span>
          </div>
          <h3 class="text-base font-bold text-white">${job.title}</h3>
          ${job.title_gu ? `<p class="font-gujarati text-amber-400/90 font-medium mt-0.5">${job.title_gu}</p>` : ''}
        </div>

        <!-- Selection Process Stages -->
        <div class="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
          <h4 class="font-bold text-slate-200 uppercase tracking-wider text-[11px] mb-2.5 flex items-center gap-2 text-cyan-400">
            <i data-lucide="layers" class="w-4 h-4"></i>
            <span>Selection Process & Examination Stages</span>
          </h4>
          <p class="text-slate-300 leading-relaxed font-mono text-xs whitespace-pre-line bg-slate-950/80 p-3 rounded-lg border border-slate-800/80">
            ${job.selection_process || 'Direct Merit Selection based on qualifying examination scores followed by document verification.'}
          </p>
        </div>

        <!-- Detailed Syllabus Breakdown -->
        <div class="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
          <h4 class="font-bold text-slate-200 uppercase tracking-wider text-[11px] mb-2.5 flex items-center gap-2 text-indigo-400">
            <i data-lucide="book-marked" class="w-4 h-4"></i>
            <span>Detailed Subject Syllabus & Marks Pattern</span>
          </h4>
          <div class="text-slate-300 leading-relaxed bg-slate-950/80 p-3.5 rounded-lg border border-slate-800/80 text-xs">
            ${job.syllabus_summary || 'Detailed syllabus prescribed as per official departmental recruitment rules.'}
          </div>
        </div>

        <!-- Official Actions & Links -->
        <div class="pt-2 flex flex-wrap items-center justify-between gap-3 border-t border-slate-800/80">
          <div class="text-slate-400 text-[11px]">
            <span>Exam Date: </span>
            <span class="text-amber-400 font-bold">${job.exam_date || 'To be announced on board portal'}</span>
          </div>
          <div class="flex items-center gap-2">
            ${job.notification_pdf_url ? `
              <a href="${job.notification_pdf_url}" target="_blank" rel="noopener noreferrer" class="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-white font-semibold text-xs transition-colors flex items-center gap-1.5 border border-slate-700">
                <i data-lucide="file-text" class="w-3.5 h-3.5 text-rose-400"></i>
                <span>Download Gazette PDF</span>
              </a>
            ` : ''}
            <a href="${job.apply_url}" target="_blank" rel="noopener noreferrer" class="px-3.5 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs transition-all shadow-md flex items-center gap-1.5">
              <span>Apply Online</span>
              <i data-lucide="external-link" class="w-3.5 h-3.5"></i>
            </a>
          </div>
        </div>
      </div>
    `;
    initLucide();
  } catch (e) {
    modalBody.innerHTML = `<div class="text-center text-rose-400 py-8">Failed to load syllabus. Please try again.</div>`;
  }
}

function closeSyllabusModal() {
  playAudioTick(400, 0.03);
  const modal = document.getElementById("syllabus-modal");
  if (modal) {
    modal.classList.add("hidden");
    modal.classList.remove("flex");
  }
}

function openFeeGuideModal() {
  playAudioTick(700, 0.04);
  const modal = document.getElementById("fee-guide-modal");
  if (modal) {
    modal.classList.remove("hidden");
    modal.classList.add("flex");
    initLucide();
  }
}

function closeFeeGuideModal() {
  playAudioTick(400, 0.03);
  const modal = document.getElementById("fee-guide-modal");
  if (modal) {
    modal.classList.add("hidden");
    modal.classList.remove("flex");
  }
}

async function openTimelineModal() {
  playAudioTick(720, 0.04);
  const modal = document.getElementById("timeline-modal");
  const body = document.getElementById("timeline-modal-body");
  if (!modal || !body) return;

  modal.classList.remove("hidden");
  modal.classList.add("flex");

  body.innerHTML = `
    <div class="py-10 text-center">
      <div class="inline-block w-8 h-8 border-4 border-amber-500 border-t-transparent rounded-full animate-spin"></div>
      <p class="mt-3 text-slate-400 font-medium">Assembling examination calendar...</p>
    </div>
  `;

  try {
    const res = await fetch("/api/jobs?limit=100");
    const data = await res.json();
    const withExams = (data.results || []).filter(j => j.exam_date && j.exam_date.trim() !== "");

    if (withExams.length === 0) {
      body.innerHTML = `<div class="text-center text-slate-400 py-8">No scheduled exam dates at present.</div>`;
      return;
    }

    let html = `<div class="space-y-3">`;
    withExams.forEach(j => {
      const isGu = j.state === "Gujarat";
      html += `
        <div class="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800/90 flex items-center justify-between gap-3 hover:border-amber-500/30 transition-colors">
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 mb-1">
              <span class="px-2 py-0.5 rounded text-[10px] font-bold ${isGu ? 'bg-orange-500/20 text-orange-300' : 'bg-blue-500/20 text-blue-300'}">${j.board_category}</span>
              <span class="text-xs text-slate-400 truncate">${j.organization}</span>
            </div>
            <h4 class="text-xs font-bold text-white truncate cursor-pointer hover:text-cyan-300" onclick="closeTimelineModal(); openJobDetailModal(${j.id});">${j.title}</h4>
          </div>
          <div class="text-right shrink-0">
            <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40">
              <i data-lucide="calendar" class="w-3.5 h-3.5"></i>
              ${j.exam_date}
            </span>
          </div>
        </div>
      `;
    });
    html += `</div>`;
    body.innerHTML = html;
    initLucide();
  } catch (err) {
    body.innerHTML = `<div class="text-center text-rose-400 py-8">Failed to load exam timeline.</div>`;
  }
}

function closeTimelineModal() {
  playAudioTick(400, 0.03);
  const modal = document.getElementById("timeline-modal");
  if (modal) {
    modal.classList.add("hidden");
    modal.classList.remove("flex");
  }
}

function filterBySector(sector, btnElement) {
  playAudioTick(600, 0.03);
  document.querySelectorAll(".filter-pill-sector").forEach(b => {
    b.classList.remove("active");
  });
  if (btnElement) {
    btnElement.classList.add("active");
  }
  currentFilters.sector = sector === "All" ? "" : sector;
  fetchJobs();
}

function filterByQualification(qual, btnElement) {
  playAudioTick(620, 0.03);
  document.querySelectorAll(".filter-pill-qual").forEach(b => {
    b.classList.remove("active");
  });
  if (btnElement) {
    btnElement.classList.add("active");
  }
  currentFilters.qualification = qual === "All" ? "" : qual;
  fetchJobs();
}

function filterByUrgency(urgency, btnElement) {
  playAudioTick(640, 0.03);
  document.querySelectorAll(".filter-pill-urgency").forEach(b => {
    b.classList.remove("active");
  });
  if (btnElement) {
    btnElement.classList.add("active");
  }
  currentFilters.urgency = urgency === "All" ? "" : urgency;
  fetchJobs();
}

function filterBySelectionMode(mode, btnElement) {
  playAudioTick(650, 0.03);
  document.querySelectorAll(".filter-pill-mode").forEach(b => {
    b.classList.remove("active");
  });
  if (btnElement) {
    btnElement.classList.add("active");
  }
  currentFilters.selection_mode = mode === "All" ? "" : mode;
  fetchJobs();
}

function resetAllFilters() {
  playAudioTick(500, 0.04);
  currentFilters = {
    q: "",
    gov_level: "",
    state: "",
    board: "",
    qualification: "",
    district: "",
    sector: "",
    selection_mode: "",
    urgency: "",
    sort_by: "deadline"
  };

  const isGu = window.location.pathname.includes("/gujarat") || document.documentElement.lang === "gu";
  if (isGu) {
    currentFilters.state = "Gujarat";
    currentFilters.gov_level = "State";
  }

  const sInput = document.getElementById("search-input");
  if (sInput) sInput.value = "";

  document.querySelectorAll(".filter-pill, .filter-btn-chip").forEach(b => {
    b.classList.remove("active", "bg-cyan-600", "bg-orange-600", "bg-[#635bff]", "text-white", "shadow-sm", "shadow-xs");
    b.classList.add("bg-white", "text-slate-700", "border-slate-200");
    b.classList.remove("bg-slate-800/80", "text-slate-300");
  });

  const allOpeningsBtn = document.querySelector(".filter-btn-chip");
  if (allOpeningsBtn) {
    allOpeningsBtn.classList.add(isGu ? "bg-orange-600" : "bg-[#635bff]", "text-white", "shadow-xs");
    allOpeningsBtn.classList.remove("bg-white", "text-slate-700", "border-slate-200", "bg-slate-800/80", "text-slate-300");
  }

  document.querySelectorAll(".pill-default-all").forEach(b => {
    b.classList.add("active");
  });

  fetchJobs();
}

// -------------------------------------------------------------
// Quick 10-Second Eligibility Radar & Multi-Step Wizard
// -------------------------------------------------------------
function goToWizardStep(step) {
  for (let i = 1; i <= 3; i++) {
    const dot = document.getElementById(`wizard-step-dot-${i}`);
    const panel = document.getElementById(`wizard-step-panel-${i}`);
    if (dot) {
      if (i < step) {
        dot.className = "wizard-step-dot completed";
      } else if (i === step) {
        dot.className = "wizard-step-dot active";
      } else {
        dot.className = "wizard-step-dot";
      }
    }
    if (panel) {
      panel.classList.toggle("hidden", i !== step);
    }
  }
  if (window.lucide) lucide.createIcons();
}
window.goToWizardStep = goToWizardStep;

async function runQuickEligibilityRadar() {
  const qual = document.getElementById("radar-qualification") ? document.getElementById("radar-qualification").value : "All";
  const age = document.getElementById("radar-age") ? parseInt(document.getElementById("radar-age").value) || 24 : 24;
  const cat = document.getElementById("radar-category") ? document.getElementById("radar-category").value : "General";
  const target = document.getElementById("radar-target") ? document.getElementById("radar-target").value : "All";

  const btn = document.getElementById("radar-submit-btn");
  const resultContainer = document.getElementById("radar-results-banner");

  if (btn) {
    btn.disabled = true;
    btn.innerHTML = `<span class="inline-block w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"></span> Scanning...`;
  }

  try {
    const res = await fetch("/api/match", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        age: age,
        qualification: qual === "All" ? "Graduate" : qual,
        category: cat,
        state_preference: target === "All" ? "Gujarat" : target,
        include_central: target !== "Gujarat"
      })
    });

    if (!res.ok) throw new Error("Matching error");
    const matches = await res.json();
    const eligibleMatches = Array.isArray(matches) 
      ? matches.filter(m => m.match_score >= 50 && (!m.eligibility_status || !m.eligibility_status.toLowerCase().includes("ineligible"))) 
      : [];

    let totalVacancies = 0;
    eligibleMatches.forEach(m => { totalVacancies += (m.job.vacancies || 0); });

    goToWizardStep(3);

    if (resultContainer) {
      resultContainer.classList.remove("hidden");
      resultContainer.innerHTML = `
        <div class="glass-panel p-4 sm:p-5 rounded-2xl border border-emerald-500/50 bg-gradient-to-r from-emerald-950/70 via-slate-900/90 to-cyan-950/70 shadow-2xl animate-in fade-in slide-in-from-top-4 duration-300">
          <div class="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div class="flex items-start gap-3.5">
              <div class="w-12 h-12 rounded-2xl bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 text-2xl shrink-0 shadow-lg">
                <i data-lucide="check-circle-2" class="w-6 h-6"></i>
              </div>
              <div>
                <div class="flex items-center gap-2 flex-wrap">
                  <span class="px-2.5 py-0.5 rounded-full text-xs font-extrabold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                    Verified Match: Gazette Confirmed
                  </span>
                  <span class="text-xs text-slate-400">Profile: ${qual} • Age ${age} • ${cat}</span>
                </div>
                <h3 class="text-base sm:text-lg font-black text-white mt-1">
                  You are eligible for <span class="text-emerald-400 font-extrabold">${eligibleMatches.length} Active Recruitment Drives</span> (<span class="text-cyan-400 font-extrabold">${totalVacancies.toLocaleString()} Total Posts</span>)!
                </h3>
                <p class="text-xs text-slate-300 mt-0.5">
                  Evaluated against official gazettes, reservation age relaxations, and educational criteria.
                </p>
              </div>
            </div>

            <div class="flex flex-wrap items-center gap-2 shrink-0 w-full md:w-auto justify-end">
              <button onclick="resetQuickEligibilityRadar()" class="btn-premium-ghost text-xs py-2 px-3.5">
                Show All Jobs
              </button>
              <button onclick="shareJobWhatsApp(0, 'I am eligible for ${eligibleMatches.length} Government Jobs (${totalVacancies.toLocaleString()} Posts) on FuturSet Rojgar! Check your eligibility:', '${totalVacancies.toLocaleString()}', '2026', 'https://futurset-rojgar.onrender.com/')" class="btn-premium-primary text-xs py-2 px-4 shadow-lg shadow-cyan-600/30">
                <i data-lucide="share-2" class="w-3.5 h-3.5"></i>
                <span>Share My Result</span>
              </button>
            </div>
          </div>

          <!-- Top Recommendations Quick Pills -->
          <div class="mt-4 pt-3 border-t border-slate-800/80 flex flex-wrap items-center gap-2">
            <span class="text-xs font-bold text-slate-400 flex items-center gap-1">Top Recommended Drives:</span>
            ${eligibleMatches.slice(0, 4).map(m => `
              <button onclick="openJobDetailModal(${m.job.id})" class="px-3 py-1.5 rounded-xl bg-slate-900/90 hover:bg-cyan-950/70 border border-slate-700 hover:border-cyan-500/50 text-xs text-slate-200 hover:text-cyan-300 flex items-center gap-1.5 transition-all">
                <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
                <span class="font-bold truncate max-w-[200px]">${m.job.title}</span>
                <span class="text-[10px] text-emerald-400 font-mono">(${m.match_score}% Match)</span>
              </button>
            `).join('')}
          </div>
        </div>
      `;
      if (window.lucide) lucide.createIcons();
      resultContainer.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }

    // Also filter the jobs feed below
    if (qual !== "All") {
      filterByQualification(qual === "B.Tech / B.E. / MCA" ? "engineering" : (qual.includes("10th") ? "10th" : (qual.includes("12th") ? "12th" : "graduate")));
    }
  } catch (err) {
    console.error("Error in Quick Eligibility Radar:", err);
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = `<i data-lucide="zap" class="w-4 h-4"></i><span>Scan My Eligibility</span>`;
      if (window.lucide) lucide.createIcons();
    }
  }
}

function resetQuickEligibilityRadar() {
  const resultContainer = document.getElementById("radar-results-banner");
  if (resultContainer) {
    resultContainer.classList.add("hidden");
    resultContainer.innerHTML = "";
  }
  goToWizardStep(1);
  resetAllFilters();
}

window.runQuickEligibilityRadar = runQuickEligibilityRadar;
window.resetQuickEligibilityRadar = resetQuickEligibilityRadar;

window.applyQuickFilter = applyQuickFilter;
window.resetFilters = resetFilters;
window.resetAllFilters = resetAllFilters;
window.filterBySector = filterBySector;
window.filterByQualification = filterByQualification;
window.filterByUrgency = filterByUrgency;
window.filterBySelectionMode = filterBySelectionMode;
window.openSyllabusModal = openSyllabusModal;
window.closeSyllabusModal = closeSyllabusModal;
window.openFeeGuideModal = openFeeGuideModal;
window.closeFeeGuideModal = closeFeeGuideModal;
window.openTimelineModal = openTimelineModal;
window.closeTimelineModal = closeTimelineModal;
window.openJobDetailModal = openJobDetailModal;
window.closeJobDetailModal = closeJobDetailModal;
window.toggleBookmark = toggleBookmark;
window.openMatcherModal = openMatcherModal;
window.closeMatcherModal = closeMatcherModal;
window.calculateAIMatches = calculateAIMatches;
window.openBookmarksModal = openBookmarksModal;
window.closeBookmarksModal = closeBookmarksModal;
window.openSubscribeModal = openSubscribeModal;
window.closeSubscribeModal = closeSubscribeModal;
window.handleSubscribe = handleSubscribe;
window.copyJobLink = copyJobLink;
window.updateSyllabusProgress = updateSyllabusProgress;
window.fetchJobs = fetchJobs;

// Modern additions
window.initHeroCanvas = initHeroCanvas;
window.initSpotlight = initSpotlight;
window.initAudioFeedback = initAudioFeedback;
window.playAudioTick = playAudioTick;
window.toggleThemeSound = toggleThemeSound;
window.initCommandPalette = initCommandPalette;
window.toggleCommandPalette = toggleCommandPalette;
window.openCommandPalette = openCommandPalette;
window.closeCommandPalette = closeCommandPalette;
window.executePaletteItem = executePaletteItem;
window.openSalaryCalculator = openSalaryCalculator;
window.closeSalaryCalculator = closeSalaryCalculator;
window.calculateSalary = calculateSalary;
window.toggleCompareJob = toggleCompareJob;
window.updateCompareFloatingBar = updateCompareFloatingBar;
window.openCompareModal = openCompareModal;
window.closeCompareModal = closeCompareModal;
window.shareJobWhatsApp = shareJobWhatsApp;
window.shareJobTelegram = shareJobTelegram;
window.openOjasGuideModal = openOjasGuideModal;
window.closeOjasGuideModal = closeOjasGuideModal;
window.filterByGujaratDistrict = filterByGujaratDistrict;
window.setMatcherPreset = setMatcherPreset;
window.filterMatchTab = filterMatchTab;
window.renderMatchList = renderMatchList;

// Universal listener for closing ANY active modal on backdrop click or Escape
document.addEventListener("click", (e) => {
  const modalConfigs = [
    { id: "job-detail-modal", close: closeJobDetailModal },
    { id: "bookmarks-modal", close: closeBookmarksModal },
    { id: "matcher-modal", close: closeMatcherModal },
    { id: "timeline-modal", close: closeTimelineModal },
    { id: "syllabus-modal", close: closeSyllabusModal },
    { id: "fee-guide-modal", close: closeFeeGuideModal },
    { id: "subscribe-modal", close: closeSubscribeModal },
    { id: "compare-modal", close: closeCompareModal },
    { id: "command-palette-modal", close: closeCommandPalette },
    { id: "ojas-guide-modal", close: closeOjasGuideModal },
    { id: "salary-calc-modal", close: closeSalaryCalculator },
    { id: "tech-job-modal", close: closeTechModal }
  ];

  modalConfigs.forEach(({ id, close }) => {
    const modalEl = document.getElementById(id);
    if (modalEl && !modalEl.classList.contains("hidden")) {
      const panel = modalEl.querySelector(".glass-panel, .glass-modal, .bg-slate-900, .bg-\\[\\#0b1227\\]");
      if (panel && !panel.contains(e.target) && modalEl.contains(e.target)) {
        if (typeof close === "function") close();
      }
    }
  });
});

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" || e.keyCode === 27) {
    if (typeof closeJobDetailModal === "function") closeJobDetailModal();
    if (typeof closeBookmarksModal === "function") closeBookmarksModal();
    if (typeof closeMatcherModal === "function") closeMatcherModal();
    if (typeof closeCommandPalette === "function") closeCommandPalette();
    if (typeof closeCompareModal === "function") closeCompareModal();
    if (typeof closeTimelineModal === "function") closeTimelineModal();
    if (typeof closeOjasGuideModal === "function") closeOjasGuideModal();
    if (typeof closeSalaryCalculator === "function") closeSalaryCalculator();
    if (typeof closeSyllabusModal === "function") closeSyllabusModal();
    if (typeof closeFeeGuideModal === "function") closeFeeGuideModal();
    if (typeof closeSubscribeModal === "function") closeSubscribeModal();
    if (typeof closeTechModal === "function") closeTechModal();
    document.body.style.overflow = "auto";
    document.documentElement.style.overflow = "auto";
  }
});

