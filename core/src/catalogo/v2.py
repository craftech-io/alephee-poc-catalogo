"""V2 · el agente se integra: consulta las tablas y el esquema del canal con herramientas.

El prompt ya no lleva las categorías ni los atributos del canal: el agente pide solo lo
que necesita para este producto. El modelo decide dos cosas: qué valor de la lista
corresponde y qué hacer con lo que la tabla no mapea.
"""

import json

from llama_index.core.base.llms.types import CacheControl, CachePoint, ChatMessage, TextBlock
from workflows import Workflow, step

from .eventos import MapeoDone, MapeoStart
from .herramientas import FuenteArchivos, FuenteCatalogo, crear_herramientas
from .llm import uso_de
from .modelos import Publicacion
from .v1 import HERRAMIENTA_SALIDA, NOMBRE_SALIDA

MAX_RONDAS = 6

INSTRUCCIONES = """\
Eres un especialista en catalogación de autopartes para marketplaces. Recibes un producto del \
catálogo de Alephee (taxonomía de Mercado Libre) y debes adaptarlo a Shopee.

Pasos:
1. Llama a buscar_categoria con el urn de la categoría del producto. Si no hay categoría de origen \
o la tabla no la tiene, no la adivines: entrega con category null y agrega {"urn": "category"} a missing.
2. Llama a atributos_del_canal y a buscar_atributos_referencia con TODOS los ids de atributos del producto, \
para esa categoría. Puedes llamarlas en paralelo.
3. Para cada atributo del canal: si la tabla lo mapea, usa ese URN sin discutirlo; si tiene lista de valores, \
elige el valor equivalente y usa su id; si es texto libre, valueId "0" y el valor tal cual. Si la tabla no lo \
mapea pero un atributo del producto es claramente el mismo concepto (peso, garantía, cantidad, condición, \
número de pieza), complétalo igual: la tabla no está completa.
4. Entrega con entregar_publicacion.

Reglas:
- Nunca inventes URN ni valores. Los valores "-1", "N/A" o vacíos significan que no hay dato: no se publican.
- Respeta maxValues: si admite un valor, entrega uno.
- Cada atributo del canal aparece una sola vez.
- Si un atributo obligatorio no se puede completar, agrégalo a "missing" con el motivo."""


# Las descripciones reales llegan a 19.000 caracteres y viajan en cada ronda del loop.
# Para mapear atributos alcanza con el comienzo (el proceso actual ni la usa).
MAX_DESCRIPCION = 1500


def mensaje_producto(producto: dict) -> str:
    campos = ("sku", "name", "description", "categories", "brand", "attributes")
    recorte = {k: producto.get(k) for k in campos}
    recorte["description"] = (recorte.get("description") or "")[:MAX_DESCRIPCION]
    return "Producto:\n" + json.dumps(recorte, ensure_ascii=False, separators=(",", ":"))


class MapeoV2(Workflow):
    instrucciones = INSTRUCCIONES

    def __init__(self, llm, fuente: FuenteCatalogo | None = None, **kwargs):
        super().__init__(**kwargs)
        self.llm = llm
        self.fuente = fuente or FuenteArchivos()
        self.herramientas = crear_herramientas(self.fuente)

    async def _al_entregar(self, publicacion: dict) -> tuple[dict | None, str | None]:
        """Qué hacer con una entrega: (publicación final, None) o (None, devolución para el
        agente, que sigue con una ronda más). En la V2 toda entrega es final."""
        return publicacion, None

    @step
    async def mapear(self, ev: MapeoStart) -> MapeoDone:
        por_nombre = {t.metadata.name: t for t in self.herramientas}
        # El punto de caché después del producto hace que cada ronda del loop reuse
        # instrucciones + herramientas + producto en vez de volver a pagarlos.
        historial = [
            ChatMessage(role="system", content=self.instrucciones),
            ChatMessage(role="user", blocks=[TextBlock(text=mensaje_producto(ev.producto)),
                                             CachePoint(cache_control=CacheControl(type="default"))]),
        ]
        uso: dict = {}
        usadas: list[str] = []

        for ronda in range(MAX_RONDAS):
            # En la última ronda solo queda la herramienta de entrega: nunca termina sin respuesta.
            ultima = ronda == MAX_RONDAS - 1
            respuesta = await self.llm.achat_with_tools(
                tools=[HERRAMIENTA_SALIDA] if ultima else [*self.herramientas, HERRAMIENTA_SALIDA],
                user_msg=None,
                chat_history=historial,
                tool_required=True,
                allow_parallel_tool_calls=not ultima,
            )
            for clave, valor in uso_de(respuesta).items():
                uso[clave] = uso.get(clave, 0) + valor
            llamadas = self.llm.get_tool_calls_from_response(respuesta, error_on_no_tool_call=False)
            usadas += [ll.tool_name for ll in llamadas]
            if not llamadas:
                return MapeoDone(publicacion=None, uso=uso, herramientas_usadas=usadas,
                                 error="El modelo terminó sin entregar la publicación")

            devolucion = None
            salida = next((ll for ll in llamadas if ll.tool_name == NOMBRE_SALIDA), None)
            if salida is not None:
                try:
                    publicacion = Publicacion.model_validate(salida.tool_kwargs).model_dump()
                except Exception as exc:  # noqa: BLE001 — cualquier salida fuera de contrato se informa igual
                    return MapeoDone(publicacion=None, uso=uso, herramientas_usadas=usadas,
                                     error=f"Salida fuera de contrato: {exc}")
                final, devolucion = await self._al_entregar(publicacion)
                if final is not None:
                    return MapeoDone(publicacion=final, uso=uso, herramientas_usadas=usadas)

            historial.append(respuesta.message)
            for llamada in llamadas:
                herramienta = por_nombre.get(llamada.tool_name)
                if llamada.tool_name == NOMBRE_SALIDA:
                    resultado = devolucion
                elif herramienta:
                    resultado = str(await herramienta.acall(**llamada.tool_kwargs))
                else:
                    resultado = f"No existe la herramienta '{llamada.tool_name}'."
                historial.append(ChatMessage(role="tool", content=resultado,
                                             additional_kwargs={"tool_call_id": llamada.tool_id}))

        return MapeoDone(publicacion=None, uso=uso, herramientas_usadas=usadas,
                         error=f"Se agotaron las {MAX_RONDAS} rondas sin entregar")
