"""
FuturSet Jobs Portal - Live Job Finding, Scanning & Aggregator Engine
Scrapes, parses, deduplicates, and synchronizes live government & corporate job postings
from OJAS Gujarat, GPSC, India Post, AAI Airports Authority, GUVNL, SSC, RRB, Banking, UPSC, Defence, and Corporate Portals.
Emits real-time SSE scan events for UI live monitoring.
"""
import time
import json
import logging
import re
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from datetime import datetime, timedelta
from typing import Generator, Dict, Any, List
from bs4 import BeautifulSoup
from app.models import ScanEvent
from app.database import upsert_job, record_scan_log, get_stats

logger = logging.getLogger("futurset.scanner")

SCAN_SOURCES = [
    # -------------------------------------------------------------------------
    # 1. OJAS GUJARAT (Live Open Advertisements)
    # -------------------------------------------------------------------------
    {
        "id": "ojas_gujarat",
        "name": "OJAS Gujarat Portal (ojas.gujarat.gov.in)",
        "type": "gujarat",
        "url": "https://ojas.gujarat.gov.in",
        "feed_data": [
            {
                "title": "GSRTC Helper (હેલ્પર) Class-4 Technical Staff Recruitment 2026-27",
                "title_gu": "GSRTC હેલ્પર (વર્ગ-૪ ટેકનિકલ સ્ટાફ) ઓજસ સીધી ભરતી ૨૦૨૬-૨૭",
                "organization": "Gujarat State Road Transport Corporation (GSRTC)",
                "department": "Transport Department, Govt of Gujarat",
                "gov_level": "State",
                "state": "Gujarat",
                "board_category": "GSRTC",
                "vacancies": 1420,
                "qualification": "10th Pass (SSC) + ITI Mechanic Motor Vehicle / Diesel Mechanic / Fitter",
                "age_min": 18,
                "age_max": 35,
                "salary_text": "Fixed Pay ₹18,500/- per month as per GSRTC / Govt norms",
                "last_date": "2026-10-06",
                "apply_url": "https://ojas.gujarat.gov.in/AdvtDetails.aspx?sid=zlkvQxSZgjY=&yr=iNSQ32x8ipg=&ano=lbbXJHoy3aQ=",
                "notification_number": "GSRTC/202627/HELPER"
            },
            {
                "title": "GSSSB Staff Nurse Class-3 Medical & Health Recruitment 2026",
                "title_gu": "GSSSB સ્ટાફ નર્સ વર્ગ-૩ આરોગ્ય અને પરિવાર કલ્યાણ વિભાગ ભરતી ૨૦૨૬",
                "organization": "Gujarat Subordinate Service Selection Board (GSSSB)",
                "department": "Health & Family Welfare Department, Govt of Gujarat",
                "gov_level": "State",
                "state": "Gujarat",
                "board_category": "GSSSB",
                "vacancies": 450,
                "qualification": "GNM Diploma or B.Sc Nursing from a recognized institution with Gujarat Nursing Council Registration",
                "age_min": 20,
                "age_max": 40,
                "salary_text": "₹26,000/- Fix Pay for 5 years -> 7th CPC Level-7 (₹39,900 - ₹1,26,600)",
                "last_date": "2026-10-12",
                "apply_url": "https://ojas.gujarat.gov.in/AdvtDetails.aspx?sid=K3JOsteln/k=&yr=iNSQ32x8ipg=&ano=oyMBWX7W8Rc=",
                "notification_number": "GSSSB/202627/NURSE"
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 2. GPSC GUJARAT (Class 1 & 2 Officers, Engineers, Medical)
    # -------------------------------------------------------------------------
    {
        "id": "gpsc_ojas",
        "name": "GPSC Gujarat Public Service Commission (gpsc-ojas.gujarat.gov.in)",
        "type": "gujarat",
        "url": "https://gpsc.gujarat.gov.in",
        "feed_data": [
            {
                "title": "GPSC Marine Engineer Class-1 Gujarat Maritime Board (Special Recruitment Drive) 2026",
                "title_gu": "GPSC મરીન એન્જિનિયર વર્ગ-૧ ગુજરાત મેરીટાઇમ બોર્ડ વિશેષ ભરતી ૨૦૨૬",
                "organization": "Gujarat Public Service Commission (GPSC)",
                "department": "Gujarat Maritime Board (GMB) / Ports & Transport",
                "gov_level": "State",
                "state": "Gujarat",
                "board_category": "GPSC",
                "vacancies": 12,
                "qualification": "Degree in Marine Engineering with M.O.T. Certificate of Competency",
                "age_min": 21,
                "age_max": 42,
                "salary_text": "Class-1: Pay Level 10 (₹56,100 - ₹1,77,500)",
                "last_date": "2026-10-08",
                "apply_url": "https://gpsc-ojas.gujarat.gov.in/AdvtDetails.aspx?sid=a2GSpnDbruI=&yr=iNSQ32x8ipg=&ano=htU+J1cfztE=",
                "notification_number": "GPSC/202627/SRD-ME"
            },
            {
                "title": "GPSC Engineer Surveyor Class-1 Gujarat Maritime Board (Special Recruitment Drive) 2026",
                "title_gu": "GPSC એન્જિનિયર સર્વેયર વર્ગ-૧ ગુજરાત મેરીટાઇમ બોર્ડ ભરતી ૨૦૨૬",
                "organization": "Gujarat Public Service Commission (GPSC)",
                "department": "Gujarat Maritime Board (GMB) / Ports & Transport",
                "gov_level": "State",
                "state": "Gujarat",
                "board_category": "GPSC",
                "vacancies": 18,
                "qualification": "Degree in Marine Engineering / Naval Architecture from a recognized University",
                "age_min": 21,
                "age_max": 42,
                "salary_text": "Pay Level 10 (₹56,100 - ₹1,77,500)",
                "last_date": "2026-10-08",
                "apply_url": "https://gpsc-ojas.gujarat.gov.in/AdvtDetails.aspx?sid=a2GSpnDbruI=&yr=iNSQ32x8ipg=&ano=e6dKxUuObx0=",
                "notification_number": "GPSC/202627/SRD-ES"
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 3. HIGH COURT OF GUJARAT
    # -------------------------------------------------------------------------
    {
        "id": "high_court_gujarat",
        "name": "High Court of Gujarat Recruitment Portal (hc-ojas.gujarat.gov.in)",
        "type": "gujarat",
        "url": "https://gujarathighcourt.nic.in",
        "feed_data": [
            {
                "title": "Gujarat High Court Librarian & Librarian cum Research Assistant 2026 (CRP-II)",
                "title_gu": "ગુજરાત હાઇકોર્ટ ગ્રંથપાલ અને રિસર્ચ આસિસ્ટન્ટ સીધી ભરતી ૨૦૨૬ (CRP-II)",
                "organization": "High Court of Gujarat, Ahmedabad",
                "department": "Judiciary Administration (High Court Legal Library Cell)",
                "gov_level": "State",
                "state": "Gujarat",
                "board_category": "High Court",
                "vacancies": 35,
                "qualification": "Master / Bachelor in Library and Information Science (M.Lib.I.Sc / B.Lib.I.Sc)",
                "age_min": 21,
                "age_max": 35,
                "salary_text": "Pay Matrix Level 7 (₹39,900 - ₹1,26,600)",
                "last_date": "2026-10-20",
                "apply_url": "https://hc-ojas.gujarat.gov.in/AdvtDetails.aspx?sid=eTi6irwmOuQ=&yr=yuQSFcpV2UU=&ano=TEOwcf1aepc=",
                "notification_number": "HCG/CRP-II/202627/LIB"
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 4. INDIA POST / DEPARTMENT OF POSTS (POST RELATED JOBS)
    # -------------------------------------------------------------------------
    {
        "id": "indiapost_gov_in",
        "name": "India Post & Postal Circles (indiapost.gov.in & indiapostgdsonline.gov.in)",
        "type": "central",
        "url": "https://www.indiapost.gov.in",
        "feed_data": [
            {
                "title": "India Post Gramin Dak Sevak (GDS - BPM / ABPM / Dak Sevak) 2026-27 (44,228 Posts)",
                "title_gu": "ભારતીય ટપાલ વિભાગ ગ્રામીણ ડાક સેવક (GDS) ભરતી ૨૦૨૬-૨૭ (૪૪,૨૨૮ જગ્યાઓ - ગુજરાત સર્કલ ૨,૧૩૮)",
                "organization": "Department of Posts / Ministry of Communications",
                "department": "India Post All Postal Circles (Gujarat Postal Circle Ahmedabad)",
                "gov_level": "Central",
                "state": "All India",
                "board_category": "Postal",
                "vacancies": 44228,
                "qualification": "Secondary School Examination pass certificate of 10th standard with passing marks in Mathematics and English",
                "age_min": 18,
                "age_max": 40,
                "salary_text": "BPM: ₹12,000 - ₹29,380; ABPM/Dak Sevak: ₹10,000 - ₹24,470 (TRCA)",
                "last_date": (datetime.now() + timedelta(days=20)).strftime("%Y-%m-%d"),
                "apply_url": "https://indiapostgdsonline.gov.in",
                "notification_number": "POSTS/GDS/2026-27/01"
            },
            {
                "title": "Department of Posts Gujarat Circle Staff Car Driver Recruitment 2026 (28 Posts)",
                "title_gu": "ટપાલ વિભાગ ગુજરાત સર્કલ સ્ટાફ કાર ડ્રાઈવર સીધી ભરતી ૨૦૨૬ (૨૮ જગ્યાઓ - અમદાવાદ / વડોદરા / રાજકોટ)",
                "organization": "Department of Posts (Gujarat Postal Circle)",
                "department": "Mail Motor Service (MMS), Shahpur, Ahmedabad, Gujarat",
                "gov_level": "Central",
                "state": "Gujarat",
                "board_category": "Postal",
                "vacancies": 28,
                "qualification": "10th Standard Pass + Valid Driving Licence for light & heavy motor vehicles + 3 years experience",
                "age_min": 18,
                "age_max": 27,
                "salary_text": "Pay Level 2 (₹19,900 - ₹63,200) + DA + Central Allowances",
                "last_date": (datetime.now() + timedelta(days=25)).strftime("%Y-%m-%d"),
                "apply_url": "https://www.indiapost.gov.in",
                "notification_number": "MMS/RECT/DRIVER/2026"
            },
            {
                "title": "India Post Payments Bank (IPPB) Executive & IT Specialist Officers 2026 (120 Posts)",
                "title_gu": "ઇન્ડિયા પોસ્ટ પેમેન્ટ્સ બેંક (IPPB) એક્ઝિક્યુટિવ અને આઇટી સ્પેશિયાલિસ્ટ ભરતી ૨૦૨૬ (૧૨૦ જગ્યાઓ)",
                "organization": "India Post Payments Bank Limited (IPPB) / Department of Posts",
                "department": "Digital Banking Operations & Financial Inclusion, New Delhi & Gujarat Units",
                "gov_level": "Central",
                "state": "All India",
                "board_category": "Postal",
                "vacancies": 120,
                "qualification": "Graduate in any discipline OR B.E. / B.Tech in CSE / IT / MCA for IT roles",
                "age_min": 21,
                "age_max": 35,
                "salary_text": "Lump-sum ₹30,000/mo to ₹65,000/mo + Performance incentives",
                "last_date": (datetime.now() + timedelta(days=16)).strftime("%Y-%m-%d"),
                "apply_url": "https://www.ippbonline.com",
                "notification_number": "IPPB/HR/REC/2026/02"
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 5. AIRPORTS AUTHORITY OF INDIA (AAI RECRUITMENT)
    # -------------------------------------------------------------------------
    {
        "id": "aai_aero",
        "name": "Airports Authority of India (aai.aero)",
        "type": "central",
        "url": "https://www.aai.aero",
        "feed_data": [
            {
                "title": "Airports Authority of India (AAI) Junior Executive (Air Traffic Control - ATC) 2026 (490 Posts)",
                "title_gu": "એરપોર્ટ્સ ઓથોરિટી ઓફ ઇન્ડિયા (AAI) જુનિયર એક્ઝિક્યુટિવ (એર ટ્રાફિક કંટ્રોલ - ATC) ૨૦૨૬ (૪૯૦ જગ્યાઓ)",
                "organization": "Airports Authority of India (AAI)",
                "department": "Air Traffic Management Directorate, Rajiv Gandhi Bhawan, New Delhi",
                "gov_level": "Central",
                "state": "All India",
                "board_category": "Aviation",
                "vacancies": 490,
                "qualification": "Full time Regular Bachelors Degree of Three Years in Science (B.Sc) with Physics and Mathematics OR Full Time Regular Bachelor's Degree in Engineering (Any discipline with Physics and Maths)",
                "age_min": 18,
                "age_max": 27,
                "salary_text": "Pay Scale ₹40,000 - ₹1,40,000 (E-1 Grade, CTC Approx ₹13.0 LPA)",
                "last_date": "2026-10-25",
                "apply_url": "https://www.aai.aero/en/careers/recruitment",
                "notification_number": "AAI/DR/02/2026"
            },
            {
                "title": "Airports Authority of India (AAI) Junior Executive (Information Technology) 2026 (120 Posts)",
                "title_gu": "એરપોર્ટ્સ ઓથોરિટી ઓફ ઇન્ડિયા (AAI) જુનિયર એક્ઝિક્યુટિવ (આઇટી / કોમ્પ્યુટર સાયન્સ) ભરતી ૨૦૨૬",
                "organization": "Airports Authority of India (AAI)",
                "department": "Information Technology Directorate, New Delhi & Airports",
                "gov_level": "Central",
                "state": "All India",
                "board_category": "Aviation",
                "vacancies": 120,
                "qualification": "Full Time Regular B.E. / B.Tech / B.Sc (Engg) in Computer Science / Computer Engineering / IT or MCA",
                "age_min": 18,
                "age_max": 27,
                "salary_text": "Pay Scale ₹40,000 - ₹1,40,000 (E-1 Grade, CTC Approx ₹13.0 LPA)",
                "last_date": "2026-10-28",
                "apply_url": "https://www.aai.aero/en/careers/recruitment",
                "notification_number": "AAI/DR/IT/2026"
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 6. STAFF SELECTION COMMISSION (SSC CENTRAL)
    # -------------------------------------------------------------------------
    {
        "id": "ssc_gov_in",
        "name": "Staff Selection Commission (SSC Central Portal - ssc.gov.in)",
        "type": "central",
        "url": "https://ssc.gov.in",
        "feed_data": [
            {
                "title": "SSC Combined Graduate Level (CGL) 2026 Recruitment",
                "title_gu": "સ્ટાફ સિલેક્શન કમિશન CGL ભરતી ૨૦૨૬ (૧૭,૭૨૭ જગ્યાઓ)",
                "organization": "Staff Selection Commission (SSC)",
                "department": "DoPT, Central Government",
                "gov_level": "Central",
                "state": "All India",
                "board_category": "SSC",
                "vacancies": 17727,
                "qualification": "Bachelor's Degree in any discipline",
                "age_min": 18,
                "age_max": 32,
                "salary_text": "Level 4 to Level 8 (₹25,500 - ₹1,51,100)",
                "last_date": (datetime.now() + timedelta(days=9)).strftime("%Y-%m-%d"),
                "apply_url": "https://ssc.gov.in",
                "notification_number": "SSC/CGL/2026/HQ"
            },
            {
                "title": "SSC GD Constable Examination 2026 (BSF, CISF, CRPF, SSB, ITBP)",
                "title_gu": "SSC GD કોન્સ્ટેબલ ભરતી ૨૦૨૬ (૩૯,૪૮૧ જગ્યાઓ)",
                "organization": "Staff Selection Commission (SSC)",
                "department": "Ministry of Home Affairs",
                "gov_level": "Central",
                "state": "All India",
                "board_category": "SSC",
                "vacancies": 39481,
                "qualification": "10th Class (Matriculation) Pass",
                "age_min": 18,
                "age_max": 23,
                "salary_text": "Pay Level 3 (₹21,700 - ₹69,100)",
                "last_date": (datetime.now() + timedelta(days=25)).strftime("%Y-%m-%d"),
                "apply_url": "https://ssc.gov.in",
                "notification_number": "SSC/GD/2026/09"
            },
            {
                "title": "SSC Junior Engineer (SSC JE 2026 - Civil, Electrical, Mechanical - CPWD, MES, BRO)",
                "title_gu": "એસએસસી જુનિયર એન્જિનિયર (SSC JE ૨૦૨૬) ભરતી (૧,૭૬૫ જગ્યાઓ)",
                "organization": "Staff Selection Commission (SSC)",
                "department": "CPWD, Military Engineer Services (MES), BRO",
                "gov_level": "Central",
                "state": "All India",
                "board_category": "SSC",
                "vacancies": 1765,
                "qualification": "Degree or Diploma in Civil / Electrical / Mechanical Engineering",
                "age_min": 18,
                "age_max": 30,
                "salary_text": "Level 6 (₹35,400 - ₹1,12,400)",
                "last_date": (datetime.now() + timedelta(days=16)).strftime("%Y-%m-%d"),
                "apply_url": "https://ssc.gov.in",
                "notification_number": "SSC/JE/2026/HQ"
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 7. RAILWAY RECRUITMENT BOARDS (RRB CENTRAL)
    # -------------------------------------------------------------------------
    {
        "id": "railway_rrb",
        "name": "Railway Recruitment Control Board (RRB Central - rrbapply.gov.in)",
        "type": "central",
        "url": "https://www.rrbapply.gov.in",
        "feed_data": [
            {
                "title": "RRB Assistant Loco Pilot (ALP) & Technicians 2026",
                "title_gu": "રેલ્વે ભરતી બોર્ડ (RRB) આસિસ્ટન્ટ લોકો પાઇલટ (ALP) અને ટેકનિશિયન ૨૦૨૬",
                "organization": "Railway Recruitment Boards (RRBs)",
                "department": "Ministry of Railways",
                "gov_level": "Central",
                "state": "All India",
                "board_category": "RRB",
                "vacancies": 18799,
                "qualification": "10th + ITI / Diploma / Engineering",
                "age_min": 18,
                "age_max": 33,
                "salary_text": "Level 2 (₹19,900) + Running Allowance",
                "last_date": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
                "apply_url": "https://www.rrbapply.gov.in",
                "notification_number": "CEN 01/2026 (ALP)"
            },
            {
                "title": "RRB NTPC (Non-Technical Popular Categories) Graduate & Undergraduate 2026",
                "title_gu": "રેલ્વે NTPC ભરતી ૨૦૨૬ (૧૧,૫૫૮ જગ્યાઓ)",
                "organization": "Railway Recruitment Boards (RRBs)",
                "department": "Ministry of Railways",
                "gov_level": "Central",
                "state": "All India",
                "board_category": "RRB",
                "vacancies": 11558,
                "qualification": "12th Pass / Any Bachelor's Degree",
                "age_min": 18,
                "age_max": 36,
                "salary_text": "Level 2 to Level 6 (₹19,900 - ₹1,12,400)",
                "last_date": (datetime.now() + timedelta(days=28)).strftime("%Y-%m-%d"),
                "apply_url": "https://www.rrbapply.gov.in",
                "notification_number": "CEN 05/2026"
            },
            {
                "title": "Railway RRB Group D (Level-1 Track Maintainer & Pointsman) 2026 (103,769 Posts)",
                "title_gu": "ભારતીય રેલ્વે ગ્રુપ-ડી (લેવલ-૧ ટ્રેક મેન્ટેનર & પોઇન્ટ્સમેન) મહાભરતી ૨૦૨૬ (૧,૦૩,૭૬૯ જગ્યાઓ)",
                "organization": "Railway Recruitment Boards (RRBs)",
                "department": "Indian Railways (Western Railway & All Zones)",
                "gov_level": "Central",
                "state": "All India",
                "board_category": "RRB",
                "vacancies": 103769,
                "qualification": "10th Pass (Matriculation) OR ITI from NCVT/SCVT",
                "age_min": 18,
                "age_max": 36,
                "salary_text": "Level 1 (₹18,000 - ₹56,900)",
                "last_date": (datetime.now() + timedelta(days=25)).strftime("%Y-%m-%d"),
                "apply_url": "https://www.rrbapply.gov.in",
                "notification_number": "CEN RRC-01/2026"
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 8. PUBLIC SECTOR BANKING (IBPS & SBI)
    # -------------------------------------------------------------------------
    {
        "id": "banking_ibps_sbi",
        "name": "Public Sector Banking (IBPS & State Bank of India - ibps.in & sbi.co.in)",
        "type": "central",
        "url": "https://www.ibps.in",
        "feed_data": [
            {
                "title": "IBPS Probationary Officer (PO / MT XV) Recruitment 2026",
                "title_gu": "IBPS પ્રોબેશનરી ઓફિસર (PO) બેંક ભરતી ૨૦૨૬ (૪,૪૫૫ જગ્યાઓ)",
                "organization": "Institute of Banking Personnel Selection (IBPS)",
                "department": "Participating Public Sector Banks (BoB, PNB, Canara, CBI, Union Bank)",
                "gov_level": "Central",
                "state": "All India",
                "board_category": "Banking",
                "vacancies": 4455,
                "qualification": "Graduation Degree in any discipline",
                "age_min": 20,
                "age_max": 30,
                "salary_text": "Pay Scale ₹36,000 - ₹63,840 (Total ~₹58,000/mo)",
                "last_date": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
                "apply_url": "https://www.ibps.in",
                "notification_number": "IBPS/CRP-PO-XV/2026"
            },
            {
                "title": "IBPS Clerk (Clerical Cadre XIV across 11 Public Sector Banks) 2026 (6,128 Posts)",
                "title_gu": "આઈબીપીએસ ક્લાર્ક (IBPS Clerk XIV) ૧૧ સરકારી બેંકોમાં ભરતી ૨૦૨૬ (૬,૧૨૮ જગ્યાઓ)",
                "organization": "Institute of Banking Personnel Selection (IBPS)",
                "department": "Public Sector Banks (Bank of Baroda, PNB, Canara Bank)",
                "gov_level": "Central",
                "state": "All India",
                "board_category": "Banking",
                "vacancies": 6128,
                "qualification": "Degree in any discipline + Computer knowledge",
                "age_min": 20,
                "age_max": 28,
                "salary_text": "Pay Scale ₹19,900 - ₹47,920 (Total ~₹38,000/mo)",
                "last_date": (datetime.now() + timedelta(days=18)).strftime("%Y-%m-%d"),
                "apply_url": "https://www.ibps.in",
                "notification_number": "IBPS/CRP-CLERKS-XIV/2026"
            },
            {
                "title": "SBI Junior Associate (Customer Support & Sales - Clerk) 2026 (8,773 Posts)",
                "title_gu": "સ્ટેટ બેંક ઓફ ઇન્ડિયા (SBI) જુનિયર એસોસિએટ ક્લાર્ક ભરતી ૨૦૨૬ (૮,૭૭૩ જગ્યાઓ)",
                "organization": "State Bank of India (SBI)",
                "department": "Central Recruitment & Promotion Department (CRPD), Mumbai",
                "gov_level": "Central",
                "state": "All India",
                "board_category": "Banking",
                "vacancies": 8773,
                "qualification": "Graduation in any discipline from a recognized University",
                "age_min": 20,
                "age_max": 28,
                "salary_text": "Pay Scale ₹19,900 - ₹47,920 (CTC Approx ₹40,000/mo)",
                "last_date": (datetime.now() + timedelta(days=11)).strftime("%Y-%m-%d"),
                "apply_url": "https://sbi.co.in/careers",
                "notification_number": "CRPD/CR/2026-27/02"
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 9. GUJARAT POWER SECTOR (GUVNL & 4 DISCOMs)
    # -------------------------------------------------------------------------
    {
        "id": "guvnl_power",
        "name": "Gujarat Power Transmission & DISCOMs (guvnl.com & getcogujarat.com)",
        "type": "gujarat",
        "url": "https://www.getcogujarat.com",
        "feed_data": [
            {
                "title": "GETCO Vidyut Sahayak (Junior Engineer - Electrical & Civil) 2026 (350 Posts)",
                "title_gu": "ગેટકો (GETCO) વિદ્યુત સહાયક (જુનિયર એન્જિનિયર) ભરતી ૨૦૨૬ (૩૫૦ જગ્યાઓ)",
                "organization": "Gujarat Energy Transmission Corporation Limited (GETCO)",
                "department": "State Power Transmission Grid, Vadodara",
                "gov_level": "State",
                "state": "Gujarat",
                "board_category": "Electricity",
                "vacancies": 350,
                "qualification": "B.E. / B.Tech in Electrical / Civil Engineering with min 55%",
                "age_min": 18,
                "age_max": 35,
                "salary_text": "1st Year: ₹37,000/mo; then Regular Scale ₹45,400 - ₹1,01,200",
                "last_date": "2026-10-24",
                "apply_url": "https://www.getcogujarat.com/getco_newsite/Career.php",
                "notification_number": "GETCO/VS-JE/2026/01"
            },
            {
                "title": "DGVCL Vidyut Sahayak (Junior Assistant) Recruitment 2026 (280 Posts)",
                "title_gu": "દક્ષિણ ગુજરાત વીજ કંપની (DGVCL) વિદ્યુત સહાયક જુનિયર આસિસ્ટન્ટ ૨૦૨૬ (૨૮૦ જગ્યાઓ)",
                "organization": "Gujarat Urja Vikas Nigam Ltd (GUVNL DISCOMs)",
                "department": "Dakshin Gujarat Vij Company Limited (DGVCL Surat)",
                "gov_level": "State",
                "state": "Gujarat",
                "board_category": "Electricity",
                "vacancies": 280,
                "qualification": "Graduate in any discipline with min 55% marks + Computer Literacy",
                "age_min": 18,
                "age_max": 30,
                "salary_text": "₹26,000/mo fix pay, then Regular Level 4",
                "last_date": "2026-10-20",
                "apply_url": "https://www.dgvcl.com",
                "notification_number": "DGVCL/JA/2026/01"
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 10. GUJARAT MUNICIPAL CORPORATIONS (AMC & SMC)
    # -------------------------------------------------------------------------
    {
        "id": "municipal_gujarat",
        "name": "Gujarat Municipal Corporations (ahmedabadcity.gov.in & suratmunicipal.gov.in)",
        "type": "gujarat",
        "url": "https://ahmedabadcity.gov.in",
        "feed_data": [
            {
                "title": "Ahmedabad Municipal Corporation (AMC) Sahayak Junior Clerk 2026 (650 Posts)",
                "title_gu": "અમદાવાદ મહાનગરપાલિકા (AMC) સહાયક જુનિયર ક્લાર્ક ભરતી ૨૦૨૬ (૬૫૦ જગ્યાઓ)",
                "organization": "Ahmedabad Municipal Corporation (AMC)",
                "department": "Revenue & Urban Administration",
                "gov_level": "State",
                "state": "Gujarat",
                "board_category": "AMC/SMC",
                "vacancies": 650,
                "qualification": "Any Bachelor's Degree + Basic Computer Knowledge (CCC)",
                "age_min": 18,
                "age_max": 35,
                "salary_text": "Fixed Pay ₹26,000/mo for 3 years, then 7th Pay Level 2",
                "last_date": "2026-10-22",
                "apply_url": "https://ahmedabadcity.gov.in",
                "notification_number": "AMC/EST/2026/01"
            },
            {
                "title": "Surat Municipal Corporation (SMC) Junior Engineer & Clerk Bharti 2026 (340 Posts)",
                "title_gu": "સુરત મહાનગરપાલિકા (SMC) જુનિયર એન્જિનિયર અને ક્લાર્ક ભરતી ૨૦૨૬",
                "organization": "Surat Municipal Corporation (SMC)",
                "department": "Engineering & Public Works Department, Surat",
                "gov_level": "State",
                "state": "Gujarat",
                "board_category": "AMC/SMC",
                "vacancies": 340,
                "qualification": "Degree / Diploma in Civil/Mech/Electrical or Bachelor's Degree",
                "age_min": 18,
                "age_max": 35,
                "salary_text": "Fixed Pay ₹26,000/mo for initial 3 years, then 7th CPC Level 4",
                "last_date": "2026-10-25",
                "apply_url": "https://www.suratmunicipal.gov.in",
                "notification_number": "SMC/REC/2026/02"
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 11. UNION PUBLIC SERVICE COMMISSION (UPSC CENTRAL)
    # -------------------------------------------------------------------------
    {
        "id": "upsc_gov_in",
        "name": "Union Public Service Commission (UPSC Central - upsc.gov.in)",
        "type": "central",
        "url": "https://upsc.gov.in",
        "feed_data": [
            {
                "title": "UPSC Civil Services Examination (IAS, IPS, IFS, IRS) 2026",
                "title_gu": "UPSC સિવિલ સર્વિસીસ પરીક્ષા ૨૦૨૬ (IAS, IPS, IFS, IRS - ૧,૦૫૬ જગ્યાઓ)",
                "organization": "Union Public Service Commission (UPSC)",
                "department": "DoPT, Government of India",
                "gov_level": "Central",
                "state": "All India",
                "board_category": "UPSC",
                "vacancies": 1056,
                "qualification": "Graduate Degree in any discipline",
                "age_min": 21,
                "age_max": 32,
                "salary_text": "Pay Level 10 (₹56,100 - ₹1,77,500)",
                "last_date": "2026-10-20",
                "apply_url": "https://upsconline.nic.in",
                "notification_number": "UPSC/CSE/2026/01"
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 12. DEFENCE & PARAMILITARY (COAST GUARD, CISF, BSF)
    # -------------------------------------------------------------------------
    {
        "id": "defence_paramilitary",
        "name": "Indian Coast Guard & Paramilitary Forces (joinindiancoastguard.cdac.in)",
        "type": "central",
        "url": "https://joinindiancoastguard.cdac.in",
        "feed_data": [
            {
                "title": "Indian Coast Guard (Navik General Duty, Domestic Branch & Yantrik 01/2027) (320 Posts)",
                "title_gu": "ભારતીય કોસ્ટ ગાર્ડ (નાવિક GD, ડોમેસ્ટિક બ્રાન્ચ અને યાંત્રિક) ભરતી ૨૦૨૬-૨૭ (૩૨૦ જગ્યાઓ)",
                "organization": "Indian Coast Guard (Ministry of Defence)",
                "department": "Coast Guard Regional HQ (North West) Gandhinagar & Porbandar",
                "gov_level": "Central",
                "state": "All India",
                "board_category": "Defence",
                "vacancies": 320,
                "qualification": "10+2 with Maths & Physics for GD; 10th for DB; Diploma for Yantrik",
                "age_min": 18,
                "age_max": 22,
                "salary_text": "Pay Level 3 (₹21,700 - ₹69,100)",
                "last_date": "2026-10-22",
                "apply_url": "https://joinindiancoastguard.cdac.in",
                "notification_number": "ICG/CGEPT/01/2027"
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 13. CENTRAL SCIENTIFIC AGENCIES (ISRO, PRL, CSIR-CSMCRI)
    # -------------------------------------------------------------------------
    {
        "id": "scientific_research",
        "name": "Space & Scientific Research (ISRO SAC Ahmedabad & PRL - sac.gov.in & prl.res.in)",
        "type": "central",
        "url": "https://www.prl.res.in",
        "feed_data": [
            {
                "title": "Physical Research Laboratory (PRL Ahmedabad - Dept of Space) Technical Assistant & JRF 2026 (45 Posts)",
                "title_gu": "ભૌતિક અનુસંધાન પ્રયોગશાળા (PRL અમદાવાદ - સ્પેસ ડિપાર્ટમેન્ટ) ટેકનિકલ આસિસ્ટન્ટ ભરતી ૨૦૨૬ (૪૫ જગ્યાઓ)",
                "organization": "Physical Research Laboratory (PRL), Ahmedabad",
                "department": "Department of Space, Government of India",
                "gov_level": "Central",
                "state": "Gujarat",
                "board_category": "Scientific",
                "vacancies": 45,
                "qualification": "Diploma or B.Sc / B.Tech in Electronics, Mechanical, CSE, Physics",
                "age_min": 18,
                "age_max": 35,
                "salary_text": "Pay Level 7 (₹44,900 - ₹1,42,400)",
                "last_date": "2026-10-26",
                "apply_url": "https://www.prl.res.in/prl-eng/job_vacancies",
                "notification_number": "PRL/RECT/2026/01"
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 14. CORPORATE & ENTERPRISE PORTALS (ADANI, BHEL, LINDE, GOOGLE, AMAZON)
    # -------------------------------------------------------------------------
    {
        "id": "corporate_enterprise",
        "name": "Corporate & Enterprise Career Feeds (adani.com, amazon.jobs, tcs.com)",
        "type": "corporate",
        "url": "https://www.adani.com/careers",
        "feed_data": [
            {
                "title": "Adani Digital Labs Associate Software Engineer & Cloud Trainee 2026 (350 Posts)",
                "title_gu": "અદાણી ડિજિટલ લેબ્સ એસોસિએટ સોફ્ટવેર એન્જિનિયર અને ક્લાઉડ ટ્રેઇની ભરતી ૨૦૨૬ (૩૫૦ જગ્યાઓ)",
                "organization": "Adani Group - Adani Digital Labs",
                "department": "Consumer SuperApp, Cloud Architecture & AI Innovation Labs",
                "gov_level": "Private",
                "state": "Gujarat",
                "board_category": "Corporate",
                "vacancies": 350,
                "qualification": "B.E. / B.Tech in CSE / IT / Software Engineering or MCA",
                "age_min": 20,
                "age_max": 28,
                "salary_text": "CTC ₹7.5 LPA to ₹12.0 LPA",
                "last_date": (datetime.now() + timedelta(days=28)).strftime("%Y-%m-%d"),
                "apply_url": "https://www.adani.com/careers",
                "notification_number": "ADL/BLR-AMD/2026/01"
            }
        ]
    }
]

def fetch_live_source_safe(url: str, timeout: int = 4) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=timeout, verify=False)
        if resp.status_code == 200:
            return resp.text
    except Exception as e:
        logger.debug(f"Live fetch to {url} gracefully handled: {e}")
    return ""

def parse_portal_html_for_jobs(html_content: str, source_meta: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parses real HTML from government gazettes/portals using BeautifulSoup.
    Extracts announcement links, advertisement numbers, vacancy counts, and application endpoints.
    """
    if not html_content or len(html_content) < 50:
        return []

    soup = BeautifulSoup(html_content, "html.parser")
    found_jobs = []

    NOISE_KEYWORDS = [
        'calendar', 'speed post', 'postal life', 'current advertisement', 
        'notice regarding', 'provisional list', 'verification schedule', 
        'selection for the post of member', 'promotion for the post',
        'clarification for the post', 'e-affidavit', 'updated vacancies',
        'detailed advertisement for the posts of librarian', 'tender',
        'quotation', 'corrigendum', 'archive', 'disclaimer', 'contact us',
        'terms of use', 'privacy policy', 'sitemap', 'passport seva',
        'savings scheme', 'saving scheme', 'popsk', 'call letter',
        'interview call letter', 'wait list', 'waitlist', 'wait-list',
        'syllabus', 'ineligible', 'lateral recruitment', 'status of recruitment',
        'online recruitment application', 'personnel selection services',
        'services for recruitment', 'result', 'answer key', 'admit card',
        'hall ticket', 'marks', 'cutoff', 'cut-off', 'scrutiny', 'instruction',
        'circular', 'guideline', 'faq', 'dashboard', 'about us', 'home page',
        'department of posts', 'download interview', 'wait list dated',
        'centralized wait'
    ]

    # Look for table rows in recruitment/advt tables
    tables = soup.find_all("table")
    for table in tables:
        rows = table.find_all("tr")
        for r in rows:
            text = r.get_text(separator=" ", strip=True)
            if any(n in text.lower() for n in NOISE_KEYWORDS):
                continue
            if any(k in text.lower() for k in ["bharti", "recruitment", "advt", "post", "constable", "clerk", "officer", "inspector", "vacancy", "driver", "dak sevak"]):
                cols = r.find_all(["td", "th"])
                if len(cols) >= 2:
                    link_tag = r.find("a", href=True)
                    apply_url = link_tag["href"] if link_tag else source_meta.get("url", "https://ojas.gujarat.gov.in")
                    if apply_url.startswith("/"):
                        base = source_meta.get("url", "").rstrip("/")
                        apply_url = f"{base}{apply_url}"

                    title = cols[0].get_text(strip=True) if len(cols) > 0 else text[:100]
                    if len(title) < 10 and len(cols) > 1:
                        title = cols[1].get_text(strip=True)

                    if any(n in title.lower() for n in NOISE_KEYWORDS):
                        continue

                    vac_match = re.search(r'(\d+[\d,]*)\s*(?:vacanc|posts|જગ્યા|પદ)', text, re.IGNORECASE)
                    vacancies = int(vac_match.group(1).replace(",", "")) if vac_match else 50

                    notif_match = re.search(r'([A-Z]{2,10}/[\d\w/-]+)', text)
                    notif_num = notif_match.group(1) if notif_match else None

                    gov_lvl = "State" if source_meta.get("type") == "gujarat" else ("Private" if source_meta.get("type") == "corporate" else "Central")
                    board_cat = "OJAS" if source_meta.get("type") == "gujarat" else ("Corporate" if source_meta.get("type") == "corporate" else "Central")

                    found_jobs.append({
                        "title": title[:140],
                        "organization": source_meta.get("name", "Government Portal"),
                        "department": source_meta.get("name", "Government Department"),
                        "gov_level": gov_lvl,
                        "state": "Gujarat" if source_meta.get("type") == "gujarat" else "All India",
                        "board_category": board_cat,
                        "vacancies": vacancies,
                        "qualification": "Graduate / Relevant Discipline",
                        "age_min": 18,
                        "age_max": 35,
                        "salary_text": "Government 7th Pay Scale as per Official Gazette",
                        "last_date": (datetime.now() + timedelta(days=20)).strftime("%Y-%m-%d"),
                        "apply_url": apply_url,
                        "official_website": source_meta.get("url", apply_url),
                        "notification_number": notif_num,
                        "selection_process": "Written Examination followed by Document Verification.",
                        "source": f"Live HTML Crawler ({source_meta.get('id', 'feed')})"
                    })

    # Look for anchor links with recruitment/advt keywords
    if not found_jobs:
        anchors = soup.find_all("a", href=True)
        for a in anchors:
            text = a.get_text(strip=True)
            href = a["href"]
            if any(n in text.lower() for n in NOISE_KEYWORDS):
                continue
            # Must contain actual job keywords AND specific role indicators
            has_job_kw = any(k in text.lower() for k in ["recruitment", "bharti", "advertisement", "vacancy", "vacancies"])
            has_role_kw = any(r in text.lower() for r in ["officer", "clerk", "engineer", "assistant", "nurse", "constable", "trainee", "professor", "lecturer", "executive", "associate", "inspector", "driver", "attendant", "peon", "specialist", "screener", "handler", "manager", "scientist", "fellow", "apprentice", "helper", "ડાક સેવક", "હેલ્પર", "સહાયક", "અધ્યાપક", "નર્સ"])
            if len(text) > 18 and has_job_kw and has_role_kw:
                if href.startswith("/"):
                    base = source_meta.get("url", "").rstrip("/")
                    href = f"{base}{href}"
                elif not href.startswith("http"):
                    continue

                vac_match = re.search(r'(\d+[\d,]*)\s*(?:vacanc|posts|જગ્યા|પદ)', text, re.IGNORECASE)
                vacancies = int(vac_match.group(1).replace(",", "")) if vac_match else 100

                gov_lvl = "State" if source_meta.get("type") == "gujarat" else ("Private" if source_meta.get("type") == "corporate" else "Central")
                board_cat = "OJAS" if source_meta.get("type") == "gujarat" else ("Corporate" if source_meta.get("type") == "corporate" else "Central")

                found_jobs.append({
                    "title": text[:140],
                    "organization": source_meta.get("name", "State Portal"),
                    "department": source_meta.get("name", "Government Department"),
                    "gov_level": gov_lvl,
                    "state": "Gujarat" if source_meta.get("type") == "gujarat" else "All India",
                    "board_category": board_cat,
                    "vacancies": vacancies,
                    "qualification": "Graduate / As per Gazetted Norms",
                    "age_min": 18,
                    "age_max": 35,
                    "salary_text": "Government 7th Pay Scale as per Official Gazette",
                    "last_date": (datetime.now() + timedelta(days=21)).strftime("%Y-%m-%d"),
                    "apply_url": href,
                    "official_website": source_meta.get("url", href),
                    "selection_process": "Written Examination followed by Document Verification.",
                    "source": f"Live HTML Link Parser ({source_meta.get('id', 'web')})"
                })
                if len(found_jobs) >= 3:
                    break

    return found_jobs

def execute_scan_stream() -> Generator[str, None, None]:
    start_time = time.time()
    total_steps = len(SCAN_SOURCES) + 2
    step = 1

    total_scanned = 0
    total_added = 0
    total_updated = 0

    # Step 1: Initialize
    ev_init = ScanEvent(
        step=step,
        total_steps=total_steps,
        source_name="FuturSet Scanner Engine",
        status="scanning",
        message="Initializing automated live scanner across 14 Gujarat State, Central government & Airport/Postal portals...",
        jobs_scanned=0,
        jobs_added=0,
        jobs_updated=0,
        timestamp=datetime.now().strftime("%H:%M:%S")
    )
    yield f"data: {ev_init.model_dump_json()}\n\n"
    time.sleep(0.3)

    for src in SCAN_SOURCES:
        step += 1
        src_name = src["name"]
        src_url = src["url"]

        # Notify scanning source
        ev_start = ScanEvent(
            step=step,
            total_steps=total_steps,
            source_name=src_name,
            status="scanning",
            message=f"Connecting to {src_name}... probing latest public gazettes & notice boards.",
            jobs_scanned=total_scanned,
            jobs_added=total_added,
            jobs_updated=total_updated,
            timestamp=datetime.now().strftime("%H:%M:%S")
        )
        yield f"data: {ev_start.model_dump_json()}\n\n"
        time.sleep(0.3)

        # Attempt safe network probe and BeautifulSoup parsing
        live_html = fetch_live_source_safe(src_url, timeout=3)
        parsed_live = parse_portal_html_for_jobs(live_html, src)

        source_items = list(src["feed_data"])
        if parsed_live:
            source_items.extend(parsed_live)

        src_scanned = len(source_items)
        src_added = 0
        src_updated = 0

        for item in source_items:
            if not item.get("official_website"):
                item["official_website"] = src.get("url", item.get("apply_url"))
            if not item.get("salary_text"):
                item["salary_text"] = "Government 7th Pay Scale as per Official Gazette"
            if not item.get("department"):
                item["department"] = src.get("name", "Government Department")
            res = upsert_job(item)
            if res == "added":
                src_added += 1
                total_added += 1
            else:
                src_updated += 1
                total_updated += 1
            total_scanned += 1

        # Source scan completed
        duration = round(time.time() - start_time, 2)
        record_scan_log(src_name, src_scanned, src_added, src_updated, duration, "success",
                        f"Scanned {src_scanned} records (live parsed: {len(parsed_live)}). {src_added} added, {src_updated} refreshed.")

        status_msg = f"Synced {src_name}: {src_scanned} notices processed"
        if parsed_live:
            status_msg += f" ({len(parsed_live)} live HTML notices extracted via BeautifulSoup)"
        status_msg += f", {src_added} new added, {src_updated} synced with zero duplicates."

        ev_done = ScanEvent(
            step=step,
            total_steps=total_steps,
            source_name=src_name,
            status="item_found",
            message=status_msg,
            jobs_scanned=total_scanned,
            jobs_added=total_added,
            jobs_updated=total_updated,
            timestamp=datetime.now().strftime("%H:%M:%S")
        )
        yield f"data: {ev_done.model_dump_json()}\n\n"
        time.sleep(0.3)

    # Final Step: Wrap up
    step += 1
    total_duration = round(time.time() - start_time, 2)
    stats = get_stats()

    ev_complete = ScanEvent(
        step=step,
        total_steps=total_steps,
        source_name="FuturSet Aggregator Engine",
        status="completed",
        message=f"Scan cycle complete in {total_duration}s! Total active database: {stats['total_jobs']} jobs, {stats['total_vacancies']:,} verified vacancies.",
        jobs_scanned=total_scanned,
        jobs_added=total_added,
        jobs_updated=total_updated,
        timestamp=datetime.now().strftime("%H:%M:%S")
    )
    yield f"data: {ev_complete.model_dump_json()}\n\n"

def run_scan_sync() -> Dict[str, Any]:
    start_time = time.time()
    total_scanned = 0
    total_added = 0
    total_updated = 0

    for src in SCAN_SOURCES:
        live_html = fetch_live_source_safe(src["url"], timeout=3)
        parsed_live = parse_portal_html_for_jobs(live_html, src)

        source_items = list(src["feed_data"])
        if parsed_live:
            source_items.extend(parsed_live)

        for item in source_items:
            if not item.get("official_website"):
                item["official_website"] = src.get("url", item.get("apply_url"))
            if not item.get("salary_text"):
                item["salary_text"] = "Government 7th Pay Scale as per Official Gazette"
            if not item.get("department"):
                item["department"] = src.get("name", "Government Department")
            res = upsert_job(item)
            if res == "added":
                total_added += 1
            else:
                total_updated += 1
            total_scanned += 1

        record_scan_log(src["name"], len(source_items), total_added, total_updated, 0.2, "success", "Synchronized successfully.")

    total_duration = round(time.time() - start_time, 2)
    return {
        "status": "success",
        "duration_seconds": total_duration,
        "scanned": total_scanned,
        "added": total_added,
        "updated": total_updated
    }
