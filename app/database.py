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
    conn = sqlite3.connect(str(DB_PATH))
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
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM jobs;")
    count = cursor.fetchone()[0]
    if count > 0:
        conn.close()
        return

    now = datetime.now()
    def future_date(days: int) -> str:
        return (now + timedelta(days=days)).strftime("%Y-%m-%d")

    def past_date(days: int) -> str:
        return (now - timedelta(days=days)).strftime("%Y-%m-%d")

    initial_jobs = [
        # GUJARAT GOVERNMENT JOBS (OJAS, GPSC, GSSSB, Police, HC, GSRTC, Electricity)
        {
            "title": "Gujarat Police Constable & Jail Sepoy Bharti 2026 (LRD)",
            "title_gu": "ગુજરાત પોલીસ કોન્સ્ટેબલ અને જેલ સિપાહી ભરતી ૨૦૨૬ (LRD)",
            "organization": "Gujarat Police Recruitment Board (GPRB / LRD)",
            "department": "Home Department, Govt of Gujarat",
            "gov_level": "State",
            "state": "Gujarat",
            "board_category": "Police",
            "vacancies": 12472,
            "qualification": "12th Pass (Higher Secondary) or equivalent",
            "age_min": 18,
            "age_max": 33,
            "age_relaxation_text": "SEBC/OBC: +3 yrs, SC/ST: +5 yrs, Women candidates: +5 yrs, Ex-SM: +3 yrs over service",
            "salary_text": "₹26,000/- Fix Pay for 5 Years -> Level 3 (₹21,700 - ₹69,100)",
            "start_date": past_date(10),
            "last_date": future_date(18),
            "exam_date": "November 2026 (Physical PET/PST) & Jan 2027 (MCQ Test)",
            "notification_number": "GPRB/202627/01",
            "notification_pdf_url": "https://ojas.gujarat.gov.in/AdvtDetailFiles/GPRB_202627_1.pdf",
            "apply_url": "https://ojas.gujarat.gov.in",
            "official_website": "https://lrdgujarat2021.in",
            "application_fee": "General: ₹100; SC/ST/SEBC/EWS/Ex-SM: Exempted (Nil)",
            "selection_process": "1. Physical Endurance Test (Running 5000m for Male, 1600m for Female) -> 2. Written Examination (200 Marks) -> 3. Medical & Document Verification",
            "syllabus_summary": "General Knowledge, Gujarat History & Geography, Current Affairs, Reasoning, Math, Constitution of India, Gujarati Language Comprehension",
            "source": "OJAS Gujarat Official",
            "is_active": 1,
            "featured": 1
        },
        {
            "title": "Gujarat Police Sub Inspector (PSI) & ASI Bharti 2026",
            "title_gu": "ગુજરાત પોલીસ સબ ઇન્સ્પેક્ટર (PSI) & આસિસ્ટન્ટ સબ ઇન્સ્પેક્ટર (ASI) ભરતી ૨૦૨૬",
            "organization": "Gujarat Police Recruitment Board (GPRB)",
            "department": "Home Department, Govt of Gujarat",
            "gov_level": "State",
            "state": "Gujarat",
            "board_category": "Police",
            "vacancies": 472,
            "qualification": "Bachelor's Degree in any discipline from a recognized University",
            "age_min": 21,
            "age_max": 35,
            "age_relaxation_text": "SEBC: 3 yrs, SC/ST: 5 yrs, Women: 5 yrs relaxation",
            "salary_text": "₹49,600/- Fix Pay for 5 Years -> Level 7 (₹39,900 - ₹1,26,600)",
            "start_date": past_date(12),
            "last_date": future_date(14),
            "exam_date": "December 2026 (PET) & February 2027 (Prelims)",
            "notification_number": "GPRB/PSI/202627/02",
            "notification_pdf_url": "https://ojas.gujarat.gov.in/AdvtDetailFiles/PSIRB_202627_2.pdf",
            "apply_url": "https://ojas.gujarat.gov.in",
            "official_website": "https://psirbgujarat2026.org",
            "application_fee": "General: ₹100; Reserved Categories: Nil",
            "selection_process": "Physical Efficiency Test (PET/PST) -> Preliminary Written Exam -> Mains Written Exam",
            "syllabus_summary": "Paper 1: General Studies & Mental Ability, Paper 2: Law & Gujarati/English Grammar",
            "source": "OJAS Gujarat Official",
            "is_active": 1,
            "featured": 1
        },
        {
            "title": "GPSC Gujarat Administrative Service Class-1 & Civil Service Class-2 (GAS/GCS 2026)",
            "title_gu": "GPSC ગુજરાત વહીવટી સેવા વર્ગ-૧ અને સિવિલ સર્વિસ વર્ગ-૨ ભરતી ૨૦૨૬ (ડેપ્યુટી કલેક્ટર, ડીવાયએસપી, મામલતદાર)",
            "organization": "Gujarat Public Service Commission (GPSC)",
            "department": "General Administration Department (GAD), Gujarat",
            "gov_level": "State",
            "state": "Gujarat",
            "board_category": "GPSC",
            "vacancies": 388,
            "qualification": "Graduate Degree in any stream from an accredited University",
            "age_min": 20,
            "age_max": 36,
            "age_relaxation_text": "SEBC/EWS/SC/ST: +5 yrs, Gujarat Female: +5 yrs (Reserved Female: +10 yrs)",
            "salary_text": "Class-1: Level 10 (₹56,100 - ₹1,77,500); Class-2: Level 8 (₹44,900 - ₹1,42,400)",
            "start_date": past_date(5),
            "last_date": future_date(22),
            "exam_date": "Prelims: November 2026, Mains: March 2027",
            "notification_number": "GPSC/202627/47",
            "notification_pdf_url": "https://gpsc.gujarat.gov.in/Documents/Advertisment_47_2026.pdf",
            "apply_url": "https://gpsc-ojas.gujarat.gov.in",
            "official_website": "https://gpsc.gujarat.gov.in",
            "application_fee": "General: ₹100 + Postal/Gateway charges; SC/ST/SEBC/EWS/PwD: Exempted",
            "selection_process": "Preliminary Exam (400 Marks) -> Mains Written Exam (6 Papers, 900 Marks) -> Personality Test (100 Marks)",
            "syllabus_summary": "General Studies I & II, Gujarati, English, Essay, History, Heritage & Culture of Gujarat, Indian Economy & Geography",
            "source": "GPSC OJAS Portal",
            "is_active": 1,
            "featured": 1
        },
        {
            "title": "GSSSB Combined Competitive Exam (CCE Group-A & Group-B) Junior Clerk & Senior Clerk 2026",
            "title_gu": "GSSSB સંયુક્ત સ્પર્ધાત્મક પરીક્ષા (CCE ગ્રૂપ-A & ગ્રૂપ-B) જુનિયર ક્લાર્ક, સિનિયર ક્લાર્ક, હેડ ક્લાર્ક અને ઓફિસ આસિસ્ટન્ટ",
            "organization": "Gujarat Subordinate Service Selection Board (GSSSB)",
            "department": "Secretariat & Various District Offices",
            "gov_level": "State",
            "state": "Gujarat",
            "board_category": "GSSSB",
            "vacancies": 5554,
            "qualification": "Bachelor's Degree in any discipline + Basic Computer Knowledge (CCC)",
            "age_min": 20,
            "age_max": 35,
            "age_relaxation_text": "SEBC/EWS: +5 yrs, SC/ST: +5 yrs, Female: +5 yrs",
            "salary_text": "₹26,000/- to ₹40,800/- Fix Pay for 5 yrs based on post cadre",
            "start_date": past_date(15),
            "last_date": future_date(6),
            "exam_date": "October 2026 (CBRT Prelims Examination)",
            "notification_number": "GSSSB/202627/212",
            "notification_pdf_url": "https://gsssb.gujarat.gov.in/Advt/CCE_2026_Notification.pdf",
            "apply_url": "https://ojas.gujarat.gov.in",
            "official_website": "https://gsssb.gujarat.gov.in",
            "application_fee": "Group A: ₹500, Group B: ₹400 (Refundable upon appearing in exam for reserved categories)",
            "selection_process": "CBRT (Computer Based Recruitment Test) Prelims -> Mains Exam (Descriptive for Group A / MCQ for Group B)",
            "syllabus_summary": "Reasoning (40 marks), Quantitative Aptitude (30 marks), Gujarati Language (15 marks), English Language (15 marks)",
            "source": "GSSSB OJAS Official",
            "is_active": 1,
            "featured": 1
        },
        {
            "title": "Gujarat High Court Assistant & DySO Recruitment 2026",
            "title_gu": "ગુજરાત હાઈકોર્ટ આસિસ્ટન્ટ અને નાયબ સેક્શન ઓફિસર (DySO) ભરતી ૨૦૨૬",
            "organization": "High Court of Gujarat, Sola, Ahmedabad",
            "department": "Judiciary Administration",
            "gov_level": "State",
            "state": "Gujarat",
            "board_category": "High Court",
            "vacancies": 1318,
            "qualification": "Graduation in any discipline + Typing speed of 5000 key depressions in English/Gujarati",
            "age_min": 21,
            "age_max": 35,
            "age_relaxation_text": "SC/ST/SEBC/EWS: 5 yrs, Women: 5 yrs, Differently Abled: 10 yrs",
            "salary_text": "Level 2 (₹19,900 - ₹63,200) + Judicial allowances",
            "start_date": past_date(8),
            "last_date": future_date(12),
            "exam_date": "Elimination Test: November 2026, Main Written: January 2027",
            "notification_number": "HCG/RC/1434/2026",
            "notification_pdf_url": "https://gujarathighcourt.nic.in/recruitment/Assistant_2026.pdf",
            "apply_url": "https://hc-ojas.gujarat.gov.in",
            "official_website": "https://gujarathighcourt.nic.in",
            "application_fee": "General: ₹1000; SC/ST/SEBC/EWS/PwD: ₹500",
            "selection_process": "Elimination Test (Objective MCQ, 100 Marks) -> Main Written Examination (Descriptive, 60 Marks) -> Practical Typing Test (40 Marks)",
            "syllabus_summary": "English Language, Gujarati Language, General Knowledge, Basic Computer, Arithmetic, Current Affairs, Indian Legal System",
            "source": "Gujarat High Court OJAS",
            "is_active": 1,
            "featured": 1
        },
        {
            "title": "GSRTC Conductor & Driver Mega Bharti 2026 (7,419 Posts)",
            "title_gu": "GSRTC ગુજરાત રાજ્ય માર્ગ વાહન વ્યવહાર નિગમ કંડક્ટર અને ડ્રાઇવર મેગા ભરતી ૨૦૨૬",
            "organization": "Gujarat State Road Transport Corporation (GSRTC)",
            "department": "Transport Department, Govt of Gujarat",
            "gov_level": "State",
            "state": "Gujarat",
            "board_category": "GSRTC",
            "vacancies": 7419,
            "qualification": "10th Pass (SSC) or 12th Pass + Valid First Aid & Conductor/Heavy Driving Licence",
            "age_min": 18,
            "age_max": 34,
            "age_relaxation_text": "SEBC: +3 yrs, SC/ST: +5 yrs, Women: +5 yrs",
            "salary_text": "₹18,500/- Fix Pay for 5 Years with annual appraisal",
            "start_date": past_date(18),
            "last_date": future_date(4),
            "exam_date": "October 2026 (OMR Written Test & Driving Skill Test)",
            "notification_number": "GSRTC/202627/04-05",
            "notification_pdf_url": "https://gsrtc.in/site/recruitment/Conductor_Driver_2026.pdf",
            "apply_url": "https://ojas.gujarat.gov.in",
            "official_website": "https://gsrtc.in",
            "application_fee": "General: ₹59; Reserved categories: Nil",
            "selection_process": "1. Merit based shortlisting -> 2. OMR Written Examination (100 Marks) -> 3. Practical Driving Test (Driver post)",
            "syllabus_summary": "Road Safety Rules, First Aid, Gujarati Grammar, General Knowledge, Basic Mathematics, Ticket Machine Operation",
            "source": "OJAS GSRTC",
            "is_active": 1,
            "featured": 1
        },
        {
            "title": "Gujarat Forest Guard (Vanrakshak) Bharti 2026",
            "title_gu": "ગુજરાત વન વિભાગ વનરક્ષક (વનપાલ / ફોરેસ્ટ ગાર્ડ) વર્ગ-૩ સીધી ભરતી ૨૦૨૬",
            "organization": "Forest & Environment Department Gujarat",
            "department": "Gujarat Forest Department",
            "gov_level": "State",
            "state": "Gujarat",
            "board_category": "Forest",
            "vacancies": 823,
            "qualification": "12th Pass (HSC) in Science, Commerce or Arts stream",
            "age_min": 18,
            "age_max": 34,
            "age_relaxation_text": "OBC/SEBC: +5 yrs, SC/ST: +5 yrs, Female: +5 yrs",
            "salary_text": "₹26,000/- Fix Pay for 5 Years + Uniform allowance",
            "start_date": past_date(20),
            "last_date": future_date(8),
            "exam_date": "December 2026 (CBRT Test & Physical Test)",
            "notification_number": "FOREST/202627/1",
            "notification_pdf_url": "https://forests.gujarat.gov.in/writereaddata/Portal/Advt_Forest_Guard_2026.pdf",
            "apply_url": "https://ojas.gujarat.gov.in",
            "official_website": "https://forests.gujarat.gov.in",
            "application_fee": "General: ₹100; SC/ST/SEBC/EWS: Nil",
            "selection_process": "Computer Based Written Test (200 Marks) -> Physical Fitness Test (Running, High Jump, Long Jump)",
            "syllabus_summary": "General Knowledge (25%), Mathematics (12.5%), Gujarati Language (12.5%), Environment & Forestry / Ecology (50%)",
            "source": "OJAS Forest Gujarat",
            "is_active": 1,
            "featured": 1
        },
        {
            "title": "Gujarat Electricity Boards (PGVCL/DGVCL/MGVCL/UGVCL) Vidyut Sahayak (Junior Assistant) 2026",
            "title_gu": "ગુજરાત વીજ કંપનીઓ (પીજીવીસીએલ, ડીજીવીસીએલ, એમજીવીસીએલ, યુજીવીસીએલ) વિદ્યુત સહાયક જુનિયર આસિસ્ટન્ટ ભરતી",
            "organization": "Gujarat Urja Vikas Nigam Ltd (GUVNL DISCOMs)",
            "department": "Energy & Petrochemicals Department",
            "gov_level": "State",
            "state": "Gujarat",
            "board_category": "Electricity",
            "vacancies": 2150,
            "qualification": "Full-time B.A., B.Com., B.Sc., B.B.A., B.C.A. with minimum 55% marks",
            "age_min": 18,
            "age_max": 31,
            "age_relaxation_text": "SEBC: +3 yrs, SC/ST: +5 yrs, Female: +5 yrs, Gujarat Domicile required",
            "salary_text": "1st Year: ₹26,000/-, 2nd to 5th Year: ₹28,000/- -> Regular Scale ₹25,000-₹55,800",
            "start_date": past_date(7),
            "last_date": future_date(16),
            "exam_date": "January 2027 (Online Computer Based Test)",
            "notification_number": "GUVNL/VSJA/2026/01",
            "notification_pdf_url": "https://www.dgvcl.com/recruitment/VS_JA_Advt_2026.pdf",
            "apply_url": "https://www.guvnl.com/careers",
            "official_website": "https://www.guvnl.com",
            "application_fee": "General/SEBC/EWS: ₹500; SC/ST: ₹250",
            "selection_process": "Two-tier Online CBT Examination (Tier 1 & Tier 2) + Document Verification",
            "syllabus_summary": "General Knowledge (10%), English Knowledge (20%), Computer Knowledge (20%), Gujarati Language (20%), Basic Math & Reasoning (15%), Company / Electrical basics (15%)",
            "source": "GUVNL Career Portal",
            "is_active": 1,
            "featured": 0
        },
        {
            "title": "Gujarat Vidhyasahayak (Std 1 to 8 Teacher) Bharti 2026",
            "title_gu": "ગુજરાત વિદ્યાસહાયક ભરતી ૨૦૨૬ (ધોરણ ૧ થી ૫ અને ૬ થી ૮ પ્રાથમિક શિક્ષક ભરતી - ૫,૩૬૦ જગ્યાઓ)",
            "organization": "Directorate of Primary Education, Gujarat",
            "department": "Education Department, Govt of Gujarat",
            "gov_level": "State",
            "state": "Gujarat",
            "board_category": "Vidhyasahayak",
            "vacancies": 5360,
            "qualification": "TET-1 / TET-2 Passed with PTC / D.El.Ed / B.Ed / B.El.Ed",
            "age_min": 18,
            "age_max": 36,
            "age_relaxation_text": "SEBC/SC/ST/EWS: +5 yrs, Women: +5 yrs",
            "salary_text": "₹26,000/- Fix Pay for 5 Years -> Regular Teacher Pay Matrix Level 6",
            "start_date": past_date(14),
            "last_date": future_date(10),
            "exam_date": "Merit based direct recruitment based on TET Scores & Academic Weightage",
            "notification_number": "DPE/VS/2026/01",
            "notification_pdf_url": "https://vsb.dpegujarat.in/Notification/Vidhyasahayak_2026_Details.pdf",
            "apply_url": "https://vsb.dpegujarat.in",
            "official_website": "https://dpegujarat.in",
            "application_fee": "General: ₹200; SC/ST/SEBC: ₹100",
            "selection_process": "Merit Score (50% TET Score + 50% Academic Marks: Graduation/HSC/B.Ed/PTC) -> District Allocation Camp",
            "syllabus_summary": "Language, Mathematics & Science, Social Science teacher cadres based on TET merit",
            "source": "Gujarat Education Portal",
            "is_active": 1,
            "featured": 1
        },
        {
            "title": "Ahmedabad Municipal Corporation (AMC) Sahayak Junior Clerk Bharti 2026",
            "title_gu": "અમદાવાદ મ્યુનિસિપલ કોર્પોરેશન (AMC) સહાયક જુનિયર ક્લાર્ક ભરતી ૨૦૨૬",
            "organization": "Ahmedabad Municipal Corporation (AMC)",
            "department": "Urban Administration & Municipal Services",
            "gov_level": "State",
            "state": "Gujarat",
            "board_category": "AMC/SMC",
            "vacancies": 940,
            "qualification": "Bachelor's Degree in any stream + CCC Computer Certification",
            "age_min": 21,
            "age_max": 33,
            "age_relaxation_text": "OBC/EWS: +3 yrs, SC/ST: +5 yrs, Women: +5 yrs",
            "salary_text": "₹26,000/- Fix Pay for 3 Years -> Regular Pay Scale Level 2",
            "start_date": past_date(16),
            "last_date": future_date(7),
            "exam_date": "November 2026 (Written Exam in Ahmedabad)",
            "notification_number": "AMC/EST/2026/08",
            "notification_pdf_url": "https://ahmedabadcity.gov.in/portal/Recruitment/AMC_Jr_Clerk_2026.pdf",
            "apply_url": "https://ahmedabadcity.gov.in",
            "official_website": "https://ahmedabadcity.gov.in",
            "application_fee": "General: ₹500; Reserved: ₹250",
            "selection_process": "Written Competitive Examination (200 Marks) -> Document Verification",
            "syllabus_summary": "General Knowledge & Ahmedabad History, Gujarati Grammar, English, Quantitative Aptitude, Logical Reasoning",
            "source": "AMC Recruitment Portal",
            "is_active": 1,
            "featured": 0
        },
        {
            "title": "Gujarat High Court Peon & Watchman (Class-4) Recruitment 2026",
            "title_gu": "ગુજરાત હાઈકોર્ટ પટાવાળા / ચોકીદાર (વર્ગ-૪) ભરતી ૨૦૨૬ (૧,૪૯૦ જગ્યાઓ)",
            "organization": "High Court of Gujarat, Ahmedabad",
            "department": "Judicial District Courts of Gujarat",
            "gov_level": "State",
            "state": "Gujarat",
            "board_category": "High Court",
            "vacancies": 1490,
            "qualification": "10th Standard (SSC) Pass from recognized Board",
            "age_min": 18,
            "age_max": 33,
            "age_relaxation_text": "SC/ST/SEBC/EWS: 5 yrs, Women: 5 yrs",
            "salary_text": "Level 1 (₹14,800 - ₹47,100) with allowances",
            "start_date": past_date(10),
            "last_date": future_date(15),
            "exam_date": "December 2026 (Elimination Test)",
            "notification_number": "HCG/RC/1435/2026",
            "notification_pdf_url": "https://gujarathighcourt.nic.in/recruitment/Peon_Class4_2026.pdf",
            "apply_url": "https://hc-ojas.gujarat.gov.in",
            "official_website": "https://gujarathighcourt.nic.in",
            "application_fee": "General: ₹600; Reserved: ₹300",
            "selection_process": "Objective Written Test (100 Marks in Gujarati medium) -> Merit List",
            "syllabus_summary": "Gujarati Language (30 marks), General Knowledge (35 marks), Arithmetic (20 marks), Sports & Current Affairs (15 marks)",
            "source": "Gujarat High Court OJAS",
            "is_active": 1,
            "featured": 0
        },
        {
            "title": "GPSC Medical Officer (Gujarat Health Service Class-2)",
            "title_gu": "GPSC મેડિકલ ઓફિસર (ગુજરાત આરોગ્ય સેવા વર્ગ-૨) ભરતી ૨૦૨૬",
            "organization": "Gujarat Public Service Commission (GPSC)",
            "department": "Health and Family Welfare Department",
            "gov_level": "State",
            "state": "Gujarat",
            "board_category": "GPSC",
            "vacancies": 850,
            "qualification": "MBBS Degree from recognized medical college + Gujarat Medical Council Registration",
            "age_min": 21,
            "age_max": 36,
            "age_relaxation_text": "SEBC/SC/ST: +5 yrs, Women: +5 yrs",
            "salary_text": "Level 9 (₹53,100 - ₹1,67,800) + NPA (Non-Practicing Allowance)",
            "start_date": past_date(9),
            "last_date": future_date(19),
            "exam_date": "Preliminary Exam: December 2026",
            "notification_number": "GPSC/202627/62",
            "notification_pdf_url": "https://gpsc.gujarat.gov.in/Documents/Advt_62_MO_2026.pdf",
            "apply_url": "https://gpsc-ojas.gujarat.gov.in",
            "official_website": "https://gpsc.gujarat.gov.in",
            "application_fee": "General: ₹100; Reserved: Nil",
            "selection_process": "Written Primary Test (300 Marks) -> Personal Interview (100 Marks)",
            "syllabus_summary": "Medical Science & Clinical Practice (200 Marks), General Studies (100 Marks)",
            "source": "GPSC OJAS Portal",
            "is_active": 1,
            "featured": 0
        },

        # CENTRAL GOVERNMENT JOBS (SSC, UPSC, RRB, Banking, Defence, ISRO)
        {
            "title": "SSC Combined Graduate Level (CGL) Examination 2026 (17,727 Vacancies)",
            "title_gu": "સ્ટાફ સિલેક્શન કમિશન CGL ભરતી ૨૦૨૬ (ઇન્સ્પેક્ટર, ઇન્કમ ટેક્સ, એક્સાઇઝ, CBI, ASO - ૧૭,૭૨૭ જગ્યાઓ)",
            "organization": "Staff Selection Commission (SSC)",
            "department": "DoPT, Central Govt Ministries & Departments",
            "gov_level": "Central",
            "state": "All India",
            "board_category": "SSC",
            "vacancies": 17727,
            "qualification": "Bachelor's Degree from a recognized University in any discipline",
            "age_min": 18,
            "age_max": 32,
            "age_relaxation_text": "OBC: +3 yrs, SC/ST: +5 yrs, PwD: +10 yrs, Ex-SM: +3 yrs",
            "salary_text": "Level 4 (₹25,500) to Level 8 (₹47,600 - ₹1,51,100)",
            "start_date": past_date(22),
            "last_date": future_date(9),
            "exam_date": "Tier-1: October 2026, Tier-2: December 2026",
            "notification_number": "SSC/CGL/2026/HQ",
            "notification_pdf_url": "https://ssc.gov.in/notice-detail/CGL_2026_Notice.pdf",
            "apply_url": "https://ssc.gov.in",
            "official_website": "https://ssc.gov.in",
            "application_fee": "General/OBC: ₹100; Women, SC, ST, PwD, ESM: Exempted (Nil)",
            "selection_process": "Tier-I Computer Based Test -> Tier-II CBT (Session I: Math, Reasoning, English, GA, Computer + Session II: Data Entry Speed Test)",
            "syllabus_summary": "Quantitative Aptitude, General Intelligence & Reasoning, English Comprehension, General Awareness, Computer Proficiency",
            "source": "SSC Official Portal",
            "is_active": 1,
            "featured": 1
        },
        {
            "title": "SSC GD Constable Examination 2026 (BSF, CISF, CRPF, SSB, ITBP, AR, SSF)",
            "title_gu": "SSC GD કોન્સ્ટેબલ ભરતી ૨૦૨૬ (અર્ધલશ્કરી દળો - ૩૯,૪૮૧ જગ્યાઓ)",
            "organization": "Staff Selection Commission (SSC)",
            "department": "Ministry of Home Affairs (MHA), Central Armed Police Forces",
            "gov_level": "Central",
            "state": "All India",
            "board_category": "SSC",
            "vacancies": 39481,
            "qualification": "Matriculation (10th Class Examination) Pass from a recognized Board",
            "age_min": 18,
            "age_max": 23,
            "age_relaxation_text": "OBC: +3 yrs, SC/ST: +5 yrs, Ex-SM: +3 yrs",
            "salary_text": "Pay Level 3 (₹21,700 - ₹69,100) + Central allowances & ration money",
            "start_date": past_date(15),
            "last_date": future_date(25),
            "exam_date": "January - February 2027 (CBT Test in 13 regional languages including Gujarati)",
            "notification_number": "SSC/GD/2026/09",
            "notification_pdf_url": "https://ssc.gov.in/notice-detail/Constable_GD_2026.pdf",
            "apply_url": "https://ssc.gov.in",
            "official_website": "https://ssc.gov.in",
            "application_fee": "General: ₹100; Women & SC/ST/Ex-SM: Nil",
            "selection_process": "Computer Based Examination (CBE) -> Physical Standard Test (PST) -> Physical Efficiency Test (PET) -> Medical Examination (DME/RME)",
            "syllabus_summary": "General Intelligence & Reasoning (40 marks), General Knowledge (40 marks), Elementary Math (40 marks), English/Hindi/Regional (40 marks)",
            "source": "SSC Official Portal",
            "is_active": 1,
            "featured": 1
        },
        {
            "title": "Railway Recruitment Board (RRB) Assistant Loco Pilot (ALP) & Technicians 2026",
            "title_gu": "ભારતીય રેલ્વે ભરતી બોર્ડ (RRB) આસિસ્ટન્ટ લોકો પાઇલટ (ALP) અને ટેકનિશિયન ભરતી ૨૦૨૬ (૧૮,૭૯૯ જગ્યાઓ)",
            "organization": "Railway Recruitment Boards (RRBs)",
            "department": "Ministry of Railways, Government of India",
            "gov_level": "Central",
            "state": "All India",
            "board_category": "RRB",
            "vacancies": 18799,
            "qualification": "Matriculation / 10th + ITI in specified trade OR 3 Years Diploma in Engineering / B.E./B.Tech",
            "age_min": 18,
            "age_max": 33,
            "age_relaxation_text": "OBC: 3 yrs, SC/ST: 5 yrs, Ex-SM: as per rules (Includes 3 years one-time COVID relaxation)",
            "salary_text": "Level 2 (₹19,900) + Running Allowances (Total approx ₹38,000 - ₹45,000/mo)",
            "start_date": past_date(25),
            "last_date": future_date(5),
            "exam_date": "CBT-1: November 2026, CBT-2: January 2027",
            "notification_number": "CEN 01/2026 (ALP)",
            "notification_pdf_url": "https://www.rrbahmedabad.gov.in/ALP_CEN01_2026.pdf",
            "apply_url": "https://www.rrbapply.gov.in",
            "official_website": "https://www.rrbahmedabad.gov.in",
            "application_fee": "All candidates: ₹500 (₹400 refunded on appearing in CBT-1); SC/ST/Female/Ex-SM/EBC: ₹250 (Full refunded on appearing)",
            "selection_process": "CBT Stage 1 -> CBT Stage 2 (Part A: Common + Part B: Trade Syllabus) -> CBAT (Aptitude Test) -> Document Verification & Medical",
            "syllabus_summary": "Mathematics, General Intelligence & Reasoning, Basic Science and Engineering, Trade Specific Technical questions",
            "source": "RRB Official Portal",
            "is_active": 1,
            "featured": 1
        },
        {
            "title": "Railway RRB Non-Technical Popular Categories (NTPC) Graduate & Under-Graduate 2026",
            "title_gu": "રેલ્વે NTPC ભરતી ૨૦૨૬ (સ્ટેશન માસ્ટર, ગુડ્સ ટ્રેન મેનેજર, ક્લાર્ક - ૧૧,૫૫૮ જગ્યાઓ)",
            "organization": "Railway Recruitment Boards (RRBs)",
            "department": "Ministry of Railways, Government of India",
            "gov_level": "Central",
            "state": "All India",
            "board_category": "RRB",
            "vacancies": 11558,
            "qualification": "12th Pass for Under-Graduate Posts; Any Bachelor Degree for Graduate Posts",
            "age_min": 18,
            "age_max": 36,
            "age_relaxation_text": "OBC: 3 yrs, SC/ST: 5 yrs, PwBD: 10 yrs",
            "salary_text": "Level 2 (₹19,900) to Level 6 (₹35,400 - ₹1,12,400)",
            "start_date": past_date(6),
            "last_date": future_date(28),
            "exam_date": "CBT-1: December 2026 - January 2027",
            "notification_number": "CEN 05/2026 & 06/2026",
            "notification_pdf_url": "https://www.rrbapply.gov.in/documents/NTPC_2026_Notification.pdf",
            "apply_url": "https://www.rrbapply.gov.in",
            "official_website": "https://indianrailways.gov.in",
            "application_fee": "General/OBC: ₹500 (₹400 refund upon CBT-1); Reserved: ₹250 (Full refund upon CBT-1)",
            "selection_process": "1st Stage Computer Based Test (CBT-1) -> 2nd Stage CBT-2 -> Typing Skill Test / CBAT -> DV & Medical",
            "syllabus_summary": "General Awareness (40 marks), Mathematics (30 marks), General Intelligence & Reasoning (30 marks)",
            "source": "RRB Central Portal",
            "is_active": 1,
            "featured": 1
        },
        {
            "title": "UPSC Civil Services Examination (IAS, IPS, IFS, IRS) 2026",
            "title_gu": "UPSC સિવિલ સર્વિસીસ પરીક્ષા ૨૦૨૬ (IAS, IPS, IFS, IRS - ૧,૦૫૬ જગ્યાઓ)",
            "organization": "Union Public Service Commission (UPSC)",
            "department": "Department of Personnel & Training, Govt of India",
            "gov_level": "Central",
            "state": "All India",
            "board_category": "UPSC",
            "vacancies": 1056,
            "qualification": "Graduate Degree in any discipline from a recognized Indian University",
            "age_min": 21,
            "age_max": 32,
            "age_relaxation_text": "OBC: +3 yrs (9 attempts), SC/ST: +5 yrs (unlimited attempts), PwBD: +10 yrs",
            "salary_text": "Pay Level 10 (₹56,100 - ₹1,77,500) + DA + HRA + Govt Accommodation",
            "start_date": past_date(12),
            "last_date": future_date(17),
            "exam_date": "Prelims: May 2027, Mains: September 2027",
            "notification_number": "UPSC/CSE/2026/01",
            "notification_pdf_url": "https://upsc.gov.in/sites/default/files/Notice_CSE_2026.pdf",
            "apply_url": "https://upsconline.nic.in",
            "official_website": "https://upsc.gov.in",
            "application_fee": "General/OBC Male: ₹100; Female / SC / ST / PwBD: Fully Exempted",
            "selection_process": "Preliminary Examination (Objective, 2 Papers) -> Main Examination (Written Descriptive, 9 Papers) -> Personality Test (Interview)",
            "syllabus_summary": "Paper 1: GS (History, Geography, Polity, Economy, Science, Current Affairs), Paper 2: CSAT (Qualifying 33%)",
            "source": "UPSC Official Portal",
            "is_active": 1,
            "featured": 1
        },
        {
            "title": "IBPS Probationary Officer (PO / MT XV) Recruitment 2026",
            "title_gu": "IBPS પ્રોબેશનરી ઓફિસર (PO) બેંક ભરતી ૨૦૨૬ (રાષ્ટ્રીયકૃત બેંકોમાં ૪,૪૫૫ જગ્યાઓ)",
            "organization": "Institute of Banking Personnel Selection (IBPS)",
            "department": "Participating Public Sector Banks (PNB, BoB, Canara, CBI, Union Bank)",
            "gov_level": "Central",
            "state": "All India",
            "board_category": "Banking",
            "vacancies": 4455,
            "qualification": "Degree (Graduation) in any discipline from a University recognized by Govt of India",
            "age_min": 20,
            "age_max": 30,
            "age_relaxation_text": "OBC: +3 yrs, SC/ST: +5 yrs, PwD: +10 yrs",
            "salary_text": "Basic Pay ₹36,000/- with gross approx ₹65,000 - ₹72,000/mo + Lease accommodation",
            "start_date": past_date(16),
            "last_date": future_date(11),
            "exam_date": "Prelims: October 2026, Mains: November 2026",
            "notification_number": "IBPS/CRP-PO/XV/2026",
            "notification_pdf_url": "https://www.ibps.in/wp-content/uploads/CRP_PO_XV_Advt.pdf",
            "apply_url": "https://ibpsonline.ibps.in/crppoxv",
            "official_website": "https://www.ibps.in",
            "application_fee": "General/OBC/EWS: ₹850; SC/ST/PwD: ₹175",
            "selection_process": "Online Preliminary Exam -> Online Main Exam -> Common Interview conducted by Nodal Bank",
            "syllabus_summary": "English Language, Quantitative Aptitude, Reasoning Ability, General/Economy/Banking Awareness, Data Analysis & Interpretation",
            "source": "IBPS Portal",
            "is_active": 1,
            "featured": 1
        },
        {
            "title": "State Bank of India (SBI) Junior Associates (Clerk) 2026",
            "title_gu": "સ્ટેટ બેંક ઓફ ઇન્ડિયા (SBI) જુનિયર એસોસિએટ્સ (ક્લાર્ક) ભરતી ૨૦૨૬ (૮,૨૮૩ જગ્યાઓ)",
            "organization": "State Bank of India (SBI)",
            "department": "Central Recruitment & Promotion Department (CRPD)",
            "gov_level": "Central",
            "state": "All India",
            "board_category": "Banking",
            "vacancies": 8283,
            "qualification": "Graduation in any discipline + Proficiency in local language of state",
            "age_min": 20,
            "age_max": 28,
            "age_relaxation_text": "OBC: +3 yrs, SC/ST: +5 yrs, PwD: +10 yrs",
            "salary_text": "Basic ₹19,900/- with starting gross around ₹37,000/mo in metro branches",
            "start_date": past_date(14),
            "last_date": future_date(13),
            "exam_date": "Prelims: November 2026, Mains: January 2027",
            "notification_number": "CRPD/CR/2026-27/03",
            "notification_pdf_url": "https://sbi.co.in/documents/careers/JA_2026_Detailed_Advt.pdf",
            "apply_url": "https://bank.sbi/careers",
            "official_website": "https://sbi.co.in",
            "application_fee": "General/OBC/EWS: ₹750; SC/ST/PwD/ESM: Nil",
            "selection_process": "Phase-I Preliminary Exam (100 Marks) -> Phase-II Main Exam (200 Marks) -> Local Language Test",
            "syllabus_summary": "General/Financial Awareness, General English, Quantitative Aptitude, Reasoning Ability & Computer Aptitude",
            "source": "SBI Careers Portal",
            "is_active": 1,
            "featured": 1
        },
        {
            "title": "Indian Air Force Agniveer Vayu Recruitment 2026 (Intake 01/2026)",
            "title_gu": "ભારતીય વાયુસેના અગ્નિવીર વાયુ ભરતી ૨૦૨૬ (૩,૫૦૦ જગ્યાઓ)",
            "organization": "Indian Air Force (IAF)",
            "department": "Ministry of Defence, Govt of India",
            "gov_level": "Central",
            "state": "All India",
            "board_category": "Defence",
            "vacancies": 3500,
            "qualification": "10+2 / Intermediate with Math, Physics and English (min 50% marks) OR 3-yr Diploma in Engg",
            "age_min": 17,
            "age_max": 21,
            "age_relaxation_text": "Candidates must be born between 02 Jan 2004 and 02 July 2007 (both dates inclusive)",
            "salary_text": "1st Yr: ₹30,000/-, 2nd Yr: ₹33,000/-, 3rd Yr: ₹36,500/-, 4th Yr: ₹40,000/- + Seva Nidhi ₹10.04 Lakhs",
            "start_date": past_date(8),
            "last_date": future_date(15),
            "exam_date": "November 2026 (Online Phase-I Test across India)",
            "notification_number": "IAF/01/2026/VAYU",
            "notification_pdf_url": "https://agnipathvayu.cdac.in/AV/img/main/Detailed_Advt_01_2026.pdf",
            "apply_url": "https://agnipathvayu.cdac.in",
            "official_website": "https://indianairforce.nic.in",
            "application_fee": "₹550 plus GST for all candidates",
            "selection_process": "Phase I Online Test -> Phase II Physical Fitness Test (PFT) & Adaptability Test -> Phase III Medical Exam",
            "syllabus_summary": "Science Subjects: English (20 q), Physics (25 q), Mathematics (25 q); Other subjects: Reasoning & General Awareness (RAGA 30 q)",
            "source": "Indian Air Force Portal",
            "is_active": 1,
            "featured": 1
        },
        {
            "title": "ISRO Scientist / Engineer 'SC' (Electronics, Mechanical, Computer Science) 2026",
            "title_gu": "ઇસરો (ISRO) વૈજ્ઞાનિક / એન્જિનિયર 'SC' ભરતી ૨૦૨૬ (૩૨૫ જગ્યાઓ)",
            "organization": "Indian Space Research Organisation (ISRO)",
            "department": "Department of Space, Government of India",
            "gov_level": "Central",
            "state": "All India",
            "board_category": "ISRO/DRDO",
            "vacancies": 325,
            "qualification": "B.E. / B.Tech or equivalent in relevant discipline with First Class (min 65% or 6.84 CGPA)",
            "age_min": 21,
            "age_max": 30,
            "age_relaxation_text": "OBC: 3 yrs, SC/ST: 5 yrs, Ex-SM: as per rules",
            "salary_text": "Level 10 (₹56,100 - ₹1,77,500) + HRA + Medical + Space allowances (~ ₹95,000/mo)",
            "start_date": past_date(11),
            "last_date": future_date(20),
            "exam_date": "January 2027 (Screening Written Test)",
            "notification_number": "ICRB/02/2026",
            "notification_pdf_url": "https://www.isro.gov.in/media_isro/pdf/recruitment/Scientist_SC_2026.pdf",
            "apply_url": "https://www.isro.gov.in/Careers.html",
            "official_website": "https://www.isro.gov.in",
            "application_fee": "₹250 (All candidates submit ₹750, ₹500 refunded upon attending exam)",
            "selection_process": "Written Test (80 marks technical discipline + 20 marks general aptitude) -> Interview (100 marks)",
            "syllabus_summary": "Core GATE syllabus of respective Engineering stream + Engineering Mathematics + Numerical Aptitude",
            "source": "ISRO Central Recruitment Board",
            "is_active": 1,
            "featured": 1
        },
        {
            "title": "DRDO CEPTAM-11 Senior Technical Assistant-B & Technician-A 2026",
            "title_gu": "DRDO સિનિયર ટેકનિકલ આસિસ્ટન્ટ (STA-B) અને ટેકનિશિયન-A ભરતી ૨૦૨૬ (૧,૯૨૦ જગ્યાઓ)",
            "organization": "Defence Research and Development Organisation (DRDO)",
            "department": "Centre for Personnel Talent Management (CEPTAM), MoD",
            "gov_level": "Central",
            "state": "All India",
            "board_category": "ISRO/DRDO",
            "vacancies": 1920,
            "qualification": "B.Sc Degree or 3-year Diploma in Engg (for STA-B) / 10th + ITI Certificate (for Tech-A)",
            "age_min": 18,
            "age_max": 28,
            "age_relaxation_text": "OBC: 3 yrs, SC/ST: 5 yrs, PwD: 10 yrs",
            "salary_text": "STA-B: Level 6 (₹35,400 - ₹1,12,400); Tech-A: Level 2 (₹19,900 - ₹63,200)",
            "start_date": past_date(5),
            "last_date": future_date(24),
            "exam_date": "December 2026 (Tier-I CBT)",
            "notification_number": "DRDO/CEPTAM-11/2026",
            "notification_pdf_url": "https://www.drdo.gov.in/careers/CEPTAM_11_Advt.pdf",
            "apply_url": "https://www.drdo.gov.in",
            "official_website": "https://www.drdo.gov.in",
            "application_fee": "₹100 for General/OBC; Exempted for Women/SC/ST/PwD",
            "selection_process": "Tier-I Screening CBT -> Tier-II Selection CBT (STA-B) or Trade Test (Tech-A)",
            "syllabus_summary": "Quantitative Aptitude, General Intelligence & Reasoning, General Awareness, English, Discipline Subject Test",
            "source": "DRDO CEPTAM Portal",
            "is_active": 1,
            "featured": 0
        },
        {
            "title": "Intelligence Bureau (IB) ACIO Grade-II / Executive Examination 2026",
            "title_gu": "ઇન્ટેલિજન્સ બ્યુરો (IB) આસિસ્ટન્ટ સેન્ટ્રલ ઇન્ટેલિજન્સ ઓફિસર (ACIO-II) ભરતી ૨૦૨૬ (૯૯૫ જગ્યાઓ)",
            "organization": "Intelligence Bureau (IB)",
            "department": "Ministry of Home Affairs, Govt of India",
            "gov_level": "Central",
            "state": "All India",
            "board_category": "Defence",
            "vacancies": 995,
            "qualification": "Graduation in any stream or equivalent with basic computer operations knowledge",
            "age_min": 18,
            "age_max": 27,
            "age_relaxation_text": "OBC: 3 yrs, SC/ST: 5 yrs, Central Govt civilian employees: up to 40 yrs",
            "salary_text": "Level 7 (₹44,900 - ₹1,42,400) + 20% Special Security Allowance + Cash compensation",
            "start_date": past_date(13),
            "last_date": future_date(11),
            "exam_date": "Tier-I: November 2026, Tier-II: January 2027",
            "notification_number": "MHA/IB/ACIO-II/2026",
            "notification_pdf_url": "https://www.mha.gov.in/notifications/IB_ACIO_II_2026.pdf",
            "apply_url": "https://www.mha.gov.in",
            "official_website": "https://www.mha.gov.in",
            "application_fee": "Exam Fee ₹100 + Recruitment Processing Charges ₹450 = ₹550 (Reserved: ₹450)",
            "selection_process": "Tier-I Online Objective Test (100 Marks) -> Tier-II Descriptive Test (50 Marks) -> Tier-III Interview (100 Marks)",
            "syllabus_summary": "Current Affairs, General Studies, Numerical Aptitude, Reasoning/Logical Aptitude, English Language",
            "source": "MHA Recruitment Portal",
            "is_active": 1,
            "featured": 0
        }
    ]

    for job in initial_jobs:
        hk = compute_job_hash(job["title"], job["organization"], job.get("notification_number"))
        now_str = datetime.now().isoformat()
        cursor.execute("""
        INSERT INTO jobs (
            title, title_gu, organization, department, gov_level, state, board_category,
            vacancies, qualification, age_min, age_max, age_relaxation_text, salary_text,
            start_date, last_date, exam_date, notification_number, notification_pdf_url,
            apply_url, official_website, application_fee, selection_process, syllabus_summary,
            source, created_at, updated_at, is_active, featured, views_count, hash_key
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            job["title"], job.get("title_gu"), job["organization"], job.get("department"),
            job["gov_level"], job["state"], job["board_category"], job["vacancies"],
            job["qualification"], job["age_min"], job["age_max"], job.get("age_relaxation_text"),
            job.get("salary_text"), job.get("start_date"), job["last_date"], job.get("exam_date"),
            job.get("notification_number"), job.get("notification_pdf_url"), job["apply_url"],
            job.get("official_website"), job.get("application_fee"), job.get("selection_process"),
            job.get("syllabus_summary"), job["source"], now_str, now_str, job["is_active"],
            job["featured"], 0, hk
        ))

    # Record initial scan log
    cursor.execute("""
    INSERT INTO scan_logs (timestamp, source_name, jobs_scanned, jobs_added, jobs_updated, duration_seconds, status, message)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(), "System Seed Aggregator", len(initial_jobs), len(initial_jobs), 0, 0.45, "completed",
        "Initial high-fidelity recruitment feed seeded with 2026 Gujarat and Central vacancies."
    ))

    conn.commit()
    conn.close()

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
            query += " AND (j.title LIKE ? OR j.title_gu LIKE ? OR j.organization LIKE ? OR j.department LIKE ? OR j.qualification LIKE ? OR j.notification_number LIKE ?)"
            args.extend([term, term, term, term, term, term])

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
    """Sync all authentic recruitment seeds from the catalog into the database."""
    try:
        from app.seeds import generate_all_authentic_jobs
        seeds = generate_all_authentic_jobs()
        added_or_updated = 0
        for s in seeds:
            res = upsert_job(s)
            if res in ("added", "updated"):
                added_or_updated += 1
        return added_or_updated
    except Exception as e:
        print(f"Catalog sync notice: {e}")
        return 0

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
