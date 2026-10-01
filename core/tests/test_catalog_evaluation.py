import copy
from types import SimpleNamespace

from catalog.data import channel_attributes, data_dir, load_cases, load_schemas
from catalog.evaluation import evaluate_case, make_item_evaluator, make_run_evaluator, summarize

MOCK = data_dir("mock")
SCHEMAS = load_schemas(MOCK)
ATTRS = channel_attributes(SCHEMAS, "urn:category:102529:vendor:shopee")
CASES = {c["id"]: c for c in load_cases(MOCK)}


def test_prediction_equal_to_expected_is_exact():
    for case in CASES.values():
        assert evaluate_case(case["expected"], case["expected"], ATTRS).exact, case["id"]


def test_value_out_of_domain_is_invalid():
    expected = CASES["01-real-calota-aro14"]["expected"]
    pred = copy.deepcopy(expected)
    pred["attributes"][0] = {"urn": "urn:attribute:101638:vendor:shopee", "valueId": "99999", "value": "Nuevo"}
    result = evaluate_case(pred, expected, ATTRS)
    assert not result.exact
    assert result.invalid == ["urn:attribute:101638:vendor:shopee"]
    assert result.fp == 1 and result.fn == 1


def test_urn_unknown_to_the_channel_is_invalid():
    expected = CASES["02-calota-aro13-preta-completa"]["expected"]
    pred = copy.deepcopy(expected)
    pred["attributes"].append({"urn": "urn:attribute:1673", "valueId": "0", "value": "Novo"})
    result = evaluate_case(pred, expected, ATTRS)
    assert result.invalid == ["urn:attribute:1673"] and result.fp == 1


def test_duplicate_attribute_is_detected():
    expected = CASES["01-real-calota-aro14"]["expected"]
    pred = copy.deepcopy(expected)
    pred["attributes"].append(copy.deepcopy(pred["attributes"][4]))
    result = evaluate_case(pred, expected, ATTRS)
    assert result.duplicates == ["urn:attribute:101730:vendor:shopee"] and not result.exact


def test_free_text_compares_the_value():
    expected = CASES["02-calota-aro13-preta-completa"]["expected"]
    pred = copy.deepcopy(expected)
    pred["attributes"][1]["value"] = "OTHER-SKU"
    result = evaluate_case(pred, expected, ATTRS)
    assert result.fp == 1 and result.fn == 1 and result.invalid == []


def test_undetected_missing_is_an_error():
    expected = CASES["06-falta-obligatorio"]["expected"]
    pred = copy.deepcopy(expected)
    pred["missing"] = []
    result = evaluate_case(pred, expected, ATTRS)
    assert result.missing_not_detected == ["urn:attribute:101638:vendor:shopee"] and not result.exact


def test_wrong_category():
    expected = CASES["08-categoria-sin-referencia"]["expected"]
    pred = copy.deepcopy(expected)
    pred["category"] = "urn:category:123:vendor:shopee"
    result = evaluate_case(pred, expected, ATTRS)
    assert not result.category_ok and not result.exact


def test_no_data_value_is_invalid():
    expected = CASES["02-calota-aro13-preta-completa"]["expected"]
    pred = copy.deepcopy(expected)
    pred["attributes"][1]["value"] = "-1"
    assert evaluate_case(pred, expected, ATTRS).invalid == ["urn:attribute:102293:vendor:shopee"]


def test_summary_precision_and_recall():
    expected = CASES["01-real-calota-aro14"]["expected"]
    perfect = evaluate_case(expected, expected, ATTRS)
    empty = evaluate_case({"category": None, "attributes": [], "missing": []}, expected, ATTRS)
    summary = summarize([perfect, empty])
    assert summary["cases"] == 2 and summary["exact"] == 1
    assert summary["precision"] == 1.0 and summary["recall"] == 0.5


def test_item_evaluator_scores_and_task_errors():
    evaluator = make_item_evaluator(SCHEMAS)
    expected = CASES["01-real-calota-aro14"]["expected"]
    scores = {e.name: e.value for e in evaluator(input={}, output=expected, expected_output=expected)}
    assert scores["exact"] is True and scores["invalid_values"] == 0 and scores["precision"] == 1.0
    failed = evaluator(input={}, output={"error": "TypeError: boom"}, expected_output=expected)
    assert {e.name: e.value for e in failed}["exact"] is False
    assert "boom" in next(e for e in failed if e.name == "exact").comment


def test_errored_item_is_never_scored_exact():
    evaluator = make_item_evaluator(SCHEMAS)
    expected = {"category": None, "attributes": [], "missing": [], "rejected": []}
    scores = {e.name: e.value for e in evaluator(input={}, output={"error": "boom"}, expected_output=expected)}
    assert scores["exact"] is False


def test_run_evaluator_aggregates():
    run_evaluator = make_run_evaluator(SCHEMAS)
    expected = CASES["01-real-calota-aro14"]["expected"]
    items = [SimpleNamespace(item=SimpleNamespace(expected_output=expected), output=expected),
             SimpleNamespace(item=SimpleNamespace(expected_output=expected), output={"error": "x"})]
    scores = {e.name: e.value for e in run_evaluator(item_results=items)}
    assert scores["exact_count"] == 1 and scores["recall"] == 0.5


def test_run_evaluator_reports_missing_not_detected_total():
    run_evaluator = make_run_evaluator(SCHEMAS)
    expected = CASES["06-falta-obligatorio"]["expected"]
    no_missing = {**expected, "missing": []}
    items = [SimpleNamespace(item=SimpleNamespace(expected_output=expected), output=no_missing)]
    scores = {e.name: e.value for e in run_evaluator(item_results=items)}
    assert scores["missing_not_detected_total"] == 1
