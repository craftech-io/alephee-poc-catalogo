from catalog.data import data_dir, load_cases, load_schemas
from catalog.reference import load_reference
from catalog.worklist import build_worklist, normalize

MOCK = data_dir("mock")
CALOTAS = "urn:category:102529:vendor:shopee"
SCHEMA = load_schemas(MOCK)[CALOTAS]
REFERENCE = load_reference(MOCK)
CASES = {c["id"]: c for c in load_cases(MOCK)}
CONDITION = "urn:attribute:101638:vendor:shopee"


def _product(*attributes):
    return {"sku": "T-1", "categories": [{"urn": "urn:category:734701"}], "attributes": list(attributes)}


def test_normalize():
    assert normalize("  NoVo ") == "novo"


def test_exact_list_match_is_resolved_ignoring_case_and_spaces():
    work = build_worklist(_product({"urn": "urn:attribute:1673", "name": "Condición", "unit": "-1", "value": " novo "}),
                          SCHEMA, REFERENCE)
    resolved = {a.urn: a for a in work.resolved}
    assert resolved[CONDITION].value == "Novo" and resolved[CONDITION].valueId == "14703"
    assert not work.to_decide


def test_value_without_exact_match_goes_to_the_agent():
    work = build_worklist(_product({"urn": "urn:attribute:1673", "name": "Condición", "unit": "-1", "value": "1"}),
                          SCHEMA, REFERENCE)
    assert [d["target_urn"] for d in work.to_decide] == [CONDITION]
    assert work.to_decide[0]["values"] and work.to_decide[0]["product_value"] == "1"


def test_no_data_values_are_skipped():
    work = build_worklist(_product({"urn": "urn:attribute:1673", "name": "Condición", "unit": "-1", "value": "-1"}),
                          SCHEMA, REFERENCE)
    assert not work.resolved and not work.to_decide
    assert CONDITION in {a["urn"] for a in work.uncovered_channel}


def test_two_product_attributes_with_the_same_target_keep_only_one():
    work = build_worklist(_product({"urn": "urn:attribute:1673", "name": "Condición", "unit": "-1", "value": "Novo"},
                                   {"urn": "urn:attribute:1673", "name": "Condición", "unit": "-1", "value": "Usado"}),
                          SCHEMA, REFERENCE)
    assert [a.urn for a in work.resolved] + [d["target_urn"] for d in work.to_decide] == [CONDITION]


def test_attributes_without_destination_and_uncovered_channel_attributes():
    work = build_worklist(CASES["01-real-calota-aro14"]["product"], SCHEMA, REFERENCE)
    covered = {a.urn for a in work.resolved} | {d["target_urn"] for d in work.to_decide}
    assert CONDITION in covered
    assert all(a["urn"] not in covered for a in work.uncovered_channel)
    assert {a["urn"] for a in work.uncovered_channel} | covered == {a["urn"] for a in SCHEMA["attributes"]}
    assert all(p["value"] not in ("-1", "N/A", "") for p in work.unmapped_product)


def test_free_text_without_unit_is_copied_and_with_unit_goes_to_the_agent():
    free = next(a for a in SCHEMA["attributes"] if not a.get("values"))
    legacy = next(lid for lid, rows in REFERENCE.attributes.items() if any(r["urn"] == free["urn"] for r in rows))
    copied = build_worklist(_product({"urn": f"urn:attribute:{legacy}", "name": "x", "unit": "-1", "value": "ABC-1"}),
                            SCHEMA, REFERENCE)
    assert [(a.urn, a.valueId, a.value) for a in copied.resolved] == [(free["urn"], "0", "ABC-1")]
    with_unit = build_worklist(_product({"urn": f"urn:attribute:{legacy}", "name": "x", "unit": "[[[Gramos]]]", "value": "390"}),
                               SCHEMA, REFERENCE)
    assert not with_unit.resolved and with_unit.to_decide[0]["product_unit"] == "[[[Gramos]]]"
