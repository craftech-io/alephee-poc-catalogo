from types import SimpleNamespace

from llama_index.core.llms.llm import ToolSelection

from catalogo import guardrails
from catalogo.datos import cargar_atributos_canal, cargar_dataset
from catalogo.memoria import Memoria
from catalogo.v1 import NOMBRE_SALIDA
from catalogo.v3 import MapeoV3

CALOTAS = "urn:category:102529:vendor:shopee"
ESQUEMA = cargar_atributos_canal(CALOTAS)
CASO = cargar_dataset()[0]
CONDICION = "urn:attribute:101638:vendor:shopee"


def _pub(atributos, missing=()):
    return {"category": CALOTAS, "attributes": list(atributos), "missing": list(missing), "rejected": []}


def test_revisar_detecta_sin_dato_fuera_de_lista_duplicado_y_obligatorio_faltante():
    pub = _pub([
        {"urn": "urn:attribute:102293:vendor:shopee", "valueId": "0", "value": "-1", "unit": None},
        {"urn": "urn:attribute:101652:vendor:shopee", "valueId": "999", "value": "Marte", "unit": None},
        {"urn": "urn:attribute:101652:vendor:shopee", "valueId": "14710", "value": "Brasil", "unit": None},
    ])

    problemas = " | ".join(guardrails.revisar(pub, ESQUEMA))

    assert "sin dato" in problemas and "no está en la lista" in problemas and "más de una vez" in problemas
    assert f"{CONDICION} es obligatorio" in problemas


def test_limpiar_nunca_deja_salir_valores_invalidos():
    pub = _pub([
        {"urn": CONDICION, "valueId": "14703", "value": "Novo", "unit": None},
        {"urn": "urn:attribute:102293:vendor:shopee", "valueId": "0", "value": "-1", "unit": None},
    ])

    limpia = guardrails.limpiar(pub, ESQUEMA)

    assert [a["urn"] for a in limpia["attributes"]] == [CONDICION]
    assert "urn:attribute:102293:vendor:shopee" in {m["urn"] for m in limpia["missing"]}


def test_memoria_guarda_correcciones_y_vacia_la_cache(tmp_path):
    memoria = Memoria(tmp_path)
    memoria.guardar_cache("sku", "734701", _pub([]))

    memoria.corregir(CALOTAS, "urn:attribute:101730:vendor:shopee", "Centro", "14729", "Parcial")

    assert memoria.correcciones(CALOTAS)[0]["value"] == "Parcial"
    assert memoria.en_cache("sku", "734701") is None


class FakeLLM:
    def __init__(self, rondas):
        self.rondas = list(rondas)
        self.historiales = []

    async def achat_with_tools(self, **kwargs):
        self.historiales.append(list(kwargs["chat_history"]))
        return SimpleNamespace(llamadas=self.rondas.pop(0), message=SimpleNamespace(role="assistant", content=""),
                               additional_kwargs={})

    def get_tool_calls_from_response(self, respuesta, error_on_no_tool_call=True):
        return respuesta.llamadas


def _entrega(pub, id_="e1"):
    return [ToolSelection(tool_id=id_, tool_name=NOMBRE_SALIDA, tool_kwargs=pub)]


async def test_una_entrega_con_problemas_recibe_devolucion_y_se_corrige(tmp_path):
    mala = _pub([{"urn": CONDICION, "valueId": "0", "value": "-1", "unit": None}])
    buena = _pub([{"urn": CONDICION, "valueId": "14703", "value": "Novo", "unit": None},
                  {"urn": "urn:attribute:102293:vendor:shopee", "valueId": "0", "value": "94701411", "unit": None},
                  {"urn": "urn:attribute:990001:vendor:shopee", "valueId": "99102", "value": '14"', "unit": None}])
    llm = FakeLLM([_entrega(mala), _entrega(buena, "e2")])

    done = await MapeoV3(llm=llm, memoria=Memoria(tmp_path), timeout=10).run(producto=CASO["product"])

    assert "no pasó la validación" in llm.historiales[1][-1].content
    assert done.publicacion["attributes"] == buena["attributes"]


async def test_si_no_corrige_los_guardrails_limpian(tmp_path):
    mala = _pub([{"urn": CONDICION, "valueId": "0", "value": "-1", "unit": None}])
    llm = FakeLLM([_entrega(mala), _entrega(mala, "e2")])

    done = await MapeoV3(llm=llm, memoria=Memoria(tmp_path), timeout=10).run(producto=CASO["product"])

    assert done.publicacion["attributes"] == []
    assert CONDICION in {m["urn"] for m in done.publicacion["missing"]}


async def test_el_mismo_sku_sale_de_cache(tmp_path):
    memoria = Memoria(tmp_path)
    buena = _pub([{"urn": CONDICION, "valueId": "14703", "value": "Novo", "unit": None}], missing=[
        {"urn": "urn:attribute:102293:vendor:shopee", "reason": "x"}, {"urn": "urn:attribute:990001:vendor:shopee", "reason": "x"}])
    await MapeoV3(llm=FakeLLM([_entrega(buena)]), memoria=memoria, timeout=10).run(producto=CASO["product"])

    done = await MapeoV3(llm=FakeLLM([]), memoria=memoria, timeout=10).run(producto=CASO["product"])

    assert done.herramientas_usadas == ["cache"]
    assert done.publicacion["attributes"][0]["value"] == "Novo"


def test_id_valido_con_etiqueta_incorrecta_se_descarta():
    pub = _pub([{"urn": CONDICION, "valueId": "14703", "value": "Usado", "unit": None}])
    assert any("no coincide" in p for p in guardrails.revisar(pub, ESQUEMA))
    limpia = guardrails.limpiar(pub, ESQUEMA)
    assert not limpia["attributes"]
    assert CONDICION in {m["urn"] for m in limpia["missing"]}


def test_sin_categoria_se_informa_y_un_atributo_resuelto_no_queda_faltante():
    vacia = {**_pub([]), "category": None}
    assert "category" in {m["urn"] for m in guardrails.limpiar(vacia, {})["missing"]}
    pub = _pub([{"urn": CONDICION, "valueId": "14703", "value": "Novo", "unit": None}],
               missing=[{"urn": CONDICION, "reason": "sin dato"}, {"urn": "category", "reason": "sin dato"}])
    assert not {CONDICION, "category"} & {m["urn"] for m in guardrails.limpiar(pub, ESQUEMA)["missing"]}


async def test_categoria_de_tabla_prevalece_aunque_el_modelo_insista(tmp_path):
    mala = {**_pub([]), "category": "urn:category:inventada"}
    llm = FakeLLM([_entrega(mala), _entrega(mala, "e2")])
    done = await MapeoV3(llm=llm, memoria=Memoria(tmp_path), timeout=10).run(producto=CASO["product"])
    assert done.publicacion["category"] == CALOTAS
    assert "La tabla fija category" in llm.historiales[1][-1].content


async def test_sin_categoria_no_consulta_modelo(tmp_path):
    producto = {**CASO["product"], "categories": []}
    done = await MapeoV3(llm=FakeLLM([]), memoria=Memoria(tmp_path), timeout=10).run(producto=producto)
    assert done.publicacion["category"] is None
    assert done.publicacion["missing"][0]["urn"] == "category"


async def test_cache_con_categoria_incorrecta_se_recalcula(tmp_path):
    memoria = Memoria(tmp_path)
    from catalogo.datos import id_categoria
    producto = CASO["product"]
    memoria.guardar_cache(producto["sku"], id_categoria(producto["categories"][0]["urn"]),
                         {**_pub([]), "category": "urn:category:inventada"})
    llm = FakeLLM([_entrega(_pub([])), _entrega(_pub([]), "e2")])
    done = await MapeoV3(llm=llm, memoria=memoria, timeout=10).run(producto=producto)
    assert done.publicacion["category"] == CALOTAS
    assert done.herramientas_usadas != ["cache"]
