import time
from urllib.parse import urlparse

import httpx

from api.config import LLM_BASE_URL, LLM_API_KEY, LLM_MODEL, LLM_TIMEOUT
from api.logger import logger


class LLMError(Exception):
    """An LLM failure with a short, user-safe message and the HTTP status to return."""

    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.status_code = status_code


def llm_enabled() -> bool:
    return bool(LLM_BASE_URL and LLM_MODEL)


def provider_host() -> str | None:
    return urlparse(LLM_BASE_URL).hostname if LLM_BASE_URL else None


def _headers() -> dict[str, str]:
    headers = {"Content-Type": "application/json"}
    # Local servers like Ollama don't need a key
    if LLM_API_KEY:
        headers["Authorization"] = f"Bearer {LLM_API_KEY}"
    return headers


async def llm_complete(prompt: str, temperature: float = 0.3) -> str:
    """Send one user prompt to an OpenAI-compatible /chat/completions endpoint."""
    if not llm_enabled():
        raise LLMError("AI analysis is not configured. Set LLM_BASE_URL and LLM_MODEL.", 503)

    url = f"{LLM_BASE_URL.rstrip('/')}/chat/completions"
    body = {
        "model": LLM_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
    }

    # Log status, model and duration only: never the key, prompt or response
    start = time.monotonic()
    try:
        async with httpx.AsyncClient(timeout=LLM_TIMEOUT) as client:
            response = await client.post(url, json=body, headers=_headers())
    except httpx.TimeoutException:
        logger.error(f"LLM timeout | model={LLM_MODEL} | {time.monotonic() - start:.2f}s")
        raise LLMError("AI analysis timed out. Try again.", 504)
    except httpx.HTTPError as e:
        logger.error(f"LLM unreachable | model={LLM_MODEL} | {type(e).__name__}")
        raise LLMError("AI provider is unreachable. Check LLM_BASE_URL.", 502)

    duration = time.monotonic() - start
    logger.info(f"LLM response | status={response.status_code} | model={LLM_MODEL} | {duration:.2f}s")

    if response.status_code == 401:
        raise LLMError("AI provider rejected the request. Check LLM_API_KEY.", 502)
    if response.status_code == 429:
        raise LLMError("AI provider rate limit reached. Try again later.", 429)
    if response.status_code >= 400:
        raise LLMError("AI provider returned an error.", 502)

    try:
        content = response.json()["choices"][0]["message"]["content"]
    except (ValueError, KeyError, IndexError, TypeError):
        logger.error(f"LLM bad response shape | model={LLM_MODEL}")
        raise LLMError("AI provider returned an unexpected response.", 502)

    if not content:
        raise LLMError("AI provider returned an empty response.", 502)
    return content.strip()
