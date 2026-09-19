"""
FuturSet Jobs Portal - AI Eligibility Matcher & Recommendation Engine
Calculates candidate match score, checks age relaxation criteria across quotas,
evaluates education hierarchies, and produces actionable career guidance.
"""
import re
from typing import List, Dict, Any, Tuple, Optional
from app.models import MatchProfile, MatchResult, JobResponse
from app.database import get_jobs

EDUCATION_LEVELS = {
    "10th Pass": 1,
    "12th Pass": 2,
    "ITI": 2,
    "Diploma": 3,
    "Graduate": 4,
    "B.E. / B.Tech": 4,
    "Engineering": 4,
    "MBBS": 5,
    "Post Graduate": 5,
    "Any": 0
}

def extract_single_level(q: str) -> Optional[Tuple[int, str]]:
    ql = q.lower().strip()
    if re.search(r'\b(mbbs|medical\s*officer|doctor)\b', ql):
        return 5, "MBBS / Medical"
    if re.search(r'\b(post[- ]?graduat\w*|master\w*|m\.?sc|m\.?tech|m\.?com|m\.?a\b|mba)\b', ql):
        return 5, "Post Graduate"
    if re.search(r'\b(diploma)\b', ql):
        return 3, "Diploma"
    if re.search(r'\b(b\.?e\b|b\.?tech|engineering)\b', ql):
        return 4, "Engineering / B.Tech"
    if re.search(r'\b(graduat\w*|bachelor\w*|degree|b\.?a\b|b\.?com\b|b\.?sc\b)\b', ql):
        return 4, "Graduate"
    if re.search(r'\b(iti)\b', ql):
        return 2, "ITI"
    if re.search(r'\b(12th|higher\s*secondary|hsc|intermediate|10\+2)\b', ql):
        return 2, "12th Pass"
    if re.search(r'\b(10th|ssc|matric\w*)\b', ql):
        return 1, "10th Pass"
    return None

def extract_required_level(qualification_text: str) -> Tuple[int, str]:
    """
    Extracts the minimum acceptable education level and description.
    Correctly handles OR alternatives such as '10th + ITI / Diploma / Engineering'
    or '12th Pass / Any Bachelor's Degree', while ignoring auxiliary conditions like 'English/Gujarati Typing'.
    """
    if not qualification_text:
        return 1, "Any Qualification"

    # Split on OR / slash options
    parts = [p.strip() for p in re.split(r'[/|]|\bor\b', qualification_text, flags=re.IGNORECASE) if p.strip()]
    extracted = [extract_single_level(part) for part in parts]
    valid_extracted = [x for x in extracted if x is not None]

    if valid_extracted:
        # Lowest education level among genuine educational requirements
        return min(valid_extracted, key=lambda x: x[0])

    full_level = extract_single_level(qualification_text)
    if full_level:
        return full_level

    return 1, "Any Qualification"

def get_age_relaxation(category: str, state: str = "Gujarat") -> int:
    cat = category.strip().lower()
    if "sc" in cat or "st" in cat:
        return 5
    if "obc" in cat or "sebc" in cat:
        return 3
    if "female" in cat or "women" in cat:
        return 5
    if "pwd" in cat or "disabled" in cat:
        return 10
    if "ex-sm" in cat or "ex-servicemen" in cat:
        return 5
    if "ews" in cat:
        return 5 if state == "Gujarat" else 0
    return 0

def match_candidate(profile: MatchProfile) -> List[MatchResult]:
    all_jobs = get_jobs({"limit": 250})
    user_cat_relaxation = get_age_relaxation(profile.category, profile.state_preference)
    user_edu_score = EDUCATION_LEVELS.get(profile.qualification, 4)

    results = []

    for j_dict in all_jobs:
        score = 60
        reasons = []
        relaxation_applied = None

        # Age Check
        age_min = j_dict.get("age_min", 18)
        age_max_base = j_dict.get("age_max", 35)
        effective_max_age = age_max_base + user_cat_relaxation

        age_eligible = True
        if profile.age < age_min:
            age_eligible = False
            reasons.append(f"Underage: Below minimum statutory age ({age_min} yrs).")
        elif profile.age > effective_max_age:
            age_eligible = False
            reasons.append(f"Over-age: Exceeds maximum age limit ({effective_max_age} yrs including quota relaxation).")
        else:
            if profile.age > age_max_base:
                score += 15
                relaxation_applied = f"+{user_cat_relaxation} yrs {profile.category} Quota Relaxation Applied"
                reasons.append(f"Eligible via {profile.category} Age Relaxation (+{user_cat_relaxation} yrs).")
            else:
                score += 15
                reasons.append("Directly within standard age limits.")

        # Qualification Check
        q_text = j_dict.get("qualification", "")
        req_level, req_name = extract_required_level(q_text)

        edu_eligible = True
        # Check specialized requirements
        job_title_lower = j_dict.get("title", "").lower()
        is_medical_req = (
            "mbbs" in q_text.lower()
            or "medical" in q_text.lower()
            or "mbbs" in job_title_lower
            or "medical" in job_title_lower
            or "nurse" in job_title_lower
            or "nursing" in q_text.lower()
        )
        if is_medical_req:
            if profile.qualification != "MBBS":
                edu_eligible = False
                reasons.append(f"Requires MBBS / Medical Degree (candidate has {profile.qualification}).")
            else:
                score += 25
                reasons.append("MBBS Medical Council qualifications verified.")
        else:
            if user_edu_score >= req_level:
                score += 20
                reasons.append(f"Education criteria satisfied ({profile.qualification} qualifies for {req_name}).")
            else:
                edu_eligible = False
                reasons.append(f"Requires higher qualification ({req_name}; candidate holds {profile.qualification}).")

        # State / Domicile Check
        is_gujarat_job = j_dict.get("state", "").lower() == "gujarat"
        if profile.state_preference.lower() == "gujarat":
            if is_gujarat_job:
                score += 10
                reasons.append("Gujarat State preference match (OJAS / GPSC domicile benefit).")
            elif profile.include_central and j_dict.get("gov_level") == "Central":
                score += 5
                reasons.append("All India Central Government opportunity.")
            else:
                score -= 10
            if j_dict.get("gov_level") == "Central":
                score += 10
                reasons.append("Central Govt All India Opening.")

        # Specialized B.Tech CSE / IT match bonus
        is_candidate_tech = any(t in profile.qualification.lower() for t in ["b.tech", "b.e.", "engineering", "cse", "it"])
        if is_candidate_tech and j_dict.get("is_btech_cse") == 1:
            score += 15
            reasons.append("🎯 Direct B.Tech CSE / IT Core Technology Role Match.")

        # Vacancies factor
        vacancies = j_dict.get("vacancies", 0)
        if vacancies > 5000:
            score += 10
            reasons.append(f"Mega recruitment: {vacancies:,} active vacancies increases selection probability.")
        elif vacancies > 1000:
            score += 5
            reasons.append(f"Large recruitment drive: {vacancies:,} posts.")

        # Hard ineligibility handling
        if not age_eligible:
            if profile.age < age_min:
                status = "Ineligible (Underage)"
            else:
                status = "Ineligible (Exceeds Age Limit)"
            final_score = min(20, max(5, score - 60))
        elif not edu_eligible:
            status = "Ineligible (Qualification Shortfall)"
            final_score = min(30, max(10, score - 50))
        else:
            final_score = max(50, min(99, score))
            if final_score >= 80:
                status = "Highly Recommended"
            elif final_score >= 65:
                status = "Eligible & Competitive"
            else:
                status = "Conditionally Eligible"

        job_resp = JobResponse(**j_dict)
        results.append(MatchResult(
            job=job_resp,
            match_score=final_score,
            eligibility_status=status,
            reasons=reasons,
            relaxation_applied=relaxation_applied
        ))

    # Sort descending by match_score
    results.sort(key=lambda x: x.match_score, reverse=True)
    return results
