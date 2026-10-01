# Guion del warroom · por diapositiva

Versión del 30/09/2026 · 64 diapositivas · 6 bloques · 13 decisiones. Diseño en `warroom/diseno-presentacion.md`; fuentes externas en `warroom/fuentes.md`. Fuente única: `docs/warroom/diapositivas.json`. Se regenera con `python3 scripts/generar_presentacion.py`.

[Presentación interactiva](presentacion-warroom.html) · [PDF estático](presentacion-warroom.pdf)

## Dinámica acordada

Gastón conduce. El deck es una cadena de 13 decisiones de diseño: cada tema tiene una lámina de concepto, una de código leído del repositorio y una de decisión que se cierra en la sala antes de seguir. V1, V2 y V3 son los puntos donde lo decidido se compila y se corre. Pedir la opinión de quienes están remotos antes de cerrar cada decisión.

Los fragmentos de código se leen del repositorio al generar el deck: si el código cambia, hay que regenerar. La propuesta de cada decisión está plegada y se abre después de escuchar al grupo; la decisión final se escribe en `decisiones/NN-titulo.md`, no en el deck. Las cifras del 28/09 son anteriores a las correcciones de esa fecha; las columnas de la prueba se completan con la corrida del día.

## Mapa y tiempos

| Sección | Horario | Diapositivas | Resultado |
|---|---|---|---|
| 01 · Punto de partida | 09:00–09:30 | 1–9 | Ver el error de hoy y acordar qué construimos |
| 02 · Diseñar el agente | 09:30–11:15 | 10–33 | Tomar las decisiones que definen la V1 |
| 03 · V1 · el agente responde | 11:15–12:30 | 34–37 | Construir, correr y leer la primera versión |
| 04 · V2 · herramientas | 13:15–14:45 | 38–47 | Decidir qué resuelve la tabla y conectarla |
| 05 · V3 · control | 15:00–16:15 | 48–57 | Decidir qué pasa cuando el agente no sabe |
| 06 · La prueba y el camino | 16:15–17:00 | 58–64 | Medir contra el criterio y repartir lo que sigue |

Pausa 11:00–11:15; almuerzo 12:30–13:15; pausa 14:45–15:00. El bloque V3 incluye preparación de comparación 16:00–16:15. Margen de preguntas 17:00–17:30 sujeto a confirmación logística.

Los minutos por diapositiva son una pauta. Preservar la hora de cierre. Si el bloque 2 se pasa, fusionar las láminas de criterios de modelo y catálogo de Bedrock y acortar la de stack; nunca saltar una decisión.

## Distribución completa dentro de cada bloque

| Bloque | Diapositivas y demos | Trabajo reservado | Total |
|---|---:|---|---:|
| 01 · Punto de partida | 25 min | Dolores del equipo y preguntas: 5 min | 30 min |
| 02 · Diseñar el agente | 85 min | Pizarra: dudas de AgentCore para Juan David: 5 min; Pausa 11:00: 15 min | 105 min |
| 03 · V1 · el agente responde | 13 min | Corridas sobre otros casos: 25 min | 38 min |
| 04 · V2 · herramientas | 36 min | Corrida del lote y lectura: 25 min | 61 min |
| 05 · V3 · control | 36 min | Corrida del lote con V3: 20 min | 56 min |
| 06 · La prueba y el camino | 17 min | Documentar decisiones y responsables: 15 min | 32 min |

Las reservas son para pizarra, corridas del lote y preguntas dentro del bloque. Son pautas ajustables de esta jornada.

## Preparación del facilitador

- Caso guía de las demos: `error-88904447` (Código OEM = ABS Plastic). Confirmarlo con el grupo en la decisión 9.
- Validar entornos y acceso al modelo antes del día. Tener una corrida guardada identificada como respaldo.
- Para un caso: `scripts/correr.sh --version v1 --datos real --caso <id>`; cambiar versión para comparar el mismo caso.
- En V3, la corrección de la demo se carga con `scripts/corregir.sh`; no modificar `data/real` ni el lote de comparación. Exportar el PDF con `uv run --with reportlab python scripts/exportar_presentacion_pdf.py`.
- Registrar decisiones en `decisiones/`: contexto, opciones, decisión y razonamiento. No cambiar expected para favorecer una versión.
- Ensayar el lote durante los bloques. La latencia histórica de V3 implica unos 12 minutos por 30 productos; las nuevas mediciones pueden variar.

## Bosquejo por diapositiva

### 01 · Un agente que mapea el catálogo a Shopee, decidido paso a paso.

**Sección:** 01 · Punto de partida · **Pauta:** 1 min · **Tipo:** divider

**Objetivo:** Qué tenemos a las 17:00: agente en local, método repetible, 13 decisiones documentadas

**En pantalla:**

- War Room · Alephee × Craftech × AWS · 1/10/2026

**Temas para hablar:** A las 17:00 queremos tres cosas: el agente corriendo en local con el código en el repositorio, un método que se pueda repetir para el próximo caso de uso y trece decisiones escritas con su razonamiento. Hoy no se enseña teoría: se diseña y se construye en el orden en que se diseña. Gastón conduce; el grupo decide en cada punto.

**Transición:** Primero, cómo funciona hoy.

### 02 · Hoy: dos llamadas, un merge y un presupuesto que se agota.

**Sección:** 01 · Punto de partida · **Pauta:** 3 min · **Tipo:** cards

**Objetivo:** Entender el proceso actual sin juzgarlo

**En pantalla:**

- Categoría: la tabla reference_category y, si no alcanza, el modelo elige
- Atributos: dos llamadas en paralelo (con y sin referencia) y un merge por código
- USD 350 por mes: cuando se agota, se publica sin atributos

**Temas para hablar:** Describir el flujo actual tal como lo explicó Maximiliano: la categoría se resuelve por tabla y el modelo entra cuando la tabla no la tiene; los atributos van en dos llamadas en paralelo porque un solo prompt era demasiado largo, y un merge por código prioriza la que usó la referencia. Latencia de 13 segundos en batch: no es una restricción. El punto que duele es el presupuesto: cuando se agota, la publicación sale sin atributos. El modelo exacto y sus parámetros siguen sin confirmar.

**Pregunta / participación:** ¿Qué parte de este flujo les da más trabajo hoy?

**Devolución esperada:** Anotar las respuestas en la pizarra: se retoman en la prueba final.

**Transición:** Veamos cómo se le pide hoy la categoría al modelo.

### 03 · Así se pide hoy la categoría.

**Sección:** 01 · Punto de partida · **Pauta:** 3 min · **Tipo:** code

**Objetivo:** Leer juntos el prompt actual y separar lo que se conserva de lo que se cambia

**En pantalla:**

- Prompt actual de Alephee · inputs/prompts-actuales/index.ts

**Temas para hablar:** Leer las reglas resaltadas: son buenas y se conservan. Señalar tres cosas que vamos a decidir distinto a lo largo del día: la salida es JSON pedido por favor en el texto (decisión 4), la lista completa de categorías viaja en cada llamada y después del producto (decisión sobre caché, bloque V2), y solo usa el nombre de la categoría y del producto, no la descripción. No es una crítica al equipo: es el punto de partida.

**Transición:** Qué pasó con esas publicaciones en Shopee.

**Código:** `inputs/prompts-actuales/index.ts` líneas 4–21

```ts
export const categoryPrompt = (product: CatalogItem, categories: any, language: string): string => `
You are an assistant that must identify the single best matching marketplace category
for a given CRM product.

Follow these steps carefully:

1️⃣ Step 1 — Exact Match:
- Compare the CRM category name with each marketplace category name.
- If you find an **exact or nearly identical** match (ignoring case, accents, plural/singular),
  return that category immediately.

2️⃣ Step 2 — Semantic Match:
- Only if no exact match exists, choose the category whose meaning is most related
  to both the CRM category name and the product name.

3️⃣ Rules:
- Never invent, merge, or rename categories.
- Never modify the URN. You must copy it **exactly as shown** in the list below, including the full prefix like "urn:category:..."
```

Reglas correctas (no inventar, copiar el URN exacto). Lo que se va a revisar: el JSON se pide en el texto y la lista completa de categorías viaja en cada llamada.

### 04 · Lo que Shopee rechazó y lo que aceptó mal.

**Sección:** 01 · Punto de partida · **Pauta:** 3 min · **Tipo:** table

**Objetivo:** Ver errores reales: los que rechaza el canal y los que acepta igual

**En pantalla:**

- Datos reales · WarRoom.zip del 24/09 · 30 productos
- Caso / Qué salió / Qué pasó
- 88904447 / Código OEM = ABS Plastic / Rechazado: el valor no pertenece al atributo
- 93221445 / Inmetro Certification con varios valores / Rechazado: solo admite un valor
- 9 de 30 / Valor -1 publicado como valor / Aceptado por Shopee
- 98550368 / 14 de 15 URN sin sufijo del canal / Aceptado por Shopee

**Temas para hablar:** Los 30 productos del zip: 20 publicados y 10 rechazados. El caso 88904447 es el hilo del día: un material (ABS Plastic) copiado al campo Código OEM, que Shopee rechazó porque el valor no está vinculado a ese atributo. El 24581199 publicó Quantity diez veces y Shopee no lo mencionó: lo rechazó por otro obligatorio (Auto-Part Number). Lo peor no es lo que Shopee rechaza, que al menos avisa, sino lo que acepta mal: un -1 publicado como valor en 9 de 30 y URN sin el sufijo del canal. Nadie se entera hasta que un comprador lo ve.

**Pregunta / participación:** ¿Cuál de estos errores les parece más grave para el negocio?

**Transición:** Cómo vamos a trabajar hoy.

### 05 · Seis bloques: cada decisión se compila en una versión.

**Sección:** 01 · Punto de partida · **Pauta:** 3 min · **Tipo:** flow

**Objetivo:** Ubicar al grupo en la agenda

**En pantalla:**

- Decidimos → construimos → medimos. Nunca se pasa al bloque siguiente con algo roto.
- Punto de partida
- Diseñar el agente
- V1 · responde
- V2 · herramientas
- V3 · control
- La prueba

**Temas para hablar:** Las decisiones de la mañana producen la V1; las de herramientas, la V2; las de control, la V3; y la prueba mide todo contra el criterio que acordamos antes de escribir código. Pausa a las 11:00, almuerzo 12:30 a 13:15, pausa 14:45. Cierre técnico a las 17:00 y margen de preguntas hasta las 17:30.

**Transición:** Primera decisión: qué hace y qué no hace.

### 06 · ¿Qué hace y qué no hace?

**Sección:** 01 · Punto de partida · **Pauta:** 3 min · **Tipo:** decision

**Objetivo:** Cerrar la decisión 1 antes de hablar de contrato

**En pantalla:**


**Temas para hablar:** Presentar las tres opciones con su consecuencia: B multiplica las tablas y los esquemas de canal sin cambiar el método; C mezcla dos problemas distintos, mapear y redactar. Abrir la propuesta solo después de escuchar al grupo. La decisión queda en decisiones/01-alcance.md con su razonamiento.

**Pregunta / participación:** ¿Hay alguna familia de productos que convenga más que otra para empezar?

**Devolución esperada:** Registrar la decisión y la familia elegida.

**Transición:** Si el alcance es ese, ¿qué entra y qué sale?

**Decisión 1:** ¿Qué alcance tiene el agente del war room?

1. A · Un canal (Shopee) y una familia de productos: categoría + atributos
2. B · Todos los canales conectados (Shopee, Magalu, Tienda Nube…)
3. C · También título, descripción y marca

**Propuesta:** A. Un canal y una familia alcanzan para decidir el método y medirlo. Los prompts de marca, título y descripción son generación libre, no mapeo: quedan fuera. Los otros canales replican el mismo diseño con sus propias tablas.

**Archivo:** `decisiones/01-alcance.md`

### 07 · Entra un producto. Sale una propuesta de publicación.

**Sección:** 01 · Punto de partida · **Pauta:** 3 min · **Tipo:** cards

**Objetivo:** Decir el contrato en palabras antes de verlo en código

**En pantalla:**

- Entrada: el producto de Alephee (SKU, nombre, descripción, categoría legacy, atributos)
- Salida: la categoría de Shopee más los atributos con URN, valueId y valor
- Y dos listas más: missing (obligatorios sin dato) y rejected (atributos descartados, con motivo)

**Temas para hablar:** La salida no es la publicación final: es una propuesta de mapeo. Lo que hoy no existe son las dos listas: qué obligatorio quedó sin dato y por qué, y qué atributo del producto se descartó y por qué. Eso es lo que reemplaza al publicar sin atributos.

**Transición:** El mismo contrato, en código.

### 08 · El contrato, en código.

**Sección:** 01 · Punto de partida · **Pauta:** 3 min · **Tipo:** code

**Objetivo:** Mostrar que el contrato es código que se valida, no un acuerdo verbal

**En pantalla:**


**Temas para hablar:** Recorrer las cuatro partes: category puede ser null si no se resuelve; attributes lleva URN, valueId y value; missing y rejected llevan el motivo. extra=forbid significa que si el modelo agrega un campo que no existe, la salida se rechaza. Este archivo es lo primero que se escribió y lo último que debería cambiar.

**Transición:** Decisión 2: cómo se informa lo que no se pudo mapear.

**Código:** `core/src/catalogo/modelos.py` líneas 21–37

```py
class Faltante(_Estricto):
    urn: str = Field(description="URN del atributo obligatorio del canal (o 'category').")
    reason: str


class Descartado(_Estricto):
    legacyId: str = Field(description="id del atributo del producto (sin el prefijo urn:attribute:).")
    reason: str


class Publicacion(_Estricto):
    """Resultado del mapeo de un producto a la publicación del canal."""

    category: str | None = Field(description="URN de la categoría del canal, copiado exacto. null si no se puede resolver.")
    attributes: list[AtributoMapeado]
    missing: list[Faltante] = Field(description="Obligatorios del canal (o la categoría) que no se pudieron completar.")
    rejected: list[Descartado] = Field(description="Atributos del producto que se descartan, con el motivo.")
```

Pydantic con extra="forbid": ningún campo fuera del contrato pasa. Los nombres (valueId, legacyId) son los del formato de publicación de Alephee para no traducir.

### 09 · ¿Qué recibe y qué entrega?

**Sección:** 01 · Punto de partida · **Pauta:** 3 min · **Tipo:** decision

**Objetivo:** Cerrar la decisión 2

**En pantalla:**


**Temas para hablar:** La opción A es el estado actual y su costo ya lo vimos en la tabla de rechazos. La B obliga a que alguien reciba esas listas: quién y cómo es la integración con la plataforma de Alephee, que se trata en el camino a producción. Registrar en decisiones/02-contrato.md.

**Transición:** Con alcance y contrato cerrados, diseñamos el agente.

**Decisión 2:** ¿Cómo se informa lo que no se pudo mapear?

1. A · No se informa: se publica lo que hay (hoy)
2. B · missing y rejected con motivo, en la misma salida
3. C · Un archivo de log aparte que alguien revisa

**Propuesta:** B. El faltante viaja con la publicación: quien revisa ve el producto, el atributo y el motivo juntos. Un log aparte se separa del dato y nadie lo mira. La decisión 12 define qué pasa después con esas listas.

**Archivo:** `decisiones/02-contrato.md`

### 10 · Diseñar antes de escribir.

**Sección:** 02 · Diseñar el agente · **Pauta:** 1 min · **Tipo:** divider

**Objetivo:** Abrir el bloque de diseño

**En pantalla:**

- Siete decisiones que definen la V1

**Temas para hablar:** En este bloque no se corre nada. Se toman las decisiones que la V1 va a implementar a las 11:15: qué tipo de aplicación, cómo se escribe el prompt, dónde corre, qué modelo, con qué stack y cómo se mide. Cada decisión tiene opciones con consecuencias y se cierra antes de pasar a la siguiente.

**Transición:** Primero, qué tipos de aplicación existen.

### 11 · Cuatro formas de usar un modelo.

**Sección:** 02 · Diseñar el agente · **Pauta:** 3 min · **Tipo:** compare

**Objetivo:** Distinguir single prompt, workflow, agente y multiagente

**En pantalla:**

- SINGLE PROMPT | Una llamada, una respuesta. Barato y fácil de evaluar; no consulta nada
- WORKFLOW | Pasos fijos en código; el modelo participa en uno o dos. Predecible
- AGENTE | El modelo decide qué herramienta pedir y cuándo entregar, dentro de un límite de rondas
- MULTIAGENTE | Varios agentes con roles distintos. Solo cuando uno no alcanza

**Temas para hablar:** El proceso actual de Alephee es un workflow: dos llamadas fijas y un merge en código. Un agente se diferencia en que el modelo elige qué consultar y cuándo terminar; el programa le pone el límite. Multiagente es la última opción, no la primera: cada agente extra suma latencia, costo y puntos de fallo.

**Pregunta / participación:** ¿El flujo de hoy es single prompt, workflow o agente?

**Devolución esperada:** Workflow: las llamadas y el merge están fijos en código.

**Transición:** Las tres versiones del día conviven en el mismo runner.

### 12 · Las tres versiones conviven en el mismo runner.

**Sección:** 02 · Diseñar el agente · **Pauta:** 4 min · **Tipo:** code

**Objetivo:** Mostrar que V1, V2 y V3 son intercambiables y comparables

**En pantalla:**


**Temas para hablar:** Lo único que cambia entre versiones es la clase. El runner, el dataset y el evaluador son los mismos: así la comparación de la tarde es justa. Sumar una V4 es registrar una clase más.

**Transición:** Decisión 3.

**Código:** `core/src/catalogo/correr.py` líneas 24–27

```py
def _versiones() -> dict:
    from . import v1, v2, v3

    return {"v1": v1.MapeoV1, "v2": v2.MapeoV2, "v3": v3.MapeoV3}
```

Cada versión es un Workflow que recibe MapeoStart y devuelve MapeoDone. Se comparan sobre el mismo dataset con el mismo evaluador.

### 13 · ¿Single prompt o agente?

**Sección:** 02 · Diseñar el agente · **Pauta:** 4 min · **Tipo:** decision

**Objetivo:** Cerrar la decisión 3

**En pantalla:**

- La opción A ya está en la base preparada (V1) · si gana otra, se discute qué cambia

**Temas para hablar:** B es tentador porque ya sabemos que vamos a necesitar herramientas, pero nos quita la evidencia de por qué. C es la pregunta que siempre hay que hacerse: ¿hace falta un modelo? Para la categoría y los campos mapeados por tabla, no; para elegir el valor equivalente de una lista, sí.

**Transición:** Si empezamos por un prompt, veamos de qué está hecho.

**Decisión 3:** ¿Con qué tipo de aplicación empezamos?

1. A · Single prompt (V1) y agregar herramientas solo cuando un fallo lo justifique
2. B · Agente con herramientas desde el inicio
3. C · Workflow determinista sin modelo

**Propuesta:** A. La V1 muestra qué resuelve el modelo solo y qué no; cada fallo justifica la capa siguiente y queda documentado. C no alcanza: elegir el valor de lista equivalente (por ejemplo, '1' → Sim) necesita interpretación.

**Archivo:** `decisiones/03-tipo-de-aplicacion.md`

### 14 · Un prompt tiene cinco partes.

**Sección:** 02 · Diseñar el agente · **Pauta:** 3 min · **Tipo:** flow

**Objetivo:** Dar un esqueleto para leer cualquier prompt

**En pantalla:**

- Rol: quién es
- Tarea: qué hace y con qué entrada
- Reglas: qué nunca hace
- Formato: cómo entrega
- Cuando falta dato: qué hace

**Temas para hablar:** Las cinco partes sirven para leer el prompt actual y el nuevo. La quinta es la que casi siempre falta: qué hacer cuando no hay dato. Si el prompt no lo dice, el modelo elige por su cuenta, y lo que elige es completar.

**Transición:** El prompt de la V1, parte por parte.

### 15 · El prompt de la V1.

**Sección:** 02 · Diseñar el agente · **Pauta:** 4 min · **Tipo:** code

**Objetivo:** Leer el prompt nuevo con el esqueleto de cinco partes

**En pantalla:**


**Temas para hablar:** Rol en la primera línea; tarea en la segunda; reglas en la lista; el formato no está en el texto porque lo impone la herramienta de entrega (siguiente decisión); y la quinta parte está en las dos reglas de missing y rejected. Las reglas resaltadas son las que el proceso actual no tiene escritas.

**Pregunta / participación:** ¿Qué regla agregarían con lo que saben del catálogo?

**Transición:** Tres prácticas que cambian el resultado.

**Código:** `core/src/catalogo/v1.py` líneas 22–39

```py
INSTRUCCIONES = """\
Eres un especialista en catalogación de autopartes para marketplaces. Recibes un producto del \
catálogo de Alephee (taxonomía de Mercado Libre) y debes adaptarlo a Shopee: elegir la \
categoría de Shopee y mapear los atributos del producto a los atributos que esa categoría espera.

Reglas:
- La categoría y los URN de atributos se copian exactos de las listas que recibes. Nunca inventes un URN.
- Si el atributo del canal tiene una lista de valores, elige el valor equivalente de esa lista y usa su id. \
Si ningún valor es equivalente, no lo completes.
- Si el atributo del canal es de texto libre, usa valueId "0" y el valor del producto tal cual.
- Nunca inventes valores. Solo usas datos presentes en los atributos del producto.
- Los valores "-1", "N/A" o vacíos significan que no hay dato.
- Si un atributo obligatorio del canal no se puede completar, agrégalo a "missing" con el motivo.
- Si un atributo del producto no se puede usar, agrégalo a "rejected" con el motivo.
- Cada atributo del canal aparece una sola vez.

Entrega el resultado llamando a la herramienta entregar_publicacion."""

```

Rol, tarea, reglas negativas explícitas (nunca inventes) y qué hacer cuando falta (missing con motivo). Comparar con el prompt actual de la lámina 3.

### 16 · Buenas prácticas que cambian el resultado.

**Sección:** 02 · Diseñar el agente · **Pauta:** 3 min · **Tipo:** cards

**Objetivo:** Tres prácticas con efecto medible

**En pantalla:**

- Lo estático primero y lo variable al final: habilita la caché de prompt (F4, F7)
- Salida estructurada por esquema, no JSON pedido en el texto
- Decir qué hacer cuando no sabe, no solo qué hacer

**Temas para hablar:** La primera tiene efecto directo en costo: Bedrock cachea el prefijo estable del prompt con cachePoint (F4, mínimo 1.024 tokens para Claude Sonnet 5) y OpenAI hace lo mismo de forma automática sobre el prefijo (F7). El prompt actual pone el producto antes de la lista de categorías: el prefijo cambia en cada llamada y no se cachea nada. Reordenarlo ya bajaría el costo sin cambiar de proveedor; hay que medirlo, no darlo por hecho. Fuentes en docs/warroom/fuentes.md.

**Transición:** La segunda práctica, en código.

### 17 · La salida es una herramienta con esquema.

**Sección:** 02 · Diseñar el agente · **Pauta:** 4 min · **Tipo:** code

**Objetivo:** Mostrar cómo el formato pasa de regla del prompt a contrato

**En pantalla:**


**Temas para hablar:** En vez de pedir JSON válido en el texto, se le da al modelo una herramienta cuyo esquema es la clase Publicacion. El modelo entrega llamando a la herramienta; si lo que entrega no cumple el esquema, falla la validación y se informa el error en vez de publicar algo a medias.

**Transición:** Decisión 4.

**Código:** `core/src/catalogo/v1.py` líneas 41–51

```py
def _entregar(**publicacion) -> str:
    # El resultado se lee de la tool call; la herramienta nunca se ejecuta.
    return "ok"


HERRAMIENTA_SALIDA = FunctionTool.from_defaults(
    fn=_entregar,
    name=NOMBRE_SALIDA,
    description="Entrega el resultado final del mapeo del producto a la publicación del canal.",
    fn_schema=Publicacion,
)
```

fn_schema=Publicacion: el modelo solo puede entregar algo que cumpla el contrato. La función nunca se ejecuta; el resultado se lee de la llamada.

### 18 · ¿Cómo garantizamos el formato?

**Sección:** 02 · Diseñar el agente · **Pauta:** 4 min · **Tipo:** decision

**Objetivo:** Cerrar la decisión 4

**En pantalla:**

- La opción B ya está en la base preparada · si gana otra, se discute qué cambia

**Temas para hablar:** Preguntar al grupo cuántas veces tuvieron que arreglar un JSON mal formado. La opción B existe en todos los proveedores grandes (tool calling o salida estructurada); no depende de Bedrock.

**Transición:** Ahora, dónde va a correr.

**Decisión 4:** ¿Cómo se garantiza que la salida cumpla el contrato?

1. A · Pedir JSON en el texto y parsear (hoy)
2. B · Herramienta con esquema Pydantic: la entrega es una llamada tipada
3. C · Post-procesar la respuesta con expresiones regulares

**Propuesta:** B. El formato deja de ser una regla del prompt y pasa a ser un contrato que el modelo no puede violar. C arregla síntomas: si el modelo omite un campo, la regex no lo inventa.

**Archivo:** `decisiones/04-salida-estructurada.md`

### 19 · Dónde corre: AgentCore o contenedor propio.

**Sección:** 02 · Diseñar el agente · **Pauta:** 3 min · **Tipo:** compare

**Objetivo:** Presentar AgentCore con sus beneficios y sus dudas, con fuente

**En pantalla:**

- Fuentes F1–F3b en docs/warroom/fuentes.md
- AGENTCORE RESUELVE | Runtime sin servidores, identidad, memoria, gateway de herramientas y observabilidad, como servicios separados que se usan juntos o no (F2)
- DUDAS | Arranque en frío sin cifra publicada, sesiones que terminan a los 15 min de inactividad y 8 h máximo (F3b), costo por CPU y memoria de la sesión (F3), región disponible
- ALTERNATIVA | Contenedor o Lambda propios: más control y más trabajo de operación; el agente es el mismo

**Temas para hablar:** AgentCore Runtime corre el contenedor del agente en una microVM por sesión y cobra por el CPU y la memoria que consume la sesión; el CPU baja a cero mientras espera al modelo (F3). Para un chat eso es ideal. Para un batch de miles de productos la pregunta es otra: ¿conviene una sesión larga en el Runtime o un proceso propio de Alephee que llame a Bedrock? No hay cifra pública de arranque en frío; se mide. Las dudas que no se resuelvan hoy van a Juan David.

**Pregunta / participación:** ¿El batch de Alephee tiene horario fijo o corre continuo?

**Transición:** El contrato con AgentCore son dos rutas HTTP.

### 20 · El contrato con AgentCore son dos rutas.

**Sección:** 02 · Diseñar el agente · **Pauta:** 4 min · **Tipo:** code

**Objetivo:** Mostrar que el contrato de despliegue es mínimo y está separado del agente

**En pantalla:**


**Temas para hablar:** Esto es todo lo que AgentCore exige del contenedor (F1): un GET de salud y un POST de invocación. Lo que se ve es el servidor del template, que hoy corre el ChatWorkflow del chat; el agente de catálogo corre por el runner batch y todavía no está conectado al chat. El punto: la lógica del agente vive en otro módulo y se prueba sin servidor; el contrato de despliegue no la condiciona.

**Transición:** Y la infraestructura que lo declara.

**Código:** `core/server.py` líneas 194–199

```py
    async def ping(_: Request) -> JSONResponse:
        return JSONResponse({"status": "Healthy"})

    async def invocations(request: Request):
        payload = await request.json()
        message = payload.get("message")
```

Las dos rutas que exige AgentCore (F1: puerto 8080, imagen ARM64). Hoy este servidor arma el chat del template; conectar el workflow de catálogo (mapear_producto) es un pendiente.

### 21 · La infraestructura declara el Runtime.

**Sección:** 02 · Diseñar el agente · **Pauta:** 4 min · **Tipo:** code

**Objetivo:** Ver que el despliegue es código y se repite

**En pantalla:**


**Temas para hablar:** Infraestructura como código: el Runtime, su imagen y su rol se declaran acá y se despliegan con un comando. El comentario sobre el digest es una lección aprendida: la validación acepta una referencia que la microVM después no puede resolver. Esto ya está probado en el template de Craftech; para Alephee cambia el slug y la cuenta.

**Transición:** Decisión 5.

**Código:** `infra/sst/runtime.ts` líneas 389–406

```ts
export const runtime = new awsnative.bedrockagentcore.Runtime("AgentRuntime", {
  // El recurso exige `[a-zA-Z][a-zA-Z0-9_]*`: stages con guion (p.ej. `pr-123`)
  // lo violarían, así que se sanitiza cualquier carácter fuera de ese alfabeto.
  // El prefijo es el slug del cliente en camelCase (infra/sst/nombres.ts): ese
  // alfabeto no acepta `-`.
  agentRuntimeName: $interpolate`${slugCamel}${$app.stage.replace(/[^a-zA-Z0-9_]/g, "_")}`,
  agentRuntimeArtifact: {
    containerConfiguration: {
      // Digest PURO (repo@sha256:...): el ref canónico de docker-build combina
      // tag y digest (repo:latest@sha256:...) — la validación de CreateRuntime
      // lo acepta, pero el pull real de la microVM no lo resuelve y el
      // contenedor jamás arranca (health check timeout con logs vacíos).
      // El digest cambia por build, así que los updates siguen disparando.
      containerUri: image.ref.apply((r) => r.replace(/:[^@]+@/, "@")),
    },
  },
  networkConfiguration: { networkMode: "PUBLIC" },
  roleArn: role.arn,
```

Imagen ARM64 referenciada por digest, red pública y un rol propio. Se despliega con SST; el modelo llega por variable de entorno.

### 22 · ¿Dónde corre?

**Sección:** 02 · Diseñar el agente · **Pauta:** 4 min · **Tipo:** decision

**Objetivo:** Cerrar la decisión 5 dejando el batch como pregunta abierta con dueño

**En pantalla:**


**Temas para hablar:** No forzar la decisión del batch sin datos: anotar qué medir (duración de una corrida de 30 y de 1.000 productos, costo de sesión, arranque) y quién lo mide.

**Transición:** Siguiente: cómo elegir el modelo.

**Decisión 5:** ¿Dónde corre el agente?

1. A · Hoy en local; el chat de demo en AgentCore; el batch como proceso de Alephee, a decidir con el camino a producción
2. B · Todo en AgentCore desde el inicio
3. C · Todo en la infraestructura actual de Alephee

**Propuesta:** A. Hoy se construye y se mide en local. El chat va a AgentCore porque es su caso natural. Para el batch hace falta medir sesiones, costo y arranque antes de decidir; se retoma a las 16:15.

**Archivo:** `decisiones/05-donde-corre.md`

### 23 · Elegir el modelo: qué pesa en este caso.

**Sección:** 02 · Diseñar el agente · **Pauta:** 3 min · **Tipo:** cards

**Objetivo:** Criterios de elección antes de nombrar modelos

**En pantalla:**

- Seguir reglas y usar herramientas sin inventar: es lo que más falla hoy
- Costo por token con caché de prompt: el presupuesto actual es de USD 350 por mes
- Latencia: no es restricción (hoy el batch tarda 13 s por producto)
- Disponible en la región y habilitado en la cuenta

**Temas para hablar:** El orden importa: primero calidad en lo que falla hoy (alucinar valores, ignorar reglas), después costo con caché, y la latencia al final porque es batch. Un modelo más chico puede ganar en costo y perder en reglas: se decide midiendo sobre el dataset, no por intuición.

**Transición:** Qué hay disponible en Bedrock.

### 24 · Qué hay en Bedrock.

**Sección:** 02 · Diseñar el agente · **Pauta:** 3 min · **Tipo:** table

**Objetivo:** Mostrar el catálogo real de Bedrock sin inventar modelos

**En pantalla:**

- Fuente F6 · Models at a glance · verificado el 30/09/2026
- Proveedor / Familias / Para este caso
- Anthropic / Claude 5.x (Sonnet 5.5, Opus 5.5, Fable 5.1, Sonnet 5…), 4.x (Haiku 4.5…), 3.x / Candidato principal: reglas y tool calling. Sonnet 5 elegido el 25/09; 5.5 y Haiku 4.5 a comparar
- Amazon / Nova 2 Lite, Nova Premier, Pro, Lite, Micro / Alternativa de costo a medir
- OpenAI / GPT-5.x, GPT-6, GPT OSS / Continuidad con el proveedor actual, dentro de AWS
- Meta · Mistral · DeepSeek · Qwen · otros / Llama 3.x y 4, Mistral Large 3, DeepSeek V3.2, Qwen3… / Abiertos; evaluar si el costo lo justifica

**Temas para hablar:** La tabla sale de la página oficial Models at a glance del 30/09 (F6). No es una recomendación de cada uno: es el menú. Lo que importa para elegir es la columna de la derecha y el criterio de la lámina anterior. La disponibilidad por región y la habilitación en la cuenta se verifican en la cuenta que usemos.

**Transición:** El módulo que habla con Bedrock.

### 25 · El único módulo que sabe de Bedrock.

**Sección:** 02 · Diseñar el agente · **Pauta:** 4 min · **Tipo:** code

**Objetivo:** Mostrar dónde se elige el modelo y por qué el ID lleva prefijo

**En pantalla:**


**Temas para hablar:** El modelo se elige en un solo lugar y llega por variable de entorno. El prefijo us. es un inference profile: Bedrock enruta entre regiones de Estados Unidos y es obligatorio para algunos modelos (F5). Las dos banderas de caché activan los cachePoint en system y tools (F4). Cambiar de modelo es cambiar una variable y volver a correr el dataset.

**Transición:** Decisión 6.

**Código:** `core/src/catalogo/llm.py` líneas 7–21

```py
# Converse acepta `us.` y `global.` (verificado 28/09); sin prefijo no hay throughput
# on-demand. `us.` es el que contempla la policy del RuntimeRole.
MODEL_ID_POR_DEFECTO = "us.anthropic.claude-sonnet-5"


def crear_llm(env=os.environ) -> BedrockConverse:
    return BedrockConverse(
        model=env.get("MODEL_ID", MODEL_ID_POR_DEFECTO),
        region_name=env.get("AWS_REGION", "us-east-1"),
        # En local se usa el perfil SSO; en el Runtime no hay perfil y boto3 toma el rol.
        profile_name=env.get("AWS_PROFILE") or None,
        max_tokens=16000,
        system_prompt_caching=True,
        tool_caching=True,
    )
```

Inference profile us.: sin prefijo, Bedrock responde ValidationException por falta de throughput on-demand (F5). Caché de system y tools activada en el cliente.

### 26 · ¿Qué modelo?

**Sección:** 02 · Diseñar el agente · **Pauta:** 4 min · **Tipo:** decision

**Objetivo:** Cerrar la decisión 6 con la prueba de Haiku como pendiente

**En pantalla:**

- Tomada el 25/09 (CLAUDE.md, decisión 6) · hoy se valida o se cambia

**Temas para hablar:** Lo primero que van a preguntar: por qué Sonnet 5 y no 5.5. Respuesta honesta: la decisión es del 25/09 y el modelo está probado en este repo; 5.5 se compara sobre el mismo dataset, no se adopta a ciegas. Anotar las pruebas de 5.5 y de Haiku 4.5 como tareas con dueño. Si Alephee quiere continuidad con OpenAI, los GPT también están en Bedrock (F6): la arquitectura no cambia.

**Transición:** Con qué lo construimos.

**Decisión 6:** ¿Con qué modelo construimos y medimos?

1. A · Claude Sonnet 5 en Bedrock, vía Converse
2. B · Un modelo más chico y barato (Claude Haiku 4.5) y medir
3. C · Seguir con OpenAI y solo reordenar el prompt para la caché

**Propuesta:** A para construir hoy: es la decisión del 25/09 y el ID está verificado en Converse. Claude Sonnet 5.5 también está en Bedrock (F6): compararlo, junto con Haiku 4.5 (B), es una corrida más con otra variable de entorno y queda como pendiente con dueño. C mejora el costo pero no resuelve herramientas, contrato ni control.

**Archivo:** `decisiones/06-modelo.md`

### 27 · Stack y harness.

**Sección:** 02 · Diseñar el agente · **Pauta:** 3 min · **Tipo:** cards

**Objetivo:** Separar el stack del agente de la herramienta con la que lo construimos

**En pantalla:**

- Python + LlamaIndex Workflows: pasos, eventos y herramientas ya resueltos
- BedrockConverse: tool calling y caché de prompt sin código propio
- Harness de desarrollo: propone cambios en el código; Gastón los revisa y corre los tests

**Temas para hablar:** Dos cosas distintas: el stack con el que corre el agente (Python, LlamaIndex, Bedrock) y el harness con el que lo construimos hoy, un entorno de desarrollo asistido por un modelo que propone cambios. El harness no es el agente ni decide nada: cada cambio que propone pasa por revisión y por los tests. No depende de un proveedor concreto.

**Pregunta / participación:** ¿Qué revisarían antes de aceptar un cambio propuesto por el harness?

**Devolución esperada:** Que resuelva la regla acordada, que pase los tests y que no toque datos reales.

**Transición:** Un Workflow de un paso, en código.

### 28 · Un Workflow de un paso.

**Sección:** 02 · Diseñar el agente · **Pauta:** 4 min · **Tipo:** code

**Objetivo:** Mostrar el patrón de inyección que hace testeable al agente

**En pantalla:**


**Temas para hablar:** La clase recibe el LLM por el constructor. Eso permite probar cada paso con un doble sin AWS y correr contra Bedrock cambiando una línea. Es el patrón que se repite en V2 y V3.

**Transición:** Decisión 7.

**Código:** `core/src/catalogo/v1.py` líneas 76–83

```py
class MapeoV1(Workflow):
    def __init__(self, llm, **kwargs):
        # `llm` es un BedrockConverse (catalogo/llm.py) o un doble en los tests.
        super().__init__(**kwargs)
        self.llm = llm

    @step
    async def mapear(self, ev: MapeoStart) -> MapeoDone:
```

El LLM se inyecta: en los tests es un doble, en producción es Bedrock. El workflow no sabe de proveedores.

### 29 · ¿Con qué lo construimos?

**Sección:** 02 · Diseñar el agente · **Pauta:** 4 min · **Tipo:** decision

**Objetivo:** Cerrar la decisión 7

**En pantalla:**

- Tomada el 28/09 (CLAUDE.md, decisión 9) · hoy se valida

**Temas para hablar:** Dejar claro que la decisión es de continuidad, no de superioridad: AgentCore funciona con cualquier framework (F2). Lo que no se negocia es el patrón: LLM inyectado y pasos testeables.

**Transición:** Última decisión antes de construir: cómo sabemos si está bien hecho.

**Decisión 7:** ¿Qué stack usamos para el agente?

1. A · Python + LlamaIndex Workflows + BedrockConverse
2. B · Llamadas directas al SDK, sin framework (como hoy)
3. C · Otro framework de agentes (Strands, LangGraph…)

**Propuesta:** A. Es el stack del template que Craftech ya opera: el workflow no conoce Bedrock y cada paso se prueba con dobles. B repite el código de loop, herramientas y caché que un framework ya trae. C es válido; se elige A por continuidad con lo que ya está probado.

**Archivo:** `decisiones/07-stack.md`

### 30 · ¿Cuándo está bien hecho?

**Sección:** 02 · Diseñar el agente · **Pauta:** 3 min · **Tipo:** cards

**Objetivo:** Acordar la métrica antes de escribir código

**En pantalla:**

- Esquema de Shopee y salida esperada MOCK · validar con el equipo de catálogo
- Exacto: categoría correcta, ni sobra ni falta atributo, nada fuera de dominio, sin duplicados y faltantes informados
- Además se reportan precisión y recall de atributos, valores inválidos, tokens y segundos
- Dataset: 30 productos reales con su publicación actual; el esquema de atributos de Shopee y el expected son simulados

**Temas para hablar:** La vara es estricta a propósito. Pero el expected es mock: se construyó a partir de la publicación actual limpia, así que hereda sus omisiones y castiga aciertos que hoy nadie mapea. Por eso los exactos van a ser bajos en todas las versiones y hay que leer también inválidos, duplicados y faltantes. El esquema oficial de Shopee y la validación con catálogo son pendientes.

**Transición:** La métrica, en código.

### 31 · La métrica en código.

**Sección:** 02 · Diseñar el agente · **Pauta:** 4 min · **Tipo:** code

**Objetivo:** Mostrar que la métrica es código que todos pueden leer y discutir

**En pantalla:**


**Temas para hablar:** Siete condiciones en un and. Si alguien discute la vara, se discute acá y se vuelve a evaluar sin llamar al modelo (scripts/reevaluar.py). La evaluación no cambia para favorecer a una versión.

**Transición:** Decisiones 8 y 9.

**Código:** `core/src/catalogo/evaluacion.py` líneas 24–34

```py
    @property
    def exacto(self) -> bool:
        return (
            self.categoria_ok
            and self.fp == 0
            and self.fn == 0
            and not self.invalidos
            and not self.duplicados
            and not self.faltantes_no_detectados
            and not self.faltantes_de_mas
        )
```

Un caso es exacto solo si todo se cumple a la vez. Es determinista: no llama a ningún modelo.

### 32 · ¿Cuál es el número que aceptamos?

**Sección:** 02 · Diseñar el agente · **Pauta:** 4 min · **Tipo:** decision

**Objetivo:** Cerrar la decisión 8 con un número escrito

**En pantalla:**


**Temas para hablar:** Escribir el número en la pizarra antes de la V1. Si el grupo quiere exigir exactos (B), advertir que con el expected mock ninguna versión los supera, incluida la actual (7 de 30), y que el 28/09 las versiones dieron 5, 4 y 4: la prueba quedaría planteada para fallar por la vara, no por el agente.

**Transición:** Y con qué datos.

**Decisión 8:** ¿Qué criterio de éxito acordamos para la prueba de las 16:15?

1. A · Cero valores inválidos, cero duplicados y todo obligatorio informado en los 30; los exactos se reportan pero no son condición hasta validar el expected con catálogo
2. B · Exactos iguales o mayores al 80 %
3. C · Solo precisión y recall de atributos

**Propuesta:** A. Con expected mock, 'exacto' castiga aciertos que hoy nadie mapea: el 28/09 el proceso actual dio 7 y las versiones 5, 4 y 4. Los inválidos, duplicados y obligatorios sin informar sí son errores seguros y hoy hay 47, 5 y 2. El número final se fija en la sala.

**Archivo:** `decisiones/08-criterio-de-exito.md`

### 33 · ¿Con qué dataset?

**Sección:** 02 · Diseñar el agente · **Pauta:** 4 min · **Tipo:** decision

**Objetivo:** Cerrar la decisión 9 y pasar a construir

**En pantalla:**


**Temas para hablar:** Pedir al grupo que elija el caso guía para las demos (propuesta: 88904447, el del Código OEM). Pausa de 11:00; a las 11:15 se construye la V1 con todo lo decidido.

**Transición:** Pausa. Volvemos con la V1.

**Decisión 9:** ¿Sobre qué datos construimos y medimos?

1. A · Los 30 reales del zip, con esquema y expected mock rotulados
2. B · Solo los 10 casos mock de borde
3. C · Esperar el esquema oficial de Shopee para empezar

**Propuesta:** A. Son productos reales con publicaciones reales y rechazos reales de Shopee. Lo simulado queda rotulado y se valida con catálogo después. Los 10 mock quedan como tests de borde.

**Archivo:** `decisiones/09-dataset.md`

### 34 · V1 · el agente responde.

**Sección:** 03 · V1 · el agente responde · **Pauta:** 1 min · **Tipo:** divider

**Objetivo:** Abrir la V1 con la expectativa correcta

**En pantalla:**

- Solo instrucciones. Se espera que falle, y esos fallos justifican lo que sigue.

**Temas para hablar:** La V1 implementa las decisiones 1 a 9: single prompt, salida por herramienta con esquema, Claude Sonnet 5 por Converse, LlamaIndex Workflows, medida con el evaluador sobre los 30 reales. No usa las tablas de referencia a propósito: queremos ver qué resuelve el modelo solo. Recordar la regla del día: no se pasa al bloque siguiente con algo roto, pero un resultado de negocio incorrecto no es algo roto, es evidencia.

**Transición:** El paso único de la V1.

### 35 · Una llamada, una entrega.

**Sección:** 03 · V1 · el agente responde · **Pauta:** 4 min · **Tipo:** code

**Objetivo:** Recorrer el paso completo: mensaje, llamada, tool call, validación

**En pantalla:**


**Temas para hablar:** Cuatro momentos: se arma el mensaje con el producto y el contexto del canal; una sola llamada al modelo con la herramienta de entrega obligatoria; se buscan las llamadas a entregar_publicacion; se valida contra Publicacion. Las dos salidas de error (no llamó, salida fuera de contrato) son resultados, no excepciones: el runner las cuenta. Lo que no está acá: ninguna tabla, ninguna consulta. Todo lo que el modelo sabe del canal viaja en el mensaje.

**Pregunta / participación:** ¿Qué pasa si el modelo responde con texto en vez de llamar a la herramienta?

**Devolución esperada:** MapeoDone con error explícito. El caso cuenta como no entregado, no como publicado.

**Transición:** Lo corremos sobre el caso guía.

**Código:** `core/src/catalogo/v1.py` líneas 83–100

```py
    async def mapear(self, ev: MapeoStart) -> MapeoDone:
        respuesta = await self.llm.achat_with_tools(
            tools=[HERRAMIENTA_SALIDA],
            user_msg=mensaje_producto(ev.producto),
            chat_history=[ChatMessage(role="system", content=INSTRUCCIONES)],
            tool_required=True,
        )
        uso = uso_de(respuesta)
        llamadas = [
            ll
            for ll in self.llm.get_tool_calls_from_response(respuesta, error_on_no_tool_call=False)
            if ll.tool_name == NOMBRE_SALIDA
        ]
        if not llamadas:
            return MapeoDone(publicacion=None, uso=uso, error=f"El modelo no llamó a {NOMBRE_SALIDA}")
        try:
            publicacion = Publicacion.model_validate(llamadas[0].tool_kwargs)
        except ValidationError as exc:
```

tool_required=True: el modelo tiene que entregar por la herramienta. Si no la llama o la entrega no cumple el contrato, se informa el error; nunca se publica a medias.

### 36 · Demo · un caso real por V1.

**Sección:** 03 · V1 · el agente responde · **Pauta:** 5 min · **Tipo:** demo

**Objetivo:** Ver una salida real y leerla con el contrato en la mano

**En pantalla:**


**Temas para hablar:** Antes de correr, pedir una predicción: ¿qué va a poner en Código OEM? Correr y leer la salida en el orden de la lista. Si Bedrock no responde (sesión SSO vencida, throttling), abrir la corrida guardada y decirlo: es una corrida vieja, anterior a las correcciones del 28/09. Después, el lote completo corre en segundo plano mientras seguimos.

**Transición:** Qué falló y qué capa lo resuelve.

```bash
scripts/correr.sh --version v1 --datos real --caso error-88904447
```

**Mirar:**

- La categoría elegida frente a la de reference_category
- Cada atributo: ¿de dónde salió el valor? ¿Está en la lista del canal?
- missing y rejected: ¿informa lo que no pudo o completó igual?
- Tokens de entrada: todo el contexto del canal viaja en cada llamada

**Respaldo:** resultados/v1-real-20260928-173758.json (corrida del 28/09, anterior a las correcciones)

### 37 · Qué falló en V1 y qué capa lo resuelve.

**Sección:** 03 · V1 · el agente responde · **Pauta:** 3 min · **Tipo:** table

**Objetivo:** Convertir cada fallo de la V1 en la justificación de una capa

**En pantalla:**

- Corrida del 28/09 · 30 reales (fila 1: caso MOCK 09) · anterior a las correcciones · expected MOCK
- Fallo / Dónde se vio / Capa que lo resuelve
- Categoría inventada cuando no hay referencia / Caso mock 09 (sin categoría de origen) / V2 · la tabla por herramienta
- Valor fuera de la lista del canal / 19 valores en los 30 reales / V3 · guardrail
- Obligatorio sin informar en missing / 2 casos en los 30 reales / V3 · guardrail
- ~22.000 tokens de entrada por producto / Todos los casos / V2 · herramientas + caché de prompt

**Temas para hablar:** Esto es lo que la V1 compra: evidencia. La categoría inventada es el fallo que justifica la V2: sin referencia, la respuesta tiene que ser determinista, no creativa. Los valores fuera de lista y los obligatorios sin informar justifican la V3: una regla escrita en el prompt no garantiza que se cumpla; hace falta comprobarla en código. Y los 22.000 tokens por producto son el costo de mandar todo el canal en cada llamada. Comparar con la columna Hoy: 47 inválidos.

**Pregunta / participación:** ¿Alguno de estos fallos les sorprende? ¿Cuál esperaban?

**Transición:** Almuerzo. A las 13:15, herramientas.

### 38 · V2 · herramientas.

**Sección:** 04 · V2 · herramientas · **Pauta:** 1 min · **Tipo:** divider

**Objetivo:** Retomar después del almuerzo y abrir la V2

**En pantalla:**

- El agente consulta antes de decidir.

**Temas para hablar:** Recapitular en una frase: la V1 responde sola y falla donde necesita datos que no tiene. La V2 le da herramientas para consultar las tablas de referencia y el esquema del canal. El prompt deja de llevar el canal entero: el agente pide solo lo que necesita para este producto.

**Transición:** Qué es una herramienta.

### 39 · Una herramienta es una función que el modelo pide y el código ejecuta.

**Sección:** 04 · V2 · herramientas · **Pauta:** 3 min · **Tipo:** flow

**Objetivo:** Definir herramienta sin jerga

**En pantalla:**

- El modelo pide buscar_categoria('urn:category:1106872')
- El programa ejecuta la función: consulta la tabla
- Devuelve {encontrada: true, urn, name} o {encontrada: false, motivo}
- El modelo sigue con ese dato, no con su memoria

**Temas para hablar:** El modelo no ejecuta nada: redacta un pedido con nombre y argumentos, el programa lo ejecuta y le devuelve el resultado como un mensaje más. Por eso la herramienta es determinista y el modelo no. Hay herramientas de lectura (consultar) y de acción (publicar); hoy todas las nuestras son de lectura. Que la herramienta exista no obliga al modelo a usarla ni a respetarla: la V3 revisa la entrega contra el esquema del canal, pero imponer por código lo que dice la tabla de atributos es un pendiente.

**Transición:** La fuente se abstrae.

### 40 · La fuente se abstrae; las herramientas no cambian.

**Sección:** 04 · V2 · herramientas · **Pauta:** 4 min · **Tipo:** code

**Objetivo:** Mostrar el punto de integración con Alephee

**En pantalla:**


**Temas para hablar:** Tres consultas: categoría destino por id legacy, destinos de un atributo legacy y esquema de una categoría del canal. Eso es todo lo que el agente necesita de Alephee. La API pública v2 alcanza para leer el producto (F8) pero no expone estas tablas: la integración real es una FuenteCatalogo nueva contra lo que Maximiliano exponga.

**Pregunta / participación:** ¿Dónde viven hoy estas tres consultas en la plataforma de Alephee?

**Transición:** Cómo se describe una herramienta.

**Código:** `core/src/catalogo/herramientas.py` líneas 17–34

```py
class FuenteCatalogo(Protocol):
    def categoria_destino(self, id_legacy: str) -> dict | None: ...

    def destinos_atributo(self, id_legacy: str) -> list[dict]: ...

    def esquema(self, categoria_urn: str) -> dict | None: ...


class FuenteArchivos:
    """Lee data/mock o data/real (según DATA_DIR). Hace de API interna de Alephee."""

    def categoria_destino(self, id_legacy: str) -> dict | None:
        return datos.cargar_referencia_categorias().get(datos.id_categoria(id_legacy))

    def destinos_atributo(self, id_legacy: str) -> list[dict]:
        return datos.cargar_referencia_atributos().get(datos.id_legacy(id_legacy), [])

    def esquema(self, categoria_urn: str) -> dict | None:
```

Hoy FuenteArchivos lee data/real; mañana una clase que llame a la base o a un endpoint interno de Alephee. Las herramientas y el agente no se tocan.

### 41 · Una herramienta bien descrita.

**Sección:** 04 · V2 · herramientas · **Pauta:** 4 min · **Tipo:** code

**Objetivo:** Buenas prácticas de diseño de herramientas

**En pantalla:**


**Temas para hablar:** Tres reglas: nombre que diga qué hace, descripción con un ejemplo del argumento y salida negativa explícita con motivo. Una herramienta que devuelve null cuando no encuentra invita al modelo a inventar; una que devuelve encontrada: false con motivo le da algo que repetir en missing.

**Transición:** Decisión 10: qué decide la tabla y qué decide el agente.

**Código:** `core/src/catalogo/herramientas.py` líneas 42–48

```py
def crear_herramientas(fuente: FuenteCatalogo) -> list[FunctionTool]:
    def buscar_categoria(categoria_legacy: str) -> str:
        """Devuelve la categoría de Shopee que la tabla reference_category asigna a la categoría
        legacy del producto (por ejemplo 'urn:category:734701'). Si la tabla no la tiene, lo dice."""
        fila = fuente.categoria_destino(categoria_legacy)
        if fila is None:
            return _json({"encontrada": False, "motivo": "la categoría legacy no está en reference_category"})
```

El docstring es lo que lee el modelo: qué devuelve, con qué formato de entrada y qué pasa si no encuentra. La respuesta negativa es explícita, nunca vacía.

### 42 · ¿Qué decide la tabla y qué decide el agente?

**Sección:** 04 · V2 · herramientas · **Pauta:** 4 min · **Tipo:** decision

**Objetivo:** Cerrar la decisión 10

**En pantalla:**

- En la base preparada: la categoría se fija en código (V3); los campos de la tabla los aplica el modelo por instrucción

**Temas para hablar:** B es el error más común: dejar que el modelo mejore un mapeo que el equipo de catálogo mantiene a mano. Si la tabla está mal, se corrige la tabla. C ya se descartó en la decisión 3. Ser exacto sobre el estado: la V3 fija la categoría en código; los campos mapeados por tabla todavía dependen de que el modelo respete la herramienta, y el guardrail solo revisa el esquema. Si la sala quiere imponerlos por código, es un cambio acotado en _al_entregar y queda como pendiente.

**Transición:** El loop del agente y su límite.

**Decisión 10:** ¿Qué decide la tabla y qué decide el agente?

1. A · La tabla fija la categoría y los campos; el agente solo elige el valor equivalente de la lista y cubre lo que la tabla no tiene
2. B · El agente puede corregir la tabla si cree que está mal
3. C · Todo por tabla; sin modelo

**Propuesta:** A. La tabla manda (acuerdo del 25/08 con Juan David). Hoy la categoría se impone en código (V3) y la tabla de atributos la consulta el agente por herramienta, desambiguada por categoría en código; imponer también los campos por código es el siguiente paso. Lo que la tabla no cubre (valores de lista, atributos sin referencia) es lo único que decide el agente.

**Archivo:** `decisiones/10-tabla-vs-agente.md`

### 43 · El loop tiene un límite y una salida garantizada.

**Sección:** 04 · V2 · herramientas · **Pauta:** 4 min · **Tipo:** code

**Objetivo:** Mostrar el control del loop agéntico

**En pantalla:**


**Temas para hablar:** Esto es lo que convierte un modelo con herramientas en un agente controlado: un límite de rondas y una última ronda forzada a entregar. Sin esto, un agente puede consultar para siempre o terminar sin respuesta. Seis no es una garantía de calidad: es una garantía de que termina. Lo que entrega todavía puede estar mal; eso es la V3.

**Transición:** Dónde se paga el costo: la caché de prompt.

**Código:** `core/src/catalogo/v2.py` líneas 82–96

```py
        for ronda in range(MAX_RONDAS):
            # En la última ronda solo queda la herramienta de entrega: nunca termina sin respuesta.
            ultima = ronda == MAX_RONDAS - 1
            respuesta = await self.llm.achat_with_tools(
                tools=[HERRAMIENTA_SALIDA] if ultima else [*self.herramientas, HERRAMIENTA_SALIDA],
                user_msg=None,
                chat_history=historial,
                tool_required=True,
                allow_parallel_tool_calls=not ultima,
            )
            for clave, valor in uso_de(respuesta).items():
                uso[clave] = uso.get(clave, 0) + valor
            llamadas = self.llm.get_tool_calls_from_response(respuesta, error_on_no_tool_call=False)
            usadas += [ll.tool_name for ll in llamadas]
            if not llamadas:
```

Seis rondas como máximo. En la última solo queda la herramienta de entrega y se desactivan las llamadas en paralelo. Si aun así no entrega, el error es explícito.

### 44 · Caché de prompt: lo estático se paga una vez.

**Sección:** 04 · V2 · herramientas · **Pauta:** 4 min · **Tipo:** code

**Objetivo:** Conectar la práctica 'estático primero' con el código y con el costo

**En pantalla:**


**Temas para hablar:** El orden del historial es la práctica de la mañana: system fijo, herramientas fijas, el producto y recién después el punto de caché. Bedrock procesa los checkpoints en orden tools → system → messages y cada ronda del loop lee ese prefijo de caché (F4). Mínimo 1.024 tokens para Sonnet 5, que acá se supera. Una ronda que cambia las herramientas invalida la caché: por eso la última ronda cuesta más.

**Transición:** Los números de la corrida del 28/09.

**Código:** `core/src/catalogo/v2.py` líneas 70–80

```py
    async def mapear(self, ev: MapeoStart) -> MapeoDone:
        por_nombre = {t.metadata.name: t for t in self.herramientas}
        # El punto de caché después del producto hace que cada ronda del loop reuse
        # instrucciones + herramientas + producto en vez de volver a pagarlos.
        historial = [
            ChatMessage(role="system", content=self.instrucciones),
            ChatMessage(role="user", blocks=[TextBlock(text=mensaje_producto(ev.producto)),
                                             CachePoint(cache_control=CacheControl(type="default"))]),
        ]
        uso: dict = {}
        usadas: list[str] = []
```

Instrucciones, herramientas y producto quedan antes del punto de caché: las seis rondas del loop reutilizan ese prefijo en vez de volver a pagarlo (F4).

### 45 · Costo por producto, medido.

**Sección:** 04 · V2 · herramientas · **Pauta:** 3 min · **Tipo:** table

**Objetivo:** Mostrar el efecto de herramientas + caché en tokens y latencia

**En pantalla:**

- Corrida del 28/09 · 30 reales · anterior a las correcciones · tokens de entrada por producto
- Versión / Entrada sin caché / Leída de caché / Segundos
- V1 / ~22.000 / — / 12,3
- V2 / ~1.600 / ~12.000 / 18,3

**Temas para hablar:** La V2 paga 1.600 tokens nuevos por producto y lee 12.000 de caché; la V1 pagaba 22.000 nuevos. La latencia sube porque hay varias rondas: es batch, no importa. Lo que falta para hablar de dólares: sumar escritura de caché, salida y reintentos, y la tasa real de reutilización. No inferir ahorro solo de esta tabla.

**Transición:** Decisión 11: el costo.

### 46 · ¿Cuánto puede costar?

**Sección:** 04 · V2 · herramientas · **Pauta:** 4 min · **Tipo:** decision

**Objetivo:** Cerrar la decisión 11 con la medición como tarea

**En pantalla:**

- Abierta: hoy no hay tope ni medición completa en la base preparada

**Temas para hablar:** Anotar como pendiente la corrida de medición completa con su dueño. Si el grupo quiere un número hoy, dar el de tokens, no el de dólares.

**Transición:** El mismo caso por V2.

**Decisión 11:** ¿Cómo tratamos la restricción de costo del modelo?

1. A · Tope mensual acordado con Alephee y medición por producto: tokens de entrada, salida, caché leída y escrita
2. B · Sin tope: se mide después
3. C · El tope de hoy (USD 350) y publicar sin atributos al agotarse

**Propuesta:** A. Hoy el tope corta la calidad (C). Con caché de prompt y caché por SKU (decisión 13) el costo por producto baja; el número se fija con una corrida completa medida, no con esta tabla.

**Archivo:** `decisiones/11-costo.md`

### 47 · Demo · el mismo caso por V2.

**Sección:** 04 · V2 · herramientas · **Pauta:** 5 min · **Tipo:** demo

**Objetivo:** Comparar V1 y V2 sobre el mismo caso

**En pantalla:**


**Temas para hablar:** Mismo caso que a la mañana, para comparar. Predicción antes de correr: ¿va a usar la referencia de atributos? Leer herramientas_usadas primero. Si el modelo entrega algo fuera de lista, señalarlo: la herramienta no obliga; eso lo arregla la V3. Pausa 14:45.

**Transición:** Pausa. A las 15:00, control.

```bash
scripts/correr.sh --version v2 --datos real --caso error-88904447
```

**Mirar:**

- Qué herramientas pidió y en qué orden (herramientas_usadas)
- La categoría ahora sale de la tabla, no del modelo
- Código OEM: ¿sigue siendo ABS Plastic?
- Tokens leídos de caché frente a los nuevos

**Respaldo:** resultados/v2-real-20260928-181509.json (corrida del 28/09, anterior a las correcciones)

### 48 · V3 · control.

**Sección:** 05 · V3 · control · **Pauta:** 1 min · **Tipo:** divider

**Objetivo:** Abrir la V3

**En pantalla:**

- Qué pasa cuando el agente no sabe.

**Temas para hablar:** La V2 consulta pero no está obligada a respetar lo que consulta. La V3 agrega tres cosas: guardrails en código que revisan cada entrega, memoria de correcciones del equipo de catálogo y caché por SKU para que el mismo producto no se mapee dos veces. Es la versión que reemplaza el publicar sin atributos.

**Transición:** Qué es un guardrail acá.

### 49 · Guardrail: una comprobación en código, no otra instrucción.

**Sección:** 05 · V3 · control · **Pauta:** 3 min · **Tipo:** compare

**Objetivo:** Diferenciar guardrail de regla del prompt

**En pantalla:**

- REVISAR | Lista los problemas en lenguaje claro y se los devuelve al agente, que tiene una ronda para corregir
- LIMPIAR | Red final: descarta lo inválido con motivo y marca los obligatorios que faltan
- NUNCA | Publica un valor fuera de la lista del canal, un -1 ni un duplicado. No verifica que el valor sea verdad: eso sigue siendo del esquema y de catálogo

**Temas para hablar:** Una regla en el prompt es un pedido; un guardrail es una comprobación que no depende de que el modelo obedezca. Dos pasos: primero se le devuelven los problemas al agente para que corrija (una ronda); lo que siga mal se descarta en código. Límite honesto: valida pertenencia al esquema y al dominio por ID; no verifica que el valor sea verdad respecto del producto.

**Transición:** Qué mira el validador.

### 50 · Qué mira el validador.

**Sección:** 05 · V3 · control · **Pauta:** 4 min · **Tipo:** code

**Objetivo:** Leer las cuatro comprobaciones

**En pantalla:**


**Temas para hablar:** Recorrer las cuatro con el caso guía: ABS Plastic en Código OEM pasa la primera (el atributo existe) y la segunda (tiene dato). Shopee lo rechazó con 'value is not linked': el canal sí tiene una lista para ese atributo, pero nuestro esquema MOCK no la tiene, así que la tercera comprobación no puede detectarlo. Ese es el límite: el guardrail detecta lo que el esquema permite detectar. Por eso el esquema oficial de Shopee es un pendiente de primer orden.

**Pregunta / participación:** ¿Qué comprobación agregarían con lo que saben del canal?

**Transición:** La red final.

**Código:** `core/src/catalogo/guardrails.py` líneas 11–23

```py
def _problema(attr: dict, esquema: dict[str, dict]) -> str | None:
    definicion = esquema.get(attr["urn"])
    if definicion is None:
        return f"{attr['urn']} no es un atributo de esta categoría"
    if str(attr.get("value", "")).strip() in SIN_DATO:
        return f"{attr['urn']} tiene un valor sin dato ('{attr.get('value')}'); no se publica"
    dominio = {v["id"]: v["name"] for v in definicion.get("values", [])}
    if dominio and str(attr.get("valueId")) not in dominio:
        return f"{attr['urn']}: el valor '{attr.get('value')}' no está en la lista del canal"
    if dominio and attr.get("value") != dominio[str(attr.get("valueId"))]:
        return f"{attr['urn']}: el nombre del valor no coincide con su ID en el canal"
    return None

```

Cuatro comprobaciones por atributo: que exista en la categoría, que tenga dato, que el valueId esté en la lista del canal y que el nombre coincida con ese ID.

### 51 · La red final no inventa: descarta y marca.

**Sección:** 05 · V3 · control · **Pauta:** 4 min · **Tipo:** code

**Objetivo:** Mostrar que la salida final siempre cumple el contrato

**En pantalla:**


**Temas para hablar:** Después de esta función nunca sale un valor inválido, un duplicado ni un obligatorio sin informar. Lo descartado no desaparece: queda en rejected con el motivo, para que quien revise entienda por qué. Esto es lo que vale medir en la prueba de las 16:15: cero inválidos detectables.

**Transición:** Decisión 12.

**Código:** `core/src/catalogo/guardrails.py` líneas 41–57

```py
def limpiar(publicacion: dict, esquema: dict[str, dict]) -> dict:
    atributos, descartados, vistos = [], list(publicacion["rejected"]), set()
    for a in publicacion["attributes"]:
        motivo = _problema(a, esquema) or (f"{a['urn']} duplicado" if a["urn"] in vistos else None)
        if motivo:
            descartados.append({"legacyId": a["urn"], "reason": f"guardrail: {motivo}"})
            continue
        vistos.add(a["urn"])
        atributos.append(a)
    faltantes = [m for m in publicacion["missing"]
                 if m["urn"] not in vistos and not (m["urn"] == "category" and publicacion["category"])]
    ya = {m["urn"] for m in faltantes}
    faltantes += [{"urn": u, "reason": "obligatorio sin dato válido (guardrail)"}
                  for u, d in esquema.items() if d.get("mandatory") and u not in vistos and u not in ya]
    if not publicacion["category"] and "category" not in ya:
        faltantes.append({"urn": "category", "reason": "sin categoría de referencia; requiere revisión"})
    return {**publicacion, "attributes": atributos, "missing": faltantes, "rejected": descartados}
```

Lo que no pasa va a rejected con el motivo del guardrail; lo obligatorio sin dato válido va a missing; sin categoría de referencia, se pide revisión.

### 52 · ¿Qué hace cuando no sabe?

**Sección:** 05 · V3 · control · **Pauta:** 4 min · **Tipo:** decision

**Objetivo:** Cerrar la decisión 12 y dejar la política de revisión como pendiente

**En pantalla:**

- La opción B ya está en la base preparada (V3) · C se construye sobre B

**Temas para hablar:** Marcar missing no crea solo un circuito de revisión: hoy es una lista en la salida. Quién la mira, dónde y con qué herramienta es una decisión de producto de Alephee, no del agente. Anotar dueño.

**Transición:** Memoria.

**Decisión 12:** ¿Qué hace el agente cuando no puede completar un atributo obligatorio?

1. A · Publicar sin el atributo (hoy)
2. B · Faltante explícito con motivo: la publicación sale con missing y alguien decide
3. C · Bloquear la publicación hasta revisión humana

**Propuesta:** B. Reemplaza el publicar sin atributos. Quién recibe missing y si bloquea o no la publicación es la integración con la plataforma de Alephee: pendiente con dueño. C es una política válida que se puede construir sobre B.

**Archivo:** `decisiones/12-cuando-no-sabe.md`

### 53 · Memoria: correcciones del equipo de catálogo.

**Sección:** 05 · V3 · control · **Pauta:** 3 min · **Tipo:** cards

**Objetivo:** Definir memoria para este agente sin prometer aprendizaje automático

**En pantalla:**

- Una corrección dice: en esta categoría, este valor del producto va a este atributo con este valor del canal
- El agente la consulta como una herramienta más y manda sobre su criterio
- Hoy es un archivo JSON local; en producción, AgentCore Memory o una tabla de Alephee

**Temas para hablar:** Memoria acá no es que el agente aprende solo: es que reutiliza correcciones que una persona del equipo de catálogo cargó explícitamente. Se cargan con un comando; el agente las consulta por categoría. Límite honesto: la persistencia existe; que el modelo siempre las respete depende de que las consulte, por eso la instrucción lo exige y el guardrail revisa después.

**Transición:** Una corrección también vacía la caché.

### 54 · Una corrección vacía la caché.

**Sección:** 05 · V3 · control · **Pauta:** 4 min · **Tipo:** code

**Objetivo:** Mostrar la relación entre memoria y caché

**En pantalla:**


**Temas para hablar:** Dos reglas simples: una corrección nueva reemplaza a la anterior para la misma categoría, atributo y valor; y toda corrección invalida la caché completa. Es la invalidación más simple posible; en producción conviene invalidar por categoría.

**Transición:** Determinismo y caché por SKU.

**Código:** `core/src/catalogo/memoria.py` líneas 31–41

```py
    def corregir(self, categoria: str, urn: str, valor_producto: str, value_id: str, value: str,
                 autor: str = "catálogo") -> dict:
        """Guarda que, en esa categoría, el valor del producto `valor_producto` va a `urn` = `value`."""
        correccion = {"categoria": categoria, "urn": urn, "valorProducto": valor_producto,
                      "valueId": value_id, "value": value, "autor": autor, "fecha": date.today().isoformat()}
        todas = [c for c in self._leer(self.correcciones_archivo)
                 if not (c["categoria"] == categoria and c["urn"] == urn and c["valorProducto"] == valor_producto)]
        self._escribir(self.correcciones_archivo, [*todas, correccion])
        # Una corrección puede cambiar cualquier mapeo guardado: la caché se vacía.
        self._escribir(self.cache_archivo, {})
        return correccion
```

La corrección se guarda con autor y fecha y reemplaza a la anterior del mismo atributo. Como puede cambiar cualquier mapeo guardado, la caché de mapeos se vacía.

### 55 · Mismo SKU, misma salida.

**Sección:** 05 · V3 · control · **Pauta:** 4 min · **Tipo:** code

**Objetivo:** Recorrer el paso de la V3 completo

**En pantalla:**


**Temas para hablar:** Orden del paso: categoría desde la tabla (decisión 10 hecha código), salida temprana si no hay referencia o esquema, caché por SKU y categoría legacy revisada contra el esquema antes de reutilizarla, y recién después el loop de la V2 con guardrails en la entrega. 40 concesionarios venden el mismo SKU de GM: un solo mapeo. Límite: la clave no incluye versión de tablas ni cuenta; eso es la decisión 13.

**Transición:** Decisión 13.

**Código:** `core/src/catalogo/v3.py` líneas 62–79

```py
    async def mapear(self, ev: MapeoStart) -> MapeoDone:
        cats = ev.producto.get("categories") or []
        clave = (ev.producto.get("sku"), id_categoria(cats[0]["urn"]) if cats else "")
        referencia = self.fuente.categoria_destino(clave[1]) if clave[1] else None
        self.categoria_referencia = referencia["urn"] if referencia else None
        self.reintentos = 1
        if not self.categoria_referencia or self.fuente.esquema(self.categoria_referencia) is None:
            return MapeoDone(publicacion={
                "category": self.categoria_referencia, "attributes": [], "rejected": [],
                "missing": [{"urn": "category", "reason": "No hay referencia o esquema de categoría disponible; requiere revisión"}],
            }, herramientas_usadas=["referencia_categoria"])
        if self.usar_cache and (guardado := self.memoria.en_cache(*clave)):
            if guardado["category"] == self.categoria_referencia and not guardrails.revisar(guardado, self._esquema(guardado)):
                return MapeoDone(publicacion=guardrails.limpiar(guardado, self._esquema(guardado)), herramientas_usadas=["cache"])
        done = await MapeoV2.mapear(self, ev)
        if self.usar_cache and done.publicacion is not None:
            self.memoria.guardar_cache(*clave, done.publicacion)
        return done
```

La tabla fija la categoría antes de llamar al modelo; sin referencia o sin esquema, se devuelve el faltante sin invocarlo. Si hay caché válida para SKU + categoría legacy, el modelo tampoco se llama.

### 56 · ¿Cómo garantizamos determinismo?

**Sección:** 05 · V3 · control · **Pauta:** 4 min · **Tipo:** decision

**Objetivo:** Cerrar la decisión 13 con las extensiones de la clave como pendiente

**En pantalla:**

- La opción A ya está en la base preparada (clave SKU + categoría legacy) · falta la invalidación por tablas

**Temas para hablar:** Preguntar al grupo qué cambios deberían invalidar la caché: cambio en el producto, en las tablas, en el esquema del canal. Anotar la lista: es la especificación de la clave de producción.

**Transición:** Demo: corregir y repetir.

**Decisión 13:** ¿Cómo garantizamos que el mismo SKU dé la misma salida?

1. A · Caché por SKU + canal; se invalida al corregir o al cambiar las tablas
2. B · Seed fijo (lo que se intentó hoy; los parámetros exactos siguen sin confirmar)
3. C · Recalcular siempre y aceptar variación

**Propuesta:** A. Un mapeo por SKU y canal. B reduce la variación pero no la elimina y sigue pagando cada corrida. La clave actual es SKU + categoría legacy; falta sumar versión de las tablas y aislamiento por cuenta antes de producción.

**Archivo:** `decisiones/13-determinismo-y-cache.md`

### 57 · Demo · corregir y repetir.

**Sección:** 05 · V3 · control · **Pauta:** 5 min · **Tipo:** demo

**Objetivo:** Ver memoria, guardrails y caché en una sola secuencia

**En pantalla:**


**Temas para hablar:** Elegir con el grupo la corrección a cargar sobre el caso guía (un valor de lista que el modelo eligió mal). Cargarla, correr, leer. Correr de nuevo: debe salir de caché. Si algo falla, abrir la corrida guardada y decir que es vieja.

**Transición:** A las 16:15, la prueba.

```bash
scripts/corregir.sh --categoria <urn-categoria> --urn <urn-atributo> --valor-producto <valor> --value-id <id> --value <nombre>
scripts/correr.sh --version v3 --datos real --caso error-88904447 --cache
```

**Mirar:**

- buscar_correcciones aparece en herramientas_usadas
- El valor corregido sale tal cual lo cargó catálogo
- rejected explica cada descarte del guardrail
- Segunda corrida del mismo caso: herramientas_usadas = [cache] y cero tokens

**Respaldo:** resultados/v3-real-20260928-180524.json (corrida del 28/09, anterior a las correcciones)

### 58 · La prueba.

**Sección:** 06 · La prueba y el camino · **Pauta:** 1 min · **Tipo:** divider

**Objetivo:** Abrir la prueba con el criterio acordado a la vista

**En pantalla:**

- Hoy contra V1, V2 y V3, sobre los 30, con el criterio de la decisión 8.

**Temas para hablar:** Volver a la pizarra: el número de la decisión 8. Las corridas del lote se lanzaron durante los bloques; acá se leen. Si alguna no terminó, se usa la del 28/09 y se dice.

**Transición:** Los resultados.

### 59 · Resultados (se completan en vivo).

**Sección:** 06 · La prueba y el camino · **Pauta:** 3 min · **Tipo:** table

**Objetivo:** Leer los resultados contra el criterio, sin maquillar

**En pantalla:**

- Columna Hoy: publicaciones exportadas, expected MOCK. Las demás se llenan con la corrida del día
- Métrica / Hoy / V1 / V2 / V3
- Casos exactos / 7 / · / · / ·
- Categoría correcta / 28 / · / · / ·
- Valores inválidos (-1 o fuera de lista) / 47 / · / · / ·
- Duplicados / 5 / · / · / ·
- Obligatorios sin informar / 2 / · / · / ·

**Temas para hablar:** Completar las columnas con la corrida del día. Referencia del 28/09, anterior a las correcciones: V1 5 exactos, 19 inválidos; V2 4 exactos, 30 categorías, 9 inválidos; V3 4 exactos, 28 categorías, 0 inválidos, 0 duplicados, 0 obligatorios sin informar. Si los exactos siguen bajos en todas las columnas, decirlo y explicar por qué en la lámina siguiente.

**Transición:** Cómo leer la tabla.

### 60 · Cómo leer la tabla.

**Sección:** 06 · La prueba y el camino · **Pauta:** 3 min · **Tipo:** cards

**Objetivo:** Dar la lectura honesta de los resultados

**En pantalla:**

- Exactos bajos en todas las columnas: el expected hereda las omisiones del proceso actual y castiga aciertos que hoy nadie mapea
- Inválidos y duplicados sí son errores seguros: la V3 no entrega ninguno detectable por este evaluador (28/09)
- Categoría: la V3 dio 28/30 en la corrida vieja; la corrección del 28/09 la fija desde la tabla y hay que volver a medir

**Temas para hablar:** Conclusión defendible: en este ensayo la V3 elimina los errores que estos controles detectan, pero todavía no demuestra mejor exactitud global contra un expected que es mock. Tenemos evidencia de qué controles ayudan y una lista clara de lo que falta para validar con el canal. Un control puede reducir errores quitando información: mirar control y cobertura juntos.

**Pregunta / participación:** ¿Qué evidencia pedirían antes de un piloto con un concesionario?

**Transición:** El camino a producción.

### 61 · Camino a producción.

**Sección:** 06 · La prueba y el camino · **Pauta:** 3 min · **Tipo:** flow

**Objetivo:** Convertir los pendientes en tareas con dueño

**En pantalla:**

- Esquema oficial de Shopee y expected validado con el equipo de catálogo
- Integración: la API pública lee el producto (F8); escribir publicaciones y leer tablas necesita acceso interno
- Decidir dónde corre el batch (decisión 5) y la política de missing (decisión 12)
- Medir el costo completo y fijar el tope (decisión 11); probar Haiku 4.5 (decisión 6)

**Temas para hablar:** Cada punto necesita responsable y fecha; se completan en la última lámina. Retomar las dudas de AgentCore anotadas a la mañana y asignarlas a Juan David. El código queda en el repositorio de Alephee que Rick indique.

**Transición:** Las trece decisiones.

### 62 · Las 13 decisiones (1 a 7).

**Sección:** 06 · La prueba y el camino · **Pauta:** 3 min · **Tipo:** table

**Objetivo:** Cerrar con el registro completo: las decisiones de la mañana

**En pantalla:**

- N / Decisión / Archivo
- 1 / Alcance: un canal, una familia, categoría + atributos / decisiones/01-alcance.md
- 2 / Contrato: missing y rejected con motivo / decisiones/02-contrato.md
- 3 / Tipo de aplicación: single prompt y escalar / decisiones/03-tipo-de-aplicacion.md
- 4 / Salida estructurada por herramienta + Pydantic / decisiones/04-salida-estructurada.md
- 5 / Dónde corre: local hoy, chat en AgentCore, batch a medir / decisiones/05-donde-corre.md
- 6 / Modelo: Claude Sonnet 5; Haiku 4.5 a probar / decisiones/06-modelo.md
- 7 / Stack: Python + LlamaIndex Workflows + BedrockConverse / decisiones/07-stack.md

**Temas para hablar:** Cada archivo tiene contexto, opciones, decisión y razonamiento. Lo que quedó distinto a la propuesta se escribe tal como se decidió en la sala.

**Transición:** Las de la tarde.

### 63 · Las 13 decisiones (8 a 13).

**Sección:** 06 · La prueba y el camino · **Pauta:** 3 min · **Tipo:** table

**Objetivo:** Cerrar con el registro completo: las decisiones de la tarde

**En pantalla:**

- N / Decisión / Archivo
- 8 / Criterio de éxito: el número de la pizarra / decisiones/08-criterio-de-exito.md
- 9 / Dataset: 30 reales con mock rotulado / decisiones/09-dataset.md
- 10 / La tabla manda; el agente elige valores y lo no cubierto / decisiones/10-tabla-vs-agente.md
- 11 / Costo: tope acordado y medición por producto / decisiones/11-costo.md
- 12 / Cuando no sabe: faltante explícito, nunca inventar / decisiones/12-cuando-no-sabe.md
- 13 / Determinismo: caché por SKU + canal con invalidación / decisiones/13-determinismo-y-cache.md

**Temas para hablar:** Este registro es el método repetible: el próximo caso de uso de Alephee arranca por estas trece preguntas, con las respuestas de hoy como punto de partida.

**Transición:** Quién hace qué.

### 64 · Quién hace qué, para cuándo.

**Sección:** 06 · La prueba y el camino · **Pauta:** 1 min · **Tipo:** divider

**Objetivo:** Cerrar con responsables y fechas

**En pantalla:**

- Se completa en la sala.

**Temas para hablar:** Repartir los pendientes del camino a producción entre Alephee, Craftech y AWS, con fecha. Confirmar el repositorio donde queda el código. Agradecer y cerrar a las 17:00; preguntas hasta las 17:30.

**Transición:** Fin.

## Fundamento editorial y revisión

Diseño de esta versión: [diseno-presentacion.md](warroom/diseno-presentacion.md). Revisión editorial de la versión anterior: [revision-agentes.md](warroom/revision-agentes.md).
