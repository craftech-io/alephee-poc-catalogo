# Guion del warroom · por diapositiva

Versión del 30/09/2026 · 48 diapositivas · 6 bloques · 13 decisiones. Diseño en `warroom/diseno-presentacion.md`; fuentes externas en `warroom/fuentes.md`. Fuente única: `docs/warroom/diapositivas.json`. Se regenera con `python3 scripts/generar_presentacion.py`.

[Presentación interactiva](presentacion-warroom.html) · [PDF estático](presentacion-warroom.pdf)

## Dinámica acordada

Gastón conduce. El deck es una cadena de 13 decisiones de diseño: cada tema tiene una lámina de concepto, una de código leído del repositorio y una de decisión que se cierra en la sala antes de seguir. V1, V2 y V3 son los puntos donde lo decidido se compila y se corre. Pedir la opinión de quienes están remotos antes de cerrar cada decisión.

Los fragmentos de código se leen del repositorio al generar el deck: si el código cambia, hay que regenerar. La propuesta de cada decisión está plegada y se abre después de escuchar al grupo; la decisión final se escribe en `decisiones/NN-titulo.md`, no en el deck. Las cifras del 28/09 son anteriores a las correcciones de esa fecha; las columnas de la prueba se completan con la corrida del día.

## Mapa y tiempos

| Sección | Horario | Diapositivas | Resultado |
|---|---|---|---|
| 01 · Punto de partida | 09:00–09:30 | 1–8 | Ver el error de hoy y acordar qué construimos |
| 02 · Diseñar el agente | 09:30–11:15 | 9–25 | Tomar las decisiones que definen la V1 |
| 03 · V1 · el agente responde | 11:15–12:30 | 26–28 | Construir, correr y leer la primera versión |
| 04 · V2 · herramientas | 13:15–14:45 | 29–34 | Decidir qué resuelve la tabla y conectarla |
| 05 · V3 · control | 15:00–16:15 | 35–41 | Decidir qué pasa cuando el agente no sabe |
| 06 · La prueba y el camino | 16:15–17:00 | 42–48 | Medir contra el criterio y repartir lo que sigue |

Pausa 11:00–11:15; almuerzo 12:30–13:15; pausa 14:45–15:00. El bloque V3 incluye preparación de comparación 16:00–16:15. Margen de preguntas 17:00–17:30 sujeto a confirmación logística.

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

**Temas para hablar:** Después de esta portada: la agenda por temas y, con un producto real, qué entra y qué queremos que salga. A las 17:00 queremos tres cosas: el agente corriendo en local con el código en el repositorio, un método que se pueda repetir para el próximo caso de uso y trece decisiones escritas con su razonamiento. Hoy no se enseña teoría: se diseña y se construye en el orden en que se diseña. Gastón conduce; el grupo decide en cada punto.

**Transición:** Lo que vamos a hacer hoy.

### 02 · Lo que vamos a hacer hoy.

**Sección:** 01 · Punto de partida · **Pauta:** 3 min · **Tipo:** compare

**Objetivo:** Ubicar al grupo en el recorrido del día, por temas

**En pantalla:**

- Decidimos → construimos → medimos. Cada bloque cierra con una versión que funciona.
- 1 · PUNTO DE PARTIDA | El error de hoy, alcance y contrato
- 2 · DISEÑAR EL AGENTE | Tipo de aplicación, prompt, dónde corre, modelo, stack y criterio de éxito
- 3 · V1 · EL AGENTE RESPONDE | Solo instrucciones: qué falla y por qué
- 4 · V2 · HERRAMIENTAS | Las tablas como herramientas, el loop y la caché de prompt
- 5 · V3 · CONTROL | Guardrails, memoria y caché por SKU
- 6 · LA PRUEBA | Hoy contra V1, V2 y V3, y el camino a producción

**Temas para hablar:** Seis bloques. Las decisiones de los dos primeros producen la V1; las de herramientas, la V2; las de control, la V3; y la prueba mide todo contra el criterio que acordamos antes de escribir código. Horarios para quien conduce: 09:00 punto de partida, 09:30 diseño, 11:15 V1, 13:15 V2, 15:00 V3, 16:15 prueba. Pausa a las 11:00, almuerzo 12:30 a 13:15, pausa 14:45. Cierre técnico 17:00 y preguntas hasta las 17:30.

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

**Temas para hablar:** Esto es lo que queremos lograr. Entra el producto como está en Alephee: los nombres de los atributos están en español porque así los define la plataforma; los valores y la categoría están en portugués porque el catálogo es de GM Brasil sobre la taxonomía de Mercado Libre Brasil. Sale la publicación para Shopee Brasil, que mezcla portugués e inglés según cómo expone cada atributo su API. Cruzar idiomas es parte del problema. Las tres primeras filas coinciden con lo que Alephee publicó hoy para este SKU (categoría 102278, Condition = New valueId 2497, 6 Months valueId 810); la cuarta es la conducta que queremos: hoy en Código OEM salió ABS Plastic y Shopee lo rechazó. La columna de la derecha anticipa el día: tabla, agente, guardrail. El esquema de atributos de Shopee con el que validamos es MOCK derivado de estas publicaciones.

**Pregunta / participación:** ¿Qué fila les parece la más difícil de automatizar?

**Transición:** Cómo lo hace hoy el proceso actual.

### 04 · Hoy: dos llamadas, un merge y un presupuesto que se agota.

**Sección:** 01 · Punto de partida · **Pauta:** 3 min · **Tipo:** cards

**Objetivo:** Entender el proceso actual sin juzgarlo

**En pantalla:**

- Categoría: la tabla reference_category y, si no alcanza, el modelo elige
- Atributos: dos llamadas en paralelo (con y sin referencia) y un merge por código
- USD 350 por mes: cuando se agota, se publica sin atributos

**Temas para hablar:** Describir el flujo actual tal como lo explicó Maximiliano: la categoría se resuelve por tabla y el modelo entra cuando la tabla no la tiene; los atributos van en dos llamadas en paralelo porque un solo prompt era demasiado largo, y un merge por código prioriza la que usó la referencia. Latencia de 13 segundos en batch: no es una restricción. El punto que duele es el presupuesto: cuando se agota, la publicación sale sin atributos. El modelo exacto y sus parámetros siguen sin confirmar.

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

**Temas para hablar:** Los 30 productos del zip: 20 publicados y 10 rechazados. El caso 88904447 es el hilo del día: un material (ABS Plastic) copiado al campo Código OEM, que Shopee rechazó porque el valor no está vinculado a ese atributo. El 24581199 publicó Quantity diez veces y Shopee no lo mencionó: lo rechazó por otro obligatorio (Auto-Part Number). Lo peor no es lo que Shopee rechaza, que al menos avisa, sino lo que acepta mal: un -1 publicado como valor en 9 de 30 y URN sin el sufijo del canal. Nadie se entera hasta que un comprador lo ve.

**Pregunta / participación:** ¿Cuál de estos errores les parece más grave para el negocio?

**Transición:** Cómo vamos a trabajar hoy.

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

**Transición:** Decisión 2: cómo se informa lo que no se pudo mapear.

### 08 · ¿Qué recibe y qué entrega?

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

### 09 · Diseñar antes de escribir.

**Sección:** 02 · Diseñar el agente · **Pauta:** 1 min · **Tipo:** divider

**Objetivo:** Abrir el bloque de diseño

**En pantalla:**

- Siete decisiones que definen la V1

**Temas para hablar:** En este bloque no se corre nada. Se toman las decisiones que la V1 va a implementar a las 11:15: qué tipo de aplicación, cómo se escribe el prompt, dónde corre, qué modelo, con qué stack y cómo se mide. Cada decisión tiene opciones con consecuencias y se cierra antes de pasar a la siguiente.

**Transición:** Primero, qué tipos de aplicación existen.

### 10 · Cuatro formas de usar un modelo.

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

**Transición:** Decisión 3.

### 11 · ¿Single prompt o agente?

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

### 12 · Un prompt tiene cinco partes.

**Sección:** 02 · Diseñar el agente · **Pauta:** 3 min · **Tipo:** flow

**Objetivo:** Dar un esqueleto para leer cualquier prompt

**En pantalla:**

- Rol: quién es
- Tarea: qué hace y con qué entrada
- Reglas: qué nunca hace
- Formato: cómo entrega
- Cuando falta dato: qué hace

**Temas para hablar:** Las cinco partes sirven para leer el prompt actual y el nuevo. La quinta es la que casi siempre falta: qué hacer cuando no hay dato. Si el prompt no lo dice, el modelo elige por su cuenta, y lo que elige es completar.

**Transición:** Tres prácticas que cambian el resultado.

### 13 · Buenas prácticas que cambian el resultado.

**Sección:** 02 · Diseñar el agente · **Pauta:** 3 min · **Tipo:** cards

**Objetivo:** Tres prácticas con efecto medible

**En pantalla:**

- Lo estático primero y lo variable al final: habilita la caché de prompt (F4, F7)
- Salida estructurada por esquema, no JSON pedido en el texto
- Decir qué hacer cuando no sabe, no solo qué hacer

**Temas para hablar:** La primera tiene efecto directo en costo: Bedrock cachea el prefijo estable del prompt con cachePoint (F4, mínimo 1.024 tokens para Claude Sonnet 5) y OpenAI hace lo mismo de forma automática sobre el prefijo (F7). El prompt actual pone el producto antes de la lista de categorías: el prefijo cambia en cada llamada y no se cachea nada. Reordenarlo ya bajaría el costo sin cambiar de proveedor; hay que medirlo, no darlo por hecho. Fuentes en docs/warroom/fuentes.md.

**Transición:** Decisión 4.

### 14 · ¿Cómo garantizamos el formato?

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

### 15 · Dónde corre: AgentCore o contenedor propio.

**Sección:** 02 · Diseñar el agente · **Pauta:** 3 min · **Tipo:** compare

**Objetivo:** Presentar AgentCore con sus beneficios y sus dudas, con fuente

**En pantalla:**

- Fuentes F1–F3b en docs/warroom/fuentes.md
- AGENTCORE RESUELVE | Runtime sin servidores, identidad, memoria, gateway de herramientas y observabilidad, como servicios separados que se usan juntos o no (F2)
- DUDAS | Arranque en frío sin cifra publicada, sesiones que terminan a los 15 min de inactividad y 8 h máximo (F3b), costo por CPU y memoria de la sesión (F3), región disponible
- ALTERNATIVA | Contenedor o Lambda propios: más control y más trabajo de operación; el agente es el mismo

**Temas para hablar:** AgentCore Runtime corre el contenedor del agente en una microVM por sesión y cobra por el CPU y la memoria que consume la sesión; el CPU baja a cero mientras espera al modelo (F3). Para un chat eso es ideal. Para un batch de miles de productos la pregunta es otra: ¿conviene una sesión larga en el Runtime o un proceso propio de Alephee que llame a Bedrock? No hay cifra pública de arranque en frío; se mide. Las dudas que no se resuelvan hoy van a Juan David.

**Pregunta / participación:** ¿El batch de Alephee tiene horario fijo o corre continuo?

**Transición:** La infraestructura completa, en un dibujo.

### 16 · La infraestructura, de punta a punta.

**Sección:** 02 · Diseñar el agente · **Pauta:** 2 min · **Tipo:** diagram

**Objetivo:** Mostrar todas las piezas de AWS y separar lo que hay de lo que falta

**En pantalla:**


**Temas para hablar:** Arriba, el camino del chat: el widget llama al BFF, que valida el token, aplica el guardrail de entrada y los topes, y encola. El worker invoca el Runtime, que llama a Bedrock y a las herramientas por el Gateway. Abajo a la derecha, punteado, el batch de catálogo: hoy corre en local contra Bedrock y su lugar en producción es la decisión 5. La franja de abajo es el monitoreo que trae el template: logs, trazas de punta a punta y un dashboard. Nada de esto está desplegado todavía para Alephee.

**Pregunta / participación:** ¿Qué piezas ya tiene Alephee y cuáles reemplazaríamos?

**Transición:** Decisión 5.

### 17 · ¿Dónde corre?

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

### 18 · Elegir el modelo: qué pesa en este caso.

**Sección:** 02 · Diseñar el agente · **Pauta:** 3 min · **Tipo:** cards

**Objetivo:** Criterios de elección antes de nombrar modelos

**En pantalla:**

- Seguir reglas y usar herramientas sin inventar: es lo que más falla hoy
- Costo por token con caché de prompt: el presupuesto actual es de USD 350 por mes
- Latencia: no es restricción (hoy el batch tarda 13 s por producto)
- Disponible en la región y habilitado en la cuenta

**Temas para hablar:** El orden importa: primero calidad en lo que falla hoy (alucinar valores, ignorar reglas), después costo con caché, y la latencia al final porque es batch. Un modelo más chico puede ganar en costo y perder en reglas: se decide midiendo sobre el dataset, no por intuición.

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

**Temas para hablar:** La tabla sale de la página oficial Models at a glance del 30/09 (F6). No es una recomendación de cada uno: es el menú. Lo que importa para elegir es la columna de la derecha y el criterio de la lámina anterior. La disponibilidad por región y la habilitación en la cuenta se verifican en la cuenta que usemos.

**Transición:** Decisión 6.

### 20 · ¿Qué modelo?

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

### 21 · Stack y harness.

**Sección:** 02 · Diseñar el agente · **Pauta:** 3 min · **Tipo:** cards

**Objetivo:** Separar el stack del agente de la herramienta con la que lo construimos

**En pantalla:**

- Python + LlamaIndex Workflows: pasos, eventos y herramientas ya resueltos
- BedrockConverse: tool calling y caché de prompt sin código propio
- Harness de desarrollo: propone cambios en el código; Gastón los revisa y corre los tests

**Temas para hablar:** Dos cosas distintas: el stack con el que corre el agente (Python, LlamaIndex, Bedrock) y el harness con el que lo construimos hoy, un entorno de desarrollo asistido por un modelo que propone cambios. El harness no es el agente ni decide nada: cada cambio que propone pasa por revisión y por los tests. No depende de un proveedor concreto.

**Pregunta / participación:** ¿Qué revisarían antes de aceptar un cambio propuesto por el harness?

**Devolución esperada:** Que resuelva la regla acordada, que pase los tests y que no toque datos reales.

**Transición:** Decisión 7.

### 22 · ¿Con qué lo construimos?

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

### 23 · ¿Cuándo está bien hecho?

**Sección:** 02 · Diseñar el agente · **Pauta:** 3 min · **Tipo:** cards

**Objetivo:** Acordar la métrica antes de escribir código

**En pantalla:**

- Esquema de Shopee y salida esperada MOCK · validar con el equipo de catálogo
- Exacto: categoría correcta, ni sobra ni falta atributo, nada fuera de dominio, sin duplicados y faltantes informados
- Además se reportan precisión y recall de atributos, valores inválidos, tokens y segundos
- Dataset: 30 productos reales con su publicación actual; el esquema de atributos de Shopee y el expected son simulados

**Temas para hablar:** La vara es estricta a propósito. Pero el expected es mock: se construyó a partir de la publicación actual limpia, así que hereda sus omisiones y castiga aciertos que hoy nadie mapea. Por eso los exactos van a ser bajos en todas las versiones y hay que leer también inválidos, duplicados y faltantes. El esquema oficial de Shopee y la validación con catálogo son pendientes.

**Transición:** Decisiones 8 y 9.

### 24 · ¿Cuál es el número que aceptamos?

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

### 25 · ¿Con qué dataset?

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

### 26 · V1 · el agente responde.

**Sección:** 03 · V1 · el agente responde · **Pauta:** 1 min · **Tipo:** divider

**Objetivo:** Abrir la V1 con la expectativa correcta

**En pantalla:**

- Solo instrucciones. Se espera que falle, y esos fallos justifican lo que sigue.

**Temas para hablar:** La V1 implementa las decisiones 1 a 9: single prompt, salida por herramienta con esquema, Claude Sonnet 5 por Converse, LlamaIndex Workflows, medida con el evaluador sobre los 30 reales. No usa las tablas de referencia a propósito: queremos ver qué resuelve el modelo solo. Recordar la regla del día: no se pasa al bloque siguiente con algo roto, pero un resultado de negocio incorrecto no es algo roto, es evidencia.

**Transición:** Lo corremos sobre el caso guía.

### 27 · Demo · un caso real por V1.

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

### 28 · Qué falló en V1 y qué capa lo resuelve.

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

### 29 · V2 · herramientas.

**Sección:** 04 · V2 · herramientas · **Pauta:** 1 min · **Tipo:** divider

**Objetivo:** Retomar después del almuerzo y abrir la V2

**En pantalla:**

- El agente consulta antes de decidir.

**Temas para hablar:** Recapitular en una frase: la V1 responde sola y falla donde necesita datos que no tiene. La V2 le da herramientas para consultar las tablas de referencia y el esquema del canal. El prompt deja de llevar el canal entero: el agente pide solo lo que necesita para este producto.

**Transición:** Qué es una herramienta.

### 30 · Una herramienta es una función que el modelo pide y el código ejecuta.

**Sección:** 04 · V2 · herramientas · **Pauta:** 3 min · **Tipo:** flow

**Objetivo:** Definir herramienta sin jerga

**En pantalla:**

- El modelo pide buscar_categoria('urn:category:1106872')
- El programa ejecuta la función: consulta la tabla
- Devuelve {encontrada: true, urn, name} o {encontrada: false, motivo}
- El modelo sigue con ese dato, no con su memoria

**Temas para hablar:** El modelo no ejecuta nada: redacta un pedido con nombre y argumentos, el programa lo ejecuta y le devuelve el resultado como un mensaje más. Por eso la herramienta es determinista y el modelo no. Hay herramientas de lectura (consultar) y de acción (publicar); hoy todas las nuestras son de lectura. Que la herramienta exista no obliga al modelo a usarla ni a respetarla: la V3 revisa la entrega contra el esquema del canal, pero imponer por código lo que dice la tabla de atributos es un pendiente.

**Transición:** Decisión 10: qué decide la tabla y qué decide el agente.

### 31 · ¿Qué decide la tabla y qué decide el agente?

**Sección:** 04 · V2 · herramientas · **Pauta:** 4 min · **Tipo:** decision

**Objetivo:** Cerrar la decisión 10

**En pantalla:**

- En la base preparada: la categoría se fija en código (V3); los campos de la tabla los aplica el modelo por instrucción

**Temas para hablar:** B es el error más común: dejar que el modelo mejore un mapeo que el equipo de catálogo mantiene a mano. Si la tabla está mal, se corrige la tabla. C ya se descartó en la decisión 3. Ser exacto sobre el estado: la V3 fija la categoría en código; los campos mapeados por tabla todavía dependen de que el modelo respete la herramienta, y el guardrail solo revisa el esquema. Si la sala quiere imponerlos por código, es un cambio acotado en _al_entregar y queda como pendiente.

**Transición:** Los números de la corrida del 28/09.

**Decisión 10:** ¿Qué decide la tabla y qué decide el agente?

1. A · La tabla fija la categoría y los campos; el agente solo elige el valor equivalente de la lista y cubre lo que la tabla no tiene
2. B · El agente puede corregir la tabla si cree que está mal
3. C · Todo por tabla; sin modelo

**Propuesta:** A. La tabla manda (acuerdo del 25/08 con Juan David). Hoy la categoría se impone en código (V3) y la tabla de atributos la consulta el agente por herramienta, desambiguada por categoría en código; imponer también los campos por código es el siguiente paso. Lo que la tabla no cubre (valores de lista, atributos sin referencia) es lo único que decide el agente.

**Archivo:** `decisiones/10-tabla-vs-agente.md`

### 32 · Costo por producto, medido.

**Sección:** 04 · V2 · herramientas · **Pauta:** 3 min · **Tipo:** table

**Objetivo:** Mostrar el efecto de herramientas + caché en tokens y latencia

**En pantalla:**

- Corrida del 28/09 · 30 reales · anterior a las correcciones · tokens de entrada por producto
- Versión / Entrada sin caché / Leída de caché / Segundos
- V1 / ~22.000 / — / 12,3
- V2 / ~1.600 / ~12.000 / 18,3

**Temas para hablar:** La V2 paga 1.600 tokens nuevos por producto y lee 12.000 de caché; la V1 pagaba 22.000 nuevos. La latencia sube porque hay varias rondas: es batch, no importa. Lo que falta para hablar de dólares: sumar escritura de caché, salida y reintentos, y la tasa real de reutilización. No inferir ahorro solo de esta tabla.

**Transición:** Decisión 11: el costo.

### 33 · ¿Cuánto puede costar?

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

### 34 · Demo · el mismo caso por V2.

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

### 35 · V3 · control.

**Sección:** 05 · V3 · control · **Pauta:** 1 min · **Tipo:** divider

**Objetivo:** Abrir la V3

**En pantalla:**

- Qué pasa cuando el agente no sabe.

**Temas para hablar:** La V2 consulta pero no está obligada a respetar lo que consulta. La V3 agrega tres cosas: guardrails en código que revisan cada entrega, memoria de correcciones del equipo de catálogo y caché por SKU para que el mismo producto no se mapee dos veces. Es la versión que reemplaza el publicar sin atributos.

**Transición:** El agente completo, en un dibujo.

### 36 · El agente por dentro: código y modelo.

**Sección:** 05 · V3 · control · **Pauta:** 3 min · **Tipo:** diagram

**Objetivo:** Ver las tres versiones como capas de un mismo flujo

**En pantalla:**


**Temas para hablar:** Verde es código determinista; violeta, el modelo. La categoría sale de la tabla antes de llamar al modelo; si no hay referencia, el flujo termina con un faltante explícito. Si el SKU ya se mapeó, sale de la caché. El modelo pide herramientas en un loop acotado y entrega; el guardrail revisa y, si hay problemas, devuelve la lista para una sola ronda de corrección. La red final limpia lo que siga mal. V1 era solo la caja violeta; V2 sumó las herramientas.

**Pregunta / participación:** ¿Qué caja sacarían a código si pudieran?

**Transición:** Qué es un guardrail acá.

### 37 · Guardrail: una comprobación en código, no otra instrucción.

**Sección:** 05 · V3 · control · **Pauta:** 3 min · **Tipo:** compare

**Objetivo:** Diferenciar guardrail de regla del prompt

**En pantalla:**

- REVISAR | Lista los problemas en lenguaje claro y se los devuelve al agente, que tiene una ronda para corregir
- LIMPIAR | Red final: descarta lo inválido con motivo y marca los obligatorios que faltan
- NUNCA | Publica un valor fuera de la lista del canal, un -1 ni un duplicado. No verifica que el valor sea verdad: eso sigue siendo del esquema y de catálogo

**Temas para hablar:** Una regla en el prompt es un pedido; un guardrail es una comprobación que no depende de que el modelo obedezca. Dos pasos: primero se le devuelven los problemas al agente para que corrija (una ronda); lo que siga mal se descarta en código. Límite honesto: valida pertenencia al esquema y al dominio por ID; no verifica que el valor sea verdad respecto del producto.

**Transición:** Decisión 12.

### 38 · ¿Qué hace cuando no sabe?

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

### 39 · Memoria: correcciones del equipo de catálogo.

**Sección:** 05 · V3 · control · **Pauta:** 3 min · **Tipo:** cards

**Objetivo:** Definir memoria para este agente sin prometer aprendizaje automático

**En pantalla:**

- Una corrección dice: en esta categoría, este valor del producto va a este atributo con este valor del canal
- El agente la consulta como una herramienta más y manda sobre su criterio
- Hoy es un archivo JSON local; en producción, AgentCore Memory o una tabla de Alephee

**Temas para hablar:** Memoria acá no es que el agente aprende solo: es que reutiliza correcciones que una persona del equipo de catálogo cargó explícitamente. Se cargan con un comando; el agente las consulta por categoría. Límite honesto: la persistencia existe; que el modelo siempre las respete depende de que las consulte, por eso la instrucción lo exige y el guardrail revisa después.

**Transición:** Decisión 13.

### 40 · ¿Cómo garantizamos determinismo?

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

### 41 · Demo · corregir y repetir.

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

### 42 · La prueba.

**Sección:** 06 · La prueba y el camino · **Pauta:** 1 min · **Tipo:** divider

**Objetivo:** Abrir la prueba con el criterio acordado a la vista

**En pantalla:**

- Hoy contra V1, V2 y V3, sobre los 30, con el criterio de la decisión 8.

**Temas para hablar:** Volver a la pizarra: el número de la decisión 8. Las corridas del lote se lanzaron durante los bloques; acá se leen. Si alguna no terminó, se usa la del 28/09 y se dice.

**Transición:** Los resultados.

### 43 · Resultados (se completan en vivo).

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

### 44 · Cómo leer la tabla.

**Sección:** 06 · La prueba y el camino · **Pauta:** 3 min · **Tipo:** cards

**Objetivo:** Dar la lectura honesta de los resultados

**En pantalla:**

- Exactos bajos en todas las columnas: el expected hereda las omisiones del proceso actual y castiga aciertos que hoy nadie mapea
- Inválidos y duplicados sí son errores seguros: la V3 no entrega ninguno detectable por este evaluador (28/09)
- Categoría: la V3 dio 28/30 en la corrida vieja; la corrección del 28/09 la fija desde la tabla y hay que volver a medir

**Temas para hablar:** Conclusión defendible: en este ensayo la V3 elimina los errores que estos controles detectan, pero todavía no demuestra mejor exactitud global contra un expected que es mock. Tenemos evidencia de qué controles ayudan y una lista clara de lo que falta para validar con el canal. Un control puede reducir errores quitando información: mirar control y cobertura juntos.

**Pregunta / participación:** ¿Qué evidencia pedirían antes de un piloto con un concesionario?

**Transición:** El camino a producción.

### 45 · Camino a producción.

**Sección:** 06 · La prueba y el camino · **Pauta:** 3 min · **Tipo:** flow

**Objetivo:** Convertir los pendientes en tareas con dueño

**En pantalla:**

- Esquema oficial de Shopee y expected validado con el equipo de catálogo
- Integración: la API pública lee el producto (F8); escribir publicaciones y leer tablas necesita acceso interno
- Decidir dónde corre el batch (decisión 5) y la política de missing (decisión 12)
- Medir el costo completo y fijar el tope (decisión 11); probar Haiku 4.5 (decisión 6)

**Temas para hablar:** Cada punto necesita responsable y fecha; se completan en la última lámina. Retomar las dudas de AgentCore anotadas a la mañana y asignarlas a Juan David. El código queda en el repositorio de Alephee que Rick indique.

**Transición:** Las trece decisiones.

### 46 · Las 13 decisiones (1 a 7).

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

**Temas para hablar:** Este registro es el método repetible: el próximo caso de uso de Alephee arranca por estas trece preguntas, con las respuestas de hoy como punto de partida.

**Transición:** Quién hace qué.

### 48 · Quién hace qué, para cuándo.

**Sección:** 06 · La prueba y el camino · **Pauta:** 1 min · **Tipo:** divider

**Objetivo:** Cerrar con responsables y fechas

**En pantalla:**

- Se completa en la sala.

**Temas para hablar:** Repartir los pendientes del camino a producción entre Alephee, Craftech y AWS, con fecha. Confirmar el repositorio donde queda el código. Agradecer y cerrar a las 17:00; preguntas hasta las 17:30.

**Transición:** Fin.

## Fundamento editorial y revisión

Diseño de esta versión: [diseno-presentacion.md](warroom/diseno-presentacion.md). Revisión editorial de la versión anterior: [revision-agentes.md](warroom/revision-agentes.md).
