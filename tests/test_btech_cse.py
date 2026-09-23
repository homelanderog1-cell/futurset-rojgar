"""
Tests for B.Tech CSE & IT Engineering Hub and Multi-Selection Ingestion
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db, get_btech_cse_jobs, get_stats, get_jobs

@pytest.fixture(scope="module")
def client():
    init_db()
    with TestClient(app) as c:
        yield c

def test_btech_cse_page_render(client):
    res = client.get("/btech-cse")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "B.Tech CSE" in res.text
    assert "Recruitment Radar" in res.text
    assert "NIC Scientist-B" in res.text or "TCS" in res.text

def test_btech_cse_api_all(client):
    res = client.get("/api/jobs/btech-cse")
    assert res.status_code == 200
    data = res.json()
    assert "count" in data
    assert "results" in data
    assert data["count"] >= 30

def test_btech_cse_api_categories(client):
    # Central Govt
    res_cen = client.get("/api/jobs/btech-cse?category=central_govt")
    assert res_cen.status_code == 200
    data_cen = res_cen.json()
    assert data_cen["count"] >= 5
    for j in data_cen["results"]:
        assert j["gov_level"] == "Central"

    # Gujarat State Govt
    res_guj = client.get("/api/jobs/btech-cse?category=gujarat_govt")
    assert res_guj.status_code == 200
    data_guj = res_guj.json()
    assert data_guj["count"] >= 5
    for j in data_guj["results"]:
        assert j["state"] == "Gujarat"

    # PSU Tech
    res_psu = client.get("/api/jobs/btech-cse?category=psu")
    assert res_psu.status_code == 200
    assert res_psu.json()["count"] >= 2

    # Private Tech MNCs
    res_pvt = client.get("/api/jobs/btech-cse?category=private")
    assert res_pvt.status_code == 200
    assert res_pvt.json()["count"] >= 5

def test_selection_mode_filters(client):
    # Direct Merit
    res_merit = client.get("/api/jobs?selection_mode=direct_merit")
    assert res_merit.status_code == 200
    assert res_merit.json()["count"] >= 5

    # Walk-in
    res_walkin = client.get("/api/jobs?selection_mode=walk_in")
    assert res_walkin.status_code == 200
    assert res_walkin.json()["count"] >= 2

    # Apprenticeship
    res_appr = client.get("/api/jobs?selection_mode=apprenticeship")
    assert res_appr.status_code == 200
    assert res_appr.json()["count"] >= 3

def test_portal_stats_counters(client):
    res = client.get("/api/stats")
    assert res.status_code == 200
    stats = res.json()
    assert stats["total_jobs"] >= 150
    assert stats["total_vacancies"] > 100000
    assert stats["btech_cse_jobs"] >= 50
    assert stats["btech_cse_vacancies"] > 300000
    assert stats["direct_merit_jobs"] > 0
    assert stats["apprentice_jobs"] > 0
