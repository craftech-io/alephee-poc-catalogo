"""Output contract of the catalog agent.

Field names follow Alephee's listing format (`valueId`, `legacyId`), not snake_case,
so the output can be compared and stored without translation.
"""

# The same `Listing` is the structured output of V1 (`as_structured_llm(Listing)`) and the
# argument schema of V2's `submit_listing` tool. Pydantic turns class docstrings and
# `Field(description=...)` into the JSON schema that Bedrock receives, so they are part of
# what the model reads: explanations for humans in this module go in `#` comments only.

from pydantic import BaseModel, ConfigDict, Field


# `extra="forbid"` becomes `additionalProperties: false` in the schema: the model cannot add
# fields outside the contract, and a stray key fails validation instead of being kept silently.
class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


# One filled channel attribute. For list attributes (dropdown, combo box) `valueId` must be an
# id from the channel domain; guardrails.py rejects anything else. Free text uses valueId "0".
class MappedAttribute(_Strict):
    urn: str = Field(description="Channel attribute URN, copied exactly from the catalog.")
    valueId: str = Field(description="Id of the channel value, or '0' for free-text attributes.")
    value: str = Field(description="Value name exactly as the channel lists it.")
    unit: str | None = Field(default=None, description="Unit accepted by the channel, or null.")


# A mandatory channel attribute the product cannot fill. The agent never invents a value to
# cover it: it reports it here so a person loads it by hand. This replaces today's behavior of
# publishing without attributes. The urn "category" means the category itself is unresolved.
class MissingAttribute(_Strict):
    urn: str = Field(description="URN of the mandatory channel attribute (or 'category').")
    reason: str


# A product attribute that was discarded, with the reason. Rejections added by the guardrails
# carry the channel urn here instead, because the validator does not know the source attribute.
class RejectedAttribute(_Strict):
    legacyId: str = Field(description="Product attribute id, without the 'urn:attribute:' prefix.")
    reason: str


# The full answer for one product. In V2 the category is fixed by `reference_category` and the
# guardrails force it back if the model returns a different one.
class Listing(_Strict):
    """Result of mapping one product to a channel listing."""

    category: str | None = Field(description="Channel category URN, copied exactly. Null if it cannot be resolved.")
    attributes: list[MappedAttribute]
    missing: list[MissingAttribute] = Field(description="Mandatory channel attributes (or the category) that could not be filled.")
    rejected: list[RejectedAttribute] = Field(description="Product attributes that are discarded, with the reason.")
