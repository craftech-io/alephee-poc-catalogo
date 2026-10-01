"""Output contract of the catalog agent.

Field names follow Alephee's listing format (`valueId`, `legacyId`), not snake_case,
so the output can be compared and stored without translation.
"""

from pydantic import BaseModel, ConfigDict, Field


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class MappedAttribute(_Strict):
    urn: str = Field(description="Channel attribute URN, copied exactly from the catalog.")
    valueId: str = Field(description="Id of the channel value, or '0' for free-text attributes.")
    value: str = Field(description="Value name exactly as the channel lists it.")
    unit: str | None = Field(default=None, description="Unit accepted by the channel, or null.")


class MissingAttribute(_Strict):
    urn: str = Field(description="URN of the mandatory channel attribute (or 'category').")
    reason: str


class RejectedAttribute(_Strict):
    legacyId: str = Field(description="Product attribute id, without the 'urn:attribute:' prefix.")
    reason: str


class Listing(_Strict):
    """Result of mapping one product to a channel listing."""

    category: str | None = Field(description="Channel category URN, copied exactly. Null if it cannot be resolved.")
    attributes: list[MappedAttribute]
    missing: list[MissingAttribute] = Field(description="Mandatory channel attributes (or the category) that could not be filled.")
    rejected: list[RejectedAttribute] = Field(description="Product attributes that are discarded, with the reason.")
