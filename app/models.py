"""
FuturSet Jobs Portal - Pydantic Data Models & Schemas
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class JobBase(BaseModel):
    title: str
    title_gu: Optional[str] = None
    organization: str
    department: Optional[str] = None
    gov_level: str = "State"  # "Central" or "State"
    state: str = "Gujarat"
    board_category: str = "OJAS"
    vacancies: int = 0
    qualification: str = "Graduate"
    age_min: int = 18
    age_max: int = 35
    age_relaxation_text: Optional[str] = "OBC: +3 yrs, SC/ST: +5 yrs, Women: +5 yrs"
    salary_text: Optional[str] = "Pay Scale Level 4"
    start_date: Optional[str] = None
    last_date: str
    exam_date: Optional[str] = None
    notification_number: Optional[str] = None
    notification_pdf_url: Optional[str] = None
    apply_url: str
    official_website: Optional[str] = None
    application_fee: Optional[str] = "₹100 for General; Exempted for Reserved"
    selection_process: Optional[str] = "Written Test & Document Verification"
    syllabus_summary: Optional[str] = "General Knowledge, Aptitude, English, Gujarati / Regional"
    source: str = "FuturSet Scanner"
    is_active: int = 1
    featured: int = 0
    selection_mode: Optional[str] = "written_exam"
    job_category: Optional[str] = "government"
    is_btech_cse: Optional[int] = 0
    experience_level: Optional[str] = "fresher"
    tech_stack: Optional[str] = ""
    ctc_lpa: Optional[float] = 0.0

class JobCreate(JobBase):
    pass

class JobResponse(JobBase):
    id: int
    created_at: str
    updated_at: str
    views_count: int = 0
    hash_key: str
    is_bookmarked: bool = False
    days_left: int = 0
    urgency_badge: str = "normal"  # 'urgent' (< 3 days), 'warning' (< 7 days), 'normal'

class JobFilterParams(BaseModel):
    q: Optional[str] = None
    gov_level: Optional[str] = None
    state: Optional[str] = None
    board: Optional[str] = None
    qualification: Optional[str] = None
    selection_mode: Optional[str] = None
    job_category: Optional[str] = None
    is_btech_cse: Optional[int] = None
    experience_level: Optional[str] = None
    sort_by: Optional[str] = "deadline"  # 'deadline', 'vacancies', 'newest', 'salary'
    limit: int = 50
    offset: int = 0

class MatchProfile(BaseModel):
    age: int = 24
    qualification: str = "Graduate"
    category: str = "General"  # General, OBC/SEBC, EWS, SC, ST, Female, PwD, Ex-SM
    state_preference: str = "Gujarat"
    include_central: bool = True

class MatchResult(BaseModel):
    job: JobResponse
    match_score: int
    eligibility_status: str
    reasons: List[str]
    relaxation_applied: Optional[str] = None

class ScanEvent(BaseModel):
    step: int
    total_steps: int
    source_name: str
    status: str
    message: str
    jobs_scanned: int
    jobs_added: int
    jobs_updated: int
    timestamp: str

class BookmarkToggleRequest(BaseModel):
    job_id: Optional[int] = None
    notes: Optional[str] = None

class AlertSubscription(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    state_pref: str = "Gujarat"
    preferred_boards: List[str] = []

class PortalStats(BaseModel):
    total_jobs: int
    total_vacancies: int
    gujarat_jobs: int
    gujarat_vacancies: int
    central_jobs: int
    central_vacancies: int
    closing_soon: int
    last_scan_time: Optional[str] = None
