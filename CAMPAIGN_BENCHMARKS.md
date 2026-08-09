# Campaign Benchmarks

Benchmark categories for measuring FRCE improvement across releases.

| Category | Measures |
|----------|----------|
| Campaign planning | Strategy diversity, SIMR integration quality |
| Cycle execution | End-to-end cycle completion rate |
| Loop integration | SEC/E&R/FMTP calls per cycle |
| Pivot accuracy | Correct pivot vs continue decisions |
| Resource efficiency | Compute per contribution level |
| Checkpoint recovery | Resume from checkpoint fidelity |
| Human gate compliance | Gates triggered when required |
| Memory compounding | Global memory entries per campaign |
| Ladder advancement | Evidence-based level progression |
| Failure preservation | Failed approaches recorded, not lost |

## Health gate

```bash
make frce-health
```

## Target for GCP-2

First Tier 1 campaign:
- ≥ 3 complete research cycles
- ≥ 1 useful observation or verified result
- Full checkpoint journal
- Human review at contribution threshold
