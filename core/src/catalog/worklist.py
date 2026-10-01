"""What the code resolves before the agent runs, and what is left for the agent to decide."""

from pydantic import BaseModel

from .data import NO_DATA
from .models import MappedAttribute
from .reference import Reference

CHANNEL_FIELDS = ("urn", "name", "type", "mandatory", "maxValues")


def normalize(value) -> str:
    return str(value).strip().casefold()


def _values(definition: dict) -> list[dict]:
    return [{"id": str(v["id"]), "name": v["name"]} for v in definition.get("values") or []]


def _channel(definition: dict) -> dict:
    return {**{k: definition.get(k) for k in CHANNEL_FIELDS}, "values": _values(definition)}


class Worklist(BaseModel):
    resolved: list[MappedAttribute]
    to_decide: list[dict]
    unmapped_product: list[dict]
    uncovered_channel: list[dict]


def build_worklist(product: dict, schema: dict, reference: Reference) -> Worklist:
    """Resolve by code what the reference table and an exact value match already answer."""
    definitions = {a["urn"]: a for a in schema["attributes"]}
    resolved: list[MappedAttribute] = []
    to_decide: list[dict] = []
    unmapped: list[dict] = []
    covered: set[str] = set()
    for attribute in product.get("attributes") or []:
        value = str(attribute.get("value", "")).strip()
        if value in NO_DATA:
            continue
        target = reference.target_for(attribute["urn"], schema)
        if target is None:
            unmapped.append({"legacy_id": attribute["urn"], "name": attribute.get("name"), "value": value,
                             "unit": attribute.get("unit")})
            continue
        if target in covered:
            continue
        covered.add(target)
        definition = definitions[target]
        values = _values(definition)
        unit = str(attribute.get("unit") or "").strip()
        if not values and unit in NO_DATA:
            resolved.append(MappedAttribute(urn=target, valueId="0", value=value, unit=None))
            continue
        match = next((v for v in values if normalize(v["name"]) == normalize(value)), None)
        if match is not None:
            resolved.append(MappedAttribute(urn=target, valueId=match["id"], value=match["name"], unit=None))
            continue
        to_decide.append({"legacy_id": attribute["urn"], "product_name": attribute.get("name"),
                          "product_value": value, "product_unit": attribute.get("unit"),
                          "target_urn": target, **{k: v for k, v in _channel(definition).items() if k != "urn"}})
    uncovered = [_channel(d) for urn, d in definitions.items() if urn not in covered]
    return Worklist(resolved=resolved, to_decide=to_decide, unmapped_product=unmapped, uncovered_channel=uncovered)
