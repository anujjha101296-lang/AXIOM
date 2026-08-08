"""Known-answer benchmark dataset — hundreds of problems with hidden answers."""

from __future__ import annotations

import json
from pathlib import Path

from axiom.research_validation.models import KnownAnswerProblem, ValidationStage

DATA_DIR = Path(__file__).parent / "data"


def _seed_problems() -> list[KnownAnswerProblem]:
    """Curated seed problems across validation categories."""
    seeds: list[KnownAnswerProblem] = [
        KnownAnswerProblem(
            id="ka_algebra_sum_n",
            stage=1,
            category="mathematical_olympiad",
            title="Sum of First n Integers",
            problem_statement="Find a closed-form formula for 1+2+...+n and verify for n=100.",
            difficulty="undergraduate",
            hidden_answer="n(n+1)/2; sum for n=100 is 5050",
            answer_keywords=["n(n+1)/2", "5050", "closed form", "gauss", "arithmetic"],
        ),
        KnownAnswerProblem(
            id="ka_nt_primes_infinite",
            stage=1,
            category="historical_theorem",
            title="Infinitude of Primes",
            problem_statement="Prove or justify that there are infinitely many primes.",
            difficulty="undergraduate",
            hidden_answer="Euclid's proof by contradiction on prime product + 1",
            answer_keywords=["euclid", "infinite", "contradiction", "prime", "product"],
        ),
        KnownAnswerProblem(
            id="ka_geom_euler_polyhedra",
            stage=1,
            category="historical_theorem",
            title="Euler's Polyhedron Formula",
            problem_statement="State and verify V - E + F = 2 for a cube.",
            difficulty="undergraduate",
            hidden_answer="V=8, E=12, F=6; V-E+F=2",
            answer_keywords=["v - e + f", "euler", "2", "cube", "8", "12", "6"],
        ),
        KnownAnswerProblem(
            id="ka_algo_binary_search",
            stage=1,
            category="algorithm_design",
            title="Binary Search Complexity",
            problem_statement="What is the time complexity of binary search on a sorted array of n elements?",
            difficulty="undergraduate",
            hidden_answer="O(log n)",
            answer_keywords=["o(log n)", "logarithm", "log n", "binary search"],
        ),
        KnownAnswerProblem(
            id="ka_sci_newton_second",
            stage=1,
            category="scientific_reasoning",
            title="Newton's Second Law",
            problem_statement="State Newton's second law and give units in SI for force.",
            difficulty="high_school",
            hidden_answer="F=ma; newton = kg·m/s²",
            answer_keywords=["f=ma", "force", "mass", "acceleration", "newton"],
        ),
        KnownAnswerProblem(
            id="ka_paper_repro_linear_reg",
            stage=2,
            category="paper_reproduction",
            title="Linear Regression MSE",
            problem_statement="Reproduce the MSE formula for linear regression with predictions ŷ and targets y.",
            difficulty="graduate",
            hidden_answer="MSE = (1/n) Σ(y - ŷ)²",
            answer_keywords=["mse", "mean squared error", "(y", "prediction", "1/n"],
        ),
    ]
    return seeds


def _expand_problems(seeds: list[KnownAnswerProblem]) -> list[KnownAnswerProblem]:
    """Programmatically expand dataset to hundreds of known-answer problems."""
    problems = list(seeds)
    idx = 0

    # Mathematical olympiad / contest style (50)
    olympiad_templates = [
        ("Find the remainder when {n} is divided by 7.", "{r}", ["remainder", "{r}"]),
        ("How many positive divisors does {n} have?", "{d}", ["divisor", "{d}"]),
        ("Solve x² - {a}x + {b} = 0 for integer roots.", "roots {r1}, {r2}", ["{r1}", "{r2}", "factor"]),
        ("Compute the sum of squares 1²+2²+...+{k}².", "{ans}", ["sum of squares", "{ans}"]),
        ("Is {p} prime? Justify.", "{yesno}", ["prime", "{yesno}"]),
    ]
    for i in range(50):
        t = olympiad_templates[i % len(olympiad_templates)]
        n = 10 + i * 3
        r = n % 7
        d = sum(1 for j in range(1, n + 1) if n % j == 0)
        a, b = 5 + i % 10, 6 + i % 8
        r1, r2 = 2, 3
        ans = n * (n + 1) * (2 * n + 1) // 6
        p = 17 + i * 2 if i % 3 else 15
        yesno = "yes" if p in (17, 19, 23, 29, 31) else "no"
        stmt = t[0].format(n=n, a=a, b=b, k=n, p=p)
        ans_text = t[1].format(r=r, d=d, r1=r1, r2=r2, ans=ans, yesno=yesno)
        kws = [k.format(r=r, d=d, r1=r1, r2=r2, ans=ans, yesno=yesno) for k in t[2]]
        problems.append(
            KnownAnswerProblem(
                id=f"ka_olympiad_{i:03d}",
                stage=1,
                category="mathematical_olympiad",
                title=f"Olympiad Problem {i + 1}",
                problem_statement=stmt,
                difficulty="contest",
                hidden_answer=ans_text,
                answer_keywords=kws,
            )
        )
        idx += 1

    # Historical theorem variants (30)
    theorems = [
        ("Pythagorean Theorem", "a²+b²=c² for right triangles", ["pythagorean", "a^2", "right"]),
        ("Fermat's Little Theorem", "a^(p-1) ≡ 1 (mod p) for prime p", ["fermat", "mod", "prime"]),
        ("Bayes' Theorem", "P(A|B) = P(B|A)P(A)/P(B)", ["bayes", "conditional", "probability"]),
        ("Fundamental Theorem of Calculus", "∫ₐᵇ f'(x)dx = f(b)-f(a)", ["fundamental", "calculus", "integral"]),
        ("Cauchy-Schwarz", "(Σaᵢbᵢ)² ≤ (Σaᵢ²)(Σbᵢ²)", ["cauchy", "schwarz", "inequality"]),
    ]
    for i in range(30):
        th = theorems[i % len(theorems)]
        problems.append(
            KnownAnswerProblem(
                id=f"ka_theorem_{i:03d}",
                stage=1,
                category="historical_theorem",
                title=f"{th[0]} (variant {i + 1})",
                problem_statement=f"State {th[0]} and give one application.",
                difficulty="undergraduate",
                hidden_answer=th[1],
                answer_keywords=th[2],
            )
        )

    # Algorithm design (50)
    algo_topics = [
        ("Dijkstra", "shortest path O((V+E) log V)", ["dijkstra", "shortest", "priority queue"]),
        ("Merge sort", "O(n log n) comparisons", ["merge sort", "o(n log n)", "divide"]),
        ("Dynamic programming knapsack", "O(nW) pseudo-polynomial", ["knapsack", "dynamic programming", "o(nw)"]),
        ("BFS", "O(V+E) graph traversal", ["bfs", "breadth", "queue"]),
        ("Hash table lookup", "O(1) average", ["hash", "o(1)", "average"]),
    ]
    for i in range(50):
        topic = algo_topics[i % len(algo_topics)]
        problems.append(
            KnownAnswerProblem(
                id=f"ka_algo_{i:03d}",
                stage=1,
                category="algorithm_design",
                title=f"{topic[0]} Analysis {i + 1}",
                problem_statement=f"Analyze time complexity of {topic[0]} on typical inputs.",
                difficulty="undergraduate",
                hidden_answer=topic[1],
                answer_keywords=topic[2],
            )
        )

    # Paper reproduction tasks (30)
    papers = [
        ("Attention Is All You Need", "scaled dot-product attention", ["attention", "transformer", "query", "key"]),
        ("ResNet", "skip connections enable deep training", ["residual", "skip", "deep"]),
        ("Adam optimizer", "adaptive moment estimation", ["adam", "learning rate", "momentum"]),
        ("PageRank", "eigenvector centrality on web graph", ["pagerank", "eigenvector", "markov"]),
        ("Word2Vec", "CBOW and skip-gram embeddings", ["word2vec", "embedding", "cbow"]),
    ]
    for i in range(30):
        p = papers[i % len(papers)]
        problems.append(
            KnownAnswerProblem(
                id=f"ka_paper_{i:03d}",
                stage=2,
                category="paper_reproduction",
                title=f"Reproduce: {p[0]}",
                problem_statement=f"Summarize the core contribution of '{p[0]}' and one equation or algorithm.",
                difficulty="graduate",
                hidden_answer=p[1],
                answer_keywords=p[2],
            )
        )

    # Scientific reasoning (90)
    sci_topics = [
        ("Ohm's law", "V=IR", ["ohm", "voltage", "current", "resistance"]),
        ("Ideal gas law", "PV=nRT", ["ideal gas", "pv=nrt", "temperature"]),
        ("Snell's law", "n₁sinθ₁=n₂sinθ₂", ["snell", "refraction", "angle"]),
        ("Half-life decay", "N(t)=N₀e^{-λt}", ["half-life", "exponential", "decay"]),
        ("Central limit theorem", "sample mean → normal for large n", ["central limit", "normal", "sample mean"]),
    ]
    for i in range(90):
        s = sci_topics[i % len(sci_topics)]
        problems.append(
            KnownAnswerProblem(
                id=f"ka_sci_{i:03d}",
                stage=1,
                category="scientific_reasoning",
                title=f"{s[0]} Application {i + 1}",
                problem_statement=f"Apply {s[0]} to a textbook scenario and state the governing relation.",
                difficulty="high_school",
                hidden_answer=s[1],
                answer_keywords=s[2],
            )
        )

    # Stage 0 infrastructure smoke tests (10)
    for i in range(10):
        problems.append(
            KnownAnswerProblem(
                id=f"ka_infra_{i:03d}",
                stage=0,
                category="infrastructure",
                title=f"Infrastructure Check {i + 1}",
                problem_statement="Verify the research validation pipeline can record a run and score it.",
                difficulty="smoke",
                hidden_answer="pipeline_ok=true",
                answer_keywords=["pipeline", "validation", "record", "score"],
            )
        )

    return problems


def load_known_answer_dataset() -> dict[str, KnownAnswerProblem]:
    """Load full known-answer dataset (cached JSON or generated)."""
    cache_path = DATA_DIR / "known_answer_problems.json"
    if cache_path.exists():
        raw = json.loads(cache_path.read_text(encoding="utf-8"))
        return {
            item["id"]: KnownAnswerProblem(**item)
            for item in raw
        }

    problems = _expand_problems(_seed_problems())
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(
        json.dumps([p.__dict__ for p in problems], indent=2),
        encoding="utf-8",
    )
    return {p.id: p for p in problems}


def get_problems_for_stage(stage: int) -> list[KnownAnswerProblem]:
    dataset = load_known_answer_dataset()
    return [p for p in dataset.values() if p.stage == stage]


def dataset_stats() -> dict[str, int]:
    dataset = load_known_answer_dataset()
    by_stage: dict[str, int] = {}
    by_category: dict[str, int] = {}
    for p in dataset.values():
        by_stage[str(p.stage)] = by_stage.get(str(p.stage), 0) + 1
        by_category[p.category] = by_category.get(p.category, 0) + 1
    return {
        "total": len(dataset),
        **{f"stage_{k}": v for k, v in by_stage.items()},
        **{f"cat_{k}": v for k, v in by_category.items()},
    }
