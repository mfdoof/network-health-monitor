import asyncio
import json
import logging

import httpx
import pytest
import respx

from api import llm
from api.llm import LLMError, llm_complete
from tests.conftest import LLM_KEY, LLM_URL

COMPLETIONS = f"{LLM_URL}/chat/completions"


def reply(content: str) -> httpx.Response:
    return httpx.Response(200, json={"choices": [{"message": {"role": "assistant", "content": content}}]})


def complete(prompt: str = "hello") -> str:
    return asyncio.run(llm_complete(prompt))


@respx.mock
def test_success():
    route = respx.post(COMPLETIONS).mock(return_value=reply("  All good.  "))
    assert complete("check this") == "All good."

    request = route.calls.last.request
    assert request.headers["Authorization"] == f"Bearer {LLM_KEY}"
    body = json.loads(request.content)
    assert body["model"] == "test-model"
    assert body["messages"] == [{"role": "user", "content": "check this"}]


@respx.mock
def test_no_key_sends_no_auth_header(monkeypatch):
    monkeypatch.setattr(llm, "LLM_API_KEY", "")
    route = respx.post(COMPLETIONS).mock(return_value=reply("ok"))
    complete()
    assert "Authorization" not in route.calls.last.request.headers


@pytest.mark.parametrize("status,expected_status,message", [
    (401, 502, "Check LLM_API_KEY"),
    (429, 429, "rate limit"),
    (500, 502, "returned an error"),
])
@respx.mock
def test_provider_errors(status, expected_status, message):
    respx.post(COMPLETIONS).mock(return_value=httpx.Response(status, json={"error": {}}))
    with pytest.raises(LLMError) as exc:
        complete()
    assert exc.value.status_code == expected_status
    assert message in str(exc.value)


@respx.mock
def test_timeout():
    respx.post(COMPLETIONS).mock(side_effect=httpx.ReadTimeout("slow"))
    with pytest.raises(LLMError) as exc:
        complete()
    assert exc.value.status_code == 504


@respx.mock
def test_unreachable():
    respx.post(COMPLETIONS).mock(side_effect=httpx.ConnectError("refused"))
    with pytest.raises(LLMError) as exc:
        complete()
    assert exc.value.status_code == 502


@respx.mock
def test_unexpected_response_shape():
    respx.post(COMPLETIONS).mock(return_value=httpx.Response(200, json={"nope": True}))
    with pytest.raises(LLMError) as exc:
        complete()
    assert exc.value.status_code == 502


@pytest.mark.parametrize("setting", ["LLM_BASE_URL", "LLM_MODEL"])
@respx.mock
def test_not_configured(monkeypatch, setting):
    monkeypatch.setattr(llm, setting, "")
    route = respx.post(COMPLETIONS).mock(return_value=reply("ok"))
    with pytest.raises(LLMError) as exc:
        complete()
    assert exc.value.status_code == 503
    assert not route.called


@respx.mock
def test_logs_never_contain_key_prompt_or_response(caplog):
    respx.post(COMPLETIONS).mock(return_value=reply("SECRET-RESPONSE-TEXT"))
    with caplog.at_level(logging.DEBUG):
        complete("SECRET-PROMPT-TEXT")
    logs = caplog.text
    assert "status=200" in logs and "model=test-model" in logs
    for secret in (LLM_KEY, "SECRET-PROMPT-TEXT", "SECRET-RESPONSE-TEXT"):
        assert secret not in logs


# --- Routes ---

def test_config_endpoint_never_returns_key(client):
    r = client.get("/api/config")
    assert r.json() == {"llm_enabled": True, "provider_host": "llm.test", "model": "test-model"}
    assert LLM_KEY not in r.text


def test_config_endpoint_when_disabled(client, monkeypatch):
    monkeypatch.setattr(llm, "LLM_BASE_URL", "")
    assert client.get("/api/config").json() == {"llm_enabled": False, "provider_host": None, "model": "test-model"}


def test_analyze_returns_llm_error_detail(client, monkeypatch):
    monkeypatch.setattr(llm, "LLM_BASE_URL", "")
    monkeypatch.setattr("api.main.run_dns_lookup", lambda target: {
        "lookup_type": "forward", "target": target, "a_records": [], "aaaa_records": [],
        "mx_records": [], "ns_records": [], "errors": [],
    })
    r = client.post("/api/dns/analyze", json={"target": "example.com"})
    assert r.status_code == 503
    assert "not configured" in r.json()["detail"]
