"""Events of the mapping workflows."""

from llama_index.core.base.llms.types import ChatMessage
from workflows.events import Event, StartEvent, StopEvent

from .models import Listing
from .worklist import Worklist


class MappingRequested(StartEvent):
    product: dict


class ContextReady(Event):
    messages: list[ChatMessage]


class MappingCompleted(StopEvent):
    """End of a mapping. No field is called `result`: it would collide with StopEvent's."""

    listing: Listing | None
    error: str | None = None
    # Where the listing came from: "model" (V1), "cache", "tables" or "agent" (V2).
    source: str = "model"


class CacheMissed(Event):
    product: dict


class WorkReady(Event):
    product: dict
    category_urn: str
    category_name: str
    worklist: Worklist


class AgentDone(Event):
    product: dict
    category_urn: str
    worklist: Worklist
    last: Listing | None
    valid: bool
    error: str | None = None
    # True when the loop stopped because it ran out of iterations, not because of an error.
    exhausted: bool = False
