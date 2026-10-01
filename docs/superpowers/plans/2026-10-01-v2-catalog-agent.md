# V2 del agente de catálogo · plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir la V2 del agente de catálogo (tablas de referencia en código, `FunctionAgent` con entrega validada y correcciones, caché por SKU en DynamoDB), medirla en Langfuse, servirla desde el chat desplegado, probarla de punta a punta y dejar el deck fiel a lo construido.

**Architecture:** Un `Workflow` de LlamaIndex con cuatro steps (`check_cache`, `resolve`, `run_agent`, `finalize`). El código resuelve la categoría y los campos que mapean las tablas; el `FunctionAgent` decide solo los valores que necesitan interpretación, consulta correcciones y entrega con `submit_listing`, que valida en código y le devuelve los problemas. Correcciones y caché viven en dos tablas DynamoDB del stage `warroom`.

**Tech Stack:** Python 3.13 + uv, `llama-index-core` 0.14.24 (`FunctionAgent`), `llama-index-llms-bedrock-converse` 0.14.18, `llama-index-workflows` 2.23.2, `langfuse` 4.15.6, boto3 (DynamoDB), SST 4.17.1, Claude Sonnet 5 en Bedrock.

**Spec:** `docs/superpowers/specs/2026-10-01-v2-catalog-agent-design.md` (y la V1: `docs/superpowers/specs/2026-10-01-v1-catalog-agent-design.md`)

## Global Constraints

- Todo el código en inglés: identificadores, archivos, eventos, docstrings, comentarios y títulos de tests. Docs, `CLAUDE.md`, el deck y los mensajes de commit en español neutro (sin voseo).
- Ningún secreto en código, docs, tests, salidas de comandos ni commits. Nunca leer ni imprimir `.env`; los scripts lo cargan con `uv run --env-file .env`.
- La V1 no cambia de comportamiento. `MappingCompleted` suma `source: str = "model"` como campo opcional.
- `langfuse>=4.15.6,<4.16` (4.16 choca con el `opentelemetry-sdk` que fija `aws-opentelemetry-distro`).
- Modelo `us.anthropic.claude-sonnet-5`, región `us-east-1`, perfil `sandbox`; cuenta sandbox de Craftech `033545611835`; stage `warroom`.
- Datos reales: `--data real` exige `--allow-real-upload` (OK de Gastón del 1/10); el chat usa solo el dataset mock salvo `CATALOG_ALLOW_REAL_DATA=1`. Los tests e2e usan solo el dataset mock.
- `FunctionAgent` en 0.14.24: una herramienta que lanza excepción devuelve el texto del error al modelo; `return_direct=True` solo corta con una salida sin error; al llegar a `max_iterations` lanza `WorkflowRuntimeError("Max iterations ...")` (verificado el 1/10 con un doble).
- El doble del LLM para `FunctionAgent` es una subclase de `FunctionCallingLLM` (el campo `llm` del agente es Pydantic).
- Los tests normales no llaman a AWS ni a Langfuse. Los e2e se marcan `@pytest.mark.e2e` y solo corren con `RUN_E2E=1`.
- Langfuse Cloud de esta organización no tiene la API vieja de trazas: leer observaciones con `GET /api/public/v2/observations?fromStartTime=&toStartTime=&fields=core,basic,usage,model`.
- El prompt del chat (`client.config.ts`, `promptSistema`) tiene que medir menos de 2.048 caracteres en base64 (límite de variables de entorno de AgentCore; hoy mide 1.048).
- Commit al final de cada tarea con la línea `Co-Authored-By` que indiquen las instrucciones de sistema del implementador.

## Review Focus

1. Valor del producto con otra capitalización o espacios (`" novo "` contra `Novo` de la lista): la coincidencia exacta normaliza con `strip().casefold()`. Test en la tarea 1.
2. Dos atributos del producto que la tabla manda al mismo atributo de Shopee: queda uno solo, sin duplicado. Test en la tarea 1.
3. El agente entrega un valor distinto para un atributo que el código ya resolvió: gana lo resuelto. Test en la tarea 4.
4. DynamoDB no responde: el mapeo sigue sin caché y sin correcciones. Test en la tarea 4.
5. Corrección cargada con otra capitalización del valor del producto: se encuentra igual. Test en la tarea 3.

---

### Task 1: Tablas de referencia y lista de trabajo

**Files:**
- Create: `core/src/catalog/reference.py`, `core/src/catalog/worklist.py`
- Test: `core/tests/test_catalog_reference.py`, `core/tests/test_catalog_worklist.py`

**Interfaces:**
- Consumes: `data_dir`, `load_cases`, `load_schemas`, `NO_DATA` (`catalog.data`); `MappedAttribute` (`catalog.models`).
- Produces:
  - `legacy_id(urn_or_id: str) -> str`
  - `Reference` (frozen dataclass): `categories: dict[str, dict]`, `attributes: dict[str, list[dict]]`, `version: str`; métodos `category_for(product: dict) -> dict | None` (`{"urn", "name"}`) y `target_for(attribute_urn: str, schema: dict) -> str | None`
  - `load_reference(directory: Path) -> Reference` (cacheado)
  - `normalize(value) -> str`
  - `Worklist` (Pydantic): `resolved: list[MappedAttribute]`, `to_decide: list[dict]`, `unmapped_product: list[dict]`, `uncovered_channel: list[dict]`
  - `build_worklist(product: dict, schema: dict, reference: Reference) -> Worklist`

- [ ] **Step 1: Write the failing tests**

```python
# core/tests/test_catalog_reference.py
from catalog.data import data_dir, load_cases, load_schemas
from catalog.reference import legacy_id, load_reference

MOCK = data_dir("mock")
REAL = data_dir("real")
CALOTAS = "urn:category:102529:vendor:shopee"


def test_legacy_id_strips_urn_prefixes():
    assert legacy_id("urn:category:734701") == "734701"
    assert legacy_id("urn:attribute:1673") == "1673"
    assert legacy_id("1106872") == "1106872"


def test_category_for_uses_the_table_and_handles_missing_categories():
    reference = load_reference(MOCK)
    cases = {c["id"]: c for c in load_cases(MOCK)}
    assert reference.category_for(cases["01-real-calota-aro14"]["product"]) == {"urn": CALOTAS, "name": "Calotas"}
    assert reference.category_for(cases["09-sin-categoria"]["product"]) is None
    assert reference.category_for({"categories": [{"urn": "urn:category:999999999"}]}) is None


def test_target_for_filters_by_category_schema():
    reference = load_reference(MOCK)
    schema = load_schemas(MOCK)[CALOTAS]
    assert reference.target_for("urn:attribute:1673", schema) == "urn:attribute:101638:vendor:shopee"
    assert reference.target_for("urn:attribute:1726", schema) is None  # Material is not in the mock table


def test_target_for_disambiguates_ids_with_several_destinations():
    reference = load_reference(REAL)
    schemas = load_schemas(REAL)
    found = None
    for legacy, rows in reference.attributes.items():
        if len(rows) < 2:
            continue
        for schema in schemas.values():
            urns = {a["urn"] for a in schema["attributes"]}
            hits = [r["urn"] for r in rows if r["urn"] in urns]
            if len(hits) == 1:
                found = (legacy, schema, hits[0])
                break
        if found:
            break
    assert found, "the real table should have an id with several destinations"
    legacy, schema, expected = found
    assert reference.target_for(f"urn:attribute:{legacy}", schema) == expected


def test_version_is_stable_and_short():
    assert load_reference(MOCK).version == load_reference(MOCK).version
    assert len(load_reference(MOCK).version) == 12
    assert load_reference(MOCK).version != load_reference(REAL).version
```

```python
# core/tests/test_catalog_worklist.py
from catalog.data import data_dir, load_cases, load_schemas
from catalog.reference import load_reference
from catalog.worklist import build_worklist, normalize

MOCK = data_dir("mock")
CALOTAS = "urn:category:102529:vendor:shopee"
SCHEMA = load_schemas(MOCK)[CALOTAS]
REFERENCE = load_reference(MOCK)
CASES = {c["id"]: c for c in load_cases(MOCK)}
CONDITION = "urn:attribute:101638:vendor:shopee"


def _product(*attributes):
    return {"sku": "T-1", "categories": [{"urn": "urn:category:734701"}], "attributes": list(attributes)}


def test_normalize():
    assert normalize("  NoVo ") == "novo"


def test_exact_list_match_is_resolved_ignoring_case_and_spaces():
    work = build_worklist(_product({"urn": "urn:attribute:1673", "name": "Condición", "unit": "-1", "value": " novo "}),
                          SCHEMA, REFERENCE)
    resolved = {a.urn: a for a in work.resolved}
    assert resolved[CONDITION].value == "Novo" and resolved[CONDITION].valueId == "14703"
    assert not work.to_decide


def test_value_without_exact_match_goes_to_the_agent():
    work = build_worklist(_product({"urn": "urn:attribute:1673", "name": "Condición", "unit": "-1", "value": "1"}),
                          SCHEMA, REFERENCE)
    assert [d["target_urn"] for d in work.to_decide] == [CONDITION]
    assert work.to_decide[0]["values"] and work.to_decide[0]["product_value"] == "1"


def test_no_data_values_are_skipped():
    work = build_worklist(_product({"urn": "urn:attribute:1673", "name": "Condición", "unit": "-1", "value": "-1"}),
                          SCHEMA, REFERENCE)
    assert not work.resolved and not work.to_decide
    assert CONDITION in {a["urn"] for a in work.uncovered_channel}


def test_two_product_attributes_with_the_same_target_keep_only_one():
    work = build_worklist(_product({"urn": "urn:attribute:1673", "name": "Condición", "unit": "-1", "value": "Novo"},
                                   {"urn": "urn:attribute:1673", "name": "Condición", "unit": "-1", "value": "Usado"}),
                          SCHEMA, REFERENCE)
    assert [a.urn for a in work.resolved] + [d["target_urn"] for d in work.to_decide] == [CONDITION]


def test_attributes_without_destination_and_uncovered_channel_attributes():
    work = build_worklist(CASES["01-real-calota-aro14"]["product"], SCHEMA, REFERENCE)
    covered = {a.urn for a in work.resolved} | {d["target_urn"] for d in work.to_decide}
    assert CONDITION in covered
    assert all(a["urn"] not in covered for a in work.uncovered_channel)
    assert {a["urn"] for a in work.uncovered_channel} | covered == {a["urn"] for a in SCHEMA["attributes"]}
    assert all(p["value"] not in ("-1", "N/A", "") for p in work.unmapped_product)


def test_free_text_without_unit_is_copied_and_with_unit_goes_to_the_agent():
    free = next(a for a in SCHEMA["attributes"] if not a.get("values"))
    legacy = next(lid for lid, rows in REFERENCE.attributes.items() if any(r["urn"] == free["urn"] for r in rows))
    copied = build_worklist(_product({"urn": f"urn:attribute:{legacy}", "name": "x", "unit": "-1", "value": "ABC-1"}),
                            SCHEMA, REFERENCE)
    assert [(a.urn, a.valueId, a.value) for a in copied.resolved] == [(free["urn"], "0", "ABC-1")]
    with_unit = build_worklist(_product({"urn": f"urn:attribute:{legacy}", "name": "x", "unit": "[[[Gramos]]]", "value": "390"}),
                               SCHEMA, REFERENCE)
    assert not with_unit.resolved and with_unit.to_decide[0]["product_unit"] == "[[[Gramos]]]"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest core/tests/test_catalog_reference.py core/tests/test_catalog_worklist.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'catalog.reference'`

- [ ] **Step 3: Write reference.py**

```python
# core/src/catalog/reference.py
"""Reference tables kept by Alephee's catalog team: legacy (Mercado Libre) ids to Shopee ids.

`reference_category` maps one legacy category to one Shopee category. `reference_attribute`
maps fields, not values, and one legacy id can point to several Shopee attributes: the
right one is the one that belongs to the product's Shopee category.
"""

import hashlib
import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path


def legacy_id(urn_or_id: str) -> str:
    """'urn:category:734701' → '734701'; 'urn:attribute:1673' → '1673'; bare ids stay as they are."""
    return str(urn_or_id).removeprefix("urn:category:").removeprefix("urn:attribute:").split(":", 1)[0]


@dataclass(frozen=True)
class Reference:
    categories: dict[str, dict]
    attributes: dict[str, list[dict]]
    version: str

    def category_for(self, product: dict) -> dict | None:
        categories = product.get("categories") or []
        if not categories:
            return None
        return self.categories.get(legacy_id(categories[0]["urn"]))

    def target_for(self, attribute_urn: str, schema: dict) -> str | None:
        in_category = {a["urn"] for a in schema["attributes"]}
        return next((row["urn"] for row in self.attributes.get(legacy_id(attribute_urn), [])
                     if row["urn"] in in_category), None)


@cache
def load_reference(directory: Path) -> Reference:
    category_bytes = (directory / "reference_category.json").read_bytes()
    attribute_bytes = (directory / "reference_attribute.json").read_bytes()
    categories = {legacy_id(row["legacyId"]): {"urn": row["urn"], "name": row["name"]}
                  for row in json.loads(category_bytes)["rows"]}
    attributes: dict[str, list[dict]] = {}
    for row in json.loads(attribute_bytes)["rows"]:
        attributes.setdefault(legacy_id(row["legacyId"]), []).append({"urn": row["urn"], "name": row["name"]})
    version = hashlib.sha256(category_bytes + attribute_bytes).hexdigest()[:12]
    return Reference(categories=categories, attributes=attributes, version=version)
```

- [ ] **Step 4: Write worklist.py**

```python
# core/src/catalog/worklist.py
"""What the code resolves before the agent runs, and what is left for the agent to decide."""

from pydantic import BaseModel

from .data import NO_DATA
from .models import MappedAttribute
from .reference import Reference

CHANNEL_FIELDS = ("urn", "name", "type", "mandatory", "maxValues")


def normalize(value) -> str:
    return str(value).strip().casefold()


def _values(definition: dict) -> list[dict]:
    return [{"id": str(v["id"]), "name": v["name"]} for v in definition.get("values") or []]


def _channel(definition: dict) -> dict:
    return {**{k: definition.get(k) for k in CHANNEL_FIELDS}, "values": _values(definition)}


class Worklist(BaseModel):
    resolved: list[MappedAttribute]
    to_decide: list[dict]
    unmapped_product: list[dict]
    uncovered_channel: list[dict]


def build_worklist(product: dict, schema: dict, reference: Reference) -> Worklist:
    """Resolve by code what the reference table and an exact value match already answer."""
    definitions = {a["urn"]: a for a in schema["attributes"]}
    resolved: list[MappedAttribute] = []
    to_decide: list[dict] = []
    unmapped: list[dict] = []
    covered: set[str] = set()
    for attribute in product.get("attributes") or []:
        value = str(attribute.get("value", "")).strip()
        if value in NO_DATA:
            continue
        target = reference.target_for(attribute["urn"], schema)
        if target is None:
            unmapped.append({"legacy_id": attribute["urn"], "name": attribute.get("name"), "value": value,
                             "unit": attribute.get("unit")})
            continue
        if target in covered:
            continue
        covered.add(target)
        definition = definitions[target]
        values = _values(definition)
        unit = str(attribute.get("unit") or "").strip()
        if not values and unit in NO_DATA:
            resolved.append(MappedAttribute(urn=target, valueId="0", value=value, unit=None))
            continue
        match = next((v for v in values if normalize(v["name"]) == normalize(value)), None)
        if match is not None:
            resolved.append(MappedAttribute(urn=target, valueId=match["id"], value=match["name"], unit=None))
            continue
        to_decide.append({"legacy_id": attribute["urn"], "product_name": attribute.get("name"),
                          "product_value": value, "product_unit": attribute.get("unit"),
                          "target_urn": target, **{k: v for k, v in _channel(definition).items() if k != "urn"}})
    uncovered = [_channel(d) for urn, d in definitions.items() if urn not in covered]
    return Worklist(resolved=resolved, to_decide=to_decide, unmapped_product=unmapped, uncovered_channel=uncovered)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `uv run pytest core/tests/test_catalog_reference.py core/tests/test_catalog_worklist.py -v`
Expected: all passed. Si `test_free_text_without_unit_is_copied...` no encuentra un atributo de texto libre en la tabla mock, reportar NEEDS_CONTEXT con el detalle (no cambiar la intención del test).

- [ ] **Step 6: Commit**

```bash
git add core/src/catalog/reference.py core/src/catalog/worklist.py core/tests/test_catalog_reference.py core/tests/test_catalog_worklist.py
git commit -m "feat(catalog): tablas de referencia y lista de trabajo de la V2"
```

---

### Task 2: Validación y red final

**Files:**
- Create: `core/src/catalog/guardrails.py`
- Test: `core/tests/test_catalog_guardrails.py`

**Interfaces:**
- Consumes: `NO_DATA` (`catalog.data`); `Listing`, `MappedAttribute`, `MissingAttribute`, `RejectedAttribute` (`catalog.models`).
- Produces:
  - `validate(listing: Listing, schema: dict, category_urn: str) -> list[str]`
  - `clean(listing: Listing, schema: dict, category_urn: str) -> Listing`
  - `merge_resolved(listing: Listing, resolved: list[MappedAttribute]) -> Listing`

- [ ] **Step 1: Write the failing tests**

```python
# core/tests/test_catalog_guardrails.py
from catalog.data import data_dir, load_cases, load_schemas
from catalog.guardrails import clean, merge_resolved, validate
from catalog.models import Listing, MappedAttribute, MissingAttribute

MOCK = data_dir("mock")
CALOTAS = "urn:category:102529:vendor:shopee"
SCHEMA = load_schemas(MOCK)[CALOTAS]
CONDITION = "urn:attribute:101638:vendor:shopee"
EXPECTED = {c["id"]: c["expected"] for c in load_cases(MOCK)}


def _listing(*attributes, missing=(), category=CALOTAS):
    return Listing(category=category, attributes=list(attributes), missing=list(missing), rejected=[])


def _all_mandatory_missing():
    return [MissingAttribute(urn=a["urn"], reason="x") for a in SCHEMA["attributes"] if a.get("mandatory")]


def test_expected_listing_of_case_01_is_valid():
    listing = Listing.model_validate({k: EXPECTED["01-real-calota-aro14"][k] for k in ("category", "attributes", "missing", "rejected")})
    assert validate(listing, SCHEMA, CALOTAS) == []


def test_validate_reports_each_problem():
    other = next(a["urn"] for a in SCHEMA["attributes"] if a["urn"] != CONDITION)
    problems = validate(_listing(
        MappedAttribute(urn="urn:attribute:1:vendor:shopee", valueId="0", value="x"),
        MappedAttribute(urn=CONDITION, valueId="99999", value="Nuevo"),
        MappedAttribute(urn=CONDITION, valueId="14703", value="Usado"),
        missing=[m for m in _all_mandatory_missing() if m.urn != other],
        category="urn:category:1:vendor:shopee"), SCHEMA, CALOTAS)
    text = "\n".join(problems)
    assert "category must be" in text
    assert "is not an attribute of" in text
    assert "is not in the channel list" in text
    assert "does not match id" in text
    assert "appears 2 times" in text
    if next(a for a in SCHEMA["attributes"] if a["urn"] == other).get("mandatory"):
        assert "is mandatory" in text


def test_no_data_value_is_a_problem():
    free = next(a["urn"] for a in SCHEMA["attributes"] if not a.get("values"))
    problems = validate(_listing(MappedAttribute(urn=free, valueId="0", value="-1"), missing=_all_mandatory_missing()),
                        SCHEMA, CALOTAS)
    assert any("means no data" in p for p in problems)


def test_clean_never_lets_invalid_or_duplicates_out_and_fixes_the_category():
    dirty = _listing(MappedAttribute(urn=CONDITION, valueId="14703", value="Novo"),
                     MappedAttribute(urn=CONDITION, valueId="14703", value="Novo"),
                     MappedAttribute(urn="urn:attribute:1:vendor:shopee", valueId="0", value="x"),
                     category="urn:category:1:vendor:shopee")
    result = clean(dirty, SCHEMA, CALOTAS)
    assert result.category == CALOTAS
    assert [a.urn for a in result.attributes] == [CONDITION]
    assert validate(result, SCHEMA, CALOTAS) == []
    assert any(r.reason.startswith("guardrail:") for r in result.rejected)


def test_clean_marks_missing_mandatory_and_drops_resolved_missing():
    result = clean(_listing(MappedAttribute(urn=CONDITION, valueId="14703", value="Novo"),
                            missing=[MissingAttribute(urn=CONDITION, reason="x"), MissingAttribute(urn="category", reason="x")]),
                   SCHEMA, CALOTAS)
    urns = {m.urn for m in result.missing}
    assert CONDITION not in urns and "category" not in urns
    assert {a["urn"] for a in SCHEMA["attributes"] if a.get("mandatory")} - {CONDITION} <= urns


def test_merge_resolved_wins_over_the_agent():
    agent = _listing(MappedAttribute(urn=CONDITION, valueId="0", value="whatever"), missing=[MissingAttribute(urn=CONDITION, reason="x")])
    merged = merge_resolved(agent, [MappedAttribute(urn=CONDITION, valueId="14703", value="Novo")])
    assert [(a.urn, a.value) for a in merged.attributes] == [(CONDITION, "Novo")]
    assert CONDITION not in {m.urn for m in merged.missing}
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest core/tests/test_catalog_guardrails.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'catalog.guardrails'`

- [ ] **Step 3: Write guardrails.py**

```python
# core/src/catalog/guardrails.py
"""Checks in code: nothing leaves out of contract, whatever the model says.

`validate` lists the problems in plain language (the agent gets them back and fixes them).
`clean` is the final net: it fixes the category, discards what is invalid and marks the
mandatory attributes that are missing. It never invents a value.
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
    missing = [m for m in listing.missing if m.urn not in seen and m.urn != "category"]
    already = {m.urn for m in missing}
    missing += [MissingAttribute(urn=urn, reason="mandatory with no valid value (guardrail)")
                for urn, d in definitions.items() if d.get("mandatory") and urn not in seen and urn not in already]
    return Listing(category=category_urn, attributes=kept, missing=missing, rejected=rejected)


def merge_resolved(listing: Listing, resolved: list[MappedAttribute]) -> Listing:
    """What the code resolved from the reference table wins over the agent."""
    fixed = {a.urn for a in resolved}
    attributes = [*resolved, *(a for a in listing.attributes if a.urn not in fixed)]
    missing = [m for m in listing.missing if m.urn not in fixed]
    return Listing(category=listing.category, attributes=attributes, missing=missing, rejected=list(listing.rejected))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest core/tests/test_catalog_guardrails.py -v`
Expected: all passed. Si `test_expected_listing_of_case_01_is_valid` falla, es una inconsistencia del `expected` mock: reportar NEEDS_CONTEXT con los problemas que devuelve `validate` (no aflojar la validación).

- [ ] **Step 5: Commit**

```bash
git add core/src/catalog/guardrails.py core/tests/test_catalog_guardrails.py
git commit -m "feat(catalog): validación en código y red final de la V2"
```

---

### Task 3: Correcciones y caché

**Files:**
- Create: `core/src/catalog/store.py`
- Test: `core/tests/test_catalog_store.py`

**Interfaces:**
- Consumes: `Listing` (`catalog.models`); `normalize` (`catalog.worklist`); `ROOT` (`catalog.data`).
- Produces:
  - `Correction` (frozen dataclass): `category_urn, attribute_urn, product_value, value_id, value, author, created_at`
  - `correction_key(attribute_urn: str, product_value: str) -> str`
  - `InMemoryCorrections`, `DynamoCorrections(table)`: `find(category_urn, attribute_urn, product_value) -> Correction | None`, `put(correction) -> None`, `list(category_urn) -> list[Correction]`
  - `InMemoryCache`, `DynamoCache(table)`: `get(sku, legacy_category, tables_version, prompt_version) -> Listing | None`, `put(sku, legacy_category, tables_version, prompt_version, category_urn, listing) -> None`, `invalidate_category(category_urn) -> int`
  - `stores_from_env(env=os.environ, outputs_path=ROOT / ".sst/outputs.json", resource_factory=None) -> tuple[corrections, cache, str]` (el `str` es `"dynamodb"` o `"in-memory"`)

- [ ] **Step 1: Write the failing tests**

```python
# core/tests/test_catalog_store.py
import json

from catalog.models import Listing
from catalog.store import (Correction, DynamoCache, DynamoCorrections, InMemoryCache, InMemoryCorrections,
                           correction_key, stores_from_env)

CALOTAS = "urn:category:102529:vendor:shopee"
CONDITION = "urn:attribute:101638:vendor:shopee"
LISTING = Listing(category=CALOTAS, attributes=[], missing=[], rejected=[])


def _correction(product_value="Usado"):
    return Correction(category_urn=CALOTAS, attribute_urn=CONDITION, product_value=product_value,
                      value_id="14703", value="Novo", author="catalog", created_at="2026-10-01")


class FakeTable:
    """Just enough of a boto3 Table: string key conditions with one :c value."""

    def __init__(self, keys):
        self.keys, self.items = keys, {}

    def _key(self, item):
        return tuple(item[k] for k in self.keys)

    def put_item(self, Item):
        self.items[self._key(Item)] = dict(Item)

    def get_item(self, Key):
        item = self.items.get(self._key(Key))
        return {"Item": item} if item else {}

    def delete_item(self, Key):
        self.items.pop(self._key(Key), None)

    def query(self, KeyConditionExpression, ExpressionAttributeValues, **kwargs):
        field = KeyConditionExpression.split(" = ")[0]
        return {"Items": [i for i in self.items.values() if i[field] == ExpressionAttributeValues[":c"]]}

    def scan(self, FilterExpression, ExpressionAttributeValues, **kwargs):
        field = FilterExpression.split(" = ")[0]
        return {"Items": [i for i in self.items.values() if i[field] == ExpressionAttributeValues[":c"]]}


def test_correction_key_normalizes_the_product_value():
    assert correction_key(CONDITION, "  USADO ") == correction_key(CONDITION, "usado")


def test_corrections_in_memory_and_dynamo_find_by_normalized_value():
    for store in (InMemoryCorrections(), DynamoCorrections(FakeTable(("category_urn", "correction_key")))):
        store.put(_correction("Usado"))
        assert store.find(CALOTAS, CONDITION, " usado ").value == "Novo"
        assert store.find(CALOTAS, CONDITION, "otro") is None
        assert [c.value for c in store.list(CALOTAS)] == ["Novo"]


def test_cache_in_memory_and_dynamo_roundtrip_and_invalidate_by_category():
    for cache in (InMemoryCache(), DynamoCache(FakeTable(("product_key", "version_key")))):
        cache.put("94701411", "734701", "t1", "seed", CALOTAS, LISTING)
        assert cache.get("94701411", "734701", "t1", "seed") == LISTING
        assert cache.get("94701411", "734701", "t2", "seed") is None
        assert cache.invalidate_category(CALOTAS) == 1
        assert cache.get("94701411", "734701", "t1", "seed") is None


def test_stores_from_env_without_tables_is_in_memory(tmp_path):
    corrections, cache, label = stores_from_env({}, outputs_path=tmp_path / "missing.json")
    assert label == "in-memory"
    assert isinstance(corrections, InMemoryCorrections) and isinstance(cache, InMemoryCache)


def test_stores_from_env_reads_table_names_from_outputs(tmp_path):
    outputs = tmp_path / "outputs.json"
    outputs.write_text(json.dumps({"correctionsTable": "corr-t", "mappingCacheTable": "cache-t"}))
    seen = []

    def resource_factory(env):
        class Resource:
            def Table(self, name):
                seen.append(name)
                return FakeTable(("a", "b"))
        return Resource()

    corrections, cache, label = stores_from_env({}, outputs_path=outputs, resource_factory=resource_factory)
    assert label == "dynamodb" and seen == ["corr-t", "cache-t"]
    assert isinstance(corrections, DynamoCorrections) and isinstance(cache, DynamoCache)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest core/tests/test_catalog_store.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'catalog.store'`

- [ ] **Step 3: Write store.py**

```python
# core/src/catalog/store.py
"""Corrections from the catalog team and the per-SKU mapping cache.

Both live in DynamoDB in the `warroom` stage; the in-memory versions serve tests and runs
without the account. Expressions are plain strings so a tiny fake table can evaluate them.
"""

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path

from .data import ROOT
from .models import Listing
from .worklist import normalize


@dataclass(frozen=True)
class Correction:
    category_urn: str
    attribute_urn: str
    product_value: str
    value_id: str
    value: str
    author: str
    created_at: str


def correction_key(attribute_urn: str, product_value: str) -> str:
    return f"{attribute_urn}#{normalize(product_value)}"


class InMemoryCorrections:
    def __init__(self):
        self._items: dict[tuple[str, str], Correction] = {}

    def find(self, category_urn, attribute_urn, product_value):
        return self._items.get((category_urn, correction_key(attribute_urn, product_value)))

    def put(self, correction: Correction) -> None:
        self._items[(correction.category_urn, correction_key(correction.attribute_urn, correction.product_value))] = correction

    def list(self, category_urn):
        return [c for (category, _), c in self._items.items() if category == category_urn]


class DynamoCorrections:
    def __init__(self, table):
        self.table = table

    def find(self, category_urn, attribute_urn, product_value):
        item = self.table.get_item(Key={"category_urn": category_urn,
                                        "correction_key": correction_key(attribute_urn, product_value)}).get("Item")
        return _correction(item) if item else None

    def put(self, correction: Correction) -> None:
        self.table.put_item(Item={**asdict(correction),
                                  "correction_key": correction_key(correction.attribute_urn, correction.product_value)})

    def list(self, category_urn):
        response = self.table.query(KeyConditionExpression="category_urn = :c",
                                    ExpressionAttributeValues={":c": category_urn})
        return [_correction(item) for item in response.get("Items", [])]


def _correction(item: dict) -> Correction:
    return Correction(**{k: item[k] for k in Correction.__dataclass_fields__})


def _cache_keys(sku, legacy_category, tables_version, prompt_version) -> tuple[str, str]:
    return f"{sku}#{legacy_category}", f"{tables_version}#{prompt_version}"


class InMemoryCache:
    def __init__(self):
        self._items: dict[tuple[str, str], tuple[str, Listing]] = {}

    def get(self, sku, legacy_category, tables_version, prompt_version):
        hit = self._items.get(_cache_keys(sku, legacy_category, tables_version, prompt_version))
        return hit[1] if hit else None

    def put(self, sku, legacy_category, tables_version, prompt_version, category_urn, listing: Listing) -> None:
        self._items[_cache_keys(sku, legacy_category, tables_version, prompt_version)] = (category_urn, listing)

    def invalidate_category(self, category_urn) -> int:
        stale = [k for k, (category, _) in self._items.items() if category == category_urn]
        for key in stale:
            del self._items[key]
        return len(stale)


class DynamoCache:
    def __init__(self, table):
        self.table = table

    def get(self, sku, legacy_category, tables_version, prompt_version):
        product_key, version_key = _cache_keys(sku, legacy_category, tables_version, prompt_version)
        item = self.table.get_item(Key={"product_key": product_key, "version_key": version_key}).get("Item")
        return Listing.model_validate_json(item["listing"]) if item else None

    def put(self, sku, legacy_category, tables_version, prompt_version, category_urn, listing: Listing) -> None:
        product_key, version_key = _cache_keys(sku, legacy_category, tables_version, prompt_version)
        self.table.put_item(Item={"product_key": product_key, "version_key": version_key,
                                  "category_urn": category_urn, "listing": listing.model_dump_json()})

    def invalidate_category(self, category_urn) -> int:
        items = self.table.scan(FilterExpression="category_urn = :c",
                                ExpressionAttributeValues={":c": category_urn}).get("Items", [])
        for item in items:
            self.table.delete_item(Key={"product_key": item["product_key"], "version_key": item["version_key"]})
        return len(items)


def _dynamodb(env):
    import boto3

    session = boto3.Session(profile_name=env.get("AWS_PROFILE") or None, region_name=env.get("AWS_REGION", "us-east-1"))
    return session.resource("dynamodb")


def stores_from_env(env=os.environ, outputs_path: Path = ROOT / ".sst/outputs.json", resource_factory=None):
    """DynamoDB tables from the env (Runtime) or from the deploy outputs (local); in memory otherwise."""
    names = {"corrections": env.get("CATALOG_CORRECTIONS_TABLE"), "cache": env.get("CATALOG_CACHE_TABLE")}
    if not all(names.values()) and outputs_path.exists():
        outputs = json.loads(outputs_path.read_text())
        names = {"corrections": outputs.get("correctionsTable"), "cache": outputs.get("mappingCacheTable")}
    if not all(names.values()):
        return InMemoryCorrections(), InMemoryCache(), "in-memory"
    resource = (resource_factory or _dynamodb)(env)
    return DynamoCorrections(resource.Table(names["corrections"])), DynamoCache(resource.Table(names["cache"])), "dynamodb"
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest core/tests/test_catalog_store.py -v`
Expected: all passed

- [ ] **Step 5: Commit**

```bash
git add core/src/catalog/store.py core/tests/test_catalog_store.py
git commit -m "feat(catalog): correcciones y caché por SKU con DynamoDB y versión en memoria"
```

---

### Task 4: Workflow V2 con FunctionAgent

**Files:**
- Modify: `core/src/catalog/events.py` (eventos nuevos y `source`)
- Modify: `core/src/catalog/prompts.py` (constante `PROMPT_NAME_V2`)
- Create: `core/src/catalog/prompts/catalog-v2-system.txt`, `core/src/catalog/v2.py`
- Create: `core/tests/catalog_fakes.py` (doble del LLM, reusable)
- Test: `core/tests/test_catalog_v2.py`

**Interfaces:**
- Consumes: tareas 1 a 3; `is_auth_error` (`catalog.llm`); `Listing`, `MissingAttribute` (`catalog.models`).
- Produces:
  - `events.py`: `CacheMissed(product: dict)`, `WorkReady(product: dict, category_urn: str, category_name: str, worklist: Worklist)`, `AgentDone(product: dict, category_urn: str, worklist: Worklist, last: Listing | None, valid: bool, error: str | None = None)`; `MappingCompleted.source: str = "model"`
  - `prompts.py`: `PROMPT_NAME_V2 = "catalog-v2-system"`
  - `v2.py`: `MAX_ITERATIONS = 5`, `work_message(ev: WorkReady) -> str`, `MappingV2(llm, system_prompt: str, prompt_version: str, schemas: dict, reference: Reference, corrections, cache, **workflow_kwargs)`; `await MappingV2(...).run(product=...)` → `MappingCompleted`
  - `catalog_fakes.py`: `ScriptedLLM(script: list[list[ToolSelection]])` con `.seen` (último mensaje que vio en cada llamada) y `call(name, **kwargs) -> ToolSelection`

- [ ] **Step 1: Write the LLM double**

```python
# core/tests/catalog_fakes.py
"""A scripted FunctionCallingLLM: FunctionAgent's `llm` field is Pydantic, so the double must subclass it."""

import itertools

from llama_index.core.base.llms.types import ChatMessage, ChatResponse, LLMMetadata
from llama_index.core.llms.function_calling import FunctionCallingLLM
from llama_index.core.llms.llm import ToolSelection

_ids = itertools.count()


def call(name: str, **kwargs) -> ToolSelection:
    return ToolSelection(tool_id=f"call-{next(_ids)}", tool_name=name, tool_kwargs=kwargs)


class ScriptedLLM(FunctionCallingLLM):
    script: list = []
    seen: list = []

    @property
    def metadata(self) -> LLMMetadata:
        return LLMMetadata(is_function_calling_model=True, model_name="scripted")

    async def achat_with_tools(self, tools, user_msg=None, chat_history=None, verbose=False,
                               allow_parallel_tool_calls=False, **kwargs):
        history = chat_history or []
        self.seen.append(history[-1].content if history else None)
        calls = self.script.pop(0) if self.script else []
        return ChatResponse(message=ChatMessage(role="assistant", content="" if calls else "done"), raw={"calls": calls})

    def get_tool_calls_from_response(self, response, error_on_no_tool_call=True, **kwargs):
        return response.raw["calls"]

    def _prepare_chat_with_tools(self, *args, **kwargs):
        raise NotImplementedError

    def chat(self, *args, **kwargs):
        raise NotImplementedError

    async def achat(self, *args, **kwargs):
        raise NotImplementedError

    def complete(self, *args, **kwargs):
        raise NotImplementedError

    async def acomplete(self, *args, **kwargs):
        raise NotImplementedError

    def stream_chat(self, *args, **kwargs):
        raise NotImplementedError

    async def astream_chat(self, *args, **kwargs):
        raise NotImplementedError

    def stream_complete(self, *args, **kwargs):
        raise NotImplementedError

    async def astream_complete(self, *args, **kwargs):
        raise NotImplementedError
```

- [ ] **Step 2: Write the failing tests**

```python
# core/tests/test_catalog_v2.py
from catalog_fakes import ScriptedLLM, call

from catalog.data import data_dir, load_cases, load_schemas
from catalog.guardrails import validate
from catalog.models import Listing
from catalog.reference import load_reference
from catalog.store import Correction, InMemoryCache, InMemoryCorrections
from catalog.v2 import MAX_ITERATIONS, MappingV2

MOCK = data_dir("mock")
SCHEMAS = load_schemas(MOCK)
REFERENCE = load_reference(MOCK)
CASES = {c["id"]: c for c in load_cases(MOCK)}
CALOTAS = "urn:category:102529:vendor:shopee"
CONDITION = "urn:attribute:101638:vendor:shopee"
PRODUCT = CASES["01-real-calota-aro14"]["product"]
GOOD = {k: CASES["01-real-calota-aro14"]["expected"][k] for k in ("category", "attributes", "missing", "rejected")}


def _workflow(llm, cache=None, corrections=None):
    return MappingV2(llm=llm, system_prompt="S", prompt_version="seed", schemas=SCHEMAS, reference=REFERENCE,
                     corrections=corrections or InMemoryCorrections(), cache=cache or InMemoryCache(), timeout=30)


async def test_valid_submission_on_the_first_try_is_cached():
    cache = InMemoryCache()
    llm = ScriptedLLM(script=[[call("submit_listing", **GOOD)]])
    done = await _workflow(llm, cache=cache).run(product=PRODUCT)
    assert done.source == "agent" and done.error is None
    assert validate(done.listing, SCHEMAS[CALOTAS], CALOTAS) == []
    assert cache.get(PRODUCT["sku"], "734701", REFERENCE.version, "seed") == done.listing


async def test_cache_hit_does_not_call_the_model():
    cache = InMemoryCache()
    cache.put(PRODUCT["sku"], "734701", REFERENCE.version, "seed", CALOTAS, Listing.model_validate(GOOD))
    llm = ScriptedLLM(script=[])
    done = await _workflow(llm, cache=cache).run(product=PRODUCT)
    assert done.source == "cache" and llm.seen == []


async def test_product_without_category_does_not_call_the_model():
    llm = ScriptedLLM(script=[])
    done = await _workflow(llm).run(product=CASES["09-sin-categoria"]["product"])
    assert done.source == "tables" and done.listing.category is None
    assert done.listing.missing[0].urn == "category" and llm.seen == []


async def test_category_without_schema_does_not_call_the_model():
    product = {**PRODUCT, "categories": [{"urn": "urn:category:900001", "name": "Amortecedores (MOCK)"}]}
    done = await _workflow(ScriptedLLM(script=[])).run(product=product)
    assert done.source == "tables" and "schema" in done.listing.missing[0].reason


async def test_invalid_submission_gets_the_problems_and_is_fixed():
    bad = {**GOOD, "attributes": [*GOOD["attributes"], {"urn": "urn:attribute:1:vendor:shopee", "valueId": "0", "value": "x"}]}
    llm = ScriptedLLM(script=[[call("submit_listing", **bad)], [call("submit_listing", **GOOD)]])
    done = await _workflow(llm).run(product=PRODUCT)
    assert "did not pass validation" in (llm.seen[1] or "")
    assert validate(done.listing, SCHEMAS[CALOTAS], CALOTAS) == []


async def test_exhausted_iterations_clean_the_last_submission_and_do_not_cache():
    bad = {**GOOD, "attributes": [*GOOD["attributes"], {"urn": "urn:attribute:1:vendor:shopee", "valueId": "0", "value": "x"}]}
    cache = InMemoryCache()
    llm = ScriptedLLM(script=[[call("submit_listing", **bad)] for _ in range(MAX_ITERATIONS + 2)])
    done = await _workflow(llm, cache=cache).run(product=PRODUCT)
    assert done.source == "agent" and validate(done.listing, SCHEMAS[CALOTAS], CALOTAS) == []
    assert cache.get(PRODUCT["sku"], "734701", REFERENCE.version, "seed") is None


async def test_no_submission_is_an_error():
    done = await _workflow(ScriptedLLM(script=[[]])).run(product=PRODUCT)
    assert done.listing is None and "never submitted" in done.error


async def test_resolved_attributes_win_over_the_agent():
    other = next(v for v in next(a for a in SCHEMAS[CALOTAS]["attributes"] if a["urn"] == CONDITION)["values"]
                 if v["name"] != "Novo")
    tampered = {**GOOD, "attributes": [{"urn": CONDITION, "valueId": str(other["id"]), "value": other["name"]}
                                       if a["urn"] == CONDITION else a for a in GOOD["attributes"]]}
    done = await _workflow(ScriptedLLM(script=[[call("submit_listing", **tampered)]])).run(product=PRODUCT)
    assert {a.urn: a.value for a in done.listing.attributes}[CONDITION] == "Novo"


async def test_lookup_corrections_returns_the_correction_to_the_model():
    corrections = InMemoryCorrections()
    corrections.put(Correction(category_urn=CALOTAS, attribute_urn=CONDITION, product_value="1", value_id="14703",
                               value="Novo", author="catalog", created_at="2026-10-01"))
    llm = ScriptedLLM(script=[[call("lookup_corrections", attribute_urn=CONDITION, product_value=" 1 ")],
                              [call("submit_listing", **GOOD)]])
    await _workflow(llm, corrections=corrections).run(product=PRODUCT)
    assert "Novo" in (llm.seen[1] or "")


async def test_dynamodb_failures_do_not_break_the_mapping():
    class Broken:
        def get(self, *a, **k):
            raise RuntimeError("dynamodb down")

        def put(self, *a, **k):
            raise RuntimeError("dynamodb down")

        def find(self, *a, **k):
            raise RuntimeError("dynamodb down")

    llm = ScriptedLLM(script=[[call("lookup_corrections", attribute_urn=CONDITION, product_value="Novo")],
                              [call("submit_listing", **GOOD)]])
    done = await _workflow(llm, cache=Broken(), corrections=Broken()).run(product=PRODUCT)
    assert done.listing is not None and done.error is None
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `uv run pytest core/tests/test_catalog_v2.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'catalog.v2'`

- [ ] **Step 4: Extend events.py and prompts.py**

En `core/src/catalog/events.py`, agregar el import `from .worklist import Worklist`, el campo `source` y los eventos nuevos:

```python
class MappingCompleted(StopEvent):
    """End of a mapping. No field is called `result`: it would collide with StopEvent's."""

    listing: Listing | None
    error: str | None = None
    # Where the listing came from: "model" (V1), "cache", "tables" or "agent" (V2).
    source: str = "model"


class CacheMissed(Event):
    product: dict


class WorkReady(Event):
    product: dict
    category_urn: str
    category_name: str
    worklist: Worklist


class AgentDone(Event):
    product: dict
    category_urn: str
    worklist: Worklist
    last: Listing | None
    valid: bool
    error: str | None = None
```

En `core/src/catalog/prompts.py`, debajo de `PROMPT_NAME`:

```python
PROMPT_NAME_V2 = "catalog-v2-system"
```

- [ ] **Step 5: Write the V2 seed prompt**

```text
You are a catalog specialist for auto parts marketplaces. The code already resolved the
Shopee category and every field that Alephee's reference tables answer. You receive a work
list in JSON and complete the listing for Shopee.

The work list has four parts:
- resolved: attributes already decided by the code. Never change them.
- to_decide: attributes the reference table maps, whose product value does not match the
  channel list exactly. Choose the equivalent value from "values" and use its id and its
  name exactly as listed. If no value is equivalent, leave it out.
- uncovered_channel: attributes of the category that the table does not map. Fill one only
  if a product attribute in unmapped_product is clearly the same concept.
- unmapped_product: product attributes with no destination in the table.

Rules:
- Before choosing a list value, call lookup_corrections with the attribute urn and the
  product value. If it returns a correction, use it exactly.
- Never invent or translate values. Shopee values stay in Portuguese, as the list shows them.
- The values "-1", "N/A" or empty mean there is no data.
- Free text attributes use valueId "0" and the product value as it is.
- If a mandatory attribute cannot be filled, add it to "missing" with the reason.
- If a product attribute cannot be used, add it to "rejected" with its legacyId and the reason.
- Use the category from the work list. Each attribute appears once.
- Deliver with submit_listing, including the resolved attributes. If it returns problems,
  fix them and call submit_listing again.
```

Guardarlo en `core/src/catalog/prompts/catalog-v2-system.txt` (sin la línea de ruta).

- [ ] **Step 6: Write v2.py**

```python
# core/src/catalog/v2.py
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
```

- [ ] **Step 7: Run tests to verify they pass**

Run: `uv run pytest core/tests/test_catalog_v2.py -v`
Expected: 10 passed. Si `FunctionAgent` no devuelve al modelo el texto del error de `submit_listing` en `llm.seen[1]`, reportar NEEDS_CONTEXT con lo que sí ve (el sondeo del 1/10 lo confirmó con 0.14.24).

- [ ] **Step 8: Run the full suite**

Run: `uv run pytest core/tests -q`
Expected: todo en verde (la V1 no cambia; `source` es opcional).

- [ ] **Step 9: Commit**

```bash
git add core/src/catalog/events.py core/src/catalog/prompts.py core/src/catalog/prompts/catalog-v2-system.txt core/src/catalog/v2.py core/tests/catalog_fakes.py core/tests/test_catalog_v2.py
git commit -m "feat(catalog): V2 como Workflow con FunctionAgent, entrega validada, correcciones y caché"
```

---

### Task 5: Tablas en el stack, carga de correcciones y deploy

**Files:**
- Create: `infra/sst/catalogo.ts`
- Modify: `infra/sst/runtime.ts` (permisos y variables del Runtime)
- Modify: `sst.config.ts` (outputs con los nombres de las tablas)
- Create: `core/src/catalog/correct.py`, `scripts/correct.sh`
- Test: `core/tests/test_catalog_correct.py`

**Interfaces:**
- Consumes: `Correction`, `stores_from_env` (tarea 3); `load_schemas`, `data_dir` (`catalog.data`).
- Produces: outputs `correctionsTable` y `mappingCacheTable` en `.sst/outputs.json`; variables `CATALOG_CORRECTIONS_TABLE` y `CATALOG_CACHE_TABLE` en el Runtime; `correct.main(argv, stores=None) -> None`.

- [ ] **Step 1: Write the failing test**

```python
# core/tests/test_catalog_correct.py
import pytest

from catalog.correct import main
from catalog.models import Listing
from catalog.store import InMemoryCache, InMemoryCorrections

CALOTAS = "urn:category:102529:vendor:shopee"
CONDITION = "urn:attribute:101638:vendor:shopee"
ARGS = ["--category", CALOTAS, "--attribute", CONDITION, "--product-value", "1", "--value-id", "14703", "--value", "Novo"]


def test_correct_stores_the_correction_and_invalidates_the_category():
    corrections, cache = InMemoryCorrections(), InMemoryCache()
    cache.put("94701411", "734701", "t", "seed", CALOTAS, Listing(category=CALOTAS, attributes=[], missing=[], rejected=[]))
    main(ARGS, stores=(corrections, cache, "in-memory"))
    assert corrections.find(CALOTAS, CONDITION, "1").value == "Novo"
    assert cache.get("94701411", "734701", "t", "seed") is None


def test_correct_rejects_a_value_outside_the_channel_list():
    with pytest.raises(SystemExit) as info:
        main([*ARGS[:-4], "--value-id", "99999", "--value", "Nuevo"], stores=(InMemoryCorrections(), InMemoryCache(), "in-memory"))
    assert "not in the channel list" in str(info.value)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest core/tests/test_catalog_correct.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'catalog.correct'`

- [ ] **Step 3: Write correct.py and the script**

```python
# core/src/catalog/correct.py
"""Load a correction from the catalog team and drop the cached mappings of that category.

    scripts/correct.sh --category <urn> --attribute <urn> --product-value <value> --value-id <id> --value <name>
"""

import argparse
from datetime import date

from .data import data_dir, load_schemas
from .store import Correction, stores_from_env


def _check(category: str, attribute: str, value_id: str, value: str) -> None:
    schemas = {**load_schemas(data_dir("mock")), **load_schemas(data_dir("real"))}
    definition = next((a for a in schemas.get(category, {}).get("attributes", []) if a["urn"] == attribute), None)
    if definition is None:
        raise SystemExit(f"{attribute} is not an attribute of {category}")
    domain = {str(v["id"]): v["name"] for v in definition.get("values") or []}
    if domain and domain.get(value_id) != value:
        raise SystemExit(f"{value} (id {value_id}) is not in the channel list of {attribute}")


def main(argv: list[str] | None = None, stores=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for flag in ("--category", "--attribute", "--product-value", "--value-id", "--value"):
        parser.add_argument(flag, required=True)
    parser.add_argument("--author", default="catalog")
    args = parser.parse_args(argv)
    _check(args.category, args.attribute, args.value_id, args.value)
    corrections, cache, label = stores or stores_from_env()
    corrections.put(Correction(category_urn=args.category, attribute_urn=args.attribute, product_value=args.product_value,
                               value_id=args.value_id, value=args.value, author=args.author,
                               created_at=date.today().isoformat()))
    dropped = cache.invalidate_category(args.category)
    print(f"Correction stored ({label}); {dropped} cached mappings of {args.category} dropped.")


if __name__ == "__main__":
    main()
```

```bash
#!/usr/bin/env bash
# scripts/correct.sh — loads a correction from the catalog team into DynamoDB (stage warroom).
set -euo pipefail
cd "$(dirname "$0")/.."
export AWS_PROFILE="${AWS_PROFILE:-sandbox}" AWS_REGION="${AWS_REGION:-us-east-1}"
PYTHONPATH=core/src exec uv run python -m catalog.correct "$@"
```

```bash
chmod +x scripts/correct.sh
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest core/tests/test_catalog_correct.py -v`
Expected: 2 passed

- [ ] **Step 5: Infrastructure**

`infra/sst/catalogo.ts`:

```ts
// Catalog agent (war room): the catalog team's corrections and the per-SKU mapping cache.
// The Runtime reads and writes them (infra/sst/runtime.ts); scripts/correct.sh loads
// corrections from a laptop with the SSO profile.
export const correctionsTable = new sst.aws.Dynamo("CatalogCorrections", {
  fields: { category_urn: "string", correction_key: "string" },
  primaryIndex: { hashKey: "category_urn", rangeKey: "correction_key" },
});

export const mappingCacheTable = new sst.aws.Dynamo("CatalogMappingCache", {
  fields: { product_key: "string", version_key: "string" },
  primaryIndex: { hashKey: "product_key", rangeKey: "version_key" },
});
```

En `infra/sst/runtime.ts`:
- agregar `import { correctionsTable, mappingCacheTable } from "./catalogo";` junto a los otros imports;
- dentro de `environmentVariables`, junto a `CATALOG_ENABLED: "1"`:

```ts
    CATALOG_CORRECTIONS_TABLE: correctionsTable.name,
    CATALOG_CACHE_TABLE: mappingCacheTable.name,
```

- dentro del `Statement: [` de la policy del `RuntimeRolePolicy`, una entrada más (el Runtime solo lee y escribe; invalidar la caché lo hace `scripts/correct.sh` desde local):

```ts
      {
        // Catalog agent (war room): corrections and per-SKU cache.
        Effect: "Allow",
        Action: ["dynamodb:GetItem", "dynamodb:PutItem", "dynamodb:Query"],
        Resource: [correctionsTable.arn, mappingCacheTable.arn],
      },
```

En `sst.config.ts`, dentro de `run()`, antes del `return`:

```ts
    const { correctionsTable, mappingCacheTable } = await import("./infra/sst/catalogo");
```

y el `return` final pasa a:

```ts
    return {
      runtimeArn: runtime.agentRuntimeArn,
      repoCore: repo.name,
      correctionsTable: correctionsTable.name,
      mappingCacheTable: mappingCacheTable.name,
    };
```

Run: `npm run typecheck`
Expected: sin errores nuevos (los de `typecheck:infra` sin `.sst/platform` son previos).

- [ ] **Step 6: Deploy**

```bash
AWS_PROFILE=sandbox AWS_REGION=us-east-1 npx sst deploy --stage warroom
python3 -c "import json; print(sorted(json.load(open('.sst/outputs.json'))))"
```

Expected: `✓ Complete` y los outputs `correctionsTable` y `mappingCacheTable`. Si un `GatewayTarget` falla con `InternalFailure`, reintentar el deploy una vez (pasó el 1/10 y se resolvió solo).

- [ ] **Step 7: Run the full suite and commit**

Run: `uv run pytest core/tests -q`

```bash
git add infra/sst/catalogo.ts infra/sst/runtime.ts sst.config.ts core/src/catalog/correct.py scripts/correct.sh core/tests/test_catalog_correct.py
git commit -m "feat(infra): tablas de correcciones y caché del catálogo, y carga de correcciones"
```

---

### Task 6: Experimento V2 y dos herramientas en el chat

**Files:**
- Modify: `core/src/catalog/experiment.py` (`--version v2`, tarea V2, total de obligatorios sin informar)
- Modify: `core/src/catalog/evaluation.py` (`missing_not_detected_total` por corrida)
- Modify: `core/src/catalog/chat_tool.py` (`map_product_v1` y `map_product_v2`)
- Modify: `client.config.ts` (regla 1 del `promptSistema`)
- Modify: `apps/web/mock.mjs`, `apps/web/mock.test.mjs` (texto del escenario `sku`)
- Test: `core/tests/test_catalog_experiment.py`, `core/tests/test_catalog_chat_tool.py`, `core/tests/test_catalog_evaluation.py`

**Interfaces:**
- Consumes: `MappingV2`, `PROMPT_NAME_V2` (tarea 4); `load_reference` (tarea 1); `stores_from_env` (tarea 3).
- Produces: `make_v2_task(llm, system_prompt, prompt_version, schemas, reference, corrections, cache, workflow_cls=MappingV2)`; `create_catalog_tools(..., workflow_v2_cls=MappingV2, stores_factory=stores_from_env)` devuelve dos herramientas.

- [ ] **Step 1: Write the failing tests**

En `core/tests/test_catalog_evaluation.py`:

```python
def test_run_evaluator_reports_missing_not_detected_total():
    run_evaluator = make_run_evaluator(SCHEMAS)
    expected = CASES["06-falta-obligatorio"]["expected"]
    no_missing = {**expected, "missing": []}
    items = [SimpleNamespace(item=SimpleNamespace(expected_output=expected), output=no_missing)]
    scores = {e.name: e.value for e in run_evaluator(item_results=items)}
    assert scores["missing_not_detected_total"] == 1
```

En `core/tests/test_catalog_experiment.py`:

```python
async def test_v2_task_returns_the_listing_and_its_source():
    from catalog.experiment import make_v2_task

    listing = Listing(category="urn:x", attributes=[], missing=[], rejected=[])

    class FakeV2:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        async def run(self, product):
            return MappingCompleted(listing=listing, source="cache")

    task = make_v2_task(llm=None, system_prompt="S", prompt_version="seed", schemas={}, reference=None,
                        corrections=None, cache=None, workflow_cls=FakeV2)
    assert (await task(item=SimpleNamespace(input={}))) == listing.model_dump()


def test_main_accepts_v2_and_still_refuses_real_data_without_the_flag():
    with pytest.raises(SystemExit) as info:
        main(["--version", "v2", "--data", "real"])
    assert "allow-real-upload" in str(info.value)
```

En `core/tests/test_catalog_chat_tool.py` (adaptar los helpers existentes que hacen `(tool,) = create_catalog_tools(...)` para elegir por nombre, y sumar):

```python
def test_two_tools_v1_and_v2():
    tools = create_catalog_tools(llm_factory=lambda: None, directories=[data_dir("mock")],
                                 stores_factory=lambda env: (None, None, "in-memory"))
    assert sorted(t.metadata.name for t in tools) == ["map_product_v1", "map_product_v2"]


async def test_v2_tool_runs_the_v2_workflow():
    expected = CASE["expected"]
    listing = Listing.model_validate({k: expected[k] for k in ("category", "attributes", "missing", "rejected")})

    class FakeV2:
        def __init__(self, **kwargs):
            pass

        async def run(self, product):
            return MappingCompleted(listing=listing, source="agent")

    tools = {t.metadata.name: t for t in create_catalog_tools(
        llm_factory=lambda: None, workflow_v2_cls=FakeV2, directories=[data_dir("mock")],
        stores_factory=lambda env: (None, None, "in-memory"))}
    out = json.loads(str(await tools["map_product_v2"].acall(sku=CASE["product"]["sku"])))
    assert out["category"]["name"] == "Calotas" and out["source"] == "agent"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest core/tests/test_catalog_evaluation.py core/tests/test_catalog_experiment.py core/tests/test_catalog_chat_tool.py -v`
Expected: FAIL (`missing_not_detected_total`, `make_v2_task`, `map_product_v2` no existen)

- [ ] **Step 3: Implement**

`evaluation.py`, en `make_run_evaluator`, agregar a la lista devuelta:

```python
            Evaluation(name="missing_not_detected_total", value=summary["missing_not_detected"]),
```

`experiment.py`:
- `--version` pasa a `choices=["v1", "v2", "current"]`;
- extraer el cuerpo protegido de `make_v1_task` a un helper y sumar `make_v2_task`:

```python
async def _run(workflow, product) -> dict:
    try:
        done = await workflow.run(product=product)
    except Exception as exc:  # noqa: BLE001 — only an auth error is special-cased
        cause = exc.__cause__
        if is_auth_error(exc) or (cause is not None and is_auth_error(cause)):
            raise SystemExit(auth_error_message(exc, os.environ.get("AWS_PROFILE") or None)) from exc
        raise
    return done.listing.model_dump() if done.listing is not None else {"error": done.error}


def make_v1_task(llm, system_prompt: str, schemas: dict[str, dict], workflow_cls=MappingV1):
    async def task(*, item, **kwargs) -> dict:
        return await _run(workflow_cls(llm=llm, system_prompt=system_prompt, schemas=schemas, timeout=180), item.input)

    return task


def make_v2_task(llm, system_prompt: str, prompt_version: str, schemas, reference, corrections, cache,
                 workflow_cls=MappingV2):
    async def task(*, item, **kwargs) -> dict:
        return await _run(workflow_cls(llm=llm, system_prompt=system_prompt, prompt_version=prompt_version,
                                       schemas=schemas, reference=reference, corrections=corrections,
                                       cache=cache, timeout=300), item.input)

    return task
```

- en `main`, `check_aws()` corre para `v1` y `v2`; y el armado de la tarea:

```python
    if args.version in ("v1", "v2"):
        name = PROMPT_NAME if args.version == "v1" else PROMPT_NAME_V2
        sync_seed(name, client)
        prompt = get_system_prompt(name, client)
        llm = create_llm()
        metadata |= {"model": llm.model, "prompt": prompt_label(prompt)}
        if args.version == "v1":
            task = make_v1_task(llm, prompt.text, schemas)
        else:
            corrections, cache, stores = stores_from_env()
            print(f"V2 stores: {stores}")
            metadata |= {"stores": stores}
            task = make_v2_task(llm, prompt.text, str(prompt.version or "seed"), schemas,
                                load_reference(directory), corrections, cache)
    else:
        task = current_task
```

con los imports `from .prompts import PROMPT_NAME, PROMPT_NAME_V2, get_system_prompt, sync_seed`, `from .reference import load_reference`, `from .store import stores_from_env`, `from .v2 import MappingV2`. Actualizar el docstring del módulo con un ejemplo `--version v2 --data mock`.

`chat_tool.py`: refactorizar a un helper común y dos herramientas:

```python
def create_catalog_tools(llm_factory=create_llm, workflow_cls=MappingV1, workflow_v2_cls=MappingV2, directories=None,
                         env=None, stores_factory=stores_from_env) -> list[FunctionTool]:
    env = os.environ if env is None else env
    if directories is None:
        directories = [data_dir("real"), data_dir("mock")] if env.get("CATALOG_ALLOW_REAL_DATA") == "1" \
            else [data_dir("mock")]

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
        return _describe(str(sku).strip(), done.listing, schemas, done.source)

    async def map_product_v1(sku: str) -> str:
        """Map a product of the Alephee catalog to a Shopee listing with V1 (a single structured call)."""
        prompt = get_system_prompt(PROMPT_NAME, langfuse_client())
        return await _map(sku, lambda product, directory, schemas: workflow_cls(
            llm=llm_factory(), system_prompt=prompt.text, schemas=schemas, timeout=180))

    async def map_product_v2(sku: str) -> str:
        """Map a product of the Alephee catalog to a Shopee listing with V2 (reference tables, validation,
        corrections and cache)."""
        prompt = get_system_prompt(PROMPT_NAME_V2, langfuse_client())
        corrections, cache, _ = stores_factory(env)
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
```

y `_describe(sku, listing, schemas, source)` suma `"source": source` al JSON. Imports: `PROMPT_NAME_V2`, `load_reference`, `stores_from_env`, `MappingV2`.

`client.config.ts`: la regla 1 del `promptSistema` pasa a:

```ts
    "1. Si te piden mapear un producto por SKU, usa `map_product_v2`. Usa `map_product_v1` solo si piden la V1 o comparar versiones. Presenta en una tabla la categoría, los atributos y los faltantes, sin cambiar lo que devuelve la herramienta.",
```

Verificar el largo: `node -e` armando el string del array y `Buffer.from(s).toString('base64').length` < 2048.

`apps/web/mock.mjs`: el texto `TEXTO_MAP_PRODUCT` menciona la V2 ("...map_product_v2...") y `mock.test.mjs` sigue pasando.

- [ ] **Step 4: Run tests**

Run: `uv run pytest core/tests -q && npm test && npm run typecheck`
Expected: todo en verde

- [ ] **Step 5: Commit**

```bash
git add core/src/catalog/experiment.py core/src/catalog/evaluation.py core/src/catalog/chat_tool.py client.config.ts apps/web/mock.mjs apps/web/mock.test.mjs core/tests/test_catalog_experiment.py core/tests/test_catalog_chat_tool.py core/tests/test_catalog_evaluation.py
git commit -m "feat(catalog): experimento V2 y herramientas map_product_v1 y map_product_v2 en el chat"
```

---

### Task 7: Tests de punta a punta

**Files:**
- Modify: `pyproject.toml` (marker `e2e` y omitirlos por defecto)
- Create: `core/tests/e2e/conftest.py`, `core/tests/e2e/test_e2e_mapping.py`, `core/tests/e2e/test_e2e_chat.py`, `scripts/e2e.sh`

**Interfaces:**
- Consumes: todo lo anterior; deploy de la tarea 5; `.env` con `CHAT_HMAC_SECRET`.

- [ ] **Step 1: Marker y saltos**

En `pyproject.toml`, `[tool.pytest.ini_options]`:

```toml
markers = ["e2e: runs against real AWS services and the deployed chat (RUN_E2E=1)"]
```

`core/tests/e2e/conftest.py`:

```python
import os

import pytest


def pytest_collection_modifyitems(config, items):
    if os.environ.get("RUN_E2E") == "1":
        return
    skip = pytest.mark.skip(reason="e2e: set RUN_E2E=1 (scripts/e2e.sh)")
    for item in items:
        if "e2e" in item.keywords:
            item.add_marker(skip)
```

- [ ] **Step 2: Nivel 1 · el agente contra Bedrock y DynamoDB**

```python
# core/tests/e2e/test_e2e_mapping.py
import boto3
import pytest

from catalog.data import data_dir, load_cases, load_schemas
from catalog.guardrails import validate
from catalog.llm import create_llm
from catalog.prompts import PROMPT_NAME, PROMPT_NAME_V2, load_seed
from catalog.reference import load_reference
from catalog.store import Correction, InMemoryCache, stores_from_env
from catalog.v1 import MappingV1
from catalog.v2 import MappingV2

pytestmark = pytest.mark.e2e
MOCK = data_dir("mock")
SCHEMAS = load_schemas(MOCK)
REFERENCE = load_reference(MOCK)
CASES = {c["id"]: c for c in load_cases(MOCK)}
CALOTAS = "urn:category:102529:vendor:shopee"
PROMPT_VERSION = "e2e"


@pytest.fixture(scope="module", autouse=True)
def aws_credentials():
    try:
        boto3.Session().client("sts").get_caller_identity()
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"no AWS credentials: {type(exc).__name__}")


@pytest.fixture(scope="module")
def stores():
    return stores_from_env()


def _v2(stores, cache=None):
    corrections, real_cache, _ = stores
    return MappingV2(llm=create_llm(), system_prompt=load_seed(PROMPT_NAME_V2), prompt_version=PROMPT_VERSION,
                     schemas=SCHEMAS, reference=REFERENCE, corrections=corrections, cache=cache or real_cache, timeout=300)


async def test_v1_maps_the_real_example_product():
    done = await MappingV1(llm=create_llm(), system_prompt=load_seed(PROMPT_NAME), schemas=SCHEMAS,
                           timeout=180).run(product=CASES["01-real-calota-aro14"]["product"])
    assert done.listing is not None and done.listing.category == CALOTAS


@pytest.mark.parametrize("case_id", sorted(CASES))
async def test_v2_never_delivers_invalid_listings(case_id, stores):
    done = await _v2(stores, cache=InMemoryCache()).run(product=CASES[case_id]["product"])
    if case_id == "09-sin-categoria":
        assert done.source == "tables" and done.listing.missing[0].urn == "category"
        return
    assert done.listing is not None, done.error
    if done.listing.category:
        assert validate(done.listing, SCHEMAS[done.listing.category], done.listing.category) == []


async def test_second_run_comes_from_the_cache(stores):
    product = CASES["02-calota-aro13-preta-completa"]["product"]
    cache = stores[1]
    cache.invalidate_category(CALOTAS)
    first = await _v2(stores).run(product=product)
    second = await _v2(stores).run(product=product)
    assert first.source == "agent" and second.source == "cache"
    assert second.listing == first.listing


async def test_a_correction_changes_the_result(stores):
    # "Novo" matches the channel list exactly and the code resolves it without asking for
    # corrections, so the test uses a product value with no exact match: the attribute goes
    # to the agent, which has to call lookup_corrections.
    from catalog.store import correction_key

    corrections, cache, _ = stores
    case = CASES["01-real-calota-aro14"]
    condition = "urn:attribute:101638:vendor:shopee"
    value = "Novo (e2e)"
    other = next(v for v in next(a for a in SCHEMAS[CALOTAS]["attributes"] if a["urn"] == condition)["values"]
                 if v["name"] != "Novo")
    product = {**case["product"], "attributes": [{**a, "value": value} if a["urn"] == "urn:attribute:1673" else a
                                                 for a in case["product"]["attributes"]]}
    try:
        corrections.put(Correction(category_urn=CALOTAS, attribute_urn=condition, product_value=value,
                                   value_id=str(other["id"]), value=other["name"], author="e2e", created_at="2026-10-01"))
        done = await _v2(stores, cache=InMemoryCache()).run(product=product)
        assert {a.urn: a.value for a in done.listing.attributes}.get(condition) == other["name"]
    finally:
        table = getattr(corrections, "table", None)
        if table is not None:
            table.delete_item(Key={"category_urn": CALOTAS, "correction_key": correction_key(condition, value)})
        cache.invalidate_category(CALOTAS)
```

- [ ] **Step 3: Nivel 2 · el chat desplegado**

```python
# core/tests/e2e/test_e2e_chat.py
import base64
import hashlib
import hmac
import json
import os
import time
from pathlib import Path

import httpx
import pytest

pytestmark = pytest.mark.e2e
ROOT = Path(__file__).resolve().parents[3]


def _b64(obj) -> str:
    return base64.urlsafe_b64encode(json.dumps(obj, separators=(",", ":")).encode()).rstrip(b"=").decode()


def _token(user_id: str, secret: str, ttl: int = 600) -> str:
    """Same token as apps/web/sign.mjs: HS256 over base64url header and body."""
    now = int(time.time())
    body = _b64({"alg": "HS256", "typ": "JWT"}) + "." + _b64({"sub": user_id, "iat": now, "exp": now + ttl})
    signature = base64.urlsafe_b64encode(hmac.new(secret.encode(), body.encode(), hashlib.sha256).digest()).rstrip(b"=")
    return f"{body}.{signature.decode()}"


def _api_url() -> str | None:
    outputs = ROOT / ".sst/outputs.json"
    if os.environ.get("API_URL"):
        return os.environ["API_URL"]
    return json.loads(outputs.read_text()).get("Chat") if outputs.exists() else None


def test_deployed_chat_maps_a_sku_with_v2():
    base, secret = _api_url(), os.environ.get("CHAT_HMAC_SECRET")
    if not base or not secret:
        pytest.skip("no deployed chat URL or CHAT_HMAC_SECRET")
    headers = {"authorization": f"Bearer {_token('warroom-e2e', secret)}"}
    thread = f"e2e-{int(time.time())}"
    posted = httpx.post(f"{base.rstrip('/')}/mensajes", json={"texto": "Mapea el SKU 94701411 con la V2", "hilo": thread},
                        headers=headers, timeout=30)
    assert posted.status_code == 200
    deadline = time.time() + 120
    while time.time() < deadline:
        time.sleep(4)
        got = httpx.get(f"{base.rstrip('/')}/mensajes", params={"hilo": thread}, headers=headers, timeout=30).json()
        messages = got if isinstance(got, list) else got.get("mensajes") or got.get("items") or []
        answers = [m for m in messages if m.get("rol") in ("assistant", "error")]
        if answers:
            text = " ".join(str(m.get("texto", "")) for m in answers)
            assert answers[-1]["rol"] == "assistant", text
            assert "Calotas" in text
            return
    pytest.fail("the deployed chat did not answer in 120 s")
```

Si `.sst/outputs.json` no trae la clave `Chat`, tomar la URL del output impreso por el deploy (`Chat: https://...`) y pasarla como `API_URL` en `scripts/e2e.sh`.

- [ ] **Step 4: Script**

```bash
#!/usr/bin/env bash
# scripts/e2e.sh — end-to-end tests against Bedrock, DynamoDB and the deployed chat (stage warroom).
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ ! -f .env ]]; then
  echo "Missing .env: copy .env.example to .env and fill in the keys" >&2
  exit 1
fi
export AWS_PROFILE="${AWS_PROFILE:-sandbox}" AWS_REGION="${AWS_REGION:-us-east-1}" RUN_E2E=1
exec uv run --env-file .env pytest core/tests/e2e -v "$@"
```

```bash
chmod +x scripts/e2e.sh
```

- [ ] **Step 5: Verify skip by default and run e2e**

Run: `uv run pytest core/tests -q`
Expected: todo en verde y los e2e salteados.

Run: `scripts/e2e.sh`
Expected: los de nivel 1 y nivel 2 pasan. Si el chat desplegado todavía corre la imagen sin la V2, redeployar (`npx sst deploy --stage warroom`) y repetir. Un fallo real del agente (un `validate` con problemas) es un hallazgo: reportarlo con el caso y los problemas, sin relajar el test.

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml core/tests/e2e scripts/e2e.sh
git commit -m "test(e2e): V1 y V2 contra Bedrock y DynamoDB, y el chat desplegado"
```

---

### Task 8: Experimentos V2 y números del día

**Files:**
- Modify: `CLAUDE.md` (tabla de resultados del 1/10)

- [ ] **Step 1: Correr los experimentos**

```bash
scripts/experiment.sh --version v2 --data mock --case 01-real-calota-aro14
scripts/experiment.sh --version v2 --data mock
scripts/experiment.sh --version current --data real --allow-real-upload
scripts/experiment.sh --version v1 --data real --allow-real-upload
scripts/experiment.sh --version v2 --data real --allow-real-upload
```

Expected: cada corrida imprime `result.format()` con los scores de corrida, incluido `missing_not_detected_total`. La V2 debe imprimir `V2 stores: dynamodb`.

- [ ] **Step 2: Tokens por producto desde Langfuse**

Para cada corrida, anotar la hora de inicio y fin y sumar el uso de las generaciones en esa ventana (no imprimir claves):

```bash
PYTHONPATH=core/src uv run --env-file .env python - <<'EOF'
import os, httpx
from datetime import datetime, timezone
start, end = "<inicio ISO>", "<fin ISO>"   # ventana de una corrida, en UTC
r = httpx.get(os.environ["LANGFUSE_BASE_URL"].rstrip("/") + "/api/public/v2/observations",
              params={"fromStartTime": start, "toStartTime": end, "type": "GENERATION", "limit": 100,
                      "fields": "core,basic,usage,model"},
              auth=(os.environ["LANGFUSE_PUBLIC_KEY"], os.environ["LANGFUSE_SECRET_KEY"]), timeout=30)
gens = [g for g in r.json().get("data", []) if g.get("name") == "BedrockConverse.achat"]
total = {k: sum((g.get("usageDetails") or {}).get(k, 0) for g in gens) for k in ("input", "output", "input_cached_tokens", "input_cache_creation")}
print(len(gens), "llamadas", total, "costo", round(sum(g.get("totalCost") or 0 for g in gens), 4))
EOF
```

Si una corrida tiene más de 100 generaciones, paginar con el parámetro `cursor` que devuelve la respuesta.

- [ ] **Step 3: Registrar en CLAUDE.md**

Agregar la tabla "Resultados del 1/10 en Langfuse (30 reales, salida esperada MOCK)" con las columnas Proceso de hoy, V1 y V2 y las filas: exactos, categoría correcta, valores inválidos, duplicados, obligatorios sin informar, precisión, recall, tokens de entrada por producto (sin caché y leídos de caché) y segundos por producto. Aclarar que la categoría de la V1 es optimista y que el `expected` es MOCK.

- [ ] **Step 4: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: resultados de la V2 en Langfuse contra el proceso de hoy y la V1"
```

---

### Task 9: El deck fiel a lo construido

**Files:**
- Modify: `docs/warroom/diapositivas.json`, `docs/presentacion-warroom.html`, `docs/presentacion-warroom.pdf`, `docs/guion-warroom-propuesto.md`

Herramientas: `python3 old/deck-tools/regenerar_deck.py` (HTML y guion; las láminas de código leen el repo y fallan si el rango o el símbolo no coinciden) y `uv run --no-project --with reportlab python old/deck-tools/exportar_pdf.py` (PDF). Editar el JSON con un script de Python (no a mano). Tipos de lámina: `divider`, `compare`, `cards`, `flow`, `table`, `decision`, `demo`, `code` (`code: {file, lines, symbol, highlight, caption}`, máximo 18 líneas), `diagram` (`diagram: {w, h, nodes, edges, caption}`, sin nodos superpuestos ni fuera del lienzo).

- [ ] **Step 1: Bloques y agenda**

- Fusionar las secciones `v2` y `v3` en una sola `v2`: título "04 · V2 · tablas y control", horario "13:15-16:15", objetivo "Resolver con las tablas lo que saben y controlar lo que decide el agente". Pasar a `v2` todas las láminas de `v3` y borrar la sección `v3`. La sección `prueba` pasa a "05 · La prueba y el camino".
- Borrar el divisor `s51` ("V3 · control.").
- `s02`: cinco bloques; el 4 dice "4 · V2 · TABLAS Y CONTROL | Las tablas en código, un agente que decide valores, validación, correcciones y caché".
- Revisar los `say` de `s01`, `s02` y del divisor `s41`, que mencionan V2 y V3 por separado.

- [ ] **Step 2: Arquitectura**

- Reemplazar el diagrama de `s52` por "La V2 por dentro." con este `diagram`:

```json
{"w": 1200, "h": 420,
 "nodes": [
  {"x": 16, "y": 180, "w": 170, "h": 84, "title": "Producto", "sub": ["MappingRequested"], "tone": "dato"},
  {"x": 216, "y": 180, "w": 170, "h": 84, "title": "check_cache", "sub": ["DynamoDB · mapping_cache", "SKU + tablas + prompt"], "tone": "codigo"},
  {"x": 416, "y": 166, "w": 200, "h": 112, "title": "resolve · código", "sub": ["categoría por tabla", "campos por tabla", "texto libre y coincidencias"], "tone": "codigo"},
  {"x": 646, "y": 166, "w": 250, "h": 112, "title": "run_agent · FunctionAgent", "sub": ["Claude Sonnet 5", "to_decide y lo no cubierto", "hasta 5 iteraciones"], "tone": "modelo"},
  {"x": 926, "y": 180, "w": 258, "h": 84, "title": "finalize · código", "sub": ["gana lo resuelto · clean()", "guarda en caché"], "tone": "codigo"},
  {"x": 646, "y": 16, "w": 250, "h": 100, "title": "Herramientas", "sub": ["lookup_corrections", "submit_listing → validate()", "los problemas vuelven al agente"], "tone": "codigo"},
  {"x": 926, "y": 16, "w": 258, "h": 84, "title": "DynamoDB · corrections", "sub": ["las carga catálogo", "scripts/correct.sh"], "tone": "dato"},
  {"x": 216, "y": 330, "w": 170, "h": 72, "title": "MappingCompleted", "sub": ["source = cache"], "tone": "dato"},
  {"x": 416, "y": 330, "w": 200, "h": 72, "title": "MappingCompleted", "sub": ["source = tables", "sin categoría o esquema"], "tone": "alerta"},
  {"x": 926, "y": 330, "w": 258, "h": 72, "title": "MappingCompleted", "sub": ["source = agent", "traza en Langfuse"], "tone": "dato"}],
 "edges": [
  {"points": [[186, 222], [216, 222]], "label": "", "dashed": false},
  {"points": [[386, 222], [416, 222]], "label": "miss", "dashed": false, "at": [401, 212]},
  {"points": [[616, 222], [646, 222]], "label": "", "dashed": false},
  {"points": [[896, 222], [926, 222]], "label": "", "dashed": false},
  {"points": [[301, 264], [301, 330]], "label": "hit", "dashed": false},
  {"points": [[516, 278], [516, 330]], "label": "sin referencia", "dashed": false},
  {"points": [[740, 166], [740, 116]], "label": "pide", "dashed": false, "at": [712, 144]},
  {"points": [[802, 116], [802, 166]], "label": "resultado", "dashed": false, "at": [846, 144]},
  {"points": [[896, 66], [926, 66]], "label": "", "dashed": false},
  {"points": [[1055, 264], [1055, 330]], "label": "", "dashed": false}],
 "caption": "Verde es código y violeta es el modelo. El código resuelve lo que saben las tablas; el agente decide valores y entrega por una herramienta que valida."}
```

- `s24` (infraestructura): el nodo DynamoDB suma la línea "corrections · mapping_cache"; el Runtime dice "map_product_v1 y map_product_v2"; el batch dice "scripts/experiment.sh → V1 / V2".
- `c05` ("La V1 por dentro.") queda como está.

- [ ] **Step 3: Código de la V2**

Sumar láminas `code` (3 minutos cada una) que lean el código final de la V2, con rangos y símbolos tomados del archivo en ese momento:
- `core/src/catalog/worklist.py`, `build_worklist`: lo que resuelve el código (resaltar el texto libre y la coincidencia exacta);
- `core/src/catalog/v2.py`, `submit_listing`: la entrega validada (resaltar el `raise` con los problemas y el `return_direct`);
- `core/src/catalog/guardrails.py`, `validate`;
- `core/src/catalog/v2.py`, los steps `check_cache` y `finalize` (la caché);
- `core/tests/e2e/test_e2e_mapping.py`, `test_v2_never_delivers_invalid_listings`.

- [ ] **Step 4: Pruebas, demos, números y decisiones**

- Nueva lámina `cards` "Cómo lo probamos.": tests unitarios (`uv run pytest core/tests -q`, sin AWS), experimentos en Langfuse (`scripts/experiment.sh --version v2 --data mock`) y tests e2e (`scripts/e2e.sh`, contra Bedrock, DynamoDB y el chat desplegado).
- `s50` (demo V2): `scripts/experiment.sh --version v2 --data mock --case 01-real-calota-aro14`; mirar `source`, los atributos resueltos por código, las entregas rechazadas por `submit_listing` en la traza y los tokens.
- `s61` (corregir y repetir): `scripts/correct.sh --category ... --attribute ... --product-value ... --value-id ... --value ...` y dos corridas: la primera usa la corrección y la segunda sale de la caché (`source = cache`).
- `c10` (demo del chat): pedir "Mapea el SKU 94701411 con la V2"; mirar que use `map_product_v2`.
- `s40` (V1): pasa de hipótesis a lo medido el 1/10: V1 sobre los 30 reales, 4 exactos, 28 categorías (optimista), 3 inválidos, 0 duplicados, recall 0,55.
- `s48` (costo): columnas V1 y V2 con los tokens por producto de la tarea 8.
- `s63` (resultados): columnas Hoy, V1 y V2 (sin V3) con los números de la tarea 8, incluida la fila de obligatorios sin informar.
- Decisiones 10 a 13 (`s45`, `s49`, `s56`, `s60`) y sus filas en `s66`/`s67`: describir la V2 tal como quedó (la tabla en código, tope de costo con la medición de la tarea 8, faltante explícito con la red final, caché por SKU + tablas + prompt en DynamoDB con invalidación al cargar una corrección).
- `s53`, `s57`: la validación es `validate`/`clean` y la memoria es DynamoDB con `scripts/correct.sh`.

- [ ] **Step 5: Revisión completa**

Recorrer las láminas una por una y dejar escrito en el reporte, por lámina, "ok" o qué se cambió. Criterios: cada comando existe y corre; cada número viene de una corrida identificada (fecha y versión); cada decisión coincide con lo construido; ninguna lámina menciona `scripts/correr.sh`, `scripts/corregir.sh`, `correr.py`, "V3" como versión separada ni el código viejo. Texto nuevo con las reglas de la skill humanizer (frases cortas, sin rayas, sin "no es X, es Y", sin remates).

- [ ] **Step 6: Regenerar y verificar**

```bash
python3 old/deck-tools/regenerar_deck.py
uv run --no-project --with reportlab python old/deck-tools/exportar_pdf.py
grep -c "—\|–" docs/guion-warroom-propuesto.md
```

Expected: genera sin errores, el PDF sale con escala mínima ≥ 0,65, y no hay rayas en el guion. Abrir el HTML (`python3 -m http.server` en `docs/`) y revisar cada diagrama y cada lámina nueva.

- [ ] **Step 7: Commit**

```bash
git add docs/warroom/diapositivas.json docs/presentacion-warroom.html docs/presentacion-warroom.pdf docs/guion-warroom-propuesto.md
git commit -m "docs(deck): bloque V2 único, arquitectura, código, pruebas y números de la V2"
```

---

## Cobertura del spec

| Requisito del spec | Tarea |
|---|---|
| Categoría y campos por tabla, texto libre y coincidencia exacta | 1 |
| `validate`, `clean`, lo resuelto gana | 2 |
| Correcciones y caché, en memoria y DynamoDB, invalidación | 3, 5 |
| Workflow `check_cache` → `resolve` → `run_agent` → `finalize`, `FunctionAgent`, `submit_listing`, `lookup_corrections`, límite de iteraciones, `source` | 4 |
| Tablas en el stack, permisos y variables del Runtime, `scripts/correct.sh` | 5 |
| Experimento `--version v2`, dos herramientas en el chat, prompt del chat | 6 |
| Tests e2e de nivel 1 y nivel 2, `scripts/e2e.sh` | 7 |
| `v2-mock` y `v2-real` en Langfuse junto a `current` y `v1`; criterio de cero inválidos, duplicados y obligatorios sin informar, recall mayor que la V1 | 8 |
| Deck: bloques, arquitectura, código, pruebas, demos, números y decisiones | 9 |
