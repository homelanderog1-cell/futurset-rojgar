---
title: FuturSet Rojgar
emoji: 🦁
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# FuturSet Rojgar Portal (ફ્યુચરસેટ રોજગાર પોર્ટલ)
### Next-Gen AI-Powered Government & State Job Intelligence Platform

FuturSet is a high-performance government and state recruitment intelligence portal. It automatically scans, aggregates, deduplicates, and presents all active public recruitment gazettes from OJAS Gujarat, GPSC, GSSSB, Police Bharti Board, High Court of Gujarat, SSC, UPSC, Railway (RRB), Banking, and Defence.

---

## 🌟 Key Features

1. **Dedicated Gujarat Government Jobs Webpage (`/gujarat`)**:
   - Bilingual support (English & Gujarati ગુજરાતી).
   - Direct integration for OJAS, GPSC, GSSSB, Police Bharti (LRD/PSI), Gujarat High Court, GSRTC, and Electricity DISCOMs (PGVCL/DGVCL/MGVCL/UGVCL).
   - Displays authentic 5-year fix pay scales, vacancy breakups, age relaxations (SEBC/SC/ST/Women), and direct application links.

2. **Real-Time Job Finding & Aggregator Engine**:
   - Live multi-source scraper with smart hash-based deduplication (`hash_key`).
   - Server-Sent Events (SSE) live telemetry stream (`/api/scan/stream`) updating the interactive radar widget and console in real-time.
   - Synchronous scan fallback & audit logging in SQLite.

3. **FuturSet AI Eligibility & Career Matcher**:
   - Computes candidate eligibility based on age, educational hierarchy, and quota relaxations (OBC/SEBC +3 yrs, SC/ST +5 yrs, Women +5 yrs, PwD +10 yrs).
   - Generates ranked match percentages, personalized preparation advice, and application checklists.

4. **World-Class Interactive UI Widgets**:
   - Responsive Glassmorphism dark theme with cyber neon accents.
   - Live marquee ticker for high-priority recruitment deadlines.
   - Real-time search with debouncing.
   - Filter by board, education, level, and salary.
   - Grid Cards vs Full Data Table switcher.
   - Detailed recruitment dossier modals.
   - One-click bookmarking system and CSV export.

---

## 🚀 Quick Start

### Launch Application
```bash
python run.py
```
Open your browser at:
- **Main Portal**: `http://127.0.0.1:8000`
- **Gujarat Govt Jobs Hub**: `http://127.0.0.1:8000/gujarat`
- **Interactive Swagger API Docs**: `http://127.0.0.1:8000/docs`

### Run Automated Tests
```bash
pytest tests/ -v
```
