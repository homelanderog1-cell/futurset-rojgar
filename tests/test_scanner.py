"""
Unit tests for FuturSet Scanner Engine
"""
import pytest
import json
from app.database import init_db, get_stats
from app.scanner_engine import run_scan_sync, execute_scan_stream

@pytest.fixture(autouse=True)
def setup_db():
    init_db()

def test_run_scan_sync():
    res = run_scan_sync()
    assert res["status"] == "success"
    assert res["scanned"] > 0
    assert res["duration_seconds"] >= 0

def test_execute_scan_stream():
    stream = execute_scan_stream()
    events = []
    for chunk in stream:
        assert chunk.startswith("data: ")
        payload = chunk.replace("data: ", "").strip()
        if payload:
            data = json.loads(payload)
            events.append(data)
            if data["status"] == "completed":
                break

    assert len(events) >= 3
    assert events[0]["step"] == 1
    assert events[-1]["status"] == "completed"

def test_parse_portal_html_for_jobs():
    from app.scanner_engine import parse_portal_html_for_jobs
    sample_html = """
    <html>
      <body>
        <table>
          <tr>
            <td>Gujarat Forest Guard & Forester Bharti 2026</td>
            <td>Forest Department announces 1,450 vacancies across districts. Notification GFD/2026/08.</td>
            <td><a href="https://ojas.gujarat.gov.in/Advt/GFD_2026.pdf">Apply Now</a></td>
          </tr>
        </table>
      </body>
    </html>
    """
    source_meta = {
        "id": "forest_gujarat",
        "name": "Gujarat Forest Department",
        "type": "gujarat",
        "board": "Forest",
        "url": "https://forests.gujarat.gov.in"
    }
    jobs = parse_portal_html_for_jobs(sample_html, source_meta)
    assert len(jobs) == 1
    j = jobs[0]
    assert "Forest" in j["title"]
    assert j["vacancies"] == 1450
    assert j["notification_number"] == "GFD/2026/08"
    assert j["apply_url"] == "https://ojas.gujarat.gov.in/Advt/GFD_2026.pdf"
