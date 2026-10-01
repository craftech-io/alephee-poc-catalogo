from catalog.data import data_dir, load_cases, load_schemas
from catalog.reference import legacy_id, load_reference

MOCK = data_dir("mock")
REAL = data_dir("real")
CALOTAS = "urn:category:102529:vendor:shopee"


def test_legacy_id_strips_urn_prefixes():
    assert legacy_id("urn:category:734701") == "734701"
    assert legacy_id("urn:attribute:1673") == "1673"
    assert legacy_id("1106872") == "1106872"


def test_category_for_uses_the_table_and_handles_missing_categories():
    reference = load_reference(MOCK)
    cases = {c["id"]: c for c in load_cases(MOCK)}
    assert reference.category_for(cases["01-real-calota-aro14"]["product"]) == {"urn": CALOTAS, "name": "Calotas"}
    assert reference.category_for(cases["09-sin-categoria"]["product"]) is None
    assert reference.category_for({"categories": [{"urn": "urn:category:999999999"}]}) is None


def test_target_for_filters_by_category_schema():
    reference = load_reference(MOCK)
    schema = load_schemas(MOCK)[CALOTAS]
    assert reference.target_for("urn:attribute:1673", schema) == "urn:attribute:101638:vendor:shopee"
    assert reference.target_for("urn:attribute:1726", schema) is None  # Material is not in the mock table


def test_target_for_disambiguates_ids_with_several_destinations():
    reference = load_reference(REAL)
    schemas = load_schemas(REAL)
    found = None
    for legacy, rows in reference.attributes.items():
        if len(rows) < 2:
            continue
        for schema in schemas.values():
            urns = {a["urn"] for a in schema["attributes"]}
            hits = [r["urn"] for r in rows if r["urn"] in urns]
            if len(hits) == 1:
                found = (legacy, schema, hits[0])
                break
        if found:
            break
    assert found, "the real table should have an id with several destinations"
    legacy, schema, expected = found
    assert reference.target_for(f"urn:attribute:{legacy}", schema) == expected


def test_version_is_stable_and_short():
    assert load_reference(MOCK).version == load_reference(MOCK).version
    assert len(load_reference(MOCK).version) == 12
    assert load_reference(MOCK).version != load_reference(REAL).version
