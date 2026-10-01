"""What the code resolves before the agent runs, and what is left for the agent to decide.

This is the deterministic half of V2 (decision 10, table vs agent). Most of what today's
`attributeReferencePrompt` asks the LLM to do (join by legacy id, copy the URN, look up the
type) is a lookup, so it happens here. The model only gets what needs judgment.
"""

from pydantic import BaseModel

from .data import NO_DATA
from .models import MappedAttribute
from .reference import Reference

# Fields of a channel attribute definition that the agent needs to decide a value.
CHANNEL_FIELDS = ("urn", "name", "type", "mandatory", "maxValues")


def normalize(value) -> str:
    """Comparison form of a value: trimmed and case-folded, so "NOVO " and "Novo" match."""
    return str(value).strip().casefold()


def _values(definition: dict) -> list[dict]:
    # `valueId` is a string in the contract, so ids are compared as strings whatever the JSON holds.
    return [{"id": str(v["id"]), "name": v["name"]} for v in definition.get("values") or []]


def _channel(definition: dict) -> dict:
    return {**{k: definition.get(k) for k in CHANNEL_FIELDS}, "values": _values(definition)}


# The four buckets of a product, serialized into V2's work message for the agent:
#   resolved: final values the code already decided; they win over the agent in merge_resolved.
#   to_decide: the table names the target attribute but the value needs judgment (e.g. "1" -> Sim).
#   unmapped_product: product attributes with no row in reference_attribute for this category.
#   uncovered_channel: channel attributes no product attribute reached; mandatory ones may end
#     up in `missing`.
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
        # "-1", "N/A" and "" mean no data: mapping them would publish a fake value.
        if value in NO_DATA:
            continue
        target = reference.target_for(attribute["urn"], schema)
        if target is None:
            unmapped.append({"legacy_id": attribute["urn"], "name": attribute.get("name"), "value": value,
                             "unit": attribute.get("unit")})
            continue
        # First product attribute wins a target: two legacy fields pointing to the same Shopee
        # attribute must not produce a duplicate (the kind of duplicate today's output shows).
        if target in covered:
            continue
        covered.add(target)
        definition = definitions[target]
        values = _values(definition)
        unit = str(attribute.get("unit") or "").strip()
        # Free text with no unit: the product value is copied as is. With a unit it goes to the
        # agent, which decides whether and how the unit fits the channel.
        if not values and unit in NO_DATA:
            resolved.append(MappedAttribute(urn=target, valueId="0", value=value, unit=None))
            continue
        # List attribute whose value matches a channel value by name: take the channel's id and
        # spelling. Anything else needs judgment and goes to the agent.
        match = next((v for v in values if normalize(v["name"]) == normalize(value)), None)
        if match is not None:
            resolved.append(MappedAttribute(urn=target, valueId=match["id"], value=match["name"], unit=None))
            continue
        to_decide.append({"legacy_id": attribute["urn"], "product_name": attribute.get("name"),
                          "product_value": value, "product_unit": attribute.get("unit"),
                          "target_urn": target, **{k: v for k, v in _channel(definition).items() if k != "urn"}})
    uncovered = [_channel(d) for urn, d in definitions.items() if urn not in covered]
    return Worklist(resolved=resolved, to_decide=to_decide, unmapped_product=unmapped, uncovered_channel=uncovered)
