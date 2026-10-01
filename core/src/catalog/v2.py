"""V2 · the reference tables in code, a FunctionAgent for what needs judgment, and control.

check_cache → resolve → run_agent → finalize. The code fixes the category and the fields the
tables answer; the agent decides list values and what the tables do not cover, looks up the
catalog team's corrections and delivers through submit_listing, which validates in code and
sends the problems back. Corrections and the cache live in DynamoDB.

Each step and what it guarantees:
- check_cache: same SKU and category, same tables and prompt version -> same listing (determinism).
- resolve: the category comes from reference_category, never from the model.
- run_agent: the agent only sees the worklist; submit_listing rejects out-of-contract output.
- finalize: code-resolved values win, the guardrails clean what is left, only valid output is cached.
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

# How many submit_listing attempts the agent gets before finalize cleans its last one.
MAX_ITERATIONS = 5
MEMORY_TOKENS = 60_000
MAX_DESCRIPTION = 1500


def _compact(value) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def work_message(ev: WorkReady) -> str:
    """The agent's only input: the fixed category, the product basics and the four worklist buckets.

    The full product attributes are not sent: what the tables already answered is in `resolved`,
    and the rest is in `to_decide` or `unmapped_product`.
    """
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
    """End early without calling the model: with no Shopee category there is nothing to map."""
    # The model is not asked to guess the category: it goes to `missing` for a person to fill.
    return MappingCompleted(listing=Listing(category=None, attributes=[], missing=[MissingAttribute(urn="category", reason=reason)],
                                            rejected=[]), source="tables")


class MappingV2(Workflow):
    """Map one product with tables first, the agent for the rest, guardrails and a per-SKU cache.

    `corrections` and `cache` are the stores from store.py (DynamoDB or in memory); the
    workflow only uses their `find`, `get` and `put` methods.
    """

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
        """(SKU, legacy category id), or None when either is missing and the product is not cacheable.

        The brand provides the catalog read-only, so the same SKU sold by about 40 dealers is
        mapped once. The table and prompt versions are added by the store, see store.py.
        """
        sku = str(product.get("sku") or "").strip()
        categories = product.get("categories") or []
        if not sku or not categories:
            return None
        return (sku, legacy_id(categories[0]["urn"]))

    @step
    async def check_cache(self, ev: MappingRequested) -> MappingCompleted | CacheMissed:
        """Return the cached listing if there is one and it still passes validation."""
        key = self._cache_key(ev.product)
        category = self.reference.category_for(ev.product)
        schema = self.schemas.get(category["urn"]) if category else None
        if key and schema:
            hit = _safe(lambda: self.cache.get(*key, self.reference.version, self.prompt_version), None, "cache get")
            # Re-validated against the current schema: a cached listing that no longer fits the
            # channel (schema changed, bad entry) is ignored and the product is mapped again.
            if hit is not None and not validate(hit, schema, category["urn"]):
                return MappingCompleted(listing=hit, source="cache")
        return CacheMissed(product=ev.product)

    @step
    async def resolve(self, ev: CacheMissed) -> MappingCompleted | WorkReady:
        """Fix the category from the table and split the attributes between code and agent."""
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
        """Let the agent decide the open items, with corrections lookup and a validating submit tool."""
        schema = self.schemas[ev.category_urn]
        # Every submission is recorded, valid or not, so finalize can fall back to the last one.
        submissions: list[Listing] = []

        # Tool for the agent. Its docstring is the tool description the model reads, so the
        # explanation lives here: a correction is a value the catalog team fixed by hand for
        # this category, attribute and product value, and the prompt tells the agent to use it
        # exactly. A DynamoDB failure returns "no correction" instead of breaking the turn.
        def lookup_corrections(attribute_urn: str, product_value: str) -> str:
            """Return the catalog team's correction for this attribute and product value, if there is one."""
            found = _safe(lambda: self.corrections.find(ev.category_urn, attribute_urn, product_value), None,
                          "corrections lookup")
            return _compact({"correction": {"valueId": found.value_id, "value": found.value} if found else None})

        # Tool for the agent; do not edit its docstring (the model reads it). The arguments are
        # validated against `Listing` (fn_schema). Code-resolved values are merged in first, so
        # the agent cannot override the reference table. On problems it raises: LlamaIndex sends
        # the exception text back to the model as the tool result, and the agent retries with
        # that list. `return_direct=True` ends the loop on the first submission that does not
        # raise; a failed one (an error result) does not end it.
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
        # One tool call per turn: corrections are looked up before the submission, never alongside.
        agent = FunctionAgent(name="catalog_v2", description="Maps one Alephee product to a Shopee listing.",
                              system_prompt=self.system_prompt, tools=tools, llm=self.llm, streaming=False,
                              allow_parallel_tool_calls=False)
        error = None
        exhausted = False
        try:
            # `parse_agent_output` raises "Max iterations" before running the tools of the turn
            # that reaches the limit, so the +1 is what lets the fifth submit_listing call actually
            # run instead of being discarded unexecuted. If the agent never submits something
            # valid, a sixth model turn is still requested, paid for and then discarded by that
            # check. The extra turn is inherent to how the library counts iterations, not a bug
            # to "fix" by tuning this number.
            await agent.run(user_msg=work_message(ev), memory=ChatMemoryBuffer.from_defaults(token_limit=MEMORY_TOKENS),
                            max_iterations=MAX_ITERATIONS + 1)
        except WorkflowRuntimeError as exc:
            # The library signals "ran out of iterations" with this generic error; anything else
            # with the same type is a real failure and propagates.
            if "Max iterations" not in str(exc):
                raise
            exhausted = True
        except Exception as exc:  # noqa: BLE001 — reported as an error, except expired credentials
            # The agent workflow may wrap the botocore error, so the cause is checked too.
            if is_auth_error(exc) or is_auth_error(exc.__cause__ or exc):
                raise
            error = f"{type(exc).__name__}: {exc}"
        # Valid means the agent's own last submission passed validation; a text answer or an
        # exhausted loop leaves `valid` False and `finalize` cleans the last submission instead.
        valid = bool(submissions) and not validate(submissions[-1], schema, ev.category_urn)
        return AgentDone(product=ev.product, category_urn=ev.category_urn, worklist=ev.worklist,
                         last=submissions[-1] if submissions else None, valid=valid, error=error,
                         exhausted=exhausted)

    @step
    async def finalize(self, ev: AgentDone) -> MappingCompleted:
        """Merge, clean and, only if the agent's listing was valid, store it in the cache."""
        if ev.last is None:
            return MappingCompleted(listing=None, error=ev.error or "the agent never submitted a listing", source="agent")
        schema = self.schemas[ev.category_urn]
        # Last safety net: whatever the agent left, the output is forced back into contract
        # (category from the table, invalid values dropped, mandatory gaps listed in `missing`).
        final = clean(merge_resolved(ev.last, ev.worklist.resolved), schema, ev.category_urn)
        key = self._cache_key(ev.product)
        # A listing the guardrails had to clean is not cached: the next run gets another chance
        # instead of repeating a degraded answer for every dealer that sells the SKU.
        if ev.valid and key:
            _safe(lambda: self.cache.put(*key, self.reference.version, self.prompt_version, ev.category_urn, final),
                  None, "cache put")
        # Never hide an agent error behind a cleaned listing; an exhausted loop with no other
        # error gets a specific reason instead of silently looking like a clean success.
        error = ev.error
        if error is None and ev.exhausted and not ev.valid:
            error = "max iterations reached; last submission cleaned"
        return MappingCompleted(listing=final, source="agent", error=error)
