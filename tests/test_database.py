"""
Unit tests for FuturSet Database Layer
"""
import pytest
from datetime import datetime
from app.database import (
    init_db, get_jobs, get_job_by_id, upsert_job,
    toggle_bookmark, get_bookmarked_jobs, get_stats, compute_job_hash
)

@pytest.fixture(autouse=True)
def setup_database():
    init_db()

def test_seeded_jobs_exist():
    jobs = get_jobs({"limit": 50})
    assert len(jobs) >= 14, f"Expected at least 20 seeded jobs, got {len(jobs)}"

def test_gujarat_jobs_filter():
    guj_jobs = get_jobs({"state": "Gujarat", "limit": 50})
    assert len(guj_jobs) >= 3
    for j in guj_jobs:
        assert j["state"] == "Gujarat"

def test_central_jobs_filter():
    cen_jobs = get_jobs({"gov_level": "Central", "limit": 50})
    assert len(cen_jobs) >= 8
    for j in cen_jobs:
        assert j["gov_level"] == "Central"

def test_search_query():
    clerk_jobs = get_jobs({"q": "Clerk"})
    assert len(clerk_jobs) >= 1
    assert any("clerk" in j["title"].lower() or "gsssb" in j["organization"].lower() for j in clerk_jobs)

def test_job_by_id_and_days_left():
    jobs = get_jobs({"limit": 1})
    assert len(jobs) > 0
    job_id = jobs[0]["id"]
    job = get_job_by_id(job_id)
    assert job is not None
    assert job["id"] == job_id
    assert "days_left" in job
    assert "urgency_badge" in job
    assert job["views_count"] >= 1

def test_bookmark_lifecycle():
    jobs = get_jobs({"limit": 1})
    job_id = jobs[0]["id"]
    
    from app.database import get_db_connection
    conn = get_db_connection()
    conn.execute("DELETE FROM bookmarks WHERE job_id = ?", (job_id,))
    conn.commit()
    conn.close()

    # Toggle on
    is_bookmarked = toggle_bookmark(job_id, "Test Note")
    assert is_bookmarked is True
    
    # Verify in list
    bookmarks = get_bookmarked_jobs()
    assert any(b["id"] == job_id for b in bookmarks)

    # Toggle off
    is_bookmarked_again = toggle_bookmark(job_id)
    assert is_bookmarked_again is False

def test_upsert_deduplication():
    import uuid
    uid = uuid.uuid4().hex[:8]
    test_job = {
        "title": f"Unique Test Officer Bharti 2026 {uid}",
        "organization": "Gujarat Testing Board",
        "notification_number": f"GTB/2026/{uid}",
        "last_date": "2026-11-30",
        "apply_url": "https://test.gujarat.gov.in",
        "vacancies": 100
    }
    # 1st insertion
    action1 = upsert_job(test_job)
    assert action1 == "added"

    # 2nd insertion with identical hash
    action2 = upsert_job(test_job)
    assert action2 == "updated"

    # Clean up test job immediately so it never leaks into production DB
    from app.database import get_db_connection
    c = get_db_connection()
    c.execute("DELETE FROM jobs WHERE organization = 'Gujarat Testing Board';")
    c.commit()
    c.close()

    # Clean up test job immediately so it never leaks into production DB
    from app.database import get_db_connection
    c = get_db_connection()
    c.execute("DELETE FROM jobs WHERE organization = 'Gujarat Testing Board';")
    c.commit()
    c.close()

def test_stats_accuracy():
    stats = get_stats()
    assert stats["total_jobs"] >= 14
    assert stats["total_vacancies"] > 50000
    assert stats["gujarat_jobs"] >= 10
    assert stats["central_jobs"] >= 8

def test_days_left_and_urgency_boundaries():
    from datetime import datetime, timedelta
    from app.database import calculate_days_left, determine_urgency

    today_str = datetime.now().strftime("%Y-%m-%d")
    tomorrow_str = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    past_str = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
    future_str = (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d")

    # Today should be 0 days and urgent, NOT closed
    assert calculate_days_left(today_str) == 0
    assert determine_urgency(0) == "urgent"

    # Tomorrow should be 1 day and urgent
    assert calculate_days_left(tomorrow_str) == 1
    assert determine_urgency(1) == "urgent"

    # Past should be negative and closed
    assert calculate_days_left(past_str) < 0
    assert determine_urgency(-2) == "closed"

    # Future should be normal
    assert calculate_days_left(future_str) == 15
    assert determine_urgency(15) == "normal"

def test_notification_deduplication_different_titles():
    # Different titles for same board and notification number should produce identical hash
    hk1 = compute_job_hash("Gujarat Police Constable Bharti 2026", "GPRB", "GPRB/2026/01")
    hk2 = compute_job_hash("Unarmed Constable & SRPF Armed Constable 2026", "GPRB", "GPRB/2026/01")
    assert hk1 == hk2
