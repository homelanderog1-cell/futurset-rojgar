"""
Edge case tests for FuturSet Jobs Portal
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db
from app.models import MatchProfile
from app.matcher import match_candidate

@pytest.fixture(scope="module")
def client():
    init_db()
    with TestClient(app) as c:
        yield c

def test_job_not_found_404(client):
    res = client.get("/api/jobs/9999999")
    assert res.status_code == 404
    assert "Job posting not found" in res.json()["detail"]

def test_bookmark_not_found_404(client):
    res = client.post("/api/bookmark/9999999", json=None)
    assert res.status_code == 404

def test_empty_search_query(client):
    res = client.get("/api/jobs?q=")
    assert res.status_code == 200
    assert res.json()["count"] > 0

def test_non_existent_search_query(client):
    res = client.get("/api/jobs?q=ZZZZZZZZ_NON_EXISTENT_RECRUITMENT")
    assert res.status_code == 200
    assert res.json()["count"] == 0

def test_static_css_served(client):
    res = client.get("/static/css/style.css")
    assert res.status_code == 200
    assert "glass-panel" in res.text

def test_static_js_app_served(client):
    res = client.get("/static/js/app.js")
    assert res.status_code == 200
    assert "fetchJobs" in res.text

def test_static_js_scanner_served(client):
    res = client.get("/static/js/scanner.js")
    assert res.status_code == 200
    assert "startLiveScan" in res.text

def test_matcher_extreme_age_boundary():
    profile = MatchProfile(age=70, qualification="Graduate", category="General")
    res = match_candidate(profile)
    assert len(res) > 0
    assert res[0].match_score <= 20
    assert res[0].eligibility_status == "Ineligible (Exceeds Age Limit)"

def test_matcher_overqualified_applicant():
    profile = MatchProfile(age=25, qualification="Post Graduate", category="SC")
    res = match_candidate(profile)
    assert len(res) > 0
    assert any(m.match_score >= 80 for m in res)
