"""Prediction generation from hypotheses."""

from __future__ import annotations

from axiom.discovery.models import HypothesisRecord, PredictionRecord, _new_id


def predictions_from_hypothesis(hypothesis: HypothesisRecord) -> list[PredictionRecord]:
    preds: list[PredictionRecord] = []
    for i, text in enumerate(hypothesis.predictions or []):
        preds.append(
            PredictionRecord(
                prediction_id=_new_id("pred"),
                hypothesis_id=hypothesis.hypothesis_id,
                statement=text,
                testable=True,
                experiment_hint=(
                    hypothesis.required_experiments[i]
                    if i < len(hypothesis.required_experiments)
                    else (hypothesis.required_experiments[0] if hypothesis.required_experiments else "controlled test")
                ),
            )
        )
    if not preds and not hypothesis.rejected:
        preds.append(
            PredictionRecord(
                prediction_id=_new_id("pred"),
                hypothesis_id=hypothesis.hypothesis_id,
                statement="No concrete prediction — mark hypothesis low priority.",
                testable=False,
                experiment_hint="none",
            )
        )
    return preds
