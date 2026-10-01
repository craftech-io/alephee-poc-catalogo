"""The `map_product_v1` and `map_product_v2` tools: let the template's chat run the catalog
agent on a product of the dataset.

The chat's own agent (core/src/agent) calls these tools by SKU; each call runs the same V1 or
V2 workflow that the batch experiment runs, and returns a compact JSON the chat can turn into
a table. The tool descriptions the chat model reads are the `description=` strings at the end.
"""

import json
import logging
import os

from llama_index.core.tools import FunctionTool

from .data import channel_attributes, data_dir, find_product, load_schemas
from .llm import create_llm
from .models import Listing
from .prompts import PROMPT_NAME, PROMPT_NAME_V2, get_system_prompt
from .reference import load_reference
from .store import stores_from_env
from .tracing import langfuse_client
from .v1 import MappingV1
from .v2 import MappingV2

logger = logging.getLogger(__name__)


def _describe(sku: str, listing: Listing, schemas: dict[str, dict], source: str, warning: str | None = None) -> str:
    """Listing as JSON for the chat, with attribute names instead of bare urns so it reads as a table."""
    attributes = channel_attributes(schemas, listing.category)
    out = {
        "sku": sku,
        "category": {"urn": listing.category, "name": schemas.get(listing.category or "", {}).get("name")},
        "attributes": [{"name": attributes.get(a.urn, {}).get("name", a.urn), "value": a.value, "unit": a.unit}
                       for a in listing.attributes],
        "missing": [m.model_dump() for m in listing.missing],
        "rejected": [r.model_dump() for r in listing.rejected],
        "source": source,
    }
    if warning:
        # The V2 agent can deliver a listing *and* an error (an exception after a
        # submission, or iterations exhausted): surface it as a warning instead of
        # hiding it behind a clean-looking listing.
        out["warning"] = warning
    return json.dumps(out, ensure_ascii=False)


def create_catalog_tools(llm_factory=create_llm, workflow_cls=MappingV1, workflow_v2_cls=MappingV2, directories=None,
                         env=None, stores_factory=stores_from_env) -> list[FunctionTool]:
    """Build the two chat tools. Every argument is injectable so tests run without AWS or Langfuse."""
    env = os.environ if env is None else env
    if directories is None:
        # Default to the mock dataset only: the deployed chat sends prompts and answers to
        # Langfuse Cloud, and real Alephee/GM products wait for Alephee's confirmation
        # (CLAUDE.md, "Chat desplegado"). The mock dataset already carries the real
        # example product (SKU 94701411, case 01-real-calota-aro14).
        directories = [data_dir("real"), data_dir("mock")] if env.get("CATALOG_ALLOW_REAL_DATA") == "1" \
            else [data_dir("mock")]

    stores: list = []

    def _stores():
        # Built lazily on first use (so creating the tools stays cheap, and tests with
        # fakes never need a real store) and cached across calls: `stores_factory(env)`
        # used to run again on every `map_product_v2` call.
        if not stores:
            stores.append(stores_factory(env))
        return stores[0]

    # Shared body of both tools; `build` creates the V1 or V2 workflow for the dataset folder where
    # the SKU was found, so schemas and reference tables always come from that same dataset.
    # Every failure becomes a short text answer: the chat should explain it, not crash.
    async def _map(sku: str, build) -> str:
        found = find_product(sku, directories)
        if found is None:
            return f"SKU {sku} is not in the war room dataset."
        product, directory = found
        schemas = load_schemas(directory)
        try:
            done = await build(product, directory, schemas).run(product=product)
        except Exception as exc:  # noqa: BLE001 — covers only the workflow run; the template's tool
            # wrapper (`_ejecutar_tool` in agent/workflow.py) is the outer net.
            logger.error("map_product failed for a SKU: %s", type(exc).__name__)
            return f"Could not map SKU {sku}: {type(exc).__name__}."
        if done.listing is None:
            return f"Could not map SKU {sku}: {done.error}"
        return _describe(str(sku).strip(), done.listing, schemas, done.source, done.error)

    # Tool body; its docstring is part of the tool and is left as is. The prompt is fetched on
    # every call, so a prompt edited in Langfuse applies to the next message; the deployed
    # Runtime has no Langfuse keys and always uses the repo seed.
    async def map_product_v1(sku: str) -> str:
        """Map a product of the Alephee catalog to a Shopee listing with V1 (a single structured call)."""
        prompt = get_system_prompt(PROMPT_NAME, langfuse_client())
        return await _map(sku, lambda product, directory, schemas: workflow_cls(
            llm=llm_factory(), system_prompt=prompt.text, schemas=schemas, timeout=180))

    # Tool body; its docstring is part of the tool and is left as is. Same flow as V1 plus the
    # reference tables of the SKU's dataset and the shared corrections and cache stores.
    async def map_product_v2(sku: str) -> str:
        """Map a product of the Alephee catalog to a Shopee listing with V2 (reference tables, validation,
        corrections and cache)."""
        prompt = get_system_prompt(PROMPT_NAME_V2, langfuse_client())
        corrections, cache, _ = _stores()
        return await _map(sku, lambda product, directory, schemas: workflow_v2_cls(
            llm=llm_factory(), system_prompt=prompt.text, prompt_version=str(prompt.version or "seed"),
            schemas=schemas, reference=load_reference(directory), corrections=corrections, cache=cache,
            timeout=300))

    return [
        FunctionTool.from_defaults(async_fn=map_product_v1, name="map_product_v1",
                                   description="Map an Alephee product to a Shopee listing by SKU with V1."),
        FunctionTool.from_defaults(async_fn=map_product_v2, name="map_product_v2",
                                   description="Map an Alephee product to a Shopee listing by SKU with V2 (default)."),
    ]
