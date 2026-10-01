"""System prompts: Langfuse is the source; the seed in prompts/ is the first version and the fallback."""

from dataclasses import dataclass
from pathlib import Path

PROMPT_NAME = "catalog-v1-system"
LABEL = "production"
_SEEDS = Path(__file__).resolve().parent / "prompts"


@dataclass(frozen=True)
class SystemPrompt:
    text: str
    name: str
    version: int | None  # None: the seed (Langfuse not configured or unreachable)


def load_seed(name: str) -> str:
    return (_SEEDS / f"{name}.txt").read_text(encoding="utf-8").strip()


def get_system_prompt(name: str, client) -> SystemPrompt:
    seed = load_seed(name)
    if client is None:
        return SystemPrompt(seed, name, None)
    prompt = client.get_prompt(name, label=LABEL, fallback=seed)
    return SystemPrompt(prompt.compile(), name, None if prompt.is_fallback else prompt.version)


def sync_seed(name: str, client) -> bool:
    """Create the prompt in Langfuse from the seed if it does not exist yet."""
    try:
        client.get_prompt(name, label=LABEL, max_retries=0)
        return False
    except Exception:  # noqa: BLE001 — the SDK raises a generic API error for "not found"
        client.create_prompt(name=name, prompt=load_seed(name), labels=[LABEL], type="text",
                             commit_message="seed from the repo")
        return True
