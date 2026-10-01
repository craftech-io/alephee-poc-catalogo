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


def base(**extra):
    s = {"id": "s99", "section": "x", "title": "T", "kind": "cards", "lead": "", "label": "", "items": [],
         "question": "", "options": [], "answer": "", "exercise": None, "table": None, "minutes": 1,
         "notes": {"objective": "o", "say": "", "ask": "", "close": "", "transition": ""}}
    s.update(extra)
    return s


def test_render_code_escapa_y_numera(repo, monkeypatch):
    monkeypatch.setattr(gp, "RAIZ", repo)
    out = gp.content(base(kind="code", code={"file": "mod.py", "lines": "3-4", "symbol": "revisar", "highlight": [4], "caption": "Mira"}))
    assert 'data-n="3"' in out and 'data-n="4"' in out
    assert "x &lt; 2 &amp; True" in out
    assert 'class="ln hl" data-n="4"' in out
    assert "mod.py · líneas 3–4" in out
    assert '<p class="caption">Mira</p>' in out


def test_render_decision():
    out = gp.content(base(kind="decision", decision={"number": 12, "question": "¿Q?", "options": ["A · uno", "B · dos"],
                                                      "proposal": "B porque", "file": "decisiones/12-x.md"}))
    assert "Decisión 12" in out and "¿Q?" in out and "<li>A · uno</li>" in out
    assert "Propuesta para discutir" in out and "B porque" in out and "decisiones/12-x.md" in out


def test_render_demo():
    out = gp.content(base(kind="demo", demo={"command": "scripts/correr.sh --version v1", "watch": ["w1"], "fallback": "resultados/x.json"}))
    assert "scripts/correr.sh --version v1" in out and "<li>w1</li>" in out and "Respaldo: resultados/x.json" in out


def test_eyebrow_por_tipo():
    assert gp.eyebrow(base(kind="code")) == "Leer el código"
    assert gp.eyebrow(base(kind="decision")) == "Decisión · se cierra antes de seguir"
    assert gp.eyebrow(base(kind="demo")) == "Demo conducida por Gastón"


def test_guion_code_incluye_fragmento(repo, monkeypatch):
    monkeypatch.setattr(gp, "RAIZ", repo)
    lineas = gp.guion_slide(0, base(kind="code", code={"file": "mod.py", "lines": "3-4", "symbol": "revisar", "caption": "c"}), {"x": {"title": "S"}})
    texto = "\n".join(lineas)
    assert "`mod.py` líneas 3–4" in texto and "```py" in texto and "def revisar(x):" in texto and "c" in texto


def test_guion_decision_y_demo():
    sec = {"x": {"title": "S"}}
    d = "\n".join(gp.guion_slide(0, base(kind="decision", decision={"number": 3, "question": "¿Q?", "options": ["A", "B"], "proposal": "B", "file": "decisiones/03-x.md"}), sec))
    assert "**Decisión 3:** ¿Q?" in d and "1. A" in d and "**Propuesta:** B" in d and "decisiones/03-x.md" in d
    m = "\n".join(gp.guion_slide(0, base(kind="demo", demo={"command": "cmd", "watch": ["w"], "fallback": "f"}), sec))
    assert "```bash\ncmd\n```" in m and "- w" in m and "**Respaldo:** f" in m


def test_render_html_omite_secciones_sin_laminas():
    data = {"title": "T", "sections": [{"id": "x", "title": "X", "time": "", "goal": "g", "work_reserve": []},
                                       {"id": "vacia", "title": "Vacía", "time": "", "goal": "g", "work_reserve": []}],
            "slides": [base(kind="cards", items=["a"])]}
    out = gp.render_html(data)
    assert "<option" in out and "Vacía" not in out


def test_todas_las_laminas_code_del_deck_resuelven_contra_el_repo():
    # Si el código commiteado cambia y un rango queda viejo, este test lo detecta en CI.
    data = gp.cargar()
    laminas = [s for s in data["slides"] if s["kind"] == "code"]
    assert laminas, "el deck tiene que tener láminas de código"
    for s in laminas:
        gp.fragmento(s["code"], gp.RAIZ)


def test_el_constructor_reproduce_el_json_commiteado(tmp_path):
    # El JSON es la fuente del deck; el constructor es la forma cómoda de editarlo. Si divergen, este test avisa.
    import json
    import construir_diapositivas as cd  # noqa: PLC0415
    data = cd.construir()
    assert data == json.loads((gp.RAIZ / "docs/warroom/diapositivas.json").read_text())
