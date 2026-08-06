# AXIOM Golden Demo — System Diagram

```mermaid
flowchart TB
    subgraph Presentation["Presentation Layer"]
        Play["Auto-Play Engine"]
        Tour["Interactive Tour"]
        Viz["Visualizations<br/>Graph · Tree · Timeline"]
    end

    subgraph Application["Application Layer"]
        PhaseSM["Phase State Machine"]
        Anim["Animation Controller"]
    end

    subgraph Service["Service Layer"]
        DemoAPI["Demo API<br/>GET /demo/state<br/>GET /demo/tour<br/>GET /demo/health"]
    end

    subgraph Data["Data Layer"]
        Curated["Curated Demo State<br/>9 nodes · 8 edges · 3 papers"]
        Sample["Sample Dataset<br/>demo/sample_dataset/"]
    end

    Play --> PhaseSM
    Tour --> PhaseSM
    PhaseSM --> Anim
    Anim --> Viz
    PhaseSM --> DemoAPI
    DemoAPI --> Curated
    Curated --- Sample
```

## Phase State Machine

```
intro → question → papers → extracting → graph → notes
  → contradictions → gaps → hypotheses → experiments → report → complete
```

| Phase | Duration | UI reveal |
|-------|----------|-----------|
| intro | 2s | Hero + CTA |
| question | 2.5s | Research question card |
| papers | 4s | 3 papers sequential read |
| extracting | 3.5s | Progress bar |
| graph | 3s | Evidence graph + stats |
| notes | 2.5s | Structured notes |
| contradictions | 2.5s | VS cards |
| gaps | 2s | Priority gaps |
| hypotheses | 2.5s | Confidence scores |
| experiments | 2.5s | Method + expected outcome |
| report | 3.5s | Full report |
| complete | — | Banner + replay |

## Deployment Topology

```
Browser → Next.js (port 3000) → FastAPI (port 8000) → /demo/state (in-memory)
```

No database required for Golden Demo operation.
