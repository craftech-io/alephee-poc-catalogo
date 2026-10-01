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
