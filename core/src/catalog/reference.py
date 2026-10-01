"""Reference tables kept by Alephee's catalog team: legacy (Mercado Libre) ids to Shopee ids.

`reference_category` maps one legacy category to one Shopee category. `reference_attribute`
maps fields, not values, and one legacy id can point to several Shopee attributes: the
right one is the one that belongs to the product's Shopee category.

V2 only (V1 never sees these tables). The rule is that the table wins: whatever it answers
is resolved in code and never goes to the model.
"""

import hashlib
import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path


def legacy_id(urn_or_id: str) -> str:
    """'urn:category:734701' -> '734701'; 'urn:attribute:1673' -> '1673'; bare ids stay as they are."""
    # The tables store the bare number in `legacyId` while the product carries the full URN,
    # so both sides go through this function before any lookup. Anything after a further ':'
    # is dropped too, so a suffixed id still joins on its number.
    return str(urn_or_id).removeprefix("urn:category:").removeprefix("urn:attribute:").split(":", 1)[0]


@dataclass(frozen=True)
class Reference:
    """Both tables indexed by bare legacy id, plus a version hash of their content."""

    # legacy category id -> {"urn", "name"} of the Shopee category.
    categories: dict[str, dict]
    # legacy attribute id -> every Shopee attribute it maps to, across all categories.
    attributes: dict[str, list[dict]]
    # Part of the cache key: when the catalog team updates a table, old cache entries stop matching.
    version: str

    def category_for(self, product: dict) -> dict | None:
        """Shopee category for the product's first legacy category, or None if the table lacks it."""
        # `categories` may be missing or empty: the current prompt breaks there, this returns None.
        categories = product.get("categories") or []
        if not categories:
            return None
        return self.categories.get(legacy_id(categories[0]["urn"]))

    def target_for(self, attribute_urn: str, schema: dict) -> str | None:
        """Shopee attribute urn for a product attribute, restricted to the category in `schema`."""
        # One legacy id can map to several Shopee attributes (306 of them in the real export);
        # only the one that exists in this category's schema is a valid target.
        in_category = {a["urn"] for a in schema["attributes"]}
        return next((row["urn"] for row in self.attributes.get(legacy_id(attribute_urn), [])
                     if row["urn"] in in_category), None)


@cache
def load_reference(directory: Path) -> Reference:
    """Read and index both tables of a dataset folder, once per process."""
    category_bytes = (directory / "reference_category.json").read_bytes()
    attribute_bytes = (directory / "reference_attribute.json").read_bytes()
    categories = {legacy_id(row["legacyId"]): {"urn": row["urn"], "name": row["name"]}
                  for row in json.loads(category_bytes)["rows"]}
    attributes: dict[str, list[dict]] = {}
    for row in json.loads(attribute_bytes)["rows"]:
        attributes.setdefault(legacy_id(row["legacyId"]), []).append({"urn": row["urn"], "name": row["name"]})
    # Hash of the raw bytes, not of the parsed rows: any change to either file is a new version.
    version = hashlib.sha256(category_bytes + attribute_bytes).hexdigest()[:12]
    return Reference(categories=categories, attributes=attributes, version=version)
