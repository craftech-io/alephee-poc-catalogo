"""Carga de tablas de referencia, atributos del canal y dataset de prueba.

`DATA_DIR` elige la carpeta: `data/mock` (por defecto, 10 casos inventados) o `data/real`
(los 30 productos de WarRoom.zip). Las dos tienen los mismos archivos, salvo el de atributos
del canal: el mock trae una sola categoría y el real, todas las del dataset.
"""

import json
import os
from functools import cache
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
SIN_DATO = {"-1", "N/A", ""}


def _dir_datos() -> Path:
    return Path(os.environ.get("DATA_DIR") or RAIZ / "data" / "mock")


def _leer(nombre: str) -> dict:
    return json.loads((_dir_datos() / nombre).read_text(encoding="utf-8"))


def id_categoria(urn_o_id: str) -> str:
    """'urn:category:734701' → '734701'. En la tabla real el legacyId ya viene pelado."""
    return urn_o_id.removeprefix("urn:category:").split(":", 1)[0]


def id_legacy(urn_atributo: str) -> str:
    """'urn:attribute:1673' → '1673'."""
    return urn_atributo.removeprefix("urn:attribute:").split(":", 1)[0]


@cache
def cargar_referencia_categorias() -> dict[str, dict]:
    """id de categoría legacy → fila de reference_category."""
    return {id_categoria(fila["legacyId"]): fila for fila in _leer("reference_category.json")["rows"]}


@cache
def cargar_referencia_atributos() -> dict[str, list[dict]]:
    """id de atributo legacy → filas de reference_attribute. Puede haber más de una: el
    atributo de destino depende de la categoría."""
    tabla: dict[str, list[dict]] = {}
    for fila in _leer("reference_attribute.json")["rows"]:
        tabla.setdefault(fila["legacyId"], []).append(fila)
    return tabla


@cache
def cargar_esquemas() -> dict[str, dict]:
    """urn de categoría del canal → {urn, name, attributes}."""
    if (_dir_datos() / "shopee_atributos_por_categoria.json").exists():
        return _leer("shopee_atributos_por_categoria.json")["categories"]
    datos = _leer("shopee_attributes_102529.json")
    return {datos["category"]["urn"]: {**datos["category"], "attributes": datos["attributes"]}}


def cargar_atributos_canal(categoria_urn: str | None = None) -> dict[str, dict]:
    """urn de atributo del canal → definición (tipo, obligatorio, dominio de valores).
    Sin categoría, la única del mock. Categoría sin esquema → vacío."""
    esquemas = cargar_esquemas()
    if categoria_urn is None:
        categoria_urn = next(iter(esquemas))
    return {a["urn"]: a for a in esquemas.get(categoria_urn, {}).get("attributes", [])}


def cargar_dataset() -> list[dict]:
    return _leer("dataset.json")["cases"]
