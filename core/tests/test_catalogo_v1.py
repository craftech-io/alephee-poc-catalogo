from types import SimpleNamespace

from llama_index.core.llms.llm import ToolSelection

from catalogo.datos import cargar_dataset
from catalogo.v1 import INSTRUCCIONES, NOMBRE_SALIDA, MapeoV1

PRODUCTO = cargar_dataset()[0]["product"]
PUBLICACION = {
    "category": "urn:category:102529:vendor:shopee",
    "attributes": [{"urn": "urn:attribute:101638:vendor:shopee", "valueId": "14703", "value": "Novo", "unit": None}],
    "missing": [],
    "rejected": [],
}


class FakeLLM:
    """Doble de BedrockConverse: devuelve las tool calls que se le indiquen."""

    def __init__(self, llamadas: list[ToolSelection]):
        self.llamadas = llamadas
        self.vistos: list[dict] = []

    async def achat_with_tools(self, **kwargs):
        self.vistos.append(kwargs)
        return SimpleNamespace(additional_kwargs={"prompt_tokens": 100, "completion_tokens": 20})

    def get_tool_calls_from_response(self, respuesta, error_on_no_tool_call=True):
        return self.llamadas


def _llamada(kwargs: dict, nombre: str = NOMBRE_SALIDA) -> ToolSelection:
    return ToolSelection(tool_id="t1", tool_name=nombre, tool_kwargs=kwargs)


async def test_devuelve_la_publicacion_de_la_tool_call():
    llm = FakeLLM([_llamada(PUBLICACION)])

    done = await MapeoV1(llm=llm, timeout=10).run(producto=PRODUCTO)

    assert done.publicacion == PUBLICACION
    assert done.error is None
    assert done.uso == {"prompt_tokens": 100, "completion_tokens": 20}
    pedido = llm.vistos[0]
    assert pedido["tool_required"] is True
    assert pedido["chat_history"][0].content == INSTRUCCIONES
    assert PRODUCTO["sku"] in pedido["user_msg"]


async def test_error_si_el_modelo_no_llama_a_la_herramienta():
    done = await MapeoV1(llm=FakeLLM([]), timeout=10).run(producto=PRODUCTO)

    assert done.publicacion is None
    assert NOMBRE_SALIDA in done.error


async def test_error_si_la_salida_no_cumple_el_contrato():
    llm = FakeLLM([_llamada({"category": None, "attributes": [{"urn": "x"}], "missing": [], "rejected": []})])

    done = await MapeoV1(llm=llm, timeout=10).run(producto=PRODUCTO)

    assert done.publicacion is None
    assert "contrato" in done.error
