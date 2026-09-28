import json
from types import SimpleNamespace

from llama_index.core.llms.llm import ToolSelection

from catalogo.datos import cargar_dataset
from catalogo.herramientas import FuenteArchivos, crear_herramientas
from catalogo.v1 import NOMBRE_SALIDA
from catalogo.v2 import MAX_RONDAS, MapeoV2

CALOTAS = "urn:category:102529:vendor:shopee"
PRODUCTO = cargar_dataset()[0]["product"]
HERRAMIENTAS = {t.metadata.name: t for t in crear_herramientas(FuenteArchivos())}


async def _llamar(nombre: str, **kwargs) -> dict:
    return json.loads(str(await HERRAMIENTAS[nombre].acall(**kwargs)))


async def test_buscar_categoria_usa_la_tabla():
    assert await _llamar("buscar_categoria", categoria_legacy="urn:category:734701") == {
        "encontrada": True, "urn": CALOTAS, "name": "Calotas"}
    assert (await _llamar("buscar_categoria", categoria_legacy="urn:category:999999"))["encontrada"] is False


async def test_atributos_del_canal_trae_dominio_y_obligatorios():
    respuesta = await _llamar("atributos_del_canal", categoria=CALOTAS)
    condicion = next(a for a in respuesta["attributes"] if a["urn"] == "urn:attribute:101638:vendor:shopee")
    assert condicion["mandatory"] is True
    assert {"id": "14703", "name": "Novo"} in condicion["values"]


async def test_buscar_atributos_referencia_filtra_por_categoria():
    respuesta = await _llamar("buscar_atributos_referencia", ids_legacy=["urn:attribute:1673", "1726"], categoria=CALOTAS)
    assert respuesta["1673"]["urn"] == "urn:attribute:101638:vendor:shopee"
    assert respuesta["1726"] is None  # Material no está en la tabla mock, a propósito


class FakeLLM:
    """Doble de BedrockConverse que responde según un guion de tool calls por ronda."""

    def __init__(self, rondas: list[list[ToolSelection]]):
        self.rondas = list(rondas)
        self.historiales: list[list] = []

    async def achat_with_tools(self, **kwargs):
        self.historiales.append(list(kwargs["chat_history"]))
        llamadas = self.rondas.pop(0) if len(self.rondas) > 1 else self.rondas[0]
        return SimpleNamespace(
            llamadas=llamadas,
            message=SimpleNamespace(role="assistant", content=""),
            additional_kwargs={"prompt_tokens": 10, "completion_tokens": 2},
        )

    def get_tool_calls_from_response(self, respuesta, error_on_no_tool_call=True):
        return respuesta.llamadas


def _ll(nombre: str, **kwargs) -> ToolSelection:
    return ToolSelection(tool_id=f"id-{nombre}", tool_name=nombre, tool_kwargs=kwargs)


PUBLICACION = {"category": CALOTAS, "attributes": [], "missing": [], "rejected": []}


async def test_consulta_herramientas_y_despues_entrega():
    llm = FakeLLM([
        [_ll("buscar_categoria", categoria_legacy="urn:category:734701")],
        [_ll(NOMBRE_SALIDA, **PUBLICACION)],
    ])

    done = await MapeoV2(llm=llm, timeout=10).run(producto=PRODUCTO)

    assert done.publicacion["category"] == CALOTAS
    assert done.uso == {"prompt_tokens": 20, "completion_tokens": 4}
    resultado_tool = llm.historiales[1][-1]
    assert resultado_tool.additional_kwargs == {"tool_call_id": "id-buscar_categoria"}
    assert json.loads(resultado_tool.content)["urn"] == CALOTAS


async def test_corta_si_nunca_entrega():
    llm = FakeLLM([[_ll("buscar_categoria", categoria_legacy="urn:category:734701")]])

    done = await MapeoV2(llm=llm, timeout=10).run(producto=PRODUCTO)

    assert done.publicacion is None
    assert str(MAX_RONDAS) in done.error
    assert len(llm.historiales) == MAX_RONDAS


async def test_en_la_ultima_ronda_solo_ofrece_la_entrega():
    llm = FakeLLM([[_ll("buscar_categoria", categoria_legacy="urn:category:734701")]])
    herramientas_por_ronda = []
    original = llm.achat_with_tools

    async def espiar(**kwargs):
        herramientas_por_ronda.append([t.metadata.name for t in kwargs["tools"]])
        return await original(**kwargs)

    llm.achat_with_tools = espiar
    await MapeoV2(llm=llm, timeout=10).run(producto=PRODUCTO)

    assert herramientas_por_ronda[-1] == [NOMBRE_SALIDA]
    assert len(herramientas_por_ronda[0]) == 4
