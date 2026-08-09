"""Capability registry — seed and manage AXIOM capabilities (VF §1)."""

from __future__ import annotations

from axiom.vfactory.models import CapabilityRecord, VerificationState, _utc_now
from axiom.vfactory.store import VFactoryStore

# Canonical capability catalog seeded from verified repository audit
DEFAULT_CAPABILITIES: list[dict] = [
    {
        "capability_id": "cap_erl",
        "name": "Evidence & Reproducibility Loop",
        "description": "Claim registry, provenance graph, discovery gate, reproduction",
        "domain": "research",
        "owner": "platform",
        "dependencies": ["cap_tss", "cap_h1obs"],
        "acceptance_criteria": ["Claims versioned", "Discovery gate blocks false upgrades", "12 unit tests pass"],
        "unit_tests": ["tests/test_evidence_registry.py"],
        "health_check": "erl-health",
        "api_prefix": "/evidence",
        "source_paths": ["axiom/evidence/"],
    },
    {
        "capability_id": "cap_simr",
        "name": "Scientific Intelligence & Model Routing",
        "description": "Model/tool registries, router, research compiler",
        "domain": "ai",
        "dependencies": ["cap_erl"],
        "acceptance_criteria": ["Deterministic routing", "14 unit tests pass"],
        "unit_tests": ["tests/test_simr_routing.py"],
        "health_check": "simr-health",
        "api_prefix": "/routing",
        "source_paths": ["axiom/routing/"],
    },
    {
        "capability_id": "cap_fmtp",
        "name": "Formal Mathematics & Theorem-Proving",
        "description": "Prover registry, formalization, proof search, compilation gate",
        "domain": "scientific",
        "dependencies": ["cap_simr"],
        "acceptance_criteria": ["Truthfulness guards", "17 unit tests pass", "Prover validates artifacts"],
        "unit_tests": ["tests/test_formal_math.py"],
        "health_check": "fmtp-health",
        "api_prefix": "/formal",
        "source_paths": ["axiom/formal_math/"],
        "known_limitations": ["Lean required for real verification", "Coq/Isabelle stubs"],
    },
    {
        "capability_id": "cap_sec",
        "name": "Scientific Experimentation & Compute",
        "description": "Experiment kernel, sandbox, lifecycle, integrity gate",
        "domain": "research",
        "dependencies": ["cap_fmtp", "cap_tss"],
        "acceptance_criteria": ["Sandboxed execution", "12 unit tests pass", "No in-app exec"],
        "unit_tests": ["tests/test_experiment_sec.py"],
        "health_check": "sec-health",
        "api_prefix": "/experiments",
        "source_paths": ["axiom/experiment/"],
        "known_limitations": ["Subprocess sandbox only — TD-008"],
    },
    {
        "capability_id": "cap_frce",
        "name": "Frontier Research Campaign Engine",
        "description": "Campaign orchestration across research loops",
        "domain": "research",
        "dependencies": ["cap_sec", "cap_erl", "cap_simr", "cap_skai"],
        "acceptance_criteria": ["Full lifecycle", "14 unit tests pass", "Loop integration"],
        "unit_tests": ["tests/test_frce_campaign.py"],
        "health_check": "frce-health",
        "api_prefix": "/frce",
        "source_paths": ["axiom/campaign/"],
    },
    {
        "capability_id": "cap_skai",
        "name": "Knowledge Acquisition & Intelligence",
        "description": "Scientific knowledge graph, acquisition, conflict/gap detection",
        "domain": "knowledge",
        "dependencies": ["cap_erl"],
        "acceptance_criteria": ["Provenance tracking", "12 unit tests pass", "EGS bridge"],
        "unit_tests": ["tests/test_skai_knowledge.py"],
        "health_check": "skai-health",
        "api_prefix": "/skai",
        "source_paths": ["axiom/skai/"],
    },
    {
        "capability_id": "cap_gcp",
        "name": "Grand Challenge Program",
        "description": "Six-tier challenge registry, campaign management, gates",
        "domain": "research",
        "dependencies": ["cap_erl"],
        "acceptance_criteria": ["Tier 0 batch runs", "12 API tests pass"],
        "unit_tests": ["tests/test_grand_challenge.py"],
        "api_prefix": "/gcp",
        "source_paths": ["axiom/grand_challenge/"],
        "research_benchmarks": ["scripts/run_gcp_benchmark.py"],
    },
    {
        "capability_id": "cap_research_ws",
        "name": "Research Workspace",
        "description": "Projects, PDF upload, FTS search, Q&A, sessions",
        "domain": "product",
        "dependencies": [],
        "acceptance_criteria": ["Store CRUD works", "PDF extraction", "API auth"],
        "unit_tests": ["tests/test_research_workspace.py"],
        "api_prefix": "/research",
        "source_paths": ["axiom/research/", "ui/src/app/research/"],
        "known_limitations": ["Mock LLM without API keys"],
    },
    {
        "capability_id": "cap_workflow",
        "name": "Workflow Engine",
        "description": "Multi-agent task orchestration",
        "domain": "agent",
        "dependencies": [],
        "acceptance_criteria": ["API mounted", "Engine creates workflows"],
        "unit_tests": ["tests/test_workflow_mount.py"],
        "api_prefix": "/workflows",
        "source_paths": ["axiom/workflow/"],
        "known_limitations": ["Worker stubs", "No dedicated integration tests"],
    },
    {
        "capability_id": "cap_egs",
        "name": "Epistemic Graph Store",
        "description": "Knowledge graph persistence and migrations",
        "domain": "knowledge",
        "dependencies": [],
        "acceptance_criteria": ["Migrations v1-v4", "23 ontology tests pass"],
        "unit_tests": ["tests/test_epistemic_layer.py", "tests/test_mde_ontology.py"],
        "api_prefix": "/graph",
        "source_paths": ["axiom/core/knowledge_graph/"],
    },
    {
        "capability_id": "cap_tss",
        "name": "Trust Security & Safety",
        "description": "Production guard, secret scanner, route auth",
        "domain": "security",
        "dependencies": [],
        "acceptance_criteria": ["Startup audit", "Secret scan passes"],
        "security_tests": ["scripts/tss_security_check.py"],
        "source_paths": ["axiom/security/"],
    },
    {
        "capability_id": "cap_api_gateway",
        "name": "API Gateway",
        "description": "HTTP entry point, auth, all routers mounted",
        "domain": "api",
        "dependencies": [],
        "acceptance_criteria": ["/health", "/ready", "281+ core tests"],
        "unit_tests": ["tests/test_api.py"],
        "api_prefix": "/",
        "source_paths": ["axiom/services/api_gateway/"],
    },
    {
        "capability_id": "cap_cel",
        "name": "Continuous Evolution Loop",
        "description": "Governance artifacts and core test gate",
        "domain": "infrastructure",
        "dependencies": [],
        "acceptance_criteria": ["CEL health passes", "Scorecards exist"],
        "health_check": "cel-health",
        "source_paths": [".axiom/"],
    },
    {
        "capability_id": "cap_landing",
        "name": "Public Landing Page",
        "description": "Honest public product entry point",
        "domain": "product",
        "dependencies": ["cap_research_ws"],
        "acceptance_criteria": ["No mock metrics as real", "Links to /research"],
        "source_paths": ["ui/src/app/page.tsx"],
        "known_limitations": ["P0-WEB: mock data, dead waitlist"],
        "status": "UNTESTED",
    },
    {
        "capability_id": "cap_vfactory",
        "name": "Verification Factory",
        "description": "Permanent autonomous verification — registry, pyramid, journeys, scoring",
        "domain": "infrastructure",
        "dependencies": ["cap_api_gateway", "cap_tss"],
        "acceptance_criteria": [
            "Capability registry seeded",
            "Pyramid levels runnable",
            "User journeys A-D pass",
            "Verification score computed",
            "Health check passes",
        ],
        "unit_tests": ["tests/test_vfactory.py"],
        "health_check": "vfactory-health",
        "api_prefix": "/vfactory",
        "source_paths": ["axiom/vfactory/"],
    },
]


def seed_registry(store: VFactoryStore) -> list[CapabilityRecord]:
    """Initialize capability registry if empty."""
    existing = store.list_capabilities()
    if existing:
        return existing

    caps: list[CapabilityRecord] = []
    for spec in DEFAULT_CAPABILITIES:
        cap = CapabilityRecord(
            capability_id=spec["capability_id"],
            name=spec["name"],
            description=spec["description"],
            domain=spec.get("domain", "research"),
            owner=spec.get("owner", "platform"),
            dependencies=list(spec.get("dependencies", [])),
            acceptance_criteria=list(spec.get("acceptance_criteria", [])),
            unit_tests=list(spec.get("unit_tests", [])),
            integration_tests=list(spec.get("integration_tests", [])),
            e2e_tests=list(spec.get("e2e_tests", [])),
            security_tests=list(spec.get("security_tests", [])),
            performance_tests=list(spec.get("performance_tests", [])),
            research_benchmarks=list(spec.get("research_benchmarks", [])),
            known_limitations=list(spec.get("known_limitations", [])),
            health_check=spec.get("health_check"),
            api_prefix=spec.get("api_prefix"),
            source_paths=list(spec.get("source_paths", [])),
            status=VerificationState(spec.get("status", "UNTESTED")),
        )
        store.save_capability(cap)
        caps.append(cap)
    return caps


def update_capability_status(
    store: VFactoryStore,
    capability_id: str,
    *,
    passed: bool,
    evidence_id: str,
) -> CapabilityRecord | None:
    cap = store.get_capability(capability_id)
    if not cap:
        return None
    now = _utc_now()
    if passed:
        cap.status = VerificationState.VERIFIED
        cap.last_verified = now
    else:
        cap.status = VerificationState.REGRESSION
        cap.last_failed = now
    cap.verification_evidence.append(evidence_id)
    store.save_capability(cap)
    return cap
