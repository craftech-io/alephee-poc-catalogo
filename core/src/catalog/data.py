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
