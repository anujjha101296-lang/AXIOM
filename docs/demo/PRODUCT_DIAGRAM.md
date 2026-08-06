# AXIOM Golden Demo — Product Diagram

```mermaid
flowchart LR
    subgraph Input
        Q["Research Question"]
        P["Papers"]
    end

    subgraph AXIOM["AXIOM Research Session"]
        direction TB
        Ingest["📄 Ingest & Read"]
        Extract["🧠 Extract Knowledge"]
        Graph["🔗 Build Relationships"]
        Notes["📝 Create Notes"]
        Analyze["⚡ Find Contradictions"]
        Gaps["🔍 Identify Gaps"]
        Hyp["💡 Suggest Hypotheses"]
        Plan["🧪 Plan Experiments"]
        Report["📊 Produce Report"]
    end

    subgraph Output
        R["Research Program"]
        M["Session Memory"]
    end

    Q --> Ingest
    P --> Ingest
    Ingest --> Extract --> Graph --> Notes --> Analyze --> Gaps --> Hyp --> Plan --> Report
    Report --> R
    Report --> M
```

## User Journey (5 minutes)

| Step | User sees | Value |
|------|-----------|-------|
| 1 | Project + question | Clarity of intent |
| 2 | Papers reading | Ingest without manual note-taking |
| 3 | Knowledge graph | Relationships made visible |
| 4 | Notes | Structured, searchable insights |
| 5 | Contradictions | Intellectual honesty |
| 6 | Gaps | Where to contribute |
| 7 | Hypotheses | Testable science |
| 8 | Experiments | Actionable lab plan |
| 9 | Report | Deliverable output |

## Product Positioning

**AXIOM is not a chatbot.** It is a research session that produces structured, evidence-classified outputs with memory.

| ChatGPT | AXIOM Golden Demo |
|---------|-------------------|
| Conversational | Session-based |
| Ephemeral | Remembers full context |
| Unstructured prose | Graph, notes, report |
| No contradiction handling | Explicit conflict resolution |
| No experiment planning | Linked hypotheses → experiments |
