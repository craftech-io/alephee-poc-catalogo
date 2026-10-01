"""V3 · el agente bajo control: guardrails, memoria de correcciones y caché por SKU.

- Guardrails: cada entrega se revisa en código. Si hay problemas, el agente recibe la lista
  y tiene una ronda para corregir; lo que siga mal se descarta y los obligatorios quedan en
  `missing`. Nunca sale un `-1`, un valor fuera de lista ni un duplicado.
- Memoria: las correcciones del equipo de catálogo se consultan como una herramienta más y
  mandan sobre el criterio del modelo.
- Caché: el mismo SKU en la misma categoría se mapea una vez (40 concesionarios, un mapeo).
"""

import json

from llama_index.core.tools import FunctionTool

from . import guardrails
from .datos import id_categoria
from .eventos import MapeoDone, MapeoStart
from .memoria import Memoria
from .v2 import INSTRUCCIONES as INSTRUCCIONES_V2
from .v2 import MapeoV2
from workflows import step

INSTRUCCIONES = INSTRUCCIONES_V2 + """
- Después de resolver la categoría, llama a buscar_correcciones: las correcciones del equipo de catálogo \
mandan sobre tu criterio. Si una corrección aplica al valor del producto, úsala tal cual."""


class MapeoV3(MapeoV2):
    instrucciones = INSTRUCCIONES

    def __init__(self, llm, fuente=None, memoria: Memoria | None = None, usar_cache: bool = True, **kwargs):
        super().__init__(llm=llm, fuente=fuente, **kwargs)
        self.memoria = memoria or Memoria()
        self.usar_cache = usar_cache
        self.reintentos = 1
        self.categoria_referencia = None

        def buscar_correcciones(categoria: str) -> str:
            """Devuelve las correcciones que el equipo de catálogo cargó para una categoría de Shopee:
            para qué valor del producto, qué atributo y qué valor del canal corresponde."""
            return json.dumps(self.memoria.correcciones(categoria), ensure_ascii=False)

        self.herramientas.append(FunctionTool.from_defaults(fn=buscar_correcciones))

    def _esquema(self, publicacion: dict) -> dict[str, dict]:
        esquema = self.fuente.esquema(publicacion["category"]) if publicacion["category"] else None
        return {a["urn"]: a for a in (esquema or {}).get("attributes", [])}

    async def _al_entregar(self, publicacion: dict) -> tuple[dict | None, str | None]:
        categoria_incorrecta = publicacion["category"] != self.categoria_referencia
        publicacion = {**publicacion, "category": self.categoria_referencia}
        esquema = self._esquema(publicacion)
        problemas = guardrails.revisar(publicacion, esquema)
        if categoria_incorrecta:
            problemas.insert(0, f"La tabla fija category = {self.categoria_referencia}. Usa sus atributos.")
        if problemas and self.reintentos > 0:
            self.reintentos -= 1
            return None, "La entrega no pasó la validación. Corrige y vuelve a entregar:\n- " + "\n- ".join(problemas)
        return guardrails.limpiar(publicacion, esquema), None

    @step
    async def mapear(self, ev: MapeoStart) -> MapeoDone:
        cats = ev.producto.get("categories") or []
        clave = (ev.producto.get("sku"), id_categoria(cats[0]["urn"]) if cats else "")
        referencia = self.fuente.categoria_destino(clave[1]) if clave[1] else None
        self.categoria_referencia = referencia["urn"] if referencia else None
        self.reintentos = 1
        if not self.categoria_referencia or self.fuente.esquema(self.categoria_referencia) is None:
            return MapeoDone(publicacion={
                "category": self.categoria_referencia, "attributes": [], "rejected": [],
                "missing": [{"urn": "category", "reason": "No hay referencia o esquema de categoría disponible; requiere revisión"}],
            }, herramientas_usadas=["referencia_categoria"])
        if self.usar_cache and (guardado := self.memoria.en_cache(*clave)):
            if guardado["category"] == self.categoria_referencia and not guardrails.revisar(guardado, self._esquema(guardado)):
                return MapeoDone(publicacion=guardrails.limpiar(guardado, self._esquema(guardado)), herramientas_usadas=["cache"])
        done = await MapeoV2.mapear(self, ev)
        if self.usar_cache and done.publicacion is not None:
            self.memoria.guardar_cache(*clave, done.publicacion)
        return done
