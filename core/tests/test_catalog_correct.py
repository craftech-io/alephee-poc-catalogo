import pytest

from catalog.correct import main
from catalog.models import Listing
from catalog.store import InMemoryCache, InMemoryCorrections

CALOTAS = "urn:category:102529:vendor:shopee"
CONDITION = "urn:attribute:101638:vendor:shopee"
ARGS = ["--category", CALOTAS, "--attribute", CONDITION, "--product-value", "1", "--value-id", "14703", "--value", "Novo"]


def test_correct_stores_the_correction_and_invalidates_the_category():
    corrections, cache = InMemoryCorrections(), InMemoryCache()
    cache.put("94701411", "734701", "t", "seed", CALOTAS, Listing(category=CALOTAS, attributes=[], missing=[], rejected=[]))
    main(ARGS, stores=(corrections, cache, "in-memory"))
    assert corrections.find(CALOTAS, CONDITION, "1").value == "Novo"
    assert cache.get("94701411", "734701", "t", "seed") is None


def test_correct_rejects_a_value_outside_the_channel_list():
    with pytest.raises(SystemExit) as info:
        main([*ARGS[:-4], "--value-id", "99999", "--value", "Nuevo"], stores=(InMemoryCorrections(), InMemoryCache(), "in-memory"))
    assert "not in the channel list" in str(info.value)
