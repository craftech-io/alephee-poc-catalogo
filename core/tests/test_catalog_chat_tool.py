import json

from catalog.chat_tool import create_catalog_tools
from catalog.data import data_dir, load_cases
from catalog.events import MappingCompleted
from catalog.models import Listing

CASE = load_cases(data_dir("mock"))[0]


def _tool(outcome):
    class FakeWorkflow:
        def __init__(self, **kwargs):
            pass

        async def run(self, product):
            return outcome

    tools = {t.metadata.name: t for t in create_catalog_tools(
        llm_factory=lambda: None, workflow_cls=FakeWorkflow, directories=[data_dir("mock")])}
    return tools["map_product_v1"]


async def test_unknown_sku_is_explained():
    tool = _tool(None)
    assert "not in the war room dataset" in str(await tool.acall(sku="nope"))


async def test_mapping_error_is_explained():
    tool = _tool(MappingCompleted(listing=None, error="TypeError: boom"))
    assert "boom" in str(await tool.acall(sku=CASE["product"]["sku"]))


async def test_listing_is_returned_with_names():
    expected = CASE["expected"]
    listing = Listing.model_validate({k: expected[k] for k in ("category", "attributes", "missing", "rejected")})
    out = json.loads(str(await _tool(MappingCompleted(listing=listing)).acall(sku=CASE["product"]["sku"])))
    assert out["category"]["name"] == "Calotas"
    assert out["attributes"][0]["name"] and out["attributes"][0]["value"]


# A SKU that only exists in data/real, never in the mock dataset (unlike 94701411,
# the real example the mock dataset already carries as case 01-real-calota-aro14).
REAL_ONLY_SKU = "12645126"


class _NoopWorkflow:
    def __init__(self, **kwargs):
        pass

    async def run(self, product):
        return MappingCompleted(listing=None, error="not reached")


async def test_default_directories_are_mock_only_without_the_allow_flag():
    tools = {t.metadata.name: t for t in create_catalog_tools(
        llm_factory=lambda: None, workflow_cls=_NoopWorkflow, env={})}
    assert "not in the war room dataset" in str(await tools["map_product_v1"].acall(sku=REAL_ONLY_SKU))


async def test_real_directory_is_included_when_the_allow_flag_is_set():
    tools = {t.metadata.name: t for t in create_catalog_tools(
        llm_factory=lambda: None, workflow_cls=_NoopWorkflow, env={"CATALOG_ALLOW_REAL_DATA": "1"})}
    assert "not reached" in str(await tools["map_product_v1"].acall(sku=REAL_ONLY_SKU))


def test_two_tools_v1_and_v2():
    tools = create_catalog_tools(llm_factory=lambda: None, directories=[data_dir("mock")],
                                 stores_factory=lambda env: (None, None, "in-memory"))
    assert sorted(t.metadata.name for t in tools) == ["map_product_v1", "map_product_v2"]


async def test_v2_tool_runs_the_v2_workflow():
    expected = CASE["expected"]
    listing = Listing.model_validate({k: expected[k] for k in ("category", "attributes", "missing", "rejected")})

    class FakeV2:
        def __init__(self, **kwargs):
            pass

        async def run(self, product):
            return MappingCompleted(listing=listing, source="agent")

    tools = {t.metadata.name: t for t in create_catalog_tools(
        llm_factory=lambda: None, workflow_v2_cls=FakeV2, directories=[data_dir("mock")],
        stores_factory=lambda env: (None, None, "in-memory"))}
    out = json.loads(str(await tools["map_product_v2"].acall(sku=CASE["product"]["sku"])))
    assert out["category"]["name"] == "Calotas" and out["source"] == "agent"


async def test_v2_tool_reports_a_warning_when_the_agent_erred_after_submitting():
    """Controller ruling (Task 4 review): the V2 workflow can return a listing together with
    an error (an exception after a submission, or iterations exhausted). The chat tool must
    surface it as a `warning`, not hide it."""
    expected = CASE["expected"]
    listing = Listing.model_validate({k: expected[k] for k in ("category", "attributes", "missing", "rejected")})

    class FakeV2:
        def __init__(self, **kwargs):
            pass

        async def run(self, product):
            return MappingCompleted(listing=listing, source="agent",
                                    error="max iterations reached; last submission cleaned")

    tools = {t.metadata.name: t for t in create_catalog_tools(
        llm_factory=lambda: None, workflow_v2_cls=FakeV2, directories=[data_dir("mock")],
        stores_factory=lambda env: (None, None, "in-memory"))}
    out = json.loads(str(await tools["map_product_v2"].acall(sku=CASE["product"]["sku"])))
    assert out["warning"] == "max iterations reached; last submission cleaned"


async def test_v1_tool_never_reports_a_warning_key():
    out = json.loads(str(await _tool(MappingCompleted(
        listing=Listing.model_validate({k: CASE["expected"][k] for k in ("category", "attributes", "missing", "rejected")}))
    ).acall(sku=CASE["product"]["sku"])))
    assert "warning" not in out


async def test_v2_tool_builds_the_stores_once_across_calls():
    """Task 3 (final fix wave): `stores_factory(env)` used to run on every `map_product_v2`
    call. It must be built once, lazily, and reused."""
    expected = CASE["expected"]
    listing = Listing.model_validate({k: expected[k] for k in ("category", "attributes", "missing", "rejected")})

    class FakeV2:
        def __init__(self, **kwargs):
            pass

        async def run(self, product):
            return MappingCompleted(listing=listing, source="agent")

    calls = []

    def stores_factory(env):
        calls.append(env)
        return (None, None, "in-memory")

    tools = {t.metadata.name: t for t in create_catalog_tools(
        llm_factory=lambda: None, workflow_v2_cls=FakeV2, directories=[data_dir("mock")],
        stores_factory=stores_factory)}

    await tools["map_product_v2"].acall(sku=CASE["product"]["sku"])
    await tools["map_product_v2"].acall(sku=CASE["product"]["sku"])

    assert len(calls) == 1
