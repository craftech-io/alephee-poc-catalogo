"""Reference tables kept by Alephee's catalog team: legacy (Mercado Libre) ids to Shopee ids.

`reference_category` maps one legacy category to one Shopee category. `reference_attribute`
maps fields, not values, and one legacy id can point to several Shopee attributes: the
right one is the one that belongs to the product's Shopee category.
"""

import hashlib
import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path


def legacy_id(urn_or_id: str) -> str:
    """'urn:category:734701' -> '734701'; 'urn:attribute:1673' -> '1673'; bare ids stay as they are."""
    return str(urn_or_id).removeprefix("urn:category:").removeprefix("urn:attribute:").split(":", 1)[0]


@dataclass(frozen=True)
class Reference:
    categories: dict[str, dict]
    attributes: dict[str, list[dict]]
    version: str

    def category_for(self, product: dict) -> dict | None:
        categories = product.get("categories") or []
        if not categories:
            return None
        return self.categories.get(legacy_id(categories[0]["urn"]))

    def target_for(self, attribute_urn: str, schema: dict) -> str | None:
        in_category = {a["urn"] for a in schema["attributes"]}
        return next((row["urn"] for row in self.attributes.get(legacy_id(attribute_urn), [])
                     if row["urn"] in in_category), None)


@cache
def load_reference(directory: Path) -> Reference:
    category_bytes = (directory / "reference_category.json").read_bytes()
    attribute_bytes = (directory / "reference_attribute.json").read_bytes()
    categories = {legacy_id(row["legacyId"]): {"urn": row["urn"], "name": row["name"]}
                  for row in json.loads(category_bytes)["rows"]}
    attributes: dict[str, list[dict]] = {}
    for row in json.loads(attribute_bytes)["rows"]:
        attributes.setdefault(legacy_id(row["legacyId"]), []).append({"urn": row["urn"], "name": row["name"]})
    version = hashlib.sha256(category_bytes + attribute_bytes).hexdigest()[:12]
    return Reference(categories=categories, attributes=attributes, version=version)
