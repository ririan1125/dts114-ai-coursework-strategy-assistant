import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import app as coursework_app


def client():
    coursework_app.app.config.update(TESTING=True)
    coursework_app.TASKS.clear()
    coursework_app.NEXT_ID = 1
    return coursework_app.app.test_client()


def valid_payload():
    return {
        "title": "DTS114TC Software Coursework",
        "deadline": "2026-06-07T23:59",
        "importance": 5,
        "complexity": 4,
        "estimated_hours": 10,
        "notes": "Need to finish implementation and screenshots.",
    }


def test_health_endpoint():
    response = client().get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_strategy_preview_returns_priority_and_actions():
    response = client().post("/api/strategy", json=valid_payload())
    data = response.get_json()
    assert response.status_code == 200
    assert data["priority_label"] in {"critical", "high", "medium", "low"}
    assert data["strategy"]
    assert data["acceptance_criteria"]


def test_invalid_payload_is_rejected():
    payload = valid_payload()
    payload["importance"] = 9
    response = client().post("/api/strategy", json=payload)
    assert response.status_code == 400
    assert "importance" in response.get_json()["error"]


def test_create_and_list_tasks():
    test_client = client()
    created = test_client.post("/api/tasks", json=valid_payload())
    assert created.status_code == 201
    listed = test_client.get("/api/tasks")
    data = listed.get_json()
    assert data["count"] == 1
    assert data["items"][0]["title"] == valid_payload()["title"]


def test_sdlc_documents_include_requirements_and_endpoints():
    test_client = client()
    test_client.post("/api/tasks", json=valid_payload())
    response = test_client.post("/api/sdlc-documents", json={})
    data = response.get_json()
    assert response.status_code == 200
    assert data["functional_requirements"]
    assert "POST /api/strategy" in data["api_endpoints"]


def test_uml_endpoint_returns_plantuml():
    response = client().get("/api/uml/use-case")
    data = response.get_json()
    assert response.status_code == 200
    assert data["format"] == "plantuml"
    assert "@startuml" in data["diagram"]

