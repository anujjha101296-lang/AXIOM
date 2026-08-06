"""Tests for Autonomous Research Loop v1 (Milestone 005)."""

from __future__ import annotations

import asyncio

import pytest

from axiom.research_loop.benchmarks import get_benchmark, list_benchmarks, score_benchmark
from axiom.research_loop.claims import classify_claim, claim_from_statement
from axiom.research_loop.failure_memory import FailureMemoryStore, fingerprint_approach
from axiom.research_loop.schema import ClaimStatus, EvidenceItem, ResearchRunConfig, ResearchState
from axiom.research_loop.engine import ResearchLoopEngine
from axiom.research_loop.roles import RESEARCH_LOOP_ROLES


@pytest.fixture
def loop_engine(tmp_path):
    db = str(tmp_path / "loop.db")
    engine = ResearchLoopEngine(db_path=db)
    yield engine
    engine.store.close()
    engine.failure_memory.close()


class TestClaimClassification:
    def test_speculative_without_evidence(self):
        assert classify_claim("This might be true", []) == ClaimStatus.SPECULATIVE

    def test_supported_with_evidence(self):
        ev = EvidenceItem(source="test", content="data")
        assert classify_claim("Result holds for all n", [ev]) == ClaimStatus.SUPPORTED

    def test_known_keyword(self):
        assert classify_claim("It is well-known that primes are infinite", []) == ClaimStatus.KNOWN


class TestFailureMemory:
    def test_blocks_repeated_approach(self, tmp_path):
        store = FailureMemoryStore(str(tmp_path / "fail.db"))
        from axiom.research_loop.schema import FailedAttemptRecord
        attempt = FailedAttemptRecord(
            approach="Try n^2 formula for sum",
            reason_attempted="test",
            failure_reason="incorrect",
            fingerprint=fingerprint_approach("Try n^2 formula for sum"),
        )
        store.record_failure("run-1", attempt)
        assert store.is_blocked("Try n^2 formula for sum", run_id="run-1")
        store.close()

    def test_fingerprint_normalization(self):
        a = fingerprint_approach("Hello   World")
        b = fingerprint_approach("hello world")
        assert a == b


class TestBenchmarks:
    def test_benchmarks_exist(self):
        benches = list_benchmarks()
        assert len(benches) >= 4
        assert all(b.hidden_solution for b in benches)

    def test_hidden_solution_not_in_problem(self):
        for b in list_benchmarks():
            assert b.hidden_solution not in b.problem_statement

    def test_score_sum_formula(self):
        report = "The sum equals n(n+1)/2. For n=100, we get 5050."
        score = score_benchmark("bench_sum_formula", report, [])
        assert score >= 0.6


class TestRoles:
    def test_roles_have_distinct_responsibilities(self):
        roles = list(RESEARCH_LOOP_ROLES.values())
        missions = {r.worker_type: r.responsibilities for r in roles}
        assert missions["research_planner"] != missions["skeptic_critic"]
        assert missions["hypothesis_generator"] != missions["evidence_verifier"]
        for role in roles:
            assert role.success_criteria
            assert role.failure_criteria


class TestResearchLoopEngine:
    def test_full_loop_sum_benchmark(self, loop_engine):
        state = loop_engine.create_benchmark_run(
            "bench_sum_formula",
            ResearchRunConfig(max_iterations=2),
        )
        result = asyncio.run(loop_engine.run(state.run_id))
        assert result.final_report
        assert len(result.subproblems) >= 2
        assert len(result.hypotheses) >= 1
        assert result.current_phase.value in ("completed", "report")

    def test_failure_memory_prevents_duplicate(self, loop_engine):
        state = loop_engine.create_run(
            "Find closed form for 1+2+...+n",
            ResearchRunConfig(max_iterations=1),
        )
        fp = fingerprint_approach("The sum 1+2+...+n equals n(n+1)/2")
        from axiom.research_loop.schema import FailedAttemptRecord
        loop_engine.failure_memory.record_failure(
            state.run_id,
            FailedAttemptRecord(
                approach="The sum 1+2+...+n equals n(n+1)/2",
                reason_attempted="prior",
                failure_reason="test block",
                fingerprint=fp,
            ),
        )
        result = asyncio.run(loop_engine.run(state.run_id))
        assert any("Blocked" in u or "blocked" in u.lower() for u in result.uncertainties) or result.failed_attempts

    def test_human_reject_hypothesis(self, loop_engine):
        state = loop_engine.create_run("Test prime infinitude", ResearchRunConfig(max_iterations=1))
        asyncio.run(loop_engine.run(state.run_id))
        updated = loop_engine.get_state(state.run_id)
        if updated and updated.hypotheses:
            hid = updated.hypotheses[0].id
            loop_engine.reject_hypothesis(state.run_id, hid, "Not relevant")
            final = loop_engine.get_state(state.run_id)
            assert any(h.rejected for h in final.hypotheses)

    def test_add_evidence(self, loop_engine):
        state = loop_engine.create_run("Euler polyhedron formula", ResearchRunConfig(max_iterations=1))
        loop_engine.add_evidence(state.run_id, "textbook", "V-E+F=2 for convex polyhedra")
        updated = loop_engine.get_state(state.run_id)
        assert len(updated.evidence) == 1
        assert updated.human_interventions == 1

    def test_pause_and_cancel_flags(self, loop_engine):
        state = loop_engine.create_run("Quick test", ResearchRunConfig(max_iterations=1))
        asyncio.run(loop_engine.pause(state.run_id))
        asyncio.run(loop_engine.cancel(state.run_id))


class TestResearchLoopAPI:
    def test_create_and_list_runs(self, tmp_path, monkeypatch):
        monkeypatch.setenv("DB_PATH", str(tmp_path / "api_loop.db"))
        from fastapi.testclient import TestClient
        import axiom.services.api_gateway.routes.research_loop as rl_routes
        rl_routes._engine = None
        from axiom.services.api_gateway.main import app

        client = TestClient(app, headers={"Authorization": "Bearer test_token"})
        res = client.post(
            "/research-loop/runs",
            json={"research_question": "Find the sum formula for 1+2+...+n integers"},
        )
        assert res.status_code == 201, res.text
        run_id = res.json()["run_id"]

        res = client.get("/research-loop/runs")
        assert res.status_code == 200
        assert any(r["id"] == run_id for r in res.json())

        res = client.get("/research-loop/benchmarks")
        assert res.status_code == 200
        assert len(res.json()) >= 4

        res = client.get("/research-loop/roles")
        assert res.status_code == 200
        assert len(res.json()) >= 8

    def test_benchmark_run_starts(self, tmp_path, monkeypatch):
        monkeypatch.setenv("DB_PATH", str(tmp_path / "bench_api.db"))
        import axiom.services.api_gateway.routes.research_loop as rl_routes
        rl_routes._engine = None
        from axiom.services.api_gateway.main import app
        from fastapi.testclient import TestClient

        client = TestClient(app, headers={"Authorization": "Bearer test_token"})
        res = client.post(
            "/research-loop/benchmarks/run",
            json={"benchmark_id": "bench_euler_polyhedra", "max_iterations": 2},
        )
        assert res.status_code == 201, res.text
        assert res.json()["run_id"]
