# Guion del warroom · por diapositiva

Versión del 1/10/2026 · 70 diapositivas · 5 bloques · 13 decisiones. Diseño en `warroom/diseno-presentacion.md`; fuentes externas en `warroom/fuentes.md`. Fuente única: `docs/warroom/diapositivas.json`. Se regenera con `python3 old/deck-tools/regenerar_deck.py` (las herramientas del deck están fuera de git hasta que vuelvan al repositorio).

[Presentación interactiva](presentacion-warroom.html) · [PDF estático](presentacion-warroom.pdf)

## Dinámica acordada

Gastón conduce. El deck es una cadena de 13 decisiones de diseño. Cada tema tiene una lámina de concepto, en varios casos una de código leído del repositorio, y una de decisión que se cierra en la sala antes de seguir. La V1 y la V2 son los puntos donde lo decidido se construye y se corre. Pedir la opinión de quienes están remotos antes de cerrar cada decisión.

Las láminas de código leen el código del repositorio al generar el deck: si el código cambia, hay que regenerar. La propuesta de cada decisión está plegada y se abre después de escuchar al grupo. La decisión final se escribe en `decisiones/NN-titulo.md` y no en el deck. Las columnas de la prueba se completan con los experimentos del día en Langfuse.

## Mapa y tiempos

| Sección | Horario | Diapositivas | Resultado |
|---|---|---|---|
| 01 · Punto de partida | 09:00-09:30 | 1 a 10 | Ver el error de hoy y acordar qué construimos |
| 02 · Diseñar el agente | 09:30-11:15 | 11 a 30 | Tomar las decisiones que definen la V1 |
| 03 · V1 · el agente responde | 11:15-12:30 | 31 a 39 | Construir, correr y leer la primera versión |
| 04 · V2 · tablas y control | 13:15-16:15 | 40 a 63 | Resolver con las tablas lo que saben y controlar lo que decide el agente |
| 05 · La prueba y el camino | 16:15-17:00 | 64 a 70 | Medir contra el criterio y repartir lo que sigue |

Pausa de 11:00 a 11:15, almuerzo de 12:30 a 13:15 y pausa de 14:45 a 15:00. El bloque de la V2 incluye la preparación de la comparación, de 16:00 a 16:15. El margen de preguntas de 17:00 a 17:30 depende de la logística.

Los minutos por diapositiva son una pauta. Preservar la hora de cierre. Si el bloque 2 se pasa, fusionar las láminas de criterios de modelo y catálogo de Bedrock y acortar la de stack; nunca saltar una decisión.

## Distribución completa dentro de cada bloque

| Bloque | Diapositivas y demos | Trabajo reservado | Total |
|---|---:|---|---:|
| 01 · Punto de partida | 27 min | Dolores del equipo y preguntas: 2 min | 29 min |
| 02 · Diseñar el agente | 64 min | Pizarra: dudas de AgentCore para Juan David: 5 min; Pausa 11:00: 15 min | 84 min |
| 03 · V1 · el agente responde | 26 min | Corridas sobre otros casos: 25 min | 51 min |
| 04 · V2 · tablas y control | 75 min | Corrida del lote con la V2 y lectura: 30 min; Pausa 14:45: 15 min; Preguntas y cambios pedidos por la sala: 35 min; Preparar la comparación: 15 min | 170 min |
| 05 · La prueba y el camino | 17 min | Documentar decisiones y responsables: 15 min | 32 min |

Las reservas son para pizarra, corridas del lote y preguntas dentro del bloque. Son pautas ajustables de esta jornada.

## Preparación del facilitador

- Caso guía de las demos: `01-real-calota-aro14` del dataset mock (la calota 94701411). Con el OK de Alephee para los datos reales, `error-88904447` (Código OEM = ABS Plastic). Confirmarlo con el grupo en la decisión 9.
- Validar el acceso al modelo y a Langfuse antes de empezar. Tener un experimento guardado en Langfuse como respaldo.
- Para un caso: `scripts/experiment.sh --version v1 --data real --case <id>`. Cambiar la versión para comparar el mismo caso. Sin el OK de Alephee para los datos reales, usar `--data mock`.
- No modificar `data/real` ni la salida esperada para favorecer una versión.
- Registrar las decisiones en `decisiones/` con contexto, opciones, decisión y razonamiento.
- Lanzar el experimento completo durante los bloques. Con 4 productos a la vez, los 30 tardan unos minutos. Medirlo antes de prometer un horario.

## Bosquejo por diapositiva

### 01 · Un agente que mapea el catálogo a Shopee, decidido paso a paso.

**Sección:** 01 · Punto de partida · **Pauta:** 1 min · **Tipo:** divider

**Objetivo:** Qué tenemos a las 17:00: agente en local, método repetible, 13 decisiones documentadas

**En pantalla:**

- War Room · Alephee × Craftech × AWS · 1/10/2026

**Temas para hablar:** Después de la portada viene la agenda y un producto real: qué entra y qué queremos que salga. A las 17:00 queremos tres cosas. El agente corriendo con el código en el repositorio, un método que sirva para el próximo caso de uso y trece decisiones escritas con su razonamiento. Hoy no damos teoría. Diseñamos y construimos en el mismo orden. Gastón conduce y el grupo decide en cada punto.

**Transición:** El código está en el repositorio.

### 02 · El código está en el repositorio.

**Sección:** 01 · Punto de partida · **Pauta:** 2 min · **Tipo:** cards

**Objetivo:** Que todos puedan seguir el código desde su máquina

**En pantalla:**

- https://github.com/craftech-io/alephee-poc-catalogo
- Repositorio: https://github.com/craftech-io/alephee-poc-catalogo
- El agente: core/src/catalog/, con v1.py y v2.py como punto de entrada
- Versiones: la rama main y los tags reinicio-v1 y reinicio-v2
- Los grafos de los Workflows: docs/workflows.md, generados desde el código

**Temas para hablar:** Todo lo que vamos a ver hoy está en este repositorio, en la rama main. El agente vive en core/src/catalog, y cada lámina de código dice de qué archivo y de qué líneas sale. La V1 y la V2 tienen su tag. El repositorio es privado: si alguien de Alephee no tiene acceso, lo damos ahora.

**Transición:** Lo que vamos a hacer hoy.

### 03 · Lo que vamos a hacer hoy.

**Sección:** 01 · Punto de partida · **Pauta:** 3 min · **Tipo:** compare

**Objetivo:** Ubicar al grupo en el recorrido del día, por temas

**En pantalla:**

- Decidimos, construimos y medimos. Cada bloque cierra con una versión que funciona.
- 1 · PUNTO DE PARTIDA | El error de hoy, el alcance y el contrato
- 2 · DISEÑAR EL AGENTE | Tipo de aplicación, prompt, dónde corre, modelo, stack y criterio de éxito
- 3 · V1 · EL AGENTE RESPONDE | Una sola llamada al modelo, sin herramientas: qué resuelve solo y qué no
- 4 · V2 · TABLAS Y CONTROL | Las tablas en código, un agente que decide valores, validación, correcciones y caché
- 5 · LA PRUEBA | El proceso de hoy contra la V1 y la V2, y el camino a producción

**Temas para hablar:** Son cinco bloques. Los dos primeros terminan en la V1. El cuarto construye la V2: las tablas en código y el control de lo que decide el agente. La prueba mide todo con el criterio que acordamos antes de escribir código. Horarios para quien conduce: 09:00 punto de partida, 09:30 diseño, 11:15 V1, 13:15 V2 y 16:15 prueba. Hay pausa a las 11:00, almuerzo de 12:30 a 13:15 y otra pausa a las 14:45. El cierre técnico es a las 17:00 y quedan preguntas hasta las 17:30.

**Transición:** Un producto real para ver qué entra y qué queremos que salga.

### 04 · De un producto de Alephee a una publicación de Shopee.

**Sección:** 01 · Punto de partida · **Pauta:** 3 min · **Tipo:** table

**Objetivo:** Que todos vean, con un producto real, qué entra y qué queremos que salga

**En pantalla:**

- Caso real · SKU 88904447 · Correia dentada · catálogo GM Brasil (Mercado Libre Brasil) → Shopee Brasil
- Entra (Alephee) / Sale (Shopee) / Quién lo resuelve
- Categoría: Correias Dentadas / Distribuição e Correias / La tabla
- Condición del ítem: Novo / Condition: New / La tabla y la lista del canal
- Tiempo de garantía: 6 meses / Duração da Garantia: 6 Months / El agente
- Código OEM: no viene / Faltante, con motivo (hoy: ABS Plastic, rechazado por Shopee) / El guardrail

**Temas para hablar:** Esto es lo que queremos lograr. Entra el producto tal como está en Alephee. Los nombres de los atributos están en español porque así los define la plataforma. Los valores y la categoría están en portugués porque el catálogo es de GM Brasil y usa la taxonomía de Mercado Libre Brasil. Sale la publicación para Shopee Brasil, que mezcla portugués e inglés según el atributo. Cruzar idiomas es parte del problema. Las tres primeras filas son lo que Alephee publicó hoy para este SKU. La cuarta es lo que queremos: hoy en Código OEM salió ABS Plastic y Shopee lo rechazó. La columna de la derecha adelanta el día: tabla, agente y guardrail. El esquema de atributos de Shopee con el que validamos es MOCK y sale de estas publicaciones.

**Pregunta / participación:** ¿Qué fila les parece la más difícil de automatizar?

**Transición:** Cómo lo hace hoy el proceso actual.

### 05 · Hoy: dos llamadas, un merge y un presupuesto que se agota.

**Sección:** 01 · Punto de partida · **Pauta:** 3 min · **Tipo:** cards

**Objetivo:** Entender el proceso actual sin juzgarlo

**En pantalla:**

- Categoría: la tabla reference_category y, si no alcanza, el modelo elige
- Atributos: dos llamadas en paralelo (con y sin referencia) y un merge por código
- USD 350 por mes: cuando se agota, se publica sin atributos

**Temas para hablar:** Contar el flujo actual como lo explicó Maximiliano. La categoría sale de la tabla y el modelo entra solo cuando la tabla no la tiene. Los atributos van en dos llamadas en paralelo, porque un solo prompt era demasiado largo, y después un merge por código prioriza la que usó la referencia. Tarda 13 segundos por producto en batch, y eso no es un problema. Lo que duele es el presupuesto: cuando se agota, la publicación sale sin atributos. El modelo exacto y sus parámetros siguen sin confirmar.

**Pregunta / participación:** ¿Qué parte de este flujo les da más trabajo hoy?

**Devolución esperada:** Anotar las respuestas en la pizarra: se retoman en la prueba final.

**Transición:** Qué pasó con esas publicaciones en Shopee.

### 06 · Lo que Shopee rechazó y lo que aceptó mal.

**Sección:** 01 · Punto de partida · **Pauta:** 3 min · **Tipo:** table

**Objetivo:** Ver errores reales: los que rechaza el canal y los que acepta igual

**En pantalla:**

- Datos reales · WarRoom.zip del 24/09 · 30 productos
- Caso / Qué salió / Qué pasó
- 88904447 / Código OEM = ABS Plastic / Rechazado: el valor no pertenece al atributo
- 93221445 / Inmetro Certification con varios valores / Rechazado: solo admite un valor
- 9 de 30 / Valor -1 publicado como valor / Aceptado por Shopee
- 98550368 / 14 de 15 URN sin sufijo del canal / Aceptado por Shopee

**Temas para hablar:** Son 30 productos: 20 publicados y 10 rechazados. El caso 88904447 nos acompaña todo el día. Copió un material, ABS Plastic, al campo Código OEM, y Shopee lo rechazó porque ese valor no corresponde al atributo. El 24581199 publicó Quantity diez veces, y Shopee lo rechazó por otro motivo: faltaba Auto-Part Number. Lo que Shopee rechaza al menos avisa. Peor es lo que acepta mal: un -1 publicado como valor en 9 de 30 casos y URN sin el sufijo del canal. Nadie se entera hasta que lo ve un comprador.

**Pregunta / participación:** ¿Cuál de estos errores les parece más grave para el negocio?

**Transición:** Cómo vamos a trabajar hoy.

### 07 · ¿Qué hace y qué no hace?

**Sección:** 01 · Punto de partida · **Pauta:** 3 min · **Tipo:** decision

**Objetivo:** Cerrar la decisión 1 antes de hablar de contrato

**En pantalla:**


**Temas para hablar:** Presentar las tres opciones con su consecuencia. B multiplica tablas y esquemas sin cambiar el método. C mezcla dos problemas distintos: mapear y redactar. Abrir la propuesta solo después de escuchar al grupo. La decisión queda escrita con su razonamiento.

**Pregunta / participación:** ¿Hay alguna familia de productos que convenga más que otra para empezar?

**Devolución esperada:** Registrar la decisión y la familia elegida.

**Transición:** Si el alcance es ese, ¿qué entra y qué sale?

**Decisión 1:** ¿Qué alcance tiene el agente del war room?

1. A · Un canal (Shopee) y una familia de productos: categoría + atributos
2. B · Todos los canales conectados (Shopee, Magalu, Tienda Nube…)
3. C · También título, descripción y marca

**Propuesta:** A. Un canal y una familia alcanzan para decidir el método y medirlo. Marca, título y descripción son redacción libre y no mapeo, así que quedan fuera. Los otros canales repiten el mismo diseño con sus propias tablas.

**Archivo:** `decisiones/01-alcance.md`

### 08 · Entra un producto. Sale una propuesta de publicación.

**Sección:** 01 · Punto de partida · **Pauta:** 3 min · **Tipo:** cards

**Objetivo:** Decir el contrato en palabras antes de verlo en código

**En pantalla:**

- Entrada: el producto de Alephee (SKU, nombre, descripción, categoría legacy, atributos)
- Salida: la categoría de Shopee más los atributos con URN, valueId y valor
- Y dos listas más: missing (obligatorios sin dato) y rejected (atributos descartados, con motivo)

**Temas para hablar:** La salida es una propuesta de mapeo, todavía no es la publicación final. Lo nuevo son las dos listas. Una dice qué obligatorio quedó sin dato y por qué. La otra dice qué atributo del producto se descartó y por qué. Con eso dejamos de publicar sin atributos sin que nadie se entere.

**Transición:** El contrato, en código.

### 09 · El contrato, en código.

**Sección:** 01 · Punto de partida · **Pauta:** 3 min · **Tipo:** code

**Objetivo:** Ver el contrato como código y no como texto

**En pantalla:**


**Temas para hablar:** Este es el contrato de salida, escrito como modelo Pydantic. Los nombres de los campos son los de Alephee, así la salida se compara y se guarda sin traducir. extra="forbid" hace que cualquier campo de más sea un error. Las dos listas nuevas, missing y rejected, llevan siempre un motivo.

**Transición:** Decisión 2: cómo se informa lo que no se pudo mapear.

**Código:** `core/src/catalog/models.py` líneas 38 a 53

```py
# A product attribute that was discarded, with the reason. Rejections added by the guardrails
# carry the channel urn here instead, because the validator does not know the source attribute.
class RejectedAttribute(_Strict):
    legacyId: str = Field(description="Product attribute id, without the 'urn:attribute:' prefix.")
    reason: str


# The full answer for one product. In V2 the category is fixed by `reference_category` and the
# guardrails force it back if the model returns a different one.
class Listing(_Strict):
    """Result of mapping one product to a channel listing."""

    category: str | None = Field(description="Channel category URN, copied exactly. Null if it cannot be resolved.")
    attributes: list[MappedAttribute]
    missing: list[MissingAttribute] = Field(description="Mandatory channel attributes (or the category) that could not be filled.")
    rejected: list[RejectedAttribute] = Field(description="Product attributes that are discarded, with the reason.")
```

Listing es lo que entrega la V1. Si el modelo devuelve algo que no cumple este esquema, el Workflow informa el error.

### 10 · ¿Qué recibe y qué entrega?

**Sección:** 01 · Punto de partida · **Pauta:** 3 min · **Tipo:** decision

**Objetivo:** Cerrar la decisión 2

**En pantalla:**


**Temas para hablar:** La opción A es lo que pasa hoy, y su costo ya lo vimos en la tabla de rechazos. La B obliga a que alguien reciba esas listas. Quién y cómo es parte de la integración con la plataforma de Alephee, que vemos en el camino a producción.

**Transición:** Con alcance y contrato cerrados, diseñamos el agente.

**Decisión 2:** ¿Cómo se informa lo que no se pudo mapear?

1. A · No se informa: se publica lo que hay (hoy)
2. B · missing y rejected con motivo, en la misma salida
3. C · Un archivo de log aparte que alguien revisa

**Propuesta:** B. El faltante viaja con la publicación, y quien revisa ve el producto, el atributo y el motivo juntos. Un log aparte se separa del dato y nadie lo mira. La decisión 12 define qué pasa después con esas listas.

**Archivo:** `decisiones/02-contrato.md`

### 11 · Diseñar antes de escribir.

**Sección:** 02 · Diseñar el agente · **Pauta:** 1 min · **Tipo:** divider

**Objetivo:** Abrir el bloque de diseño

**En pantalla:**

- Siete decisiones que definen la V1

**Temas para hablar:** En este bloque no corremos nada. Tomamos las decisiones que la V1 implementa a las 11:15: tipo de aplicación, prompt, dónde corre, modelo, stack y cómo se mide. Cada decisión tiene opciones con consecuencias y se cierra antes de pasar a la siguiente.

**Transición:** Primero, qué tipos de aplicación existen.

### 12 · Cuatro formas de usar un modelo.

**Sección:** 02 · Diseñar el agente · **Pauta:** 3 min · **Tipo:** compare

**Objetivo:** Distinguir single prompt, workflow, agente y multiagente

**En pantalla:**

- SINGLE PROMPT | Una llamada y una respuesta. Barato y fácil de evaluar, pero no consulta nada
- WORKFLOW | Pasos fijos en código, y el modelo participa en uno o dos. Es predecible
- AGENTE | El modelo decide qué herramienta pedir y cuándo entregar, con un límite de rondas
- MULTIAGENTE | Varios agentes con roles distintos. Solo cuando uno no alcanza

**Temas para hablar:** El proceso actual de Alephee es un workflow: dos llamadas fijas y un merge en código. En un agente, el modelo elige qué consultar y cuándo terminar, y el programa le pone el límite. Multiagente es la última opción. Cada agente extra suma latencia, costo y lugares donde fallar.

**Pregunta / participación:** ¿El flujo de hoy es single prompt, workflow o agente?

**Devolución esperada:** Workflow: las llamadas y el merge están fijos en código.

**Transición:** Decisión 3.

### 13 · ¿Single prompt o agente?

**Sección:** 02 · Diseñar el agente · **Pauta:** 4 min · **Tipo:** decision

**Objetivo:** Cerrar la decisión 3

**En pantalla:**

- La V1 se construye con la opción A · si gana otra, vemos qué cambia

**Temas para hablar:** B es tentador porque ya sabemos que vamos a necesitar herramientas, pero nos quita la evidencia de por qué. C es la pregunta que siempre hay que hacerse: ¿hace falta un modelo? Para la categoría y los campos que ya están en la tabla, no. Para elegir el valor equivalente de una lista, sí.

**Transición:** Si empezamos por un prompt, veamos de qué está hecho.

**Decisión 3:** ¿Con qué tipo de aplicación empezamos?

1. A · Una sola llamada estructurada (V1) y sumar herramientas solo cuando un fallo lo justifique
2. B · Agente con herramientas desde el inicio
3. C · Workflow determinista, sin modelo

**Propuesta:** A. La V1 muestra qué resuelve el modelo solo y qué no, y cada fallo justifica la capa siguiente. También es la buena práctica de LlamaIndex: si el modelo no tiene herramientas que elegir, no hace falta un agente. El FunctionAgent entra en la V2. C no alcanza, porque elegir el valor equivalente de una lista (por ejemplo, '1' es Sim) necesita interpretación.

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

**Temas para hablar:** Con estas cinco partes leemos el prompt actual y el nuevo. La quinta casi siempre falta: qué hacer cuando no hay dato. Si el prompt no lo dice, el modelo decide solo, y casi siempre decide completar.

**Transición:** Tres prácticas que cambian el resultado.

### 15 · Buenas prácticas que cambian el resultado.

**Sección:** 02 · Diseñar el agente · **Pauta:** 3 min · **Tipo:** cards

**Objetivo:** Tres prácticas con efecto medible

**En pantalla:**

- Lo fijo primero y lo variable al final: así funciona la caché de prompt (F4, F7)
- Salida con esquema, en lugar de pedir JSON en el texto
- Decir qué hacer cuando no sabe, además de qué hacer

**Temas para hablar:** La primera baja el costo directamente. Bedrock guarda en caché el comienzo del prompt que no cambia, marcado con un cachePoint (F4). Para Claude Sonnet 5 el mínimo es 1.024 tokens, y la caché dura 5 minutos desde el último uso. OpenAI hace lo mismo de forma automática (F7). El prompt actual pone el producto antes de la lista de categorías, así que el comienzo cambia en cada llamada y no se cachea nada. Reordenarlo ya bajaría el costo sin cambiar de proveedor, pero hay que medirlo antes de darlo por hecho. En la V1 lo vemos en Langfuse, en cada traza. Fuentes en docs/warroom/fuentes.md.

**Transición:** Decisión 4.

### 16 · ¿Cómo garantizamos el formato?

**Sección:** 02 · Diseñar el agente · **Pauta:** 4 min · **Tipo:** decision

**Objetivo:** Cerrar la decisión 4

**En pantalla:**

- La V1 usa la opción B · si gana otra, vemos qué cambia

**Temas para hablar:** Preguntar cuántas veces tuvieron que arreglar un JSON mal formado. La salida estructurada existe en todos los proveedores grandes, así que no depende de Bedrock. El Workflow de la V1 cierra con un evento tipado, MappingCompleted, que trae el Listing.

**Transición:** Salida estructurada en LlamaIndex.

**Decisión 4:** ¿Cómo se garantiza que la salida cumpla el contrato?

1. A · Pedir JSON en el texto y parsearlo (hoy)
2. B · Salida estructurada con un modelo Pydantic: el modelo devuelve un Listing validado
3. C · Corregir la respuesta después con expresiones regulares

**Propuesta:** B. El formato deja de ser un pedido en el prompt y pasa a ser un contrato. En LlamaIndex es as_structured_llm(Listing): el modelo responde por tool calling y la librería valida contra el esquema. Si la salida no cumple, el Workflow devuelve el error en lugar de publicar algo a medias. C arregla síntomas: si el modelo omite un campo, la expresión regular no lo inventa.

**Archivo:** `decisiones/04-salida-estructurada.md`

### 17 · Salida estructurada en LlamaIndex.

**Sección:** 02 · Diseñar el agente · **Pauta:** 3 min · **Tipo:** code

**Objetivo:** Ver cómo se garantiza el formato

**En pantalla:**


**Temas para hablar:** Esta es la opción B en código. as_structured_llm(Listing) le pide al modelo que responda con el esquema, por tool calling, y LlamaIndex valida la respuesta. Si falla, el step devuelve el error en texto. La única excepción son las credenciales vencidas: ahí se corta todo, porque el producto siguiente fallaría igual.

**Transición:** Ahora, dónde va a correr.

**Código:** `core/src/catalog/v1.py` líneas 84 a 98

```py
@step
async def map(self, ev: ContextReady) -> MappingCompleted:
    """Call the model with `Listing` as the output schema and return what it produced."""
    try:
        # `as_structured_llm` sends `Listing` as the schema and parses the answer into it;
        # an answer that does not fit the schema raises here instead of leaking bad JSON.
        response = await self.llm.as_structured_llm(Listing).achat(ev.messages)
    except Exception as exc:  # noqa: BLE001, any failure becomes a reported error, except credentials
        # Expired credentials would fail every remaining product: let them stop the run.
        if is_auth_error(exc):
            raise
        return MappingCompleted(listing=None, error=f"{type(exc).__name__}: {exc}")
    # `raw` holds the parsed `Listing` instance. V1 has no guardrails: the listing is returned
    # as the model wrote it, which is what the V1 column measures.
    return MappingCompleted(listing=response.raw)
```

Una sola llamada. response.raw ya es un Listing validado.

### 18 · Dónde corre: AgentCore o contenedor propio.

**Sección:** 02 · Diseñar el agente · **Pauta:** 3 min · **Tipo:** compare

**Objetivo:** Presentar AgentCore con sus beneficios y sus dudas, con fuente

**En pantalla:**

- Fuentes F1 a F3b en docs/warroom/fuentes.md
- AGENTCORE RESUELVE | Runtime sin servidores, identidad, memoria, gateway de herramientas y observabilidad. Son servicios separados que se pueden usar juntos o no (F2)
- DUDAS | No hay cifra publicada de arranque en frío. Las sesiones terminan a los 15 minutos sin actividad y duran 8 horas como máximo (F3b). Se cobra por CPU y memoria de la sesión (F3), y hay que confirmar la región
- ALTERNATIVA | Contenedor o Lambda propios: más control y más trabajo de operación. El agente es el mismo

**Temas para hablar:** AgentCore Runtime corre el contenedor del agente en una microVM por sesión. Cobra por el CPU y la memoria de la sesión, y el CPU baja a cero mientras espera al modelo (F3). Para un chat eso funciona muy bien. Para un batch de miles de productos la pregunta cambia: ¿conviene una sesión larga en el Runtime o un proceso de Alephee que llame a Bedrock? No hay cifra pública de arranque en frío, así que hay que medirlo. Las dudas que no cerremos hoy van a Juan David.

**Pregunta / participación:** ¿El batch de Alephee tiene horario fijo o corre continuo?

**Transición:** La infraestructura completa, en un dibujo.

### 19 · La infraestructura, de punta a punta.

**Sección:** 02 · Diseñar el agente · **Pauta:** 2 min · **Tipo:** diagram

**Objetivo:** Mostrar todas las piezas de AWS y separar lo que hay de lo que falta

**En pantalla:**


**Temas para hablar:** Arriba está el camino del chat. El widget llama al BFF, que valida el token, aplica el guardrail de entrada y los topes, y encola el mensaje. El worker invoca el Runtime, que llama a Bedrock y a las herramientas por el Gateway. El Runtime también tiene dos herramientas propias, map_product_v1 y map_product_v2, que corren la V1 y la V2. La V2 lee las correcciones y la caché de dos tablas de DynamoDB, corrections y mapping_cache. En el stack, los recursos se llaman CatalogCorrections y CatalogMappingCache. Abajo a la derecha, punteado, está el batch de catálogo. Hoy corre en local como experimento de Langfuse, y su lugar en producción es la decisión 5. La franja de abajo es el monitoreo: logs y métricas en CloudWatch, y trazas, prompts y experimentos en Langfuse.

**Pregunta / participación:** ¿Qué piezas ya tiene Alephee y cuáles reemplazaríamos?

**Transición:** Decisión 5.

**Diagrama (cajas):**

- Widget de chat: apps/web · packages/widget
- BFF · Lambda: auth HMAC · topes · guardrail de entrada
- SQS FIFO: MensajesCola · con DLQ
- Worker · Lambda: InvokeAgentRuntime · timeout 3 min
- AgentCore Runtime: contenedor ARM64 desde ECR · ChatWorkflow · core/server.py · map_product_v1 y map_product_v2
- DynamoDB: Messages · Sessions · Limits · corrections · mapping_cache
- AgentCore Gateway: tools MCP · SigV4
- Amazon Bedrock: Claude Sonnet 5 · us-east-1 · guardrail de salida
- API del cliente: target OpenAPI (demo)
- Knowledge Base: S3 Vectors · ToolDocumentos
- Escalamiento: ToolEscalamiento
- Batch de catálogo · hoy local: scripts/experiment.sh → V1 / V2 · experimentos y trazas en Langfuse · producción: a decidir (decisión 5)
- Observabilidad · CloudWatch, X-Ray y Langfuse: logs y métricas en CloudWatch · trazas del agente, prompts y experimentos en Langfuse

Es la infraestructura del template en infra/sst. El chat se despliega en la cuenta sandbox con el stage warroom, y las trazas del agente van a Langfuse. AgentCore Memory se sacó del stack.

### 20 · ¿Dónde corre?

**Sección:** 02 · Diseñar el agente · **Pauta:** 4 min · **Tipo:** decision

**Objetivo:** Cerrar la decisión 5 dejando el batch como pregunta abierta con dueño

**En pantalla:**


**Temas para hablar:** No forzar la decisión del batch sin datos. Anotar qué medir: cuánto tarda una corrida de 30 productos y una de 1.000, cuánto cuesta la sesión y cuánto tarda en arrancar. Y anotar quién lo mide.

**Transición:** Siguiente: cómo elegir el modelo.

**Decisión 5:** ¿Dónde corre el agente?

1. A · Hoy en local y el chat de demo en AgentCore (stage warroom). El batch como proceso de Alephee se decide con el camino a producción
2. B · Todo en AgentCore desde el inicio
3. C · Todo en la infraestructura actual de Alephee

**Propuesta:** A. Hoy construimos y medimos en local. El chat va a AgentCore porque es su caso natural. Para el batch hay que medir sesiones, costo y arranque antes de decidir, y lo retomamos a las 16:15.

**Archivo:** `decisiones/05-donde-corre.md`

### 21 · Elegir el modelo: qué pesa en este caso.

**Sección:** 02 · Diseñar el agente · **Pauta:** 3 min · **Tipo:** cards

**Objetivo:** Criterios de elección antes de nombrar modelos

**En pantalla:**

- Seguir reglas sin inventar valores: es lo que más falla hoy
- Costo por token con caché de prompt: el presupuesto actual es de USD 350 por mes
- Latencia: no es una restricción (hoy el batch tarda 13 s por producto)
- Que esté disponible en la región y habilitado en la cuenta

**Temas para hablar:** El orden importa. Primero, calidad en lo que falla hoy: inventar valores e ignorar reglas. Después, costo con caché. La latencia va al final porque es batch. Un modelo más chico puede ganar en costo y perder en reglas, y eso se decide midiendo sobre el dataset.

**Transición:** Qué hay disponible en Bedrock.

### 22 · Qué hay en Bedrock.

**Sección:** 02 · Diseñar el agente · **Pauta:** 3 min · **Tipo:** table

**Objetivo:** Mostrar el catálogo real de Bedrock sin inventar modelos

**En pantalla:**

- Fuente F6 · Models at a glance · verificado el 30/09/2026
- Proveedor / Familias / Para este caso
- Anthropic / Claude 5.x (Sonnet 5.5, Opus 5.5, Fable 5.1, Sonnet 5…), 4.x (Haiku 4.5…), 3.x / Candidato principal: reglas y tool calling. Sonnet 5 elegido el 25/09; 5.5 y Haiku 4.5 a comparar
- Amazon / Nova 2 Lite, Nova Premier, Pro, Lite, Micro / Alternativa de costo a medir
- OpenAI / GPT-5.x, GPT-6, GPT OSS / Continuidad con el proveedor actual, dentro de AWS
- Meta · Mistral · DeepSeek · Qwen · otros / Llama 3.x y 4, Mistral Large 3, DeepSeek V3.2, Qwen3… / Abiertos; evaluar si el costo lo justifica

**Temas para hablar:** La tabla sale de la página oficial Models at a glance, revisada el 30/09 (F6). Es el menú, no una recomendación. Para elegir importan la columna de la derecha y el criterio de la lámina anterior. La región y la habilitación se verifican en la cuenta que usemos.

**Transición:** Decisión 6.

### 23 · ¿Qué modelo?

**Sección:** 02 · Diseñar el agente · **Pauta:** 4 min · **Tipo:** decision

**Objetivo:** Cerrar la decisión 6 con la prueba de Haiku como pendiente

**En pantalla:**

- Tomada el 25/09 (CLAUDE.md, decisión 6) · hoy se valida o se cambia

**Temas para hablar:** Lo primero que van a preguntar es por qué Sonnet 5 y no 5.5. La decisión es del 25/09 y el modelo ya está probado en este repositorio. El 5.5 se compara sobre el mismo dataset antes de adoptarlo. Anotar las pruebas de 5.5 y de Haiku 4.5 como tareas con dueño. Si Alephee quiere seguir con OpenAI, los GPT también están en Bedrock (F6) y la arquitectura no cambia.

**Transición:** El único módulo que sabe de Bedrock.

**Decisión 6:** ¿Con qué modelo construimos y medimos?

1. A · Claude Sonnet 5 en Bedrock, vía Converse
2. B · Un modelo más chico y barato (Claude Haiku 4.5) y medir
3. C · Seguir con OpenAI y solo reordenar el prompt para la caché

**Propuesta:** A para construir hoy. Es la decisión del 25/09 y el ID está verificado en Converse. Claude Sonnet 5.5 también está en Bedrock (F6). Compararlo con Haiku 4.5 (B) es una corrida más del experimento con otra variable de entorno, y queda como pendiente con dueño. C mejora el costo pero no resuelve el contrato ni el control.

**Archivo:** `decisiones/06-modelo.md`

### 24 · El único módulo que sabe de Bedrock.

**Sección:** 02 · Diseñar el agente · **Pauta:** 3 min · **Tipo:** code

**Objetivo:** Mostrar que cambiar de modelo es una variable

**En pantalla:**


**Temas para hablar:** El modelo se elige con una variable de entorno. Para probar Sonnet 5.5 o Haiku 4.5 alcanza con cambiar MODEL_ID y correr el mismo experimento. El resto del código recibe el modelo inyectado y no sabe que abajo hay Bedrock.

**Transición:** Con qué lo construimos.

**Código:** `core/src/catalog/llm.py` líneas 12 a 26

```py
# Converse accepts the `us.` and `global.` profiles; the bare model id has no on-demand throughput.
DEFAULT_MODEL_ID = "us.anthropic.claude-sonnet-5"
_AUTH_ERRORS = (NoCredentialsError, SSOError, TokenRetrievalError, UnauthorizedSSOTokenError)


def create_llm(env=os.environ) -> BedrockConverse:
    """Build the Bedrock Converse client from the environment (MODEL_ID, AWS_REGION, AWS_PROFILE)."""
    return BedrockConverse(
        model=env.get("MODEL_ID", DEFAULT_MODEL_ID),
        region_name=env.get("AWS_REGION", "us-east-1"),
        # Local runs use the SSO profile; inside the Runtime boto3 takes the role.
        profile_name=env.get("AWS_PROFILE") or None,
        # High ceiling on purpose: an answer cut off at the limit is not a valid Listing.
        max_tokens=16000,
    )
```

En local usa el perfil SSO; en el Runtime de AgentCore toma el rol de la cuenta.

### 25 · Stack y harness.

**Sección:** 02 · Diseñar el agente · **Pauta:** 3 min · **Tipo:** cards

**Objetivo:** Separar el stack del agente de la herramienta con la que lo construimos

**En pantalla:**

- Python + LlamaIndex Workflows: pasos y eventos tipados, y cada paso se prueba por separado
- BedrockConverse: salida estructurada, tool calling y caché de prompt sin código propio
- Langfuse: el prompt versionado, las trazas de cada llamada y los experimentos
- Harness de desarrollo: propone cambios en el código, y Gastón los revisa y corre los tests

**Temas para hablar:** Hay dos cosas distintas. Una es el stack con el que corre el agente: Python, LlamaIndex, Bedrock y Langfuse. La otra es el harness con el que lo construimos hoy, un entorno de desarrollo asistido por un modelo que propone cambios. El harness no es el agente ni decide nada. Cada cambio que propone pasa por revisión y por los tests, y no depende de un proveedor concreto.

**Pregunta / participación:** ¿Qué revisarían antes de aceptar un cambio propuesto por el harness?

**Devolución esperada:** Que resuelva la regla acordada, que pase los tests y que no toque datos reales.

**Transición:** Decisión 7.

### 26 · ¿Con qué lo construimos?

**Sección:** 02 · Diseñar el agente · **Pauta:** 4 min · **Tipo:** decision

**Objetivo:** Cerrar la decisión 7

**En pantalla:**

- Tomada el 28/09 · Langfuse se sumó el 1/10 · hoy se valida

**Temas para hablar:** Aclarar que es una decisión de continuidad. AgentCore funciona con cualquier framework (F2). Lo que no se negocia es el patrón: el modelo se inyecta y cada paso se puede probar. Langfuse se sumó el 1/10 para guardar el prompt y correr la evaluación. Con Langfuse Cloud, los productos y las respuestas salen de AWS, y eso hay que acordarlo con Alephee.

**Transición:** Última decisión antes de construir: cómo sabemos si está bien hecho.

**Decisión 7:** ¿Qué stack usamos para el agente?

1. A · Python + LlamaIndex Workflows + BedrockConverse, con Langfuse para prompts y evaluación
2. B · Llamadas directas al SDK, sin framework (como hoy)
3. C · Otro framework de agentes (Strands, LangGraph…)

**Propuesta:** A. Es el stack del template que Craftech ya opera. El Workflow no conoce Bedrock y cada paso se prueba con dobles. B repite el código de loop, herramientas y caché que un framework ya trae. C es válido, y elegimos A por continuidad con lo que ya está probado.

**Archivo:** `decisiones/07-stack.md`

### 27 · ¿Cuándo está bien hecho?

**Sección:** 02 · Diseñar el agente · **Pauta:** 3 min · **Tipo:** cards

**Objetivo:** Acordar la métrica antes de escribir código

**En pantalla:**

- Esquema de Shopee y salida esperada MOCK · validar con el equipo de catálogo
- Exacto: categoría correcta, ningún atributo de más ni de menos, nada fuera de la lista del canal, sin duplicados y con los faltantes informados
- También medimos precisión y recall de atributos, valores inválidos, tokens y segundos, todo en Langfuse
- Dataset: 30 productos reales con su publicación actual. El esquema de Shopee y la salida esperada son simulados

**Temas para hablar:** La vara es estricta a propósito. Pero la salida esperada es mock: la armamos a partir de la publicación actual limpia, así que hereda sus omisiones y castiga aciertos que hoy nadie mapea. Por eso los exactos van a salir bajos en todas las versiones, y hay que mirar también inválidos, duplicados y faltantes. Cada versión corre como experimento en Langfuse, al lado del proceso de hoy. El esquema oficial de Shopee y la validación con catálogo quedan pendientes.

**Transición:** La métrica, en código.

### 28 · La métrica, en código.

**Sección:** 02 · Diseñar el agente · **Pauta:** 3 min · **Tipo:** code

**Objetivo:** Ver que la vara es la misma para todas las versiones

**En pantalla:**


**Temas para hablar:** Esta es la regla del exacto. Un caso es exacto solo si se cumplen todas las condiciones a la vez. En Langfuse aparece como un score por producto, junto a los inválidos, los duplicados, la precisión y el recall.

**Transición:** Decisiones 8 y 9.

**Código:** `core/src/catalog/evaluation.py` líneas 25 a 42

```py
class CaseResult:
    """Score of one case: attribute counts (true/false positives, false negatives) and the
    urns behind each kind of error, so a Langfuse comment can name them."""

    category_ok: bool
    tp: int
    fp: int
    fn: int
    invalid: list[str] = field(default_factory=list)
    duplicates: list[str] = field(default_factory=list)
    missing_not_detected: list[str] = field(default_factory=list)
    extra_missing: list[str] = field(default_factory=list)

    @property
    def exact(self) -> bool:
        """All checks pass at once: the strictest metric of the table."""
        return (self.category_ok and self.fp == 0 and self.fn == 0 and not self.invalid
                and not self.duplicates and not self.missing_not_detected and not self.extra_missing)
```

La misma función mide el proceso de hoy y cada versión.

### 29 · ¿Cuál es el número que aceptamos?

**Sección:** 02 · Diseñar el agente · **Pauta:** 4 min · **Tipo:** decision

**Objetivo:** Cerrar la decisión 8 con un número escrito

**En pantalla:**


**Temas para hablar:** Escribir el número en la pizarra antes de la V1. Si el grupo quiere exigir exactos (B), advertir que con esta salida esperada ni el proceso de hoy llega: saca 7 de 30. La prueba quedaría armada para fallar por la vara y no por el agente.

**Transición:** Y con qué datos.

**Decisión 8:** ¿Qué criterio de éxito acordamos para la prueba de las 16:15?

1. A · Cero valores inválidos, cero duplicados y todos los obligatorios informados en los 30. Los exactos se informan, pero no son condición hasta validar la salida esperada con catálogo
2. B · Exactos iguales o mayores al 80 %
3. C · Solo precisión y recall de atributos

**Propuesta:** A. Con una salida esperada mock, el exacto castiga aciertos que hoy nadie mapea: el proceso actual saca 7 de 30. Los inválidos, duplicados y obligatorios sin informar sí son errores seguros, y hoy hay 47, 5 y 2. El número final se fija en la sala.

**Archivo:** `decisiones/08-criterio-de-exito.md`

### 30 · ¿Con qué dataset?

**Sección:** 02 · Diseñar el agente · **Pauta:** 4 min · **Tipo:** decision

**Objetivo:** Cerrar la decisión 9 y pasar a construir

**En pantalla:**


**Temas para hablar:** Pedir al grupo que elija el caso guía de las demos. Con los datos reales, la propuesta es 88904447, el del Código OEM. Mientras Alephee no confirme que pueden ir a Langfuse Cloud, las demos usan el caso 01-real-calota-aro14 del dataset mock. A las 11:00 hay pausa, y a las 11:15 construimos la V1 con todo lo decidido.

**Transición:** Pausa. Volvemos con la V1.

**Decisión 9:** ¿Sobre qué datos construimos y medimos?

1. A · Los 30 reales del zip, con esquema y expected mock rotulados
2. B · Solo los 10 casos mock de borde
3. C · Esperar el esquema oficial de Shopee para empezar

**Propuesta:** A. Son productos reales, con publicaciones reales y rechazos reales de Shopee. Lo simulado queda rotulado y se valida con catálogo después. Los 10 casos mock quedan como pruebas de borde.

**Archivo:** `decisiones/09-dataset.md`

### 31 · V1 · el agente responde.

**Sección:** 03 · V1 · el agente responde · **Pauta:** 1 min · **Tipo:** divider

**Objetivo:** Abrir la V1 con la expectativa correcta

**En pantalla:**

- Una sola llamada al modelo, sin herramientas. Esperamos que falle, y esos fallos justifican lo que sigue.

**Temas para hablar:** La V1 junta las decisiones 1 a 9. Es un Workflow de LlamaIndex con dos pasos. El primero, prepare, arma el mensaje: el catálogo de Shopee al principio, para que entre en la caché, y el producto al final. El segundo, map, hace una llamada estructurada y devuelve un Listing validado. El prompt de sistema vive en Langfuse y la evaluación corre ahí. La V1 no usa las tablas de referencia a propósito, porque queremos ver qué resuelve el modelo solo. La regla del día sigue: no pasamos al bloque siguiente con algo roto. Si la V1 se equivoca en un atributo, eso no frena el día. Lo anotamos como evidencia para la V2.

**Transición:** La V1 por dentro.

### 32 · La V1 por dentro.

**Sección:** 03 · V1 · el agente responde · **Pauta:** 3 min · **Tipo:** diagram

**Objetivo:** Dar el mapa de la V1 antes de leer el código

**En pantalla:**


**Temas para hablar:** Verde es código y violeta es el modelo. El step prepare arma el mensaje: el prompt de sistema sale de Langfuse, después va el catálogo de Shopee y al final el producto. El step map hace una sola llamada estructurada a Claude Sonnet 5 y cierra con MappingCompleted. El experimento y el chat corren el mismo Workflow. Cada llamada deja una traza en Langfuse con el prompt, la respuesta y los tokens.

**Transición:** El prompt de sistema.

**Diagrama (cajas):**

- Langfuse · prompt: catalog-v1-system · label production · semilla en el repo
- Amazon Bedrock: us.anthropic.claude-sonnet-5 · Converse · caché de prompt
- Producto: MappingRequested · JSON de Alephee
- prepare · código: system: prompt de Langfuse · catálogo de Shopee (23 categorías) · CachePoint · producto al final
- map · Claude Sonnet 5: as_structured_llm(Listing) · una sola llamada · sin herramientas
- MappingCompleted: listing: Listing | None · error: str | None
- Experimento en Langfuse: scripts/experiment.sh --version v1 | current · datasets real y mock · evaluadores del deck
- Chat del template: map_product_v1(sku) corre la V1 · stage warroom en sandbox
- Langfuse · trazas: prompt, respuesta y tokens · latencia de cada llamada

La V1 es un Workflow de dos steps. El experimento y el chat corren el mismo Workflow, y Langfuse guarda el prompt, las trazas y los resultados.

### 33 · El prompt de sistema.

**Sección:** 03 · V1 · el agente responde · **Pauta:** 3 min · **Tipo:** code

**Objetivo:** Leer el prompt nuevo con el esqueleto de cinco partes

**En pantalla:**


**Temas para hablar:** Este es el prompt de la V1, en inglés como los prompts actuales de Alephee, y escrito con las cinco partes: rol, tarea, reglas, qué hacer cuando falta el dato y formato. En pantalla están las reglas y la sección de cuando falta el dato, que es la que el prompt actual no tiene. Las resaltadas dicen que nunca invente, que -1 no es un valor y que un obligatorio sin dato va a missing con el motivo. El formato no pide JSON en el texto: dice que la respuesta va por el esquema del Listing.

**Pregunta / participación:** ¿Qué regla agregarían con lo que saben del catálogo?

**Transición:** El prompt vive en Langfuse.

**Código:** `core/src/catalog/prompts/catalog-v1-system.txt` líneas 10 a 27

```txt
Rules
- Choose the category only from the Shopee catalog, comparing it with the product category name
  and the product name. Copy its URN exactly.
- Copy every attribute URN exactly from the chosen category. Never invent a URN.
- If the channel attribute has a list of values, choose the equivalent value from that list and
  use its id and its name exactly as listed.
- If the channel attribute is free text, use valueId "0" and the product value as it is.
- Never translate values: Shopee values stay in Portuguese, exactly as the catalog lists them.
- Never invent values. Use only data present in the product attributes.
- Each channel attribute appears at most once.

When data is missing
- The values "-1", "N/A" or empty mean there is no data. Never publish them as values.
- If no value in the channel list is equivalent to the product value, leave the attribute out
  and add the product attribute to "rejected" with the reason.
- If a mandatory channel attribute cannot be filled from the product, add it to "missing" with
  the reason. Never fill it with a guess.
- If a product attribute has no matching attribute in the category, add it to "rejected" with
```

Esta copia es la semilla. La versión que se usa vive en Langfuse con el label production.

### 34 · El prompt vive en Langfuse.

**Sección:** 03 · V1 · el agente responde · **Pauta:** 3 min · **Tipo:** code

**Objetivo:** Mostrar dónde vive el prompt y qué pasa si Langfuse no responde

**En pantalla:**


**Temas para hablar:** La V1 pide el prompt a Langfuse por nombre y label. Si Langfuse no responde, usa la semilla del repositorio. La versión del prompt queda registrada en cada experimento, así sabemos con qué prompt salió cada número. Ojo: si alguien edita el prompt en Langfuse, la V1 cambia sin un commit.

**Transición:** Lo fijo primero, el producto al final.

**Código:** `core/src/catalog/prompts.py` líneas 31 a 39

```py

def get_system_prompt(name: str, client) -> SystemPrompt:
    """The `production` prompt from Langfuse, or the seed when there is no client or Langfuse fails."""
    seed = load_seed(name)
    if client is None:
        return SystemPrompt(seed, name, None)
    # With `fallback`, the SDK returns the seed instead of raising when Langfuse is unreachable,
    # and flags it with `is_fallback`, so the version is reported as None (the seed), not a number.
    prompt = client.get_prompt(name, label=LABEL, fallback=seed)
```

version None quiere decir que se usó la semilla.

### 35 · Lo fijo primero, el producto al final.

**Sección:** 03 · V1 · el agente responde · **Pauta:** 3 min · **Tipo:** code

**Objetivo:** Ver la caché de prompt en el código

**En pantalla:**


**Temas para hablar:** Así se aplica la buena práctica de la caché. Todo lo que va antes del CachePoint es igual para los 30 productos: el prompt y el catálogo. Bedrock lo guarda 5 minutos desde el último uso y lo cobra más barato. Solo cambia el producto, que va al final. Con los datos reales el catálogo ronda los 7.500 tokens. Con el mock no llega al mínimo, así que la caché no aparece en esas corridas.

**Transición:** El Workflow cierra con un evento tipado.

**Código:** `core/src/catalog/v1.py` líneas 53 a 67

```py
def build_messages(system_prompt: str, schemas: dict[str, dict], product: dict) -> list[ChatMessage]:
    """System prompt, then the static catalog, then the product.

    Today's prompts put the product first and the big lists after it, which defeats prompt
    caching. Here the order is reversed: everything static comes first.
    """
    return [
        ChatMessage(role="system", content=system_prompt),
        ChatMessage(role="user", blocks=[
            TextBlock(text=catalog_text(schemas)),
            # Everything before this point is identical for every product: Bedrock caches it.
            CachePoint(cache_control=CacheControl(type="default")),
            TextBlock(text=product_text(product)),
        ]),
    ]
```

En la traza de Langfuse se ven los tokens leídos de caché.

### 36 · El Workflow cierra con un evento tipado.

**Sección:** 03 · V1 · el agente responde · **Pauta:** 3 min · **Tipo:** code

**Objetivo:** Ver el contrato del Workflow

**En pantalla:**


**Temas para hablar:** Estos son los eventos de la V1. Entra MappingRequested con el producto, pasa ContextReady con los mensajes y sale MappingCompleted. Como MappingCompleted es una subclase de StopEvent, run() lo devuelve tal cual, con el Listing tipado adentro.

**Transición:** El flujo de la V1, según LlamaIndex.

**Código:** `core/src/catalog/events.py` líneas 22 a 38

```py

class MappingRequested(StartEvent):
    """Start of both workflows: `workflow.run(product=...)` builds this event from the kwargs."""

    product: dict


class ContextReady(Event):
    """V1: the messages for the single structured call, already in cache-friendly order."""

    messages: list[ChatMessage]


class MappingCompleted(StopEvent):
    """End of a mapping. No field is called `result`: it would collide with StopEvent's."""

    listing: Listing | None
```

El batch, el chat y los tests leen fin.listing sin parsear nada.

### 37 · El flujo de la V1, según LlamaIndex.

**Sección:** 03 · V1 · el agente responde · **Pauta:** 2 min · **Tipo:** diagram

**Objetivo:** Mostrar que el flujo sale del código

**En pantalla:**


**Temas para hablar:** Este grafo no lo dibujamos a mano. LlamaIndex lo arma leyendo las firmas de los steps: prepare recibe MappingRequested y devuelve ContextReady, map recibe ContextReady y devuelve MappingCompleted. Si alguien cambia una firma, el grafo cambia solo. El script scripts/draw_workflows.py lo deja en docs/workflows.md y un test fija las flechas.

**Transición:** Lo corremos sobre el caso guía.

**Diagrama (cajas):**

- MappingRequested: evento de entrada · product
- prepare: step · código · arma los mensajes
- ContextReady: evento · messages
- map: step · Claude Sonnet 5 · as_structured_llm(Listing)
- MappingCompleted: StopEvent tipado · listing · error

Este grafo lo dibuja LlamaIndex a partir de las firmas de los steps: cada step recibe un evento y devuelve otro.

### 38 · Demo · la V1 sobre un producto real.

**Sección:** 03 · V1 · el agente responde · **Pauta:** 5 min · **Tipo:** demo

**Objetivo:** Ver la V1 funcionando sobre un caso y leer el resultado en Langfuse

**En pantalla:**


**Temas para hablar:** El caso 01-real-calota-aro14 es el producto real del ejemplo de Alephee, la calota 94701411, y vive en el dataset mock. Antes de correr, pedir una predicción: ¿qué categoría y qué atributos va a devolver? Correr y leer la salida en el orden de la lista. Después abrir Langfuse: primero la traza, con el prompt, la respuesta y los tokens, y después los scores del caso. Los 30 productos reales se usan recién cuando Alephee confirme que pueden quedar en Langfuse Cloud: ahí se corre con --data real --allow-real-upload. Si Bedrock no responde, por sesión SSO vencida o por throttling, mostrar el experimento guardado y decirlo.

**Transición:** Qué falló y qué capa lo resuelve.

```bash
scripts/experiment.sh --version v1 --data mock --case 01-real-calota-aro14
```

**Mirar:**

- La categoría que eligió el modelo y la esperada
- Cada atributo: de dónde sale el valor y si está en la lista del canal
- missing y rejected: si informa lo que no pudo o completa igual
- En Langfuse: la traza con el prompt, la respuesta, los tokens y los segundos, y los scores del caso

**Respaldo:** el experimento v1-mock que corrimos antes de la sesión, abierto en Langfuse

### 39 · Qué falló en la V1 y qué capa lo resuelve.

**Sección:** 03 · V1 · el agente responde · **Pauta:** 3 min · **Tipo:** table

**Objetivo:** Convertir cada fallo de la V1 en la justificación de una capa

**En pantalla:**

- Medido el 1/10 en Langfuse · V1 sobre los 30 reales · salida esperada MOCK
- Qué medimos / V1 · 30 reales / Qué capa lo ataca en la V2
- Casos exactos / 3 de 30 (hoy: 7) / Se compara en la prueba
- Categoría correcta / 28 de 30, optimista: elige entre 23 que incluyen la correcta / La categoría sale de reference_category, en código
- Valores inválidos / 3 (hoy: 47) / validate en cada entrega y clean al final
- Duplicados / 0 (hoy: 5) / validate y clean
- Recall de atributos / 0,57: faltan 4 de cada 10 atributos esperados / Los campos de reference_attribute en código. Medido el 1/10: 0,60 en la V2

**Temas para hablar:** Esto medimos el 1/10 con la V1 sobre los 30 productos reales, contra una salida esperada mock. Hay menos inválidos que hoy, 3 contra 47, y ningún duplicado. Pero el recall es 0,57: faltan 4 de cada 10 atributos esperados. La categoría sale bien en 28 de 30, pero el número es optimista, porque la V1 elige entre 23 categorías que siempre incluyen la correcta. Los 3 inválidos muestran que una regla en el prompt no alcanza y hay que comprobarla en código. La V2 suma las dos cosas: las tablas en código y la validación en código.

**Pregunta / participación:** ¿Alguno de estos números les sorprende?

**Transición:** Almuerzo. A las 13:15, la V2.

### 40 · V2 · tablas y control.

**Sección:** 04 · V2 · tablas y control · **Pauta:** 1 min · **Tipo:** divider

**Objetivo:** Retomar después del almuerzo y abrir la V2

**En pantalla:**

- El código resuelve lo que saben las tablas. El agente decide el resto y entrega por una herramienta que valida.

**Temas para hablar:** La V1 responde sola y falla donde necesita datos que no tiene. La V2 hace tres cambios. El código resuelve la categoría y los campos que ya están en las tablas, sin modelo. Un FunctionAgent de LlamaIndex decide los valores de lista y los atributos que la tabla no cubre, y entrega por submit_listing, que valida en código. Las correcciones del equipo de catálogo y la caché viven en DynamoDB. El prompt ya no lleva el catálogo entero: lleva la lista de trabajo de este producto.

**Transición:** Qué es una herramienta.

### 41 · Una herramienta es una función que el modelo pide y el código ejecuta.

**Sección:** 04 · V2 · tablas y control · **Pauta:** 3 min · **Tipo:** flow

**Objetivo:** Definir herramienta sin jerga

**En pantalla:**

- El modelo pide lookup_corrections(attribute_urn, product_value)
- El programa ejecuta la función: busca en la tabla corrections de DynamoDB
- Devuelve {correction: {valueId, value}} o {correction: null}
- El modelo sigue con ese dato, no con su memoria

**Temas para hablar:** El modelo no ejecuta nada. Escribe un pedido con nombre y argumentos. El programa lo ejecuta y le devuelve el resultado como un mensaje más. Por eso la herramienta es determinista y el modelo no. La V2 tiene dos herramientas. lookup_corrections es de lectura y busca lo que cargó el equipo de catálogo. submit_listing es la entrega: valida en código y, si hay problemas, se los devuelve al modelo. Que una herramienta exista no obliga al modelo a usarla. Por eso la única forma de entregar es submit_listing.

**Transición:** Decisión 10: qué decide la tabla y qué decide el agente.

### 42 · ¿Qué decide la tabla y qué decide el agente?

**Sección:** 04 · V2 · tablas y control · **Pauta:** 4 min · **Tipo:** decision

**Objetivo:** Cerrar la decisión 10

**En pantalla:**

- La V2 se construyó con la opción A · si gana otra, vemos qué cambia

**Temas para hablar:** B es el error más común: dejar que el modelo mejore un mapeo que el equipo de catálogo mantiene a mano. Si la tabla está mal, se corrige la tabla. C ya lo descartamos en la decisión 3. Lo que la tabla resuelve no pasa por el modelo.

**Transición:** La V2 por dentro.

**Decisión 10:** ¿Qué decide la tabla y qué decide el agente?

1. A · La tabla fija la categoría y los campos; el agente solo elige el valor equivalente de la lista y cubre lo que la tabla no tiene
2. B · El agente puede corregir la tabla si cree que está mal
3. C · Todo por tabla; sin modelo

**Propuesta:** A. La tabla manda, como se acordó el 25/08 con Juan David. En la V2, el step resolve fija en código la categoría con reference_category y los campos con reference_attribute. Si el campo es texto libre o el valor coincide con la lista del canal, también lo resuelve el código. El agente recibe solo lo que queda: los valores de lista por decidir y los atributos que la tabla no cubre. Si cambia algo resuelto, gana lo resuelto.

**Archivo:** `decisiones/10-tabla-vs-agente.md`

### 43 · La V2 por dentro.

**Sección:** 04 · V2 · tablas y control · **Pauta:** 3 min · **Tipo:** diagram

**Objetivo:** Ver qué hace el código y qué hace el modelo en la V2

**En pantalla:**


**Temas para hablar:** Verde es código y violeta es el modelo. Son cuatro steps. check_cache busca el SKU en DynamoDB: si ya se mapeó con las mismas tablas y el mismo prompt, sale de ahí sin llamar al modelo. resolve fija la categoría y los campos con las tablas. Si no hay categoría o esquema, termina con un faltante explícito y sin modelo. run_agent le pasa al FunctionAgent la lista de lo que falta decidir. El agente puede consultar correcciones y entrega con submit_listing, que valida en código y le devuelve los problemas. Tiene hasta cinco entregas. finalize junta lo resuelto con lo del agente, y gana lo resuelto. Después pasa clean y guarda en la caché si la entrega pasó la validación.

**Pregunta / participación:** ¿Qué caja sacarían a código si pudieran?

**Transición:** El flujo de la V2, según LlamaIndex.

**Diagrama (cajas):**

- Producto: MappingRequested
- check_cache: mapping_cache · en DynamoDB · SKU + tablas + prompt
- resolve · código: categoría por tabla · campos por tabla · texto libre y coincidencias
- run_agent · FunctionAgent: Claude Sonnet 5 · to_decide y lo no cubierto · hasta 5 iteraciones
- finalize · código: gana lo resuelto · clean() · guarda en caché
- Herramientas: lookup_corrections · submit_listing → validate() · los problemas vuelven al agente
- DynamoDB · corrections: las carga catálogo · scripts/correct.sh
- MappingCompleted: source = cache
- MappingCompleted: source = tables · sin categoría o esquema
- MappingCompleted: source = agent · traza en Langfuse

Verde es código y violeta es el modelo. El código resuelve lo que saben las tablas; el agente decide valores y entrega por una herramienta que valida.

### 44 · El flujo de la V2, según LlamaIndex.

**Sección:** 04 · V2 · tablas y control · **Pauta:** 2 min · **Tipo:** diagram

**Objetivo:** Ver los caminos que no pasan por el modelo

**En pantalla:**


**Temas para hablar:** Es el mismo dibujo automático, ahora para la V2. Lo importante son las tres salidas hacia MappingCompleted. Si la caché tiene el SKU, check_cache termina ahí. Si no hay categoría en la tabla o no hay esquema, resolve termina con un faltante explícito, sin modelo. Solo lo que llega a WorkReady pasa por el agente, y finalize siempre limpia lo que entrega.

**Pregunta / participación:** ¿Qué porcentaje de los productos debería salir por la caché en producción?

**Transición:** Adentro de run_agent: el ciclo del FunctionAgent.

**Diagrama (cajas):**

- MappingRequested: evento de entrada · product
- check_cache: step · código · caché en DynamoDB
- CacheMissed: evento · product
- resolve: step · código · categoría y campos por tabla
- WorkReady: evento · worklist
- MappingCompleted: StopEvent tipado · listing · error · source
- finalize: step · código · merge, clean y caché
- AgentDone: evento · last · valid · error
- run_agent: step · FunctionAgent · hasta 5 entregas

La V2 tiene tres salidas: desde la caché, desde las tablas sin llamar al modelo, o después del agente.

### 45 · Adentro de run_agent: el ciclo del FunctionAgent.

**Sección:** 04 · V2 · tablas y control · **Pauta:** 2 min · **Tipo:** diagram

**Objetivo:** Entender qué hace la librería y qué hace nuestro código

**En pantalla:**


**Temas para hablar:** El FunctionAgent es otro Workflow, el de la librería. setup_agent arma el pedido, run_agent_step llama a Claude y parse_agent_output decide. Si el modelo pide una herramienta, call_tool la corre. Si submit_listing encuentra problemas, levanta un error y el texto vuelve al modelo como resultado, y el ciclo da otra vuelta. Si la entrega es válida, aggregate_tool_results corta con StopEvent porque la herramienta es return_direct. parse_agent_output también cuenta las vueltas: por eso la V2 pasa MAX_ITERATIONS más uno.

**Transición:** Las dos herramientas del agente.

**Diagrama (cajas):**

- user_msg: AgentWorkflow · StartEvent
- init_run: memoria y mensaje · emite AgentInput
- setup_agent: system prompt y tools · emite AgentSetup
- run_agent_step: llama a Claude · emite AgentOutput
- parse_agent_output: cuenta las iteraciones · texto: StopEvent · tool call: ToolCall
- call_tool: corre la herramienta · un error vuelve como texto · emite ToolCallResult
- aggregate_tool_results: return_direct válido: StopEvent · si no: AgentInput
- StopEvent: el Listing entregado · o la respuesta en texto

El ciclo propio del FunctionAgent, leído de la librería. submit_listing es return_direct: solo una entrega válida corta el ciclo.

### 46 · Las dos herramientas del agente.

**Sección:** 04 · V2 · tablas y control · **Pauta:** 2 min · **Tipo:** table

**Objetivo:** Entender qué puede hacer el agente y qué no

**En pantalla:**

- El agente solo recibe lo que falta decidir: to_decide, unmapped_product y uncovered_channel
- Herramienta / Qué recibe / Qué devuelve / Para qué sirve
- lookup_corrections / attribute_urn y product_value / La corrección del equipo de catálogo, o correction: null / Ver si catálogo ya corrigió ese valor. La corrección manda sobre el modelo
- submit_listing / El Listing completo: category, attributes, missing y rejected / Si pasa la validación, el Listing y fin del ciclo. Si no, la lista de problemas / Entregar. Lo valida el código, no el modelo

**Temas para hablar:** El agente de la V2 tiene solo dos herramientas. lookup_corrections le pregunta al equipo de catálogo si ya corrigió ese valor para esa categoría; si hay corrección, manda sobre lo que piense el modelo. submit_listing es la única forma de entregar. El código valida la entrega: si tiene problemas, se los devuelve al modelo como texto y el ciclo sigue. Si pasa, es return_direct y corta el ciclo. El modelo nunca decide si su propia respuesta está bien.

**Pregunta / participación:** ¿Qué otra herramienta le darían, y qué riesgo trae?

**Transición:** Un caso real: pastillas de freno, SKU 98550735.

### 47 · Un caso real: pastillas de freno, SKU 98550735.

**Sección:** 04 · V2 · tablas y control · **Pauta:** 2 min · **Tipo:** table

**Objetivo:** Ver las herramientas funcionando con un producto real

**En pantalla:**

- Datos reales · corrida de la V2 del 1/10, leída de Langfuse · el esquema de Shopee es MOCK
- Paso / Quién / Qué pasó
- Hoy / Proceso actual / Shopee rechazó la publicación: faltaba Inmetro Certification, que es obligatorio
- resolve / Código / Categoría Pastilha de Freio por reference_category. Cuatro campos sin modelo: Novo, Brasil, Inmetro 007077/2015 y Modelo
- lookup_corrections × 3 / Agente / lookup_corrections(101826, "1"), (100134, "Metal") y (100037, "Brasil"): las tres devuelven correction: null
- submit_listing / Agente, validado por el código / 10 atributos: "1" pasa a Sim, 4 pastillas, Dianteira. Pasa la validación al primer intento
- finalize / Código / Sale el Listing con Inmetro incluido, 17 atributos rechazados con motivo y 0 faltantes. Cuatro llamadas al modelo

**Temas para hablar:** Es un producto real de GM. Hoy Shopee rechazó su publicación porque faltaba Inmetro Certification, que es obligatorio. En la V2, resolve fija la categoría con la tabla y resuelve cuatro campos en código, entre ellos Inmetro Certification, sin llamar al modelo. Al agente le quedan pocos valores. Primero consulta correcciones tres veces, por ejemplo lookup_corrections con el atributo 101826 y el valor 1, y recibe correction null. Después entrega con submit_listing: 1 pasa a Sim, la cantidad de pastillas a 4 y la posición a Dianteira. La entrega pasa la validación al primer intento. Fueron cuatro llamadas al modelo. Ojo: Metal pasa a Others porque el dominio de Material del esquema es MOCK.

**Pregunta / participación:** ¿Qué atributo de este caso debería resolver la tabla y hoy decide el agente?

**Transición:** Lo que resuelve el código.

### 48 · Lo que resuelve el código.

**Sección:** 04 · V2 · tablas y control · **Pauta:** 3 min · **Tipo:** code

**Objetivo:** Ver en código qué no pasa por el modelo

**En pantalla:**


**Temas para hablar:** Esto corre dentro de build_worklist, antes del agente. Justo antes de estas líneas, target_for busca el campo de Shopee en reference_attribute, entre los atributos de la categoría, y si no está el atributo va a unmapped_product. Si dos campos legacy apuntan al mismo campo de Shopee, gana el primero y no hay duplicado. Si el campo es texto libre y no tiene unidad, el valor se copia tal cual. Si el valor coincide con uno de la lista del canal, se toma ese. Lo demás va a to_decide, y es lo único que decide el agente.

**Transición:** La entrega pasa por una herramienta que valida.

**Código:** `core/src/catalog/worklist.py` líneas 62 a 79

```py
# First product attribute wins a target: two legacy fields pointing to the same Shopee
# attribute must not produce a duplicate (the kind of duplicate today's output shows).
if target in covered:
    continue
covered.add(target)
definition = definitions[target]
values = _values(definition)
unit = str(attribute.get("unit") or "").strip()
# Free text with no unit: the product value is copied as is. With a unit it goes to the
# agent, which decides whether and how the unit fits the channel.
if not values and unit in NO_DATA:
    resolved.append(MappedAttribute(urn=target, valueId="0", value=value, unit=None))
    continue
# List attribute whose value matches a channel value by name: take the channel's id and
# spelling. Anything else needs judgment and goes to the agent.
match = next((v for v in values if normalize(v["name"]) == normalize(value)), None)
if match is not None:
    resolved.append(MappedAttribute(urn=target, valueId=match["id"], value=match["name"], unit=None))
```

Texto libre y coincidencia exacta salen sin modelo. Lo que no coincide va a to_decide.

### 49 · La entrega pasa por una herramienta que valida.

**Sección:** 04 · V2 · tablas y control · **Pauta:** 3 min · **Tipo:** code

**Objetivo:** Ver cómo vuelve al agente lo que no pasa la validación

**En pantalla:**


**Temas para hablar:** submit_listing es la única forma de entregar. Primero junta la entrega con lo que resolvió el código, y gana lo resuelto. Después la valida. Si hay problemas, lanza un error con la lista. El FunctionAgent le devuelve ese texto al modelo, que corrige y vuelve a entregar. Si pasa, return_direct corta el loop y la entrega sale tal cual, sin otra vuelta por el modelo.

**Transición:** Lo corremos.

**Código:** `core/src/catalog/v2.py` líneas 150 a 162

```py
def submit_listing(**listing) -> dict:
    """Deliver the listing. It is validated in code; if there are problems you get them back."""
    candidate = merge_resolved(Listing.model_validate(listing), ev.worklist.resolved)
    submissions.append(candidate)
    problems = validate(candidate, schema, ev.category_urn)
    if problems:
        raise ValueError("The listing did not pass validation. Fix these and submit again:\n- " + "\n- ".join(problems))
    return candidate.model_dump()

tools = [
    FunctionTool.from_defaults(fn=lookup_corrections, name="lookup_corrections"),
    FunctionTool.from_defaults(fn=submit_listing, name="submit_listing", fn_schema=Listing, return_direct=True,
                               description="Deliver the final listing. It is validated in code."),
```

Cada entrega queda en submissions. Si se agotan las cinco, finalize limpia la última.

### 50 · Demo · la V2 sobre el mismo caso.

**Sección:** 04 · V2 · tablas y control · **Pauta:** 5 min · **Tipo:** demo

**Objetivo:** Comparar V1 y V2 sobre el mismo caso

**En pantalla:**


**Temas para hablar:** Es el mismo caso de la V1, para comparar. Antes de correr, pedir una predicción: ¿cuántos atributos resuelve el código sin preguntar? En este caso son cinco: Condição do Item, Origem, Número da Peça, Type of shell y Cor (MOCK). Al agente le quedan tres valores por decidir, Weight, Is it insurable y Aro (MOCK), y Material, que no está en la tabla. En la salida del experimento, source dice de dónde salió la publicación: cache, tables o agent. Ojo: si el SKU ya se corrió con las mismas tablas y el mismo prompt, sale de la caché y no se ve al agente. En ese caso, mostrar la traza de la corrida del 1/10 y dejar la caché para la demo de corregir y repetir. Si Bedrock no responde, mostrar el experimento guardado y decirlo.

**Transición:** Cuánto cuesta por producto.

```bash
scripts/experiment.sh --version v2 --data mock --case 01-real-calota-aro14
```

**Mirar:**

- source, en la traza: con run_agent salió del agente; sin él, de la caché o de las tablas
- Los atributos que resolvió el código: la lista resolved del mensaje al agente
- Las entregas que rechazó submit_listing: cada llamada a la herramienta con su error
- Los tokens de la traza: nuevos, leídos de caché y escritos en caché

**Respaldo:** el experimento v2-mock del 1/10, abierto en Langfuse

### 51 · Costo por producto, medido.

**Sección:** 04 · V2 · tablas y control · **Pauta:** 3 min · **Tipo:** table

**Objetivo:** Mostrar el efecto de herramientas + caché en tokens y latencia

**En pantalla:**

- Medido el 1/10 en Langfuse · 30 reales · promedio por producto
- Versión / Entrada sin caché / Leída de caché / Segundos
- V1 / ~4.560 / ~14.780 / ~3,3
- V2 / ~9.970 / 0 / ~12,4

**Temas para hablar:** Estos números salen de las trazas de Langfuse de las corridas del 1/10 sobre los 30 reales, en promedio por producto. La V1 manda el catálogo entero, pero casi todo se lee de caché. La V2 manda solo la lista de trabajo del producto y aun así paga más tokens nuevos: el agente hace varias llamadas por producto y en esta corrida no leyó nada de caché. La causa es que la V2 no marca ningún punto de caché, y Bedrock solo cachea lo que queda antes de uno. Sumarlo es una tarea pendiente. Para hablar de dólares faltan la salida, la escritura en caché y el precio de la región. No sacar el ahorro solo de esta tabla. Un SKU que ya está en la caché de la V2 no paga tokens.

**Transición:** Decisión 11: el costo.

### 52 · ¿Cuánto puede costar?

**Sección:** 04 · V2 · tablas y control · **Pauta:** 4 min · **Tipo:** decision

**Objetivo:** Cerrar la decisión 11 con la medición como tarea

**En pantalla:**

- Abierta: el tope se acuerda con Alephee sobre la medición del 1/10

**Temas para hablar:** Anotar quién convierte los tokens en dólares con el precio de Bedrock de la región, y para cuándo. Si el grupo quiere un número hoy, dar el de tokens.

**Transición:** Qué controla la V2.

**Decisión 11:** ¿Cómo tratamos la restricción de costo del modelo?

1. A · Tope mensual acordado con Alephee y medición por producto: tokens de entrada, salida, caché leída y escrita
2. B · Sin tope: se mide después
3. C · El tope de hoy (USD 350) y publicar sin atributos al agotarse

**Propuesta:** A. Hoy el tope corta la calidad, que es la opción C. Medido el 1/10, la V2 paga unos 9.970 tokens de entrada nuevos por producto y no leyó caché, contra 4.560 nuevos y 14.780 leídos de caché de la V1. Con la caché por SKU (decisión 13), el mismo producto que venden 40 concesionarios se paga una vez. El tope en dólares se fija con Alephee sobre esa medición, después de revisar por qué la V2 no leyó caché.

**Archivo:** `decisiones/11-costo.md`

### 53 · Guardrail: una comprobación en código.

**Sección:** 04 · V2 · tablas y control · **Pauta:** 3 min · **Tipo:** compare

**Objetivo:** Diferenciar guardrail de regla del prompt

**En pantalla:**

- VALIDATE | Lista los problemas en lenguaje claro. submit_listing se los devuelve al agente, que corrige y vuelve a entregar, hasta cinco veces
- CLEAN | La red final: fija la categoría de la tabla, descarta lo inválido con su motivo y marca los obligatorios que faltan
- NUNCA PUBLICA | Un valor fuera de la lista del canal, un -1 ni un duplicado. No verifica que el valor sea cierto: eso depende del esquema y de catálogo

**Temas para hablar:** Una regla en el prompt depende de que el modelo obedezca. Un guardrail la comprueba en código. En la V2 son dos funciones. validate revisa cada entrega y le devuelve los problemas al agente para que corrija. clean corre siempre al final y descarta lo que siga mal, con el motivo en rejected. Tiene un límite: comprueba que el valor esté en el esquema y en la lista del canal, pero no que sea cierto para el producto.

**Transición:** La validación, en código.

### 54 · La validación, en código.

**Sección:** 04 · V2 · tablas y control · **Pauta:** 3 min · **Tipo:** code

**Objetivo:** Ver las reglas que toda entrega tiene que cumplir

**En pantalla:**


**Temas para hablar:** Son cuatro comprobaciones. La categoría tiene que ser la de la tabla. Cada atributo tiene que existir en la categoría, y su valor tiene que estar en la lista del canal con un id y un nombre que coincidan. Ningún atributo puede repetirse. Y cada obligatorio tiene que tener valor o estar en missing con su motivo. clean usa las mismas reglas para descartar.

**Transición:** Decisión 12.

**Código:** `core/src/catalog/guardrails.py` líneas 45 a 60

```py
def validate(listing: Listing, schema: dict, category_urn: str) -> list[str]:
    """Every contract problem of a listing, as messages for the agent. Empty list means valid."""
    definitions = _definitions(schema)
    problems = []
    # The reference table decides the category; the model cannot change it.
    if listing.category != category_urn:
        problems.append(f"category must be {category_urn} (it comes from the reference table)")
    problems += [p for a in listing.attributes if (p := _attribute_problem(a, definitions, category_urn))]
    counts = Counter(a.urn for a in listing.attributes)
    problems += [f"{urn} appears {n} times; keep only one" for urn, n in counts.items() if n > 1]
    # A mandatory attribute must be either filled or declared missing with a reason. Silently
    # leaving it out is what today's process does when the budget runs out.
    missing = {m.urn for m in listing.missing}
    problems += [f"{urn} ({d.get('name')}) is mandatory: fill it or add it to missing with the reason"
                 for urn, d in definitions.items() if d.get("mandatory") and urn not in counts and urn not in missing]
    return problems
```

Devuelve texto para el modelo. Una lista vacía quiere decir que la entrega pasa.

### 55 · ¿Qué hace cuando no sabe?

**Sección:** 04 · V2 · tablas y control · **Pauta:** 4 min · **Tipo:** decision

**Objetivo:** Cerrar la decisión 12 y dejar la política de revisión como pendiente

**En pantalla:**

- La V2 se construyó con la opción B · C se puede armar encima

**Temas para hablar:** Marcar missing no arma solo un circuito de revisión. Hoy es una lista en la salida. Quién la mira, dónde y con qué herramienta lo decide Alephee como producto. Anotar el dueño.

**Transición:** Memoria.

**Decisión 12:** ¿Qué hace el agente cuando no puede completar un atributo obligatorio?

1. A · Publicar sin el atributo (hoy)
2. B · Faltante explícito con motivo: la publicación sale con missing y alguien decide
3. C · Bloquear la publicación hasta revisión humana

**Propuesta:** B. Reemplaza el publicar sin atributos. En la V2, validate rechaza una entrega con un obligatorio sin valor ni motivo, y clean lo marca en missing si el agente no lo corrige. Sin categoría en la tabla o sin esquema, el Workflow termina sin llamar al modelo, con missing: category. Quién recibe la lista missing y si bloquea la publicación es parte de la integración con la plataforma de Alephee, y queda pendiente con dueño. C es una política válida que se puede construir sobre B.

**Archivo:** `decisiones/12-cuando-no-sabe.md`

### 56 · Memoria: correcciones del equipo de catálogo.

**Sección:** 04 · V2 · tablas y control · **Pauta:** 3 min · **Tipo:** cards

**Objetivo:** Definir memoria para este agente sin prometer aprendizaje automático

**En pantalla:**

- Una corrección dice: en esta categoría, este valor del producto va a este atributo con este valor del canal
- El agente la consulta con lookup_corrections, y la corrección manda sobre su criterio
- En la V2 vive en DynamoDB (tabla corrections) y se carga con scripts/correct.sh. En producción, una tabla de Alephee o AgentCore Memory

**Temas para hablar:** Acá memoria no quiere decir que el agente aprende solo. Quiere decir que reusa correcciones que alguien del equipo de catálogo cargó a mano. Se cargan con scripts/correct.sh, que revisa que el valor esté en la lista del canal y borra la caché de esa categoría. Que el agente la respete depende de que la consulte. El prompt lo exige y un test e2e lo comprueba contra Bedrock. Un límite: la corrección solo se aplica a lo que llega al agente. Si el valor coincide con la lista del canal, lo resuelve el código y no consulta correcciones.

**Transición:** La caché: la clave y la lectura.

### 57 · La caché: la clave y la lectura.

**Sección:** 04 · V2 · tablas y control · **Pauta:** 3 min · **Tipo:** code

**Objetivo:** Ver qué hace que el mismo SKU dé la misma salida

**En pantalla:**


**Temas para hablar:** La clave es el SKU y la categoría legacy, más la versión de las tablas y la versión del prompt. Si cambia una tabla o el prompt, la clave cambia y el producto se vuelve a mapear. Antes de devolver una entrada guardada, la valida otra vez contra el esquema. Si ya no pasa, la ignora. Un producto sin SKU o sin categoría no usa la caché.

**Transición:** finalize: qué se guarda.

**Código:** `core/src/catalog/v2.py` líneas 95 a 112

```py
    sku = str(product.get("sku") or "").strip()
    categories = product.get("categories") or []
    if not sku or not categories:
        return None
    return (sku, legacy_id(categories[0]["urn"]))

@step
async def check_cache(self, ev: MappingRequested) -> MappingCompleted | CacheMissed:
    """Return the cached listing if there is one and it still passes validation."""
    key = self._cache_key(ev.product)
    category = self.reference.category_for(ev.product)
    schema = self.schemas.get(category["urn"]) if category else None
    if key and schema:
        hit = _safe(lambda: self.cache.get(*key, self.reference.version, self.prompt_version), None, "cache get")
        # Re-validated against the current schema: a cached listing that no longer fits the
        # channel (schema changed, bad entry) is ignored and the product is mapped again.
        if hit is not None and not validate(hit, schema, category["urn"]):
            return MappingCompleted(listing=hit, source="cache")
```

Un error de DynamoDB no frena el mapeo: _safe sigue sin caché.

### 58 · finalize: gana lo resuelto y se guarda lo válido.

**Sección:** 04 · V2 · tablas y control · **Pauta:** 3 min · **Tipo:** code

**Objetivo:** Ver el cierre del Workflow y qué entra en la caché

**En pantalla:**


**Temas para hablar:** finalize junta la última entrega con lo que resolvió el código, y gana lo resuelto. Después pasa clean, la red final. Solo guarda en la caché si la última entrega del agente pasó la validación. Si el agente agotó las cinco entregas, el resultado sale limpio y con un error que lo dice.

**Transición:** Decisión 13.

**Código:** `core/src/catalog/v2.py` líneas 198 a 215

```py
async def finalize(self, ev: AgentDone) -> MappingCompleted:
    """Merge, clean and, only if the agent's listing was valid, store it in the cache."""
    if ev.last is None:
        return MappingCompleted(listing=None, error=ev.error or "the agent never submitted a listing", source="agent")
    schema = self.schemas[ev.category_urn]
    # Last safety net: whatever the agent left, the output is forced back into contract
    # (category from the table, invalid values dropped, mandatory gaps listed in `missing`).
    final = clean(merge_resolved(ev.last, ev.worklist.resolved), schema, ev.category_urn)
    key = self._cache_key(ev.product)
    # A listing the guardrails had to clean is not cached: the next run gets another chance
    # instead of repeating a degraded answer for every dealer that sells the SKU.
    if ev.valid and key:
        _safe(lambda: self.cache.put(*key, self.reference.version, self.prompt_version, ev.category_urn, final),
              None, "cache put")
    # Never hide an agent error behind a cleaned listing; an exhausted loop with no other
    # error gets a specific reason instead of silently looking like a clean success.
    error = ev.error
    if error is None and ev.exhausted and not ev.valid:
```

Sin ninguna entrega, el resultado lleva un error.

### 59 · ¿Cómo garantizamos determinismo?

**Sección:** 04 · V2 · tablas y control · **Pauta:** 4 min · **Tipo:** decision

**Objetivo:** Cerrar la decisión 13 con las extensiones de la clave como pendiente

**En pantalla:**

- La V2 se construyó con la opción A · falta separar por cuenta

**Temas para hablar:** Preguntar qué otros cambios deberían invalidar la caché. Hoy un cambio en el producto o en el esquema del canal no cambia la clave. Anotar la lista, porque es la especificación de la clave de producción.

**Transición:** Demo: corregir y repetir.

**Decisión 13:** ¿Cómo garantizamos que el mismo SKU dé la misma salida?

1. A · Caché por SKU + tablas + prompt en DynamoDB; se invalida al cargar una corrección
2. B · Seed fijo (lo que se intentó hoy; los parámetros exactos siguen sin confirmar)
3. C · Recalcular siempre y aceptar variación

**Propuesta:** A. Un mapeo por SKU, con la versión de las tablas y la del prompt en la clave, en la tabla mapping_cache de DynamoDB. Cambiar una tabla o el prompt cambia la clave. Cargar una corrección con scripts/correct.sh borra la caché de esa categoría. Solo se guarda una entrega que pasó la validación. B reduce la variación pero no la elimina, y sigue pagando cada corrida. Antes de producción falta separar por cuenta y sumar la versión del esquema del canal.

**Archivo:** `decisiones/13-determinismo-y-cache.md`

### 60 · Demo · corregir y repetir.

**Sección:** 04 · V2 · tablas y control · **Pauta:** 5 min · **Tipo:** demo

**Objetivo:** Ver correcciones, validación y caché en una sola secuencia

**En pantalla:**


**Temas para hablar:** La corrección del ejemplo es para el caso 01: Aro (MOCK) con valor 14 va a 14", id 99102. Llega al agente porque 14 no coincide con ninguna opción de la lista. Si el grupo prefiere otra, cambiar los argumentos. scripts/correct.sh revisa que el valor esté en la lista del canal, guarda la corrección en DynamoDB y borra la caché de la categoría. Correr una vez: el agente consulta la corrección. Correr de nuevo: tiene que salir de la caché. Si algo falla, mostrar la corrida guardada y decirlo.

**Transición:** La misma V2 desde el chat.

```bash
scripts/correct.sh --category urn:category:102529:vendor:shopee --attribute urn:attribute:990001:vendor:shopee --product-value 14 --value-id 99102 --value '14"'
```

**Mirar:**

- Primera corrida, scripts/experiment.sh --version v2 --data mock --case 01-real-calota-aro14: en la traza, lookup_corrections devuelve la corrección
- El valor de Aro sale tal cual lo cargó catálogo
- Segunda corrida, el mismo comando: sale de la caché (source = cache), sin run_agent ni llamadas al modelo
- rejected explica cada descarte de clean

**Respaldo:** las corridas del experimento v2-mock del 1/10, en Langfuse

### 61 · Demo · la V2 desde el chat.

**Sección:** 04 · V2 · tablas y control · **Pauta:** 4 min · **Tipo:** demo

**Objetivo:** Mostrar que la misma V2 sirve desde el chat del template

**En pantalla:**


**Temas para hablar:** Es el mismo Workflow del experimento, detrás de una herramienta del chat. El chat tiene dos, map_product_v1 y map_product_v2, y usa la V2 por defecto. Corre en AgentCore, en el stage warroom de la cuenta sandbox, y mapea solo el dataset mock. El chat usa la semilla del prompt del repositorio, así que su caché no se mezcla con la del experimento. Si el deploy no responde, mostrar el modo mock local y decir que esa respuesta es de ejemplo.

**Transición:** Cómo lo probamos.

```bash
API_URL=<Function URL del BFF> CHAT_HMAC_SECRET=<secreto HMAC> npm start -w apps/web
```

**Mirar:**

- Escribir en el chat: Mapea el SKU 94701411 con la V2
- El asistente llama a map_product_v2 y muestra la categoría, los atributos, los faltantes y source
- Pedirlo otra vez: source dice cache
- En Langfuse: la traza del turno del chat, con map_product_v2 y, adentro, los steps de la V2

**Respaldo:** npm run dev en localhost:3000: modo mock del chat, con una respuesta de ejemplo que no corre la V2

### 62 · Cómo lo probamos.

**Sección:** 04 · V2 · tablas y control · **Pauta:** 3 min · **Tipo:** cards

**Objetivo:** Mostrar cómo sabemos que la V2 funciona antes de medirla

**En pantalla:**

- Tests unitarios: uv run pytest core/tests -q. Son 181, con dobles del modelo, sin AWS ni Langfuse
- Experimentos en Langfuse: scripts/experiment.sh --version v2 --data mock. Cada producto queda con su traza y sus scores
- Tests e2e: API_URL=<Function URL del BFF> scripts/e2e.sh, contra Bedrock, DynamoDB y el chat desplegado. Sin API_URL se omite el test del chat. Los 14 pasaron el 1/10

**Temas para hablar:** Son tres niveles. Los tests unitarios prueban cada step con dobles y corren en segundos. Los experimentos miden la calidad sobre el dataset con la métrica de la decisión 8. Los tests e2e comprueban que las piezas reales funcionan juntas: Bedrock, las tablas de DynamoDB y el chat desplegado. Los e2e usan solo el dataset mock.

**Transición:** Un test e2e, en código.

### 63 · Un test e2e, en código.

**Sección:** 04 · V2 · tablas y control · **Pauta:** 3 min · **Tipo:** code

**Objetivo:** Ver una prueba contra el modelo real

**En pantalla:**


**Temas para hablar:** Este test corre la V2 contra Bedrock sobre cada uno de los 10 casos mock, con una caché en memoria para que siempre llame al modelo. El caso sin categoría tiene que terminar por tablas, sin modelo. En los demás, la salida tiene que pasar validate sin ningún problema. Es la regla de la decisión 8, comprobada contra el modelo real.

**Transición:** A las 16:15, la prueba.

**Código:** `core/tests/e2e/test_e2e_mapping.py` líneas 47 a 55

```py
@pytest.mark.parametrize("case_id", sorted(CASES))
async def test_v2_never_delivers_invalid_listings(case_id, stores):
    done = await _v2(stores, cache=InMemoryCache()).run(product=CASES[case_id]["product"])
    if case_id == "09-sin-categoria":
        assert done.source == "tables" and done.listing.missing[0].urn == "category"
        return
    assert done.listing is not None, done.error
    if done.listing.category:
        assert validate(done.listing, SCHEMAS[done.listing.category], done.listing.category) == []
```

Corre con scripts/e2e.sh, que pone RUN_E2E=1. Sin eso, se omite.

### 64 · La prueba.

**Sección:** 05 · La prueba y el camino · **Pauta:** 1 min · **Tipo:** divider

**Objetivo:** Abrir la prueba con el criterio acordado a la vista

**En pantalla:**

- El proceso de hoy contra la V1 y la V2, sobre los 30 reales, con el criterio de la decisión 8.

**Temas para hablar:** Volver a la pizarra y al número de la decisión 8. Los experimentos corrieron el 1/10 en Langfuse, y acá los comparamos.

**Transición:** Los resultados.

### 65 · Resultados del 1/10.

**Sección:** 05 · La prueba y el camino · **Pauta:** 3 min · **Tipo:** table

**Objetivo:** Leer los resultados contra el criterio, sin maquillar

**En pantalla:**

- 30 reales · salida esperada MOCK · Hoy: lo que publicó Alephee · V1 y V2: experimentos de Langfuse del 1/10
- Métrica / Hoy / V1 / V2
- Casos exactos / 7 / 3 / 5
- Categoría correcta / 28 / 28 / 27
- Valores inválidos (-1 o fuera de lista) / 47 / 3 / 0
- Duplicados / 5 / 0 / 0
- Obligatorios sin informar / 2 / 1 / 1
- Precisión / 0,70 / 0,70 / 0,69
- Recall / 0,97 / 0,57 / 0,60

**Temas para hablar:** La columna Hoy sale de la misma métrica aplicada a las publicaciones actuales. La V2 es la única columna con cero valores inválidos y cero duplicados. Su único obligatorio sin informar es el caso error-26301167. La V2 completó Manufacturer (MOCK) con GM, tomado del atributo Marca del producto, y la salida esperada mock lo marca como faltante porque solo completa obligatorios a través de reference_attribute. Es un límite de la salida esperada: el valor sale del producto. Las 27 categorías de la V2 salen de esa corrida. Al volver a correr los tres casos que dieron problemas, los tres salieron con la categoría correcta y una publicación válida, así que no se repitió. La categoría de la V1 es optimista, porque elige entre 23 opciones que incluyen la correcta. El recall de Hoy sale inflado, porque la salida esperada hereda lo que hoy se mapea. El recall de la V2, 0,60, es casi igual al de la V1: la salida esperada mock hereda lo que hoy no se mapea y castiga los atributos extra bien mapeados (precisión 0,69).

**Transición:** Cómo leer la tabla.

### 66 · Cómo leer la tabla.

**Sección:** 05 · La prueba y el camino · **Pauta:** 3 min · **Tipo:** cards

**Objetivo:** Dar la lectura honesta de los resultados

**En pantalla:**

- Exactos bajos en todas las columnas: la salida esperada hereda las omisiones del proceso actual y castiga aciertos que hoy nadie mapea
- Inválidos y duplicados sí son errores seguros. La V2 es la única columna con cero en los dos
- El obligatorio sin informar de la V2 (error-26301167) es Manufacturer (MOCK) = GM, tomado de Marca: la salida esperada mock no lo prevé
- Categoría: la V1 elige entre 23 opciones con la correcta adentro, así que su número es optimista

**Temas para hablar:** Lo que se puede afirmar: estos controles detectan errores concretos, y cada versión los baja o no. Lo que todavía no se puede afirmar es una mejor exactitud general, porque la salida esperada es mock. Un control también puede bajar errores quitando información, así que hay que mirar control y cobertura juntos.

**Pregunta / participación:** ¿Qué evidencia pedirían antes de un piloto con un concesionario?

**Transición:** El camino a producción.

### 67 · Camino a producción.

**Sección:** 05 · La prueba y el camino · **Pauta:** 3 min · **Tipo:** flow

**Objetivo:** Convertir los pendientes en tareas con dueño

**En pantalla:**

- Esquema oficial de Shopee y salida esperada validada con el equipo de catálogo
- Integración: la API pública lee el producto (F8), pero escribir publicaciones y leer tablas necesita acceso interno
- Decidir dónde corre el batch (decisión 5) y qué pasa con missing (decisión 12)
- Fijar el tope de costo con la medición del 1/10 (decisión 11) y probar Haiku 4.5 (decisión 6)

**Temas para hablar:** Cada punto necesita responsable y fecha, y se completan en la última lámina. Retomar las dudas de AgentCore de la mañana y asignarlas a Juan David. Confirmar con Alephee si los datos pueden quedar en Langfuse Cloud. El código queda en el repositorio de Alephee que indique Rick.

**Transición:** Las trece decisiones.

### 68 · Las 13 decisiones (1 a 7).

**Sección:** 05 · La prueba y el camino · **Pauta:** 3 min · **Tipo:** table

**Objetivo:** Cerrar con el registro completo: las decisiones de la mañana

**En pantalla:**

- N / Decisión / Archivo
- 1 / Alcance: un canal, una familia, categoría + atributos / decisiones/01-alcance.md
- 2 / Contrato: missing y rejected con motivo / decisiones/02-contrato.md
- 3 / Tipo de aplicación: una llamada en la V1, Workflow con FunctionAgent en la V2 / decisiones/03-tipo-de-aplicacion.md
- 4 / Salida estructurada con Pydantic (Listing) / decisiones/04-salida-estructurada.md
- 5 / Dónde corre: local hoy, chat en AgentCore, batch a medir / decisiones/05-donde-corre.md
- 6 / Modelo: Claude Sonnet 5; Haiku 4.5 a probar / decisiones/06-modelo.md
- 7 / Stack: Python + LlamaIndex Workflows + BedrockConverse + Langfuse / decisiones/07-stack.md

**Temas para hablar:** Cada archivo tiene contexto, opciones, decisión y razonamiento. Si la sala decidió algo distinto de la propuesta, se escribe tal como se decidió.

**Transición:** Las de la tarde.

### 69 · Las 13 decisiones (8 a 13).

**Sección:** 05 · La prueba y el camino · **Pauta:** 3 min · **Tipo:** table

**Objetivo:** Cerrar con el registro completo: las decisiones de la tarde

**En pantalla:**

- N / Decisión / Archivo
- 8 / Criterio de éxito: el número de la pizarra / decisiones/08-criterio-de-exito.md
- 9 / Dataset: 30 reales con mock rotulado / decisiones/09-dataset.md
- 10 / La tabla manda: categoría y campos en código; el agente decide valores y lo no cubierto / decisiones/10-tabla-vs-agente.md
- 11 / Costo: tope acordado con Alephee sobre la medición del 1/10 (V2: ~9.970 tokens nuevos (sin caché) de entrada por producto) / decisiones/11-costo.md
- 12 / Cuando no sabe: faltante explícito con motivo; clean es la red final / decisiones/12-cuando-no-sabe.md
- 13 / Determinismo: caché por SKU + tablas + prompt en DynamoDB; se invalida al cargar una corrección / decisiones/13-determinismo-y-cache.md

**Temas para hablar:** Este registro es el método repetible. El próximo caso de uso de Alephee arranca por estas trece preguntas, con las respuestas de hoy como punto de partida.

**Transición:** Quién hace qué.

### 70 · Quién hace qué, para cuándo.

**Sección:** 05 · La prueba y el camino · **Pauta:** 1 min · **Tipo:** divider

**Objetivo:** Cerrar con responsables y fechas

**En pantalla:**

- Se completa en la sala.

**Temas para hablar:** Repartir los pendientes del camino a producción entre Alephee, Craftech y AWS, con fecha. Confirmar el repositorio donde queda el código. Agradecer y cerrar a las 17:00, con preguntas hasta las 17:30.

**Transición:** Fin.

## Fundamento editorial y revisión

Diseño de esta versión: [diseno-presentacion.md](warroom/diseno-presentacion.md). Revisión editorial de la versión anterior: [revision-agentes.md](warroom/revision-agentes.md).
