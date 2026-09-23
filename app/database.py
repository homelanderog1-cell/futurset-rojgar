"""
FuturSet Jobs Portal - Database Layer (SQLite)
High-performance SQLite interface with indexing, FTS capabilities, seed data, and bookmarking.
"""
import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from app.config import DB_PATH

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH), timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn

def compute_job_hash(title: str, organization: str, notification_number: Optional[str]) -> str:
    clean_notif = (notification_number or "").strip().lower()
    clean_org = organization.strip().lower()
    clean_title = title.strip().lower()
    if clean_notif and len(clean_notif) > 2:
        raw = f"{clean_org}|{clean_notif}"
    else:
        raw = f"{clean_title}|{clean_org}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()

def calculate_days_left(last_date_str: str) -> int:
    try:
        last_dt = datetime.strptime(last_date_str.strip()[:10], "%Y-%m-%d").date()
        today = datetime.now().date()
        delta = (last_dt - today).days
        return delta
    except Exception:
        return 30

def determine_urgency(days_left: int) -> str:
    if days_left < 0:
        return "closed"
    elif days_left == 0:
        return "urgent"  # Closes today
    elif days_left <= 3:
        return "urgent"
    elif days_left <= 7:
        return "warning"
    return "normal"

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        title_gu TEXT,
        organization TEXT NOT NULL,
        department TEXT,
        gov_level TEXT NOT NULL,  -- 'Central' or 'State'
        state TEXT NOT NULL,      -- 'Gujarat', 'All India', etc.
        board_category TEXT NOT NULL, -- 'OJAS', 'GPSC', 'GSSSB', 'Police', 'High Court', 'GSRTC', 'SSC', 'UPSC', 'RRB', 'Banking', 'Electricity', etc.
        district TEXT DEFAULT 'All Gujarat',
        vacancies INTEGER NOT NULL DEFAULT 0,
        qualification TEXT NOT NULL,
        qualification_level TEXT DEFAULT 'Graduate',
        age_min INTEGER NOT NULL DEFAULT 18,
        age_max INTEGER NOT NULL DEFAULT 35,
        age_relaxation_text TEXT,
        salary_text TEXT,
        start_date TEXT,
        last_date TEXT NOT NULL,
        exam_date TEXT,
        notification_number TEXT,
        notification_pdf_url TEXT,
        apply_url TEXT NOT NULL,
        official_website TEXT,
        application_fee TEXT,
        selection_process TEXT,
        syllabus_summary TEXT,
        source TEXT DEFAULT 'FuturSet Engine',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        is_active INTEGER NOT NULL DEFAULT 1,
        featured INTEGER NOT NULL DEFAULT 0,
        views_count INTEGER NOT NULL DEFAULT 0,
        hash_key TEXT UNIQUE NOT NULL
    );
    """)

    # Schema migration check for existing tables
    cursor.execute("PRAGMA table_info(jobs);")
    existing_cols = [c[1] for c in cursor.fetchall()]
    if "district" not in existing_cols:
        cursor.execute("ALTER TABLE jobs ADD COLUMN district TEXT DEFAULT 'All Gujarat';")
    if "qualification_level" not in existing_cols:
        cursor.execute("ALTER TABLE jobs ADD COLUMN qualification_level TEXT DEFAULT 'Graduate';")
    if "selection_mode" not in existing_cols:
        cursor.execute("ALTER TABLE jobs ADD COLUMN selection_mode TEXT DEFAULT 'written_exam';")
    if "job_category" not in existing_cols:
        cursor.execute("ALTER TABLE jobs ADD COLUMN job_category TEXT DEFAULT 'government';")
    if "is_btech_cse" not in existing_cols:
        cursor.execute("ALTER TABLE jobs ADD COLUMN is_btech_cse INTEGER DEFAULT 0;")
    if "experience_level" not in existing_cols:
        cursor.execute("ALTER TABLE jobs ADD COLUMN experience_level TEXT DEFAULT 'fresher';")
    if "tech_stack" not in existing_cols:
        cursor.execute("ALTER TABLE jobs ADD COLUMN tech_stack TEXT DEFAULT '';")
    if "ctc_lpa" not in existing_cols:
        cursor.execute("ALTER TABLE jobs ADD COLUMN ctc_lpa REAL DEFAULT 0.0;")

    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_jobs_gov_state ON jobs(gov_level, state);
    """)
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_jobs_board ON jobs(board_category);
    """)
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_jobs_last_date ON jobs(last_date);
    """)
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_jobs_active ON jobs(is_active);
    """)
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_jobs_sel_mode ON jobs(selection_mode);
    """)
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_jobs_btech ON jobs(is_btech_cse);
    """)
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_jobs_category ON jobs(job_category);
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookmarks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER UNIQUE NOT NULL,
        created_at TEXT NOT NULL,
        notes TEXT,
        FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scan_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        source_name TEXT NOT NULL,
        jobs_scanned INTEGER NOT NULL DEFAULT 0,
        jobs_added INTEGER NOT NULL DEFAULT 0,
        jobs_updated INTEGER NOT NULL DEFAULT 0,
        duration_seconds REAL NOT NULL DEFAULT 0.0,
        status TEXT NOT NULL,
        message TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subscribers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT,
        state_pref TEXT DEFAULT 'Gujarat',
        preferred_boards TEXT,
        created_at TEXT NOT NULL
    );
    """)

    conn.commit()
    conn.close()

    # Seed initial authentic job datasets if empty
    seed_initial_jobs()
    sync_all_catalog_jobs()

def seed_initial_jobs():
    """Delegate directly to sync_all_catalog_jobs to prevent duplicate seed entries."""
    sync_all_catalog_jobs()



def get_jobs(params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    SELECT j.*, (b.id IS NOT NULL) AS is_bookmarked
    FROM jobs j
    LEFT JOIN bookmarks b ON j.id = b.job_id
    WHERE j.is_active = 1
    """
    args = []

    if params:
        if params.get("q"):
            term = f"%{params['q'].strip()}%"
            query += " AND (j.title LIKE ? OR j.title_gu LIKE ? OR j.organization LIKE ? OR j.department LIKE ? OR j.qualification LIKE ? OR j.notification_number LIKE ? OR j.board_category LIKE ? OR j.district LIKE ? OR j.state LIKE ?)"
            args.extend([term, term, term, term, term, term, term, term, term])

        if params.get("gov_level"):
            query += " AND j.gov_level = ?"
            args.append(params["gov_level"])

        if params.get("state"):
            if params["state"].lower() == "gujarat":
                query += " AND j.state = 'Gujarat'"
            else:
                query += " AND j.state = ?"
                args.append(params["state"])

        if params.get("board"):
            query += " AND j.board_category = ?"
            args.append(params["board"])

        if params.get("district"):
            dist = params["district"].strip()
            if dist and dist != "All Gujarat":
                query += " AND (j.district LIKE ? OR j.district = 'All Gujarat')"
                args.append(f"%{dist}%")

        if params.get("sector"):
            sec = params["sector"].strip().lower()
            if sec == "police":
                query += " AND (j.board_category IN ('Police', 'Defence') OR j.title LIKE '%Police%' OR j.title LIKE '%Constable%' OR j.title LIKE '%પોલીસ%')"
            elif sec == "civil":
                query += " AND (j.board_category IN ('GPSC', 'UPSC') OR j.title LIKE '%Administrative%' OR j.title LIKE '%Civil%' OR j.title LIKE '%વહીવટી%')"
            elif sec == "clerk":
                query += " AND (j.title LIKE '%Clerk%' OR j.title LIKE '%Assistant%' OR j.title LIKE '%ક્લાર્ક%' OR j.board_category IN ('GSSSB', 'High Court', 'GPSSB'))"
            elif sec == "teaching":
                query += " AND (j.board_category = 'Vidhyasahayak' OR j.title LIKE '%Teacher%' OR j.title LIKE '%Professor%' OR j.title LIKE '%શિક્ષક%' OR j.title LIKE '%શિક્ષણ%')"
            elif sec == "engineering":
                query += " AND (j.qualification LIKE '%Engineering%' OR j.qualification LIKE '%B.E.%' OR j.title LIKE '%Engineer%' OR j.title LIKE '%ઈજનેર%')"
            elif sec == "medical":
                query += " AND (j.qualification LIKE '%MBBS%' OR j.qualification LIKE '%Nursing%' OR j.title LIKE '%Medical%' OR j.title LIKE '%Nurse%' OR j.title LIKE '%તબીબી%')"
            elif sec == "railways":
                query += " AND (j.board_category = 'RRB' OR j.title LIKE '%Railway%' OR j.title LIKE '%રેલ્વે%')"
            elif sec == "banking":
                query += " AND (j.board_category = 'Banking' OR j.title LIKE '%Bank%' OR j.title LIKE '%IBPS%' OR j.title LIKE '%SBI%')"
            elif sec == "transport":
                query += " AND (j.board_category = 'GSRTC' OR j.title LIKE '%GSRTC%' OR j.title LIKE '%ST%')"
            elif sec == "electricity":
                query += " AND (j.board_category = 'Electricity' OR j.title LIKE '%Vidyut%' OR j.title LIKE '%વિદ્યુત%')"
            elif sec == "defence":
                query += " AND (j.board_category = 'Defence' OR j.title LIKE '%Army%' OR j.title LIKE '%Navy%' OR j.title LIKE '%Air Force%' OR j.title LIKE '%સેના%')"
            elif sec == "forest":
                query += " AND (j.board_category = 'Forest' OR j.title LIKE '%Forest%' OR j.title LIKE '%વનરક્ષક%' OR j.title LIKE '%વનપાલ%')"
            elif sec == "postal":
                query += " AND (j.board_category = 'Postal' OR j.organization LIKE '%Post%' OR j.title LIKE '%Postal%' OR j.title LIKE '%Postman%' OR j.title LIKE '%Dak Sevak%' OR j.title LIKE '%GDS%' OR j.title LIKE '%ટપાલ%')"
            elif sec in ("aviation", "airport"):
                query += " AND (j.board_category = 'Aviation' OR j.title LIKE '%Airport%' OR j.title LIKE '%Aviation%' OR j.title LIKE '%AAI%' OR j.title LIKE '%Air Traffic%' OR j.title LIKE '%એરપોર્ટ%')"

        if params.get("urgency"):
            urg = params["urgency"].strip().lower()
            if urg == "closing_48h":
                query += " AND j.last_date <= date('now', '+2 days') AND j.last_date >= date('now')"
            elif urg == "closing_week":
                query += " AND j.last_date <= date('now', '+7 days') AND j.last_date >= date('now')"
            elif urg == "no_fee":
                query += " AND (j.application_fee LIKE '%0%' OR j.application_fee LIKE '%Nil%' OR j.application_fee LIKE '%Exempt%' OR j.application_fee LIKE '%Free%')"

        if params.get("selection_mode"):
            mode = params["selection_mode"].strip().lower()
            if mode in ("direct_merit", "direct", "merit"):
                query += " AND (j.selection_mode = 'direct_merit' OR j.selection_process LIKE '%Merit%' OR j.title LIKE '%Merit%' OR j.title LIKE '%GDS%')"
            elif mode in ("walk_in", "walkin", "interview"):
                query += " AND (j.selection_mode = 'walk_in' OR j.selection_process LIKE '%Walk-in%' OR j.selection_process LIKE '%Interview%')"
            elif mode in ("apprenticeship", "apprentice"):
                query += " AND (j.selection_mode = 'apprenticeship' OR j.title LIKE '%Apprentice%' OR j.board_category = 'Apprenticeship')"
            elif mode in ("written_exam", "exam", "cbt"):
                query += " AND (j.selection_mode = 'written_exam' OR j.selection_process LIKE '%Written%' OR j.selection_process LIKE '%Exam%' OR j.selection_process LIKE '%CBT%')"
            elif mode in ("coding_test", "tech_interview", "coding"):
                query += " AND (j.selection_mode = 'coding_test' OR j.selection_process LIKE '%Coding%' OR j.selection_process LIKE '%Technical Interview%')"

        if params.get("job_category"):
            cat = params["job_category"].strip().lower()
            if cat in ("govt", "government"):
                query += " AND (j.job_category = 'government' OR j.gov_level IN ('Central', 'State'))"
            elif cat in ("psu", "public_sector"):
                query += " AND (j.job_category = 'psu' OR j.board_category IN ('PSU', 'Aviation', 'Electricity'))"
            elif cat in ("private", "corporate", "mnc"):
                query += " AND j.job_category = 'private'"

        if params.get("is_btech_cse"):
            query += " AND (j.is_btech_cse = 1 OR j.qualification LIKE '%Computer%' OR j.qualification LIKE '%B.Tech CSE%' OR j.qualification LIKE '%IT%')"

        if params.get("experience_level"):
            exp = params["experience_level"].strip().lower()
            if exp in ("fresher", "0-1"):
                query += " AND (j.experience_level = 'fresher' OR j.experience_level = 'all' OR j.qualification LIKE '%fresher%' OR j.age_min <= 21)"
            elif exp in ("experienced", "2+"):
                query += " AND (j.experience_level = 'experienced' OR j.experience_level = 'all')"

        # Sorting
        sort_by = params.get("sort_by", "deadline")
        if sort_by == "vacancies":
            query += " ORDER BY j.vacancies DESC, j.last_date ASC"
        elif sort_by == "newest":
            query += " ORDER BY j.id DESC"
        elif sort_by == "salary":
            query += " ORDER BY j.featured DESC, j.vacancies DESC"
        else:  # deadline
            query += " ORDER BY j.last_date ASC"

        limit = params.get("limit", 50)
        offset = params.get("offset", 0)
        query += " LIMIT ? OFFSET ?"
        args.extend([limit, offset])
    else:
        query += " ORDER BY j.last_date ASC LIMIT 50"

    cursor.execute(query, args)
    rows = cursor.fetchall()
    results = []
    for r in rows:
        d = dict(r)
        d["days_left"] = calculate_days_left(d["last_date"])
        d["urgency_badge"] = determine_urgency(d["days_left"])
        d["is_bookmarked"] = bool(d["is_bookmarked"])
        results.append(d)

    conn.close()
    return results

def get_job_by_id(job_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT j.*, (b.id IS NOT NULL) AS is_bookmarked
    FROM jobs j
    LEFT JOIN bookmarks b ON j.id = b.job_id
    WHERE j.id = ?
    """, (job_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None

    # Increment view count
    cursor.execute("UPDATE jobs SET views_count = views_count + 1 WHERE id = ?", (job_id,))
    conn.commit()

    d = dict(row)
    d["days_left"] = calculate_days_left(d["last_date"])
    d["urgency_badge"] = determine_urgency(d["days_left"])
    d["is_bookmarked"] = bool(d["is_bookmarked"])
    conn.close()
    return d

def upsert_job(job_dict: Dict[str, Any]) -> str:
    conn = get_db_connection()
    cursor = conn.cursor()

    title = job_dict["title"]
    org = job_dict["organization"]
    notif_no = job_dict.get("notification_number")
    hk = compute_job_hash(title, org, notif_no)
    now_str = datetime.now().isoformat()

    cursor.execute("SELECT id FROM jobs WHERE hash_key = ?", (hk,))
    existing = cursor.fetchone()

    if existing:
        job_id = existing[0]
        cursor.execute("""
        UPDATE jobs SET
            title_gu = COALESCE(?, title_gu),
            vacancies = COALESCE(?, vacancies),
            last_date = COALESCE(?, last_date),
            apply_url = COALESCE(?, apply_url),
            notification_pdf_url = COALESCE(?, notification_pdf_url),
            salary_text = COALESCE(?, salary_text),
            district = COALESCE(?, district),
            qualification_level = COALESCE(?, qualification_level),
            selection_mode = COALESCE(?, selection_mode),
            job_category = COALESCE(?, job_category),
            is_btech_cse = COALESCE(?, is_btech_cse),
            experience_level = COALESCE(?, experience_level),
            tech_stack = COALESCE(?, tech_stack),
            ctc_lpa = COALESCE(?, ctc_lpa),
            updated_at = ?,
            is_active = 1
        WHERE id = ?
        """, (
            job_dict.get("title_gu"),
            job_dict.get("vacancies"),
            job_dict.get("last_date"),
            job_dict.get("apply_url"),
            job_dict.get("notification_pdf_url"),
            job_dict.get("salary_text"),
            job_dict.get("district"),
            job_dict.get("qualification_level"),
            job_dict.get("selection_mode"),
            job_dict.get("job_category"),
            job_dict.get("is_btech_cse"),
            job_dict.get("experience_level"),
            job_dict.get("tech_stack"),
            job_dict.get("ctc_lpa"),
            now_str,
            job_id
        ))
        conn.commit()
        conn.close()
        return "updated"
    else:
        cursor.execute("""
        INSERT INTO jobs (
            title, title_gu, organization, department, gov_level, state, board_category,
            district, vacancies, qualification, qualification_level, age_min, age_max,
            age_relaxation_text, salary_text, start_date, last_date, exam_date,
            notification_number, notification_pdf_url, apply_url, official_website,
            application_fee, selection_process, syllabus_summary, source, created_at,
            updated_at, is_active, featured, views_count, hash_key,
            selection_mode, job_category, is_btech_cse, experience_level, tech_stack, ctc_lpa
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            title, job_dict.get("title_gu"), org, job_dict.get("department"),
            job_dict.get("gov_level", "State"), job_dict.get("state", "Gujarat"),
            job_dict.get("board_category", "OJAS"), job_dict.get("district", "All Gujarat"),
            job_dict.get("vacancies", 0), job_dict.get("qualification", "Graduate"),
            job_dict.get("qualification_level", "Graduate"), job_dict.get("age_min", 18),
            job_dict.get("age_max", 35), job_dict.get("age_relaxation_text"),
            job_dict.get("salary_text"), job_dict.get("start_date", now_str[:10]),
            job_dict["last_date"], job_dict.get("exam_date"), notif_no,
            job_dict.get("notification_pdf_url"), job_dict["apply_url"],
            job_dict.get("official_website"), job_dict.get("application_fee"),
            job_dict.get("selection_process"), job_dict.get("syllabus_summary"),
            job_dict.get("source", "FuturSet Live Scanner"), now_str, now_str,
            1, job_dict.get("featured", 0), 0, hk,
            job_dict.get("selection_mode", "written_exam"),
            job_dict.get("job_category", "government"),
            job_dict.get("is_btech_cse", 0),
            job_dict.get("experience_level", "fresher"),
            job_dict.get("tech_stack", ""),
            job_dict.get("ctc_lpa", 0.0)
        ))
        conn.commit()
        conn.close()
        return "added"

def sync_all_catalog_jobs() -> int:
    """Sync all authentic recruitment seeds (Govt, Tech & Merit, Corporate) into the database."""
    added_or_updated = 0
    # 1. Government authentic jobs (Gujarat OJAS + Central)
    try:
        from app.seeds import generate_all_authentic_jobs
        for s in generate_all_authentic_jobs():
            res = upsert_job(s)
            if res in ("added", "updated"):
                added_or_updated += 1
    except Exception as e:
        print(f"Govt catalog sync notice: {e}")

    # 2. Tech & Merit jobs (B.Tech CSE/IT, Apprenticeships, Engineering)
    try:
        from app.tech_and_merit_seeds import generate_all_tech_and_merit_jobs
        for s in generate_all_tech_and_merit_jobs():
            res = upsert_job(s)
            if res in ("added", "updated"):
                added_or_updated += 1
    except Exception as e:
        print(f"Tech catalog sync notice: {e}")

    # 3. Corporate jobs (Enterprise, Conglomerate, Tech Hubs)
    try:
        from app.corporate_seeds import generate_all_corporate_jobs
        for s in generate_all_corporate_jobs():
            res = upsert_job(s)
            if res in ("added", "updated"):
                added_or_updated += 1
    except Exception as e:
        print(f"Corporate catalog sync notice: {e}")

    return added_or_updated

def toggle_bookmark(job_id: int, notes: Optional[str] = None) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM bookmarks WHERE job_id = ?", (job_id,))
    row = cursor.fetchone()
    if row:
        cursor.execute("DELETE FROM bookmarks WHERE job_id = ?", (job_id,))
        is_bookmarked = False
    else:
        cursor.execute("INSERT INTO bookmarks (job_id, created_at, notes) VALUES (?, ?, ?)",
                       (job_id, datetime.now().isoformat(), notes))
        is_bookmarked = True
    conn.commit()
    conn.close()
    return is_bookmarked

def get_bookmarked_jobs() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT j.*, 1 AS is_bookmarked, b.notes AS bookmark_notes, b.created_at AS bookmarked_at
    FROM bookmarks b
    JOIN jobs j ON b.job_id = j.id
    ORDER BY b.id DESC
    """)
    rows = cursor.fetchall()
    results = []
    for r in rows:
        d = dict(r)
        d["days_left"] = calculate_days_left(d["last_date"])
        d["urgency_badge"] = determine_urgency(d["days_left"])
        d["is_bookmarked"] = True
        results.append(d)
    conn.close()
    return results

def get_btech_cse_jobs(params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Fetch jobs relevant to B.Tech CSE, IT, Software Engineering & MCA graduates."""
    params = params or {}
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    SELECT j.*, (b.id IS NOT NULL) AS is_bookmarked
    FROM jobs j
    LEFT JOIN bookmarks b ON j.id = b.job_id
    WHERE j.is_active = 1
      AND (
          j.is_btech_cse = 1
          OR j.qualification LIKE '%Computer%'
          OR j.qualification LIKE '%B.Tech CSE%'
          OR j.qualification LIKE '%Information Technology%'
          OR j.qualification LIKE '%MCA%'
          OR j.title LIKE '%Software%'
          OR j.title LIKE '%Programmer%'
          OR j.title LIKE '%IT Officer%'
          OR j.title LIKE '%Scientist%'
      )
    """
    args = []

    if params.get("category"):
        cat = params["category"].strip().lower()
        if cat in ("central_govt", "central"):
            query += " AND j.gov_level = 'Central' AND j.job_category = 'government'"
        elif cat in ("gujarat_govt", "state", "gujarat"):
            query += " AND j.state = 'Gujarat' AND j.job_category = 'government'"
        elif cat == "psu":
            query += " AND (j.job_category = 'psu' OR j.board_category IN ('PSU', 'Aviation', 'Electricity'))"
        elif cat == "private":
            query += " AND j.job_category = 'private'"

    if params.get("selection_mode"):
        mode = params["selection_mode"].strip().lower()
        if mode == "gate":
            query += " AND (j.selection_process LIKE '%GATE%' OR j.syllabus_summary LIKE '%GATE%')"
        elif mode == "written_exam":
            query += " AND (j.selection_mode = 'written_exam' OR j.selection_process LIKE '%Written%' OR j.selection_process LIKE '%CBT%')"
        elif mode == "coding_test":
            query += " AND (j.selection_mode = 'coding_test' OR j.selection_process LIKE '%Coding%' OR j.selection_process LIKE '%Technical Interview%')"
        elif mode in ("direct_merit", "merit"):
            query += " AND (j.selection_mode = 'direct_merit' OR j.selection_process LIKE '%Merit%')"

    if params.get("experience"):
        exp = params["experience"].strip().lower()
        if exp in ("fresher", "0-1"):
            query += " AND (j.experience_level = 'fresher' OR j.experience_level = 'all')"
        elif exp in ("experienced", "2+"):
            query += " AND (j.experience_level = 'experienced' OR j.experience_level = 'all')"

    if params.get("min_ctc"):
        try:
            min_c = float(params["min_ctc"])
            query += " AND j.ctc_lpa >= ?"
            args.append(min_c)
        except Exception:
            pass

    if params.get("q"):
        term = f"%{params['q'].strip()}%"
        query += " AND (j.title LIKE ? OR j.organization LIKE ? OR j.tech_stack LIKE ? OR j.qualification LIKE ?)"
        args.extend([term, term, term, term])

    query += " ORDER BY j.featured DESC, j.vacancies DESC, j.last_date ASC"
    limit = params.get("limit", 100)
    query += " LIMIT ?"
    args.append(limit)

    cursor.execute(query, args)
    rows = cursor.fetchall()
    results = []
    for r in rows:
        d = dict(r)
        d["days_left"] = calculate_days_left(d["last_date"])
        d["urgency_badge"] = determine_urgency(d["days_left"])
        d["is_bookmarked"] = bool(d["is_bookmarked"])
        results.append(d)
    conn.close()
    return results

def get_corporate_jobs(params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Fetch jobs from corporate, semi-private, PSU, conglomerate, and tech enterprises.
    Supports Adani, BHEL, Linde, Amazon, Flipkart, NPCI/UPI, Reliance, Tata, L&T, GIFT City, etc.
    """
    params = params or {}
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    SELECT j.*, (b.id IS NOT NULL) AS is_bookmarked
    FROM jobs j
    LEFT JOIN bookmarks b ON j.id = b.job_id
    WHERE j.is_active = 1
      AND (
          j.job_category IN ('private', 'semi_private', 'global_tech', 'fintech_startup', 'mid_sized', 'psu')
          OR j.board_category IN ('Corporate', 'PSU', 'Aviation')
          OR j.organization LIKE '%Adani%'
          OR j.organization LIKE '%BHEL%'
          OR j.organization LIKE '%Linde%'
          OR j.organization LIKE '%Amazon%'
          OR j.organization LIKE '%Flipkart%'
          OR j.organization LIKE '%NPCI%'
          OR j.organization LIKE '%UPI%'
          OR j.organization LIKE '%Reliance%'
          OR j.organization LIKE '%Tata%'
          OR j.organization LIKE '%L&T%'
          OR j.organization LIKE '%GSFC%'
          OR j.organization LIKE '%GNFC%'
          OR j.organization LIKE '%GACL%'
          OR j.organization LIKE '%PhonePe%'
          OR j.organization LIKE '%Paytm%'
          OR j.organization LIKE '%Zerodha%'
          OR j.organization LIKE '%GIFT City%'
          OR j.organization LIKE '%Infosys%'
          OR j.organization LIKE '%Wipro%'
          OR j.organization LIKE '%Google%'
          OR j.organization LIKE '%Microsoft%'
      )
    """
    args = []

    # Filter: company_type
    if params.get("company_type") and params["company_type"] != "all":
        ctype = params["company_type"].strip().lower()
        if ctype == "semi_private":
            query += """ AND (
                j.job_category IN ('semi_private', 'psu')
                OR j.organization LIKE '%BHEL%'
                OR j.organization LIKE '%Linde%'
                OR j.organization LIKE '%NPCI%'
                OR j.organization LIKE '%GSFC%'
                OR j.organization LIKE '%GNFC%'
                OR j.organization LIKE '%GACL%'
                OR j.organization LIKE '%BEL%'
                OR j.organization LIKE '%PowerGrid%'
            )"""
        elif ctype == "conglomerate":
            query += """ AND (
                j.job_category = 'conglomerate'
                OR j.organization LIKE '%Adani%'
                OR j.organization LIKE '%Reliance%'
                OR j.organization LIKE '%Jio%'
                OR j.organization LIKE '%Tata%'
                OR j.organization LIKE '%Larsen%'
                OR j.organization LIKE '%L&T%'
                OR j.organization LIKE '%Birla%'
                OR j.organization LIKE '%JSW%'
                OR j.organization LIKE '%Vedanta%'
                OR j.organization LIKE '%Mahindra%'
            )"""
        elif ctype == "global_tech":
            query += """ AND (
                j.job_category = 'global_tech'
                OR j.organization LIKE '%Amazon%'
                OR j.organization LIKE '%Flipkart%'
                OR j.organization LIKE '%Google%'
                OR j.organization LIKE '%Microsoft%'
                OR j.organization LIKE '%Apple%'
                OR j.organization LIKE '%Meta%'
                OR j.organization LIKE '%Adobe%'
                OR j.organization LIKE '%Oracle%'
                OR j.organization LIKE '%Cisco%'
                OR j.organization LIKE '%Intel%'
                OR j.organization LIKE '%NVIDIA%'
                OR j.organization LIKE '%Qualcomm%'
                OR j.organization LIKE '%Salesforce%'
                OR j.organization LIKE '%SAP%'
                OR j.organization LIKE '%IBM%'
                OR j.organization LIKE '%Uber%'
                OR j.organization LIKE '%Atlassian%'
                OR j.organization LIKE '%Intuit%'
            )"""
        elif ctype in ("unicorns", "fintech_startup"):
            query += """ AND (
                j.job_category IN ('unicorns', 'fintech_startup', 'mid_sized')
                OR j.organization LIKE '%Swiggy%'
                OR j.organization LIKE '%Zomato%'
                OR j.organization LIKE '%Meesho%'
                OR j.organization LIKE '%Zepto%'
                OR j.organization LIKE '%CRED%'
                OR j.organization LIKE '%Groww%'
                OR j.organization LIKE '%Razorpay%'
                OR j.organization LIKE '%Delhivery%'
                OR j.organization LIKE '%Nykaa%'
                OR j.organization LIKE '%PhonePe%'
                OR j.organization LIKE '%Paytm%'
                OR j.organization LIKE '%Zerodha%'
            )"""
        elif ctype == "it_services":
            query += """ AND (
                j.job_category = 'it_services'
                OR j.organization LIKE '%TCS%'
                OR j.organization LIKE '%Tata Consultancy%'
                OR j.organization LIKE '%Infosys%'
                OR j.organization LIKE '%Wipro%'
                OR j.organization LIKE '%Capgemini%'
                OR j.organization LIKE '%Cognizant%'
                OR j.organization LIKE '%HCL%'
                OR j.organization LIKE '%Tech Mahindra%'
                OR j.organization LIKE '%LTIMindtree%'
                OR j.organization LIKE '%Hexaware%'
                OR j.organization LIKE '%Persistent%'
                OR j.organization LIKE '%Mphasis%'
                OR j.organization LIKE '%Coforge%'
                OR j.organization LIKE '%Birlasoft%'
                OR j.organization LIKE '%Zensar%'
                OR j.organization LIKE '%KPIT%'
            )"""
        elif ctype == "bfsi":
            query += """ AND (
                j.job_category = 'bfsi'
                OR j.organization LIKE '%HDFC%'
                OR j.organization LIKE '%ICICI%'
                OR j.organization LIKE '%Axis%'
                OR j.organization LIKE '%Kotak%'
                OR j.organization LIKE '%Bajaj Finance%'
                OR j.organization LIKE '%IndusInd%'
                OR j.organization LIKE '%Tata Capital%'
                OR j.organization LIKE '%Aditya Birla Capital%'
                OR j.organization LIKE '%Muthoot%'
            )"""
        elif ctype == "auto_ev":
            query += """ AND (
                j.job_category = 'auto_ev'
                OR j.organization LIKE '%Maruti%'
                OR j.organization LIKE '%Ola Electric%'
                OR j.organization LIKE '%Ather%'
                OR j.organization LIKE '%Hyundai%'
                OR j.organization LIKE '%Hero%'
                OR j.organization LIKE '%Bajaj Auto%'
                OR j.organization LIKE '%TVS%'
            )"""
        elif ctype == "pharma":
            query += """ AND (
                j.job_category = 'pharma'
                OR j.organization LIKE '%Sun Pharma%'
                OR j.organization LIKE '%Zydus%'
                OR j.organization LIKE '%Torrent Pharma%'
                OR j.organization LIKE '%Dr. Reddy%'
                OR j.organization LIKE '%Cipla%'
                OR j.organization LIKE '%Lupin%'
                OR j.organization LIKE '%Intas%'
                OR j.organization LIKE '%Alembic%'
                OR j.organization LIKE '%Mankind%'
            )"""
        elif ctype == "fmcg":
            query += """ AND (
                j.job_category = 'fmcg'
                OR j.organization LIKE '%Hindustan Unilever%'
                OR j.organization LIKE '%HUL%'
                OR j.organization LIKE '%ITC%'
                OR j.organization LIKE '%Nestle%'
                OR j.organization LIKE '%Asian Paints%'
                OR j.organization LIKE '%Britannia%'
                OR j.organization LIKE '%Marico%'
                OR j.organization LIKE '%Dabur%'
                OR j.organization LIKE '%Pidilite%'
                OR j.organization LIKE '%Havells%'
                OR j.organization LIKE '%Godrej%'
            )"""
        elif ctype == "gujarat_champions":
            query += """ AND (
                j.job_category = 'gujarat_champions'
                OR j.organization LIKE '%Torrent Power%'
                OR j.organization LIKE '%Nirma%'
                OR j.organization LIKE '%Arvind%'
                OR j.organization LIKE '%Astral%'
                OR j.organization LIKE '%Welspun%'
                OR j.organization LIKE '%Cadila%'
                OR j.organization LIKE '%Suzlon%'
                OR j.organization LIKE '%GHCL%'
                OR j.organization LIKE '%Crest%'
                OR j.organization LIKE '%Radixweb%'
                OR j.organization LIKE '%GIFT City%'
            )"""

    # Filter: eligible_only
    if params.get("eligible_only") in (True, 1, "1", "true", "True"):
        query += """ AND (
            j.is_btech_cse = 1
            OR j.qualification_level IN ('Engineering', 'Graduate')
            OR j.qualification LIKE '%Engineering%'
            OR j.qualification LIKE '%B.Tech%'
            OR j.qualification LIKE '%Graduate%'
            OR j.qualification LIKE '%Any Degree%'
        )"""

    # Filter: location
    if params.get("location") and params["location"] != "all":
        loc = params["location"].strip().lower()
        if loc in ("gujarat", "gujarat_only"):
            query += """ AND (
                j.state = 'Gujarat'
                OR j.district LIKE '%અમદાવાદ%'
                OR j.district LIKE '%વડોદરા%'
                OR j.district LIKE '%કચ્છ%'
                OR j.district LIKE '%મુન્દ્રા%'
                OR j.district LIKE '%ગાંધીનગર%'
                OR j.district LIKE '%ભરૂચ%'
                OR j.district LIKE '%સુરત%'
                OR j.district LIKE '%રાજકોટ%'
                OR j.organization LIKE '%Gujarat%'
                OR j.organization LIKE '%GIFT City%'
            )"""
        elif loc == "remote":
            query += " AND (j.state LIKE '%Remote%' OR j.district LIKE '%Remote%' OR j.title LIKE '%Remote%')"
        elif loc == "metros":
            query += " AND (j.district LIKE '%Bengaluru%' OR j.district LIKE '%Mumbai%' OR j.district LIKE '%Hyderabad%' OR j.district LIKE '%Pune%' OR j.district LIKE '%Noida%' OR j.district LIKE '%Gurugram%' OR j.state = 'All India')"

    # Filter: experience
    if params.get("experience"):
        exp = params["experience"].strip().lower()
        if exp in ("fresher", "0-1"):
            query += " AND (j.experience_level = 'fresher' OR j.experience_level = 'all' OR j.age_min <= 21)"
        elif exp in ("experienced", "2+"):
            query += " AND (j.experience_level = 'experienced' OR j.experience_level = 'all')"

    # Filter: min_ctc
    if params.get("min_ctc"):
        try:
            min_c = float(params["min_ctc"])
            query += " AND j.ctc_lpa >= ?"
            args.append(min_c)
        except Exception:
            pass

    # Filter: q
    if params.get("q"):
        term = f"%{params['q'].strip()}%"
        query += " AND (j.title LIKE ? OR j.organization LIKE ? OR j.tech_stack LIKE ? OR j.department LIKE ? OR j.qualification LIKE ?)"
        args.extend([term, term, term, term, term])

    query += " ORDER BY j.featured DESC, j.ctc_lpa DESC, j.vacancies DESC"
    limit = params.get("limit", 200)
    query += " LIMIT ?"
    args.append(limit)

    cursor.execute(query, args)
    rows = cursor.fetchall()
    results = []
    for r in rows:
        d = dict(r)
        d["days_left"] = calculate_days_left(d["last_date"])
        d["urgency_badge"] = determine_urgency(d["days_left"])
        d["is_bookmarked"] = bool(d["is_bookmarked"])
        results.append(d)
    conn.close()
    return results

def get_corporate_stats() -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()

    base_where = """
    WHERE is_active = 1
      AND (
          job_category IN ('private', 'semi_private', 'global_tech', 'fintech_startup', 'mid_sized', 'psu', 'unicorns', 'it_services', 'bfsi', 'conglomerate', 'auto_ev', 'pharma', 'fmcg', 'gujarat_champions')
          OR board_category IN ('Corporate', 'PSU')
          OR gov_level = 'Private'
          OR organization LIKE '%Adani%'
          OR organization LIKE '%BHEL%'
          OR organization LIKE '%Linde%'
          OR organization LIKE '%Amazon%'
          OR organization LIKE '%Flipkart%'
          OR organization LIKE '%NPCI%'
          OR organization LIKE '%Reliance%'
          OR organization LIKE '%Tata%'
          OR organization LIKE '%L&T%'
      )
    """
    cursor.execute(f"SELECT COUNT(*), COALESCE(SUM(vacancies), 0), COALESCE(MAX(ctc_lpa), 0.0) FROM jobs {base_where};")
    tot_corp_jobs, tot_corp_vac, max_ctc = cursor.fetchone()

    cursor.execute(f"SELECT COUNT(*), COALESCE(SUM(vacancies), 0) FROM jobs {base_where} AND (state = 'Gujarat' OR district LIKE '%અમદાવાદ%' OR district LIKE '%વડોદરા%' OR district LIKE '%મુન્દ્રા%' OR district LIKE '%કચ્છ%' OR district LIKE '%સુરત%' OR district LIKE '%ગાંધીનગર%' OR district LIKE '%ભરૂચ%' OR organization LIKE '%Gujarat%' OR organization LIKE '%GIFT City%');")
    guj_corp_jobs, guj_corp_vac = cursor.fetchone()

    cursor.execute(f"SELECT COUNT(*) FROM jobs {base_where} AND (job_category IN ('semi_private', 'psu') OR organization LIKE '%BHEL%' OR organization LIKE '%Linde%' OR organization LIKE '%NPCI%' OR organization LIKE '%GSFC%' OR organization LIKE '%GNFC%');")
    semi_private_count = cursor.fetchone()[0]

    cursor.execute(f"SELECT COUNT(*) FROM jobs {base_where} AND (job_category = 'conglomerate' OR organization LIKE '%Adani%' OR organization LIKE '%Reliance%' OR organization LIKE '%Tata%' OR organization LIKE '%Larsen%');")
    conglomerate_count = cursor.fetchone()[0]

    cursor.execute(f"SELECT COUNT(*) FROM jobs {base_where} AND (job_category = 'global_tech' OR organization LIKE '%Amazon%' OR organization LIKE '%Flipkart%' OR organization LIKE '%Google%' OR organization LIKE '%Microsoft%');")
    global_tech_count = cursor.fetchone()[0]

    cursor.execute(f"SELECT COUNT(*) FROM jobs {base_where} AND (job_category IN ('unicorns', 'fintech_startup', 'mid_sized') OR organization LIKE '%Swiggy%' OR organization LIKE '%Zomato%' OR organization LIKE '%PhonePe%');")
    unicorns_count = cursor.fetchone()[0]

    cursor.execute(f"SELECT COUNT(*) FROM jobs {base_where} AND (job_category = 'it_services' OR organization LIKE '%TCS%' OR organization LIKE '%Infosys%' OR organization LIKE '%Wipro%' OR organization LIKE '%Cognizant%');")
    it_services_count = cursor.fetchone()[0]

    cursor.execute(f"SELECT COUNT(*) FROM jobs {base_where} AND (job_category = 'bfsi' OR organization LIKE '%HDFC%' OR organization LIKE '%ICICI%' OR organization LIKE '%Axis%');")
    bfsi_count = cursor.fetchone()[0]

    cursor.execute(f"SELECT COUNT(*) FROM jobs {base_where} AND (job_category = 'auto_ev' OR organization LIKE '%Maruti%' OR organization LIKE '%Ola Electric%');")
    auto_ev_count = cursor.fetchone()[0]

    cursor.execute(f"SELECT COUNT(*) FROM jobs {base_where} AND (job_category = 'pharma' OR organization LIKE '%Sun Pharma%' OR organization LIKE '%Zydus%');")
    pharma_count = cursor.fetchone()[0]

    cursor.execute(f"SELECT COUNT(*) FROM jobs {base_where} AND (job_category = 'fmcg' OR organization LIKE '%Hindustan Unilever%' OR organization LIKE '%ITC%');")
    fmcg_count = cursor.fetchone()[0]

    cursor.execute(f"SELECT COUNT(*) FROM jobs {base_where} AND (job_category = 'gujarat_champions' OR organization LIKE '%Torrent Power%' OR organization LIKE '%Nirma%');")
    gujarat_champions_count = cursor.fetchone()[0]

    cursor.execute(f"SELECT COUNT(*) FROM jobs {base_where} AND (is_btech_cse = 1 OR qualification_level IN ('Engineering', 'Graduate') OR qualification LIKE '%Engineering%' OR qualification LIKE '%B.Tech%' OR qualification LIKE '%Graduate%' OR qualification LIKE '%Any Degree%');")
    eligible_count = cursor.fetchone()[0]

    conn.close()
    return {
        "total_corporate_jobs": tot_corp_jobs,
        "total_corporate_vacancies": tot_corp_vac,
        "gujarat_corporate_jobs": guj_corp_jobs,
        "gujarat_corporate_vacancies": guj_corp_vac,
        "semi_private_count": semi_private_count,
        "conglomerate_count": conglomerate_count,
        "global_tech_count": global_tech_count,
        "unicorns_count": unicorns_count,
        "it_services_count": it_services_count,
        "bfsi_count": bfsi_count,
        "auto_ev_count": auto_ev_count,
        "pharma_count": pharma_count,
        "fmcg_count": fmcg_count,
        "gujarat_champions_count": gujarat_champions_count,
        "eligible_count": eligible_count,
        "highest_ctc_lpa": max_ctc
    }

def get_stats() -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*), COALESCE(SUM(vacancies), 0) FROM jobs WHERE is_active = 1;")
    tot_jobs, tot_vacancies = cursor.fetchone()

    cursor.execute("SELECT COUNT(*), COALESCE(SUM(vacancies), 0) FROM jobs WHERE is_active = 1 AND state = 'Gujarat';")
    guj_jobs, guj_vacancies = cursor.fetchone()

    cursor.execute("SELECT COUNT(*), COALESCE(SUM(vacancies), 0) FROM jobs WHERE is_active = 1 AND gov_level = 'Central';")
    cen_jobs, cen_vacancies = cursor.fetchone()

    # B.Tech CSE Stats
    cursor.execute("""
    SELECT COUNT(*), COALESCE(SUM(vacancies), 0)
    FROM jobs
    WHERE is_active = 1 AND (is_btech_cse = 1 OR qualification LIKE '%Computer%' OR qualification LIKE '%B.Tech CSE%' OR qualification LIKE '%IT%');
    """)
    btech_jobs, btech_vacancies = cursor.fetchone()

    # Selection process stats
    cursor.execute("SELECT COUNT(*) FROM jobs WHERE is_active = 1 AND (selection_mode = 'direct_merit' OR selection_process LIKE '%Merit%');")
    direct_merit_jobs = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM jobs WHERE is_active = 1 AND (selection_mode = 'walk_in' OR selection_process LIKE '%Walk-in%');")
    walkin_jobs = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM jobs WHERE is_active = 1 AND (selection_mode = 'apprenticeship' OR board_category = 'Apprenticeship' OR title LIKE '%Apprentice%');")
    apprentice_jobs = cursor.fetchone()[0]

    now_date = datetime.now().strftime("%Y-%m-%d")
    soon_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    cursor.execute("SELECT COUNT(*) FROM jobs WHERE is_active = 1 AND last_date >= ? AND last_date <= ?;", (now_date, soon_date))
    closing_soon = cursor.fetchone()[0]

    cursor.execute("SELECT timestamp FROM scan_logs ORDER BY id DESC LIMIT 1;")
    last_scan = cursor.fetchone()
    last_scan_time = last_scan[0] if last_scan else None

    conn.close()
    return {
        "total_jobs": tot_jobs,
        "total_vacancies": tot_vacancies,
        "gujarat_jobs": guj_jobs,
        "gujarat_vacancies": guj_vacancies,
        "central_jobs": cen_jobs,
        "central_vacancies": cen_vacancies,
        "btech_cse_jobs": btech_jobs,
        "btech_cse_vacancies": btech_vacancies,
        "direct_merit_jobs": direct_merit_jobs,
        "walkin_jobs": walkin_jobs,
        "apprentice_jobs": apprentice_jobs,
        "closing_soon": closing_soon,
        "last_scan_time": last_scan_time
    }

def record_scan_log(source_name: str, jobs_scanned: int, jobs_added: int, jobs_updated: int, duration_seconds: float, status: str, message: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO scan_logs (timestamp, source_name, jobs_scanned, jobs_added, jobs_updated, duration_seconds, status, message)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (datetime.now().isoformat(), source_name, jobs_scanned, jobs_added, jobs_updated, duration_seconds, status, message))
    conn.commit()
    conn.close()

def get_recent_scans(limit: int = 10) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scan_logs ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_subscriber(name: str, email: str, phone: Optional[str] = None, state_pref: str = "Gujarat", preferred_boards: Optional[List[str]] = None) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    import json
    boards_str = json.dumps(preferred_boards or ["OJAS", "GPSC", "SSC"])
    try:
        cursor.execute("""
        INSERT INTO subscribers (name, email, phone, state_pref, preferred_boards, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(email) DO UPDATE SET
            name = excluded.name,
            phone = excluded.phone,
            state_pref = excluded.state_pref,
            preferred_boards = excluded.preferred_boards
        """, (name, email, phone, state_pref, boards_str, datetime.now().isoformat()))
        conn.commit()
        success = True
    except Exception:
        success = False
    conn.close()
    return success
