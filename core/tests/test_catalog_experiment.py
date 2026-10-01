from types import SimpleNamespace

import pytest
from botocore.exceptions import NoCredentialsError

from catalog import experiment
from catalog.data import data_dir, load_cases, load_schemas
from catalog.events import MappingCompleted
from catalog.experiment import (
    check_aws,
    current_task,
    dataset_items,
    main,
    make_v1_task,
    prompt_label,
    upload_dataset,
)
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


async def test_v1_task_exits_on_an_auth_error_instead_of_reporting_it_as_a_case_error(monkeypatch):
    monkeypatch.setenv("AWS_PROFILE", "sandbox")

    class FailingWorkflow:
        def __init__(self, **kwargs):
            pass

        async def run(self, product):
            raise NoCredentialsError()

    task = make_v1_task(llm=None, system_prompt="S", schemas={}, workflow_cls=FailingWorkflow)
    with pytest.raises(SystemExit) as info:
        await task(item=SimpleNamespace(input={}))
    assert "aws sso login --profile sandbox" in str(info.value)


def test_check_aws_exits_with_the_login_command(monkeypatch):
    monkeypatch.setenv("AWS_PROFILE", "sandbox")
    seen = {}

    class Broken:
        def client(self, name):
            raise RuntimeError("Token has expired")

    def factory(**kw):
        seen.update(kw)
        return Broken()

    with pytest.raises(SystemExit) as info:
        check_aws(session_factory=factory)
    assert seen == {"profile_name": "sandbox"}
    assert "aws sso login --profile sandbox" in str(info.value)


def test_check_aws_without_an_aws_profile_uses_the_default_credential_chain(monkeypatch):
    monkeypatch.delenv("AWS_PROFILE", raising=False)
    seen = {}

    class Broken:
        def client(self, name):
            raise RuntimeError("Token has expired")

    def factory(**kw):
        seen.update(kw)
        return Broken()

    with pytest.raises(SystemExit) as info:
        check_aws(session_factory=factory)
    assert seen == {"profile_name": None}
    assert "aws sso login" in str(info.value) and "--profile" not in str(info.value)


def test_main_exits_without_langfuse(monkeypatch):
    monkeypatch.delenv("LANGFUSE_PUBLIC_KEY", raising=False)
    monkeypatch.delenv("LANGFUSE_SECRET_KEY", raising=False)
    with pytest.raises(SystemExit) as info:
        main(["--version", "current", "--data", "mock"])
    assert "LANGFUSE" in str(info.value)


def test_main_refuses_real_data_without_the_allow_flag(monkeypatch):
    calls = []
    monkeypatch.setattr(experiment, "setup_tracing", lambda: calls.append("setup_tracing"))
    monkeypatch.setattr(experiment, "upload_dataset", lambda *a, **kw: calls.append("upload_dataset"))

    with pytest.raises(SystemExit) as info:
        main(["--version", "current", "--data", "real"])

    assert "Alephee" in str(info.value)
    assert calls == []


class _FakeExperimentClient:
    """Enough of the Langfuse client surface for `main` to run end to end."""

    def get_dataset(self, name):
        return SimpleNamespace(items=[SimpleNamespace(metadata={"case": None})])

    def run_experiment(self, **kwargs):
        return SimpleNamespace(format=lambda: "ok")

    def flush(self):
        pass


def test_main_uploads_real_data_with_the_allow_flag(monkeypatch):
    calls = []
    monkeypatch.setattr(experiment, "setup_tracing", lambda: _FakeExperimentClient())
    monkeypatch.setattr(experiment, "upload_dataset", lambda *a, **kw: calls.append("upload_dataset"))

    main(["--version", "current", "--data", "real", "--allow-real-upload"])

    assert calls == ["upload_dataset"]


def test_check_aws_runs_before_upload_dataset_for_v1(monkeypatch):
    calls = []
    monkeypatch.setattr(experiment, "setup_tracing", lambda: _FakeExperimentClient())
    monkeypatch.setattr(experiment, "check_aws", lambda: calls.append("check_aws"))
    monkeypatch.setattr(experiment, "upload_dataset", lambda *a, **kw: calls.append("upload_dataset"))
    monkeypatch.setattr(experiment, "sync_seed", lambda *a, **kw: None)
    monkeypatch.setattr(
        experiment, "get_system_prompt",
        lambda *a, **kw: SimpleNamespace(text="S", name="catalog-v1-system", version=None),
    )
    monkeypatch.setattr(experiment, "create_llm", lambda: SimpleNamespace(model="fake-model"))
    monkeypatch.setattr(experiment, "make_v1_task", lambda *a, **kw: (lambda **kw: None))

    main(["--version", "v1", "--data", "mock"])

    assert calls == ["check_aws", "upload_dataset"]


def test_prompt_label_uses_seed_when_there_is_no_version():
    assert prompt_label(SimpleNamespace(name="catalog-v1-system", version=None)) == "catalog-v1-system:seed"
    assert prompt_label(SimpleNamespace(name="catalog-v1-system", version=3)) == "catalog-v1-system:v3"
