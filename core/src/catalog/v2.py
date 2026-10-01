"""V2 · the reference tables in code, a FunctionAgent for what needs judgment, and control.

check_cache → resolve → run_agent → finalize. The code fixes the category and the fields the
tables answer; the agent decides list values and what the tables do not cover, looks up the
catalog team's corrections and delivers through submit_listing, which validates in code and
sends the problems back. Corrections and the cache live in DynamoDB.
"""

import json
import logging

from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.tools import FunctionTool
from workflows import Workflow, step
from workflows.errors import WorkflowRuntimeError

from .events import AgentDone, CacheMissed, MappingCompleted, MappingRequested, WorkReady
from .guardrails import clean, merge_resolved, validate
from .llm import is_auth_error
from .models import Listing, MissingAttribute
from .reference import Reference, legacy_id
from .worklist import build_worklist

logger = logging.getLogger(__name__)

MAX_ITERATIONS = 5
MEMORY_TOKENS = 60_000
MAX_DESCRIPTION = 1500


def _compact(value) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def work_message(ev: WorkReady) -> str:
    product = {"sku": ev.product.get("sku"), "name": ev.product.get("name"),
               "description": (ev.product.get("description") or "")[:MAX_DESCRIPTION]}
    return "Work list:\n" + _compact({"category": {"urn": ev.category_urn, "name": ev.category_name},
                                      "product": product, **ev.worklist.model_dump()})


def _safe(action, default, what: str):
    """Corrections and cache are a help, not a dependency: a DynamoDB failure never stops a mapping."""
    try:
        return action()
    except Exception as exc:  # noqa: BLE001
        logger.warning("%s failed, continuing without it: %s", what, type(exc).__name__)
        return default


def _no_category(reason: str) -> MappingCompleted:
    return MappingCompleted(listing=Listing(category=None, attributes=[], missing=[MissingAttribute(urn="category", reason=reason)],
                                            rejected=[]), source="tables")


class MappingV2(Workflow):
    def __init__(self, llm, system_prompt: str, prompt_version: str, schemas: dict[str, dict], reference: Reference,
                 corrections, cache, **kwargs):
        super().__init__(**kwargs)
        self.llm = llm
        self.system_prompt = system_prompt
        self.prompt_version = prompt_version
        self.schemas = schemas
        self.reference = reference
        self.corrections = corrections
        self.cache = cache

    def _cache_key(self, product: dict) -> tuple[str, str] | None:
        categories = product.get("categories") or []
        return (str(product.get("sku")), legacy_id(categories[0]["urn"])) if categories else None

    @step
    async def check_cache(self, ev: MappingRequested) -> MappingCompleted | CacheMissed:
        key = self._cache_key(ev.product)
        category = self.reference.category_for(ev.product)
        schema = self.schemas.get(category["urn"]) if category else None
        if key and schema:
            hit = _safe(lambda: self.cache.get(*key, self.reference.version, self.prompt_version), None, "cache get")
            if hit is not None and not validate(hit, schema, category["urn"]):
                return MappingCompleted(listing=hit, source="cache")
        return CacheMissed(product=ev.product)

    @step
    async def resolve(self, ev: CacheMissed) -> MappingCompleted | WorkReady:
        category = self.reference.category_for(ev.product)
        if category is None:
            return _no_category("the product category is not in reference_category")
        schema = self.schemas.get(category["urn"])
        if schema is None:
            return _no_category("the Shopee category has no attribute schema")
        return WorkReady(product=ev.product, category_urn=category["urn"], category_name=category["name"],
                         worklist=build_worklist(ev.product, schema, self.reference))

    @step
    async def run_agent(self, ev: WorkReady) -> AgentDone:
        schema = self.schemas[ev.category_urn]
        submissions: list[Listing] = []

        def lookup_corrections(attribute_urn: str, product_value: str) -> str:
            """Return the catalog team's correction for this attribute and product value, if there is one."""
            found = _safe(lambda: self.corrections.find(ev.category_urn, attribute_urn, product_value), None,
                          "corrections lookup")
            return _compact({"correction": {"valueId": found.value_id, "value": found.value} if found else None})

        def submit_listing(**listing) -> dict:
            """Deliver the listing. It is validated in code; if there are problems you get them back."""
            candidate = merge_resolved(Listing.model_validate(listing), ev.worklist.resolved)
            submissions.append(candidate)
            problems = validate(candidate, schema, ev.category_urn)
            if problems:
                raise ValueError("The listing did not pass validation. Fix these and submit again:\n- " + "\n- ".join(problems))
            return candidate.model_dump()

        tools = [
            FunctionTool.from_defaults(fn=lookup_corrections, name="lookup_corrections"),
            FunctionTool.from_defaults(fn=submit_listing, name="submit_listing", fn_schema=Listing, return_direct=True,
                                       description="Deliver the final listing. It is validated in code."),
        ]
        agent = FunctionAgent(name="catalog_v2", description="Maps one Alephee product to a Shopee listing.",
                              system_prompt=self.system_prompt, tools=tools, llm=self.llm, streaming=False)
        error = None
        try:
            await agent.run(user_msg=work_message(ev), memory=ChatMemoryBuffer.from_defaults(token_limit=MEMORY_TOKENS),
                            max_iterations=MAX_ITERATIONS)
        except WorkflowRuntimeError as exc:
            if "Max iterations" not in str(exc):
                raise
        except Exception as exc:  # noqa: BLE001 — reported as an error, except expired credentials
            if is_auth_error(exc) or is_auth_error(exc.__cause__ or exc):
                raise
            error = f"{type(exc).__name__}: {exc}"
        # Valid means the agent's own last submission passed validation; a text answer or an
        # exhausted loop leaves `valid` False and `finalize` cleans the last submission instead.
        valid = bool(submissions) and not validate(submissions[-1], schema, ev.category_urn)
        return AgentDone(product=ev.product, category_urn=ev.category_urn, worklist=ev.worklist,
                         last=submissions[-1] if submissions else None, valid=valid, error=error)

    @step
    async def finalize(self, ev: AgentDone) -> MappingCompleted:
        if ev.last is None:
            return MappingCompleted(listing=None, error=ev.error or "the agent never submitted a listing", source="agent")
        schema = self.schemas[ev.category_urn]
        final = clean(merge_resolved(ev.last, ev.worklist.resolved), schema, ev.category_urn)
        key = self._cache_key(ev.product)
        if ev.valid and key:
            _safe(lambda: self.cache.put(*key, self.reference.version, self.prompt_version, ev.category_urn, final),
                  None, "cache put")
        return MappingCompleted(listing=final, source="agent")
