"""The `map_product` tool: lets the template's chat run V1 on a product of the dataset."""

import json
import logging
import os

from llama_index.core.tools import FunctionTool

from .data import channel_attributes, data_dir, find_product, load_schemas
from .llm import create_llm
from .models import Listing
from .prompts import PROMPT_NAME, get_system_prompt
from .tracing import langfuse_client
from .v1 import MappingV1

logger = logging.getLogger(__name__)


def _describe(sku: str, listing: Listing, schemas: dict[str, dict]) -> str:
    attributes = channel_attributes(schemas, listing.category)
    return json.dumps({
        "sku": sku,
        "category": {"urn": listing.category, "name": schemas.get(listing.category or "", {}).get("name")},
        "attributes": [{"name": attributes.get(a.urn, {}).get("name", a.urn), "value": a.value, "unit": a.unit}
                       for a in listing.attributes],
        "missing": [m.model_dump() for m in listing.missing],
        "rejected": [r.model_dump() for r in listing.rejected],
    }, ensure_ascii=False)


def create_catalog_tools(llm_factory=create_llm, workflow_cls=MappingV1, directories=None,
                         env=None) -> list[FunctionTool]:
    env = os.environ if env is None else env
    if directories is None:
        # Default to the mock dataset only: the deployed chat sends prompts and answers to
        # Langfuse Cloud, and real Alephee/GM products wait for Alephee's confirmation
        # (CLAUDE.md, "Chat desplegado"). The mock dataset already carries the real
        # example product (SKU 94701411, case 01-real-calota-aro14).
        directories = [data_dir("real"), data_dir("mock")] if env.get("CATALOG_ALLOW_REAL_DATA") == "1" \
            else [data_dir("mock")]

    async def map_product(sku: str) -> str:
        """Map a product of the Alephee catalog to a Shopee listing (category and attributes) by its SKU."""
        found = find_product(sku, directories)
        if found is None:
            return f"SKU {sku} is not in the war room dataset."
        product, directory = found
        schemas = load_schemas(directory)
        prompt = get_system_prompt(PROMPT_NAME, langfuse_client())
        try:
            done = await workflow_cls(llm=llm_factory(), system_prompt=prompt.text, schemas=schemas,
                                      timeout=180).run(product=product)
        except Exception as exc:  # noqa: BLE001 — covers only the workflow run above; the
            # template's tool wrapper (`_ejecutar_tool` in agent/workflow.py) is the outer
            # net that catches whatever escapes here.
            logger.error("map_product failed for a SKU: %s", type(exc).__name__)
            return f"Could not map SKU {sku}: {type(exc).__name__}."
        if done.listing is None:
            return f"Could not map SKU {sku}: {done.error}"
        return _describe(str(sku).strip(), done.listing, schemas)

    return [FunctionTool.from_defaults(
        async_fn=map_product, name="map_product",
        description="Map a product of the Alephee catalog to a Shopee listing (category and attributes) by its SKU.",
    )]
