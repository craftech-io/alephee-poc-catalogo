"""V1 · el agente responde: solo instrucciones.

Un solo paso y una sola llamada al modelo con el producto, las categorías del canal
y los atributos que espera la categoría. No usa las tablas de referencia: se espera
que falle en algunos casos, y esos fallos justifican las capas de V2 y V3.
"""

import json

from llama_index.core.base.llms.types import ChatMessage
from llama_index.core.tools import FunctionTool
from pydantic import ValidationError
from workflows import Workflow, step

from .datos import cargar_esquemas
from .eventos import MapeoDone, MapeoStart
from .llm import uso_de
from .modelos import Publicacion

NOMBRE_SALIDA = "entregar_publicacion"

INSTRUCCIONES = """\
Eres un especialista en catalogación de autopartes para marketplaces. Recibes un producto del \
catálogo de Alephee (taxonomía de Mercado Libre) y debes adaptarlo a Shopee: elegir la \
categoría de Shopee y mapear los atributos del producto a los atributos que esa categoría espera.

Reglas:
- La categoría y los URN de atributos se copian exactos de las listas que recibes. Nunca inventes un URN.
- Si el atributo del canal tiene una lista de valores, elige el valor equivalente de esa lista y usa su id. \
Si ningún valor es equivalente, no lo completes.
- Si el atributo del canal es de texto libre, usa valueId "0" y el valor del producto tal cual.
- Nunca inventes valores. Solo usas datos presentes en los atributos del producto.
- Los valores "-1", "N/A" o vacíos significan que no hay dato.
- Si un atributo obligatorio del canal no se puede completar, agrégalo a "missing" con el motivo.
- Si un atributo del producto no se puede usar, agrégalo a "rejected" con el motivo.
- Cada atributo del canal aparece una sola vez.

Entrega el resultado llamando a la herramienta entregar_publicacion."""


def _entregar(**publicacion) -> str:
    # El resultado se lee de la tool call; la herramienta nunca se ejecuta.
    return "ok"


HERRAMIENTA_SALIDA = FunctionTool.from_defaults(
    fn=_entregar,
    name=NOMBRE_SALIDA,
    description="Entrega el resultado final del mapeo del producto a la publicación del canal.",
    fn_schema=Publicacion,
)


def _contexto_canal() -> str:
    # Sin las tablas de referencia (eso es la V2): el modelo ve las categorías que tienen
    # esquema y sus atributos, y elige solo.
    esquemas = [
        {"urn": e["urn"], "name": e.get("name"),
         "attributes": [{k: a.get(k) for k in ("urn", "name", "type", "mandatory", "maxValues", "values")}
                        for a in e["attributes"]]}
        for e in cargar_esquemas().values()
    ]
    return "Categorías de Shopee disponibles y los atributos que espera cada una:\n" + json.dumps(
        esquemas, ensure_ascii=False, separators=(",", ":"))


def mensaje_producto(producto: dict) -> str:
    campos = ("sku", "name", "description", "categories", "brand", "attributes")
    return (
        _contexto_canal()
        + "\n\nProducto:\n"
        + json.dumps({k: producto.get(k) for k in campos}, ensure_ascii=False, indent=1)
    )


class MapeoV1(Workflow):
    def __init__(self, llm, **kwargs):
        # `llm` es un BedrockConverse (catalogo/llm.py) o un doble en los tests.
        super().__init__(**kwargs)
        self.llm = llm

    @step
    async def mapear(self, ev: MapeoStart) -> MapeoDone:
        respuesta = await self.llm.achat_with_tools(
            tools=[HERRAMIENTA_SALIDA],
            user_msg=mensaje_producto(ev.producto),
            chat_history=[ChatMessage(role="system", content=INSTRUCCIONES)],
            tool_required=True,
        )
        uso = uso_de(respuesta)
        llamadas = [
            ll
            for ll in self.llm.get_tool_calls_from_response(respuesta, error_on_no_tool_call=False)
            if ll.tool_name == NOMBRE_SALIDA
        ]
        if not llamadas:
            return MapeoDone(publicacion=None, uso=uso, error=f"El modelo no llamó a {NOMBRE_SALIDA}")
        try:
            publicacion = Publicacion.model_validate(llamadas[0].tool_kwargs)
        except ValidationError as exc:
            return MapeoDone(publicacion=None, uso=uso, error=f"Salida fuera de contrato: {exc.error_count()} errores")
        return MapeoDone(publicacion=publicacion.model_dump(), uso=uso)
