# AXIOM Golden Demo — Presenter Notes

**Duration:** 5 minutes (auto-play) · 8–10 minutes (with Q&A)  
**Audience:** Researchers, YC partners, investors, engineers, enterprise

---

## Opening (30 seconds)

> "Imagine you just picked up a new research area. Three papers, a vague question, and a deadline. Watch what AXIOM does — no slides."

Click **▶ Play Demo**. Do not narrate over the intro — let the UI breathe.

---

## Act 1 — The Question (0:30–1:00)

**On screen:** Research question card appears.

**Say:**
> "Every AXIOM session starts with a precise question. This one asks when graph neural networks actually generalize across molecular scaffolds — the kind of question that matters for drug discovery."

**Highlight:** The question stays visible throughout the session as the north star.

---

## Act 2 — Paper Ingestion (1:00–2:00)

**On screen:** Three papers upload and read sequentially.

**Say:**
> "Three foundational papers — Gilmer on message passing, Hu on pre-training, Sun on out-of-distribution failure. AXIOM reads them, extracts text, and surfaces summaries automatically."

**Pause if audience asks:** "In production, these are real PDFs via the Research Workspace."

---

## Act 3 — Knowledge Graph (2:00–2:45)

**On screen:** Evidence graph animates; stats appear.

**Say:**
> "Nine concepts, eight relationships — methods, findings, gaps, even contradictions. Every node has an evidence tier. This isn't a pretty picture — it's an inspectable knowledge structure."

**For engineers:** Mention `GET /demo/state` returns full graph JSON.

---

## Act 4 — Contradictions & Gaps (2:45–3:30)

**On screen:** Contradictions with VS layout; gap cards.

**Say:**
> "AXIOM doesn't smooth over conflicts. Gilmer says depth saturates at four layers; Hu shows deeper pre-trained encoders help transfer. Sun shows pre-training doesn't fix scaffold OOD. These are flagged with resolution paths — not hidden."

---

## Act 5 — Hypotheses & Experiments (3:30–4:15)

**On screen:** Hypothesis cards with confidence; experiment plans.

**Say:**
> "Three testable hypotheses, each linked to an experiment with method and expected outcome. This is ready for a lab meeting — not a chat transcript."

---

## Act 6 — Report (4:15–5:00)

**On screen:** Professional report with sections.

**Say:**
> "A publication-ready synthesis in four minutes. AXIOM remembered the full session — papers, contradictions, gaps, plan. That's the product: research memory that compounds."

**Close:**
> "Questions? The Research Workspace is live at `/research`. This demo is at `/demo` anytime."

---

## Q&A Cheat Sheet

| Question | Answer |
|----------|--------|
| Is this real AI? | Demo uses curated data for reliability; workspace uses real PDFs + model gateway |
| vs ChatGPT? | AXIOM structures evidence, tracks contradictions, plans experiments, remembers sessions |
| Production ready? | Demo-ready; see `MVP_READINESS.md` for alpha blockers |
| Pricing? | Not yet — focused on researcher pilots |
| Can I try my papers? | Yes — sign in at `/login`, use Research Workspace |

---

## Do Not Say

- "AXIOM solved drug discovery"
- "Autonomous scientific discovery" (say "research orchestration")
- "Production SaaS ready" (say "demo-ready with documented limitations")

---

## Recovery Lines

- **API down:** "Let me show you the architecture diagram while we restart the server."
- **Animation glitch:** Switch to **Guided Tour** for manual stepping.
- **Skeptical researcher:** Open contradiction panel — "This is the honesty layer."
