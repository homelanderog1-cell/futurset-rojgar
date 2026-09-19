"""
Integration tests for FuturSet FastAPI Endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db

@pytest.fixture(scope="module")
def client():
    init_db()
    with TestClient(app) as c:
        yield c

def test_health_endpoint(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["brand"] == "FuturSet"

def test_homepage_html(client):
    res = client.get("/")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "FuturSet" in res.text
    assert "Live Scanner" in res.text

def test_gujarat_portal_html(client):
    res = client.get("/gujarat")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "ગુજરાત" in res.text
    assert "OJAS" in res.text

def test_api_jobs_list(client):
    res = client.get("/api/jobs?limit=10")
    assert res.status_code == 200
    data = res.json()
    assert "count" in data
    assert "results" in data
    assert data["count"] > 0
    assert len(data["results"]) <= 10

def test_api_jobs_filter_gujarat(client):
    res = client.get("/api/jobs?state=Gujarat")
    assert res.status_code == 200
    data = res.json()
    for job in data["results"]:
        assert job["state"] == "Gujarat"

def test_api_job_detail(client):
    list_res = client.get("/api/jobs?limit=1")
    job_id = list_res.json()["results"][0]["id"]

    res = client.get(f"/api/jobs/{job_id}")
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == job_id
    assert "title" in data
    assert "apply_url" in data

def test_api_match(client):
    payload = {
        "age": 25,
        "qualification": "Graduate",
        "category": "OBC/SEBC",
        "state_preference": "Gujarat",
        "include_central": True
    }
    res = client.post("/api/match", json=payload)
    assert res.status_code == 200
    matches = res.json()
    assert len(matches) > 0
    assert "match_score" in matches[0]

def test_api_bookmark_flow(client):
    list_res = client.get("/api/jobs?limit=1")
    job_id = list_res.json()["results"][0]["id"]

    # Ensure clean state for test
    from app.database import get_db_connection
    conn = get_db_connection()
    conn.execute("DELETE FROM bookmarks WHERE job_id = ?", (job_id,))
    conn.commit()
    conn.close()

    res = client.post(f"/api/bookmark/{job_id}", json={"notes": "Exam prep"})
    assert res.status_code == 200
    data = res.json()
    assert data["job_id"] == job_id
    assert data["is_bookmarked"] is True

    bookmarks_res = client.get("/api/bookmarks")
    assert bookmarks_res.status_code == 200
    assert any(b["id"] == job_id for b in bookmarks_res.json()["bookmarks"])

    # Clean up toggle off
    res2 = client.post(f"/api/bookmark/{job_id}")
    assert res2.status_code == 200
    assert res2.json()["is_bookmarked"] is False

def test_api_export_csv(client):
    res = client.get("/api/export")
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
    assert "Title (EN)" in res.text
    assert "Organization" in res.text

def test_api_subscribe(client):
    payload = {
        "name": "Candidate Patel",
        "email": "candidate.patel@example.com",
        "state_pref": "Gujarat",
        "preferred_boards": ["OJAS", "GPSC"]
    }
    res = client.post("/api/subscribe", json=payload)
    assert res.status_code == 200
    assert res.json()["status"] == "success"
