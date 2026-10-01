"""Tests del generador del deck: fragmentos de código leídos del repo y render de los tipos nuevos."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generar_presentacion as gp  # noqa: E402


@pytest.fixture
def repo(tmp_path):
    (tmp_path / "mod.py").write_text("a = 1\n\ndef revisar(x):\n    return x < 2 & True\n\nb = 3\n")
    return tmp_path


def test_fragmento_devuelve_lineas_con_numeracion_real(repo):
    f = gp.fragmento({"file": "mod.py", "lines": "3-4", "symbol": "revisar", "highlight": [4], "caption": "c"}, repo)
    assert f["inicio"] == 3
    assert f["lineas"] == ["def revisar(x):", "    return x < 2 & True"]
    assert f["highlight"] == {4}
    assert f["caption"] == "c"


def test_fragmento_falla_si_el_simbolo_no_esta_en_el_rango(repo):
    with pytest.raises(ValueError, match="revisar"):
        gp.fragmento({"file": "mod.py", "lines": "1-1", "symbol": "revisar"}, repo)


def test_fragmento_falla_si_el_rango_se_sale_del_archivo(repo):
    with pytest.raises(ValueError, match="mod.py"):
        gp.fragmento({"file": "mod.py", "lines": "5-40", "symbol": "b"}, repo)


def test_fragmento_falla_si_el_archivo_no_existe(repo):
    with pytest.raises(ValueError, match="no-existe.py"):
        gp.fragmento({"file": "no-existe.py", "lines": "1-1", "symbol": "x"}, repo)


def test_fragmento_rechaza_highlight_fuera_del_rango(repo):
    with pytest.raises(ValueError, match="highlight"):
        gp.fragmento({"file": "mod.py", "lines": "3-4", "symbol": "revisar", "highlight": [1]}, repo)


def test_fragmento_rechaza_mas_de_18_lineas(repo):
    (repo / "largo.py").write_text("x = 1\n" * 30)
    with pytest.raises(ValueError, match="18"):
        gp.fragmento({"file": "largo.py", "lines": "1-19", "symbol": "x"}, repo)
