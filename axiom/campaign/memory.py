"""Campaign and global research memory (FRCE §12, §13)."""

from __future__ import annotations

from axiom.campaign.models import (
    CycleRecord,
    FrontierCampaign,
    ResearchMemoryEntry,
    _new_id,
)
from axiom.campaign.store import CampaignEngineStore


def record_cycle_memory(
    campaign: FrontierCampaign,
    cycle: CycleRecord,
) -> ResearchMemoryEntry:
    """Capture institutional memory from a completed cycle."""
    entry = ResearchMemoryEntry(
        entry_id=_new_id("mem"),
        cycle_number=cycle.cycle_number,
        what_learned="; ".join(cycle.learned) if cycle.learned else "No new learnings recorded",
        what_failed="; ".join(cycle.failed_approaches) if cycle.failed_approaches else "No failures",
        assumptions_changed=campaign.context.get("assumptions_changed", ""),
        exhausted_approaches=[
            s.name for s in campaign.strategies if s.status == "exhausted"
        ],
        promising_approaches=[
            s.name for s in campaign.strategies if s.status in ("active", "selected")
        ],
        new_questions=campaign.context.get("new_questions", []),
        tools_that_worked=campaign.context.get("tools_that_worked", []),
        models_that_failed=campaign.context.get("models_that_failed", []),
        never_repeat=campaign.failed_approaches[-3:],
    )
    campaign.memory.append(entry)
    return entry


def compound_to_global_memory(
    store: CampaignEngineStore,
    campaign: FrontierCampaign,
) -> list[str]:
    """
    Flow useful results into global research memory (FRCE §13).

    Provenance remains intact — speculative ideas stay labeled.
    """
    entry_ids: list[str] = []
    for mem in campaign.memory:
        global_entry = {
            **mem.to_dict(),
            "source_campaign_id": campaign.campaign_id,
            "source_campaign_name": campaign.name,
            "ladder_level": int(campaign.ladder_level),
            "contribution_level": campaign.contribution_level.value,
            "provenance_note": "Derived from campaign memory; not established fact",
        }
        eid = store.save_global_memory(campaign.campaign_id, global_entry)
        entry_ids.append(eid)
    return entry_ids
