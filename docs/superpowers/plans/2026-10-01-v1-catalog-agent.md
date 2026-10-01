# V1 del agente de catálogo · plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir la V1 del agente de catálogo (una llamada estructurada que mapea un producto de Alephee a una publicación de Shopee), medirla en Langfuse contra el proceso actual y servirla desde el chat del template desplegado en sandbox.

**Architecture:** Un `Workflow` de LlamaIndex con dos steps (`prepare` arma los mensajes con el catálogo cacheable y el producto; `map` hace `as_structured_llm(Listing).achat`) que cierra con `MappingCompleted(StopEvent)` tipado. El prompt de sistema vive en Langfuse con fallback a una semilla del repo. La evaluación es un experimento de Langfuse con evaluadores propios. El chat del template suma la herramienta `map_product(sku)`.

**Tech Stack:** Python 3.13 + uv, `llama-index-core` 0.14.24, `llama-index-llms-bedrock-converse` 0.14.18, `llama-index-workflows` 2.23.2, `langfuse` 4.16.x, `openinference-instrumentation-llama-index` 4.4.8, Claude Sonnet 5 en Bedrock (`us.anthropic.claude-sonnet-5`), SST para el deploy.

**Spec:** `docs/superpowers/specs/2026-10-01-v1-catalog-agent-design.md`

## Global Constraints

- Todo el código en inglés: identificadores, archivos, eventos, docstrings y comentarios. Docs y mensajes de commit en español.
- Ningún secreto en código, docs, tests ni commits. Langfuse se lee de `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY` y `LANGFUSE_BASE_URL` (`.env`, ignorado por git, y secretos de SST). Las claves las carga Gastón.
- Modelo: `us.anthropic.claude-sonnet-5`, región `us-east-1`, perfil `sandbox` en local.
- Los datos (`data/real`, `data/mock`) se copian de `old/data` sin cambios.
- `MappingCompleted` no tiene un campo `result` (choca con `StopEvent.result`).
- Los tests no llaman a AWS ni a Langfuse.
- Antes de subir `alephee-shopee-real` a Langfuse Cloud, Gastón confirma con Rick (spec, "Condiciones").
- `BedrockConverse` 0.14.18 ignora el `ttl` del `CachePoint` (`utils.py` solo emite `{"type": "default"}`): la caché dura 5 minutos. El spec decía 1 hora "a verificar"; queda en 5 minutos y se actualiza el spec en la tarea 3.
- El catálogo de la V1 tiene solo las 23 categorías con esquema: todo resultado de categoría de la V1 se rotula como optimista (decisión del 1/10).
- Commit al final de cada tarea, con la línea `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Review Focus

1. Producto sin categoría de origen (`categories: []`, caso `09-sin-categoria`): `prepare` no debe romper y el producto debe llegar al modelo igual. Test en la tarea 3.
2. Descripción de 19.000 caracteres: tiene que llegar recortada a 1.500. Test en la tarea 3.
3. SKU pedido en el chat con espacios o como número (`" 94701411 "`, `94701411`): `find_product` normaliza con `str(sku).strip()`. Test en la tarea 2.
4. Langfuse sin configurar (sin `.env`): el experimento corta con un mensaje claro y el chat usa la semilla del prompt. Tests en las tareas 4 y 6.
5. Sesión SSO vencida: el experimento corta antes de correr ítems, con el comando para renovarla. Test en la tarea 6.

---

### Task 1: Clonado del template y base del proyecto

**Files:**
- Run: `scripts/clonar-para-cliente.sh` (se borra a sí mismo, `CLAUDE.md` y `.claude/`)
- Create: `CLAUDE.md` (del proyecto, a partir de `old/CLAUDE.md`)
- Create: `data/real/*`, `data/mock/*` (copia de `old/data`)

**Interfaces:**
- Produces: `apps/web/` (ex `examples/demo-client`), `apps/api/`, slug `alephee-catalogo` en `client.config.ts`; `data/real/dataset.json`, `data/mock/dataset.json`.

- [ ] **Step 1: Correr el clonado**

```bash
bash scripts/clonar-para-cliente.sh alephee-catalogo
```

Expected: termina imprimiendo "lo que queda para una persona"; `apps/web`, `apps/api` y `documentos/` existen; `CLAUDE.md`, `.claude/` y el script ya no están.

- [ ] **Step 2: Copiar los datos**

```bash
mkdir -p data && cp -R old/data/real old/data/mock data/ && ls data/real data/mock
```

Expected: `data/real` con `dataset.json`, `reference_attribute.json`, `reference_category.json`, `shopee_atributos_por_categoria.json`; `data/mock` con `dataset.json`, `reference_attribute.json`, `reference_category.json`, `shopee_attributes_102529.json`.

- [ ] **Step 3: Rehacer el CLAUDE.md del proyecto**

Copiar `old/CLAUDE.md` a `CLAUDE.md` y editar:
- Encabezado: agregar "**Reinicio del 1/10.** El código anterior está en `old/` (fuera de git) y en la rama `backup/pre-reinicio`. Se reconstruye versión por versión; spec y plan de la V1 en `docs/superpowers/`."
- Reemplazar la sección "Estructura de este directorio" por la estructura nueva (`core/src/catalog/` en inglés, `apps/web`, `data/`, `docs/`).
- Reemplazar "Stack y cómo correr" por: `uv sync`, `uv run pytest core/tests`, `npm test`, `scripts/experiment.sh --version v1 --data mock`.
- Agregar en "Reglas para trabajar en este repo": "Todo el código en inglés (decisión de Gastón, 1/10), aunque el template escriba en español."
- Quitar las secciones de resultados de V1/V2/V3 del 28/09 y el 1/10 (quedan en `old/CLAUDE.md`).

- [ ] **Step 4: Verificar que el template sigue sano**

```bash
uv sync && uv run pytest core/tests -q && npm ci && npm test
```

Expected: todo en verde (los tests del template, sin cambios de código todavía).

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "chore: clon del template para alephee-catalogo y datos del war room

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: Carga de datos

**Files:**
- Create: `core/src/catalog/__init__.py` (vacío)
- Create: `core/src/catalog/data.py`
- Test: `core/tests/test_catalog_data.py`

**Interfaces:**
- Produces:
  - `ROOT: Path` (raíz del repo), `NO_DATA: frozenset[str]` = `{"-1", "N/A", ""}`
  - `data_dir(name: str) -> Path` → `ROOT / "data" / name`
  - `load_cases(directory: Path) -> list[dict]`
  - `load_schemas(directory: Path) -> dict[str, dict]` → urn de categoría del canal → `{"urn", "name", "attributes": [...]}`
  - `channel_attributes(schemas: dict[str, dict], category_urn: str | None) -> dict[str, dict]` → urn de atributo → definición
  - `find_product(sku, directories: list[Path]) -> tuple[dict, Path] | None`

- [ ] **Step 1: Write the failing tests**

```python
# core/tests/test_catalog_data.py
from catalog.data import NO_DATA, channel_attributes, data_dir, find_product, load_cases, load_schemas

REAL = data_dir("real")
MOCK = data_dir("mock")


def test_load_cases_reads_both_datasets():
    assert len(load_cases(REAL)) == 30
    assert len(load_cases(MOCK)) == 10


def test_real_schemas_have_names_from_reference_category():
    schemas = load_schemas(REAL)
    assert "urn:category:102273:vendor:shopee" in schemas
    assert all(s["name"] for s in schemas.values())


def test_mock_schema_is_the_single_calotas_category():
    schemas = load_schemas(MOCK)
    assert list(schemas) == ["urn:category:102529:vendor:shopee"]
    assert schemas["urn:category:102529:vendor:shopee"]["name"] == "Calotas"


def test_channel_attributes_by_urn_and_empty_for_unknown_category():
    schemas = load_schemas(MOCK)
    attrs = channel_attributes(schemas, "urn:category:102529:vendor:shopee")
    assert attrs["urn:attribute:101638:vendor:shopee"]["mandatory"] is True
    assert channel_attributes(schemas, "urn:category:999:vendor:shopee") == {}
    assert channel_attributes(schemas, None) == {}


def test_find_product_normalizes_the_sku_and_searches_in_order():
    sku = load_cases(REAL)[0]["product"]["sku"]
    product, directory = find_product(f"  {sku} ", [REAL, MOCK])
    assert product["sku"] == sku and directory == REAL
    assert find_product(int(sku) if str(sku).isdigit() else sku, [REAL, MOCK]) is not None
    assert find_product("does-not-exist", [REAL, MOCK]) is None


def test_no_data_values():
    assert NO_DATA == frozenset({"-1", "N/A", ""})
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest core/tests/test_catalog_data.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'catalog'`

- [ ] **Step 3: Write the implementation**

```python
# core/src/catalog/data.py
"""Load the war room data: the Alephee dataset and the Shopee channel schemas.

`data/real` holds the 30 products from WarRoom.zip; `data/mock` holds 10 edge cases.
Both folders share file names except for the channel schema: the mock ships a single
category (`shopee_attributes_102529.json`), the real one all categories in the dataset.
"""

import json
from functools import cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NO_DATA = frozenset({"-1", "N/A", ""})


def data_dir(name: str) -> Path:
    return ROOT / "data" / name


@cache
def _read(directory: Path, name: str) -> dict:
    return json.loads((directory / name).read_text(encoding="utf-8"))


def load_cases(directory: Path) -> list[dict]:
    return _read(directory, "dataset.json")["cases"]


def _category_names(directory: Path) -> dict[str, str]:
    return {row["urn"]: row["name"] for row in _read(directory, "reference_category.json")["rows"]}


def load_schemas(directory: Path) -> dict[str, dict]:
    """Channel category urn → {urn, name, attributes}."""
    if (directory / "shopee_atributos_por_categoria.json").exists():
        schemas = _read(directory, "shopee_atributos_por_categoria.json")["categories"]
    else:
        single = _read(directory, "shopee_attributes_102529.json")
        schemas = {single["category"]["urn"]: {**single["category"], "attributes": single["attributes"]}}
    names = _category_names(directory)
    return {urn: {**schema, "name": schema.get("name") or names.get(urn, urn)} for urn, schema in schemas.items()}


def channel_attributes(schemas: dict[str, dict], category_urn: str | None) -> dict[str, dict]:
    """Attribute urn → definition (type, mandatory, valid values). Empty if the category has no schema."""
    return {a["urn"]: a for a in schemas.get(category_urn or "", {}).get("attributes", [])}


def find_product(sku, directories: list[Path]) -> tuple[dict, Path] | None:
    wanted = str(sku).strip()
    for directory in directories:
        for case in load_cases(directory):
            if str(case["product"].get("sku", "")).strip() == wanted:
                return case["product"], directory
    return None
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest core/tests/test_catalog_data.py -v`
Expected: 6 passed

- [ ] **Step 5: Commit**

```bash
git add core/src/catalog core/tests/test_catalog_data.py
git commit -m "feat(catalog): carga del dataset y de los esquemas de Shopee

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: Contrato, eventos y Workflow V1

**Files:**
- Create: `core/src/catalog/models.py`, `core/src/catalog/events.py`, `core/src/catalog/llm.py`, `core/src/catalog/v1.py`
- Modify: `docs/superpowers/specs/2026-10-01-v1-catalog-agent-design.md` (TTL de la caché: 5 minutos, no 1 hora)
- Test: `core/tests/test_catalog_v1.py`

**Interfaces:**
- Consumes: `channel_attributes`, `load_schemas`, `data_dir`, `load_cases` (tarea 2).
- Produces:
  - `Listing`, `MappedAttribute`, `MissingAttribute`, `RejectedAttribute` (Pydantic)
  - `MappingRequested(StartEvent)`: `product: dict`; `ContextReady(Event)`: `messages: list[ChatMessage]`; `MappingCompleted(StopEvent)`: `listing: Listing | None`, `error: str | None = None`
  - `create_llm(env=os.environ) -> BedrockConverse`; `is_auth_error(exc: BaseException) -> bool`
  - `build_messages(system_prompt: str, schemas: dict[str, dict], product: dict) -> list[ChatMessage]`
  - `MappingV1(llm, system_prompt: str, schemas: dict[str, dict], **workflow_kwargs)`; `await MappingV1(...).run(product=...)` devuelve `MappingCompleted`

- [ ] **Step 1: Write the failing tests**

```python
# core/tests/test_catalog_v1.py
import pytest
from llama_index.core.base.llms.types import CachePoint, TextBlock
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest core/tests/test_catalog_v1.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'catalog.events'`

- [ ] **Step 3: Write models.py and events.py**

```python
# core/src/catalog/models.py
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
```

```python
# core/src/catalog/events.py
"""Events of the mapping workflows."""

from llama_index.core.base.llms.types import ChatMessage
from workflows.events import Event, StartEvent, StopEvent

from .models import Listing


class MappingRequested(StartEvent):
    product: dict


class ContextReady(Event):
    messages: list[ChatMessage]


class MappingCompleted(StopEvent):
    """End of a mapping. No field is called `result`: it would collide with StopEvent's."""

    listing: Listing | None
    error: str | None = None
```

- [ ] **Step 4: Write llm.py**

```python
# core/src/catalog/llm.py
"""The only catalog module that knows Bedrock is underneath."""

import os

from botocore.exceptions import NoCredentialsError, SSOError, TokenRetrievalError, UnauthorizedSSOTokenError
from llama_index.llms.bedrock_converse import BedrockConverse

# Converse accepts the `us.` and `global.` profiles; the bare model id has no on-demand throughput.
DEFAULT_MODEL_ID = "us.anthropic.claude-sonnet-5"
_AUTH_ERRORS = (NoCredentialsError, SSOError, TokenRetrievalError, UnauthorizedSSOTokenError)


def create_llm(env=os.environ) -> BedrockConverse:
    return BedrockConverse(
        model=env.get("MODEL_ID", DEFAULT_MODEL_ID),
        region_name=env.get("AWS_REGION", "us-east-1"),
        # Local runs use the SSO profile; inside the Runtime boto3 takes the role.
        profile_name=env.get("AWS_PROFILE") or None,
        max_tokens=16000,
    )


def is_auth_error(exc: BaseException) -> bool:
    """Expired or missing AWS credentials: retrying the next product would fail the same way."""
    return isinstance(exc, _AUTH_ERRORS) or "ExpiredToken" in str(exc)
```

- [ ] **Step 5: Write v1.py**

```python
# core/src/catalog/v1.py
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
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `uv run pytest core/tests/test_catalog_v1.py -v`
Expected: 8 passed

- [ ] **Step 7: Actualizar el spec (TTL)**

En `docs/superpowers/specs/2026-10-01-v1-catalog-agent-design.md`, reemplazar "`CachePoint` con TTL de 1 hora" por "`CachePoint` (TTL de 5 minutos: `BedrockConverse` 0.14.18 no pasa el `ttl` a Converse)" en el diagrama y en el paso 3 de `prepare`, y quitar el `ttl` de la lista "A verificar en la implementación".

- [ ] **Step 8: Commit**

```bash
git add core/src/catalog core/tests/test_catalog_v1.py docs/superpowers/specs/2026-10-01-v1-catalog-agent-design.md
git commit -m "feat(catalog): V1 como Workflow de dos steps con salida Listing tipada

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: Prompt de sistema con Langfuse y semilla

**Files:**
- Modify: `pyproject.toml`, `uv.lock` (dependencia `langfuse`)
- Create: `core/src/catalog/prompts/catalog-v1-system.txt`
- Create: `core/src/catalog/prompts.py`
- Create: `core/src/catalog/tracing.py`
- Create: `.env.example`
- Test: `core/tests/test_catalog_prompts.py`

**Interfaces:**
- Produces:
  - `PROMPT_NAME = "catalog-v1-system"`
  - `SystemPrompt(text: str, name: str, version: int | None)` (dataclass frozen; `version=None` = semilla)
  - `load_seed(name: str) -> str`
  - `get_system_prompt(name: str, client) -> SystemPrompt` (`client` es un `Langfuse` o `None`)
  - `sync_seed(name: str, client) -> bool` (crea el prompt si no existe; `True` si lo creó)
  - `langfuse_client(env=os.environ)` → `Langfuse | None`; `setup_tracing(env=os.environ)` → `Langfuse | None`

- [ ] **Step 1: Agregar la dependencia**

```bash
uv add "langfuse>=4.16.0"
```

Expected: `pyproject.toml` y `uv.lock` actualizados.

- [ ] **Step 2: Write the failing tests**

```python
# core/tests/test_catalog_prompts.py
from types import SimpleNamespace

from catalog.prompts import PROMPT_NAME, get_system_prompt, load_seed, sync_seed
from catalog.tracing import langfuse_client


class FakeLangfuse:
    def __init__(self, exists=True):
        self.exists = exists
        self.created = None

    def get_prompt(self, name, *, label=None, fallback=None, max_retries=None, **kwargs):
        if not self.exists and fallback is None:
            raise RuntimeError("prompt not found")
        if not self.exists:
            return SimpleNamespace(compile=lambda: fallback, version=1, is_fallback=True)
        return SimpleNamespace(compile=lambda: "FROM LANGFUSE", version=7, is_fallback=False)

    def create_prompt(self, **kwargs):
        self.created = kwargs


def test_seed_is_english_and_mentions_the_contract():
    seed = load_seed(PROMPT_NAME)
    assert "missing" in seed and "rejected" in seed and "Never invent" in seed


def test_without_client_uses_the_seed():
    prompt = get_system_prompt(PROMPT_NAME, None)
    assert prompt.text == load_seed(PROMPT_NAME) and prompt.version is None


def test_with_client_uses_langfuse_and_its_version():
    prompt = get_system_prompt(PROMPT_NAME, FakeLangfuse())
    assert prompt.text == "FROM LANGFUSE" and prompt.version == 7


def test_langfuse_fallback_reports_no_version():
    prompt = get_system_prompt(PROMPT_NAME, FakeLangfuse(exists=False))
    assert prompt.text == load_seed(PROMPT_NAME) and prompt.version is None


def test_sync_seed_creates_only_when_missing():
    missing = FakeLangfuse(exists=False)
    assert sync_seed(PROMPT_NAME, missing) is True
    assert missing.created["name"] == PROMPT_NAME and missing.created["labels"] == ["production"]
    present = FakeLangfuse()
    assert sync_seed(PROMPT_NAME, present) is False and present.created is None


def test_no_client_without_keys():
    assert langfuse_client({}) is None
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `uv run pytest core/tests/test_catalog_prompts.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'catalog.prompts'`

- [ ] **Step 4: Write the seed prompt**

```text
# core/src/catalog/prompts/catalog-v1-system.txt
You are a catalog specialist for auto parts marketplaces. You receive a product from the
Alephee catalog (Mercado Libre taxonomy) and the Shopee catalog: every Shopee category with
the attributes it expects and, for list attributes, the valid values. You adapt the product
to Shopee: choose the Shopee category and map the product attributes to that category's
attributes.

Rules:
- Copy the category URN and every attribute URN exactly from the Shopee catalog. Never invent a URN.
- If the channel attribute has a list of values, choose the equivalent value from that list and use
  its id and its name exactly as listed. If no value is equivalent, do not fill it.
- If the channel attribute is free text, use valueId "0" and the product value as it is.
- Never translate values: Shopee values stay in Portuguese, exactly as the catalog lists them.
- Never invent values. Use only data present in the product attributes.
- The values "-1", "N/A" or empty mean there is no data.
- If a mandatory channel attribute cannot be filled, add it to "missing" with the reason.
- If a product attribute cannot be used, add it to "rejected" with its legacyId and the reason.
- Each channel attribute appears at most once.
- If you cannot choose a category, return category null and add {"urn": "category"} to "missing".
```

(La primera línea con `#` no va en el archivo: es solo la ruta.)

- [ ] **Step 5: Write tracing.py and prompts.py**

```python
# core/src/catalog/tracing.py
"""Langfuse client and LlamaIndex instrumentation, shared by the experiment and the chat tool."""

import os

_instrumented = False


def langfuse_client(env=os.environ):
    """The Langfuse client, or None when the keys are not configured (tests, offline runs)."""
    if not (env.get("LANGFUSE_PUBLIC_KEY") and env.get("LANGFUSE_SECRET_KEY")):
        return None
    from langfuse import get_client

    return get_client()


def setup_tracing(env=os.environ):
    """Connect OpenInference spans to Langfuse once per process. Returns the client or None."""
    global _instrumented
    client = langfuse_client(env)
    if client is not None and not _instrumented:
        from openinference.instrumentation.llama_index import LlamaIndexInstrumentor

        LlamaIndexInstrumentor().instrument()
        _instrumented = True
    return client
```

```python
# core/src/catalog/prompts.py
"""System prompts: Langfuse is the source; the seed in prompts/ is the first version and the fallback."""

from dataclasses import dataclass
from pathlib import Path

PROMPT_NAME = "catalog-v1-system"
LABEL = "production"
_SEEDS = Path(__file__).resolve().parent / "prompts"


@dataclass(frozen=True)
class SystemPrompt:
    text: str
    name: str
    version: int | None  # None: the seed (Langfuse not configured or unreachable)


def load_seed(name: str) -> str:
    return (_SEEDS / f"{name}.txt").read_text(encoding="utf-8").strip()


def get_system_prompt(name: str, client) -> SystemPrompt:
    seed = load_seed(name)
    if client is None:
        return SystemPrompt(seed, name, None)
    prompt = client.get_prompt(name, label=LABEL, fallback=seed)
    return SystemPrompt(prompt.compile(), name, None if prompt.is_fallback else prompt.version)


def sync_seed(name: str, client) -> bool:
    """Create the prompt in Langfuse from the seed if it does not exist yet."""
    try:
        client.get_prompt(name, label=LABEL, max_retries=0)
        return False
    except Exception:  # noqa: BLE001 — the SDK raises a generic API error for "not found"
        client.create_prompt(name=name, prompt=load_seed(name), labels=[LABEL], type="text",
                             commit_message="seed from the repo")
        return True
```

- [ ] **Step 6: Write .env.example**

```bash
# .env.example — copiar a .env (ignorado por git) y completar. Nunca commitear valores.
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
LANGFUSE_BASE_URL=https://us.cloud.langfuse.com
```

- [ ] **Step 7: Run tests to verify they pass**

Run: `uv run pytest core/tests/test_catalog_prompts.py -v`
Expected: 6 passed

- [ ] **Step 8: Commit**

```bash
git add pyproject.toml uv.lock core/src/catalog core/tests/test_catalog_prompts.py .env.example
git commit -m "feat(catalog): prompt de sistema en Langfuse con semilla y fallback

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5: Evaluadores

**Files:**
- Create: `core/src/catalog/evaluation.py`
- Test: `core/tests/test_catalog_evaluation.py`

**Interfaces:**
- Consumes: `NO_DATA`, `channel_attributes`, `load_schemas`, `load_cases`, `data_dir` (tarea 2).
- Produces:
  - `CaseResult` (dataclass): `category_ok`, `tp`, `fp`, `fn`, `invalid: list[str]`, `duplicates: list[str]`, `missing_not_detected: list[str]`, `extra_missing: list[str]`, property `exact`
  - `evaluate_case(predicted: dict, expected: dict, attributes: dict[str, dict]) -> CaseResult`
  - `summarize(results: list[CaseResult]) -> dict`
  - `make_item_evaluator(schemas)` → `evaluator(*, input, output, expected_output, metadata=None, **kwargs) -> list[Evaluation]`
  - `make_run_evaluator(schemas)` → `run_evaluator(*, item_results, **kwargs) -> list[Evaluation]`

- [ ] **Step 1: Write the failing tests**

```python
# core/tests/test_catalog_evaluation.py
import copy
from types import SimpleNamespace

from catalog.data import channel_attributes, data_dir, load_cases, load_schemas
from catalog.evaluation import evaluate_case, make_item_evaluator, make_run_evaluator, summarize

MOCK = data_dir("mock")
SCHEMAS = load_schemas(MOCK)
ATTRS = channel_attributes(SCHEMAS, "urn:category:102529:vendor:shopee")
CASES = {c["id"]: c for c in load_cases(MOCK)}


def test_prediction_equal_to_expected_is_exact():
    for case in CASES.values():
        assert evaluate_case(case["expected"], case["expected"], ATTRS).exact, case["id"]


def test_value_out_of_domain_is_invalid():
    expected = CASES["01-real-calota-aro14"]["expected"]
    pred = copy.deepcopy(expected)
    pred["attributes"][0] = {"urn": "urn:attribute:101638:vendor:shopee", "valueId": "99999", "value": "Nuevo"}
    result = evaluate_case(pred, expected, ATTRS)
    assert not result.exact
    assert result.invalid == ["urn:attribute:101638:vendor:shopee"]
    assert result.fp == 1 and result.fn == 1


def test_urn_unknown_to_the_channel_is_invalid():
    expected = CASES["02-calota-aro13-preta-completa"]["expected"]
    pred = copy.deepcopy(expected)
    pred["attributes"].append({"urn": "urn:attribute:1673", "valueId": "0", "value": "Novo"})
    result = evaluate_case(pred, expected, ATTRS)
    assert result.invalid == ["urn:attribute:1673"] and result.fp == 1


def test_duplicate_attribute_is_detected():
    expected = CASES["01-real-calota-aro14"]["expected"]
    pred = copy.deepcopy(expected)
    pred["attributes"].append(copy.deepcopy(pred["attributes"][4]))
    result = evaluate_case(pred, expected, ATTRS)
    assert result.duplicates == ["urn:attribute:101730:vendor:shopee"] and not result.exact


def test_free_text_compares_the_value():
    expected = CASES["02-calota-aro13-preta-completa"]["expected"]
    pred = copy.deepcopy(expected)
    pred["attributes"][1]["value"] = "OTHER-SKU"
    result = evaluate_case(pred, expected, ATTRS)
    assert result.fp == 1 and result.fn == 1 and result.invalid == []


def test_undetected_missing_is_an_error():
    expected = CASES["06-falta-obligatorio"]["expected"]
    pred = copy.deepcopy(expected)
    pred["missing"] = []
    result = evaluate_case(pred, expected, ATTRS)
    assert result.missing_not_detected == ["urn:attribute:101638:vendor:shopee"] and not result.exact


def test_wrong_category():
    expected = CASES["08-categoria-sin-referencia"]["expected"]
    pred = copy.deepcopy(expected)
    pred["category"] = "urn:category:123:vendor:shopee"
    result = evaluate_case(pred, expected, ATTRS)
    assert not result.category_ok and not result.exact


def test_no_data_value_is_invalid():
    expected = CASES["02-calota-aro13-preta-completa"]["expected"]
    pred = copy.deepcopy(expected)
    pred["attributes"][1]["value"] = "-1"
    assert evaluate_case(pred, expected, ATTRS).invalid == ["urn:attribute:102293:vendor:shopee"]


def test_summary_precision_and_recall():
    expected = CASES["01-real-calota-aro14"]["expected"]
    perfect = evaluate_case(expected, expected, ATTRS)
    empty = evaluate_case({"category": None, "attributes": [], "missing": []}, expected, ATTRS)
    summary = summarize([perfect, empty])
    assert summary["cases"] == 2 and summary["exact"] == 1
    assert summary["precision"] == 1.0 and summary["recall"] == 0.5


def test_item_evaluator_scores_and_task_errors():
    evaluator = make_item_evaluator(SCHEMAS)
    expected = CASES["01-real-calota-aro14"]["expected"]
    scores = {e.name: e.value for e in evaluator(input={}, output=expected, expected_output=expected)}
    assert scores["exact"] is True and scores["invalid_values"] == 0 and scores["precision"] == 1.0
    failed = evaluator(input={}, output={"error": "TypeError: boom"}, expected_output=expected)
    assert {e.name: e.value for e in failed}["exact"] is False
    assert "boom" in next(e for e in failed if e.name == "exact").comment


def test_run_evaluator_aggregates():
    run_evaluator = make_run_evaluator(SCHEMAS)
    expected = CASES["01-real-calota-aro14"]["expected"]
    items = [SimpleNamespace(item=SimpleNamespace(expected_output=expected), output=expected),
             SimpleNamespace(item=SimpleNamespace(expected_output=expected), output={"error": "x"})]
    scores = {e.name: e.value for e in run_evaluator(item_results=items)}
    assert scores["exact_count"] == 1 and scores["recall"] == 0.5
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest core/tests/test_catalog_evaluation.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'catalog.evaluation'`

- [ ] **Step 3: Write the implementation**

```python
# core/src/catalog/evaluation.py
"""Compare a listing against the expected one, and expose it as Langfuse evaluators.

Deterministic: it never calls a model. A case is exact when the category is right, no
attribute is extra or missing, no value is out of the channel domain, nothing is
duplicated and the reported missing attributes match the expected ones.
"""

from collections import Counter
from dataclasses import dataclass, field

from langfuse import Evaluation

from .data import NO_DATA, channel_attributes

EMPTY = {"category": None, "attributes": [], "missing": [], "rejected": []}


@dataclass
class CaseResult:
    category_ok: bool
    tp: int
    fp: int
    fn: int
    invalid: list[str] = field(default_factory=list)
    duplicates: list[str] = field(default_factory=list)
    missing_not_detected: list[str] = field(default_factory=list)
    extra_missing: list[str] = field(default_factory=list)

    @property
    def exact(self) -> bool:
        return (self.category_ok and self.fp == 0 and self.fn == 0 and not self.invalid
                and not self.duplicates and not self.missing_not_detected and not self.extra_missing)


def _key(attr: dict, attributes: dict[str, dict]) -> tuple:
    """Identity of a mapped attribute: by valueId when the channel has a domain, by text otherwise."""
    definition = attributes.get(attr["urn"])
    if definition and definition.get("values"):
        return (attr["urn"], str(attr.get("valueId")))
    return (attr["urn"], str(attr.get("value", "")).strip(), attr.get("unit") or None)


def _is_invalid(attr: dict, attributes: dict[str, dict]) -> bool:
    definition = attributes.get(attr["urn"])
    if definition is None or str(attr.get("value", "")).strip() in NO_DATA:
        return True
    domain = {v["id"] for v in definition.get("values", [])}
    return bool(domain) and str(attr.get("valueId")) not in domain


def evaluate_case(predicted: dict, expected: dict, attributes: dict[str, dict]) -> CaseResult:
    pred_attrs = predicted.get("attributes") or []
    pred_keys = Counter(_key(a, attributes) for a in pred_attrs)
    exp_keys = Counter(_key(a, attributes) for a in expected["attributes"])
    tp = sum((pred_keys & exp_keys).values())
    urn_count = Counter(a["urn"] for a in pred_attrs)
    pred_missing = {m["urn"] for m in predicted.get("missing") or []}
    exp_missing = {m["urn"] for m in expected["missing"]}
    return CaseResult(
        category_ok=predicted.get("category") == expected["category"],
        tp=tp,
        fp=sum(pred_keys.values()) - tp,
        fn=sum(exp_keys.values()) - tp,
        invalid=[a["urn"] for a in pred_attrs if _is_invalid(a, attributes)],
        duplicates=sorted(urn for urn, n in urn_count.items() if n > 1),
        missing_not_detected=sorted(exp_missing - pred_missing),
        extra_missing=sorted(pred_missing - exp_missing),
    )


def _ratio(num: int, den: int) -> float:
    return round(num / den, 3) if den else 0.0


def summarize(results: list[CaseResult]) -> dict:
    tp, fp, fn = (sum(getattr(r, k) for r in results) for k in ("tp", "fp", "fn"))
    return {
        "cases": len(results),
        "exact": sum(r.exact for r in results),
        "category_ok": sum(r.category_ok for r in results),
        "precision": _ratio(tp, tp + fp),
        "recall": _ratio(tp, tp + fn),
        "invalid_values": sum(len(r.invalid) for r in results),
        "duplicates": sum(len(r.duplicates) for r in results),
        "missing_not_detected": sum(len(r.missing_not_detected) for r in results),
    }


def _evaluate_output(output, expected: dict, schemas: dict[str, dict]) -> tuple[CaseResult, str | None]:
    error = output.get("error") if isinstance(output, dict) else "the task returned no output"
    predicted = EMPTY if error else output
    return evaluate_case(predicted, expected, channel_attributes(schemas, expected["category"])), error


def make_item_evaluator(schemas: dict[str, dict]):
    def evaluator(*, input, output, expected_output, metadata=None, **kwargs) -> list[Evaluation]:
        result, error = _evaluate_output(output, expected_output, schemas)
        return [
            Evaluation(name="exact", value=result.exact, data_type="BOOLEAN", comment=error),
            Evaluation(name="category_ok", value=result.category_ok, data_type="BOOLEAN"),
            Evaluation(name="invalid_values", value=len(result.invalid), comment=", ".join(result.invalid) or None),
            Evaluation(name="duplicates", value=len(result.duplicates), comment=", ".join(result.duplicates) or None),
            Evaluation(name="missing_ok", value=not (result.missing_not_detected or result.extra_missing),
                       data_type="BOOLEAN"),
            Evaluation(name="precision", value=_ratio(result.tp, result.tp + result.fp)),
            Evaluation(name="recall", value=_ratio(result.tp, result.tp + result.fn)),
        ]

    return evaluator


def make_run_evaluator(schemas: dict[str, dict]):
    def run_evaluator(*, item_results, **kwargs) -> list[Evaluation]:
        results = [_evaluate_output(r.output, r.item.expected_output, schemas)[0] for r in item_results]
        summary = summarize(results)
        return [
            Evaluation(name="exact_count", value=summary["exact"]),
            Evaluation(name="category_ok_count", value=summary["category_ok"]),
            Evaluation(name="invalid_values_total", value=summary["invalid_values"]),
            Evaluation(name="duplicates_total", value=summary["duplicates"]),
            Evaluation(name="precision", value=summary["precision"]),
            Evaluation(name="recall", value=summary["recall"]),
        ]

    return run_evaluator
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest core/tests/test_catalog_evaluation.py -v`
Expected: 11 passed

- [ ] **Step 5: Commit**

```bash
git add core/src/catalog/evaluation.py core/tests/test_catalog_evaluation.py
git commit -m "feat(catalog): métrica del war room como evaluadores de Langfuse

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 6: Experimento en Langfuse

**Files:**
- Create: `core/src/catalog/experiment.py`
- Create: `scripts/experiment.sh`, `scripts/sync_prompts.sh`
- Test: `core/tests/test_catalog_experiment.py`

**Interfaces:**
- Consumes: `load_cases`, `load_schemas`, `data_dir` (2); `MappingV1`, `create_llm` (3); `PROMPT_NAME`, `get_system_prompt`, `sync_seed`, `setup_tracing` (4); `make_item_evaluator`, `make_run_evaluator` (5).
- Produces:
  - `DATASETS = {"real": "alephee-shopee-real", "mock": "alephee-shopee-mock"}`
  - `dataset_items(cases: list[dict], origin: str) -> list[dict]` (claves `id`, `input`, `expected_output`, `metadata`)
  - `upload_dataset(client, origin: str, cases: list[dict]) -> None`
  - `current_task(*, item, **kwargs) -> dict`
  - `make_v1_task(llm, system_prompt: str, schemas, workflow_cls=MappingV1)` → `async task(*, item, **kwargs) -> dict`
  - `check_aws(session_factory=boto3.Session) -> None` (sale con `SystemExit` si no hay credenciales)
  - `main(argv: list[str] | None = None) -> None`

- [ ] **Step 1: Write the failing tests**

```python
# core/tests/test_catalog_experiment.py
from types import SimpleNamespace

import pytest

from catalog.data import data_dir, load_cases, load_schemas
from catalog.events import MappingCompleted
from catalog.experiment import check_aws, current_task, dataset_items, main, make_v1_task, upload_dataset
from catalog.models import Listing

REAL = load_cases(data_dir("real"))
MOCK = load_cases(data_dir("mock"))


def test_dataset_items_carry_expected_and_metadata():
    items = dataset_items(REAL, "real")
    assert len(items) == 30
    first = items[0]
    assert first["id"] == f"alephee-shopee-real-{REAL[0]['id']}"
    assert first["input"] == REAL[0]["product"]
    assert first["expected_output"]["category"] == REAL[0]["expected"]["category"]
    assert first["metadata"]["origin"] == "real" and first["metadata"]["expected_is_mock"] is True
    assert first["metadata"]["actual"] == REAL[0]["actual"]
    assert dataset_items(MOCK, "mock")[6]["metadata"]["decision_pending"]


def _missing(name):
    raise RuntimeError("not found")


def test_upload_dataset_creates_once_and_upserts_items_by_id():
    calls = []
    client = SimpleNamespace(get_dataset=_missing,
                             create_dataset=lambda **kw: calls.append(("dataset", kw["name"])),
                             create_dataset_item=lambda **kw: calls.append(("item", kw["id"])))
    upload_dataset(client, "mock", MOCK)
    assert calls[0] == ("dataset", "alephee-shopee-mock")
    assert len({c[1] for c in calls if c[0] == "item"}) == 10

    calls.clear()
    client.get_dataset = lambda name: object()
    upload_dataset(client, "mock", MOCK)
    assert not [c for c in calls if c[0] == "dataset"]


def test_current_task_returns_todays_listing_without_a_model():
    item = SimpleNamespace(metadata={"actual": REAL[0]["actual"]})
    out = current_task(item=item)
    assert out["category"] == REAL[0]["actual"]["category"]
    assert out["missing"] == [] and set(out["attributes"][0]) == {"urn", "valueId", "value", "unit"}


async def test_v1_task_returns_the_listing_or_the_error():
    listing = Listing(category="urn:x", attributes=[], missing=[], rejected=[])

    class FakeWorkflow:
        outcome = MappingCompleted(listing=listing)

        def __init__(self, **kwargs):
            pass

        async def run(self, product):
            return self.outcome

    task = make_v1_task(llm=None, system_prompt="S", schemas={}, workflow_cls=FakeWorkflow)
    assert (await task(item=SimpleNamespace(input={}))) == listing.model_dump()
    FakeWorkflow.outcome = MappingCompleted(listing=None, error="TypeError: boom")
    assert (await task(item=SimpleNamespace(input={}))) == {"error": "TypeError: boom"}


def test_check_aws_exits_with_the_login_command():
    class Broken:
        def client(self, name):
            raise RuntimeError("Token has expired")

    with pytest.raises(SystemExit) as info:
        check_aws(session_factory=lambda **kw: Broken())
    assert "aws sso login --profile" in str(info.value)


def test_main_exits_without_langfuse(monkeypatch):
    monkeypatch.delenv("LANGFUSE_PUBLIC_KEY", raising=False)
    monkeypatch.delenv("LANGFUSE_SECRET_KEY", raising=False)
    with pytest.raises(SystemExit) as info:
        main(["--version", "current", "--data", "mock"])
    assert "LANGFUSE" in str(info.value)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest core/tests/test_catalog_experiment.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'catalog.experiment'`

- [ ] **Step 3: Write experiment.py**

```python
# core/src/catalog/experiment.py
"""Run a version of the catalog agent as a Langfuse experiment.

    scripts/experiment.sh --version v1 --data mock
    scripts/experiment.sh --version current --data real      # today's process, no model
    scripts/experiment.sh --version v1 --data real --case error-88904447
"""

import argparse
import os
import subprocess

import boto3

from .data import data_dir, load_cases, load_schemas
from .evaluation import make_item_evaluator, make_run_evaluator
from .llm import create_llm
from .prompts import PROMPT_NAME, get_system_prompt, sync_seed
from .tracing import setup_tracing
from .v1 import MappingV1

DATASETS = {"real": "alephee-shopee-real", "mock": "alephee-shopee-mock"}
MAX_CONCURRENCY = 4


def dataset_items(cases: list[dict], origin: str) -> list[dict]:
    name = DATASETS[origin]
    return [{
        "id": f"{name}-{case['id']}",
        "input": case["product"],
        "expected_output": {k: case["expected"][k] for k in ("category", "attributes", "missing", "rejected")},
        "metadata": {"case": case["id"], "origin": origin, "expected_is_mock": True,
                     "decision_pending": case.get("decision_pendiente"), "actual": case.get("actual")},
    } for case in cases]


def upload_dataset(client, origin: str, cases: list[dict]) -> None:
    """Create the dataset if needed and upsert its items by id: re-uploading never duplicates."""
    try:
        client.get_dataset(DATASETS[origin])
    except Exception:  # noqa: BLE001 — the SDK raises a generic API error for "not found"
        client.create_dataset(name=DATASETS[origin],
                              description=f"War room Alephee × Shopee ({origin}); expected outputs are MOCK")
    for item in dataset_items(cases, origin):
        client.create_dataset_item(dataset_name=DATASETS[origin], **item)


def current_task(*, item, **kwargs) -> dict:
    """Today's Alephee listing in the agent contract. It never reports missing attributes."""
    actual = (item.metadata or {}).get("actual")
    if not actual:
        return {"error": "the case has no current listing (mock dataset)"}
    return {"category": actual["category"], "missing": [], "rejected": [],
            "attributes": [{k: a.get(k) for k in ("urn", "valueId", "value", "unit")} for a in actual["attributes"]]}


def make_v1_task(llm, system_prompt: str, schemas: dict[str, dict], workflow_cls=MappingV1):
    async def task(*, item, **kwargs) -> dict:
        done = await workflow_cls(llm=llm, system_prompt=system_prompt, schemas=schemas, timeout=180).run(
            product=item.input)
        return done.listing.model_dump() if done.listing is not None else {"error": done.error}

    return task


def check_aws(session_factory=boto3.Session) -> None:
    profile = os.environ.get("AWS_PROFILE", "sandbox")
    try:
        session_factory(profile_name=profile).client("sts").get_caller_identity()
    except Exception as exc:  # noqa: BLE001
        raise SystemExit(f"AWS credentials expired or missing ({exc}). Run: aws sso login --profile {profile}") from exc


def _commit() -> str:
    return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version", choices=["v1", "current"], default="v1")
    parser.add_argument("--data", choices=list(DATASETS), default="mock")
    parser.add_argument("--case", help="run a single case by id")
    args = parser.parse_args(argv)

    client = setup_tracing()
    if client is None:
        raise SystemExit("Langfuse is not configured: set LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY and "
                         "LANGFUSE_BASE_URL in .env (see .env.example)")
    directory = data_dir(args.data)
    cases = load_cases(directory)
    schemas = load_schemas(directory)
    upload_dataset(client, args.data, cases)

    metadata = {"version": args.version, "commit": _commit()}
    if args.version == "v1":
        check_aws()
        sync_seed(PROMPT_NAME, client)
        prompt = get_system_prompt(PROMPT_NAME, client)
        llm = create_llm()
        task = make_v1_task(llm, prompt.text, schemas)
        metadata |= {"model": llm.model, "prompt": f"{prompt.name}:v{prompt.version}"}
    else:
        task = current_task

    dataset = client.get_dataset(DATASETS[args.data])
    items = [i for i in dataset.items if not args.case or i.metadata.get("case") == args.case]
    if not items:
        raise SystemExit(f"No case {args.case} in {DATASETS[args.data]}")
    result = client.run_experiment(
        name=f"{args.version}-{args.data}", data=items, task=task,
        evaluators=[make_item_evaluator(schemas)], run_evaluators=[make_run_evaluator(schemas)],
        max_concurrency=MAX_CONCURRENCY, metadata=metadata)
    print(result.format())
    client.flush()


if __name__ == "__main__":
    main()
```

Nota: `client.run_experiment(data=items)` con `DatasetItem` de Langfuse crea el dataset run igual que `dataset.run_experiment`, y permite filtrar por `--case`. Si al correr la tarea 7 la interfaz no muestra el run asociado al dataset, cambiar a `dataset.run_experiment(...)` sin `data` y filtrar el caso en la tarea.

- [ ] **Step 4: Write the scripts**

```bash
#!/usr/bin/env bash
# scripts/experiment.sh — corre una versión del agente como experimento de Langfuse.
set -euo pipefail
cd "$(dirname "$0")/.."
export AWS_PROFILE="${AWS_PROFILE:-sandbox}" AWS_REGION="${AWS_REGION:-us-east-1}"
PYTHONPATH=core/src exec uv run --env-file .env python -m catalog.experiment "$@"
```

```bash
#!/usr/bin/env bash
# scripts/sync_prompts.sh — sube a Langfuse la semilla del prompt si todavía no existe.
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHONPATH=core/src exec uv run --env-file .env python -c \
  "from catalog.prompts import PROMPT_NAME, sync_seed; from catalog.tracing import langfuse_client; print('creado' if sync_seed(PROMPT_NAME, langfuse_client()) else 'ya existía')"
```

```bash
chmod +x scripts/experiment.sh scripts/sync_prompts.sh
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `uv run pytest core/tests/test_catalog_experiment.py -v`
Expected: 6 passed

- [ ] **Step 6: Run the whole Python suite**

Run: `uv run pytest core/tests -q`
Expected: todo en verde

- [ ] **Step 7: Commit**

```bash
git add core/src/catalog/experiment.py core/tests/test_catalog_experiment.py scripts/experiment.sh scripts/sync_prompts.sh
git commit -m "feat(catalog): experimento de Langfuse con línea de base del proceso actual

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 7: Corridas reales (humo, mock y real)

**Files:**
- Modify: `CLAUDE.md` (resultados de la V1 del día)

Requiere: `.env` completo (Gastón), sesión SSO activa, y para el paso 4, la confirmación de Rick.

- [ ] **Step 1: Verificar Langfuse y AWS**

```bash
aws sts get-caller-identity --profile sandbox
PYTHONPATH=core/src uv run --env-file .env python -c "from catalog.tracing import langfuse_client; print(langfuse_client().auth_check())"
```

Expected: la identidad de la cuenta `033545611835` y `True`.

- [ ] **Step 2: Humo con un caso mock**

```bash
scripts/sync_prompts.sh
scripts/experiment.sh --version v1 --data mock --case 01-real-calota-aro14
```

Expected: el resumen de `result.format()` con un ítem y sus scores. En Langfuse: el prompt `catalog-v1-system` con label `production`, el dataset `alephee-shopee-mock`, y una traza con la llamada a Bedrock, sus tokens (incluidos `cacheRead`/`cacheWrite`) y la latencia. Si la traza no trae tokens, revisar que `setup_tracing()` se llame antes de crear el LLM.

- [ ] **Step 3: Mock completo y línea de base**

```bash
scripts/experiment.sh --version v1 --data mock
```

Expected: 10 ítems evaluados. Anotar exactos, inválidos y duplicados.

- [ ] **Step 4: Real (después de la confirmación de Rick)**

```bash
scripts/experiment.sh --version current --data real
scripts/experiment.sh --version v1 --data real
```

Expected: la línea de base `current` da 7 exactos, 28 categorías y 47 inválidos (los mismos números del evaluador anterior sobre los mismos datos). Si no coinciden, hay un error en el port de la métrica: parar y revisar la tarea 5. Luego la V1 sobre los 30.

- [ ] **Step 5: Registrar y commitear**

Agregar a `CLAUDE.md` una tabla con los resultados de `current` y `v1` (exactos, categorías, inválidos, duplicados, precisión, recall, tokens y segundos por producto desde Langfuse), aclarando que el `expected` es mock y que la categoría de la V1 es optimista: elige entre 23 categorías que incluyen siempre la correcta.

```bash
git add CLAUDE.md
git commit -m "docs: resultados de la V1 en Langfuse contra el proceso actual

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 8: Herramienta `map_product` en el chat

**Files:**
- Create: `core/src/catalog/chat_tool.py`
- Modify: `core/server.py` (`build_app`: parámetro `catalog_tools_factory` y uso en `armar_tools`)
- Modify: `core/Dockerfile` (copiar `data/`)
- Modify: `client.config.ts` (regla en `promptSistema`)
- Modify: `apps/web/mock.mjs`, `apps/web/mock.test.mjs` (escenario "sku")
- Test: `core/tests/test_catalog_chat_tool.py`, `core/tests/test_server.py`

**Interfaces:**
- Consumes: `find_product`, `load_schemas`, `data_dir` (2); `MappingV1`, `create_llm` (3); `PROMPT_NAME`, `get_system_prompt`, `langfuse_client` (4).
- Produces: `create_catalog_tools(llm_factory=create_llm, workflow_cls=MappingV1, directories=None) -> list[FunctionTool]` con una herramienta `map_product(sku: str) -> str`; `build_app(..., catalog_tools_factory=None)`.

- [ ] **Step 1: Write the failing tests**

```python
# core/tests/test_catalog_chat_tool.py
import json

from catalog.chat_tool import create_catalog_tools
from catalog.data import data_dir, load_cases
from catalog.events import MappingCompleted
from catalog.models import Listing

CASE = load_cases(data_dir("mock"))[0]


def _tool(outcome):
    class FakeWorkflow:
        def __init__(self, **kwargs):
            pass

        async def run(self, product):
            return outcome

    (tool,) = create_catalog_tools(llm_factory=lambda: None, workflow_cls=FakeWorkflow,
                                   directories=[data_dir("mock")])
    return tool


async def test_unknown_sku_is_explained():
    tool = _tool(None)
    assert "not in the war room dataset" in str(await tool.acall(sku="nope"))


async def test_mapping_error_is_explained():
    tool = _tool(MappingCompleted(listing=None, error="TypeError: boom"))
    assert "boom" in str(await tool.acall(sku=CASE["product"]["sku"]))


async def test_listing_is_returned_with_names():
    expected = CASE["expected"]
    listing = Listing.model_validate({k: expected[k] for k in ("category", "attributes", "missing", "rejected")})
    out = json.loads(str(await _tool(MappingCompleted(listing=listing)).acall(sku=CASE["product"]["sku"])))
    assert out["category"]["name"] == "Calotas"
    assert out["attributes"][0]["name"] and out["attributes"][0]["value"]
```

Agregar a `core/tests/test_server.py`:

```python
def test_catalog_tool_is_registered_only_when_enabled():
    from llama_index.core.tools import FunctionTool

    seen = {}

    class ToolsLLM:
        async def aresponder_con_tools(self, message, history, tools):
            seen["tools"] = [t.metadata.name for t in tools]
            return RespuestaLLM(texto="listo", llamadas=[])

    fake_tool = FunctionTool.from_defaults(fn=lambda sku: sku, name="map_product")
    app = build_app(llm_factory=lambda cfg: ToolsLLM(), env={"MODEL_ID": "fake", "CATALOG_ENABLED": "1"},
                    catalog_tools_factory=lambda: [fake_tool])
    TestClient(app).post("/invocations", json={"message": "mapea el SKU 1", "sessionId": "s", "userId": "u"})
    assert seen["tools"] == ["map_product"]
```

(`RespuestaLLM` y `TestClient` ya están importados en `test_server.py`; si no, importarlos de `agent.workflow` y `starlette.testclient`.)

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest core/tests/test_catalog_chat_tool.py core/tests/test_server.py -v`
Expected: FAIL (`ModuleNotFoundError: No module named 'catalog.chat_tool'` y `unexpected keyword argument 'catalog_tools_factory'`)

- [ ] **Step 3: Write chat_tool.py**

```python
# core/src/catalog/chat_tool.py
"""The `map_product` tool: lets the template's chat run V1 on a product of the dataset."""

import json
import logging

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


def create_catalog_tools(llm_factory=create_llm, workflow_cls=MappingV1, directories=None) -> list[FunctionTool]:
    directories = directories or [data_dir("real"), data_dir("mock")]

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
        except Exception as exc:  # noqa: BLE001 — the chat never gets an exception
            logger.error("map_product failed for a SKU: %s", type(exc).__name__)
            return f"Could not map SKU {sku}: {type(exc).__name__}."
        if done.listing is None:
            return f"Could not map SKU {sku}: {done.error}"
        return _describe(str(sku).strip(), done.listing, schemas)

    return [FunctionTool.from_defaults(
        async_fn=map_product, name="map_product",
        description="Map a product of the Alephee catalog to a Shopee listing (category and attributes) by its SKU.",
    )]
```

- [ ] **Step 4: Wire it in core/server.py**

En la firma de `build_app` (`core/server.py:138`), agregar el parámetro:

```python
def build_app(
    llm_factory=None,
    env=None,
    tools_usuario_factory=None,
    tools_gateway_factory=None,
    estimador_de_costo=None,
    instrumentador_factory=None,
    catalog_tools_factory=None,
) -> Starlette:
```

Después de `cache_gateway: list | None = None`, agregar:

```python
    # Catalog agent (war room): fixed tools, built once per process, only when the Runtime enables them.
    catalog_tools: list = []
    if env.get("CATALOG_ENABLED") == "1":
        if catalog_tools_factory is None:
            from catalog.chat_tool import create_catalog_tools

            catalog_tools_factory = create_catalog_tools
        catalog_tools = catalog_tools_factory()
```

Y en `armar_tools`, reemplazar `tools: list = []` por:

```python
        tools: list = [*catalog_tools]
```

- [ ] **Step 5: Dockerfile, prompt del chat y Runtime**

En `core/Dockerfile`, después de `COPY core/ ./core/`:

```dockerfile
# War room data: the catalog tool looks the product up by SKU in data/real and data/mock.
COPY data/ ./data/
```

En `client.config.ts`, agregar al final del array `promptSistema` (antes de `].join("\n")`):

```ts
    "8. When the user asks to map a product by SKU, call the `map_product` tool and present the category, the attributes and the missing ones as a table. Do not change what the tool returns.",
```

En `infra/sst/runtime.ts`, dentro de `environmentVariables` (línea ~407), agregar:

```ts
    // War room: enables the map_product tool (core/src/catalog/chat_tool.py).
    CATALOG_ENABLED: "1",
```

- [ ] **Step 6: Escenario mock del chat**

En `apps/web/mock.mjs`, junto a las demás constantes de texto:

```js
// Modo local del agente de catálogo: NO corre la V1. Es una publicación de ejemplo
// (MOCK) con la forma que devuelve map_product, para ensayar la UI sin Bedrock.
const TEXTO_MAP_PRODUCT =
  "Resultado de ejemplo del modo mock (no corre el agente): SKU 94701411 → categoría " +
  "Calotas. Condição do Item: Novo · Aro: 14 · Material: Plástico ABS. Faltantes: ninguno.";
```

Y en `planificarRespuesta`, antes del bloque de `"pedido"`:

```js
  if (minusculas.includes("sku")) {
    return {
      demoraMs,
      frames: [{ type: "done", text: TEXTO_MAP_PRODUCT }],
    };
  }
```

En `apps/web/mock.test.mjs`, dentro del `describe("planificarRespuesta", ...)`:

```js
  it("'sku' responde con la publicación de ejemplo de map_product, rotulada como mock", () => {
    const plan = planificarRespuesta("mapea el SKU 94701411", "A");
    expect(plan.frames).toHaveLength(1);
    expect(plan.frames[0].type).toBe("done");
    expect(plan.frames[0].text).toContain("modo mock");
  });
```

- [ ] **Step 7: Run all tests**

Run: `uv run pytest core/tests -q && npm test && npm run typecheck`
Expected: todo en verde.

- [ ] **Step 8: Commit**

```bash
git add core/src/catalog/chat_tool.py core/server.py core/Dockerfile client.config.ts infra/sst/runtime.ts apps/web/mock.mjs apps/web/mock.test.mjs core/tests/test_catalog_chat_tool.py core/tests/test_server.py
git commit -m "feat(chat): herramienta map_product que corre la V1 desde el chat

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 9: Deploy en sandbox con trazas en Langfuse

**Files:**
- Modify: `client.config.ts` (`observabilidad`)
- Modify: `CLAUDE.md` (cómo probar el chat desplegado)

Requiere: Docker con buildx, sesión SSO activa, y que Gastón cargue los secretos.

- [ ] **Step 1: Observabilidad hacia Langfuse**

En `client.config.ts`, en el objeto `observabilidad` del cliente:

```ts
    muestreo: 1,
    contenidoEnTrazas: true,
    destino: "otlp",
```

Run: `npm run typecheck`
Expected: verde.

- [ ] **Step 2: Secretos (los corre Gastón, con `!`)**

```bash
AUTH=$(printf '%s:%s' "$LANGFUSE_PUBLIC_KEY" "$LANGFUSE_SECRET_KEY" | base64)
npx sst secret set ClientHmacSecret "<secreto HMAC>" --stage warroom
npx sst secret set ObservabilidadOtlpEndpoint "https://us.cloud.langfuse.com/api/public/otel/v1/traces" --stage warroom
npx sst secret set ObservabilidadOtlpHeaders "Authorization=Basic%20${AUTH},x-langfuse-ingestion-version=4" --stage warroom
```

(El `%20` no es opcional: ver `docs/langfuse.md`. `base64` en macOS no parte líneas; en Linux usar `base64 -w0`.)

- [ ] **Step 3: Deploy**

```bash
AWS_PROFILE=sandbox npx sst deploy --stage warroom
```

Expected: termina con los outputs (`runtimeArn`, `repoCore`, la Function URL del BFF). Si falla el build de la imagen, verificar `docker buildx ls` con soporte `linux/arm64`.

- [ ] **Step 4: Probar el chat desplegado**

```bash
API_URL="<Function URL del BFF>" CHAT_HMAC_SECRET="<el mismo secreto>" npm start -w apps/web
```

En `http://localhost:3000`, escribir: "Mapea el SKU <un SKU de data/real>". Expected: una tabla con categoría, atributos y faltantes. En Langfuse, una traza del Runtime con el turno del chat, la llamada a `map_product` y, adentro, la llamada estructurada de la V1.

- [ ] **Step 5: Registrar y commitear**

Agregar a `CLAUDE.md` la sección "Chat desplegado (stage warroom)" con el comando del paso 4 (sin secretos) y cómo destruir el stage (`npx sst remove --stage warroom`).

```bash
git add client.config.ts CLAUDE.md
git commit -m "feat(infra): stage warroom en sandbox con trazas del Runtime en Langfuse

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

## Cobertura del spec

| Requisito del spec | Tarea |
|---|---|
| Paso 0, clonado con `alephee-catalogo` | 1 |
| Datos de `old/` sin cambios | 1, 2 |
| `Listing` tipado y `MappingCompleted(StopEvent)` | 3 |
| Steps `prepare` y `map`, orden de mensajes y `CachePoint` | 3 |
| `as_structured_llm(Listing).achat` | 3 |
| Prompt en Langfuse con semilla y fallback | 4 |
| Evaluadores por ítem y por corrida | 5 |
| Datasets, experimento y línea de base `current` | 6, 7 |
| Errores: SSO vencida, Langfuse caído, salida inválida | 3, 4, 6 |
| `map_product` en el chat, Dockerfile, prompt del chat, mock | 8 |
| Deploy stage `warroom`, trazas a Langfuse | 9 |
| Criterio de terminado (tests, experimento, chat, traza) | 6, 7, 9 |
