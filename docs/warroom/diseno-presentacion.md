# Diseño de la presentación del war room · versión "cadena de decisiones"

Spec del 30/09/2026 (Gastón Zarate). Reemplaza la estructura de 43 diapositivas en 7 secciones del 29/09. Fuente única sigue siendo `docs/warroom/diapositivas.json`; HTML, guion y PDF se regeneran desde ahí.

## 1. Problema a resolver

La versión anterior no se termina de entender: mucha dinámica (quizzes, parejas, respuestas revelables) y poca inspección del código real. Se pide un deck **didáctico** que recorra el diseño completo del agente como una **cadena de decisiones**, mostrando en cada tema una sección del código del repo, y que conserve la progresión V1 → V2 → V3.

## 2. Acuerdos de diseño

| Tema | Decisión |
|---|---|
| Audiencia | Mixta. Cada tema lleva una lámina de concepto (negocio) y una lámina de código (devs). |
| Código en la sala | Fragmento en la lámina, leído del archivo real al generar el deck, más salto al editor/terminal para correrlo. |
| Dinámica | Se quitan quizzes, consignas en parejas y respuestas revelables. Quedan las demos conducidas por Gastón y la prueba final. |
| Decisiones de negocio | Las 7 del bloque 09:30 se integran a la cadena junto con las técnicas: una sola lista numerada (D1–D13). |
| Horarios | No se mueven. Los bloques se rediseñan por dentro. |
| Columna vertebral | La cadena de decisiones. V1, V2 y V3 son los puntos donde se "compila" lo decidido hasta ahí. |
| Nombre | "Agente" o "solución", nunca "bot". |

## 3. Estructura: 6 bloques, 24 temas, ~55 láminas

Cada tema con código ocupa hasta tres láminas: concepto → código → decisión. Cada bloque abre con un `divider`.

### Bloque 1 · 09:00 · Punto de partida
| # | Tema | Concepto | Código | Decisión |
|---|---|---|---|---|
| 1 | Qué tenemos a las 17:00 | El error real (SKU 88904447, Código OEM = "ABS Plastic"), el proceso de hoy (dos llamadas + merge, USD 350/mes, publica sin atributos cuando se agota), qué se construye hoy | `inputs/prompts-actuales/index.ts` (`categoryPrompt`) | — |
| 2 | Qué hace y qué no | Un canal (Shopee), una familia, mapea categoría + atributos; no genera título, descripción ni marca | — | D1 Alcance |
| 3 | Qué recibe y qué entrega | Entrada: producto de Alephee. Salida: `category`, `attributes`, `missing`, `rejected` | `core/src/catalogo/modelos.py` (`Publicacion`) | D2 Contrato |

### Bloque 2 · 09:30 · Diseñar el agente antes de escribirlo (pausa 11:00)
| # | Tema | Concepto | Código | Decisión |
|---|---|---|---|---|
| 4 | Tipos de aplicación | Single prompt · workflow determinista · agente con herramientas · multiagente; cuándo conviene cada uno | `core/src/catalogo/correr.py` (`_versiones`) | D3 Empezar single prompt y escalar solo si hace falta |
| 5 | Anatomía de un prompt | Rol · tarea · reglas · formato · qué hacer si falta dato. Buenas prácticas: estático primero, negativas explícitas, salida estructurada en vez de JSON "por favor" | `core/src/catalogo/v1.py` (`INSTRUCCIONES`, `HERRAMIENTA_SALIDA`) vs. `categoryPrompt` | D4 Salida estructurada por tool + Pydantic |
| 6 | Dónde corre | AgentCore: qué resuelve (runtime, identidad, memoria, gateway, observabilidad) y dudas (cold start, batch vs. chat, costo, región). Alternativa: contenedor/Lambda propio | `core/server.py` (`/ping`, `/invocations`) + `infra/sst/runtime.ts` | D5 Local hoy; chat en AgentCore, batch como lo usaría Alephee |
| 7 | Cómo elegir el modelo | Criterios: tool calling confiable, seguir reglas, costo por token, caché de prompt, latencia (no restrictiva), región | — | — |
| 8 | Qué hay en Bedrock | Familias disponibles, inference profiles `us.`/`global.`, habilitación por cuenta y región | `core/src/catalogo/llm.py` (`crear_llm`) + `client.config.ts` (`modelo`) | D6 Claude Sonnet 5 vía Converse |
| 9 | Stack y harness | Por qué un framework esta vez; qué es el harness de desarrollo y qué se revisa antes de aceptar un cambio | `core/src/catalogo/v1.py` (`MapeoV1`) | D7 Python + LlamaIndex Workflows + BedrockConverse |
| 10 | ¿Cuándo está bien hecho? | Métrica "exacto", precisión/recall, inválidos, duplicados, tokens. Dataset: 30 reales, esquema y `expected` mock | `core/src/catalogo/evaluacion.py` + `data/real/` | D8 Criterio de éxito · D9 Dataset |

### Bloque 3 · 11:15 · V1 · el agente responde
| # | Tema | Contenido | Código |
|---|---|---|---|
| 11 | Construir V1 | Recorrido de `mapear`: mensaje, llamada, tool call, validación | `core/src/catalogo/v1.py` (`mapear`) |
| 12 | Demo V1 | `scripts/correr.sh --version v1 --datos real --caso <id>`; leer una salida | — |
| 13 | Qué falló y por qué | Categoría inventada, valores fuera de lista, obligatorio sin informar → cada fallo apunta a una capa siguiente | — |

### Bloque 4 · 13:15 · V2 · herramientas (pausa 14:45)
| # | Tema | Concepto | Código | Decisión |
|---|---|---|---|---|
| 14 | Qué es una herramienta | Función que el modelo pide y el código ejecuta. Lectura vs. acción. Diseño: nombre, descripción, argumentos, salida con `encontrada: false` | `core/src/catalogo/herramientas.py` (`FuenteCatalogo`, `crear_herramientas`) | D10 Qué decide la tabla y qué decide el agente |
| 15 | El loop y su control | Rondas, `MAX_RONDAS`, última ronda solo entrega, error explícito | `core/src/catalogo/v2.py` (`mapear`) | — |
| 16 | Costo y caché de prompt | Estático primero, `CachePoint` tras el producto, `system_prompt_caching` y `tool_caching`. Presupuesto actual | `core/src/catalogo/v2.py` (historial) + `llm.py` | D11 Restricción de costo |
| 17 | Demo V2 | Mismo caso que V1; comparar | — |

### Bloque 5 · 15:00 · V3 · control
| # | Tema | Concepto | Código | Decisión |
|---|---|---|---|---|
| 18 | ¿Qué hace cuando no sabe? | Guardrail = comprobación en código: `revisar` (devolución) y `limpiar` (red final). Reemplaza "publicar sin atributos" | `core/src/catalogo/guardrails.py` | D12 Faltante explícito, nunca inventar |
| 19 | Memoria | Qué es memoria en un agente; acá: correcciones persistidas del equipo de catálogo, mandan sobre el modelo | `core/src/catalogo/memoria.py` + `buscar_correcciones` en `v3.py` | — |
| 20 | Determinismo y caché por SKU | Mismo SKU → misma salida; 40 concesionarios, un mapeo; qué invalida la caché | `core/src/catalogo/memoria.py` (`en_cache`) + `v3.py` (`mapear`) | D13 Caché por SKU + canal |
| 21 | Demo V3 | `scripts/corregir.sh` y repetición | — |

### Bloque 6 · 16:15 · La prueba y el camino
| # | Tema | Contenido |
|---|---|---|
| 22 | La prueba | Hoy vs. V1/V2/V3 sobre los 30 contra D8. Tabla que se completa en vivo. Lectura honesta: exactos bajos porque `expected` es mock |
| 23 | Camino a producción | Retomar dudas de AgentCore; integración (API pública lee, interna escribe); quién hace qué y para cuándo |
| 24 | Las 13 decisiones | Lista final numerada, con la ruta de cada `decisiones/NN-titulo.md` |

## 4. Formato de las láminas

Se conservan `divider`, `cards`, `flow`, `compare`, `table`. Se dejan de usar `quiz` y `exercise` (el generador puede seguir soportándolos). Se agregan tres tipos:

**`code`**
```json
{"kind": "code", "code": {"file": "core/src/catalogo/guardrails.py", "lines": "11-23", "highlight": [14, 17], "caption": "Qué mira el validador"}}
```
El generador lee el archivo al generar. Si el archivo o el rango no existen, **falla** en vez de producir un deck desactualizado. Renderiza con números de línea reales y resalta `highlight`. El guion incluye el fragmento en un bloque de código con la ruta y las líneas. `caption` va debajo. Los rangos se anclan a líneas: cuando cambie el código hay que ajustar el JSON (el fallo del generador avisa si el rango se sale del archivo; un rango desplazado pero válido no se detecta, por eso cada `code` lleva además `symbol` opcional que el generador verifica que aparezca dentro del rango).

**`decision`**
```json
{"kind": "decision", "decision": {"number": 12, "question": "¿Qué hace el agente cuando no sabe?", "options": ["A · Publicar sin el atributo (hoy)", "B · Faltante explícito con motivo", "C · Pedir revisión y bloquear"], "proposal": "B: ...", "file": "decisiones/12-que-hace-cuando-no-sabe.md"}}
```
Muestra número, pregunta, opciones con consecuencias y la propuesta en un `details` (se abre después de discutir). La decisión final se escribe en el archivo, no en el deck.

**`demo`**
```json
{"kind": "demo", "demo": {"command": "scripts/correr.sh --version v1 --datos real --caso publicados-88904447", "watch": ["...", "..."], "fallback": "resultados/v1-real-<fecha>.json"}}
```

Los campos `notes` (`objective`, `say`, `ask`, `close`, `transition`) y `minutes` se mantienen en todas las láminas; `ask` queda vacío en la mayoría.

## 5. Archivos que cambian

| Archivo | Cambio |
|---|---|
| `docs/warroom/diapositivas.json` | Se reescribe: 6 secciones, ~55 láminas. |
| `scripts/generar_presentacion.py` | Render de `code`, `decision`, `demo` en HTML y guion; lectura y verificación de fragmentos; título del guion con la fecha nueva. |
| `scripts/warroom.css` | Estilos de `pre`/líneas/resaltado, de la lámina de decisión y de la de demo. |
| `scripts/warroom.js` | Sin cambios previstos (la navegación no depende del tipo). |
| `scripts/warroom.test.mjs` | Cantidad de láminas y clases nuevas `slide--code`, `slide--decision`, `slide--demo`. |
| `scripts/exportar_presentacion_pdf.py` | Render de los tres tipos nuevos (código en monoespaciado, decisión como lista, demo como comando + lista). |
| `decisiones/01-…md` … `13-…md` | Se crean con contexto y opciones escritos y la sección "Decisión" y "Razonamiento" en blanco. |
| `docs/guion-warroom-propuesto.md`, `docs/presentacion-warroom.html`, `docs/presentacion-warroom.pdf` | Regenerados. |
| `CLAUDE.md`, `README.md`, `docs/revision-warroom.md` | Cuenta de láminas, secciones y enlace a este spec. |

## 6. Reglas de contenido

- Toda afirmación externa (capacidades y límites de AgentCore, catálogo de modelos de Bedrock, caché de prompts de OpenAI y Bedrock) lleva enlace a la documentación oficial en `notes.say` y en el guion. Lo que no se pueda verificar queda como "a confirmar con Juan David / Mariale".
- Datos mock siempre rotulados; cifras históricas rotuladas como anteriores a las correcciones del 28/09.
- Sin voseo en el texto en pantalla (español neutro).
- Sin nombres de asistentes salvo quienes conducen (Gastón) y quienes validan (Rick, Maximiliano, Juan David).

## 7. Verificación

1. `python3 scripts/generar_presentacion.py` genera sin error y todos los `code` resuelven (`symbol` dentro del rango).
2. `node --test scripts/warroom.test.mjs` pasa con la cantidad nueva.
3. `uv run python scripts/exportar_presentacion_pdf.py` genera el PDF con los tipos nuevos.
4. Revisión visual del HTML en el navegador (láminas de código legibles a tamaño de proyector: máximo ~18 líneas por fragmento).
5. Ensayo de tiempos por bloque: el bloque 2 tiene 7 temas en ~100 min; si se pasa, fusionar 7 con 8 y acortar 9.

## 8. Fuera de alcance

- No cambia el código del agente ni los datos.
- No se integra `mapear_producto` al chat (pendiente aparte).
- No se vuelve al deck de claude.ai.
