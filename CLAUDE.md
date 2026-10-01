# War Room Alephee × Craftech × AWS

> Contexto de trabajo para construir, en un día, el agente que mapea categorías y atributos de un producto del catálogo de Alephee a una publicación de canal (Shopee).
> Última actualización: 2026-10-01 (Gastón Zarate).

**Reinicio del 1/10.** El código anterior está en `old/` (fuera de git) y en la rama `backup/pre-reinicio`. Se reconstruye versión por versión; spec y plan de la V1 en `docs/superpowers/`.

## Datos del evento

**Dinámica (actualizada el 30/09):** Gastón conduce una cadena de 13 decisiones de diseño; cada tema tiene lámina de concepto, lámina de código leído del repo y lámina de decisión que se cierra en la sala antes de seguir. V1, V2 y V3 son los puntos donde lo decidido se compila y se corre. Sin quizzes ni consignas en parejas (se quitaron el 30/09); quedan tres demos conducidas y la prueba final. Guion en `docs/guion-warroom-propuesto.md`.

| |
|---|---|
| **Fecha** | **Jueves 1 de octubre de 2026, 09:00–17:30** (confirmado en el calendario, en el sync del 16/09 y en el mail de Alephee del 24/09) |
| **Lugar** | Oficinas de AWS (Buenos Aires), presencial, con sala con pizarra. Stream por Meet/Teams para quienes estén en Brasil |
| **Formato** | Se construye en vivo. No es una capacitación. Cada bloque cierra con una versión que funciona y no se pasa a la capa siguiente con algo roto |
| **Resultado esperado a las 17:00** | Agente funcionando en local con el código en el repo de Alephee, un método repetible y 5+ decisiones documentadas |
| **Jira** | PREV-83 "Workshop Alephee - AI" (Pre-sales), asignado a Gastón |

⚠️ El temario de Google Docs dice "Miércoles 14 de octubre", pero la fecha vigente es el **1/10**. Hay que corregir el encabezado del doc antes de volver a compartirlo.

## Personas

**Alephee** (cliente)
- Ricardo "Rick" Flores (rflores@alephee.com): sponsor y contacto principal. Recibe el temario y valida.
- Maximiliano Olivari (molivari@alephee.com): dueño técnico del flujo actual de IA (prompts, merge de las dos llamadas).
- Hanss Becerra (hbecerra@alephee.com): dev.
- Otros asistentes registrados: Agustin Wenner, Victoria Huxley, Jonas Gho, Federico Miguez, David Dellacha y, probablemente, Jonathan Saiegh.
- Angel Bejarano estuvo en la reunión del 25/08. Falta confirmar si es de Alephee.

**Craftech**
- Jesus Liernur: Account Manager, lidera la iniciativa, logística y viajes.
- Gastón Zarate: experto en IA, diseña la metodología y conduce la parte técnica.
- Luciano Serra: experto en IA.

**AWS**
- Maria Alejandra "Mariale" Cotes (mcotes@amazon.com): Account Manager Startups. Sala y coordinación de accesos para la jornada.
- Juan David Novoa (jdnovoa@amazon.com): SA de AWS. Propuso el flujo mixto determinista + agéntico y el whiteboarding de criterios de éxito.

## Qué es Alephee
Es una plataforma B2B para el **aftermarket automotriz**: repuestos, neumáticos y piezas de motos, camiones y vehículos pesados. Conecta marcas y fabricantes, distribuidores mayoristas y minoristas, y publica sus catálogos certificados en marketplaces (Mercado Libre, Amazon, Shopee). Opera en 8 países de Latinoamérica: Brasil, México, Argentina, Chile, Colombia, Perú, Ecuador y Uruguay ([alephee.com](https://www.alephee.com/)). En la transcripción, el sistema legacy aparece como "la B2". Casi seguro es **"la V2"**: la API pública es v2, vive en `api.alephcrm.com` (la marca anterior sería AlephCRM) y las imágenes del ejemplo están en `alephv2imgstorage`. Es una inferencia y hay que confirmarla con Alephee. En este documento se usa "legacy (V2)".

Para Craftech ya es cliente (ver "Contexto comercial"). En este caso, su cliente más grande es **GM – Chevrolet Brasil**: la marca provee el catálogo y unos 40 concesionarios lo venden en modo solo lectura.

## API pública de Alephee (v2)
Documentación en [developers.alephee.com/v2](https://developers.alephee.com/v2), con el índice completo en [llms.txt](https://developers.alephee.com/v2/llms.txt) y el Swagger en [api.alephcrm.com/swagger](https://api.alephcrm.com/swagger/ui/index).

- **Autenticación:** `API_KEY` y `accountId` como **parámetros de la URL**, no como headers ([docs](https://developers.alephee.com/v2/introduction/using-the-api/authentication)). Cuidado: la key queda en los logs de URLs. Nunca loguear la URL completa. La key se pide a soporte de Alephee.
- **Límite de uso:** por `API_KEY`, en ventanas de 1 minuto, con respuesta 429 al excederlo; cada endpoint tiene su propio límite ([docs](https://developers.alephee.com/v2/usage-limiting/rate-limiting)).
- **Endpoints relevantes** ([índice de métodos](https://developers.alephee.com/v2/introduction/overall-index-of-methods)):
  - `GET /v2/products?SKU=...`: trae el producto. Los **atributos** (`Name`, `Value`, `ValueName`, `MeasurementUnit`), la `MELICategory` y la descripción vienen solo en la "sección PIM", que requiere licencia PIM ([docs](https://developers.alephee.com/v2/products/get-methods/page-1/response)). **Sirve como herramienta de lectura para el agente.**
  - `GET /v2/productlistings/search`: publicaciones existentes, filtrables por SKU y marketplace.
  - `PUT /v2/productlistings`: según las reglas de negocio documentadas, actualiza **precio, margen y valor fijo** de publicaciones activas, no atributos ni categorías ([docs](https://developers.alephee.com/v2/product-listings/put-methods/update-product-listings/business-rules)).
- **Lo que la API pública NO tiene:** endpoints de categorías, de atributos por canal, de las tablas `reference_*` ni para crear publicaciones con atributos.
- **Conclusión:** la API pública alcanza para **leer el producto**, pero no para escribir la publicación ni para leer las tablas. Además, el formato de la API (PascalCase, IDs numéricos) **no es el mismo** que el de los ejemplos del mail (Mongo, URNs, camelCase): el flujo de publicaciones vive en la plataforma nueva, que es interna. Para la integración real hace falta acceso interno. Hay que pedírselo a Maximiliano.

## El problema

Alephee migra catálogos desde su producto legacy (**V2**, que usa la taxonomía de categorías y atributos de **Mercado Libre**) y genera una **publicación** para cada canal conectado: Shopee, Magalu, Tienda Nube, etc. La publicación es el producto adaptado al canal, y lo que más importa adaptar es **la categoría y los atributos**.

**Caso del war room:** un producto real del catálogo de **GM – Chevrolet Brasil** publicado en **Shopee**. Un canal y una familia de productos.

### Cómo funciona hoy
1. **Categoría:** se resuelve primero con la tabla `reference_category` (legacy → canal). Si no alcanza, el LLM elige a partir del nombre de la categoría del CRM y el nombre del producto. Según `index.ts` no usa la descripción, aunque en la reunión se dijo que sí. No se usan imágenes.
2. **Atributos:** el LLM recibe los atributos del producto, los atributos que espera la categoría del canal y las reglas del canal por tipo de campo (texto libre, dropdown, combo box).
3. Se hacen **dos llamadas en paralelo**, una con los atributos de referencia (`reference_attribute`) y otra sin ellos. Después un **merge por código** prioriza la lista que usó la referencia. El prompt único era demasiado largo y el modelo no lo resolvía.
4. **Modelo:** OpenAI, con llamadas directas a la API y sin framework. En la transcripción aparece como "4o mini", "O4 mini" y "GPT-4.1". `index.ts` solo tiene los prompts, no el modelo ni los parámetros (seed, temperatura), así que **sigue sin confirmar**: hay que preguntárselo a Maximiliano.
5. **Latencia:** es un proceso batch que no bloquea. Tarda 13 s en promedio y 20 s en el peor caso. La latencia no es una restricción.

### Dolores conocidos
- **Alucinación de atributos:** el modelo inventa valores con tal de responder.
- **No determinismo:** el mismo producto (mismo SKU de GM, vendido por unos 40 concesionarios) devuelve atributos distintos en cada corrida. Se agregó un seed.
- **Costo:** el presupuesto de OpenAI es de unos USD 350/mes, con recargas de USD 50 hasta un tope. **Cuando se agota, se publica sin atributos.**
- **No hay caché:** el mismo SKU se reprocesa para cada seller aunque el catálogo lo provee la marca en modo solo lectura.
- **Salida duplicada:** en el ejemplo, `Type of shell` sale dos veces con el mismo URN. Lo más probable es que el merge de las dos llamadas no deduplique por URN (hipótesis: el merge no está en `index.ts`). Ver `inputs/ejemplos/`.
- **37 atributos de entrada, 7 de salida:** no es necesariamente un error. Las medidas del paquete van a `dimensions` y la categoría Calotas de Shopee probablemente pide pocos atributos. Para saberlo hace falta la lista de atributos de esa categoría en Shopee.
- Si un atributo es obligatorio en el canal y no existe en el origen, alguien tiene que cargarlo a mano. El agente no puede inventarlo.

### Tablas de referencia (las mantiene el equipo de catálogo de Alephee)
- `reference_attribute`: ID de atributo legacy (V2/ML) → ID de atributo del canal. Mapea **campos, no valores**. La exportación real tiene **2.567 filas para Shopee sobre 930 ids legacy, y 306 ids legacy apuntan a más de un atributo de Shopee** (el atributo de destino depende de la categoría). En la reunión se habló de 735.
- `reference_category`: categoría legacy → categoría del canal. La exportación real tiene **2.866 filas, una por id legacy**. El `legacyId` es el número pelado (`"1106872"`); en el producto la categoría viene como `urn:category:<número>`.
- Hay una tabla de cada tipo por canal. El equipo de catálogo no participa del flujo en tiempo real: actualiza las tablas cada tanto.

### Prompts actuales (`inputs/prompts-actuales/index.ts`)
El archivo tiene 5 prompts en TypeScript. Los tres primeros son el alcance del war room:

| Prompt | Qué hace | Observación |
|---|---|---|
| `categoryPrompt` | Elige una categoría del canal: primero por coincidencia exacta de nombre y, si no hay, por similitud semántica | Solo usa el **nombre de la categoría del CRM y el nombre del producto**, no la descripción (en la reunión se dijo otra cosa). Manda la lista completa de categorías en el prompt. `product.categories?.[0].name` rompe si `categories` viene vacío |
| `attributeReferencePrompt` | Llamada "con referencia": cruza `legacyId` de la tabla con el URN del producto, copia el URN y el tipo, y elige el valor | **Casi todo es lógica determinista pedida al LLM:** join por ID, copiar URN, buscar tipo. Lo único que necesita modelo es elegir el valor de lista más cercano (por ejemplo, `"1"` → `Sim`) |
| `attributePrompt` | Llamada "sin referencia": mapeo semántico libre de atributos del CRM a atributos del canal, con reglas de tipos de Shopee | Contradice al anterior en unidades: este dice "usar la unidad más cercana" y el de referencia dice "NEVER transform units" |
| `brandPrompt` | Elige la marca del canal | Fuera de alcance |
| `productInfoPrompt` | Genera título y descripción de marketing | Fuera de alcance. Es generación libre, no mapeo |

**Implicancias para el diseño (para llevar a la decisión 3):**
- `attributeReferencePrompt` se puede pasar **casi entero a código**. El agente solo intervendría para normalizar valores de lista y para los atributos que no están en la tabla. Eso elimina la doble llamada y el merge.
- Los prompts ponen primero la parte variable (el producto) y después listas grandes (categorías, atributos). OpenAI aplica caché de prompts automáticamente sobre el **prefijo** idéntico de prompts de 1024 tokens o más ([docs de OpenAI](https://platform.openai.com/docs/guides/prompt-caching)). Reordenando el prompt para dejar primero lo estático, ya se reduciría el costo sin cambiar de proveedor. Esto hay que medirlo, no darlo por hecho.
- Las salidas son JSON pedido "por favor" en el texto. Con salida estructurada (JSON schema o tool calling) se evitan los errores de formato.
- El formato de valores del prompt (`id`/`name`) no coincide con el de la publicación guardada (`urn`/`name`/`unit`). La conversión se hace en un código que no tenemos.

## Decisiones ya tomadas (antes del war room)
1. Este proyecto es la **base arquitectónica**: el stack y la arquitectura agéntica se van a replicar en otros casos de uso de Alephee (25/08).
2. **Flujo mixto:** lo que ya resuelven las tablas se hace con una capa determinista y **no pasa por el modelo**. El agente invoca esa capa como herramienta pero no razona sobre ella (25/08, a propuesta de Juan David).
3. **Harness de desarrollo genérico** para conducir la construcción, sin proveedor obligatorio (actualizado por Gastón, 29/09). Verificar capacidades, accesos y presupuesto del entorno elegido; no asumir créditos ni licencias de un proveedor concreto.
4. La solución se llama "agente" o "solución", no "bot", porque puede terminar siendo un flujo agéntico con más de un agente (16/09).
5. La definición de la solución incluye whiteboarding de arquitectura, criterios de éxito y el dataset de prueba (16/09).
6. **El agente corre sobre Amazon Bedrock con Claude Sonnet 5** (Gastón, 25/09).
7. **Este directorio es el repo del agente** (Gastón, 25/09). Es un **clon del template `craftech-io/chatbot-demo`** con slug `alephee-catalogo` (Gastón, 28/09).
8. **Mientras no lleguen los datos reales, se trabaja con mocks** en `data/mock/` (Gastón, 25/09).
9. **Stack: Python + LlamaIndex Workflows + `BedrockConverse`**, el mismo del core del template (Gastón, 28/09).
10. **Interfaz: chat y batch.** En la sala se muestra el chat del template (widget + BFF + AgentCore) y el mismo workflow corre en batch sobre el dataset, que es como lo usaría Alephee en producción (Gastón, 28/09).
11. **Clon:** remoto en GitHub `craftech-io`, auth del chat por **HMAC** para la demo, trazas **solo en CloudWatch** (Gastón, 28/09).

## Decisiones a tomar en la sala (13, repartidas en la jornada)
Cada decisión se presenta con opciones y consecuencias, y se cierra antes de pasar a la siguiente. Se documentan en `decisiones/NN-titulo.md` (contexto, opciones, propuesta, decisión, razonamiento, responsable); los 13 archivos ya existen con la decisión en blanco.

| N | Decisión | Bloque | Archivo |
|---|---|---|---|
| 1 | ¿Qué hace y qué no hace? (un canal, una familia) | 09:00 | `decisiones/01-alcance.md` |
| 2 | ¿Qué recibe y qué entrega? (`missing` y `rejected` con motivo) | 09:00 | `decisiones/02-contrato.md` |
| 3 | ¿Single prompt, workflow, agente o multiagente? | 09:30 | `decisiones/03-tipo-de-aplicacion.md` |
| 4 | ¿Cómo se garantiza el formato? (tool + Pydantic) | 09:30 | `decisiones/04-salida-estructurada.md` |
| 5 | ¿Dónde corre? (local hoy; chat en AgentCore; batch a medir) | 09:30 | `decisiones/05-donde-corre.md` |
| 6 | ¿Qué modelo? (Sonnet 5; Haiku 4.5 a probar) | 09:30 | `decisiones/06-modelo.md` |
| 7 | ¿Con qué stack? | 09:30 | `decisiones/07-stack.md` |
| 8 | ¿Cuándo está bien hecho? (número acordado antes de la V1) | 09:30 | `decisiones/08-criterio-de-exito.md` |
| 9 | ¿Con qué dataset? | 09:30 | `decisiones/09-dataset.md` |
| 10 | ¿Qué decide la tabla y qué decide el agente? | V2 | `decisiones/10-tabla-vs-agente.md` |
| 11 | ¿Cuánto puede costar? | V2 | `decisiones/11-costo.md` |
| 12 | ¿Qué hace cuando no sabe? (reemplaza "publicar sin atributos") | V3 | `decisiones/12-cuando-no-sabe.md` |
| 13 | ¿Cómo garantizamos determinismo? (caché por SKU + canal) | V3 | `decisiones/13-determinismo-y-cache.md` |

Temas abiertos que no se deciden hoy: gobernanza, seguridad, política de revisión de `missing` e integración con Alephee (API pública para leer, acceso interno para escribir).

## Agenda
| Hora | Bloque |
|---|---|
| 09:00 | Arranque: qué tenemos a las 17:00 y repaso del caso (producto GM en Shopee) |
| 09:30 | Definimos la solución (las 7 decisiones de arriba) con whiteboarding |
| 10:30 | Cómo está hecho un agente por dentro, 30 min: instrucciones, herramientas, memoria y control |
| 11:15 | **V1 · el agente responde:** solo instrucciones. Se espera que falle, y esos fallos justifican las capas siguientes |
| 13:15 | **V2 · el agente se integra:** herramientas (lookup en las tablas de referencia, catálogo de atributos del canal) |
| 15:00 | **V3 · el agente bajo control:** guardrails y memoria |
| 16:15 | **La prueba:** agente nuevo contra el proceso actual sobre el mismo dataset y con el criterio de la mañana. Cierre: camino a producción, quién hace qué y para cuándo |

## Estructura de este directorio
Es el clon del template `chatbot-demo` (ver su `README.md` y `docs/`), más lo propio del war room. Lo nuevo se construye tarea por tarea (ver `docs/superpowers/plans/2026-10-01-v1-catalog-agent.md`):

```
CLAUDE.md                      este archivo
client.config.ts               config por cliente: slug alephee-catalogo, modelo, región, prompt, topes
core/                          el agente (Python / LlamaIndex Workflows), contrato BYOC /ping y /invocations
  src/agent/                   el chat del template: ChatWorkflow, adaptador BedrockConverse, tools, costo
  src/catalog/                 LO NUESTRO: el agente de catálogo, todo en inglés (decisión de Gastón, 1/10)
    models.py                  contrato de salida (Pydantic `Listing`, `MappedAttribute`, `MissingAttribute`, `RejectedAttribute`)
    events.py                  MappingRequested / ContextReady / MappingCompleted
    llm.py                     crea el BedrockConverse (único módulo que sabe de Bedrock)
    data.py                    carga el dataset y los esquemas de Shopee desde DATA_DIR (data/real o data/mock)
    prompts.py                 lee el prompt de sistema de Langfuse, con fallback a la semilla del repo
    v1.py                      V1: Workflow de dos steps (prepare, map), salida estructurada sin herramientas
    tracing.py                 instrumentación de Langfuse / OpenInference
    evaluation.py              evaluadores por ítem y por corrida (exacto, precisión, recall, inválidos, duplicados)
    experiment.py               CLI: sube los datasets a Langfuse y corre run_experiment (v1 o current)
    chat_tool.py                FunctionTool map_product(sku) para el chat
    prompts/catalog-v1-system.txt   semilla del prompt de sistema
  tests/                       tests del template + test_catalog_*.py (con dobles, sin AWS ni Langfuse)
packages/                      bff, worker, widget, shared (TypeScript)
apps/web, apps/api             app web de demo (modo mock sin AWS) y stand-in de la API del cliente
infra/sst/                     IaC (SST): Runtime, Gateway, Guardrail, Memory, tablas, colas
data/mock/                     datos MOCK (10 casos con salida esperada inventada), copiados de old/ sin cambios
data/real/                     datos REALES de WarRoom.zip (2 tablas + 30 productos con la publicación actual), copiados de old/ sin cambios
docs/                          deck, guion y notas técnicas del war room; docs/superpowers/ con spec y plan de la V1
old/                           código anterior al reinicio del 1/10, fuera de git (ver cabecera de este archivo)
```

## Stack y cómo correr
- **Python 3.13 + uv**, **LlamaIndex Workflows** y **`BedrockConverse`**. Front, BFF e IaC en TypeScript con **SST**.
- **Comandos:**
  ```bash
  uv sync
  uv run pytest core/tests
  npm test
  scripts/experiment.sh --version v1 --data mock
  scripts/experiment.sh --version v2 --data mock
  scripts/experiment.sh --version v2 --data mock --fresh   # stores en memoria, no lee la caché de DynamoDB
  scripts/map.sh 94701411 --version v2   # imprime el JSON de la publicación (urn, valueId) de un SKU, sin DynamoDB ni Langfuse
  scripts/correct.sh --category <urn> --attribute <urn> --product-value <valor> --value-id <id> --value <nombre>
  scripts/e2e.sh    # contra Bedrock, DynamoDB y el chat desplegado (RUN_E2E=1; API_URL del BFF como env var)
  ```
- **`scripts/correct.sh` solo afecta lo que decide el agente** (`worklist.to_decide`): un valor
  que el código ya resolvió por coincidencia exacta con el dominio del canal (`resolved`) le
  gana al agente en el merge y una corrección sobre ese atributo no tiene efecto visible. En
  el dataset mock, caso `01-real-calota-aro14`, los atributos `101731` (valor `"1"`), `990001`
  (`"14"`) y `100095` (`"0.39"`) los decide el agente; en el caso `03-valor-en-otro-idioma`,
  `101638` (`"Nuevo"`) también. Una corrección sobre cualquiera de estos cuatro muestra su
  efecto; sobre un atributo ya resuelto, no.

## Resultados del 1/10 en Langfuse (30 reales, salida esperada MOCK)

Corridas del 1/10 con `scripts/experiment.sh --data real --allow-real-upload` sobre el dataset `alephee-shopee-real` (30 productos de GM en Shopee). La V2 corrió una sola vez (sin entradas en caché de DynamoDB todavía); una segunda corrida leería varios casos de `source=cache` y no sería comparable con esta tabla sin aclararlo (para remedir sin ese efecto, usar `--fresh`, que corre la V2 con stores en memoria).

| Métrica | Proceso de hoy | V1 | V2 |
|---|---|---|---|
| Casos exactos | 7 | 3 | 5 |
| Categoría correcta | 28 | 28 | 27 |
| Valores inválidos | 47 | 3 | 0 |
| Duplicados | 5 | 0 | 0 |
| Obligatorios sin informar | 2 | 1 | 1 |
| Precisión | 0,70 | 0,70 | 0,69 |
| Recall | 0,97 | 0,57 | 0,60 |
| Tokens de entrada por producto (sin caché / leídos de caché) | — | ~4.560 (+14.780 de caché) | ~9.970 (0 de caché) |
| Segundos por producto | ~0,6* | ~3,3 | ~12,4 |

*El tiempo de "Proceso de hoy" no es la latencia real de Alephee (13 s en promedio, informados en la reunión del 25/08): el runner `current` solo relee la publicación `actual` ya guardada en el dataset, sin llamar a ningún modelo.

**Lectura de la tabla, no solo los números:**
- **La categoría correcta de la V1 es optimista.** La V1 no tiene tabla de referencia ni herramientas: cuando acierta la categoría puede estar acertándola por nombre mientras alucina atributos o pasa por alto obligatorios que el caso no esperaba (mismo patrón que el caso 09 del dataset mock). No leer "28/30" como "la V1 entiende la categoría tan bien como hoy".
- **El `expected` sigue siendo MOCK:** hereda las omisiones del proceso actual (un atributo que hoy no se mapea tampoco está en `expected`), por lo que el recall de "Proceso de hoy" sale inflado y un atributo extra bien mapeado por V1 o V2 cuenta como error de precisión. Los "exactos" bajos en las tres columnas reflejan esta vara, no necesariamente peor desempeño.
- **V2 no muestra tokens leídos de caché en esta corrida (0 de 30 productos) porque no pone ningún `CachePoint`.** La V1 sí marca uno en `build_messages` (`core/src/catalog/v1.py`), y Bedrock Converse solo cachea lo que queda antes de un punto de caché explícito ([docs de Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html)); además el prefijo fijo de la V2 (system prompt más los esquemas de las dos herramientas, `lookup_corrections` y `submit_listing`) puede quedar por debajo del mínimo de tokens por modelo que exige esos docs. Pendiente: sumar un `CachePoint` después de la lista de trabajo (`work_message` en `v2.py`).
- **V2 es la única columna con 0 valores inválidos y 0 duplicados** de las tres, consistente con que las herramientas restringen los valores de lista al dominio del canal en vez de dejar que el modelo los invente.
- Tokens y segundos salen de Langfuse (`GET /api/public/v2/observations`, generaciones `BedrockConverse.achat`) sumando las ventanas de cada corrida del 1/10; no se registran en `resultados/` (ese directorio no se usa en el reinicio del 1/10).

## Reglas para trabajar en este repo
- **Todo el código en inglés** (decisión de Gastón, 1/10), aunque el template escriba en español.
- **La tabla de referencia manda.** Si `reference_attribute` o `reference_category` tienen el mapeo, se usa sin consultar al modelo. Nunca proponer que el LLM "mejore" un mapeo de la tabla.
- **Nunca inventar valores de atributos.** Si el canal exige un valor que no existe en el origen, marcarlo como faltante con un motivo explícito. No rellenarlo.
- **Los valores de lista deben pertenecer al dominio del canal** (por ejemplo, `Condição do Item` = `Novo` con URN `14703`). Todo valor fuera del dominio se rechaza.
- **Determinismo:** el mismo SKU tiene que dar la misma salida. Preferir la caché por SKU y canal antes que recalcular.
- **No hardcodear las API keys** de OpenAI, AWS, Alephee ni Langfuse. Van en variables de entorno o en un gestor de secretos, y el `.env` va en el `.gitignore`.
- **Datos personales:** los DNI de los asistentes están en el hilo de mail de logística y **no** se copian a este repo.
- Cada versión (V1, V2, V3) se commitea y se tagea antes de pasar a la siguiente, para poder comparar.
- Los datos del catálogo son de Alephee y de sus clientes (GM, concesionarios). No se suben a servicios externos fuera de los acordados.

## Chat desplegado (stage warroom)

Pendiente para Gastón:

1. Cargar secretos para el stage `warroom`:
   ```bash
   AUTH=$(printf '%s:%s' "$LANGFUSE_PUBLIC_KEY" "$LANGFUSE_SECRET_KEY" | base64)
   npx sst secret set ClientHmacSecret "<secreto HMAC>" --stage warroom
   npx sst secret set ObservabilidadOtlpEndpoint "https://us.cloud.langfuse.com/api/public/otel/v1/traces" --stage warroom
   npx sst secret set ObservabilidadOtlpHeaders "Authorization=Basic%20${AUTH},x-langfuse-ingestion-version=4" --stage warroom
   ```
   (Nota: los `LANGFUSE_*` deben ser los valores rotados de la organización.)

2. Desplegar a sandbox:
   ```bash
   AWS_PROFILE=sandbox npx sst deploy --stage warroom
   ```
   La salida lista los outputs (runtimeArn, repoCore, Function URL del BFF).

3. Probar el chat con el Runtime desplegado:
   ```bash
   API_URL="<Function URL del BFF>" CHAT_HMAC_SECRET="<el mismo secreto HMAC>" npm start -w apps/web
   ```
   En `http://localhost:3000`, escribir: "Mapea el SKU <un SKU de data/mock, por ejemplo 94701411>". El chat debe responder una tabla con categoría, atributos y faltantes. En Langfuse, una traza del Runtime con el turno del chat, la llamada a `map_product` y, adentro, la llamada estructurada de la V1. Un SKU que solo esté en `data/real` no se encuentra hasta que `CATALOG_ALLOW_REAL_DATA=1` esté seteado.

4. Destruir el stage cuando cierre:
   ```bash
   npx sst remove --stage warroom
   ```

**Advertencias:**
- El chat desplegado manda prompts y respuestas a Langfuse Cloud porque `contenidoEnTrazas: true`. Por eso mapea solo el dataset mock hasta que `CATALOG_ALLOW_REAL_DATA=1` se setee en el Runtime, y eso espera la confirmación de Alephee (spec, "Condiciones").
- El chat desplegado usa la semilla del prompt de sistema del repo, no Langfuse: el Runtime no tiene las claves de Langfuse (decisión del 1/10: no sumar más secretos al Runtime para el war room).
- `experiment.sh --data real` necesita `--allow-real-upload` después de que Alephee confirme.

## Contexto comercial (no es alcance del war room)
- Alephee ya es cliente de Craftech: renovación, SOW "IW Build", propuesta de un equipo de arquitectura y desarrollo, y una PoC de Data Lake.
- Alephee está migrando su base a Postgres. Cuando cierre la etapa 1, Rick comparte los esquemas para arrancar los cimientos del data lake.
- AWS nominó a Juan David y a Rick como speakers en AI Experience (4 de noviembre) con esta metodología, si el war room sale bien.

## Fuentes
- Temario: [War Room Alephee × Craftech — Temario (validación AWS)](https://docs.google.com/document/d/1bZbFmeoRltffTDj9lr48_JAFz9lAlRVww5CunzLx-Vg/edit)
- Borrador previo de Gastón: [War room … (14/10/2026)](https://docs.google.com/document/d/142WUJ5VZUFnG1h8cAmtV5Gegiy6BEKmHAS_EppAlKOg/edit)
- Reunión 25/08 "Alephee — AI workshop": [notas y transcripción de Gemini](https://docs.google.com/document/d/1BS6eTnPPWyKIoVS1mglrca4Lq8bIgcoi4eR7f4vYJqY/edit)
- Reunión 16/09 "Sync Alephee - War Room": [notas y transcripción de Gemini](https://docs.google.com/document/d/1_u7NyZG4pYwJuQ7wkHmAKKIoAi6AMIdg--SRiK63FCQ/edit)
- Mails: "Prompts" y "Re: Prompts" (Maximiliano Olivari, 25/08), "War Room AI — 1/10" (logística, 17–24/09), "Archivos para la War Room Alephee" (Maximiliano Olivari, 24/09)
