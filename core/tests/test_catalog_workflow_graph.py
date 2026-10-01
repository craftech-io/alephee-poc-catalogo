"""Pin the event graph of each Workflow: the deck and docs/workflows.md draw exactly these edges."""

from workflows.representation import get_workflow_representation

from catalog.v1 import MappingV1
from catalog.v2 import MappingV2


def _edges(workflow) -> set[tuple[str, str]]:
    return {(e.source, e.target) for e in get_workflow_representation(workflow).edges}


def test_v1_is_a_two_step_chain():
    assert _edges(MappingV1) == {
        ("MappingRequested", "prepare"), ("prepare", "ContextReady"),
        ("ContextReady", "map"), ("map", "MappingCompleted"),
    }


def test_v2_can_end_at_cache_tables_or_agent():
    assert _edges(MappingV2) == {
        ("MappingRequested", "check_cache"),
        ("check_cache", "MappingCompleted"), ("check_cache", "CacheMissed"),
        ("CacheMissed", "resolve"),
        ("resolve", "MappingCompleted"), ("resolve", "WorkReady"),
        ("WorkReady", "run_agent"), ("run_agent", "AgentDone"),
        ("AgentDone", "finalize"), ("finalize", "MappingCompleted"),
    }
