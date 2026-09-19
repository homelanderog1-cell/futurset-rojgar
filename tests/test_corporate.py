"""
Unit & Integration tests for FuturSet Corporate & Enterprise Hub (/corporate)
Validates Adani, BHEL, Linde, Amazon, Flipkart, NPCI/UPI, semi-private, and conglomerate recruitments.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db, get_corporate_jobs, get_corporate_stats

@pytest.fixture(scope="module")
def client():
    init_db()
    with TestClient(app) as c:
        yield c

def test_corporate_page_render(client):
    response = client.get("/corporate")
    assert response.status_code == 200
    assert "Enterprise" in response.text
    assert "Corporate Careers" in response.text
    assert "Adani" in response.text
    assert "BHEL" in response.text
    assert "Linde" in response.text
    assert "Amazon" in response.text
    assert "Flipkart" in response.text

def test_api_get_corporate_jobs(client):
    response = client.get("/api/jobs/corporate")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert data["count"] >= 25

def test_api_corporate_company_type_filters(client):
    # Semi-Private & Govt-backed (BHEL, Linde, GSFC, NPCI/UPI)
    res_semi = client.get("/api/jobs/corporate?company_type=semi_private")
    assert res_semi.status_code == 200
    semi_data = res_semi.json()
    assert semi_data["count"] >= 5
    orgs = [j["organization"] for j in semi_data["results"]]
    assert any("BHEL" in o for o in orgs)
    assert any("Linde" in o for o in orgs)
    assert any("NPCI" in o for o in orgs)

    # Conglomerates (Adani, Reliance, Tata, L&T)
    res_cong = client.get("/api/jobs/corporate?company_type=conglomerate")
    assert res_cong.status_code == 200
    cong_data = res_cong.json()
    assert cong_data["count"] >= 4
    cong_orgs = [j["organization"] for j in cong_data["results"]]
    assert any("Adani" in o for o in cong_orgs)

    # Global Tech (Amazon, Flipkart, Google)
    res_tech = client.get("/api/jobs/corporate?company_type=global_tech")
    assert res_tech.status_code == 200
    tech_data = res_tech.json()
    assert tech_data["count"] >= 3
    tech_orgs = [j["organization"] for j in tech_data["results"]]
    assert any("Amazon" in o for o in tech_orgs)
    assert any("Flipkart" in o for o in tech_orgs)

def test_api_corporate_eligible_only(client):
    response = client.get("/api/jobs/corporate?eligible_only=true")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] >= 20
    for j in data["results"]:
        assert (
            j["is_btech_cse"] == 1 
            or j["qualification_level"] in ("Engineering", "Graduate", "Diploma") 
            or "Engineering" in j["qualification"] 
            or "Degree" in j["qualification"] 
            or "Graduate" in j["qualification"]
        )

def test_api_corporate_gujarat_location(client):
    response = client.get("/api/jobs/corporate?location=gujarat")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] >= 10
    # Check Gujarat company presence
    orgs = [j["organization"] for j in data["results"]]
    assert any("Adani" in o for o in orgs)
    assert any("Linde" in o for o in orgs)
    assert any("GSFC" in o for o in orgs)

def test_api_corporate_all_sectors_filters(client):
    # 1. Big Tech
    res_tech = client.get("/api/jobs/corporate?company_type=global_tech")
    assert res_tech.status_code == 200
    tech_data = res_tech.json()
    assert tech_data["count"] >= 15
    tech_orgs = [j["organization"] for j in tech_data["results"]]
    assert any("Microsoft" in o for o in tech_orgs)
    assert any("Amazon" in o for o in tech_orgs)
    assert any("Google" in o for o in tech_orgs)

    # 2. Unicorns
    res_uni = client.get("/api/jobs/corporate?company_type=unicorns")
    assert res_uni.status_code == 200
    uni_data = res_uni.json()
    assert uni_data["count"] >= 10
    uni_orgs = [j["organization"] for j in uni_data["results"]]
    assert any("Swiggy" in o for o in uni_orgs)
    assert any("Zomato" in o for o in uni_orgs)
    assert any("Razorpay" in o for o in uni_orgs)

    # 3. IT Services
    res_it = client.get("/api/jobs/corporate?company_type=it_services")
    assert res_it.status_code == 200
    it_data = res_it.json()
    assert it_data["count"] >= 12
    it_orgs = [j["organization"] for j in it_data["results"]]
    assert any("Cognizant" in o for o in it_orgs)
    assert any("Accenture" in o for o in it_orgs)
    assert any("Capgemini" in o for o in it_orgs)

    # 4. BFSI Private
    res_bfsi = client.get("/api/jobs/corporate?company_type=bfsi")
    assert res_bfsi.status_code == 200
    bfsi_data = res_bfsi.json()
    assert bfsi_data["count"] >= 8
    bfsi_orgs = [j["organization"] for j in bfsi_data["results"]]
    assert any("HDFC" in o for o in bfsi_orgs)
    assert any("ICICI" in o for o in bfsi_orgs)
    assert any("Axis" in o for o in bfsi_orgs)

    # 5. Automobile & EV
    res_auto = client.get("/api/jobs/corporate?company_type=auto_ev")
    assert res_auto.status_code == 200
    auto_data = res_auto.json()
    assert auto_data["count"] >= 6
    auto_orgs = [j["organization"] for j in auto_data["results"]]
    assert any("Maruti" in o for o in auto_orgs)
    assert any("Ola Electric" in o for o in auto_orgs)

    # 6. Pharma
    res_pharma = client.get("/api/jobs/corporate?company_type=pharma")
    assert res_pharma.status_code == 200
    pharma_data = res_pharma.json()
    assert pharma_data["count"] >= 8
    pharma_orgs = [j["organization"] for j in pharma_data["results"]]
    assert any("Sun Pharma" in o for o in pharma_orgs)
    assert any("Zydus" in o for o in pharma_orgs)

    # 7. FMCG
    res_fmcg = client.get("/api/jobs/corporate?company_type=fmcg")
    assert res_fmcg.status_code == 200
    fmcg_data = res_fmcg.json()
    assert fmcg_data["count"] >= 8
    fmcg_orgs = [j["organization"] for j in fmcg_data["results"]]
    assert any("Hindustan Unilever" in o or "HUL" in o for o in fmcg_orgs)
    assert any("ITC" in o for o in fmcg_orgs)

    # 8. Gujarat Champions
    res_guj = client.get("/api/jobs/corporate?company_type=gujarat_champions")
    assert res_guj.status_code == 200
    guj_data = res_guj.json()
    assert guj_data["count"] >= 9
    guj_orgs = [j["organization"] for j in guj_data["results"]]
    assert any("Torrent Power" in o for o in guj_orgs)
    assert any("Nirma" in o for o in guj_orgs)

def test_api_corporate_stats(client):
    response = client.get("/api/corporate/stats")
    assert response.status_code == 200
    stats = response.json()
    assert stats["total_corporate_jobs"] >= 100
    assert stats["total_corporate_vacancies"] >= 200000
    assert stats["gujarat_corporate_jobs"] >= 50
    assert stats["highest_ctc_lpa"] >= 44.0
