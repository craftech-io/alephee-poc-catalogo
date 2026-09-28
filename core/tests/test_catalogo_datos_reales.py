import os
from pathlib import Path

import pytest

from catalogo import datos
from catalogo.correr import _proceso_actual
from catalogo.evaluacion import evaluar_caso

REAL = Path(datos.RAIZ) / "data" / "real"


@pytest.fixture
def datos_reales(monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(REAL))
    for f in (datos.cargar_esquemas, datos.cargar_referencia_categorias, datos.cargar_referencia_atributos):
        f.cache_clear()
    yield
    for f in (datos.cargar_esquemas, datos.cargar_referencia_categorias, datos.cargar_referencia_atributos):
        f.cache_clear()


def test_cada_caso_real_tiene_esquema_para_su_categoria(datos_reales):
    for caso in datos.cargar_dataset():
        assert datos.cargar_atributos_canal(caso["expected"]["category"]), caso["id"]


def test_la_categoria_esperada_sale_de_la_tabla(datos_reales):
    tabla = datos.cargar_referencia_categorias()
    for caso in datos.cargar_dataset():
        legacy = datos.id_categoria(caso["product"]["categories"][0]["urn"])
        assert caso["expected"]["category"] == tabla[legacy]["urn"], caso["id"]


def test_el_proceso_actual_publica_valores_sin_dato(datos_reales):
    caso = next(c for c in datos.cargar_dataset() if c["id"] == "publicados-24579729")
    atributos = datos.cargar_atributos_canal(caso["expected"]["category"])

    resultado = evaluar_caso(_proceso_actual(caso)["publicacion"], caso["expected"], atributos)

    assert resultado.invalidos
