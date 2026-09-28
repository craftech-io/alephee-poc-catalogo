import copy

from catalogo.datos import cargar_atributos_canal, cargar_dataset
from catalogo.evaluacion import evaluar_caso, resumir

ATRIBUTOS = cargar_atributos_canal()
CASOS = {c["id"]: c for c in cargar_dataset()}


def test_prediccion_igual_a_esperado_es_exacta():
    for caso in CASOS.values():
        resultado = evaluar_caso(caso["expected"], caso["expected"], ATRIBUTOS)
        assert resultado.exacto, caso["id"]


def test_valor_fuera_de_dominio_cuenta_como_invalido():
    esperado = CASOS["01-real-calota-aro14"]["expected"]
    pred = copy.deepcopy(esperado)
    pred["attributes"][0] = {"urn": "urn:attribute:101638:vendor:shopee", "valueId": "99999", "value": "Nuevo"}

    resultado = evaluar_caso(pred, esperado, ATRIBUTOS)

    assert not resultado.exacto
    assert resultado.invalidos == ["urn:attribute:101638:vendor:shopee"]
    assert resultado.fp == 1 and resultado.fn == 1


def test_urn_inexistente_en_el_canal_es_invalido():
    esperado = CASOS["02-calota-aro13-preta-completa"]["expected"]
    pred = copy.deepcopy(esperado)
    pred["attributes"].append({"urn": "urn:attribute:1673", "valueId": "0", "value": "Novo"})

    resultado = evaluar_caso(pred, esperado, ATRIBUTOS)

    assert resultado.invalidos == ["urn:attribute:1673"]
    assert resultado.fp == 1


def test_atributo_duplicado_se_detecta():
    esperado = CASOS["01-real-calota-aro14"]["expected"]
    pred = copy.deepcopy(esperado)
    pred["attributes"].append(copy.deepcopy(pred["attributes"][4]))

    resultado = evaluar_caso(pred, esperado, ATRIBUTOS)

    assert resultado.duplicados == ["urn:attribute:101730:vendor:shopee"]
    assert not resultado.exacto


def test_texto_libre_compara_el_valor():
    esperado = CASOS["02-calota-aro13-preta-completa"]["expected"]
    pred = copy.deepcopy(esperado)
    pred["attributes"][1]["value"] = "OTRO-SKU"

    resultado = evaluar_caso(pred, esperado, ATRIBUTOS)

    assert resultado.fp == 1 and resultado.fn == 1
    assert resultado.invalidos == []


def test_faltante_no_detectado_cuenta_como_error():
    esperado = CASOS["06-falta-obligatorio"]["expected"]
    pred = copy.deepcopy(esperado)
    pred["missing"] = []

    resultado = evaluar_caso(pred, esperado, ATRIBUTOS)

    assert resultado.faltantes_no_detectados == ["urn:attribute:101638:vendor:shopee"]
    assert not resultado.exacto


def test_categoria_incorrecta():
    esperado = CASOS["08-categoria-sin-referencia"]["expected"]
    pred = copy.deepcopy(esperado)
    pred["category"] = "urn:category:123:vendor:shopee"

    resultado = evaluar_caso(pred, esperado, ATRIBUTOS)

    assert not resultado.categoria_ok
    assert not resultado.exacto


def test_resumen_calcula_precision_y_recall():
    esperado = CASOS["01-real-calota-aro14"]["expected"]
    perfecto = evaluar_caso(esperado, esperado, ATRIBUTOS)
    vacio = evaluar_caso({"category": None, "attributes": [], "missing": []}, esperado, ATRIBUTOS)

    resumen = resumir([perfecto, vacio])

    assert resumen["casos"] == 2
    assert resumen["exactos"] == 1
    assert resumen["precision"] == 1.0
    assert resumen["recall"] == 0.5
