"""
AXIOM Python SDK — v0.1.0 Founder Release
==========================================
Official Python Client for the AXIOM Epistemic & Scientific Research Platform.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
import urllib.request
import urllib.parse


class AxiomClient:
    """Synchronous / Async Python Client SDK for AXIOM REST API."""

    def __init__(self, base_url: str = "http://localhost:8000", token: str = "axiom-dev-token"):
        self.base_url = base_url.rstrip("/")
        self.token = token

    def _headers(self, user_id: Optional[str] = None) -> Dict[str, str]:
        h = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        if user_id:
            h["X-User-Id"] = user_id
        return h

    def _request(self, method: str, path: str, payload: Optional[Dict[str, Any]] = None, user_id: Optional[str] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        headers = self._headers(user_id)
        data = json.dumps(payload).encode("utf-8") if payload else None

        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        with urllib.request.urlopen(req) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body)

    # 1. Projects
    def list_projects(self) -> List[Dict[str, Any]]:
        return self._request("GET", "/api/v1/projects")

    def create_project(self, name: str, description: str = "") -> Dict[str, Any]:
        return self._request("POST", "/api/v1/projects", {"name": name, "description": description})

    # 2. Knowledge Graph (Phase 13)
    def get_knowledge_graph(self, project_id: str) -> Dict[str, Any]:
        return self._request("GET", f"/api/v1/knowledge-graph/summary/{project_id}")

    # 3. Hypotheses (Phase 14)
    def generate_hypotheses(self, project_id: str, question: str) -> List[Dict[str, Any]]:
        return self._request("POST", "/api/v1/hypothesis/generate", {"project_id": project_id, "question": question})

    # 4. Computational Experiments (Phase 15)
    def design_experiment(self, project_id: str, name: str, code_body: str) -> Dict[str, Any]:
        return self._request("POST", "/api/v1/experiment/design", {"project_id": project_id, "name": name, "code_body": code_body})

    def run_experiment(self, experiment_id: str) -> Dict[str, Any]:
        return self._request("POST", f"/api/v1/experiment/{experiment_id}/run")

    # 5. Formal Mathematics (Phase 16)
    def formalize_claim(self, project_id: str, natural_language: str) -> Dict[str, Any]:
        return self._request("POST", "/api/v1/formal-math/formalize", {"project_id": project_id, "natural_language": natural_language})

    def verify_lean_proof(self, theorem_id: str, proof_script: str) -> Dict[str, Any]:
        return self._request("POST", "/api/v1/formal-math/verify-lean", {"theorem_id": theorem_id, "proof_script": proof_script})
