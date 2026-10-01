import json

from catalog.models import Listing
from catalog.store import (Correction, DynamoCache, DynamoCorrections, InMemoryCache, InMemoryCorrections,
                           correction_key, stores_from_env)

CALOTAS = "urn:category:102529:vendor:shopee"
CONDITION = "urn:attribute:101638:vendor:shopee"
LISTING = Listing(category=CALOTAS, attributes=[], missing=[], rejected=[])


def _correction(product_value="Usado"):
    return Correction(category_urn=CALOTAS, attribute_urn=CONDITION, product_value=product_value,
                      value_id="14703", value="Novo", author="catalog", created_at="2026-10-01")


class FakeTable:
    """Just enough of a boto3 Table: string key conditions with one :c value."""

    def __init__(self, keys):
        self.keys, self.items = keys, {}

    def _key(self, item):
        return tuple(item[k] for k in self.keys)

    def put_item(self, Item):
        self.items[self._key(Item)] = dict(Item)

    def get_item(self, Key):
        item = self.items.get(self._key(Key))
        return {"Item": item} if item else {}

    def delete_item(self, Key):
        self.items.pop(self._key(Key), None)

    def query(self, KeyConditionExpression, ExpressionAttributeValues, **kwargs):
        field = KeyConditionExpression.split(" = ")[0]
        return {"Items": [i for i in self.items.values() if i[field] == ExpressionAttributeValues[":c"]]}

    def scan(self, FilterExpression, ExpressionAttributeValues, **kwargs):
        field = FilterExpression.split(" = ")[0]
        return {"Items": [i for i in self.items.values() if i[field] == ExpressionAttributeValues[":c"]]}


def test_correction_key_normalizes_the_product_value():
    assert correction_key(CONDITION, "  USADO ") == correction_key(CONDITION, "usado")


def test_corrections_in_memory_and_dynamo_find_by_normalized_value():
    for store in (InMemoryCorrections(), DynamoCorrections(FakeTable(("category_urn", "correction_key")))):
        store.put(_correction("Usado"))
        assert store.find(CALOTAS, CONDITION, " usado ").value == "Novo"
        assert store.find(CALOTAS, CONDITION, "otro") is None
        assert [c.value for c in store.list(CALOTAS)] == ["Novo"]


def test_cache_in_memory_and_dynamo_roundtrip_and_invalidate_by_category():
    for cache in (InMemoryCache(), DynamoCache(FakeTable(("product_key", "version_key")))):
        cache.put("94701411", "734701", "t1", "seed", CALOTAS, LISTING)
        assert cache.get("94701411", "734701", "t1", "seed") == LISTING
        assert cache.get("94701411", "734701", "t2", "seed") is None
        assert cache.invalidate_category(CALOTAS) == 1
        assert cache.get("94701411", "734701", "t1", "seed") is None


def test_stores_from_env_without_tables_is_in_memory(tmp_path):
    corrections, cache, label = stores_from_env({}, outputs_path=tmp_path / "missing.json")
    assert label == "in-memory"
    assert isinstance(corrections, InMemoryCorrections) and isinstance(cache, InMemoryCache)


def test_stores_from_env_reads_table_names_from_outputs(tmp_path):
    outputs = tmp_path / "outputs.json"
    outputs.write_text(json.dumps({"correctionsTable": "corr-t", "mappingCacheTable": "cache-t"}))
    seen = []

    def resource_factory(env):
        class Resource:
            def Table(self, name):
                seen.append(name)
                return FakeTable(("a", "b"))
        return Resource()

    corrections, cache, label = stores_from_env({}, outputs_path=outputs, resource_factory=resource_factory)
    assert label == "dynamodb" and seen == ["corr-t", "cache-t"]
    assert isinstance(corrections, DynamoCorrections) and isinstance(cache, DynamoCache)
