"""System prompts: Langfuse is the source; the seed in prompts/ is the first version and the fallback.

Keeping the prompt in Langfuse lets the room edit it and compare experiment runs by prompt
version without a deploy. The seed keeps tests, offline runs and the deployed chat (which has
no Langfuse keys) working with the same text that is committed in the repo.
"""

from dataclasses import dataclass
from pathlib import Path

PROMPT_NAME = "catalog-v1-system"
PROMPT_NAME_V2 = "catalog-v2-system"
# The Langfuse label that is read and written; moving it to another version changes the prompt.
LABEL = "production"
_SEEDS = Path(__file__).resolve().parent / "prompts"


@dataclass(frozen=True)
class SystemPrompt:
    """The prompt text plus where it came from, so runs and cache entries can record the version."""

    text: str
    name: str
    version: int | None  # None: the seed (Langfuse not configured or unreachable)


def load_seed(name: str) -> str:
    """Text of `prompts/<name>.txt`, the version committed in the repo."""
    return (_SEEDS / f"{name}.txt").read_text(encoding="utf-8").strip()


def get_system_prompt(name: str, client) -> SystemPrompt:
    """The `production` prompt from Langfuse, or the seed when there is no client or Langfuse fails."""
    seed = load_seed(name)
    if client is None:
        return SystemPrompt(seed, name, None)
    # With `fallback`, the SDK returns the seed instead of raising when Langfuse is unreachable,
    # and flags it with `is_fallback`, so the version is reported as None (the seed), not a number.
    prompt = client.get_prompt(name, label=LABEL, fallback=seed)
    return SystemPrompt(prompt.compile(), name, None if prompt.is_fallback else prompt.version)


def sync_seed(name: str, client) -> bool:
    """Create the prompt in Langfuse from the seed if it does not exist yet."""
    # Only creates, never overwrites: edits made in Langfuse during the day are not lost.
    try:
        # No retries: a missing prompt is the expected case on the first run, not a failure.
        client.get_prompt(name, label=LABEL, max_retries=0)
        return False
    except Exception:  # noqa: BLE001 — the SDK raises a generic API error for "not found"
        client.create_prompt(name=name, prompt=load_seed(name), labels=[LABEL], type="text",
                             commit_message="seed from the repo")
        return True
