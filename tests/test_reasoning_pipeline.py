import pytest
import os
import tempfile
from fastapi.testclient import TestClient

from axiom.core.verification.smt_gateway import SmtGateway
from axiom.core.verification.lean_exporter import LeanExporter
from axiom.core.reasoning.mcts import MctsSolver
from axiom.services.api_gateway.main import app

client = TestClient(app)
headers = {"Authorization": "Bearer test_token"}

def test_smt_gateway():
    smt = SmtGateway()
    
    # x + y == z mod 5 is valid (no counterexamples when inputs are bound, wait - actually modular equations can be verified.
    # Let's test a simple valid claim: (x + y) == (x + y) mod 5
    is_valid, counterexample = smt.verify_modular_conjecture(
        equation="x + y == x + y",
        modulus=5,
        variables=["x", "y"]
    )
    assert is_valid is True
    assert counterexample is None

    # (x + y) == 0 mod 5 is refuted (since x=1, y=1 => 2 != 0)
    is_valid_refuted, counterexample_refuted = smt.verify_modular_conjecture(
        equation="x + y == 0",
        modulus=5,
        variables=["x", "y"]
    )
    assert is_valid_refuted is False
    assert counterexample_refuted is not None
    assert "x" in counterexample_refuted
    assert "y" in counterexample_refuted

def test_mcts_solver():
    solver = MctsSolver(max_iterations=100)
    
    # Simple reduction: x + 0 -> x
    steps = solver.solve("x + 0", "x")
    assert steps is not None
    assert len(steps) >= 1
    assert steps[0][0] == "IDENTITY_ADD"
    assert steps[0][1] == "x"

def test_lean_exporter():
    exporter = LeanExporter()
    
    variables = {"x": "Int", "y": "Int", "m": "Nat"}
    code = exporter.export_theorem(
        name="modular addition commutativity",
        statement="(x + y) % m = (y + x) % m",
        variables=variables,
        proof_body="rfl"
    )
    
    assert "import Mathlib.Data.Int.Basic" in code
    assert "theorem modular_addition_commutativity" in code
    assert "(x y : ℤ) (m : ℕ)" in code
    assert "rfl" in code

def test_api_conjecture_endpoint():
    payload = {
        "conjecture_name": "Sum modular bound check",
        "equation": "x + 0 == x",
        "modulus": 10,
        "variables": ["x"]
    }
    response = client.post("/verify/conjecture", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["is_valid"] is True
    assert data["epistemic_status"] == "VERIFIED"
    assert data["verification_tier"] == 2

def test_api_proof_endpoint():
    payload = {
        "theorem_name": "Simplification Proof Test",
        "start_expression": "x * 1 + 0",
        "target_expression": "x",
        "variables": {"x": "Int"}
    }
    response = client.post("/verify/proof", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["is_proven"] is True
    assert len(data["proof_steps"]) >= 1
    assert "lean_file" in data

def test_api_graph_export():
    # Make sure we can retrieve the graph from EGS store
    response = client.get("/graph", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
    # Check that nodes added in previous tests exist
    node_names = [n["name"] for n in data["nodes"]]
    assert "Sum modular bound check" in node_names
    assert "Simplification Proof Test" in node_names
