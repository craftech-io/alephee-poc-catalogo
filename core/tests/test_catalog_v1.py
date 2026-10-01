import pytest
from llama_index.core.base.llms.types import CachePoint, TextBlock
from llama_index.core.prompts import ChatPromptTemplate
from pydantic import ValidationError

from catalog.data import data_dir, load_cases, load_schemas
from catalog.events import MappingCompleted
from catalog.llm import is_auth_error
from catalog.models import Listing
from catalog.v1 import MAX_DESCRIPTION, MappingV1, build_messages

MOCK = data_dir("mock")
SCHEMAS = load_schemas(MOCK)
CASES = {c["id"]: c for c in load_cases(MOCK)}
PRODUCT = CASES["01-real-calota-aro14"]["product"]
EXPECTED = CASES["01-real-calota-aro14"]["expected"]  # also carries `_origen`, outside the contract
LISTING = Listing.model_validate({k: EXPECTED[k] for k in ("category", "attributes", "missing", "rejected")})


class FakeStructuredLLM:
    def __init__(self, outcome):
        self.outcome = outcome
        self.seen = None

    async def achat(self, messages):
        self.seen = messages
        if isinstance(self.outcome, BaseException):
            raise self.outcome
        return type("Response", (), {"raw": self.outcome})()


class FakeLLM:
    def __init__(self, outcome):
        self.structured = FakeStructuredLLM(outcome)
        self.output_cls = None

    def as_structured_llm(self, output_cls):
        self.output_cls = output_cls
        return self.structured


def test_listing_rejects_extra_fields():
    with pytest.raises(ValidationError):
        Listing.model_validate({"category": None, "attributes": [], "missing": [], "rejected": [], "extra": 1})


def test_build_messages_order_static_first_then_cache_point_then_product():
    messages = build_messages("SYSTEM", SCHEMAS, PRODUCT)
    assert [m.role.value for m in messages] == ["system", "user"]
    assert messages[0].content == "SYSTEM"
    blocks = messages[1].blocks
    assert [type(b) for b in blocks] == [TextBlock, CachePoint, TextBlock]
    assert "urn:category:102529:vendor:shopee" in blocks[0].text
    assert PRODUCT["sku"] in blocks[2].text and PRODUCT["sku"] not in blocks[0].text


def test_catalog_block_is_deterministic():
    first = build_messages("S", SCHEMAS, PRODUCT)[1].blocks[0].text
    again = build_messages("S", dict(reversed(list(SCHEMAS.items()))), PRODUCT)[1].blocks[0].text
    assert first == again


def test_long_description_is_trimmed():
    product = {**PRODUCT, "description": "x" * 19_000}
    text = build_messages("S", SCHEMAS, product)[1].blocks[2].text
    assert "x" * MAX_DESCRIPTION in text and "x" * (MAX_DESCRIPTION + 1) not in text


def test_product_without_category_still_builds():
    product = CASES["09-sin-categoria"]["product"]
    assert build_messages("S", SCHEMAS, product)[1].blocks[2].text


def test_chat_prompt_template_preserves_blocks_and_json_braces():
    """`as_structured_llm(...).achat` runs the messages through ChatPromptTemplate first;
    this must not choke on the catalog's JSON braces nor drop the CachePoint."""
    messages = build_messages("SYSTEM", SCHEMAS, PRODUCT)
    formatted = ChatPromptTemplate(message_templates=messages).format_messages()
    assert [m.role.value for m in formatted] == ["system", "user"]
    assert formatted[0].content == messages[0].content
    assert [type(b) for b in formatted[1].blocks] == [TextBlock, CachePoint, TextBlock]
    assert formatted[1].blocks[0].text == messages[1].blocks[0].text
    assert formatted[1].blocks[2].text == messages[1].blocks[2].text


async def test_map_returns_typed_listing():
    llm = FakeLLM(LISTING)
    done = await MappingV1(llm=llm, system_prompt="S", schemas=SCHEMAS, timeout=10).run(product=PRODUCT)
    assert isinstance(done, MappingCompleted)
    assert done.listing == LISTING and done.error is None
    assert llm.output_cls is Listing
    assert len(llm.structured.seen) == 2


async def test_map_reports_invalid_output_as_error():
    llm = FakeLLM(TypeError("StructuredLLM expected a Listing instance"))
    done = await MappingV1(llm=llm, system_prompt="S", schemas=SCHEMAS, timeout=10).run(product=PRODUCT)
    assert done.listing is None
    assert "TypeError" in done.error


async def test_map_reraises_auth_errors():
    from botocore.exceptions import NoCredentialsError

    llm = FakeLLM(NoCredentialsError())
    with pytest.raises(Exception) as info:
        await MappingV1(llm=llm, system_prompt="S", schemas=SCHEMAS, timeout=10).run(product=PRODUCT)
    assert is_auth_error(info.value) or is_auth_error(info.value.__cause__ or info.value)
