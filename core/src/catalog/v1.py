"""V1 · a single structured call, no tools.

The model sees the Shopee catalog (every category with its attributes and valid values)
and the product, and returns a `Listing`. It does not see the reference tables: its
mistakes are what justify V2.
"""

import json

from llama_index.core.base.llms.types import CacheControl, CachePoint, ChatMessage, TextBlock
from workflows import Workflow, step

from .events import ContextReady, MappingCompleted, MappingRequested
from .llm import is_auth_error
from .models import Listing

# Real descriptions reach 19,000 characters; the beginning is enough to map attributes.
MAX_DESCRIPTION = 1500
PRODUCT_FIELDS = ("sku", "name", "categories", "brand", "attributes", "description")
ATTRIBUTE_FIELDS = ("urn", "name", "type", "mandatory", "maxValues")


def _compact(value) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def catalog_text(schemas: dict[str, dict]) -> str:
    """Same text for every product, in a fixed order, so the prefix stays cacheable."""
    catalog = [
        {"urn": urn, "name": schema.get("name"), "attributes": [
            {**{k: a.get(k) for k in ATTRIBUTE_FIELDS},
             "values": [{"id": v["id"], "name": v["name"]} for v in a.get("values", [])]}
            for a in sorted(schema["attributes"], key=lambda a: a["urn"])
        ]}
        for urn, schema in sorted(schemas.items())
    ]
    return "Shopee categories and the attributes each one expects:\n" + _compact(catalog)


def product_text(product: dict) -> str:
    trimmed = {k: product.get(k) for k in PRODUCT_FIELDS}
    trimmed["description"] = (trimmed.get("description") or "")[:MAX_DESCRIPTION]
    return "Product to map:\n" + _compact(trimmed)


def build_messages(system_prompt: str, schemas: dict[str, dict], product: dict) -> list[ChatMessage]:
    return [
        ChatMessage(role="system", content=system_prompt),
        ChatMessage(role="user", blocks=[
            TextBlock(text=catalog_text(schemas)),
            # Everything before this point is identical for every product: Bedrock caches it.
            CachePoint(cache_control=CacheControl(type="default")),
            TextBlock(text=product_text(product)),
        ]),
    ]


class MappingV1(Workflow):
    def __init__(self, llm, system_prompt: str, schemas: dict[str, dict], **kwargs):
        super().__init__(**kwargs)
        self.llm = llm
        self.system_prompt = system_prompt
        self.schemas = schemas

    @step
    async def prepare(self, ev: MappingRequested) -> ContextReady:
        return ContextReady(messages=build_messages(self.system_prompt, self.schemas, ev.product))

    @step
    async def map(self, ev: ContextReady) -> MappingCompleted:
        try:
            response = await self.llm.as_structured_llm(Listing).achat(ev.messages)
        except Exception as exc:  # noqa: BLE001 — any failure becomes a reported error, except credentials
            if is_auth_error(exc):
                raise
            return MappingCompleted(listing=None, error=f"{type(exc).__name__}: {exc}")
        return MappingCompleted(listing=response.raw)
