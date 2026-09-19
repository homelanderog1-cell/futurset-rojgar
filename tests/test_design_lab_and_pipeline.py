"""
Test Suite for Design Lab (50 Previews), Standalone Concept Websites (20 Concepts),
and the 5-Stage Article & Gazette Editorial Pipeline.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_design_lab_hub():
    response = client.get("/design-lab")
    assert response.status_code == 200
    assert "01 / 50" in response.text
    assert "Master Luminous" in response.text
    assert "preview-iframe" in response.text
    assert "btn-view-dashboard" in response.text
    assert "btn-view-pipeline" in response.text

def test_design_lab_preview_switch():
    response = client.get("/design-lab?preview=02")
    assert response.status_code == 200
    assert "Linear Precision" in response.text

    response50 = client.get("/design-lab?preview=50")
    assert response50.status_code == 200
    assert "Quantum Nebula" in response50.text

def test_previews_metadata_api():
    response = client.get("/api/previews")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 50
    assert len(data["previews"]) == 50
    # Verify every preview has required fields and rich animation provenance
    for p in data["previews"]:
        assert "id" in p
        assert "name" in p
        assert "inspired_by" in p
        assert "animations" in p
        assert len(p["animations"]) >= 2
        for anim in p["animations"]:
            assert "name" in anim
            assert "source" in anim
            assert "url" in anim
            assert "usage" in anim
            assert "tech"
            assert "gpu" in anim
            assert "a11y" in anim

def test_concepts_hub():
    response = client.get("/concepts")
    assert response.status_code == 200
    assert "20 Standalone Experimental Concepts" in response.text

def test_concept_individual_views():
    for cid in ["01", "05", "10", "15", "20"]:
        response = client.get(f"/concepts/{cid}")
        assert response.status_code == 200
        assert f"Concept #{cid}" in response.text

def test_article_pipeline_api_get():
    response = client.get("/api/pipeline/articles")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] >= 6
    stages = [a["stage"] for a in data["articles"]]
    valid_stages = {"ingested", "parsing", "drafting", "review", "published"}
    assert set(stages).issubset(valid_stages)
    assert len(stages) > 0

def test_article_pipeline_transition():
    # Create an article in ingested stage and transition it to parsing
    create_res = client.post("/api/pipeline/articles", json={
        "title": "Automated Test Gazette Notice",
        "stage": "ingested",
        "vacancies": 250,
        "category": "Test"
    })
    assert create_res.status_code == 200
    art_id = create_res.json()["article_id"]

    response = client.post(f"/api/pipeline/articles/{art_id}/transition", json={"stage": "parsing"})
    assert response.status_code == 200
    assert response.json()["stage"] == "parsing"

def test_article_pipeline_publish():
    response = client.post("/api/pipeline/articles/2/publish")
    assert response.status_code == 200
    assert response.json()["success"] is True

def test_home_page_preserves_article_pipeline_and_theme():
    response = client.get("/?theme=03")
    assert response.status_code == 200
    assert 'id="article-pipeline-modal"' in response.text
    assert 'data-preview-theme="03"' in response.text
    assert 'window.__PIPELINE_ARTICLES__' in response.text
    assert 'window.__PREVIEWS__' in response.text
    assert 'window.__ACTIVE_VIEW__ = "dashboard"' in response.text

def test_home_page_pipeline_view():
    response = client.get("/?theme=50&view=pipeline")
    assert response.status_code == 200
    assert "FuturSet Article &amp; Gazette Editorial Pipeline" in response.text
    assert "article-pipeline-board" in response.text
    assert 'data-preview-theme="50"' in response.text
    assert 'window.__ACTIVE_VIEW__ = "pipeline"' in response.text

