from types import SimpleNamespace

from catalog.prompts import PROMPT_NAME, get_system_prompt, load_seed, sync_seed
from catalog.tracing import langfuse_client


class FakeLangfuse:
    def __init__(self, exists=True):
        self.exists = exists
        self.created = None

    def get_prompt(self, name, *, label=None, fallback=None, max_retries=None, **kwargs):
        if not self.exists and fallback is None:
            raise RuntimeError("prompt not found")
        if not self.exists:
            return SimpleNamespace(compile=lambda: fallback, version=1, is_fallback=True)
        return SimpleNamespace(compile=lambda: "FROM LANGFUSE", version=7, is_fallback=False)

    def create_prompt(self, **kwargs):
        self.created = kwargs


def test_seed_is_english_and_mentions_the_contract():
    seed = load_seed(PROMPT_NAME)
    assert "missing" in seed and "rejected" in seed and "Never invent" in seed


def test_without_client_uses_the_seed():
    prompt = get_system_prompt(PROMPT_NAME, None)
    assert prompt.text == load_seed(PROMPT_NAME) and prompt.version is None


def test_with_client_uses_langfuse_and_its_version():
    prompt = get_system_prompt(PROMPT_NAME, FakeLangfuse())
    assert prompt.text == "FROM LANGFUSE" and prompt.version == 7


def test_langfuse_fallback_reports_no_version():
    prompt = get_system_prompt(PROMPT_NAME, FakeLangfuse(exists=False))
    assert prompt.text == load_seed(PROMPT_NAME) and prompt.version is None


def test_sync_seed_creates_only_when_missing():
    missing = FakeLangfuse(exists=False)
    assert sync_seed(PROMPT_NAME, missing) is True
    assert missing.created["name"] == PROMPT_NAME and missing.created["labels"] == ["production"]
    present = FakeLangfuse()
    assert sync_seed(PROMPT_NAME, present) is False and present.created is None


def test_no_client_without_keys():
    assert langfuse_client({}) is None
