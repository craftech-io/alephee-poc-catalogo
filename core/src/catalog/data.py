"""Load the war room data: the Alephee dataset and the Shopee channel schemas.

`data/real` holds the 30 products from WarRoom.zip; `data/mock` holds 10 edge cases.
Both folders share file names except for the channel schema: the mock ships a single
category (`shopee_attributes_102529.json`), the real one all categories in the dataset.

Used by V1 (the full catalog goes into the prompt), by V2 (one category schema per product),
by the evaluation (to know each attribute's domain) and by the chat tool (to find a SKU).
"""

import json
from functools import cache
from pathlib import Path

# core/src/catalog/data.py -> repo root, where `data/` lives.
ROOT = Path(__file__).resolve().parents[3]
# Values the Alephee export uses for "no data". They are skipped, never mapped as a real value.
NO_DATA = frozenset({"-1", "N/A", ""})


def data_dir(name: str) -> Path:
    """Folder of a dataset: "real" or "mock"."""
    return ROOT / "data" / name


# Files are read once per process: a batch run asks for the same schemas for every product.
# Callers must not mutate what comes back, since every caller shares the cached object.
@cache
def _read(directory: Path, name: str) -> dict:
    return json.loads((directory / name).read_text(encoding="utf-8"))


def load_cases(directory: Path) -> list[dict]:
    """Cases of `dataset.json`: each has `id`, `product`, `expected` (MOCK) and, for real data, `actual`."""
    return _read(directory, "dataset.json")["cases"]


def _category_names(directory: Path) -> dict[str, str]:
    return {row["urn"]: row["name"] for row in _read(directory, "reference_category.json")["rows"]}


def load_schemas(directory: Path) -> dict[str, dict]:
    """Channel category urn → {urn, name, attributes}."""
    # The real export has every category of the dataset; the mock has only one file for Calotas.
    if (directory / "shopee_atributos_por_categoria.json").exists():
        schemas = _read(directory, "shopee_atributos_por_categoria.json")["categories"]
    else:
        single = _read(directory, "shopee_attributes_102529.json")
        schemas = {single["category"]["urn"]: {**single["category"], "attributes": single["attributes"]}}
    # Some schemas come without a name; take it from reference_category, or fall back to the urn.
    names = _category_names(directory)
    return {urn: {**schema, "name": schema.get("name") or names.get(urn, urn)} for urn, schema in schemas.items()}


def channel_attributes(schemas: dict[str, dict], category_urn: str | None) -> dict[str, dict]:
    """Attribute urn → definition (type, mandatory, valid values). Empty if the category has no schema."""
    return {a["urn"]: a for a in schemas.get(category_urn or "", {}).get("attributes", [])}


def find_product(sku, directories: list[Path]) -> tuple[dict, Path] | None:
    """First product with this SKU in the given folders, in order, plus the folder it came from.

    The folder matters: the caller loads the schemas and reference tables of that same dataset.
    """
    # SKUs arrive as numbers or strings with spaces (typed in the chat): compare as trimmed text.
    wanted = str(sku).strip()
    for directory in directories:
        for case in load_cases(directory):
            if str(case["product"].get("sku", "")).strip() == wanted:
                return case["product"], directory
    return None
