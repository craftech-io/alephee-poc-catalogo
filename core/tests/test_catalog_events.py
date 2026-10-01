import pytest
from pydantic import ValidationError

from catalog.events import MappingCompleted
from catalog.models import Listing


def test_mapping_completed_defaults_to_model_source():
    completed = MappingCompleted(listing=Listing(category="urn:x", attributes=[], missing=[], rejected=[]))
    assert completed.source == "model"


@pytest.mark.parametrize("source", ["model", "tables", "cache", "agent"])
def test_mapping_completed_accepts_every_source_the_code_emits(source):
    completed = MappingCompleted(listing=None, error="x", source=source)
    assert completed.source == source


def test_mapping_completed_rejects_an_unknown_source():
    """Task 4 (final fix wave): `source` is typed as a `Literal` of exactly the values the
    code emits (grep for `source=` in core/src/catalog): "tables" and "agent" from v2.py,
    "cache" from v2.py's cache hit, and the "model" default (V1 and the base case)."""
    with pytest.raises(ValidationError):
        MappingCompleted(listing=None, error="x", source="unknown")
