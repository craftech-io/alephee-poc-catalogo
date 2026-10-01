import boto3
import pytest

from catalog.data import data_dir, load_cases, load_schemas
from catalog.guardrails import validate
from catalog.llm import create_llm
from catalog.prompts import PROMPT_NAME, PROMPT_NAME_V2, load_seed
from catalog.reference import load_reference
from catalog.store import Correction, InMemoryCache, stores_from_env
from catalog.v1 import MappingV1
from catalog.v2 import MappingV2

pytestmark = pytest.mark.e2e
MOCK = data_dir("mock")
SCHEMAS = load_schemas(MOCK)
REFERENCE = load_reference(MOCK)
CASES = {c["id"]: c for c in load_cases(MOCK)}
CALOTAS = "urn:category:102529:vendor:shopee"
PROMPT_VERSION = "e2e"


@pytest.fixture(scope="module", autouse=True)
def aws_credentials():
    try:
        boto3.Session().client("sts").get_caller_identity()
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"no AWS credentials: {type(exc).__name__}")


@pytest.fixture(scope="module")
def stores():
    return stores_from_env()


def _v2(stores, cache=None):
    corrections, real_cache, _ = stores
    return MappingV2(llm=create_llm(), system_prompt=load_seed(PROMPT_NAME_V2), prompt_version=PROMPT_VERSION,
                     schemas=SCHEMAS, reference=REFERENCE, corrections=corrections, cache=cache or real_cache, timeout=300)


async def test_v1_maps_the_real_example_product():
    done = await MappingV1(llm=create_llm(), system_prompt=load_seed(PROMPT_NAME), schemas=SCHEMAS,
                           timeout=180).run(product=CASES["01-real-calota-aro14"]["product"])
    assert done.listing is not None and done.listing.category == CALOTAS


@pytest.mark.parametrize("case_id", sorted(CASES))
async def test_v2_never_delivers_invalid_listings(case_id, stores):
    done = await _v2(stores, cache=InMemoryCache()).run(product=CASES[case_id]["product"])
    if case_id == "09-sin-categoria":
        assert done.source == "tables" and done.listing.missing[0].urn == "category"
        return
    assert done.listing is not None, done.error
    if done.listing.category:
        assert validate(done.listing, SCHEMAS[done.listing.category], done.listing.category) == []


async def test_second_run_comes_from_the_cache(stores):
    product = CASES["02-calota-aro13-preta-completa"]["product"]
    cache = stores[1]
    cache.invalidate_category(CALOTAS)
    first = await _v2(stores).run(product=product)
    second = await _v2(stores).run(product=product)
    assert first.source == "agent" and second.source == "cache"
    assert second.listing == first.listing


async def test_a_correction_changes_the_result(stores):
    # "Novo" matches the channel list exactly and the code resolves it without asking for
    # corrections, so the test uses a product value with no exact match: the attribute goes
    # to the agent, which has to call lookup_corrections.
    from catalog.store import correction_key

    corrections, cache, _ = stores
    case = CASES["01-real-calota-aro14"]
    condition = "urn:attribute:101638:vendor:shopee"
    value = "Novo (e2e)"
    other = next(v for v in next(a for a in SCHEMAS[CALOTAS]["attributes"] if a["urn"] == condition)["values"]
                 if v["name"] != "Novo")
    product = {**case["product"], "attributes": [{**a, "value": value} if a["urn"] == "urn:attribute:1673" else a
                                                 for a in case["product"]["attributes"]]}
    try:
        corrections.put(Correction(category_urn=CALOTAS, attribute_urn=condition, product_value=value,
                                   value_id=str(other["id"]), value=other["name"], author="e2e", created_at="2026-10-01"))
        done = await _v2(stores, cache=InMemoryCache()).run(product=product)
        assert {a.urn: a.value for a in done.listing.attributes}.get(condition) == other["name"]
    finally:
        table = getattr(corrections, "table", None)
        if table is not None:
            table.delete_item(Key={"category_urn": CALOTAS, "correction_key": correction_key(condition, value)})
        cache.invalidate_category(CALOTAS)
