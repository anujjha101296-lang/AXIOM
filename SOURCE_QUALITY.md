# Source Quality Engine

## Quality tiers (highest to lowest)

1. **Peer-reviewed primary research**
2. **Primary preprint**
3. **Established technical source** (books, formal libraries)
4. **Research repository** (datasets, benchmarks)
5. **Secondary analysis**
6. **General web source**
7. **Unverified claim**

Lower tiers are not useless — quality is **explicit metadata**, not implicit trust.

## Reliability score

`reliability_score = tier_rank / 6.0`

## Application

Every source passes through `apply_quality()` before storage. Campaign-scoped and private sources retain their scope.
