# Guion del warroom · por diapositiva

Versión del 1/10/2026 · 48 diapositivas · 6 bloques · 13 decisiones. Diseño en `warroom/diseno-presentacion.md`; fuentes externas en `warroom/fuentes.md`. Fuente única: `docs/warroom/diapositivas.json`. Se regenera con el generador que está en `old/scripts` hasta que vuelva al repositorio.

[Presentación interactiva](presentacion-warroom.html) · [PDF estático](presentacion-warroom.pdf)

## Dinámica acordada

Gastón conduce. El deck es una cadena de 13 decisiones de diseño. Cada tema tiene una lámina de concepto y una de decisión que se cierra en la sala antes de seguir. V1, V2 y V3 son los puntos donde lo decidido se construye y se corre. Pedir la opinión de quienes están remotos antes de cerrar cada decisión.

Las láminas de código salieron del deck con el reinicio del 1/10 y vuelven cuando el código nuevo exista. La propuesta de cada decisión está plegada y se abre después de escuchar al grupo. La decisión final se escribe en `decisiones/NN-titulo.md` y no en el deck. Las columnas de la prueba se completan con los experimentos del día en Langfuse.

## Mapa y tiempos

| Sección | Horario | Diapositivas | Resultado |
|---|---|---|---|
| 01 · Punto de partida | 09:00-09:30 | 1 a 8 | Ver el error de hoy y acordar qué construimos |
| 02 · Diseñar el agente | 09:30-11:15 | 9 a 25 | Tomar las decisiones que definen la V1 |
| 03 · V1 · el agente responde | 11:15-12:30 | 26 a 28 | Construir, correr y leer la primera versión |
| 04 · V2 · herramientas | 13:15-14:45 | 29 a 34 | Decidir qué resuelve la tabla y conectarla |
| 05 · V3 · control | 15:00-16:15 | 35 a 41 | Decidir qué pasa cuando el agente no sabe |
| 06 · La prueba y el camino | 16:15-17:00 | 42 a 48 | Medir contra el criterio y repartir lo que sigue |

Pausa de 11:00 a 11:15, almuerzo de 12:30 a 13:15 y pausa de 14:45 a 15:00. El bloque V3 incluye la preparación de la comparación, de 16:00 a 16:15. El margen de preguntas de 17:00 a 17:30 depende de la logística.

Los minutos por diapositiva son una pauta. Preservar la hora de cierre. Si el bloque 2 se pasa, fusionar las láminas de criterios de modelo y catálogo de Bedrock y acortar la de stack; nunca saltar una decisión.

## Distribución completa dentro de cada bloque

| Bloque | Diapositivas y demos | Trabajo reservado | Total |
|---|---:|---|---:|
| 01 · Punto de partida | 22 min | Dolores del equipo y preguntas: 2 min | 24 min |
| 02 · Diseñar el agente | 55 min | Pizarra: dudas de AgentCore para Juan David: 5 min; Pausa 11:00: 15 min | 75 min |
| 03 · V1 · el agente responde | 9 min | Corridas sobre otros casos: 25 min | 34 min |
| 04 · V2 · herramientas | 20 min | Corrida del lote y lectura: 25 min | 45 min |
| 05 · V3 · control | 23 min | Corrida del lote con V3: 20 min | 43 min |
| 06 · La prueba y el camino | 17 min | Documentar decisiones y responsables: 15 min | 32 min |

Las reservas son para pizarra, corridas del lote y preguntas dentro del bloque. Son pautas ajustables de esta jornada.

## Preparación del facilitador

- Caso guía de las demos: `error-88904447` (Código OEM = ABS Plastic). Confirmarlo con el grupo en la decisión 9.
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

**Transición:** Lo que vamos a hacer hoy.

### 02 · Lo que vamos a hacer hoy.

**Sección:** 01 · Punto de partida · **Pauta:** 3 min · **Tipo:** compare

**Objetivo:** Ubicar al grupo en el recorrido del día, por temas

**En pantalla:**

- Decidimos, construimos y medimos. Cada bloque cierra con una versión que funciona.
- 1 · PUNTO DE PARTIDA | El error de hoy, el alcance y el contrato
- 2 · DISEÑAR EL AGENTE | Tipo de aplicación, prompt, dónde corre, modelo, stack y criterio de éxito
- 3 · V1 · EL AGENTE RESPONDE | Una sola llamada al modelo, sin herramientas: qué resuelve solo y qué no
- 4 · V2 · HERRAMIENTAS | Las tablas de Alephee como herramientas que el agente consulta
- 5 · V3 · CONTROL | Validaciones en código, correcciones del equipo y caché por SKU
- 6 · LA PRUEBA | El proceso de hoy contra V1, V2 y V3, y el camino a producción

**Temas para hablar:** Son seis bloques. Los dos primeros terminan en la V1, el de herramientas en la V2 y el de control en la V3. La prueba mide todo con el criterio que acordamos antes de escribir código. Horarios para quien conduce: 09:00 punto de partida, 09:30 diseño, 11:15 V1, 13:15 V2, 15:00 V3 y 16:15 prueba. Hay pausa a las 11:00, almuerzo de 12:30 a 13:15 y otra pausa a las 14:45. El cierre técnico es a las 17:00 y quedan preguntas hasta las 17:30.

**Transición:** Un producto real para ver qué entra y qué queremos que salga.

### 03 · De un producto de Alephee a una publicación de Shopee.

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

### 04 · Hoy: dos llamadas, un merge y un presupuesto que se agota.

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

### 05 · Lo que Shopee rechazó y lo que aceptó mal.

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

### 06 · ¿Qué hace y qué no hace?

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

### 07 · Entra un producto. Sale una propuesta de publicación.

**Sección:** 01 · Punto de partida · **Pauta:** 3 min · **Tipo:** cards

**Objetivo:** Decir el contrato en palabras antes de verlo en código

**En pantalla:**

- Entrada: el producto de Alephee (SKU, nombre, descripción, categoría legacy, atributos)
- Salida: la categoría de Shopee más los atributos con URN, valueId y valor
- Y dos listas más: missing (obligatorios sin dato) y rejected (atributos descartados, con motivo)

**Temas para hablar:** La salida es una propuesta de mapeo, todavía no es la publicación final. Lo nuevo son las dos listas. Una dice qué obligatorio quedó sin dato y por qué. La otra dice qué atributo del producto se descartó y por qué. Con eso dejamos de publicar sin atributos sin que nadie se entere.

**Transición:** Decisión 2: cómo se informa lo que no se pudo mapear.

### 08 · ¿Qué recibe y qué entrega?

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

### 09 · Diseñar antes de escribir.

**Sección:** 02 · Diseñar el agente · **Pauta:** 1 min · **Tipo:** divider

**Objetivo:** Abrir el bloque de diseño

**En pantalla:**

- Siete decisiones que definen la V1

**Temas para hablar:** En este bloque no corremos nada. Tomamos las decisiones que la V1 implementa a las 11:15: tipo de aplicación, prompt, dónde corre, modelo, stack y cómo se mide. Cada decisión tiene opciones con consecuencias y se cierra antes de pasar a la siguiente.

**Transición:** Primero, qué tipos de aplicación existen.

### 10 · Cuatro formas de usar un modelo.

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

### 11 · ¿Single prompt o agente?

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

### 12 · Un prompt tiene cinco partes.

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

### 13 · Buenas prácticas que cambian el resultado.

**Sección:** 02 · Diseñar el agente · **Pauta:** 3 min · **Tipo:** cards

**Objetivo:** Tres prácticas con efecto medible

**En pantalla:**

- Lo fijo primero y lo variable al final: así funciona la caché de prompt (F4, F7)
- Salida con esquema, en lugar de pedir JSON en el texto
- Decir qué hacer cuando no sabe, además de qué hacer

**Temas para hablar:** La primera baja el costo directamente. Bedrock guarda en caché el comienzo del prompt que no cambia, marcado con un cachePoint (F4). Para Claude Sonnet 5 el mínimo es 1.024 tokens, y la caché dura 5 minutos desde el último uso. OpenAI hace lo mismo de forma automática (F7). El prompt actual pone el producto antes de la lista de categorías, así que el comienzo cambia en cada llamada y no se cachea nada. Reordenarlo ya bajaría el costo sin cambiar de proveedor, pero hay que medirlo antes de darlo por hecho. En la V1 lo vemos en Langfuse, en cada traza. Fuentes en docs/warroom/fuentes.md.

**Transición:** Decisión 4.

### 14 · ¿Cómo garantizamos el formato?

**Sección:** 02 · Diseñar el agente · **Pauta:** 4 min · **Tipo:** decision

**Objetivo:** Cerrar la decisión 4

**En pantalla:**

- La V1 usa la opción B · si gana otra, vemos qué cambia

**Temas para hablar:** Preguntar cuántas veces tuvieron que arreglar un JSON mal formado. La salida estructurada existe en todos los proveedores grandes, así que no depende de Bedrock. El Workflow de la V1 cierra con un evento tipado, MappingCompleted, que trae el Listing.

**Transición:** Ahora, dónde va a correr.

**Decisión 4:** ¿Cómo se garantiza que la salida cumpla el contrato?

1. A · Pedir JSON en el texto y parsearlo (hoy)
2. B · Salida estructurada con un modelo Pydantic: el modelo devuelve un Listing validado
3. C · Corregir la respuesta después con expresiones regulares

**Propuesta:** B. El formato deja de ser un pedido en el prompt y pasa a ser un contrato. En LlamaIndex es as_structured_llm(Listing): el modelo responde por tool calling y la librería valida contra el esquema. Si la salida no cumple, el Workflow devuelve el error en lugar de publicar algo a medias. C arregla síntomas: si el modelo omite un campo, la expresión regular no lo inventa.

**Archivo:** `decisiones/04-salida-estructurada.md`

### 15 · Dónde corre: AgentCore o contenedor propio.

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

### 16 · La infraestructura, de punta a punta.

**Sección:** 02 · Diseñar el agente · **Pauta:** 2 min · **Tipo:** diagram

**Objetivo:** Mostrar todas las piezas de AWS y separar lo que hay de lo que falta

**En pantalla:**


**Temas para hablar:** Arriba está el camino del chat. El widget llama al BFF, que valida el token, aplica el guardrail de entrada y los topes, y encola el mensaje. El worker invoca el Runtime, que llama a Bedrock y a las herramientas por el Gateway. Una de esas herramientas es map_product, que corre la V1. Abajo a la derecha, punteado, está el batch de catálogo: hoy corre en local como experimento de Langfuse, y su lugar en producción es la decisión 5. La franja de abajo es el monitoreo: logs y métricas en CloudWatch, y trazas, prompts y experimentos en Langfuse.

**Pregunta / participación:** ¿Qué piezas ya tiene Alephee y cuáles reemplazaríamos?

**Transición:** Decisión 5.

**Diagrama (cajas):**

- Widget de chat: apps/web · packages/widget
- BFF · Lambda: auth HMAC · topes · guardrail de entrada
- SQS FIFO: MensajesCola · con DLQ
- Worker · Lambda: InvokeAgentRuntime · timeout 3 min
- AgentCore Runtime: contenedor ARM64 desde ECR · core/server.py · /invocations · ChatWorkflow + map_product (V1)
- DynamoDB: Messages · Sessions · Limits
- AgentCore Gateway: tools MCP · SigV4
- Amazon Bedrock: Claude Sonnet 5 · us-east-1 · guardrail de salida
- API del cliente: target OpenAPI (demo)
- Knowledge Base: S3 Vectors · ToolDocumentos
- Escalamiento: ToolEscalamiento
- Batch de catálogo · hoy local: scripts/experiment.sh → V1 · experimentos y trazas en Langfuse · producción: a decidir (decisión 5)
- Observabilidad · CloudWatch, X-Ray y Langfuse: logs y métricas en CloudWatch · trazas del agente, prompts y experimentos en Langfuse

Es la infraestructura del template en infra/sst. El chat de la V1 se despliega en la cuenta sandbox con el stage warroom, y las trazas del agente van a Langfuse. AgentCore Memory se sacó del stack.

### 17 · ¿Dónde corre?

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

### 18 · Elegir el modelo: qué pesa en este caso.

**Sección:** 02 · Diseñar el agente · **Pauta:** 3 min · **Tipo:** cards

**Objetivo:** Criterios de elección antes de nombrar modelos

**En pantalla:**

- Seguir reglas sin inventar valores: es lo que más falla hoy
- Costo por token con caché de prompt: el presupuesto actual es de USD 350 por mes
- Latencia: no es una restricción (hoy el batch tarda 13 s por producto)
- Que esté disponible en la región y habilitado en la cuenta

**Temas para hablar:** El orden importa. Primero, calidad en lo que falla hoy: inventar valores e ignorar reglas. Después, costo con caché. La latencia va al final porque es batch. Un modelo más chico puede ganar en costo y perder en reglas, y eso se decide midiendo sobre el dataset.

**Transición:** Qué hay disponible en Bedrock.

### 19 · Qué hay en Bedrock.

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

### 20 · ¿Qué modelo?

**Sección:** 02 · Diseñar el agente · **Pauta:** 4 min · **Tipo:** decision

**Objetivo:** Cerrar la decisión 6 con la prueba de Haiku como pendiente

**En pantalla:**

- Tomada el 25/09 (CLAUDE.md, decisión 6) · hoy se valida o se cambia

**Temas para hablar:** Lo primero que van a preguntar es por qué Sonnet 5 y no 5.5. La decisión es del 25/09 y el modelo ya está probado en este repositorio. El 5.5 se compara sobre el mismo dataset antes de adoptarlo. Anotar las pruebas de 5.5 y de Haiku 4.5 como tareas con dueño. Si Alephee quiere seguir con OpenAI, los GPT también están en Bedrock (F6) y la arquitectura no cambia.

**Transición:** Con qué lo construimos.

**Decisión 6:** ¿Con qué modelo construimos y medimos?

1. A · Claude Sonnet 5 en Bedrock, vía Converse
2. B · Un modelo más chico y barato (Claude Haiku 4.5) y medir
3. C · Seguir con OpenAI y solo reordenar el prompt para la caché

**Propuesta:** A para construir hoy. Es la decisión del 25/09 y el ID está verificado en Converse. Claude Sonnet 5.5 también está en Bedrock (F6). Compararlo con Haiku 4.5 (B) es una corrida más del experimento con otra variable de entorno, y queda como pendiente con dueño. C mejora el costo pero no resuelve el contrato ni el control.

**Archivo:** `decisiones/06-modelo.md`

### 21 · Stack y harness.

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

### 22 · ¿Con qué lo construimos?

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

### 23 · ¿Cuándo está bien hecho?

**Sección:** 02 · Diseñar el agente · **Pauta:** 3 min · **Tipo:** cards

**Objetivo:** Acordar la métrica antes de escribir código

**En pantalla:**

- Esquema de Shopee y salida esperada MOCK · validar con el equipo de catálogo
- Exacto: categoría correcta, ningún atributo de más ni de menos, nada fuera de la lista del canal, sin duplicados y con los faltantes informados
- También medimos precisión y recall de atributos, valores inválidos, tokens y segundos, todo en Langfuse
- Dataset: 30 productos reales con su publicación actual. El esquema de Shopee y la salida esperada son simulados

**Temas para hablar:** La vara es estricta a propósito. Pero la salida esperada es mock: la armamos a partir de la publicación actual limpia, así que hereda sus omisiones y castiga aciertos que hoy nadie mapea. Por eso los exactos van a salir bajos en todas las versiones, y hay que mirar también inválidos, duplicados y faltantes. Cada versión corre como experimento en Langfuse, al lado del proceso de hoy. El esquema oficial de Shopee y la validación con catálogo quedan pendientes.

**Transición:** Decisiones 8 y 9.

### 24 · ¿Cuál es el número que aceptamos?

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

### 25 · ¿Con qué dataset?

**Sección:** 02 · Diseñar el agente · **Pauta:** 4 min · **Tipo:** decision

**Objetivo:** Cerrar la decisión 9 y pasar a construir

**En pantalla:**


**Temas para hablar:** Pedir al grupo que elija el caso guía de las demos. La propuesta es 88904447, el del Código OEM. A las 11:00 hay pausa, y a las 11:15 construimos la V1 con todo lo decidido.

**Transición:** Pausa. Volvemos con la V1.

**Decisión 9:** ¿Sobre qué datos construimos y medimos?

1. A · Los 30 reales del zip, con esquema y expected mock rotulados
2. B · Solo los 10 casos mock de borde
3. C · Esperar el esquema oficial de Shopee para empezar

**Propuesta:** A. Son productos reales, con publicaciones reales y rechazos reales de Shopee. Lo simulado queda rotulado y se valida con catálogo después. Los 10 casos mock quedan como pruebas de borde.

**Archivo:** `decisiones/09-dataset.md`

### 26 · V1 · el agente responde.

**Sección:** 03 · V1 · el agente responde · **Pauta:** 1 min · **Tipo:** divider

**Objetivo:** Abrir la V1 con la expectativa correcta

**En pantalla:**

- Una sola llamada al modelo, sin herramientas. Esperamos que falle, y esos fallos justifican lo que sigue.

**Temas para hablar:** La V1 junta las decisiones 1 a 9. Es un Workflow de LlamaIndex con dos pasos. El primero, prepare, arma el mensaje: el catálogo de Shopee al principio, para que entre en la caché, y el producto al final. El segundo, map, hace una llamada estructurada y devuelve un Listing validado. El prompt de sistema vive en Langfuse y la evaluación corre ahí. La V1 no usa las tablas de referencia a propósito, porque queremos ver qué resuelve el modelo solo. La regla del día sigue: no pasamos al bloque siguiente con algo roto. Si la V1 se equivoca en un atributo, eso no frena el día. Lo anotamos como evidencia para la V2.

**Transición:** Lo corremos sobre el caso guía.

### 27 · Demo · un caso real por V1.

**Sección:** 03 · V1 · el agente responde · **Pauta:** 5 min · **Tipo:** demo

**Objetivo:** Ver una salida real y leerla con el contrato en la mano

**En pantalla:**


**Temas para hablar:** Antes de correr, pedir una predicción: ¿qué va a poner en Código OEM? Correr y leer la salida en el orden de la lista. Después abrir la traza en Langfuse y mostrar el prompt, la respuesta y los tokens. Si todavía no tenemos el OK de Alephee para subir los datos reales a Langfuse, usar el caso mock 01-real-calota-aro14 con --data mock. Si Bedrock no responde, por sesión SSO vencida o por throttling, mostrar la corrida de la mañana y decirlo. El lote completo corre en segundo plano mientras seguimos.

**Transición:** Qué falló y qué capa lo resuelve.

```bash
scripts/experiment.sh --version v1 --data real --case error-88904447
```

**Mirar:**

- La categoría que eligió el modelo y la que dice reference_category
- Cada atributo: de dónde sale el valor y si está en la lista del canal
- missing y rejected: si informa lo que no pudo o completa igual
- En la traza de Langfuse: tokens de entrada, tokens leídos de caché y segundos

**Respaldo:** la corrida del experimento v1-real de la mañana, en Langfuse

### 28 · Qué esperamos que falle en la V1 y qué capa lo resuelve.

**Sección:** 03 · V1 · el agente responde · **Pauta:** 3 min · **Tipo:** table

**Objetivo:** Convertir cada fallo de la V1 en la justificación de una capa

**En pantalla:**

- Hipótesis para confirmar con la corrida del día · salida esperada MOCK
- Fallo esperado / Cómo se ve / Capa que lo resuelve
- Categoría inventada cuando el producto no trae una / Caso mock 09, sin categoría de origen / V2 · la tabla de categorías
- Valor fuera de la lista del canal / Score invalid_values en Langfuse / V3 · validación en código
- Obligatorio sin informar en missing / Score missing_ok en Langfuse / V3 · validación en código
- Unos 20.000 tokens de entrada por producto / Tokens de cada traza en Langfuse / V2 · herramientas en lugar del catálogo entero
- Categoría acertada con ayuda / Elige entre 23 categorías que incluyen la correcta / V2 · la tabla de categorías

**Temas para hablar:** Esto es lo que buscamos con la V1: evidencia. Si inventa la categoría cuando el producto no trae una, eso justifica la V2, porque sin referencia la respuesta tiene que salir de la tabla y no del modelo. Los valores fuera de lista y los obligatorios sin informar justifican la V3: una regla escrita en el prompt no garantiza que se cumpla, y hay que comprobarla en código. Los tokens son el costo de mandar el catálogo entero en cada llamada. Un aviso: la V1 elige entre 23 categorías que siempre incluyen la correcta, así que su número de categorías sale optimista. Completar la columna con lo que muestre Langfuse.

**Pregunta / participación:** ¿Alguno de estos fallos les sorprende? ¿Cuál esperaban?

**Transición:** Almuerzo. A las 13:15, herramientas.

### 29 · V2 · herramientas.

**Sección:** 04 · V2 · herramientas · **Pauta:** 1 min · **Tipo:** divider

**Objetivo:** Retomar después del almuerzo y abrir la V2

**En pantalla:**

- El agente consulta antes de decidir.

**Temas para hablar:** En una frase: la V1 responde sola y falla donde necesita datos que no tiene. La V2 le da herramientas para consultar las tablas de referencia y el esquema del canal. Acá entra el FunctionAgent de LlamaIndex, porque ahora el modelo sí tiene que decidir qué consultar. El prompt deja de llevar el canal entero y el agente pide solo lo que necesita para este producto.

**Transición:** Qué es una herramienta.

### 30 · Una herramienta es una función que el modelo pide y el código ejecuta.

**Sección:** 04 · V2 · herramientas · **Pauta:** 3 min · **Tipo:** flow

**Objetivo:** Definir herramienta sin jerga

**En pantalla:**

- El modelo pide buscar_categoria('urn:category:1106872')
- El programa ejecuta la función: consulta la tabla
- Devuelve {encontrada: true, urn, name} o {encontrada: false, motivo}
- El modelo sigue con ese dato, no con su memoria

**Temas para hablar:** El modelo no ejecuta nada. Escribe un pedido con nombre y argumentos, el programa lo ejecuta y le devuelve el resultado como un mensaje más. Por eso la herramienta es determinista y el modelo no. Hay herramientas de lectura, para consultar, y de acción, como publicar. Hoy todas las nuestras son de lectura. Que la herramienta exista no obliga al modelo a usarla ni a respetar lo que devuelve. Eso lo controla la V3.

**Transición:** Decisión 10: qué decide la tabla y qué decide el agente.

### 31 · ¿Qué decide la tabla y qué decide el agente?

**Sección:** 04 · V2 · herramientas · **Pauta:** 4 min · **Tipo:** decision

**Objetivo:** Cerrar la decisión 10

**En pantalla:**

- Se construye en la V2 y la V3

**Temas para hablar:** B es el error más común: dejar que el modelo mejore un mapeo que el equipo de catálogo mantiene a mano. Si la tabla está mal, se corrige la tabla. C ya lo descartamos en la decisión 3. Lo que la tabla resuelve se aplica en código, sin pasar por el modelo.

**Transición:** Los números de la corrida del 28/09.

**Decisión 10:** ¿Qué decide la tabla y qué decide el agente?

1. A · La tabla fija la categoría y los campos; el agente solo elige el valor equivalente de la lista y cubre lo que la tabla no tiene
2. B · El agente puede corregir la tabla si cree que está mal
3. C · Todo por tabla; sin modelo

**Propuesta:** A. La tabla manda, como se acordó el 25/08 con Juan David. Lo que la tabla no cubre, como los valores de lista o los atributos sin referencia, es lo único que decide el agente.

**Archivo:** `decisiones/10-tabla-vs-agente.md`

### 32 · Costo por producto, medido.

**Sección:** 04 · V2 · herramientas · **Pauta:** 3 min · **Tipo:** table

**Objetivo:** Mostrar el efecto de herramientas + caché en tokens y latencia

**En pantalla:**

- Se completa con los experimentos del día en Langfuse
- Versión / Entrada sin caché / Leída de caché / Segundos
- V1 / · / · / ·
- V2 / · / · / ·

**Temas para hablar:** Completar con los datos de Langfuse. Cada traza trae tokens nuevos, tokens leídos de caché, tokens escritos en caché y segundos. Como referencia, en el ensayo del 28/09 con el código anterior, la versión de una llamada pagaba unos 22.000 tokens nuevos por producto. La de herramientas pagaba unos 1.600 nuevos y leía 12.000 de caché. Para hablar de dólares faltan la escritura en caché, la salida y los reintentos. No sacar el ahorro solo de esta tabla.

**Transición:** Decisión 11: el costo.

### 33 · ¿Cuánto puede costar?

**Sección:** 04 · V2 · herramientas · **Pauta:** 4 min · **Tipo:** decision

**Objetivo:** Cerrar la decisión 11 con la medición como tarea

**En pantalla:**

- Abierta: todavía no hay tope ni una medición completa

**Temas para hablar:** Anotar como pendiente la corrida de medición completa, con su dueño. Si el grupo quiere un número hoy, dar el de tokens y no el de dólares.

**Transición:** El mismo caso por V2.

**Decisión 11:** ¿Cómo tratamos la restricción de costo del modelo?

1. A · Tope mensual acordado con Alephee y medición por producto: tokens de entrada, salida, caché leída y escrita
2. B · Sin tope: se mide después
3. C · El tope de hoy (USD 350) y publicar sin atributos al agotarse

**Propuesta:** A. Hoy el tope corta la calidad, que es la opción C. Con la caché de prompt y la caché por SKU (decisión 13) el costo por producto baja. El número se fija con una corrida completa medida en Langfuse.

**Archivo:** `decisiones/11-costo.md`

### 34 · Demo · el mismo caso por V2.

**Sección:** 04 · V2 · herramientas · **Pauta:** 5 min · **Tipo:** demo

**Objetivo:** Comparar V1 y V2 sobre el mismo caso

**En pantalla:**


**Temas para hablar:** Es el mismo caso de la mañana, para comparar. Antes de correr, pedir una predicción: ¿va a usar la referencia de atributos? Mirar primero qué herramientas pidió. Si entrega un valor fuera de lista, señalarlo: la herramienta no obliga, y eso lo resuelve la V3. Pausa a las 14:45.

**Transición:** Pausa. A las 15:00, control.

```bash
scripts/experiment.sh --version v2 --data real --case error-88904447
```

**Mirar:**

- Qué herramientas pidió y en qué orden, en la traza de Langfuse
- La categoría ahora sale de la tabla y no del modelo
- Código OEM: ¿sigue saliendo ABS Plastic?
- Tokens leídos de caché frente a los nuevos

**Respaldo:** la corrida del experimento v2-real, en Langfuse

### 35 · V3 · control.

**Sección:** 05 · V3 · control · **Pauta:** 1 min · **Tipo:** divider

**Objetivo:** Abrir la V3

**En pantalla:**

- Qué pasa cuando el agente no sabe.

**Temas para hablar:** La V2 consulta, pero no está obligada a respetar lo que consulta. La V3 suma tres cosas: validaciones en código que revisan cada entrega, las correcciones que carga el equipo de catálogo y una caché por SKU para no mapear dos veces el mismo producto. Con la V3 dejamos de publicar sin atributos.

**Transición:** El agente completo, en un dibujo.

### 36 · El agente por dentro: código y modelo.

**Sección:** 05 · V3 · control · **Pauta:** 3 min · **Tipo:** diagram

**Objetivo:** Ver las tres versiones como capas de un mismo flujo

**En pantalla:**


**Temas para hablar:** Verde es código determinista y violeta es el modelo. La categoría sale de la tabla antes de llamar al modelo. Si no hay referencia, el flujo termina con un faltante explícito. Si el SKU ya se mapeó, sale de la caché. El modelo pide herramientas en un loop con límite y entrega. La validación revisa la entrega y, si hay problemas, se los devuelve al modelo para una sola ronda de corrección. Lo que siga mal se descarta al final. La V1 de hoy es solo la caja violeta.

**Pregunta / participación:** ¿Qué caja sacarían a código si pudieran?

**Transición:** Qué es un guardrail acá.

**Diagrama (cajas):**

- Herramientas · código: buscar_categoria · atributos_del_canal · buscar_atributos_referencia · buscar_correcciones (V3)
- FuenteCatalogo: hoy: archivos de data/ · mañana: lo que exponga Alephee
- Producto: MapeoStart · SKU + categoría
- Categoría por tabla: reference_category · en código (V3)
- Caché (V3): SKU + categoría · legacy
- Claude Sonnet 5: decide qué consultar · hasta 6 rondas · la última: solo entregar
- Guardrail (V3): revisar: dominio, · duplicados, obligatorios
- Red final (V3): limpiar: descarta · y marca missing
- Sin referencia: missing: category · fin, sin modelo
- Guardada: sale sin llamar · al modelo
- Publicación: MapeoDone · se guarda en caché

La V1 es solo la caja del modelo, con una llamada estructurada. La V2 suma las herramientas y el FunctionAgent. La V3 suma la categoría por tabla, la caché, las correcciones y las validaciones.

### 37 · Guardrail: una comprobación en código.

**Sección:** 05 · V3 · control · **Pauta:** 3 min · **Tipo:** compare

**Objetivo:** Diferenciar guardrail de regla del prompt

**En pantalla:**

- REVISAR | Lista los problemas en lenguaje claro y se los devuelve al agente, que tiene una ronda para corregir
- LIMPIAR | Al final descarta lo inválido con su motivo y marca los obligatorios que faltan
- NUNCA PUBLICA | Un valor fuera de la lista del canal, un -1 ni un duplicado. No verifica que el valor sea cierto: eso depende del esquema y de catálogo

**Temas para hablar:** Una regla en el prompt depende de que el modelo obedezca. Un guardrail la comprueba en código. Funciona en dos pasos. Primero le devuelve los problemas al agente para que corrija, una sola vez. Lo que siga mal se descarta en código. Tiene un límite: comprueba que el valor esté en el esquema y en la lista del canal, pero no que sea cierto para el producto.

**Transición:** Decisión 12.

### 38 · ¿Qué hace cuando no sabe?

**Sección:** 05 · V3 · control · **Pauta:** 4 min · **Tipo:** decision

**Objetivo:** Cerrar la decisión 12 y dejar la política de revisión como pendiente

**En pantalla:**

- La V3 se construye con la opción B · C se puede armar encima

**Temas para hablar:** Marcar missing no arma solo un circuito de revisión. Hoy es una lista en la salida. Quién la mira, dónde y con qué herramienta lo decide Alephee como producto. Anotar el dueño.

**Transición:** Memoria.

**Decisión 12:** ¿Qué hace el agente cuando no puede completar un atributo obligatorio?

1. A · Publicar sin el atributo (hoy)
2. B · Faltante explícito con motivo: la publicación sale con missing y alguien decide
3. C · Bloquear la publicación hasta revisión humana

**Propuesta:** B. Reemplaza el publicar sin atributos. Quién recibe la lista missing y si bloquea la publicación es parte de la integración con la plataforma de Alephee, y queda pendiente con dueño. C es una política válida que se puede construir sobre B.

**Archivo:** `decisiones/12-cuando-no-sabe.md`

### 39 · Memoria: correcciones del equipo de catálogo.

**Sección:** 05 · V3 · control · **Pauta:** 3 min · **Tipo:** cards

**Objetivo:** Definir memoria para este agente sin prometer aprendizaje automático

**En pantalla:**

- Una corrección dice: en esta categoría, este valor del producto va a este atributo con este valor del canal
- El agente la consulta como una herramienta más, y la corrección manda sobre su criterio
- En la V3 de hoy es un archivo local. En producción, una tabla de Alephee o AgentCore Memory

**Temas para hablar:** Acá memoria no quiere decir que el agente aprende solo. Quiere decir que reusa correcciones que alguien del equipo de catálogo cargó a mano. Se cargan con un comando y el agente las consulta por categoría. Que las respete depende de que las consulte, por eso la instrucción lo exige y la validación revisa después.

**Transición:** Decisión 13.

### 40 · ¿Cómo garantizamos determinismo?

**Sección:** 05 · V3 · control · **Pauta:** 4 min · **Tipo:** decision

**Objetivo:** Cerrar la decisión 13 con las extensiones de la clave como pendiente

**En pantalla:**

- La V3 se construye con la opción A · falta definir cuándo se invalida

**Temas para hablar:** Preguntar qué cambios deberían invalidar la caché: el producto, las tablas o el esquema del canal. Anotar la lista, porque es la especificación de la clave de producción.

**Transición:** Demo: corregir y repetir.

**Decisión 13:** ¿Cómo garantizamos que el mismo SKU dé la misma salida?

1. A · Caché por SKU + canal; se invalida al corregir o al cambiar las tablas
2. B · Seed fijo (lo que se intentó hoy; los parámetros exactos siguen sin confirmar)
3. C · Recalcular siempre y aceptar variación

**Propuesta:** A. Un mapeo por SKU y canal. B reduce la variación pero no la elimina, y sigue pagando cada corrida. Antes de producción, la clave tiene que sumar la versión de las tablas y separar por cuenta.

**Archivo:** `decisiones/13-determinismo-y-cache.md`

### 41 · Demo · corregir y repetir.

**Sección:** 05 · V3 · control · **Pauta:** 5 min · **Tipo:** demo

**Objetivo:** Ver memoria, guardrails y caché en una sola secuencia

**En pantalla:**


**Temas para hablar:** Elegir con el grupo la corrección a cargar sobre el caso guía: un valor de lista que el modelo eligió mal. Cargarla, correr y leer. Correr de nuevo: tiene que salir de la caché. Si algo falla, mostrar la corrida guardada y decirlo.

**Transición:** A las 16:15, la prueba.

```bash
scripts/experiment.sh --version v3 --data real --case error-88904447
```

**Mirar:**

- La consulta de correcciones aparece en la traza
- El valor corregido sale tal cual lo cargó catálogo
- rejected explica cada descarte de la validación
- Segunda corrida del mismo caso: sale de caché, sin tokens

**Respaldo:** la corrida del experimento v3-real, en Langfuse

### 42 · La prueba.

**Sección:** 06 · La prueba y el camino · **Pauta:** 1 min · **Tipo:** divider

**Objetivo:** Abrir la prueba con el criterio acordado a la vista

**En pantalla:**

- El proceso de hoy contra V1, V2 y V3, sobre los 30, con el criterio de la decisión 8.

**Temas para hablar:** Volver a la pizarra y al número de la decisión 8. Los experimentos corrieron durante los bloques, y acá los comparamos en Langfuse. Si alguno no terminó, decirlo.

**Transición:** Los resultados.

### 43 · Resultados (se completan en vivo).

**Sección:** 06 · La prueba y el camino · **Pauta:** 3 min · **Tipo:** table

**Objetivo:** Leer los resultados contra el criterio, sin maquillar

**En pantalla:**

- Columna Hoy: publicaciones que Alephee exportó, salida esperada MOCK. Las demás salen de los experimentos de Langfuse
- Métrica / Hoy / V1 / V2 / V3
- Casos exactos / 7 / · / · / ·
- Categoría correcta / 28 / · / · / ·
- Valores inválidos (-1 o fuera de lista) / 47 / · / · / ·
- Duplicados / 5 / · / · / ·
- Obligatorios sin informar / 2 / · / · / ·

**Temas para hablar:** Completar las columnas con los experimentos del día. La columna Hoy sale de la misma métrica aplicada a las publicaciones actuales. Al leer la V1, recordar que su categoría es optimista, porque elige entre 23 opciones que incluyen la correcta. Si los exactos salen bajos en todas las columnas, decirlo y explicar por qué en la lámina siguiente.

**Transición:** Cómo leer la tabla.

### 44 · Cómo leer la tabla.

**Sección:** 06 · La prueba y el camino · **Pauta:** 3 min · **Tipo:** cards

**Objetivo:** Dar la lectura honesta de los resultados

**En pantalla:**

- Exactos bajos en todas las columnas: la salida esperada hereda las omisiones del proceso actual y castiga aciertos que hoy nadie mapea
- Inválidos y duplicados sí son errores seguros: es lo primero que tiene que bajar
- Categoría: la V1 elige entre 23 opciones con la correcta adentro, así que su número es optimista

**Temas para hablar:** Lo que se puede afirmar: estos controles detectan errores concretos, y cada versión los baja o no. Lo que todavía no se puede afirmar es una mejor exactitud general, porque la salida esperada es mock. Un control también puede bajar errores quitando información, así que hay que mirar control y cobertura juntos.

**Pregunta / participación:** ¿Qué evidencia pedirían antes de un piloto con un concesionario?

**Transición:** El camino a producción.

### 45 · Camino a producción.

**Sección:** 06 · La prueba y el camino · **Pauta:** 3 min · **Tipo:** flow

**Objetivo:** Convertir los pendientes en tareas con dueño

**En pantalla:**

- Esquema oficial de Shopee y salida esperada validada con el equipo de catálogo
- Integración: la API pública lee el producto (F8), pero escribir publicaciones y leer tablas necesita acceso interno
- Decidir dónde corre el batch (decisión 5) y qué pasa con missing (decisión 12)
- Medir el costo completo y fijar el tope (decisión 11), y probar Haiku 4.5 (decisión 6)

**Temas para hablar:** Cada punto necesita responsable y fecha, y se completan en la última lámina. Retomar las dudas de AgentCore de la mañana y asignarlas a Juan David. Confirmar con Alephee si los datos pueden quedar en Langfuse Cloud. El código queda en el repositorio de Alephee que indique Rick.

**Transición:** Las trece decisiones.

### 46 · Las 13 decisiones (1 a 7).

**Sección:** 06 · La prueba y el camino · **Pauta:** 3 min · **Tipo:** table

**Objetivo:** Cerrar con el registro completo: las decisiones de la mañana

**En pantalla:**

- N / Decisión / Archivo
- 1 / Alcance: un canal, una familia, categoría + atributos / decisiones/01-alcance.md
- 2 / Contrato: missing y rejected con motivo / decisiones/02-contrato.md
- 3 / Tipo de aplicación: una llamada estructurada, y escalar / decisiones/03-tipo-de-aplicacion.md
- 4 / Salida estructurada con Pydantic (Listing) / decisiones/04-salida-estructurada.md
- 5 / Dónde corre: local hoy, chat en AgentCore, batch a medir / decisiones/05-donde-corre.md
- 6 / Modelo: Claude Sonnet 5; Haiku 4.5 a probar / decisiones/06-modelo.md
- 7 / Stack: Python + LlamaIndex Workflows + BedrockConverse + Langfuse / decisiones/07-stack.md

**Temas para hablar:** Cada archivo tiene contexto, opciones, decisión y razonamiento. Si la sala decidió algo distinto de la propuesta, se escribe tal como se decidió.

**Transición:** Las de la tarde.

### 47 · Las 13 decisiones (8 a 13).

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

**Temas para hablar:** Este registro es el método repetible. El próximo caso de uso de Alephee arranca por estas trece preguntas, con las respuestas de hoy como punto de partida.

**Transición:** Quién hace qué.

### 48 · Quién hace qué, para cuándo.

**Sección:** 06 · La prueba y el camino · **Pauta:** 1 min · **Tipo:** divider

**Objetivo:** Cerrar con responsables y fechas

**En pantalla:**

- Se completa en la sala.

**Temas para hablar:** Repartir los pendientes del camino a producción entre Alephee, Craftech y AWS, con fecha. Confirmar el repositorio donde queda el código. Agradecer y cerrar a las 17:00, con preguntas hasta las 17:30.

**Transición:** Fin.

## Fundamento editorial y revisión

Diseño de esta versión: [diseno-presentacion.md](warroom/diseno-presentacion.md). Revisión editorial de la versión anterior: [revision-agentes.md](warroom/revision-agentes.md).
