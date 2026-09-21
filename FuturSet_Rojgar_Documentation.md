# FuturSet Rojgar: Comprehensive Enterprise Documentation

This document contains the complete lifecycle documentation for the FuturSet Rojgar Portal, ensuring enterprise-grade transparency, security, and architectural clarity.

---

## 1. Product Requirements Document (PRD)
**Product Vision:** FuturSet Rojgar is a next-generation, high-performance public service employment portal. It aggregates, tracks, and matches candidates with verified government (OJAS, GPSC, SSC, Railways) and corporate vacancies in real-time.

**Target Audience:** Job seekers across Gujarat and India, primarily aged 18-35, spanning 10th pass, 12th pass, graduates, and B.Tech/CSE engineering professionals.

**Core Features:**
- **Zero-Latency Hydration:** Instantaneous loading of 300+ jobs via SSR and client-side pre-seeding.
- **Unified Eligibility Engine:** A smart wizard to instantly match candidates to roles based on age, education, and reservation quota.
- **Sector-Specific Hubs:** Dedicated portals for Gujarat State (`/gujarat`), B.Tech CSE (`/btech-cse`), and Corporate (`/corporate`).
- **Live Telemetry Scanner:** Real-time data aggregation dashboard.

---

## 2. Security & Compliance Document
**Incident Report Context:** A recent audit (driven by external social media claims regarding AI-generated sites leaking APIs) confirmed that the FuturSet Rojgar frontend **Network Tab** only displays public REST API calls (e.g., `/api/jobs`) and standard static assets (e.g., `lucide.min.js`). **No secret API keys, database credentials, or sensitive environment variables were exposed.**

**Security Enhancements Implemented:**
- **Strict CORS Policy:** The API is now restricted to `https://futurset-rojgar.onrender.com`.
- **HTTP Security Headers:** Injected `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection: 1; mode=block`, and `Strict-Transport-Security: max-age=31536000; includeSubDomains`.
- **Database Lock Prevention:** SQLite timeout raised to `30.0` seconds to prevent threading contention during high-concurrency API floods.
- **Git Hooks & `.gitignore`:** Strict exclusion of `.env`, `venv`, and `*.sqlite3` to prevent credential leakage to GitHub.

---

## 3. System Requirements Specification (SRS)
**3.1 Functional Requirements:**
- The system must serve jobs via a RESTful API with pagination, filtering, and sorting.
- The system must support SSR (Server-Side Rendering) for SEO and initial load speed.
- The system must provide bookmarking functionality (stored in local storage or session state).

**3.2 Non-Functional Requirements:**
- **Performance:** Time-To-Interactive (TTI) must be under 1.5 seconds on 4G networks.
- **Scalability:** The API must handle up to 500 concurrent connections.
- **Security:** Must block Cross-Site Scripting (XSS) and Clickjacking.

---

## 4. Technical Design Document (TDD)
**Architecture:** Monolithic Client-Server model deployed on Render.
- **Backend:** Python 3.11+, FastAPI (ASGI framework for high concurrency).
- **Database:** SQLite3 (Local file-based for rapid reads).
- **Frontend:** HTML5, Tailwind CSS (utility-first styling), Vanilla JavaScript (ES6+).
- **Templating:** Jinja2 for Server-Side Rendering.

**Data Flow:**
1. Client requests page (`/gujarat`).
2. FastAPI queries SQLite for top 300 jobs.
3. Jinja2 renders `gujarat.html`, injecting data into `window.__INITIAL_JOBS__`.
4. Client JS reads `__INITIAL_JOBS__` and renders cards instantly (Zero-Flicker).

---

## 5. UI/UX Document
**Design Language:** "Dark Command Center" (Professional, high-contrast, data-dense).
- **Color Palette:** Slate (`#0f172a`), Indigo (`#635bff`), Orange (`#f97316`) for alerts, and Emerald (`#10b981`) for success states.
- **Typography:** System-ui fonts with bold sans-serif headers for readability.
- **Interaction Design:**
  - **Hover Lifts:** Job cards elevate `scale-105` on hover.
  - **Skeletons:** Shimmering placeholders only appear during deep network latency.
  - **Modals:** Universal blurred backdrops (`backdrop-blur-md`) with `Escape` key dismissal.

---

## 6. Developer Documentation
**Local Setup:**
```bash
# 1. Clone the repository
git clone https://github.com/homelanderog1-cell/futurset-rojgar.git
cd futurset-rojgar

# 2. Setup Virtual Environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install Dependencies
pip install -r requirements.txt

# 4. Run the Uvicorn Server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
**Deployment:** The application is auto-deployed to Render via GitHub Webhooks. Pushing to the `main` branch triggers an automated build and container restart.
