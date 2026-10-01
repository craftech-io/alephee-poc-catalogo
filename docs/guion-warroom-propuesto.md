# Guion del warroom · por diapositiva

Versión del 29/09/2026 · 37 diapositivas · 7 secciones. Fuente única: `docs/warroom/diapositivas.json`. Se regenera con `python3 scripts/generar_presentacion.py`.

[Presentación interactiva](presentacion-warroom.html) · [PDF estático](presentacion-warroom.pdf) · [Ficha de participantes](warroom/ficha-participantes.md)

## Dinámica acordada

Gastón conduce una construcción compartida. En parejas, el equipo toma decisiones, ejecuta casos y valida resultados. No se exige programar un agente completo ni rotar a quien conduce. Si falla un entorno, la pareja dirige su prueba en la pantalla principal. Pedir devoluciones de participantes remotos.

Las selecciones, respuestas revelables y temporizadores son ayudas locales de facilitación. No reciben votos remotos ni ejecutan el agente. Las pruebas reales se corren en el repositorio. Los ejemplos DEMO-01 usan reglas e IDs inventados; los resultados históricos siguen rotulados como anteriores a las correcciones nuevas.

## Mapa y tiempos

| Sección | Horario | Diapositivas | Resultado |
|---|---|---|---|
| 01 · Punto de partida | 09:00–09:30 | 1–9 | Ver el error de hoy y acordar qué construimos |
| 02 · Diseñar el agente | 09:30–11:15 | 10–33 | Tomar las decisiones que definen la V1 |
| 03 · V1 · el agente responde | 11:15–12:30 | 34–37 | Construir, correr y leer la primera versión |

Pausa 11:00–11:15; almuerzo 12:30–13:15; pausa 14:45–15:00. El bloque V3 incluye preparación de comparación 16:00–16:15. Margen de preguntas 17:00–17:30 sujeto a confirmación logística.

Los minutos por diapositiva son una pauta para explicaciones y consignas, no un cronograma adicional: el resto de cada bloque se dedica a construcción compartida, demos y discusión. Preservar la hora de cierre. Si falta tiempo, abreviar teoría ya comprendida y abrir las respuestas directamente; mantener prácticas y conclusiones.

## Distribución completa dentro de cada bloque

| Bloque | Diapositivas, consignas y demos | Trabajo reservado | Total |
|---|---:|---|---:|
| 01 · Punto de partida | 29 min | Dolores del equipo y preguntas: 10 min | 39 min |
| 02 · Diseñar el agente | 85 min | Pizarra: tipos de aplicación y dónde corre: 15 min; Pausa 11:00: 15 min | 115 min |
| 03 · V1 · el agente responde | 13 min | Corridas sobre otros casos: 25 min | 38 min |
| 04 · V2 · herramientas | 0 min | Corrida del lote y lectura: 25 min | 25 min |
| 05 · V3 · control | 0 min | Corrida del lote con V3: 20 min | 20 min |
| 06 · La prueba y el camino | 0 min | Documentar decisiones y responsables: 15 min | 15 min |

Las consignas y puestas en común ya están incluidas en los minutos de sus diapositivas. Las reservas son para trabajo adicional dentro del bloque; no duplican la demo indicada en una diapositiva. Son pautas ajustables de esta jornada, no reglas prescritas por los libros.

## Preparación del facilitador

- Elegir tres casos guiados y asignar IDs del dataset a las parejas; no confundirlos con DEMO-01.
- Validar entornos y acceso al modelo antes del día. Tener una corrida guardada identificada como respaldo.
- Para un caso: `scripts/correr.sh --version v1 --datos real --caso <id>`; cambiar versión para comparar el mismo caso.
- En V3, usar copias o tests locales para alterar entradas: no modificar `data/real` ni el lote de comparación.
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

**Sección:** 01 · Punto de partida · **Pauta:** 4 min · **Tipo:** code

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
- 24581199 / Quantity publicado 10 veces / Rechazado: solo admite un valor
- 9 de 30 / Valor -1 publicado como valor / Aceptado por Shopee
- 98550368 / 14 de 15 URN sin sufijo del canal / Aceptado por Shopee

**Temas para hablar:** Los 30 productos del zip: 20 publicados y 10 rechazados. El caso 88904447 es el hilo del día: un material (ABS Plastic) copiado al campo Código OEM. Lo peor no es lo que Shopee rechaza, que al menos avisa, sino lo que acepta mal: un -1 publicado como valor en 9 de 30 y URN sin el sufijo del canal. Nadie se entera hasta que un comprador lo ve.

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

**Sección:** 01 · Punto de partida · **Pauta:** 4 min · **Tipo:** decision

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

**Sección:** 01 · Punto de partida · **Pauta:** 4 min · **Tipo:** code

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

**Sección:** 01 · Punto de partida · **Pauta:** 4 min · **Tipo:** decision

**Objetivo:** Cerrar la decisión 2

**En pantalla:**


**Temas para hablar:** La opción A es el estado actual y su costo ya lo vimos en la tabla de rechazos. La B obliga a que alguien reciba esas listas: quién y cómo es la integración con la plataforma de Alephee, que se trata en el camino a producción. Registrar en decisiones/02-contrato.md.

**Transición:** Con alcance y contrato cerrados, diseñamos el agente.

**Decisión 2:** ¿Cómo se informa lo que no se pudo mapear?

1. A · No se informa: se publica lo que hay (hoy)
2. B · missing y rejected con motivo, en la misma salida
3. C · Un archivo de log aparte que alguien revisa

**Propuesta:** B. El faltante viaja con la publicación: quien revisa ve el producto, el atributo y el motivo juntos. Un log aparte se separa del dato y nadie lo mira.

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


**Temas para hablar:** Esto es todo lo que AgentCore exige del contenedor (F1). El servidor arma el workflow y responde; la lógica del agente está en otro módulo y se prueba sin servidor. En local se corre con un comando; en el Runtime, igual.

**Transición:** Y la infraestructura que lo declara.

**Código:** `core/server.py` líneas 194–199

```py
    async def ping(_: Request) -> JSONResponse:
        return JSONResponse({"status": "Healthy"})

    async def invocations(request: Request):
        payload = await request.json()
        message = payload.get("message")
```

GET /ping y POST /invocations en el puerto 8080, imagen ARM64 (F1). El agente no sabe dónde corre: el mismo código sirve en local y en el Runtime.

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
- Anthropic / Claude 5.x (Sonnet 5, Opus 5.5, Fable 5.1…), 4.x (Haiku 4.5…), 3.x / Candidato principal: reglas y tool calling
- Amazon / Nova 2, Nova Premier/Pro/Lite/Micro / Alternativa de costo a medir
- OpenAI / GPT-5.x, GPT-6, GPT OSS / Continuidad con el proveedor actual, dentro de AWS
- Meta · Mistral · DeepSeek · Qwen · otros / Llama 3.x/4, Mistral Large 3, DeepSeek V3.2, Qwen3… / Abiertos; evaluar si el costo lo justifica

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


**Temas para hablar:** Anotar la prueba de B como tarea con dueño: es la misma corrida con otra variable de entorno. Si Alephee quiere continuidad con OpenAI, los modelos GPT también están en Bedrock (F6): la arquitectura no cambia.

**Transición:** Con qué lo construimos.

**Decisión 6:** ¿Con qué modelo construimos y medimos?

1. A · Claude Sonnet 5 en Bedrock, vía Converse
2. B · Un modelo más chico y barato (Claude Haiku 4.5) y medir
3. C · Seguir con OpenAI y solo reordenar el prompt para la caché

**Propuesta:** A para construir hoy; B queda como prueba pendiente sobre el mismo dataset: si cumple el criterio, gana por costo. C mejora el costo pero no resuelve herramientas, contrato ni control.

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


**Temas para hablar:** Escribir el número en la pizarra antes de la V1. Si el grupo elige B, advertir que el expected mock hace casi imposible el 80 % para cualquier versión, incluida la actual (7 de 30).

**Transición:** Y con qué datos.

**Decisión 8:** ¿Qué criterio de éxito acordamos para la prueba de las 16:15?

1. A · Cero valores inválidos y cero duplicados en los 30; exactos iguales o mejores que el proceso actual
2. B · Exactos iguales o mayores al 80 %
3. C · Solo precisión y recall de atributos

**Propuesta:** A. Con expected mock, 'exacto' castiga aciertos que hoy nadie mapea; los inválidos y duplicados sí son errores seguros y hoy hay 47 y 5. El número final se fija en la sala.

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

- Corrida del 28/09 sobre los 30 reales · anterior a las correcciones · expected MOCK
- Fallo / Dónde se vio / Capa que lo resuelve
- Categoría inventada cuando no hay referencia / Caso mock 09 (sin categoría de origen) / V2 · la tabla por herramienta
- Valor fuera de la lista del canal / 19 valores en los 30 reales / V3 · guardrail
- Obligatorio sin informar en missing / 2 casos en los 30 reales / V3 · guardrail
- ~22.000 tokens de entrada por producto / Todos los casos / V2 · herramientas + caché de prompt

**Temas para hablar:** Esto es lo que la V1 compra: evidencia. La categoría inventada es el fallo que justifica la V2: sin referencia, la respuesta tiene que ser determinista, no creativa. Los valores fuera de lista y los obligatorios sin informar justifican la V3: una regla escrita en el prompt no garantiza que se cumpla; hace falta comprobarla en código. Y los 22.000 tokens por producto son el costo de mandar todo el canal en cada llamada. Comparar con la columna Hoy: 47 inválidos.

**Pregunta / participación:** ¿Alguno de estos fallos les sorprende? ¿Cuál esperaban?

**Transición:** Almuerzo. A las 13:15, herramientas.

## Fundamento editorial y revisión

Ver [revisión de los dos agentes](warroom/revision-agentes.md). Se aplican principios de claridad, audiencia y explicación de Garr Reynolds, Nancy Duarte y Lee LeFever; el número de diapositivas, los tiempos y las parejas son decisiones de esta sesión.
