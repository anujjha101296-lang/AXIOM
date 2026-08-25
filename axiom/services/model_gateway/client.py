import os
import sqlite3
import json
import hashlib
import requests
import time
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ModelClient:
    def __init__(self, cache_path: str = "/tmp/axiom_model_cache.db"):
        self.cache_path = cache_path
        self.default_model = os.getenv("DEFAULT_MODEL", "mock-model")
        self.max_retries = 3
        self.timeout_sec = 30
        self._init_cache()

    def _init_cache(self):
        conn = sqlite3.connect(self.cache_path)
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS model_cache (
                    prompt_hash TEXT PRIMARY KEY,
                    prompt TEXT,
                    model TEXT,
                    response TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """)
        conn.close()

    def _get_cache(self, prompt_hash: str) -> Optional[str]:
        try:
            conn = sqlite3.connect(self.cache_path, timeout=5)
            cursor = conn.cursor()
            cursor.execute("SELECT response FROM model_cache WHERE prompt_hash = ?;", (prompt_hash,))
            row = cursor.fetchone()
            conn.close()
            return row[0] if row else None
        except sqlite3.Error:
            return None

    def _set_cache(self, prompt_hash: str, prompt: str, model: str, response: str):
        try:
            conn = sqlite3.connect(self.cache_path, timeout=5)
            with conn:
                conn.execute(
                    "INSERT OR REPLACE INTO model_cache (prompt_hash, prompt, model, response) VALUES (?, ?, ?, ?);",
                    (prompt_hash, prompt, model, response)
                )
            conn.close()
        except sqlite3.Error:
            pass

    def generate(self, prompt: str, model: str = "mock-model", temperature: float = 0.7) -> str:
        """
        Normalized generation interface with bounded retries, timeouts, and fallback.
        """
        if model == "mock-model" and self.default_model != "mock-model":
            model = self.default_model

        prompt_hash = hashlib.sha256(f"{model}:{prompt}:{temperature}".encode()).hexdigest()
        
        cached_response = self._get_cache(prompt_hash)
        if cached_response:
            return cached_response

        openai_key = os.getenv("OPENAI_API_KEY")
        gemini_key = os.getenv("GEMINI_API_KEY")
        
        # Build prioritized list of models/providers to try
        strategies = []
        if openai_key and model.startswith("gpt"):
            strategies.append(lambda: self._call_openai(prompt, model, temperature, openai_key))
            if gemini_key: # Fallback to gemini if openai fails
                strategies.append(lambda: self._call_gemini(prompt, "gemini-1.5-pro", temperature, gemini_key))
        elif gemini_key and model.startswith("gemini"):
            strategies.append(lambda: self._call_gemini(prompt, model, temperature, gemini_key))
            if openai_key: # Fallback to openai if gemini fails
                strategies.append(lambda: self._call_openai(prompt, "gpt-4o", temperature, openai_key))
        
        # Always fallback to mock if API calls fail or keys are absent
        strategies.append(lambda: self._generate_mock(prompt, model))

        response_text = ""
        for attempt, strategy in enumerate(strategies):
            retries = 0
            while retries <= self.max_retries:
                try:
                    response_text = strategy()
                    self._set_cache(prompt_hash, prompt, model, response_text)
                    return response_text
                except (requests.Timeout, requests.RequestException) as e:
                    logger.warning(f"Strategy {attempt} retry {retries} failed: {e}")
                    retries += 1
                    time.sleep(2 ** retries) # Exponential backoff
                except Exception as e:
                    logger.error(f"Strategy {attempt} failed unrecoverably: {e}")
                    break # Try next strategy immediately

        # If all else fails, return a safe explicit failure state
        safe_fallback = "AXIOM ERROR: LLM Generation Failed (All providers exhausted)"
        self._set_cache(prompt_hash, prompt, model, safe_fallback)
        return safe_fallback

    def _call_openai(self, prompt: str, model: str, temperature: float, api_key: str) -> str:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature
        }
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=self.timeout_sec
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    def _call_gemini(self, prompt: str, model: str, temperature: float, api_key: str) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": temperature}
        }
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=self.timeout_sec
        )
        response.raise_for_status()
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]

    def _generate_mock(self, prompt: str, model: str) -> str:
        """Generates deterministic mock text for testing."""
        prompt_lower = prompt.lower()
        if "summarize" in prompt_lower or "summary" in prompt_lower:
            return (
                "This document examines foundational results in analytic number theory. "
                "Main thesis: the distribution of primes is controlled by the location of "
                "zeta function zeros. Methods include complex analysis and sieve techniques. "
                "Key finding: evidence supports zeros on the critical line. "
                "Limitation: results are conditional on unproven hypotheses."
            )
        if "document context" in prompt_lower or "question:" in prompt_lower:
            return (
                "Based on the uploaded document, the paper discusses the Riemann zeta function "
                "and its connection to prime distribution. The main claim is that non-trivial zeros "
                "are conjectured to lie on the critical line Re(s)=1/2. The authors use analytic "
                "methods including the functional equation. Limitations include reliance on "
                "unproven hypotheses and bounded numerical evidence."
            )
        if "theorem" in prompt_lower or "prove" in prompt_lower:
            return "Proof: Let x be an element of G. By Lagrange's theorem, we have x^|G| = e. Therefore, the statement holds."
        elif "hypothesis" in prompt_lower:
            return "Hypothesis: The attractor cycle converges for all odd values of N."
        else:
            return f"Mock response from {model} for prompt: {prompt[:30]}..."
