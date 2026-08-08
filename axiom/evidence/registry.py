"""Scientific claim registry and provenance graph store (E&R §1–2)."""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any

from axiom.evidence.discovery_gate import GateResult, validate_discovery_label, validate_status_upgrade
from axiom.evidence.models import (
    ClaimStatus,
    EvidenceObject,
    EvidenceType,
    ExperimentRecord,
    ProvenanceEdgeType,
    ScientificClaim,
    SourceRecord,
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


class ClaimRegistry:
    """SQLite-backed claim registry with provenance graph edges."""

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._persistent_conn: sqlite3.Connection | None = None
        if db_path == ":memory:":
            self._persistent_conn = sqlite3.connect(":memory:", check_same_thread=False)
            self._persistent_conn.row_factory = sqlite3.Row
        self._ensure_schema()

    def _conn(self) -> sqlite3.Connection:
        if self._persistent_conn is not None:
            return self._persistent_conn
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _release_conn(self, conn: sqlite3.Connection) -> None:
        if conn is not self._persistent_conn:
            conn.close()

    def _ensure_schema(self) -> None:
        conn = self._conn()
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS er_claims (
            claim_id TEXT PRIMARY KEY,
            version INTEGER NOT NULL,
            status TEXT NOT NULL,
            json_data TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS er_claim_versions (
            claim_id TEXT NOT NULL,
            version INTEGER NOT NULL,
            json_data TEXT NOT NULL,
            archived_at TEXT NOT NULL,
            PRIMARY KEY (claim_id, version)
        );
        CREATE TABLE IF NOT EXISTS er_evidence (
            evidence_id TEXT PRIMARY KEY,
            claim_id TEXT,
            json_data TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS er_sources (
            source_id TEXT PRIMARY KEY,
            json_data TEXT NOT NULL,
            retrieved_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS er_experiments (
            experiment_id TEXT PRIMARY KEY,
            json_data TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS er_provenance_edges (
            edge_id TEXT PRIMARY KEY,
            source_id TEXT NOT NULL,
            target_id TEXT NOT NULL,
            edge_type TEXT NOT NULL,
            json_data TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_er_evidence_claim ON er_evidence(claim_id);
        CREATE INDEX IF NOT EXISTS idx_er_edges_source ON er_provenance_edges(source_id);
        CREATE INDEX IF NOT EXISTS idx_er_edges_target ON er_provenance_edges(target_id);
        """)
        conn.commit()
        self._release_conn(conn)

    def register_claim(
        self,
        statement: str,
        *,
        author: str = "system",
        campaign_id: str | None = None,
        parent_claim_ids: list[str] | None = None,
        status: ClaimStatus = ClaimStatus.UNKNOWN,
    ) -> ScientificClaim:
        now = _utc_now()
        claim = ScientificClaim(
            claim_id=_new_id("clm"),
            statement=statement,
            status=status,
            version=1,
            created_at=now,
            updated_at=now,
            author=author,
            campaign_id=campaign_id,
            parent_claim_ids=parent_claim_ids or [],
        )
        self._save_claim(claim)
        return claim

    def _save_claim(self, claim: ScientificClaim) -> None:
        conn = self._conn()
        conn.execute(
            """INSERT OR REPLACE INTO er_claims
               (claim_id, version, status, json_data, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                claim.claim_id,
                claim.version,
                claim.status.value,
                json.dumps(claim.to_dict()),
                claim.created_at,
                claim.updated_at,
            ),
        )
        conn.commit()
        self._release_conn(conn)

    def _archive_version(self, claim: ScientificClaim) -> None:
        conn = self._conn()
        conn.execute(
            """INSERT OR REPLACE INTO er_claim_versions
               (claim_id, version, json_data, archived_at)
               VALUES (?, ?, ?, ?)""",
            (claim.claim_id, claim.version, json.dumps(claim.to_dict()), _utc_now()),
        )
        conn.commit()
        self._release_conn(conn)

    def get_claim(self, claim_id: str) -> ScientificClaim | None:
        conn = self._conn()
        row = conn.execute(
            "SELECT json_data FROM er_claims WHERE claim_id = ?", (claim_id,)
        ).fetchone()
        self._release_conn(conn)
        if not row:
            return None
        return _claim_from_dict(json.loads(row["json_data"]))

    def list_claims(self, limit: int = 100) -> list[ScientificClaim]:
        conn = self._conn()
        rows = conn.execute(
            "SELECT json_data FROM er_claims ORDER BY updated_at DESC LIMIT ?", (limit,)
        ).fetchall()
        self._release_conn(conn)
        return [_claim_from_dict(json.loads(r["json_data"])) for r in rows]

    def add_evidence(
        self,
        claim_id: str,
        evidence_type: EvidenceType,
        summary: str,
        *,
        source_id: str | None = None,
        experiment_id: str | None = None,
        provenance: dict[str, Any] | None = None,
        verifier: str | None = None,
        formally_verified: bool = False,
        supports: bool = True,
    ) -> EvidenceObject:
        claim = self.get_claim(claim_id)
        if not claim:
            raise KeyError(f"Claim not found: {claim_id}")

        if evidence_type == EvidenceType.FORMAL_PROOF and formally_verified and not verifier:
            raise ValueError("Formal proof evidence requires verifier identity")

        now = _utc_now()
        evidence = EvidenceObject(
            evidence_id=_new_id("evd"),
            evidence_type=evidence_type,
            summary=summary,
            created_at=now,
            claim_id=claim_id,
            source_id=source_id,
            experiment_id=experiment_id,
            provenance=provenance or {},
            verifier=verifier,
            formally_verified=formally_verified,
        )

        conn = self._conn()
        conn.execute(
            "INSERT INTO er_evidence (evidence_id, claim_id, json_data, created_at) VALUES (?, ?, ?, ?)",
            (evidence.evidence_id, claim_id, json.dumps(evidence.to_dict()), now),
        )
        conn.commit()
        self._release_conn(conn)

        self._archive_version(claim)
        if supports:
            claim.supporting_evidence_ids.append(evidence.evidence_id)
        else:
            claim.contradicting_evidence_ids.append(evidence.evidence_id)
        claim.version += 1
        claim.updated_at = now
        self._save_claim(claim)

        self.add_edge(
            evidence.evidence_id,
            claim_id,
            ProvenanceEdgeType.SUPPORTS if supports else ProvenanceEdgeType.CONTRADICTS,
        )
        return evidence

    def register_source(self, title: str, **kwargs: Any) -> SourceRecord:
        now = _utc_now()
        source = SourceRecord(
            source_id=kwargs.get("source_id") or _new_id("src"),
            title=title,
            retrieved_at=kwargs.get("retrieved_at", now),
            url=kwargs.get("url"),
            authors=kwargs.get("authors", []),
            publication=kwargs.get("publication"),
            content_hash=kwargs.get("content_hash"),
            extraction_method=kwargs.get("extraction_method"),
            version=kwargs.get("version"),
            metadata=kwargs.get("metadata", {}),
        )
        conn = self._conn()
        conn.execute(
            "INSERT OR REPLACE INTO er_sources (source_id, json_data, retrieved_at) VALUES (?, ?, ?)",
            (source.source_id, json.dumps(source.to_dict()), source.retrieved_at),
        )
        conn.commit()
        self._release_conn(conn)
        return source

    def register_experiment(
        self,
        objective: str,
        *,
        hypothesis: str | None = None,
        config: dict[str, Any] | None = None,
        environment: dict[str, Any] | None = None,
        result: dict[str, Any] | None = None,
        run_id: str | None = None,
    ) -> ExperimentRecord:
        now = _utc_now()
        experiment = ExperimentRecord(
            experiment_id=_new_id("exp"),
            objective=objective,
            hypothesis=hypothesis,
            created_at=now,
            config=config or {},
            environment=environment or {},
            result=result or {},
            run_id=run_id,
        )
        conn = self._conn()
        conn.execute(
            "INSERT INTO er_experiments (experiment_id, json_data, created_at) VALUES (?, ?, ?)",
            (experiment.experiment_id, json.dumps(experiment.to_dict()), now),
        )
        conn.commit()
        self._release_conn(conn)
        return experiment

    def add_edge(
        self,
        source_id: str,
        target_id: str,
        edge_type: ProvenanceEdgeType,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        edge_id = _new_id("edg")
        now = _utc_now()
        payload = {"source_id": source_id, "target_id": target_id, "edge_type": edge_type.value}
        if metadata:
            payload.update(metadata)
        conn = self._conn()
        conn.execute(
            """INSERT INTO er_provenance_edges
               (edge_id, source_id, target_id, edge_type, json_data, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (edge_id, source_id, target_id, edge_type.value, json.dumps(payload), now),
        )
        conn.commit()
        self._release_conn(conn)
        return edge_id

    def get_evidence_for_claim(self, claim_id: str) -> list[EvidenceObject]:
        conn = self._conn()
        rows = conn.execute(
            "SELECT json_data FROM er_evidence WHERE claim_id = ?", (claim_id,)
        ).fetchall()
        self._release_conn(conn)
        return [_evidence_from_dict(json.loads(r["json_data"])) for r in rows]

    def update_status(
        self,
        claim_id: str,
        new_status: ClaimStatus,
        *,
        reviewer: str | None = None,
    ) -> tuple[ScientificClaim, GateResult]:
        claim = self.get_claim(claim_id)
        if not claim:
            raise KeyError(f"Claim not found: {claim_id}")

        evidence = self.get_evidence_for_claim(claim_id)
        gate = validate_status_upgrade(claim, new_status, evidence, reviewer=reviewer)
        if not gate.allowed:
            return claim, gate

        self._archive_version(claim)
        claim.status = new_status
        claim.version += 1
        claim.updated_at = _utc_now()
        if reviewer:
            claim.reviewer = reviewer
        self._save_claim(claim)
        return claim, gate

    def add_discovery_label(
        self,
        claim_id: str,
        label: str,
        *,
        reproduction_passed: bool = False,
        independent_verification: bool = False,
        human_review: bool = False,
    ) -> tuple[ScientificClaim, GateResult]:
        claim = self.get_claim(claim_id)
        if not claim:
            raise KeyError(f"Claim not found: {claim_id}")

        evidence = self.get_evidence_for_claim(claim_id)
        gate = validate_discovery_label(
            claim,
            label,
            evidence,
            reproduction_passed=reproduction_passed,
            independent_verification=independent_verification,
            human_review=human_review,
        )
        if not gate.allowed:
            return claim, gate

        self._archive_version(claim)
        if label not in claim.labels:
            claim.labels.append(label)
        claim.version += 1
        claim.updated_at = _utc_now()
        self._save_claim(claim)
        return claim, gate

    def get_lineage(self, claim_id: str) -> dict[str, Any]:
        """Return supporting evidence, edges, and parent claims for a claim."""
        claim = self.get_claim(claim_id)
        if not claim:
            raise KeyError(f"Claim not found: {claim_id}")

        evidence = self.get_evidence_for_claim(claim_id)
        conn = self._conn()
        edges = conn.execute(
            """SELECT json_data FROM er_provenance_edges
               WHERE source_id = ? OR target_id = ?""",
            (claim_id, claim_id),
        ).fetchall()
        self._release_conn(conn)

        parents = [self.get_claim(pid) for pid in claim.parent_claim_ids]
        return {
            "claim": claim.to_dict(),
            "evidence": [e.to_dict() for e in evidence],
            "edges": [json.loads(r["json_data"]) for r in edges],
            "parents": [p.to_dict() for p in parents if p],
        }

    def dashboard_stats(self) -> dict[str, Any]:
        conn = self._conn()
        total = conn.execute("SELECT COUNT(*) FROM er_claims").fetchone()[0]
        by_status = {
            row[0]: row[1]
            for row in conn.execute(
                "SELECT status, COUNT(*) FROM er_claims GROUP BY status"
            ).fetchall()
        }
        evidence_count = conn.execute("SELECT COUNT(*) FROM er_evidence").fetchone()[0]
        experiment_count = conn.execute("SELECT COUNT(*) FROM er_experiments").fetchone()[0]
        formal = conn.execute(
            "SELECT COUNT(*) FROM er_evidence WHERE json_data LIKE '%\"formally_verified\": true%'"
        ).fetchone()[0]
        self._release_conn(conn)

        verified = by_status.get(ClaimStatus.VERIFIED.value, 0) + by_status.get(
            ClaimStatus.FORMALLY_VERIFIED.value, 0
        )
        unverified = total - verified - by_status.get(ClaimStatus.REJECTED.value, 0)

        return {
            "total_claims": total,
            "by_status": by_status,
            "verified_claims": verified,
            "unverified_claims": unverified,
            "rejected_claims": by_status.get(ClaimStatus.REJECTED.value, 0),
            "formal_proofs": formal,
            "evidence_objects": evidence_count,
            "experiments": experiment_count,
            "evidence_coverage": round(evidence_count / total, 2) if total else 0.0,
        }


def _claim_from_dict(data: dict[str, Any]) -> ScientificClaim:
    return ScientificClaim(
        claim_id=data["claim_id"],
        statement=data["statement"],
        status=ClaimStatus(data["status"]),
        version=data["version"],
        created_at=data["created_at"],
        updated_at=data["updated_at"],
        author=data.get("author", "system"),
        campaign_id=data.get("campaign_id"),
        parent_claim_ids=data.get("parent_claim_ids", []),
        confidence=data.get("confidence", 0.0),
        reviewer=data.get("reviewer"),
        supporting_evidence_ids=data.get("supporting_evidence_ids", []),
        contradicting_evidence_ids=data.get("contradicting_evidence_ids", []),
        source_ids=data.get("source_ids", []),
        experiment_ids=data.get("experiment_ids", []),
        labels=data.get("labels", []),
        limitations=data.get("limitations", []),
    )


def _evidence_from_dict(data: dict[str, Any]) -> EvidenceObject:
    return EvidenceObject(
        evidence_id=data["evidence_id"],
        evidence_type=EvidenceType(data["evidence_type"]),
        summary=data["summary"],
        created_at=data["created_at"],
        claim_id=data.get("claim_id"),
        source_id=data.get("source_id"),
        experiment_id=data.get("experiment_id"),
        provenance=data.get("provenance", {}),
        verifier=data.get("verifier"),
        formally_verified=data.get("formally_verified", False),
    )


_registry_cache: dict[str, ClaimRegistry] = {}


def get_claim_registry(db_path: str) -> ClaimRegistry:
    if db_path not in _registry_cache:
        _registry_cache[db_path] = ClaimRegistry(db_path)
    return _registry_cache[db_path]
