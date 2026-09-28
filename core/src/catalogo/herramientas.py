"""Herramientas de consulta del agente (V2): las tablas de referencia y los atributos del canal.

Son código determinista: el agente las invoca, pero no razona sobre lo que devuelven
(acuerdo del 25/08). Leen a través de una `FuenteCatalogo`: hoy los archivos de data/,
mañana lo que Alephee exponga (su base, un endpoint interno). Cambiar de fuente no toca
el agente.
"""

import json
from typing import Protocol

from llama_index.core.tools import FunctionTool

from . import datos


class FuenteCatalogo(Protocol):
    def categoria_destino(self, id_legacy: str) -> dict | None: ...

    def destinos_atributo(self, id_legacy: str) -> list[dict]: ...

    def esquema(self, categoria_urn: str) -> dict | None: ...


class FuenteArchivos:
    """Lee data/mock o data/real (según DATA_DIR). Hace de API interna de Alephee."""

    def categoria_destino(self, id_legacy: str) -> dict | None:
        return datos.cargar_referencia_categorias().get(datos.id_categoria(id_legacy))

    def destinos_atributo(self, id_legacy: str) -> list[dict]:
        return datos.cargar_referencia_atributos().get(datos.id_legacy(id_legacy), [])

    def esquema(self, categoria_urn: str) -> dict | None:
        return datos.cargar_esquemas().get(categoria_urn)


def _json(valor) -> str:
    return json.dumps(valor, ensure_ascii=False, separators=(",", ":"))


def crear_herramientas(fuente: FuenteCatalogo) -> list[FunctionTool]:
    def buscar_categoria(categoria_legacy: str) -> str:
        """Devuelve la categoría de Shopee que la tabla reference_category asigna a la categoría
        legacy del producto (por ejemplo 'urn:category:734701'). Si la tabla no la tiene, lo dice."""
        fila = fuente.categoria_destino(categoria_legacy)
        if fila is None:
            return _json({"encontrada": False, "motivo": "la categoría legacy no está en reference_category"})
        return _json({"encontrada": True, "urn": fila["urn"], "name": fila["name"]})

    def atributos_del_canal(categoria: str) -> str:
        """Devuelve los atributos que Shopee espera para una categoría (urn con :vendor:shopee):
        tipo, si es obligatorio, cuántos valores admite y la lista de valores válidos."""
        esquema = fuente.esquema(categoria)
        if esquema is None:
            return _json({"encontrada": False, "motivo": f"no hay atributos cargados para {categoria}"})
        campos = ("urn", "name", "type", "mandatory", "maxValues", "values")
        return _json({"encontrada": True, "attributes": [
            {k: (v if k != "values" else [{"id": x["id"], "name": x["name"]} for x in v])
             for k, v in a.items() if k in campos}
            for a in esquema["attributes"]
        ]})

    def buscar_atributos_referencia(ids_legacy: list[str], categoria: str) -> str:
        """Para cada id de atributo del producto (por ejemplo '1673' o 'urn:attribute:1673'), devuelve
        el atributo de Shopee que la tabla reference_attribute le asigna dentro de la categoría dada.
        Solo se consideran los atributos que esa categoría tiene."""
        en_categoria = {a["urn"] for a in (fuente.esquema(categoria) or {}).get("attributes", [])}
        salida = {}
        for id_ in ids_legacy:
            destinos = [d for d in fuente.destinos_atributo(id_) if d["urn"] in en_categoria]
            salida[datos.id_legacy(id_)] = (
                {"urn": destinos[0]["urn"], "name": destinos[0]["name"]} if destinos else None
            )
        return _json(salida)

    return [FunctionTool.from_defaults(fn=f) for f in (buscar_categoria, atributos_del_canal, buscar_atributos_referencia)]
