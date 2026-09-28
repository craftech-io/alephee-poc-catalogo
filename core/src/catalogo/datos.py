"""Carga de tablas de referencia, atributos del canal y dataset de prueba.

Por defecto lee data/mock/. Cuando lleguen los datos reales, apuntar DATA_DIR a otra carpeta
con los mismos nombres de archivo.
"""

import json
import os
from functools import cache
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]


def _dir_datos() -> Path:
    return Path(os.environ.get("DATA_DIR", RAIZ / "data" / "mock"))


def _leer(nombre: str) -> dict:
    return json.loads((_dir_datos() / nombre).read_text(encoding="utf-8"))


@cache
def cargar_referencia_categorias() -> dict[str, dict]:
    """legacyId de categoría → fila de reference_category."""
    return {fila["legacyId"]: fila for fila in _leer("reference_category.json")["rows"]}


@cache
def cargar_referencia_atributos() -> dict[str, dict]:
    """legacyId de atributo → fila de reference_attribute."""
    return {fila["legacyId"]: fila for fila in _leer("reference_attribute.json")["rows"]}


@cache
def cargar_atributos_canal(categoria_urn: str = "urn:category:102529:vendor:shopee") -> dict[str, dict]:
    """urn de atributo del canal → definición (tipo, obligatorio, dominio de valores)."""
    datos = _leer("shopee_attributes_102529.json")
    if datos["category"]["urn"] != categoria_urn:
        raise KeyError(f"No hay atributos cargados para la categoría {categoria_urn}")
    return {attr["urn"]: attr for attr in datos["attributes"]}


def cargar_dataset() -> list[dict]:
    return _leer("dataset.json")["cases"]


def id_legacy(urn_atributo: str) -> str:
    """'urn:attribute:1673' → '1673'."""
    return urn_atributo.removeprefix("urn:attribute:").split(":", 1)[0]
