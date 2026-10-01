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

    (tool,) = create_catalog_tools(llm_factory=lambda: None, workflow_cls=FakeWorkflow,
                                   directories=[data_dir("mock")])
    return tool


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
    (tool,) = create_catalog_tools(llm_factory=lambda: None, workflow_cls=_NoopWorkflow, env={})
    assert "not in the war room dataset" in str(await tool.acall(sku=REAL_ONLY_SKU))


async def test_real_directory_is_included_when_the_allow_flag_is_set():
    (tool,) = create_catalog_tools(llm_factory=lambda: None, workflow_cls=_NoopWorkflow,
                                   env={"CATALOG_ALLOW_REAL_DATA": "1"})
    assert "not reached" in str(await tool.acall(sku=REAL_ONLY_SKU))
