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


EYEBROWS = {"quiz": "Tu turno · elegí y justificá", "exercise": "Práctica en parejas", "example": "Ejemplo paso a paso",
            "demo": "Demo conducida por Gastón", "code": "Leer el código",
            "decision": "Decisión · se cierra antes de seguir"}


def eyebrow(s: dict) -> str:
    return EYEBROWS.get(s["kind"], "Construir · comprobar · decidir")


def _code(s: dict) -> str:
    f = fragmento(s["code"], RAIZ)
    lineas = "".join(
        f'<span class="ln{" hl" if n in f["highlight"] else ""}" data-n="{n}">{E(l) or " "}</span>'
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


def content(s):
    items = s['items']
    if s['kind'] == 'code':
        return _code(s)
    if s['kind'] == 'decision':
        return _decision(s)
    if s['kind'] == 'demo' and s.get('demo'):
        return _demo(s)
    if s['kind'] == 'table':
        t = s['table']
        return f'<div class="table-wrap"><table{" class=\"dense\"" if len(t["rows"]) > 4 else ""}><thead><tr>' + ''.join(f'<th scope="col">{E(x)}</th>' for x in t['headers']) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join(f'<{"th scope=\"row\"" if i == 0 else "td"}>{E(x)}</{"th" if i == 0 else "td"}>' for i, x in enumerate(row)) + '</tr>' for row in t['rows']) + '</tbody></table></div>'
    if s['exercise']:
        ex = s['exercise']
        return f'<div class="exercise"><p class="prompt">{E(ex["prompt"])}</p><ol>' + ''.join(f'<li>{E(x)}</li>' for x in ex['steps']) + f'</ol><div class="deliverable"><strong>Entreguen</strong> {E(ex["deliverable"])}</div><p class="debrief">{E(ex["debrief"])}</p><div class="timer" data-seconds="{ex["duration"] * 60}"><output aria-label="Tiempo restante">{ex["duration"]:02}:00</output><button data-action="timer">Iniciar tiempo</button><button data-action="reset-timer">Reiniciar</button></div></div>'
    if s['kind'] == 'flow':
        return '<ol class="flow">' + ''.join(f'<li><span class="step">{i+1:02}</span>{E(x)}</li>' for i,x in enumerate(items)) + '</ol>'
    if s['kind'] == 'compare':
        return '<div class="cards">' + ''.join(f'<article><span class="card-label">{E(x.split(" | ")[0])}</span><p>{E(x.split(" | ",1)[1])}</p></article>' for x in items) + '</div>'
    if items:
        return '<ul class="facts">' + ''.join(f'<li>{E(x)}</li>' for x in items) + '</ul>'
    return ''


def render_slide(i, s, data):
    slides = data['slides']
    section = {x['id']: x for x in data['sections']}[s['section']]
    choices = ''
    if s['options']:
        choices = '<div class="choices" role="group" aria-label="Elegí una opción para discutir">' + ''.join(f'<button class="choice" aria-pressed="false">{E(o)}</button>' for o in s['options']) + '</div><p class="hint">Voten a mano o por el chat de la reunión. La selección en pantalla no cuenta votos.</p>'
    answer = f'<details class="answer"><summary>Revelar respuesta y discutir</summary><p>{E(s["answer"])}</p></details>' if s['answer'] else ''
    notes = '<dl>' + ''.join(f'<dt>{label}</dt><dd>{E(s["notes"][key])}</dd>' for key,label in [('objective','Objetivo'),('say','Temas para hablar'),('ask','Pregunta al grupo'),('close','Devolución'),('transition','Transición')] if s['notes'][key]) + '</dl>'
    return f'<section id="{s["id"]}" class="slide slide--{s["kind"]}{" active" if i==0 else ""}" data-section="{E(s["section"])}" aria-label="Diapositiva {i+1} de {len(slides)}" aria-hidden="{str(i!=0).lower()}"{(" hidden" if i != 0 else "")}><header><span>ALEPHEE × CRAFTECH × AWS</span><span>{E(section["title"])} · {E(section["time"])}</span></header><div class="body"><div class="eyebrow">{E(section["goal"] if s["kind"]=="divider" else eyebrow(s))}</div><h1>{E(s["title"])}</h1>' + (f'<p class="lead">{E(s["lead"])}</p>' if s['lead'] else '') + (f'<p class="source">{E(s["label"])}</p>' if s['label'] else '') + content(s) + (f'<p class="question">{E(s["question"])}</p>' if s['question'] else '') + choices + answer + '</div><div class="notes-content" hidden>'+notes+'</div></section>'


def render_html(data):
    slides = data['slides']
    parts = [render_slide(i, s, data) for i, s in enumerate(slides)]
    options=[]
    for section in data['sections']:
        # Una sección sin láminas (deck a medio escribir) no entra al selector.
        index=next((i for i,s in enumerate(slides) if s['section']==section['id']), None)
        if index is not None:
            options.append(f'<option value="{index}">{E(section["title"])}</option>')
    css=(RAIZ/'scripts/warroom.css').read_text()
    js=(RAIZ/'scripts/warroom.js').read_text()
    return f'<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(data["title"])}</title><style>{css}</style></head><body><main>'+''.join(parts)+'</main><aside id="notes-panel" hidden aria-label="Notas del expositor"><button id="close-notes">Cerrar notas</button><div id="notes-body"></div></aside><nav aria-label="Controles de presentación"><span id="count" aria-live="polite"></span><label for="section-select" class="sr-only">Ir a una sección</label><select id="section-select">'+''.join(options)+'</select><button id="prev" aria-label="Diapositiva anterior">←</button><button id="next" aria-label="Diapositiva siguiente">→</button><button id="notes" aria-expanded="false" aria-controls="notes-panel">Notas · N</button><button id="print">Imprimir / PDF</button></nav><div class="progress" aria-hidden="true"></div><script>'+js+'</script></body></html>'


def guion_slide(i, s, secciones):
    lines = [f'### {i+1:02} · {s["title"]}', '', f'**Sección:** {secciones[s["section"]]["title"]} · **Pauta:** {s["minutes"]} min · **Tipo:** {s["kind"]}', '', f'**Objetivo:** {s["notes"]["objective"]}', '']
    screen=[s['lead'],s['label'],*s['items'],s['question'],*s['options']]
    if s['table']:
        screen += [' / '.join(s['table']['headers'])]+[' / '.join(row) for row in s['table']['rows']]
    lines += ['**En pantalla:**', ''] + [f'- {x}' for x in screen if x] + ['']
    for key,label in [('say','Temas para hablar'),('ask','Pregunta / participación'),('close','Devolución esperada'),('transition','Transición')]:
        if s['notes'][key]: lines += [f'**{label}:** {s["notes"][key]}','']
    if s['exercise']:
        ex=s['exercise'];lines += [f'**Consigna ({ex["duration"]} min):** {ex["prompt"]}','']+[f'{j+1}. {v}' for j,v in enumerate(ex['steps'])]+['',f'**Entrega:** {ex["deliverable"]}', '',f'**Puesta en común:** {ex["debrief"]}','']
    if s['answer']: lines += [f'**Respuesta al revelar:** {s["answer"]}','']
    if s['kind'] == 'code':
        f = fragmento(s['code'], RAIZ)
        ext = Path(f['file']).suffix.lstrip('.') or 'text'
        fin = f['inicio'] + len(f['lineas']) - 1
        lines += [f'**Código:** `{f["file"]}` líneas {f["inicio"]}–{fin}', '', f'```{ext}', *f['lineas'], '```', '']
        if f['caption']: lines += [f['caption'], '']
    if s['kind'] == 'decision':
        d = s['decision']
        lines += [f'**Decisión {d["number"]}:** {d["question"]}', ''] + [f'{j+1}. {o}' for j, o in enumerate(d['options'])] + ['', f'**Propuesta:** {d["proposal"]}', '', f'**Archivo:** `{d["file"]}`', '']
    if s['kind'] == 'demo' and s.get('demo'):
        d = s['demo']
        lines += ['```bash', d['command'], '```', '', '**Mirar:**', ''] + [f'- {w}' for w in d['watch']] + ['']
        if d.get('fallback'): lines += [f'**Respaldo:** {d["fallback"]}', '']
    return lines


def render_guion(data):
    slides = data['slides']
    secciones = {s['id']: s for s in data['sections']}
    lines=['# Guion del warroom · por diapositiva','',f'Versión del 30/09/2026 · {len(slides)} diapositivas · {len([s for s in data["sections"] if any(x["section"]==s["id"] for x in slides)])} bloques · 13 decisiones. Diseño en `warroom/diseno-presentacion.md`; fuentes externas en `warroom/fuentes.md`. Fuente única: `docs/warroom/diapositivas.json`. Se regenera con `python3 scripts/generar_presentacion.py`.','', '[Presentación interactiva](presentacion-warroom.html) · [PDF estático](presentacion-warroom.pdf)','', '## Dinámica acordada','', 'Gastón conduce. El deck es una cadena de 13 decisiones de diseño: cada tema tiene una lámina de concepto, una de código leído del repositorio y una de decisión que se cierra en la sala antes de seguir. V1, V2 y V3 son los puntos donde lo decidido se compila y se corre. Pedir la opinión de quienes están remotos antes de cerrar cada decisión.','', 'Los fragmentos de código se leen del repositorio al generar el deck: si el código cambia, hay que regenerar. La propuesta de cada decisión está plegada y se abre después de escuchar al grupo; la decisión final se escribe en `decisiones/NN-titulo.md`, no en el deck. Las cifras del 28/09 son anteriores a las correcciones de esa fecha; las columnas de la prueba se completan con la corrida del día.','', '## Mapa y tiempos','', '| Sección | Horario | Diapositivas | Resultado |','|---|---|---|---|']
    for sec in data['sections']:
        nums=[i+1 for i,s in enumerate(slides) if s['section']==sec['id']]
        if not nums: continue
        lines.append(f'| {sec["title"]} | {sec["time"]} | {nums[0]}–{nums[-1]} | {sec["goal"]} |')
    lines += ['', 'Pausa 11:00–11:15; almuerzo 12:30–13:15; pausa 14:45–15:00. El bloque V3 incluye preparación de comparación 16:00–16:15. Margen de preguntas 17:00–17:30 sujeto a confirmación logística.', '', 'Los minutos por diapositiva son una pauta. Preservar la hora de cierre. Si el bloque 2 se pasa, fusionar las láminas de criterios de modelo y catálogo de Bedrock y acortar la de stack; nunca saltar una decisión.', '', '## Preparación del facilitador','', '- Caso guía de las demos: `error-88904447` (Código OEM = ABS Plastic). Confirmarlo con el grupo en la decisión 9.', '- Validar entornos y acceso al modelo antes del día. Tener una corrida guardada identificada como respaldo.', '- Para un caso: `scripts/correr.sh --version v1 --datos real --caso <id>`; cambiar versión para comparar el mismo caso.', '- En V3, la corrección de la demo se carga con `scripts/corregir.sh`; no modificar `data/real` ni el lote de comparación. Exportar el PDF con `uv run --with reportlab python scripts/exportar_presentacion_pdf.py`.', '- Registrar decisiones en `decisiones/`: contexto, opciones, decisión y razonamiento. No cambiar expected para favorecer una versión.', '- Ensayar el lote durante los bloques. La latencia histórica de V3 implica unos 12 minutos por 30 productos; las nuevas mediciones pueden variar.', '', '## Bosquejo por diapositiva','']
    schedule = ['## Distribución completa dentro de cada bloque', '', '| Bloque | Diapositivas y demos | Trabajo reservado | Total |', '|---|---:|---|---:|']
    for sec in data['sections']:
        guided = sum(s['minutes'] for s in slides if s['section'] == sec['id'])
        reserve = sec['work_reserve']
        schedule.append(f'| {sec["title"]} | {guided} min | ' + '; '.join(f'{label}: {minutes} min' for label, minutes in reserve) + f' | {guided + sum(m for _, m in reserve)} min |')
    schedule += ['', 'Las reservas son para pizarra, corridas del lote y preguntas dentro del bloque. Son pautas ajustables de esta jornada.', '']
    where = lines.index('## Preparación del facilitador')
    lines[where:where] = schedule
    for i,s in enumerate(slides):
        lines += guion_slide(i, s, secciones)
    lines += ['## Fundamento editorial y revisión','', 'Diseño de esta versión: [diseno-presentacion.md](warroom/diseno-presentacion.md). Revisión editorial de la versión anterior: [revision-agentes.md](warroom/revision-agentes.md).','']
    return '\n'.join(lines)


def main() -> None:
    data = cargar()
    (RAIZ / 'docs/presentacion-warroom.html').write_text(render_html(data))
    (RAIZ / 'docs/guion-warroom-propuesto.md').write_text(render_guion(data))
    print(f'Generados HTML y guion de {len(data["slides"])} diapositivas.')


if __name__ == '__main__':
    main()
