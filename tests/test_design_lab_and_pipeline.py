"""
Test Suite for Design Lab (28 Previews), Standalone Concept Websites (20 Concepts),
and the 5-Stage Article & Gazette Editorial Pipeline.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_design_lab_hub():
    response = client.get("/design-lab")
    assert response.status_code == 200
    assert "01 / 28" in response.text
    assert "Master Luminous" in response.text
    assert "preview-iframe" in response.text

def test_design_lab_preview_switch():
    response = client.get("/design-lab?preview=02")
    assert response.status_code == 200
    assert "Linear Precision" in response.text

def test_previews_metadata_api():
    response = client.get("/api/previews")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 28
    assert len(data["previews"]) == 28
    # Verify every preview has required fields
    for p in data["previews"]:
        assert "id" in p
        assert "name" in p
        assert "inspired_by" in p
        assert "animations" in p

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
    assert "published" in stages
    assert "ingested" in stages

def test_article_pipeline_transition():
    # Advance article 5 (ingested) to parsing
    response = client.post("/api/pipeline/articles/5/transition", json={"stage": "parsing"})
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
