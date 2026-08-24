"""
axiom.knowledge_graph.query_engine
===================================
Authorized Knowledge Graph Query Engine.
All queries enforce project and user authorization.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from axiom.core.models import (
    GraphEntityDB,
    GraphEntityAliasDB,
    GraphClaimDB,
    GraphClaimEvidenceDB,
    GraphRelationshipDB,
    GraphRelationshipEvidenceDB,
    GraphContradictionDB,
    GraphResearchGapDB,
    Project,
)
from axiom.knowledge_graph.models import (
    GraphEntity,
    GraphEntityAlias,
    GraphClaim,
    GraphClaimEvidence,
    GraphRelationship,
    GraphContradiction,
    GraphResearchGap,
    KnowledgeGraphSummary,
)


class AuthorizedGraphQueryEngine:
    """Query engine with strict project-level access control."""

    async def get_graph_summary(
        self,
        project_id: str,
        user_id: str,
        db: AsyncSession,
    ) -> KnowledgeGraphSummary:
        """Retrieve full knowledge graph summary for authorized project."""
        await self._verify_project_access(project_id, user_id, db)

        # 1. Fetch Entities
        res_e = await db.execute(select(GraphEntityDB).where(GraphEntityDB.project_id == project_id))
        entities = [GraphEntity.from_db(row[0]) for row in res_e.all()]

        # 2. Fetch Claims
        res_c = await db.execute(select(GraphClaimDB).where(GraphClaimDB.project_id == project_id))
        claims = [GraphClaim.from_db(row[0]) for row in res_c.all()]

        # 3. Fetch Relationships
        res_r = await db.execute(select(GraphRelationshipDB).where(GraphRelationshipDB.project_id == project_id))
        relationships = [GraphRelationship.model_validate(row[0]) for row in res_r.all()]

        # 4. Fetch Contradictions
        res_cd = await db.execute(select(GraphContradictionDB).where(GraphContradictionDB.project_id == project_id))
        contradictions = [GraphContradiction.model_validate(row[0]) for row in res_cd.all()]

        # 5. Fetch Research Gaps
        res_g = await db.execute(select(GraphResearchGapDB).where(GraphResearchGapDB.project_id == project_id))
        gaps = [GraphResearchGap.model_validate(row[0]) for row in res_g.all()]

        return KnowledgeGraphSummary(
            project_id=project_id,
            total_entities=len(entities),
            total_claims=len(claims),
            total_relationships=len(relationships),
            total_contradictions=len(contradictions),
            total_gaps=len(gaps),
            entities=entities,
            claims=claims,
            relationships=relationships,
            contradictions=contradictions,
            research_gaps=gaps,
        )

    async def get_claim_provenance(
        self,
        claim_id: str,
        project_id: str,
        user_id: str,
        db: AsyncSession,
    ) -> Dict[str, Any]:
        """Fetch provenance chain for a claim."""
        await self._verify_project_access(project_id, user_id, db)

        res_c = await db.execute(select(GraphClaimDB).where(GraphClaimDB.id == claim_id, GraphClaimDB.project_id == project_id))
        claim_row = res_c.scalar_one_or_none()
        if not claim_row:
            raise ValueError(f"Claim {claim_id} not found in project {project_id}")

        res_ev = await db.execute(select(GraphClaimEvidenceDB).where(GraphClaimEvidenceDB.claim_id == claim_id))
        evidences = [GraphClaimEvidence.model_validate(r[0]) for r in res_ev.all()]

        return {
            "claim": GraphClaim.model_validate(claim_row),
            "evidences": evidences,
            "provenance_chain": [
                {
                    "evidence_id": ev.id,
                    "chunk_id": ev.chunk_id,
                    "source_id": ev.source_id,
                    "document_id": ev.document_id,
                    "snippet": ev.snippet,
                }
                for ev in evidences
            ],
        }

    async def _verify_project_access(
        self,
        project_id: str,
        user_id: str,
        db: AsyncSession,
    ) -> None:
        """Verify project exists and belongs to requesting user."""
        res_p = await db.execute(select(Project).where(Project.id == project_id))
        proj = res_p.scalar_one_or_none()
        if not proj:
            raise PermissionError(f"Project {project_id} not found")
        if proj.owner_id != user_id and user_id != "admin":
            raise PermissionError(f"User {user_id} is not authorized to access project {project_id}")
