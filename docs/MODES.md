# AXIOM Operation Modes

**Policy:** Demo Mode must never be confused with live scientific capability. Every demonstration and interface clearly indicates which mode is active.

---

## Two Modes

| | **Mode 1 — Demo Mode** | **Mode 2 — Research Mode** |
|---|--------------------------|----------------------------|
| **Purpose** | Presentation reliability | Real scientific work |
| **URL** | `/demo` | `/research`, `/research/runs` |
| **Data** | Curated sample dataset | Live PDF uploads, SQLite persistence |
| **Models** | None (pre-authored outputs) | ModelClient (live or mock fallback) |
| **Deterministic** | Yes — guaranteed completion | No — actual failures possible |
| **Uncertainty** | Hidden (by design) | Explicit and expected |
| **Represents scientific capability** | **No** | Yes (with limitations) |
| **Evidence on claims** | Illustrative only | Required — verify against sources |
| **Suitable for** | Conferences, YC, investors, onboarding | Daily research, lab pilots |

---

## Demo Mode Contract

- Uses curated datasets and deterministic outputs where appropriate
- Stable execution with guaranteed completion
- **Never** presented as measured AI or scientific capability
- Persistent **DEMO MODE** banner on all demo pages
- Report outputs carry `illustrative_only: true` and `mode_notice`
- API: `GET /demo/mode` returns `represents_scientific_capability: false`

```json
{
  "mode": "demo",
  "represents_scientific_capability": false,
  "data_source": "Curated sample dataset (pre-authored, in-memory)"
}
```

---

## Research Mode Contract

- Uses live PDFs, real retrieval, real search, actual AI models
- May produce uncertain, incomplete, or incorrect results
- Persistent **RESEARCH MODE** banner on workspace and loop pages
- Users must verify claims against source documents
- API: `GET /research/mode`, `GET /research-loop/mode`

```json
{
  "mode": "research",
  "represents_scientific_capability": true,
  "uncertainty_expected": true,
  "evidence_required": true
}
```

---

## Implementation

| Layer | Path |
|-------|------|
| Mode contracts (Python) | `axiom/modes.py` |
| Demo API mode endpoint | `GET /demo/mode` |
| Research API mode endpoint | `GET /research/mode` |
| Research loop mode endpoint | `GET /research-loop/mode` |
| UI banner component | `ui/src/components/OperationModeBanner.tsx` |
| Mode types (TypeScript) | `ui/src/lib/modes.ts` |

---

## Presenter Rules

1. **Always say "Demo Mode"** when showing `/demo`
2. **Never claim** demo outputs reflect live AI performance
3. **Transition explicitly** when switching to Research Mode: "Now let me show you the real workspace"
4. **Evidence accompanies** every research claim in Research Mode
5. When asked "is this real?" — answer with the active mode, not marketing language

---

## Constitution Alignment

This policy implements AXIOM Constitution principles:

- **Truth over theater** — modes are explicit, not hidden
- **Verification is explicit** — demo outputs labeled illustrative
- **No fabricated results** — demo does not claim to be live inference

See also: `docs/demo/PRESENTER_NOTES.md`, `docs/MILESTONE_006.md`, `MVP_READINESS.md`
