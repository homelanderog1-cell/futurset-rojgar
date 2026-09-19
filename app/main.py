"""
FuturSet Jobs Portal - FastAPI Application Entry Point
High-performance RESTful API and SSR Portal with SSE live scanner stream,
dedicated Gujarat recruitment hub, AI candidate matcher, and CSV export.
"""
import io
import csv
from datetime import datetime
from contextlib import asynccontextmanager
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Query, Path as FPath, Request, HTTPException, BackgroundTasks, Body
from fastapi.responses import HTMLResponse, StreamingResponse, Response, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import (
    PORTAL_TITLE, PORTAL_GUJARAT_TITLE, APP_VERSION,
    STATIC_DIR, TEMPLATES_DIR, BOARDS_GUJARAT, BOARDS_CENTRAL
)
from app.database import (
    init_db, get_jobs, get_job_by_id, toggle_bookmark,
    get_bookmarked_jobs, get_stats, get_recent_scans, add_subscriber,
    get_btech_cse_jobs, get_corporate_jobs, get_corporate_stats,
    get_pipeline_articles, get_pipeline_article_by_id, create_pipeline_article,
    transition_pipeline_article, publish_pipeline_article
)
from app.design_lab_data import PREVIEWS_DATA, CONCEPTS_DATA
from app.models import (
    JobResponse, MatchProfile, MatchResult, JobFilterParams,
    BookmarkToggleRequest, AlertSubscription, PortalStats
)
from app.matcher import match_candidate
from app.scanner_engine import execute_scan_stream, run_scan_sync

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="FuturSet Rojgar Portal API",
    description="Next-Gen AI-Powered Government & State Job Intelligence Platform",
    version=APP_VERSION,
    lifespan=lifespan
)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
templates.env.filters["format_vacancies"] = lambda val: f"{val:,}" if isinstance(val, (int, float)) else str(val)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, theme: str = Query("01")):
    stats = get_stats()
    initial_jobs = get_jobs({"limit": 50, "sort_by": "deadline"})
    gujarat_jobs = get_jobs({"state": "Gujarat", "limit": 6})
    pipeline_articles = get_pipeline_articles()
    
    # Clean theme ID (01 to 28)
    active_theme = theme if any(p["id"] == theme for p in PREVIEWS_DATA) else "01"
    
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "title": PORTAL_TITLE,
            "stats": stats,
            "initial_jobs": initial_jobs,
            "featured_jobs": initial_jobs[:8],
            "gujarat_jobs": gujarat_jobs,
            "pipeline_articles": pipeline_articles,
            "previews": PREVIEWS_DATA,
            "active_theme": active_theme,
            "boards_gujarat": BOARDS_GUJARAT,
            "boards_central": BOARDS_CENTRAL,
            "version": APP_VERSION
        }
    )

@app.get("/gujarat", response_class=HTMLResponse)
async def gujarat_portal(request: Request):
    stats = get_stats()
    gujarat_all_jobs = get_jobs({"state": "Gujarat", "limit": 100})
    return templates.TemplateResponse(
        request,
        "gujarat.html",
        {
            "title": PORTAL_GUJARAT_TITLE,
            "stats": stats,
            "jobs": gujarat_all_jobs,
            "boards_gujarat": BOARDS_GUJARAT,
            "version": APP_VERSION
        }
    )

@app.get("/btech-cse", response_class=HTMLResponse)
async def btech_cse_portal(request: Request):
    stats = get_stats()
    tech_jobs = get_btech_cse_jobs({"limit": 100})
    return templates.TemplateResponse(
        request,
        "btech_cse.html",
        {
            "title": "FuturSet B.Tech CSE & IT Engineering Jobs Hub 2026",
            "stats": stats,
            "jobs": tech_jobs,
            "version": APP_VERSION
        }
    )

@app.get("/corporate", response_class=HTMLResponse)
async def corporate_portal(request: Request):
    corp_stats = get_corporate_stats()
    stats = get_stats()
    return templates.TemplateResponse(
        request,
        "corporate.html",
        {
            "title": "FuturSet Enterprise & Corporate Careers 2026 - Adani, BHEL, Linde, Amazon, Flipkart, UPI & Startups",
            "corp_stats": corp_stats,
            "stats": stats,
            "version": APP_VERSION
        }
    )

@app.get("/api/jobs")
def api_get_jobs(
    q: Optional[str] = None,
    gov_level: Optional[str] = None,
    state: Optional[str] = None,
    board: Optional[str] = None,
    district: Optional[str] = None,
    sector: Optional[str] = None,
    urgency: Optional[str] = None,
    qualification: Optional[str] = None,
    selection_mode: Optional[str] = None,
    job_category: Optional[str] = None,
    is_btech_cse: Optional[int] = None,
    experience_level: Optional[str] = None,
    sort_by: Optional[str] = "deadline",
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0)
):
    params = {
        "q": q,
        "gov_level": gov_level,
        "state": state,
        "board": board,
        "district": district,
        "sector": sector,
        "urgency": urgency,
        "qualification": qualification,
        "selection_mode": selection_mode,
        "job_category": job_category,
        "is_btech_cse": is_btech_cse,
        "experience_level": experience_level,
        "sort_by": sort_by,
        "limit": limit,
        "offset": offset
    }
    jobs = get_jobs(params)
    return {
        "count": len(jobs),
        "results": jobs
    }

@app.get("/api/jobs/btech-cse")
def api_get_btech_cse_jobs(
    q: Optional[str] = None,
    category: Optional[str] = None,
    selection_mode: Optional[str] = None,
    experience: Optional[str] = None,
    min_ctc: Optional[float] = None,
    limit: int = Query(100, ge=1, le=200)
):
    params = {
        "q": q,
        "category": category,
        "selection_mode": selection_mode,
        "experience": experience,
        "min_ctc": min_ctc,
        "limit": limit
    }
    jobs = get_btech_cse_jobs(params)
    return {
        "count": len(jobs),
        "results": jobs
    }

@app.get("/api/jobs/corporate")
def api_get_corporate_jobs(
    company_type: Optional[str] = "all",
    location: Optional[str] = "all",
    eligible_only: Optional[bool] = False,
    min_ctc: Optional[float] = None,
    experience: Optional[str] = None,
    q: Optional[str] = None,
    limit: int = Query(100, ge=1, le=200)
):
    params = {
        "company_type": company_type,
        "location": location,
        "eligible_only": eligible_only,
        "min_ctc": min_ctc,
        "experience": experience,
        "q": q,
        "limit": limit
    }
    jobs = get_corporate_jobs(params)
    return {
        "count": len(jobs),
        "results": jobs
    }

@app.get("/api/corporate/stats")
def api_get_corporate_stats():
    return get_corporate_stats()

@app.get("/api/jobs/{job_id}")
def api_get_job_detail(job_id: int = FPath(..., description="Job ID")):
    job = get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")
    return job

@app.post("/api/match", response_model=List[MatchResult])
def api_match_profile(profile: MatchProfile):
    results = match_candidate(profile)
    return results

@app.get("/api/scan/stream")
def api_scan_stream():
    """Real-time Server-Sent Events (SSE) stream for live radar scanner widget."""
    return StreamingResponse(
        execute_scan_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@app.post("/api/scan/start")
def api_scan_sync():
    """Trigger synchronous batch scan."""
    result = run_scan_sync()
    stats = get_stats()
    return {
        "scan_result": result,
        "stats": stats
    }

@app.get("/api/scan/status")
def api_scan_status():
    scans = get_recent_scans(limit=10)
    stats = get_stats()
    return {
        "stats": stats,
        "recent_scans": scans
    }

@app.post("/api/bookmark/{job_id}")
def api_toggle_bookmark(job_id: int, req: Optional[BookmarkToggleRequest] = Body(default=None)):
    job = get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    notes = req.notes if req else None
    bookmarked = toggle_bookmark(job_id, notes)
    return {
        "job_id": job_id,
        "is_bookmarked": bookmarked,
        "message": "Job bookmarked" if bookmarked else "Bookmark removed"
    }

@app.get("/api/bookmarks")
def api_list_bookmarks():
    bookmarks = get_bookmarked_jobs()
    return {
        "count": len(bookmarks),
        "bookmarks": bookmarks
    }

@app.get("/api/stats")
def api_stats():
    return get_stats()

@app.get("/api/export")
def api_export_csv():
    jobs = get_jobs({"limit": 500})
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "ID", "Title (EN)", "Title (GU)", "Organization", "Department",
        "Level", "State", "Board", "Vacancies", "Qualification",
        "Age Limit", "Salary / Pay Scale", "Last Date", "Exam Date",
        "Apply Link", "Notification PDF", "Application Fee"
    ])

    for j in jobs:
        writer.writerow([
            j["id"],
            j["title"],
            j.get("title_gu", ""),
            j["organization"],
            j.get("department", ""),
            j["gov_level"],
            j["state"],
            j["board_category"],
            j["vacancies"],
            j["qualification"],
            f"{j['age_min']}-{j['age_max']} yrs",
            j.get("salary_text", ""),
            j["last_date"],
            j.get("exam_date", ""),
            j["apply_url"],
            j.get("notification_pdf_url", ""),
            j.get("application_fee", "")
        ])

    output.seek(0)
    filename = f"futurset_recruitment_report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.post("/api/subscribe")
def api_subscribe(sub: AlertSubscription):
    success = add_subscriber(
        name=sub.name,
        email=sub.email,
        phone=sub.phone,
        state_pref=sub.state_pref,
        preferred_boards=sub.preferred_boards
    )
    if not success:
        raise HTTPException(status_code=400, detail="Failed to subscribe. Please verify email.")
    return {"status": "success", "message": "Successfully subscribed to FuturSet Job Alerts!"}

@app.get("/api/pipeline/articles")
def api_get_pipeline_articles(stage: Optional[str] = None):
    """Fetch articles in the gazette editorial pipeline."""
    articles = get_pipeline_articles(stage)
    return {"count": len(articles), "articles": articles}

@app.post("/api/pipeline/articles")
def api_create_pipeline_article(payload: Dict[str, Any] = Body(...)):
    """Create a new article in the pipeline."""
    article_id = create_pipeline_article(payload)
    return {"success": True, "article_id": article_id}

@app.post("/api/pipeline/articles/{article_id}/transition")
def api_transition_pipeline_article(article_id: int, payload: Dict[str, str] = Body(...)):
    """Advance or move an article to another stage."""
    target_stage = payload.get("stage", "ingested")
    success = transition_pipeline_article(article_id, target_stage)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid stage or article not found")
    return {"success": True, "article_id": article_id, "stage": target_stage}

@app.post("/api/pipeline/articles/{article_id}/publish")
def api_publish_pipeline_article(article_id: int):
    """Publish an article directly to the live jobs database."""
    result = publish_pipeline_article(article_id)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail="Article not found")
    return result

@app.get("/api/previews")
def api_get_previews():
    """Returns metadata for all 28 visual directions and their animation references."""
    return {
        "count": len(PREVIEWS_DATA),
        "previews": PREVIEWS_DATA
    }

@app.get("/api/concepts")
def api_get_concepts():
    """Returns metadata for all 20 standalone concept websites."""
    return {
        "count": len(CONCEPTS_DATA),
        "concepts": CONCEPTS_DATA
    }

@app.get("/design-lab", response_class=HTMLResponse)
async def design_lab(request: Request, preview: str = Query("01")):
    """Dedicated Design Lab interactive showcase for all 28 visual directions."""
    active_preview = next((p for p in PREVIEWS_DATA if p["id"] == preview), PREVIEWS_DATA[0])
    stats = get_stats()
    return templates.TemplateResponse(
        request,
        "design_lab.html",
        {
            "title": "FuturSet Design Lab - 28 Visual Identities of FuturSet",
            "previews": PREVIEWS_DATA,
            "active_preview": active_preview,
            "stats": stats,
            "version": APP_VERSION
        }
    )

@app.get("/concepts", response_class=HTMLResponse)
async def concepts_hub(request: Request):
    """Concept Lab showcasing the 20 standalone experimental websites."""
    return templates.TemplateResponse(
        request,
        "concepts.html",
        {
            "title": "FuturSet Concept Lab - 20 Standalone Experimental Websites",
            "concepts": CONCEPTS_DATA,
            "version": APP_VERSION
        }
    )

@app.get("/concepts/{concept_id}", response_class=HTMLResponse)
async def concept_detail(request: Request, concept_id: str = FPath(...)):
    """View an individual standalone concept website."""
    concept = next((c for c in CONCEPTS_DATA if c["id"] == concept_id or c["slug"] == concept_id), None)
    if not concept:
        raise HTTPException(status_code=404, detail=f"Concept {concept_id} not found")
    stats = get_stats()
    jobs = get_jobs({"limit": 20})
    return templates.TemplateResponse(
        request,
        "concept_view.html",
        {
            "title": f"Concept #{concept['id']} — {concept['title']} | FuturSet Experimental",
            "concept": concept,
            "all_concepts": CONCEPTS_DATA,
            "jobs": jobs,
            "stats": stats,
            "version": APP_VERSION
        }
    )

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "brand": "FuturSet",
        "version": APP_VERSION,
        "database": "connected",
        "design_lab": "enabled",
        "previews_count": len(PREVIEWS_DATA),
        "concepts_count": len(CONCEPTS_DATA)
    }
