from types import SimpleNamespace

import pytest

from catalog.data import data_dir, load_cases, load_schemas
from catalog.events import MappingCompleted
from catalog.experiment import check_aws, current_task, dataset_items, main, make_v1_task, upload_dataset
from catalog.models import Listing

REAL = load_cases(data_dir("real"))
MOCK = load_cases(data_dir("mock"))


def test_dataset_items_carry_expected_and_metadata():
    items = dataset_items(REAL, "real")
    assert len(items) == 30
    first = items[0]
    assert first["id"] == f"alephee-shopee-real-{REAL[0]['id']}"
    assert first["input"] == REAL[0]["product"]
    assert first["expected_output"]["category"] == REAL[0]["expected"]["category"]
    assert first["metadata"]["origin"] == "real" and first["metadata"]["expected_is_mock"] is True
    assert first["metadata"]["actual"] == REAL[0]["actual"]
    assert dataset_items(MOCK, "mock")[6]["metadata"]["decision_pending"]


def _missing(name):
    raise RuntimeError("not found")


def test_upload_dataset_creates_once_and_upserts_items_by_id():
    calls = []
    client = SimpleNamespace(get_dataset=_missing,
                             create_dataset=lambda **kw: calls.append(("dataset", kw["name"])),
                             create_dataset_item=lambda **kw: calls.append(("item", kw["id"])))
    upload_dataset(client, "mock", MOCK)
    assert calls[0] == ("dataset", "alephee-shopee-mock")
    assert len({c[1] for c in calls if c[0] == "item"}) == 10

    calls.clear()
    client.get_dataset = lambda name: object()
    upload_dataset(client, "mock", MOCK)
    assert not [c for c in calls if c[0] == "dataset"]


def test_current_task_returns_todays_listing_without_a_model():
    item = SimpleNamespace(metadata={"actual": REAL[0]["actual"]})
    out = current_task(item=item)
    assert out["category"] == REAL[0]["actual"]["category"]
    assert out["missing"] == [] and set(out["attributes"][0]) == {"urn", "valueId", "value", "unit"}


async def test_v1_task_returns_the_listing_or_the_error():
    listing = Listing(category="urn:x", attributes=[], missing=[], rejected=[])

    class FakeWorkflow:
        outcome = MappingCompleted(listing=listing)

        def __init__(self, **kwargs):
            pass

        async def run(self, product):
            return self.outcome

    task = make_v1_task(llm=None, system_prompt="S", schemas={}, workflow_cls=FakeWorkflow)
    assert (await task(item=SimpleNamespace(input={}))) == listing.model_dump()
    FakeWorkflow.outcome = MappingCompleted(listing=None, error="TypeError: boom")
    assert (await task(item=SimpleNamespace(input={}))) == {"error": "TypeError: boom"}


def test_check_aws_exits_with_the_login_command():
    class Broken:
        def client(self, name):
            raise RuntimeError("Token has expired")

    with pytest.raises(SystemExit) as info:
        check_aws(session_factory=lambda **kw: Broken())
    assert "aws sso login --profile" in str(info.value)


def test_main_exits_without_langfuse(monkeypatch):
    monkeypatch.delenv("LANGFUSE_PUBLIC_KEY", raising=False)
    monkeypatch.delenv("LANGFUSE_SECRET_KEY", raising=False)
    with pytest.raises(SystemExit) as info:
        main(["--version", "current", "--data", "mock"])
    assert "LANGFUSE" in str(info.value)
