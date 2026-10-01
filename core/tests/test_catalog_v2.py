from catalog_fakes import ScriptedLLM, call

from catalog.data import data_dir, load_cases, load_schemas
from catalog.guardrails import validate
from catalog.models import Listing
from catalog.reference import load_reference
from catalog.store import Correction, InMemoryCache, InMemoryCorrections
from catalog.v2 import MAX_ITERATIONS, MappingV2

MOCK = data_dir("mock")
SCHEMAS = load_schemas(MOCK)
REFERENCE = load_reference(MOCK)
CASES = {c["id"]: c for c in load_cases(MOCK)}
CALOTAS = "urn:category:102529:vendor:shopee"
CONDITION = "urn:attribute:101638:vendor:shopee"
PRODUCT = CASES["01-real-calota-aro14"]["product"]
GOOD = {k: CASES["01-real-calota-aro14"]["expected"][k] for k in ("category", "attributes", "missing", "rejected")}


def _workflow(llm, cache=None, corrections=None):
    return MappingV2(llm=llm, system_prompt="S", prompt_version="seed", schemas=SCHEMAS, reference=REFERENCE,
                     corrections=corrections or InMemoryCorrections(), cache=cache or InMemoryCache(), timeout=30)


async def test_valid_submission_on_the_first_try_is_cached():
    cache = InMemoryCache()
    llm = ScriptedLLM(script=[[call("submit_listing", **GOOD)]])
    done = await _workflow(llm, cache=cache).run(product=PRODUCT)
    assert done.source == "agent" and done.error is None
    assert validate(done.listing, SCHEMAS[CALOTAS], CALOTAS) == []
    assert cache.get(PRODUCT["sku"], "734701", REFERENCE.version, "seed") == done.listing


async def test_cache_hit_does_not_call_the_model():
    cache = InMemoryCache()
    cache.put(PRODUCT["sku"], "734701", REFERENCE.version, "seed", CALOTAS, Listing.model_validate(GOOD))
    llm = ScriptedLLM(script=[])
    done = await _workflow(llm, cache=cache).run(product=PRODUCT)
    assert done.source == "cache" and llm.seen == []


async def test_product_without_category_does_not_call_the_model():
    llm = ScriptedLLM(script=[])
    done = await _workflow(llm).run(product=CASES["09-sin-categoria"]["product"])
    assert done.source == "tables" and done.listing.category is None
    assert done.listing.missing[0].urn == "category" and llm.seen == []


async def test_category_without_schema_does_not_call_the_model():
    product = {**PRODUCT, "categories": [{"urn": "urn:category:900001", "name": "Amortecedores (MOCK)"}]}
    done = await _workflow(ScriptedLLM(script=[])).run(product=product)
    assert done.source == "tables" and "schema" in done.listing.missing[0].reason


async def test_invalid_submission_gets_the_problems_and_is_fixed():
    bad = {**GOOD, "attributes": [*GOOD["attributes"], {"urn": "urn:attribute:1:vendor:shopee", "valueId": "0", "value": "x"}]}
    llm = ScriptedLLM(script=[[call("submit_listing", **bad)], [call("submit_listing", **GOOD)]])
    done = await _workflow(llm).run(product=PRODUCT)
    assert "did not pass validation" in (llm.seen[1] or "")
    assert validate(done.listing, SCHEMAS[CALOTAS], CALOTAS) == []


async def test_exhausted_iterations_clean_the_last_submission_and_do_not_cache():
    bad = {**GOOD, "attributes": [*GOOD["attributes"], {"urn": "urn:attribute:1:vendor:shopee", "valueId": "0", "value": "x"}]}
    cache = InMemoryCache()
    llm = ScriptedLLM(script=[[call("submit_listing", **bad)] for _ in range(MAX_ITERATIONS + 2)])
    done = await _workflow(llm, cache=cache).run(product=PRODUCT)
    assert done.source == "agent" and validate(done.listing, SCHEMAS[CALOTAS], CALOTAS) == []
    assert cache.get(PRODUCT["sku"], "734701", REFERENCE.version, "seed") is None


async def test_no_submission_is_an_error():
    done = await _workflow(ScriptedLLM(script=[[]])).run(product=PRODUCT)
    assert done.listing is None and "never submitted" in done.error


async def test_resolved_attributes_win_over_the_agent():
    other = next(v for v in next(a for a in SCHEMAS[CALOTAS]["attributes"] if a["urn"] == CONDITION)["values"]
                 if v["name"] != "Novo")
    tampered = {**GOOD, "attributes": [{"urn": CONDITION, "valueId": str(other["id"]), "value": other["name"]}
                                       if a["urn"] == CONDITION else a for a in GOOD["attributes"]]}
    done = await _workflow(ScriptedLLM(script=[[call("submit_listing", **tampered)]])).run(product=PRODUCT)
    assert {a.urn: a.value for a in done.listing.attributes}[CONDITION] == "Novo"


async def test_lookup_corrections_returns_the_correction_to_the_model():
    corrections = InMemoryCorrections()
    corrections.put(Correction(category_urn=CALOTAS, attribute_urn=CONDITION, product_value="1", value_id="14703",
                               value="Novo", author="catalog", created_at="2026-10-01"))
    llm = ScriptedLLM(script=[[call("lookup_corrections", attribute_urn=CONDITION, product_value=" 1 ")],
                              [call("submit_listing", **GOOD)]])
    await _workflow(llm, corrections=corrections).run(product=PRODUCT)
    assert "Novo" in (llm.seen[1] or "")


async def test_dynamodb_failures_do_not_break_the_mapping():
    class Broken:
        def get(self, *a, **k):
            raise RuntimeError("dynamodb down")

        def put(self, *a, **k):
            raise RuntimeError("dynamodb down")

        def find(self, *a, **k):
            raise RuntimeError("dynamodb down")

    llm = ScriptedLLM(script=[[call("lookup_corrections", attribute_urn=CONDITION, product_value="Novo")],
                              [call("submit_listing", **GOOD)]])
    done = await _workflow(llm, cache=Broken(), corrections=Broken()).run(product=PRODUCT)
    assert done.listing is not None and done.error is None
