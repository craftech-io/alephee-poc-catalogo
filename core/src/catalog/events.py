"""Events of the mapping workflows.

LlamaIndex Workflows route by type: each `@step` declares the event it accepts and the events
it can return, and the engine wires the steps from those signatures.

    V1: MappingRequested -> prepare -> ContextReady -> map -> MappingCompleted
    V2: MappingRequested -> check_cache -> CacheMissed -> resolve -> WorkReady
        -> run_agent -> AgentDone -> finalize -> MappingCompleted

In V2, `check_cache` (cache hit) and `resolve` (no category) can also end the run early with a
MappingCompleted.
"""

from typing import Literal

from llama_index.core.base.llms.types import ChatMessage
from workflows.events import Event, StartEvent, StopEvent

from .models import Listing
from .worklist import Worklist


class MappingRequested(StartEvent):
    """Start of both workflows: `workflow.run(product=...)` builds this event from the kwargs."""

    product: dict


class ContextReady(Event):
    """V1: the messages for the single structured call, already in cache-friendly order."""

    messages: list[ChatMessage]


class MappingCompleted(StopEvent):
    """End of a mapping. No field is called `result`: it would collide with StopEvent's."""

    listing: Listing | None
    error: str | None = None
    # Where the listing came from: "model" (V1, the default), or "cache", "tables" or
    # "agent" (V2 — see `source=` in v2.py for where each one is emitted).
    source: Literal["model", "cache", "tables", "agent"] = "model"


class CacheMissed(Event):
    """V2: no valid cached listing for this SKU, so the mapping has to be computed."""

    product: dict


class WorkReady(Event):
    """V2: category fixed by the reference table and the worklist split between code and agent."""

    product: dict
    category_urn: str
    category_name: str
    worklist: Worklist


class AgentDone(Event):
    """V2: what the agent loop left behind, for `finalize` to merge, clean and maybe cache."""

    product: dict
    category_urn: str
    worklist: Worklist
    # The agent's last submit_listing call, valid or not; None if it never submitted.
    last: Listing | None
    # Whether `last` passed validation. Only a valid listing is written to the cache.
    valid: bool
    error: str | None = None
    # True when the loop stopped because it ran out of iterations, not because of an error.
    exhausted: bool = False
