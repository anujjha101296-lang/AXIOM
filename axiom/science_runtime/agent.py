"""Optional local LLM adapter.

No API key is required for the deterministic runtime. If Ollama is running,
this adapter can turn a scientific question into a structured research plan.
OpenAI remains an optional premium provider through the existing AXIOM gateway.
"""

from __future__ import annotations

import json
import os
import urllib.request


def ollama_available(base_url: str | None = None) -> bool:
    url = (base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")).rstrip("/") + "/api/tags"
    try:
        with urllib.request.urlopen(url, timeout=1) as response:
            return response.status == 200
    except Exception:
        return False


def plan_with_ollama(question: str, model: str | None = None, base_url: str | None = None) -> str:
    """Ask a local Ollama model for a concise research plan.

    The response is intentionally returned as text: scientific claims still
    require execution and verification by deterministic tools.
    """
    model = model or os.getenv("OLLAMA_MODEL", "llama3.2")
    url = (base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")).rstrip("/") + "/api/generate"
    prompt = (
        "You are the planning component of a scientific research engine. "
        "Do not claim a result. Return a short plan with: model, variables, "
        "hypothesis, falsifier, experiments, and verification checks.\n\n"
        f"Question: {question}"
    )
    body = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode()
    request = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = json.loads(response.read().decode())
    return str(payload.get("response", "")).strip()
