import sys
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

LLM_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = LLM_ROOT.parent
for candidate in (str(PROJECT_ROOT), str(LLM_ROOT)):
    if candidate not in sys.path:
        sys.path.insert(0, candidate)

from llm.api.v1.endpoints.translation import router as translation_router


@pytest.fixture
def client():
    test_app = FastAPI()
    test_app.include_router(translation_router)
    return TestClient(test_app)


def test_detect_endpoint_respects_preference(client):
    response = client.post(
        "/api/v1/translation/detect",
        json={"text": "", "preferred_language": "HI-IN"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["language"] == "hi"
    assert payload["detected"] is False
    assert payload["default_language"] == "en"


def test_detect_endpoint_auto_detects(monkeypatch, client):
    def fake_detect(text, allow=None):
        assert text == "Hola"
        return "es"

    monkeypatch.setattr(
        "llm.api.v1.endpoints.translation.detect_language",
        fake_detect,
    )
    response = client.post("/api/v1/translation/detect", json={"text": "Hola"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["language"] == "es"
    assert payload["detected"] is True


def test_translate_endpoint_uses_helper(monkeypatch, client):
    calls = {}

    def fake_translate(text, target_language, *, source_language=None, max_tokens=300):
        calls["args"] = (text, target_language, source_language, max_tokens)
        return "Hola"

    monkeypatch.setattr(
        "llm.api.v1.endpoints.translation.translate_text",
        fake_translate,
    )
    response = client.post(
        "/api/v1/translation/translate",
        json={"text": "Hello", "target_language": "es", "source_language": "en"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["text"] == "Hola"
    assert payload["translated"] is True
    assert calls["args"] == ("Hello", "es", "en", 300)
