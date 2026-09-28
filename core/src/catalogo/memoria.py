"""Memoria de la V3: correcciones del equipo de catálogo y caché de mapeos por SKU.

Hoy es un archivo JSON en `memoria/` (fuera de git); en el deploy sería AgentCore Memory
o una tabla de Alephee. Una corrección manda sobre el criterio del modelo.
"""

import json
from datetime import date
from pathlib import Path

from .datos import RAIZ

DIR_MEMORIA = RAIZ / "memoria"


class Memoria:
    def __init__(self, carpeta: Path = DIR_MEMORIA):
        self.correcciones_archivo = carpeta / "correcciones.json"
        self.cache_archivo = carpeta / "cache_mapeos.json"

    def _leer(self, archivo: Path) -> dict | list:
        return json.loads(archivo.read_text(encoding="utf-8")) if archivo.exists() else ([] if "correcciones" in archivo.name else {})

    def _escribir(self, archivo: Path, datos) -> None:
        archivo.parent.mkdir(parents=True, exist_ok=True)
        archivo.write_text(json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8")

    def correcciones(self, categoria: str) -> list[dict]:
        return [c for c in self._leer(self.correcciones_archivo) if c["categoria"] in (categoria, "*")]

    def corregir(self, categoria: str, urn: str, valor_producto: str, value_id: str, value: str,
                 autor: str = "catálogo") -> dict:
        """Guarda que, en esa categoría, el valor del producto `valor_producto` va a `urn` = `value`."""
        correccion = {"categoria": categoria, "urn": urn, "valorProducto": valor_producto,
                      "valueId": value_id, "value": value, "autor": autor, "fecha": date.today().isoformat()}
        todas = [c for c in self._leer(self.correcciones_archivo)
                 if not (c["categoria"] == categoria and c["urn"] == urn and c["valorProducto"] == valor_producto)]
        self._escribir(self.correcciones_archivo, [*todas, correccion])
        # Una corrección puede cambiar cualquier mapeo guardado: la caché se vacía.
        self._escribir(self.cache_archivo, {})
        return correccion

    def en_cache(self, sku: str, categoria_legacy: str) -> dict | None:
        return self._leer(self.cache_archivo).get(f"{sku}|{categoria_legacy}")

    def guardar_cache(self, sku: str, categoria_legacy: str, publicacion: dict) -> None:
        cache = self._leer(self.cache_archivo)
        cache[f"{sku}|{categoria_legacy}"] = publicacion
        self._escribir(self.cache_archivo, cache)
