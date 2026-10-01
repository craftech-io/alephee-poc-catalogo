"""Corrections from the catalog team and the per-SKU mapping cache.

Both live in DynamoDB in the `warroom` stage; the in-memory versions serve tests and runs
without the account. Expressions are plain strings so a tiny fake table can evaluate them.
"""

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path

from .data import ROOT
from .models import Listing
from .worklist import normalize


@dataclass(frozen=True)
class Correction:
    category_urn: str
    attribute_urn: str
    product_value: str
    value_id: str
    value: str
    author: str
    created_at: str


def correction_key(attribute_urn: str, product_value: str) -> str:
    return f"{attribute_urn}#{normalize(product_value)}"


class InMemoryCorrections:
    def __init__(self):
        self._items: dict[tuple[str, str], Correction] = {}

    def find(self, category_urn, attribute_urn, product_value):
        return self._items.get((category_urn, correction_key(attribute_urn, product_value)))

    def put(self, correction: Correction) -> None:
        self._items[(correction.category_urn, correction_key(correction.attribute_urn, correction.product_value))] = correction

    def list(self, category_urn):
        return [c for (category, _), c in self._items.items() if category == category_urn]


class DynamoCorrections:
    def __init__(self, table):
        self.table = table

    def find(self, category_urn, attribute_urn, product_value):
        item = self.table.get_item(Key={"category_urn": category_urn,
                                        "correction_key": correction_key(attribute_urn, product_value)}).get("Item")
        return _correction(item) if item else None

    def put(self, correction: Correction) -> None:
        self.table.put_item(Item={**asdict(correction),
                                  "correction_key": correction_key(correction.attribute_urn, correction.product_value)})

    def list(self, category_urn):
        response = self.table.query(KeyConditionExpression="category_urn = :c",
                                    ExpressionAttributeValues={":c": category_urn})
        return [_correction(item) for item in response.get("Items", [])]


def _correction(item: dict) -> Correction:
    return Correction(**{k: item[k] for k in Correction.__dataclass_fields__})


def _cache_keys(sku, legacy_category, tables_version, prompt_version) -> tuple[str, str]:
    return f"{sku}#{legacy_category}", f"{tables_version}#{prompt_version}"


class InMemoryCache:
    def __init__(self):
        self._items: dict[tuple[str, str], tuple[str, Listing]] = {}

    def get(self, sku, legacy_category, tables_version, prompt_version):
        hit = self._items.get(_cache_keys(sku, legacy_category, tables_version, prompt_version))
        return hit[1] if hit else None

    def put(self, sku, legacy_category, tables_version, prompt_version, category_urn, listing: Listing) -> None:
        self._items[_cache_keys(sku, legacy_category, tables_version, prompt_version)] = (category_urn, listing)

    def invalidate_category(self, category_urn) -> int:
        stale = [k for k, (category, _) in self._items.items() if category == category_urn]
        for key in stale:
            del self._items[key]
        return len(stale)


class DynamoCache:
    def __init__(self, table):
        self.table = table

    def get(self, sku, legacy_category, tables_version, prompt_version):
        product_key, version_key = _cache_keys(sku, legacy_category, tables_version, prompt_version)
        item = self.table.get_item(Key={"product_key": product_key, "version_key": version_key}).get("Item")
        return Listing.model_validate_json(item["listing"]) if item else None

    def put(self, sku, legacy_category, tables_version, prompt_version, category_urn, listing: Listing) -> None:
        product_key, version_key = _cache_keys(sku, legacy_category, tables_version, prompt_version)
        self.table.put_item(Item={"product_key": product_key, "version_key": version_key,
                                  "category_urn": category_urn, "listing": listing.model_dump_json()})

    def invalidate_category(self, category_urn) -> int:
        items = self.table.scan(FilterExpression="category_urn = :c",
                                ExpressionAttributeValues={":c": category_urn}).get("Items", [])
        for item in items:
            self.table.delete_item(Key={"product_key": item["product_key"], "version_key": item["version_key"]})
        return len(items)


def _dynamodb(env):
    import boto3

    session = boto3.Session(profile_name=env.get("AWS_PROFILE") or None, region_name=env.get("AWS_REGION", "us-east-1"))
    return session.resource("dynamodb")


def stores_from_env(env=os.environ, outputs_path: Path = ROOT / ".sst/outputs.json", resource_factory=None):
    """DynamoDB tables from the env (Runtime) or from the deploy outputs (local); in memory otherwise."""
    names = {"corrections": env.get("CATALOG_CORRECTIONS_TABLE"), "cache": env.get("CATALOG_CACHE_TABLE")}
    if not all(names.values()) and outputs_path.exists():
        outputs = json.loads(outputs_path.read_text())
        names = {"corrections": outputs.get("correctionsTable"), "cache": outputs.get("mappingCacheTable")}
    if not all(names.values()):
        return InMemoryCorrections(), InMemoryCache(), "in-memory"
    resource = (resource_factory or _dynamodb)(env)
    return DynamoCorrections(resource.Table(names["corrections"])), DynamoCache(resource.Table(names["cache"])), "dynamodb"
