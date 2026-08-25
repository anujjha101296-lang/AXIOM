"""
axiom.demo.seed
===============
Reproducible Golden Demo Seed Script.
Resets and populates a clean demo project, vector chunks, and formal statements.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from axiom.core.models import (
    Base,
    Project,
    User,
    ResearchSession,
    ResearchArtifact,
)
from axiom.core.database import sync_engine, SyncSessionLocal


def reset_and_seed_demo():
    """Reset database tables and seed clean Golden Demo data."""
    # Re-create tables
    Base.metadata.drop_all(bind=sync_engine)
    Base.metadata.create_all(bind=sync_engine)

    db = SyncSessionLocal()
    try:
        # Seed User
        u = User(id="user-demo", email="demo@axiom.com", hashed_password="hashed_demo_pw")
        db.add(u)

        # Seed Project
        p = Project(id="proj-demo", owner_id="user-demo", name="Golden Demo: Collatz & Integer Bounds", description="Reproducible pilot research project.")
        db.add(p)

        # Seed Session
        s = ResearchSession(id="sess-demo", project_id="proj-demo", goal="Investigate 3n+1 bounded trajectories and formalize base induction.")
        db.add(s)

        # Seed Artifact
        art = ResearchArtifact(
            id="art-demo",
            session_id="sess-demo",
            type="SUMMARY",
            content=json.dumps({"title": "Golden Demo Research Summary", "content": "Python Simulation: 10,000,000 cases passed. Lean 4 Verification: theorem thm_sum (n : Nat) : n + 0 = n := by rfl (VERIFIED)"}),
        )
        db.add(art)

        db.commit()
        print("Successfully reset and seeded clean Golden Demo environment.")
    finally:
        db.close()


if __name__ == "__main__":
    reset_and_seed_demo()
