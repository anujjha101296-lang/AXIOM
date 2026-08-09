# Scientific Knowledge Graph Specification

## Node types

- Theorem, Lemma, Definition, Conjecture, Experiment, Hypothesis, Method, Dataset, Result, Limitation, Open Question, Counterexample

## Relation types

- `depends_on`, `proves`, `refutes`, `extends`, `cites`, `uses`, `contradicts`, `supports`, `formalized_as`, `leaves_open`, `challenges`

## Example structures

```text
Theorem A → depends_on → Lemma B → uses → Definition C
Paper X → proves → Theorem A → extends → Paper Y
Conjecture Q → supported_by → Experiment E → challenged_by → Paper P
```

## Storage

- **SKAI store** (`skai_entities`, `skai_relations`) — structured extraction
- **EGS** (`EpistemicStore`) — bridged nodes and edges
- **E&R** (`ClaimRegistry`) — claims with evidence tiers

## Provenance

Every entity links to `source_id` with: version, authors, date, identifier, content hash, extraction method, quality tier.
