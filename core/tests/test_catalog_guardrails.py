from catalog.data import data_dir, load_cases, load_schemas
from catalog.guardrails import clean, merge_resolved, validate
from catalog.models import Listing, MappedAttribute, MissingAttribute

MOCK = data_dir("mock")
CALOTAS = "urn:category:102529:vendor:shopee"
SCHEMA = load_schemas(MOCK)[CALOTAS]
CONDITION = "urn:attribute:101638:vendor:shopee"
EXPECTED = {c["id"]: c["expected"] for c in load_cases(MOCK)}


def _listing(*attributes, missing=(), category=CALOTAS):
    return Listing(category=category, attributes=list(attributes), missing=list(missing), rejected=[])


def _all_mandatory_missing():
    return [MissingAttribute(urn=a["urn"], reason="x") for a in SCHEMA["attributes"] if a.get("mandatory")]


def test_expected_listing_of_case_01_is_valid():
    listing = Listing.model_validate({k: EXPECTED["01-real-calota-aro14"][k] for k in ("category", "attributes", "missing", "rejected")})
    assert validate(listing, SCHEMA, CALOTAS) == []


def test_validate_reports_each_problem():
    other = next(a["urn"] for a in SCHEMA["attributes"] if a["urn"] != CONDITION)
    problems = validate(_listing(
        MappedAttribute(urn="urn:attribute:1:vendor:shopee", valueId="0", value="x"),
        MappedAttribute(urn=CONDITION, valueId="99999", value="Nuevo"),
        MappedAttribute(urn=CONDITION, valueId="14703", value="Usado"),
        missing=[m for m in _all_mandatory_missing() if m.urn != other],
        category="urn:category:1:vendor:shopee"), SCHEMA, CALOTAS)
    text = "\n".join(problems)
    assert "category must be" in text
    assert "is not an attribute of" in text
    assert "is not in the channel list" in text
    assert "does not match id" in text
    assert "appears 2 times" in text
    if next(a for a in SCHEMA["attributes"] if a["urn"] == other).get("mandatory"):
        assert "is mandatory" in text


def test_no_data_value_is_a_problem():
    free = next(a["urn"] for a in SCHEMA["attributes"] if not a.get("values"))
    problems = validate(_listing(MappedAttribute(urn=free, valueId="0", value="-1"), missing=_all_mandatory_missing()),
                        SCHEMA, CALOTAS)
    assert any("means no data" in p for p in problems)


def test_clean_never_lets_invalid_or_duplicates_out_and_fixes_the_category():
    dirty = _listing(MappedAttribute(urn=CONDITION, valueId="14703", value="Novo"),
                     MappedAttribute(urn=CONDITION, valueId="14703", value="Novo"),
                     MappedAttribute(urn="urn:attribute:1:vendor:shopee", valueId="0", value="x"),
                     category="urn:category:1:vendor:shopee")
    result = clean(dirty, SCHEMA, CALOTAS)
    assert result.category == CALOTAS
    assert [a.urn for a in result.attributes] == [CONDITION]
    assert validate(result, SCHEMA, CALOTAS) == []
    assert any(r.reason.startswith("guardrail:") for r in result.rejected)


def test_clean_marks_missing_mandatory_and_drops_resolved_missing():
    result = clean(_listing(MappedAttribute(urn=CONDITION, valueId="14703", value="Novo"),
                            missing=[MissingAttribute(urn=CONDITION, reason="x"), MissingAttribute(urn="category", reason="x")]),
                   SCHEMA, CALOTAS)
    urns = {m.urn for m in result.missing}
    assert CONDITION not in urns and "category" not in urns
    assert {a["urn"] for a in SCHEMA["attributes"] if a.get("mandatory")} - {CONDITION} <= urns


def test_merge_resolved_wins_over_the_agent():
    agent = _listing(MappedAttribute(urn=CONDITION, valueId="0", value="whatever"), missing=[MissingAttribute(urn=CONDITION, reason="x")])
    merged = merge_resolved(agent, [MappedAttribute(urn=CONDITION, valueId="14703", value="Novo")])
    assert [(a.urn, a.value) for a in merged.attributes] == [(CONDITION, "Novo")]
    assert CONDITION not in {m.urn for m in merged.missing}


def test_merge_resolved_deduplicates_resolved_by_urn_keeping_the_first():
    agent = _listing()
    a_novo = MappedAttribute(urn=CONDITION, valueId="14703", value="Novo")
    a_other_same_urn = MappedAttribute(urn=CONDITION, valueId="14704", value="Usado")
    merged = merge_resolved(agent, [a_novo, a_other_same_urn])
    assert [a.urn for a in merged.attributes].count(CONDITION) == 1
    assert [(a.urn, a.value) for a in merged.attributes] == [(CONDITION, "Novo")]


def test_clean_deduplicates_missing_by_urn_keeping_the_first():
    result = clean(_listing(missing=[MissingAttribute(urn=CONDITION, reason="first"),
                                     MissingAttribute(urn=CONDITION, reason="second")]),
                   SCHEMA, CALOTAS)
    matches = [m for m in result.missing if m.urn == CONDITION]
    assert len(matches) == 1
    assert matches[0].reason == "first"
