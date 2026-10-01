"""Checks in code: nothing leaves out of contract, whatever the model says.

`validate` lists the problems in plain language (the agent gets them back and fixes them).
`clean` is the final net: it fixes the category, discards what is invalid and marks the
mandatory attributes that are missing. It never invents a value. Guardrail rejections carry
the channel attribute urn in `legacyId`, because the validator does not know which product
attribute produced the value.
"""

from collections import Counter

from .data import NO_DATA
from .models import Listing, MappedAttribute, MissingAttribute, RejectedAttribute


def _definitions(schema: dict) -> dict[str, dict]:
    return {a["urn"]: a for a in schema["attributes"]}


def _attribute_problem(attribute: MappedAttribute, definitions: dict[str, dict], category_urn: str) -> str | None:
    definition = definitions.get(attribute.urn)
    if definition is None:
        return f"{attribute.urn} is not an attribute of category {category_urn}"
    if attribute.value.strip() in NO_DATA:
        return f"{attribute.urn}: '{attribute.value}' means no data; do not submit it"
    domain = {str(v["id"]): v["name"] for v in definition.get("values") or []}
    if domain and attribute.valueId not in domain:
        return f"{attribute.urn}: value '{attribute.value}' (id {attribute.valueId}) is not in the channel list"
    if domain and domain[attribute.valueId] != attribute.value:
        return f"{attribute.urn}: name '{attribute.value}' does not match id {attribute.valueId} ('{domain[attribute.valueId]}')"
    return None


def validate(listing: Listing, schema: dict, category_urn: str) -> list[str]:
    definitions = _definitions(schema)
    problems = []
    if listing.category != category_urn:
        problems.append(f"category must be {category_urn} (it comes from the reference table)")
    problems += [p for a in listing.attributes if (p := _attribute_problem(a, definitions, category_urn))]
    counts = Counter(a.urn for a in listing.attributes)
    problems += [f"{urn} appears {n} times; keep only one" for urn, n in counts.items() if n > 1]
    missing = {m.urn for m in listing.missing}
    problems += [f"{urn} ({d.get('name')}) is mandatory: fill it or add it to missing with the reason"
                 for urn, d in definitions.items() if d.get("mandatory") and urn not in counts and urn not in missing]
    return problems


def clean(listing: Listing, schema: dict, category_urn: str) -> Listing:
    definitions = _definitions(schema)
    kept: list[MappedAttribute] = []
    rejected = list(listing.rejected)
    seen: set[str] = set()
    for attribute in listing.attributes:
        problem = _attribute_problem(attribute, definitions, category_urn) or (
            f"{attribute.urn} duplicated" if attribute.urn in seen else None)
        if problem:
            rejected.append(RejectedAttribute(legacyId=attribute.urn, reason=f"guardrail: {problem}"))
            continue
        seen.add(attribute.urn)
        kept.append(attribute)
    missing: list[MissingAttribute] = []
    already: set[str] = set()
    for m in listing.missing:
        if m.urn in seen or m.urn == "category" or m.urn in already:
            continue
        already.add(m.urn)
        missing.append(m)
    missing += [MissingAttribute(urn=urn, reason="mandatory with no valid value (guardrail)")
                for urn, d in definitions.items() if d.get("mandatory") and urn not in seen and urn not in already]
    return Listing(category=category_urn, attributes=kept, missing=missing, rejected=rejected)


def merge_resolved(listing: Listing, resolved: list[MappedAttribute]) -> Listing:
    """What the code resolved from the reference table wins over the agent.

    `resolved` is deduplicated by urn, keeping the first occurrence, so a caller that
    passes two entries for the same urn never produces two attributes in the output.
    """
    deduplicated: list[MappedAttribute] = []
    fixed: set[str] = set()
    for a in resolved:
        if a.urn in fixed:
            continue
        fixed.add(a.urn)
        deduplicated.append(a)
    attributes = [*deduplicated, *(a for a in listing.attributes if a.urn not in fixed)]
    missing = [m for m in listing.missing if m.urn not in fixed]
    return Listing(category=listing.category, attributes=attributes, missing=missing, rejected=list(listing.rejected))
