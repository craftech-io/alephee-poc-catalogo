"""Events of the mapping workflows."""

from llama_index.core.base.llms.types import ChatMessage
from workflows.events import Event, StartEvent, StopEvent

from .models import Listing


class MappingRequested(StartEvent):
    product: dict


class ContextReady(Event):
    messages: list[ChatMessage]


class MappingCompleted(StopEvent):
    """End of a mapping. No field is called `result`: it would collide with StopEvent's."""

    listing: Listing | None
    error: str | None = None
