# Plan de implementación · presentación "cadena de decisiones"

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reescribir el deck del war room (JSON + generador + guion + PDF) como una cadena de 13 decisiones de diseño que recorre el código real del repo y conserva V1 → V2 → V3.

**Architecture:** `docs/warroom/diapositivas.json` sigue siendo la fuente única. `scripts/generar_presentacion.py` se refactoriza en funciones puras (fragmento, render por tipo, guion) con `main()` y gana tres tipos de lámina: `code` (lee el archivo fuente al generar y falla si el rango o el símbolo no existen), `decision` y `demo`. El exportador PDF aprende los mismos tipos. El contenido se escribe bloque por bloque y los 13 archivos de `decisiones/` se crean con la decisión en blanco.

**Tech Stack:** Python 3.13 estándar (sin dependencias nuevas; reportlab ya está para el PDF), pytest para el generador, `node --test` para el HTML generado.

**Spec:** `docs/warroom/diseno-presentacion.md`

## Global Constraints

- Español neutro en todo texto visible: sin voseo ("vos", "podés"), sin regionalismos.
- "Agente" o "solución", nunca "bot".
- Toda afirmación externa (AgentCore, catálogo de Bedrock, caché de prompts) lleva enlace a documentación oficial en `notes.say` del JSON; lo no verificable se escribe como "a confirmar con Juan David / Mariale".
- Datos mock siempre rotulados ("MOCK" o "esquema simulado"); cifras del 28/09 rotuladas como "anteriores a las correcciones del 28/09".
- Un fragmento de código no supera 18 líneas en pantalla.
- Ningún nombre de asistente en pantalla salvo Gastón (conduce), Rick, Maximiliano y Juan David (validan).
- Los `code` de láminas apuntan a archivos existentes del repo con `symbol` presente en el rango; el generador falla si no.
- El JSON conserva en cada lámina las claves `id, section, title, kind, lead, label, items, question, options, answer, exercise, table, notes, minutes` (el generador y el PDF las leen sin `.get`), más la clave del tipo nuevo (`code`, `decision` o `demo`).
- No se commitea ni se pushea sin pedido explícito de Gastón: cada "Commit" del plan es un punto donde se le pregunta.

## Review Focus

1. Un `code` cuyo rango es válido pero quedó desplazado por un cambio en el código muestra otro fragmento → `fragmento()` exige que `symbol` aparezca dentro del rango (test en Task 1).
2. Un `code` con `highlight` fuera del rango no debe renderizar vacío ni romper → `fragmento()` rechaza índices fuera de `[inicio, fin]` (test en Task 1).
3. Código con `<`, `>`, `&` o comillas (TypeScript, f-strings) debe verse literal en el HTML → el render escapa cada línea (test en Task 2).
4. El PDF rechaza láminas "demasiado densas" bajando la escala hasta 0,65: un fragmento de 18 líneas en monoespaciado tiene que caber → test de exportación completa en Task 4 y límite de 18 líneas en la constraint.
5. El test de navegación del HTML tenía hardcodeado "43": con el nuevo deck tiene que derivar la cantidad del JSON, si no pasa en falso o falla siempre → Task 2.

---

### Task 1: Refactor del generador en funciones + `fragmento()` para láminas `code`

**Files:**
- Modify: `scripts/generar_presentacion.py` (completo: 74 líneas)
- Test: `scripts/test_generar_presentacion.py` (crear)

**Interfaces:**
- Produces: `fragmento(code: dict, raiz: Path = RAIZ) -> dict` que devuelve `{"file": str, "inicio": int, "lineas": list[str], "highlight": set[int], "caption": str}` o lanza `ValueError` con mensaje que incluye el archivo y el motivo. `code` tiene `file`, `lines` ("a-b"), `symbol`, opcional `highlight` (lista de números de línea absolutos) y `caption`.
- Produces: `content(s) -> str`, `render_slide(i, s, total) -> str`, `render_html(data) -> str`, `render_guion(data) -> str`, `main()`. Todo lo que hoy corre al importar pasa a `main()` bajo `if __name__ == "__main__":`.

- [ ] **Step 1: Escribir los tests de `fragmento`**

```python
# scripts/test_generar_presentacion.py
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
```

- [ ] **Step 2: Correr y ver que falla**

Run: `uv run pytest scripts/test_generar_presentacion.py -v`
Expected: FAIL. Importar `generar_presentacion` ejecuta la generación completa al cargar y no existe `fragmento`.

- [ ] **Step 3: Refactorizar el generador**

Reescribir `scripts/generar_presentacion.py` con esta forma (el cuerpo de `content`, el HTML por lámina y el guion se mueven tal cual desde el script actual a las funciones indicadas; no cambiar su salida en esta tarea):

```python
"""Genera HTML y guion desde docs/warroom/diapositivas.json, sin dependencias."""
import html
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
E = html.escape
MAX_LINEAS_CODE = 18


def fragmento(code: dict, raiz: Path = RAIZ) -> dict:
    """Lee el fragmento real del repo. Falla fuerte: un deck con código viejo es peor que ninguno."""
    archivo = raiz / code["file"]
    if not archivo.is_file():
        raise ValueError(f"{code['file']}: el archivo no existe")
    lineas = archivo.read_text(encoding="utf-8").splitlines()
    inicio, fin = (int(x) for x in code["lines"].split("-"))
    if inicio < 1 or fin > len(lineas) or inicio > fin:
        raise ValueError(f"{code['file']}: el rango {code['lines']} se sale del archivo ({len(lineas)} líneas)")
    if fin - inicio + 1 > MAX_LINEAS_CODE:
        raise ValueError(f"{code['file']}: {fin - inicio + 1} líneas; el máximo en pantalla es {MAX_LINEAS_CODE}")
    seleccion = lineas[inicio - 1:fin]
    if code["symbol"] not in "\n".join(seleccion):
        raise ValueError(f"{code['file']}: el símbolo '{code['symbol']}' no está en {code['lines']}")
    highlight = set(code.get("highlight", []))
    if any(h < inicio or h > fin for h in highlight):
        raise ValueError(f"{code['file']}: highlight {sorted(highlight)} fuera de {code['lines']}")
    return {"file": code["file"], "inicio": inicio, "lineas": seleccion, "highlight": highlight,
            "caption": code.get("caption", "")}


def cargar(raiz: Path = RAIZ) -> dict:
    return json.loads((raiz / "docs/warroom/diapositivas.json").read_text())


def content(s: dict) -> str:
    ...  # cuerpo actual de content(), sin cambios


def render_slide(i: int, s: dict, data: dict) -> str:
    ...  # el f-string de `parts.append(...)` actual, con `section = {x['id']: x for x in data['sections']}[s['section']]`


def render_html(data: dict) -> str:
    ...  # arma `parts`, `options`, lee css/js y devuelve el documento


def render_guion(data: dict) -> str:
    ...  # arma `lines` como hoy y devuelve '\n'.join(lines)


def main() -> None:
    data = cargar()
    (RAIZ / "docs/presentacion-warroom.html").write_text(render_html(data))
    (RAIZ / "docs/guion-warroom-propuesto.md").write_text(render_guion(data))
    print(f"Generados HTML y guion de {len(data['slides'])} diapositivas.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Correr los tests y el generador**

Run: `uv run pytest scripts/test_generar_presentacion.py -v && python3 scripts/generar_presentacion.py && git diff --stat docs/presentacion-warroom.html docs/guion-warroom-propuesto.md`
Expected: 6 PASS; el generador imprime "Generados HTML y guion de 43 diapositivas."; `git diff --stat` no muestra cambios en los dos archivos generados (el refactor no altera la salida).

- [ ] **Step 5: Commit (preguntar a Gastón)**

```bash
git add scripts/generar_presentacion.py scripts/test_generar_presentacion.py
git commit -m "refactor(deck): generador en funciones + fragmento() para láminas de código"
```

---

### Task 2: Render HTML de `code`, `decision` y `demo` + CSS + test del HTML

**Files:**
- Modify: `scripts/generar_presentacion.py` (`content`, `render_slide`)
- Modify: `scripts/warroom.css` (agregar al final, antes del bloque `/* Las clases de componentes... */`)
- Modify: `scripts/warroom.test.mjs:12-24,55-66`
- Test: `scripts/test_generar_presentacion.py`

**Interfaces:**
- Consumes: `fragmento()` de Task 1.
- Produces: en el HTML, `section.slide--code` contiene `<figure class="code"><figcaption>ruta · líneas a–b</figcaption><pre><code><span class="ln" data-n="12">…</span>…</code></pre><p class="caption">…</p></figure>`; las líneas resaltadas llevan `class="ln hl"`. `section.slide--decision` contiene `<div class="decision"><span class="d-num">Decisión 12</span><p class="d-question">…</p><ol class="d-options"><li>…</li></ol><details class="answer"><summary>Propuesta para discutir</summary><p>…</p></details><p class="d-file">decisiones/12-….md</p></div>`. `section.slide--demo` contiene `<div class="demo"><pre class="cmd"><code>…</code></pre><ul class="watch"><li>…</li></ul><p class="fallback">Respaldo: …</p></div>`.
- El eyebrow por tipo: `code` → "Leer el código", `decision` → "Decisión · se cierra antes de seguir", `demo` → "Demo conducida por Gastón".

- [ ] **Step 1: Tests del render**

Agregar a `scripts/test_generar_presentacion.py`:

```python
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
    assert "<p class=\"caption\">Mira</p>" in out


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
```

- [ ] **Step 2: Correr y ver que falla**

Run: `uv run pytest scripts/test_generar_presentacion.py -v`
Expected: los 4 nuevos FAIL (`content` devuelve '' para kinds desconocidos; `eyebrow` no existe).

- [ ] **Step 3: Implementar**

En `generar_presentacion.py`:

```python
EYEBROWS = {"quiz": "Tu turno · elegí y justificá", "exercise": "Práctica en parejas", "example": "Ejemplo paso a paso",
            "demo": "Demo conducida por Gastón", "code": "Leer el código",
            "decision": "Decisión · se cierra antes de seguir"}


def eyebrow(s: dict) -> str:
    return EYEBROWS.get(s["kind"], "Construir · comprobar · decidir")


def _code(s: dict) -> str:
    f = fragmento(s["code"], RAIZ)
    lineas = "".join(
        f'<span class="ln{" hl" if n in f["highlight"] else ""}" data-n="{n}">{E(l) or " "}</span>\n'
        for n, l in enumerate(f["lineas"], start=f["inicio"]))
    fin = f["inicio"] + len(f["lineas"]) - 1
    return (f'<figure class="code"><figcaption>{E(f["file"])} · líneas {f["inicio"]}–{fin}</figcaption>'
            f'<pre><code>{lineas}</code></pre>'
            + (f'<p class="caption">{E(f["caption"])}</p>' if f["caption"] else "") + "</figure>")


def _decision(s: dict) -> str:
    d = s["decision"]
    return (f'<div class="decision"><span class="d-num">Decisión {d["number"]}</span><p class="d-question">{E(d["question"])}</p>'
            '<ol class="d-options">' + "".join(f"<li>{E(o)}</li>" for o in d["options"]) + "</ol>"
            f'<details class="answer"><summary>Propuesta para discutir</summary><p>{E(d["proposal"])}</p></details>'
            f'<p class="d-file">{E(d["file"])}</p></div>')


def _demo(s: dict) -> str:
    d = s["demo"]
    return (f'<div class="demo"><pre class="cmd"><code>{E(d["command"])}</code></pre><ul class="watch">'
            + "".join(f"<li>{E(w)}</li>" for w in d["watch"]) + "</ul>"
            + (f'<p class="fallback">Respaldo: {E(d["fallback"])}</p>' if d.get("fallback") else "") + "</div>")
```

Al inicio de `content(s)`: `if s["kind"] == "code": return _code(s)`, ídem `decision` y `demo`. En `render_slide`, reemplazar el diccionario inline del eyebrow por `eyebrow(s)` (manteniendo `section["goal"]` para `divider`).

En `warroom.css`, agregar antes del comentario final:

```css
.code{margin:0;background:#07121b;border:1px solid var(--line);border-radius:12px;overflow:hidden}.code figcaption{font:14px ui-monospace,monospace;color:var(--accent);padding:10px 18px;border-bottom:1px solid var(--line);letter-spacing:.5px}.code pre{margin:0;padding:14px 0;overflow-x:auto;font:clamp(14px,1.25vw,19px)/1.5 ui-monospace,Menlo,monospace}.code code{display:block}.ln{display:block;padding:0 18px 0 64px;position:relative;white-space:pre}.ln::before{content:attr(data-n);position:absolute;left:0;width:48px;text-align:right;color:#5b7488}.ln.hl{background:#1d4a40;box-shadow:inset 4px 0 0 var(--accent)}.code .caption{margin:0;padding:12px 18px;font-size:18px;color:#d2e2eb;border-top:1px solid var(--line)}.decision{display:grid;gap:14px}.d-num{color:var(--accent);font-size:15px;letter-spacing:1px;text-transform:uppercase}.d-question{font-size:clamp(22px,2.3vw,32px);line-height:1.3;margin:0}.d-options{margin:0;padding-left:0;list-style:none;display:grid;gap:10px}.d-options li{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px 18px;font-size:clamp(18px,1.8vw,25px);line-height:1.35}.d-file{font:15px ui-monospace,monospace;color:var(--muted);margin:0}.demo .cmd{background:#07121b;border:1px solid var(--line);border-radius:10px;padding:16px 20px;font:clamp(16px,1.6vw,23px)/1.4 ui-monospace,monospace;overflow-x:auto;color:var(--accent)}.watch{list-style:none;padding:0;margin:16px 0 0}.watch li{font-size:clamp(19px,2vw,27px);line-height:1.35;margin:10px 0;padding-left:18px;border-left:3px solid var(--accent)}.fallback{color:var(--muted);font-size:16px}@media print{.code,.demo .cmd{background:#edf5f8;color:#152b3b;border-color:#c5d3dc}.code pre{font-size:12px}.ln::before{color:#6e8597}.ln.hl{background:#dff3ec}.d-options li{background:#edf5f8;color:#152b3b;font-size:17px}.watch li{font-size:17px}}
```

En `warroom.test.mjs`: importar el JSON y derivar la cuenta.

```js
const data = JSON.parse(readFileSync(new URL('../docs/warroom/diapositivas.json', import.meta.url), 'utf8'));
const TOTAL = data.slides.length;
const id = n => `s${String(n).padStart(2, '0')}`;
```

Reemplazar `assert.equal(tags.length, 43)` por `assert.equal(tags.length, TOTAL)`; en el test de recorrido usar `TOTAL` y `id(n+1)`, y al final `assert.deepEqual(visible(p), [id(TOTAL-1)])`. En el test de selección de sección, reemplazar `#s28`/`'38'`/`['s39']` por valores derivados: `const second = tags.findIndex(t => attrs(t)['data-section'] !== attrs(tags[0])['data-section']);` y navegar a `id(second+1)`; `section-select.value = String(second)` → visible `[id(second+1)]`. Agregar un test:

```js
test('las láminas de código, decisión y demo existen y están escapadas', () => {
  const kinds = new Set(data.slides.map(s => s.kind));
  for (const k of ['code', 'decision', 'demo']) assert.ok(kinds.has(k), k);
  assert.ok(html.includes('class="ln" data-n="'));
  assert.doesNotMatch(html, /<code>[^<]*<(?!\/code|span|\/span)/);
});
```

(Este último test queda en rojo hasta que el JSON tenga los tipos nuevos, Task 5; marcarlo con `{ todo: true }` hasta entonces y quitar el `todo` en Task 5.)

- [ ] **Step 4: Correr tests**

Run: `uv run pytest scripts/test_generar_presentacion.py -v && python3 scripts/generar_presentacion.py && node --test scripts/warroom.test.mjs`
Expected: pytest 10 PASS; node: todos PASS salvo el `todo`.

- [ ] **Step 5: Commit (preguntar a Gastón)**

```bash
git add scripts/generar_presentacion.py scripts/warroom.css scripts/warroom.test.mjs scripts/test_generar_presentacion.py
git commit -m "feat(deck): láminas de código, decisión y demo"
```

---

### Task 3: Guion con los tipos nuevos

**Files:**
- Modify: `scripts/generar_presentacion.py` (`render_guion`)
- Test: `scripts/test_generar_presentacion.py`

**Interfaces:**
- Produces: `guion_slide(i, s, secciones) -> list[str]` (las líneas markdown de una lámina) usado por `render_guion`. Para `code` emite un bloque ```` ```<ext> ```` con la ruta y las líneas como título; para `decision` emite "**Decisión N:** pregunta", las opciones numeradas, "**Propuesta:**" y "**Archivo:**"; para `demo` emite el comando en bloque `bash`, "**Mirar:**" con viñetas y "**Respaldo:**".

- [ ] **Step 1: Tests**

```python
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
```

- [ ] **Step 2: Correr y ver que falla**

Run: `uv run pytest scripts/test_generar_presentacion.py -k guion -v`
Expected: FAIL, `guion_slide` no existe.

- [ ] **Step 3: Implementar**

Extraer del bucle actual de `render_guion` el cuerpo por lámina a `guion_slide(i, s, secciones)` (devuelve la lista de líneas que hoy se hace con `lines += [...]`), y agregar al final de esa función:

```python
    if s["kind"] == "code":
        f = fragmento(s["code"], RAIZ)
        ext = Path(f["file"]).suffix.lstrip(".") or "text"
        fin = f["inicio"] + len(f["lineas"]) - 1
        lines += [f'**Código:** `{f["file"]}` líneas {f["inicio"]}–{fin}', '', f'```{ext}', *f["lineas"], '```', '']
        if f["caption"]: lines += [f["caption"], '']
    if s["kind"] == "decision":
        d = s["decision"]
        lines += [f'**Decisión {d["number"]}:** {d["question"]}', ''] + [f'{j+1}. {o}' for j, o in enumerate(d["options"])] + ['', f'**Propuesta:** {d["proposal"]}', '', f'**Archivo:** `{d["file"]}`', '']
    if s["kind"] == "demo":
        d = s["demo"]
        lines += ['```bash', d["command"], '```', '', '**Mirar:**', ''] + [f'- {w}' for w in d["watch"]] + ['']
        if d.get("fallback"): lines += [f'**Respaldo:** {d["fallback"]}', '']
```

- [ ] **Step 4: Correr tests**

Run: `uv run pytest scripts/test_generar_presentacion.py -v`
Expected: 12 PASS.

- [ ] **Step 5: Commit (preguntar a Gastón)**

```bash
git add scripts/generar_presentacion.py scripts/test_generar_presentacion.py
git commit -m "feat(deck): guion con código, decisiones y demos"
```

---

### Task 4: PDF con los tipos nuevos

**Files:**
- Modify: `scripts/exportar_presentacion_pdf.py:30-58` (`make_blocks`) y la lectura del JSON
- Test: comando de exportación completo (no hay test unitario: reportlab dibuja; se valida que exporte sin `ValueError`)

**Interfaces:**
- Consumes: `fragmento` de `generar_presentacion` (importarlo: `sys.path.insert(0, str(Path(__file__).parent)); from generar_presentacion import fragmento`).

- [ ] **Step 1: Agregar fuente monoespaciada y render**

Después del registro de fuentes, registrar `Menlo.ttc`/`Courier New.ttf` si existen, si no `DejaVuSansMono.ttf`:

```python
mono=next((p for p in [fontdir/'Courier New.ttf', Path('/System/Library/Fonts/Menlo.ttc'), Path('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf')] if p.exists()), None)
if mono: pdfmetrics.registerFont(TTFont('Mono',str(mono)))
MONO='Mono' if mono else 'Deck'
```

En `make_blocks`, después de `add(s['label'],...)`:

```python
    if s['kind']=='code':
        f=fragmento(s['code'],ROOT)
        fin=f['inicio']+len(f['lineas'])-1
        add(f"{f['file']} · líneas {f['inicio']}–{fin}",11,ACCENT,gap=8)
        for n,l in enumerate(f['lineas'],start=f['inicio']):
            b.append((Paragraph(f"<font color='#5b7488'>{n:>4}</font>  {escape(l).replace(' ','&nbsp;')}",ParagraphStyle('c',fontName=MONO,fontSize=11*k,leading=14*k,textColor=ACCENT if n in f['highlight'] else INK)),0))
        if f['caption']:add(f['caption'],15,MUTED,gap=8)
    if s['kind']=='decision':
        d=s['decision'];add(f"DECISIÓN {d['number']}",12,ACCENT,gap=8);add(d['question'],22,INK,True,gap=12)
        for o in d['options']:add(o,17,gap=8)
        add('PROPUESTA · '+d['proposal'],14,ACCENT,gap=8);add(d['file'],11,MUTED,gap=0)
    if s['kind']=='demo':
        d=s['demo'];b.append((Paragraph(escape(d['command']),ParagraphStyle('m',fontName=MONO,fontSize=14*k,leading=18*k,textColor=ACCENT)),14*k))
        for w in d['watch']:add('•  '+w,18,gap=8)
        if d.get('fallback'):add('Respaldo · '+d['fallback'],13,MUTED,gap=0)
```

Cambiar el pie "PDF estático · las respuestas se incluyen; usar HTML para las interacciones" por "PDF estático · las propuestas de decisión se incluyen; usar HTML para las notas".

- [ ] **Step 2: Exportar con el JSON actual (sin tipos nuevos)**

Run: `uv run python scripts/exportar_presentacion_pdf.py`
Expected: "PDF: 43 páginas; escala mínima …" sin error (regresión). La prueba con los tipos nuevos se repite en Task 11.

- [ ] **Step 3: Commit (preguntar a Gastón)**

```bash
git add scripts/exportar_presentacion_pdf.py
git commit -m "feat(deck): PDF con código, decisiones y demos"
```

---

### Task 5: Fuentes externas para las láminas de AgentCore, Bedrock y caché

**Files:**
- Create: `docs/warroom/fuentes.md`

Antes de escribir el bloque 2 hay que tener las citas. Consultar con WebFetch (o el MCP `aws___search_documentation`) y anotar en `fuentes.md` **la URL exacta que respondió, la fecha y la frase que respalda cada afirmación**. Si una afirmación no se puede respaldar, se anota "sin fuente → a confirmar con Juan David" y la lámina la escribe así.

- [ ] **Step 1: Verificar y anotar estas afirmaciones**

| Afirmación de la lámina | Dónde buscar |
|---|---|
| AgentCore Runtime ejecuta agentes en contenedores propios (BYOC) con contrato `/ping` y `/invocations` en el puerto 8080, imagen ARM64 | Guía de AgentCore Runtime, "service contract" |
| AgentCore ofrece Identity, Memory, Gateway, Observability como servicios separados | Página "What is Amazon Bedrock AgentCore" |
| Modelo de precios de AgentCore Runtime (por consumo de CPU/memoria, sin costo en reposo) | Página de precios de AgentCore |
| Bedrock soporta prompt caching en Converse para los modelos Claude listados, con `cachePoint` | Guía de Bedrock, "Prompt caching" |
| Inference profiles `us.` y `global.`: qué son y por qué el ID sin prefijo da `ValidationException` | Guía de Bedrock, "Inference profiles" |
| Familias de modelos disponibles en Bedrock al 30/09/2026 (Anthropic, Amazon Nova, Meta, Mistral, …) | Guía de Bedrock, "Supported foundation models" |
| OpenAI cachea el prefijo idéntico de prompts ≥ 1024 tokens | https://platform.openai.com/docs/guides/prompt-caching |
| Autenticación de la API v2 de Alephee por `API_KEY` en la URL; rate limit por minuto con 429 | https://developers.alephee.com/v2/introduction/using-the-api/authentication y /usage-limiting/rate-limiting |

- [ ] **Step 2: Formato de `fuentes.md`**

```markdown
# Fuentes de la presentación (verificadas el 30/09/2026)

| # | Afirmación | Fuente | Cita textual |
|---|---|---|---|
| F1 | … | [título](url) | "…" |
```

Las láminas referencian `F1`, `F2`… en `notes.say` junto con el enlace.

- [ ] **Step 3: Commit (preguntar a Gastón)**

```bash
git add docs/warroom/fuentes.md
git commit -m "docs(deck): fuentes verificadas para AgentCore, Bedrock y caché"
```

---

### Task 6: JSON · secciones nuevas + Bloque 1 (Punto de partida)

**Files:**
- Modify: `docs/warroom/diapositivas.json` (reescritura completa; se conserva `title`; `date` = "2026-10-01")
- Modify: `scripts/warroom.test.mjs` (quitar el `todo` del test de tipos nuevos)

**Interfaces:**
- Produces: `sections` con ids `partida`, `diseno`, `v1`, `v2`, `v3`, `prueba` y campos `title`, `time`, `goal`, `work_reserve` (lista de `[texto, minutos]`).

- [ ] **Step 1: Escribir `sections`**

```json
[
 {"id":"partida","title":"01 · Punto de partida","time":"09:00–09:30","goal":"Ver el error de hoy y acordar qué construimos","work_reserve":[["Dolores del equipo y preguntas",10]]},
 {"id":"diseno","title":"02 · Diseñar el agente","time":"09:30–11:15","goal":"Tomar las decisiones que definen la V1","work_reserve":[["Pizarra: tipos de aplicación y dónde corre",15],["Pausa 11:00",15]]},
 {"id":"v1","title":"03 · V1 · el agente responde","time":"11:15–12:30","goal":"Construir, correr y leer la primera versión","work_reserve":[["Corridas sobre otros casos",25]]},
 {"id":"v2","title":"04 · V2 · herramientas","time":"13:15–14:45","goal":"Decidir qué resuelve la tabla y conectarla","work_reserve":[["Corrida del lote y lectura",25]]},
 {"id":"v3","title":"05 · V3 · control","time":"15:00–16:15","goal":"Decidir qué pasa cuando el agente no sabe","work_reserve":[["Corrida del lote con V3",20]]},
 {"id":"prueba","title":"06 · La prueba y el camino","time":"16:15–17:00","goal":"Medir contra el criterio y repartir lo que sigue","work_reserve":[["Documentar decisiones y responsables",15]]}
]
```

- [ ] **Step 2: Láminas del bloque 1** (ids `s01`…; todas con las 14 claves base; `kind` indicado)

| id | kind | title | Contenido en pantalla | notes.objective |
|---|---|---|---|---|
| s01 | divider | "Un agente que mapea el catálogo a Shopee, decidido paso a paso." | lead: "War Room · Alephee × Craftech × AWS · 1/10/2026" | Qué tenemos a las 17:00: agente en local, método repetible, 13 decisiones documentadas |
| s02 | cards | "Hoy: dos llamadas, un merge y un presupuesto que se agota." | items: "Categoría: tabla y, si no alcanza, el modelo elige", "Atributos: dos llamadas en paralelo y merge por código", "USD 350/mes: cuando se agota, se publica sin atributos" | El proceso actual, sin juzgarlo |
| s03 | code | "Así se pide hoy la categoría." | code: `{"file":"inputs/prompts-actuales/index.ts","lines":"4-21","symbol":"categoryPrompt","highlight":[20,21],"caption":"Reglas correctas, pero JSON pedido en el texto y la lista completa de categorías en cada llamada."}` | Leer juntos el prompt actual; señalar lo que se conserva |
| s04 | table | "Lo que Shopee rechazó y lo que aceptó mal." | table headers: "Caso","Qué salió","Qué pasó"; rows: ["88904447","Código OEM = ABS Plastic","Rechazado: valor no pertenece al atributo"],["24581199","Quantity 10 veces","Rechazado: solo admite un valor"],["9 de 30","Valor -1 publicado","Aceptado por Shopee"],["98550368","14 de 15 URN sin sufijo","Aceptado por Shopee"] | Errores reales del dataset, con el label "Datos reales · WarRoom.zip 24/09" |
| s05 | flow | "Seis bloques: cada decisión se compila en una versión." | items: "Punto de partida","Diseñar","V1 responde","V2 herramientas","V3 control","La prueba" | Agenda con pausas en `notes.say` |
| s06 | decision | "¿Qué hace y qué no hace?" | decision: number 1, question "¿Qué alcance tiene el agente del war room?", options ["A · Un canal (Shopee) y una familia de productos: categoría + atributos","B · Todos los canales conectados","C · También título, descripción y marca"], proposal "A. Un canal y una familia alcanzan para decidir el método; los otros prompts (marca, título) son generación libre, no mapeo, y quedan fuera.", file "decisiones/01-alcance.md" | D1 |
| s07 | cards | "Entra un producto. Sale una propuesta de publicación." | items: "Entrada: producto de Alephee (SKU, nombre, descripción, categoría legacy, atributos)","Salida: categoría de Shopee + atributos con URN, valueId y valor","Más dos listas: `missing` (obligatorios sin dato) y `rejected` (atributos descartados con motivo)" | Contrato en palabras antes del código |
| s08 | code | "El contrato, en código." | code: `{"file":"core/src/catalogo/modelos.py","lines":"20-37","symbol":"class Publicacion","highlight":[34,36,37],"caption":"extra=\"forbid\": nada que no esté en el contrato pasa."}` | Pydantic como contrato |
| s09 | decision | "¿Qué recibe y qué entrega?" | number 2, question "¿Cómo se informa lo que no se pudo mapear?", options ["A · No se informa: se publica lo que hay (hoy)","B · `missing` y `rejected` con motivo, en la misma salida","C · Un archivo de log aparte"], proposal "B. El faltante viaja con la publicación: quien revisa ve el producto y el motivo juntos.", file "decisiones/02-contrato.md" | D2 |

`minutes`: dividers 1, cards/table/flow 3, code 4, decision 4.

- [ ] **Step 3: Generar y testear**

Run: `python3 scripts/generar_presentacion.py && node --test scripts/warroom.test.mjs`
Expected: generador OK (los `code` resuelven); todos los tests de node PASS incluido el de tipos nuevos (quitar `{ todo: true }`).

- [ ] **Step 4: Commit (preguntar a Gastón)**

```bash
git add docs/warroom/diapositivas.json scripts/warroom.test.mjs docs/presentacion-warroom.html docs/guion-warroom-propuesto.md
git commit -m "feat(deck): secciones nuevas y bloque 1 · punto de partida"
```

---

### Task 7: JSON · Bloque 2 (Diseñar el agente)

**Files:**
- Modify: `docs/warroom/diapositivas.json`

Láminas (continuar numeración; `section: "diseno"`):

| id | kind | title | Contenido | Decisión |
|---|---|---|---|---|
| s10 | divider | "Diseñar antes de escribir." | lead "Siete decisiones que definen la V1" | |
| s11 | compare | "Cuatro formas de usar un modelo." | items: "SINGLE PROMPT \| Una llamada, una respuesta. Barato, fácil de evaluar, no consulta nada", "WORKFLOW \| Pasos fijos en código, el modelo en uno o dos. Predecible", "AGENTE \| El modelo decide qué herramienta pedir y cuándo entregar, dentro de un límite", "MULTIAGENTE \| Varios agentes con roles. Solo si un agente no alcanza" | |
| s12 | code | "Las tres versiones conviven en el mismo runner." | `{"file":"core/src/catalogo/correr.py","lines":"24-27","symbol":"_versiones","caption":"Cada versión es un Workflow que recibe MapeoStart y devuelve MapeoDone. Se comparan sobre el mismo dataset."}` | |
| s13 | decision | "¿Single prompt o agente?" | number 3, options ["A · Empezar con single prompt (V1) y agregar herramientas solo cuando un fallo lo justifique","B · Agente con herramientas desde el inicio","C · Workflow determinista sin modelo"], proposal "A. V1 muestra qué resuelve el modelo solo y qué no; cada fallo justifica la capa siguiente. C no alcanza: elegir el valor de lista equivalente necesita interpretación.", file "decisiones/03-tipo-de-aplicacion.md" | D3 |
| s14 | flow | "Un prompt tiene cinco partes." | items: "Rol: quién es","Tarea: qué hace con qué entrada","Reglas: qué nunca hace","Formato: cómo entrega","Cuando falta dato: qué hace" | |
| s15 | code | "El prompt de la V1." | `{"file":"core/src/catalogo/v1.py","lines":"22-39","symbol":"INSTRUCCIONES","highlight":[30,33,34],"caption":"Negativas explícitas (nunca inventes) y qué hacer cuando falta (missing con motivo). Comparar con el prompt actual de s03."}` | |
| s16 | cards | "Buenas prácticas que cambian el resultado." | items: "Lo estático primero, lo variable al final: habilita la caché de prompt","Salida estructurada por esquema, no JSON pedido en el texto","Decir qué hacer cuando no sabe, no solo qué hacer" | notes.say cita F7 (OpenAI caché) y la caché de Bedrock (F4) |
| s17 | code | "La salida es una herramienta con esquema." | `{"file":"core/src/catalogo/v1.py","lines":"41-51","symbol":"HERRAMIENTA_SALIDA","highlight":[50],"caption":"fn_schema=Publicacion: el modelo solo puede entregar algo que cumpla el contrato."}` | |
| s18 | decision | "¿Cómo garantizamos el formato?" | number 4, options ["A · Pedir JSON en el texto y parsear (hoy)","B · Tool con esquema Pydantic: la entrega es una llamada tipada","C · Post-procesar con regex"], proposal "B. El formato deja de ser una regla del prompt y pasa a ser un contrato que el modelo no puede violar.", file "decisiones/04-salida-estructurada.md" | D4 |
| s19 | compare | "Dónde corre: AgentCore o contenedor propio." | items: "AGENTCORE RESUELVE \| Runtime gestionado, identidad, memoria, gateway de herramientas, observabilidad (F1, F2)", "DUDAS \| Arranque en frío, costo por sesión, batch largo vs. chat, región disponible (F3)", "ALTERNATIVA \| Contenedor o Lambda propio: más control, más trabajo de operación" | notes.say con enlaces de `fuentes.md` |
| s20 | code | "El contrato con AgentCore son dos rutas." | `{"file":"core/server.py","lines":"194-199","symbol":"invocations","caption":"GET /ping y POST /invocations en el puerto 8080. El agente no sabe dónde corre."}` | |
| s21 | code | "La infraestructura declara el Runtime." | `{"file":"infra/sst/runtime.ts","lines":"389-406","symbol":"bedrockagentcore.Runtime","highlight":[402,405],"caption":"Imagen ARM64 por digest, red pública, rol propio. Se despliega con SST."}` | |
| s22 | decision | "¿Dónde corre?" | number 5, options ["A · Hoy local; el chat en AgentCore; el batch como proceso de Alephee","B · Todo en AgentCore desde el inicio","C · Todo en la infraestructura actual de Alephee"], proposal "A. Hoy se construye y mide en local. El chat de demo va a AgentCore; el batch es cómo Alephee lo usaría en producción, y dónde corre se decide con el camino a producción.", file "decisiones/05-donde-corre.md" | D5 |
| s23 | cards | "Elegir el modelo: qué pesa en este caso." | items: "Seguir reglas y usar herramientas sin inventar: lo que más falla hoy","Costo por token con caché de prompt: presupuesto de USD 350/mes","Latencia: no es restricción (batch de 13 s hoy)","Disponible en la región y la cuenta" | |
| s24 | table | "Qué hay en Bedrock." | headers "Familia","Proveedor","Notas"; filas según F6 (completar con lo verificado; si la lista no se puede verificar al 30/09, label "Lista a confirmar con Juan David") | |
| s25 | code | "El único módulo que sabe de Bedrock." | `{"file":"core/src/catalogo/llm.py","lines":"7-21","symbol":"crear_llm","highlight":[9,18,19],"caption":"Inference profile us.: sin prefijo no hay throughput on-demand (F5). Caché de system y tools activada."}` | |
| s26 | decision | "¿Qué modelo?" | number 6, options ["A · Claude Sonnet 5 en Bedrock, vía Converse","B · Un modelo más chico y barato (Haiku 4.5) y medir","C · Seguir con OpenAI y reordenar el prompt"], proposal "A para construir; B queda como prueba pendiente sobre el mismo dataset. C mejora costo pero no resuelve herramientas ni contrato.", file "decisiones/06-modelo.md" | D6 |
| s27 | cards | "Stack y harness." | items: "Python + LlamaIndex Workflows: pasos, eventos y herramientas ya resueltos","BedrockConverse: tool calling y caché sin código propio","Harness de desarrollo: propone cambios; Gastón revisa y corre los tests" | |
| s28 | code | "Un Workflow de un paso." | `{"file":"core/src/catalogo/v1.py","lines":"76-82","symbol":"class MapeoV1","caption":"El LLM se inyecta: en tests es un doble, en producción Bedrock."}` | |
| s29 | decision | "¿Con qué lo construimos?" | number 7, options ["A · Python + LlamaIndex Workflows + BedrockConverse","B · Llamadas directas al SDK, sin framework (como hoy)","C · Strands / otro framework de agentes"], proposal "A. Es el stack del template que Craftech ya opera; el workflow no conoce Bedrock y cada paso se prueba con dobles.", file "decisiones/07-stack.md" | D7 |
| s30 | cards | "¿Cuándo está bien hecho?" | items: "Exacto: categoría correcta, ni sobra ni falta atributo, nada fuera de dominio, sin duplicados, faltantes informados","Además: precisión y recall de atributos, inválidos, tokens, segundos","Dataset: 30 productos reales; esquema de Shopee y salida esperada MOCK" | label "Esquema y expected simulados · validar con catálogo" |
| s31 | code | "La métrica en código." | `{"file":"core/src/catalogo/evaluacion.py","lines":"14-33","symbol":"exacto","highlight":[25,33],"caption":"Un caso es exacto solo si todo se cumple. La vara es estricta a propósito."}` (ajustar rango a ≤ 18 líneas: usar "14-31" si hace falta y verificar que `exacto` quede dentro) | |
| s32 | decision | "¿Cuál es el número que aceptamos?" | number 8, options ["A · Cero valores inválidos y cero duplicados en los 30; exactos ≥ los del proceso actual","B · Exactos ≥ 80 %","C · Solo precisión y recall"], proposal "A. Con expected mock, 'exacto' castiga aciertos que hoy nadie mapea; los inválidos y duplicados sí son errores seguros. Se fija el número en la sala.", file "decisiones/08-criterio-de-exito.md" | D8 |
| s33 | decision | "¿Con qué dataset?" | number 9, options ["A · Los 30 reales del zip, con esquema y expected mock rotulados","B · Solo los 10 mock","C · Esperar el esquema oficial de Shopee"], proposal "A. Son productos reales con publicaciones reales; lo simulado queda rotulado y se valida con catálogo después.", file "decisiones/09-dataset.md" | D9 |

Para cada `code`, antes de escribirlo correr `sed -n 'a,bp' <archivo>` y confirmar que el símbolo está y que son ≤ 18 líneas; ajustar el rango si el archivo cambió.

- [ ] **Step 1: Escribir las láminas s10–s33**
- [ ] **Step 2: Generar y testear**

Run: `python3 scripts/generar_presentacion.py && node --test scripts/warroom.test.mjs`
Expected: sin `ValueError` de fragmentos; tests PASS.

- [ ] **Step 3: Commit (preguntar a Gastón)**

```bash
git add docs/warroom/diapositivas.json docs/presentacion-warroom.html docs/guion-warroom-propuesto.md
git commit -m "feat(deck): bloque 2 · diseñar el agente (decisiones 3 a 9)"
```

---

### Task 8: JSON · Bloque 3 (V1)

**Files:**
- Modify: `docs/warroom/diapositivas.json`

| id | kind | title | Contenido |
|---|---|---|---|
| s34 | divider | "V1 · el agente responde." | lead "Solo instrucciones: se espera que falle, y esos fallos justifican lo que sigue" |
| s35 | code | "Una llamada, una entrega." | `{"file":"core/src/catalogo/v1.py","lines":"83-102","symbol":"async def mapear","highlight":[88,97,99]}` → recortar a "83-100" si supera 18 líneas y verificar que `mapear` y `model_validate` queden dentro; caption "tool_required=True: el modelo tiene que entregar. Si la entrega no cumple el contrato, se informa el error, no se publica." |
| s36 | demo | "Demo · un caso real por V1." | command "scripts/correr.sh --version v1 --datos real --caso error-88904447", watch ["La categoría elegida frente a `reference_category`","Cada atributo: ¿de dónde salió el valor?","`missing` y `rejected`: ¿informa lo que no pudo?"], fallback "resultados/v1-real-20260928-173758.json" |
| s37 | table | "Qué falló en V1 y qué capa lo resuelve." | headers "Fallo","Caso","Capa"; rows ["Categoría inventada sin referencia","09-sin-categoria (mock)","V2 · tabla por herramienta"],["Valor fuera de la lista del canal","19 en los 30 reales","V3 · guardrail"],["Obligatorio sin informar","2 en los 30 reales","V3 · guardrail"],["~22.000 tokens de entrada por producto","todos","V2 · caché de prompt"]; label "Corrida del 28/09, anterior a las correcciones" |

- [ ] **Step 1: Escribir s34–s37**
- [ ] **Step 2: Generar y testear** — `python3 scripts/generar_presentacion.py && node --test scripts/warroom.test.mjs`
- [ ] **Step 3: Commit (preguntar a Gastón)** — `git commit -m "feat(deck): bloque 3 · V1"`

---

### Task 9: JSON · Bloque 4 (V2)

**Files:**
- Modify: `docs/warroom/diapositivas.json`

| id | kind | title | Contenido | Decisión |
|---|---|---|---|---|
| s38 | divider | "V2 · herramientas." | lead "El agente consulta antes de decidir" | |
| s39 | flow | "Una herramienta es una función que el modelo pide y el código ejecuta." | items: "El modelo pide buscar_categoria('urn:category:1106872')","El código consulta la tabla","Devuelve {encontrada: true, urn, name} o {encontrada: false, motivo}","El modelo sigue con ese dato" | |
| s40 | code | "La fuente se abstrae; las herramientas no cambian." | `{"file":"core/src/catalogo/herramientas.py","lines":"17-34","symbol":"FuenteCatalogo","highlight":[17,26],"caption":"Hoy lee archivos; mañana la base o un endpoint de Alephee. El agente no se toca."}` | |
| s41 | code | "Una herramienta bien descrita." | `{"file":"core/src/catalogo/herramientas.py","lines":"42-48","symbol":"buscar_categoria","caption":"El docstring es lo que lee el modelo. Dice qué devuelve y qué pasa si no encuentra."}` | |
| s42 | decision | "¿Qué decide la tabla y qué decide el agente?" | number 10, options ["A · La tabla fija categoría y campos; el agente solo elige el valor equivalente y lo que la tabla no cubre","B · El agente puede corregir la tabla si cree que está mal","C · Todo por tabla; sin modelo"], proposal "A. La tabla manda (acuerdo del 25/08). 306 ids legacy apuntan a más de un atributo de Shopee: se desambigua por categoría, en código.", file "decisiones/10-tabla-vs-agente.md" | D10 |
| s43 | code | "El loop tiene un límite y una salida garantizada." | `{"file":"core/src/catalogo/v2.py","lines":"82-96","symbol":"MAX_RONDAS","highlight":[84,86],"caption":"En la última ronda solo queda la herramienta de entrega. Si no entrega, el error es explícito."}` | |
| s44 | code | "Caché de prompt: lo estático se paga una vez." | `{"file":"core/src/catalogo/v2.py","lines":"70-80","symbol":"CachePoint","highlight":[76,77],"caption":"Instrucciones + herramientas + producto quedan cacheados para todas las rondas del loop (F4)."}` | |
| s45 | table | "Costo por producto, medido." | headers "Versión","Entrada sin caché","Leído de caché","Segundos"; rows ["V1","~22.000","—","12,3"],["V2","~1.600","~12.000","18,3"]; label "Corrida del 28/09 · 30 reales · anterior a las correcciones" | |
| s46 | decision | "¿Cuánto puede costar?" | number 11, options ["A · Tope mensual acordado con Alephee y medición por producto (tokens de entrada, salida, caché)","B · Sin tope: se mide después","C · El tope de hoy (USD 350) y publicar sin atributos al agotarse"], proposal "A. Hoy el tope corta la calidad. Con caché por SKU (D13) y caché de prompt el costo baja; el número se fija con una corrida completa medida.", file "decisiones/11-costo.md" | D11 |
| s47 | demo | "Demo · el mismo caso por V2." | command "scripts/correr.sh --version v2 --datos real --caso error-88904447", watch ["Qué herramientas pidió y en qué orden (`herramientas_usadas`)","La categoría ahora viene de la tabla","Tokens leídos de caché"], fallback "resultados/v2-real-20260928-181509.json" | |

- [ ] **Step 1: Escribir s38–s47** (verificar cada rango con `sed -n`)
- [ ] **Step 2: Generar y testear**
- [ ] **Step 3: Commit (preguntar a Gastón)** — `git commit -m "feat(deck): bloque 4 · V2 (decisiones 10 y 11)"`

---

### Task 10: JSON · Bloque 5 (V3) y Bloque 6 (La prueba)

**Files:**
- Modify: `docs/warroom/diapositivas.json`

Bloque 5 (`section: "v3"`):

| id | kind | title | Contenido | Decisión |
|---|---|---|---|---|
| s48 | divider | "V3 · control." | lead "Qué pasa cuando el agente no sabe" | |
| s49 | compare | "Guardrail: una comprobación en código, no otra instrucción." | items: "REVISAR \| Lista los problemas y se los devuelve al agente: tiene una ronda para corregir", "LIMPIAR \| Red final: descarta lo inválido y marca los obligatorios que faltan", "NUNCA \| Inventa un valor ni publica un -1" | |
| s50 | code | "Qué mira el validador." | `{"file":"core/src/catalogo/guardrails.py","lines":"11-23","symbol":"_problema","highlight":[13,18,20],"caption":"Atributo fuera de categoría, sin dato, fuera de lista o con nombre que no coincide con su ID."}` | |
| s51 | code | "La red final no inventa: descarta y marca." | `{"file":"core/src/catalogo/guardrails.py","lines":"41-57","symbol":"def limpiar","highlight":[46,53,54],"caption":"Lo que no pasa va a rejected con el motivo; lo obligatorio sin dato va a missing."}` | |
| s52 | decision | "¿Qué hace cuando no sabe?" | number 12, options ["A · Publicar sin el atributo (hoy)","B · Faltante explícito con motivo; la publicación sale con `missing` y alguien decide","C · Bloquear la publicación hasta revisión humana"], proposal "B. Reemplaza el 'publicar sin atributos'. Quién revisa y si bloquea o no es la integración con Alephee: pendiente.", file "decisiones/12-cuando-no-sabe.md" | D12 |
| s53 | cards | "Memoria: correcciones del equipo de catálogo." | items: "Una corrección: en esta categoría, este valor del producto va a este atributo con este valor del canal","Se consulta como una herramienta más y manda sobre el modelo","Hoy un JSON local; en producción AgentCore Memory o una tabla de Alephee" | |
| s54 | code | "Una corrección vacía la caché." | `{"file":"core/src/catalogo/memoria.py","lines":"31-41","symbol":"def corregir","highlight":[39,40],"caption":"Una corrección puede cambiar cualquier mapeo guardado: la caché se vacía."}` | |
| s55 | code | "Mismo SKU, misma salida." | `{"file":"core/src/catalogo/v3.py","lines":"62-79","symbol":"en_cache","highlight":[65,73,74],"caption":"La tabla fija la categoría antes del modelo; si hay caché válida, el modelo no se llama."}` | |
| s56 | decision | "¿Cómo garantizamos determinismo?" | number 13, options ["A · Caché por SKU + canal; invalidar al corregir o al cambiar tablas","B · Seed y temperatura 0 (hoy)","C · Recalcular siempre"], proposal "A. 40 concesionarios venden el mismo SKU: un mapeo. La clave de caché hoy es SKU + categoría legacy; falta sumar versión de tablas y aislamiento por cuenta.", file "decisiones/13-determinismo-y-cache.md" | D13 |
| s57 | demo | "Demo · corregir y repetir." | command "scripts/corregir.sh --categoria <urn> --urn <atributo> --valor-producto <valor> --value-id <id> --value <nombre> && scripts/correr.sh --version v3 --datos real --caso error-88904447", watch ["`buscar_correcciones` aparece en `herramientas_usadas`","El valor corregido sale tal cual","Segunda corrida: `herramientas_usadas` = [cache]"], fallback "resultados/v3-real-20260928-180524.json" | |

Bloque 6 (`section: "prueba"`):

| id | kind | title | Contenido |
|---|---|---|---|
| s58 | divider | "La prueba." | lead "Hoy contra V1, V2 y V3, sobre los 30, con el criterio de la decisión 8" |
| s59 | table | "Resultados (se completan en vivo)." | headers "Métrica","Hoy","V1","V2","V3"; rows ["Casos exactos","7","·","·","·"],["Categoría correcta","28","·","·","·"],["Valores inválidos","47","·","·","·"],["Duplicados","5","·","·","·"],["Obligatorios sin informar","2","·","·","·"]; label "Columna 'Hoy': publicaciones exportadas, expected MOCK. Las otras se llenan con la corrida del día" |
| s60 | cards | "Cómo leer la tabla." | items: "Exactos bajos en todas las columnas: el expected hereda omisiones del proceso actual","Inválidos y duplicados sí son errores seguros: V3 no entrega ninguno (28/09)","Categoría: V3 28/30 en la corrida vieja; la corrección del 28/09 fija la categoría desde la tabla y hay que volver a medir" |
| s61 | flow | "Camino a producción." | items: "Esquema oficial de Shopee y expected validado con catálogo","Integración: API pública lee; escribir y leer tablas necesita acceso interno","Decidir dónde corre el batch (D5) y la política de `missing` (D12)","Medir costo completo y fijar el tope (D11)" |
| s62 | table | "Las 13 decisiones." | headers "N","Decisión","Archivo"; 13 filas con el título y `decisiones/NN-….md` |
| s63 | divider | "Quién hace qué, para cuándo." | lead "Se completa en la sala" |

- [ ] **Step 1: Escribir s48–s63**
- [ ] **Step 2: Generar y testear** — `python3 scripts/generar_presentacion.py && node --test scripts/warroom.test.mjs`
- [ ] **Step 3: Commit (preguntar a Gastón)** — `git commit -m "feat(deck): bloques 5 y 6 · V3 y la prueba"`

---

### Task 11: `decisiones/` + PDF + documentación

**Files:**
- Create: `decisiones/01-alcance.md` … `decisiones/13-determinismo-y-cache.md`
- Modify: `CLAUDE.md` (sección "Revisión aplicada del material y V3", "Decisiones a tomar en la sala", "Agenda", tabla de pendientes "Presentación del war room")
- Modify: `README.md` (entrada que menciona 43 diapositivas / 7 secciones)
- Modify: `docs/revision-warroom.md` (párrafo "Mejoras aplicadas": agregar la versión del 30/09 y enlace al spec)

- [ ] **Step 1: Crear los 13 archivos con esta plantilla**

```markdown
# Decisión NN · <título>

**Contexto.** <2–4 oraciones copiadas/adaptadas de la lámina `decision` y de CLAUDE.md>

**Opciones.**
1. <opción A> — consecuencias: …
2. <opción B> — consecuencias: …
3. <opción C> — consecuencias: …

**Propuesta para la sala.** <la `proposal` de la lámina>

**Decisión.** _(se completa el 1/10)_

**Razonamiento.** _(se completa el 1/10)_

**Responsable y fecha.** _(se completa el 1/10)_
```

Nombres: `01-alcance`, `02-contrato`, `03-tipo-de-aplicacion`, `04-salida-estructurada`, `05-donde-corre`, `06-modelo`, `07-stack`, `08-criterio-de-exito`, `09-dataset`, `10-tabla-vs-agente`, `11-costo`, `12-cuando-no-sabe`, `13-determinismo-y-cache`. Deben coincidir con el campo `file` de cada lámina `decision`: verificar con

```bash
python3 -c "import json,os;[print(d['decision']['file'], os.path.exists(d['decision']['file'])) for d in json.load(open('docs/warroom/diapositivas.json'))['slides'] if d['kind']=='decision']"
```
Expected: 13 líneas, todas `True`.

- [ ] **Step 2: Exportar el PDF**

Run: `uv run python scripts/exportar_presentacion_pdf.py`
Expected: "PDF: 63 páginas; escala mínima ≥ 0,65" sin `ValueError`. Si una lámina de código es "demasiado densa", recortar el rango (≤ 18 líneas ya es la constraint) o partir el fragmento en dos láminas.

- [ ] **Step 3: Actualizar documentación**

En `CLAUDE.md`:
- "Revisión aplicada del material y V3": reemplazar la primera viñeta por "Presentación local: `docs/presentacion-warroom.html`, 63 diapositivas en 6 bloques organizadas como una cadena de 13 decisiones con láminas de código leídas del repo (30/09). Fuente: `docs/warroom/diapositivas.json`; diseño en `docs/warroom/diseno-presentacion.md`; fuentes externas en `docs/warroom/fuentes.md`."
- "Decisiones a tomar en la sala": reemplazar la lista de 7 por las 13 con su archivo; aclarar que D1–D9 se toman en los bloques 1 y 2, D10–D11 en V2 y D12–D13 en V3.
- Tabla de pendientes, fila "Presentación del war room": "**Rehecha** (30/09): 63 láminas, 13 decisiones, código del repo en pantalla".
- Última actualización: 2026-09-30.

En `README.md`: actualizar la mención a la presentación (cantidad y enlace al spec). En `docs/revision-warroom.md`, agregar al inicio de "Mejoras aplicadas": "El 30/09 se rediseñó el deck como cadena de decisiones con código del repo en pantalla; ver `warroom/diseno-presentacion.md`. Lo que sigue describe la versión del 29/09."

- [ ] **Step 4: Verificación final completa**

Run: `uv run pytest scripts/test_generar_presentacion.py core/tests -q && python3 scripts/generar_presentacion.py && node --test scripts/warroom.test.mjs && uv run python scripts/exportar_presentacion_pdf.py && grep -nE "\bvos\b|podés|tenés|\bbot\b" docs/warroom/diapositivas.json`
Expected: todo PASS; el `grep` no devuelve nada.

- [ ] **Step 5: Revisión visual**

Abrir `docs/presentacion-warroom.html` en el navegador: recorrer las láminas `code` (legibles a 1280 px de ancho, sin scroll horizontal en fragmentos ≤ 100 columnas), abrir una `decision` y comprobar que la propuesta está plegada, y una `demo`.

- [ ] **Step 6: Commit (preguntar a Gastón)**

```bash
git add decisiones CLAUDE.md README.md docs/revision-warroom.md docs/presentacion-warroom.pdf docs/presentacion-warroom.html docs/guion-warroom-propuesto.md
git commit -m "docs(deck): decisiones 1–13, PDF y documentación de la presentación rediseñada"
```
