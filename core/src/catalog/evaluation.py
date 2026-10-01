"""Compare a listing against the expected one, and expose it as Langfuse evaluators.

Deterministic: it never calls a model. A case is exact when the category is right, no
attribute is extra or missing, no value is out of the channel domain, nothing is
duplicated and the reported missing attributes match the expected ones.
"""

from collections import Counter
from dataclasses import dataclass, field

from langfuse import Evaluation

from .data import NO_DATA, channel_attributes

EMPTY = {"category": None, "attributes": [], "missing": [], "rejected": []}


@dataclass
class CaseResult:
    category_ok: bool
    tp: int
    fp: int
    fn: int
    invalid: list[str] = field(default_factory=list)
    duplicates: list[str] = field(default_factory=list)
    missing_not_detected: list[str] = field(default_factory=list)
    extra_missing: list[str] = field(default_factory=list)

    @property
    def exact(self) -> bool:
        return (self.category_ok and self.fp == 0 and self.fn == 0 and not self.invalid
                and not self.duplicates and not self.missing_not_detected and not self.extra_missing)


def _key(attr: dict, attributes: dict[str, dict]) -> tuple:
    """Identity of a mapped attribute: by valueId when the channel has a domain, by text otherwise."""
    definition = attributes.get(attr["urn"])
    if definition and definition.get("values"):
        return (attr["urn"], str(attr.get("valueId")))
    return (attr["urn"], str(attr.get("value", "")).strip(), attr.get("unit") or None)


def _is_invalid(attr: dict, attributes: dict[str, dict]) -> bool:
    definition = attributes.get(attr["urn"])
    if definition is None or str(attr.get("value", "")).strip() in NO_DATA:
        return True
    domain = {v["id"] for v in definition.get("values", [])}
    return bool(domain) and str(attr.get("valueId")) not in domain


def evaluate_case(predicted: dict, expected: dict, attributes: dict[str, dict]) -> CaseResult:
    pred_attrs = predicted.get("attributes") or []
    pred_keys = Counter(_key(a, attributes) for a in pred_attrs)
    exp_keys = Counter(_key(a, attributes) for a in expected["attributes"])
    tp = sum((pred_keys & exp_keys).values())
    urn_count = Counter(a["urn"] for a in pred_attrs)
    pred_missing = {m["urn"] for m in predicted.get("missing") or []}
    exp_missing = {m["urn"] for m in expected["missing"]}
    return CaseResult(
        category_ok=predicted.get("category") == expected["category"],
        tp=tp,
        fp=sum(pred_keys.values()) - tp,
        fn=sum(exp_keys.values()) - tp,
        invalid=[a["urn"] for a in pred_attrs if _is_invalid(a, attributes)],
        duplicates=sorted(urn for urn, n in urn_count.items() if n > 1),
        missing_not_detected=sorted(exp_missing - pred_missing),
        extra_missing=sorted(pred_missing - exp_missing),
    )


def _ratio(num: int, den: int) -> float:
    return round(num / den, 3) if den else 0.0


def summarize(results: list[CaseResult]) -> dict:
    tp, fp, fn = (sum(getattr(r, k) for r in results) for k in ("tp", "fp", "fn"))
    return {
        "cases": len(results),
        "exact": sum(r.exact for r in results),
        "category_ok": sum(r.category_ok for r in results),
        "precision": _ratio(tp, tp + fp),
        "recall": _ratio(tp, tp + fn),
        "invalid_values": sum(len(r.invalid) for r in results),
        "duplicates": sum(len(r.duplicates) for r in results),
        "missing_not_detected": sum(len(r.missing_not_detected) for r in results),
    }


def _evaluate_output(output, expected: dict, schemas: dict[str, dict]) -> tuple[CaseResult, str | None]:
    error = output.get("error") if isinstance(output, dict) else "the task returned no output"
    predicted = EMPTY if error else output
    return evaluate_case(predicted, expected, channel_attributes(schemas, expected["category"])), error


def make_item_evaluator(schemas: dict[str, dict]):
    def evaluator(*, input, output, expected_output, metadata=None, **kwargs) -> list[Evaluation]:
        result, error = _evaluate_output(output, expected_output, schemas)
        return [
            # A task that errored never scores exact, even if the empty fallback output
            # happens to match an "empty" expected (category None, no attributes).
            Evaluation(name="exact", value=result.exact and not error, data_type="BOOLEAN", comment=error),
            Evaluation(name="category_ok", value=result.category_ok, data_type="BOOLEAN"),
            Evaluation(name="invalid_values", value=len(result.invalid), comment=", ".join(result.invalid) or None),
            Evaluation(name="duplicates", value=len(result.duplicates), comment=", ".join(result.duplicates) or None),
            Evaluation(name="missing_ok", value=not (result.missing_not_detected or result.extra_missing),
                       data_type="BOOLEAN"),
            Evaluation(name="precision", value=_ratio(result.tp, result.tp + result.fp)),
            Evaluation(name="recall", value=_ratio(result.tp, result.tp + result.fn)),
        ]

    return evaluator


def make_run_evaluator(schemas: dict[str, dict]):
    def run_evaluator(*, item_results, **kwargs) -> list[Evaluation]:
        results = [_evaluate_output(r.output, r.item.expected_output, schemas)[0] for r in item_results]
        summary = summarize(results)
        return [
            Evaluation(name="exact_count", value=summary["exact"]),
            Evaluation(name="category_ok_count", value=summary["category_ok"]),
            Evaluation(name="invalid_values_total", value=summary["invalid_values"]),
            Evaluation(name="duplicates_total", value=summary["duplicates"]),
            Evaluation(name="missing_not_detected_total", value=summary["missing_not_detected"]),
            Evaluation(name="precision", value=summary["precision"]),
            Evaluation(name="recall", value=summary["recall"]),
        ]

    return run_evaluator
