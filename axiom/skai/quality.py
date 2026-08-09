"""Source quality assessment engine (SKAI §4)."""

from __future__ import annotations

from axiom.skai.models import SourceProvenance, SourceQualityTier, SourceType, QUALITY_RANK


def assess_source_quality(
    source_type: SourceType,
    *,
    has_peer_review: bool = False,
    is_preprint: bool = False,
    is_formal_library: bool = False,
    is_secondary: bool = False,
    is_web: bool = False,
) -> SourceQualityTier:
    if has_peer_review:
        return SourceQualityTier.PEER_REVIEWED_PRIMARY
    if is_preprint or source_type == SourceType.PREPRINT:
        return SourceQualityTier.PRIMARY_PREPRINT
    if is_formal_library or source_type == SourceType.FORMAL_LIBRARY:
        return SourceQualityTier.ESTABLISHED_TECHNICAL
    if source_type in (SourceType.REPOSITORY, SourceType.BENCHMARK, SourceType.DATASET):
        return SourceQualityTier.RESEARCH_REPOSITORY
    if is_secondary:
        return SourceQualityTier.SECONDARY_ANALYSIS
    if is_web or source_type == SourceType.WEB:
        return SourceQualityTier.GENERAL_WEB
    if source_type == SourceType.RESEARCH_PAPER:
        return SourceQualityTier.PRIMARY_PREPRINT
    if source_type == SourceType.BOOK:
        return SourceQualityTier.ESTABLISHED_TECHNICAL
    return SourceQualityTier.UNVERIFIED


def reliability_score(tier: SourceQualityTier) -> float:
    return QUALITY_RANK.get(tier, 0) / 6.0


def apply_quality(source: SourceProvenance) -> SourceProvenance:
    tier = assess_source_quality(
        source.source_type,
        has_peer_review=source.metadata.get("peer_reviewed", False),
        is_preprint=source.source_type == SourceType.PREPRINT,
        is_formal_library=source.source_type == SourceType.FORMAL_LIBRARY,
        is_secondary=source.metadata.get("secondary", False),
        is_web=source.source_type == SourceType.WEB,
    )
    source.quality_tier = tier
    source.reliability_score = reliability_score(tier)
    return source
