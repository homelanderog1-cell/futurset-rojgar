"""
Unit tests for FuturSet AI Eligibility Matcher
"""
import pytest
from app.database import init_db
from app.models import MatchProfile
from app.matcher import match_candidate, get_age_relaxation, extract_required_level

@pytest.fixture(autouse=True)
def setup_db():
    init_db()

def test_age_relaxation_rules():
    assert get_age_relaxation("General") == 0
    assert get_age_relaxation("OBC/SEBC") == 3
    assert get_age_relaxation("SC") == 5
    assert get_age_relaxation("ST") == 5
    assert get_age_relaxation("Female") == 5
    assert get_age_relaxation("PwD") == 10
    assert get_age_relaxation("EWS", state="Gujarat") == 5

def test_extract_required_level():
    lvl, name = extract_required_level("10th Pass or Matriculation")
    assert lvl == 1
    lvl, name = extract_required_level("12th Pass Higher Secondary")
    assert lvl == 2
    lvl, name = extract_required_level("Diploma in Mechanical Engineering")
    assert lvl == 3
    lvl, name = extract_required_level("Bachelor's Degree in any discipline")
    assert lvl == 4
    lvl, name = extract_required_level("Graduation in any discipline + English/Gujarati Typing")
    assert lvl == 4
    lvl, name = extract_required_level("10th + ITI / Diploma / Engineering")
    assert lvl == 2
    lvl, name = extract_required_level("12th Pass / Any Bachelor's Degree")
    assert lvl == 2
    lvl, name = extract_required_level("MBBS Degree + Council Registration")
    assert lvl == 5

def test_match_candidate_high_score():
    # 22-year-old graduate in Gujarat
    profile = MatchProfile(
        age=22,
        qualification="Graduate",
        category="General",
        state_preference="Gujarat",
        include_central=True
    )
    results = match_candidate(profile)
    assert len(results) > 0
    top_result = results[0]
    assert top_result.match_score >= 80
    assert top_result.eligibility_status in ["Highly Recommended", "Eligible & Competitive"]

def test_match_candidate_underage():
    profile = MatchProfile(
        age=14,  # Strictly below all statutory minimum ages (including 15 for Railway Apprentice)
        qualification="10th Pass",
        category="General",
        state_preference="Gujarat"
    )
    results = match_candidate(profile)
    assert len(results) > 0
    # Every job must mark a 14-year-old as Ineligible (Underage) with a disqualified score
    assert all(r.eligibility_status == "Ineligible (Underage)" for r in results)
    assert all(r.match_score <= 20 for r in results)

def test_match_candidate_overage():
    profile = MatchProfile(
        age=65,  # Exceeds maximum age limit
        qualification="Graduate",
        category="General",
        state_preference="Gujarat"
    )
    results = match_candidate(profile)
    assert len(results) > 0
    assert all(r.eligibility_status == "Ineligible (Exceeds Age Limit)" for r in results)
    assert all(r.match_score <= 20 for r in results)

def test_specialization_enforcement():
    profile = MatchProfile(
        age=28,
        qualification="10th Pass",
        category="General",
        state_preference="All India"
    )
    results = match_candidate(profile)
    upsc_results = [r for r in results if "UPSC" in r.job.title or "Civil Services" in r.job.title]
    assert len(upsc_results) > 0
    for ur in upsc_results:
        assert ur.eligibility_status == "Ineligible (Qualification Shortfall)"
        assert ur.match_score <= 30
