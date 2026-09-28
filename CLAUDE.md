# War Room Alephee × Craftech × AWS

> Contexto de trabajo para construir, en un día, el agente que mapea categorías y atributos de un producto del catálogo de Alephee a una publicación de canal (Shopee).
> Última actualización: 2026-09-28 (Gastón Zarate).

## Datos del evento

| | |
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
- Maria Alejandra "Mariale" Cotes (mcotes@amazon.com): Account Manager Startups. Sala, licencias de Kiro, merch.
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
3. **Kiro** es la herramienta de desarrollo durante el día, con licencias pagas activadas vía AWS, para no consumir tokens del cliente (16/09).
4. La solución se llama "agente" o "solución", no "bot", porque puede terminar siendo un flujo agéntico con más de un agente (16/09).
5. La definición de la solución incluye whiteboarding de arquitectura, criterios de éxito y el dataset de prueba (16/09).
6. **El agente corre sobre Amazon Bedrock con Claude Sonnet 5** (Gastón, 25/09).
7. **Este directorio es el repo del agente** (Gastón, 25/09). Es un **clon del template `craftech-io/chatbot-demo`** con slug `alephee-catalogo` (Gastón, 28/09).
8. **Mientras no lleguen los datos reales, se trabaja con mocks** en `data/mock/` (Gastón, 25/09).
9. **Stack: Python + LlamaIndex Workflows + `BedrockConverse`**, el mismo del core del template (Gastón, 28/09).
10. **Interfaz: chat y batch.** En la sala se muestra el chat del template (widget + BFF + AgentCore) y el mismo workflow corre en batch sobre el dataset, que es como lo usaría Alephee en producción (Gastón, 28/09).
11. **Clon:** remoto en GitHub `craftech-io`, auth del chat por **HMAC** para la demo, trazas **solo en CloudWatch** (Gastón, 28/09).

## Decisiones a tomar en la sala (bloque 09:30)
Cada decisión se presenta con opciones y consecuencias, y se cierra antes de pasar a la siguiente. Se documentan en `decisiones/` con el formato `NN-titulo.md` (contexto, opciones, decisión, razonamiento).
1. ¿Qué hace y qué no hace? (un canal, una familia de productos)
2. ¿Qué recibe y qué entrega? (contrato de entrada y salida por escrito)
3. ¿Qué decide el agente y qué decide una tabla?
4. ¿Qué hace cuando no sabe? (reemplaza el "publicar sin atributos" de hoy)
5. ¿Cuándo está bien hecho? (un número acordado antes de escribir código)
6. Criterios de éxito de la solución (incluir restricción de costo del modelo)
7. Dataset de prueba (los 30 productos)

Temas abiertos para el whiteboarding, que no están decididos: caché por SKU, gobernanza, seguridad e integración con Alephee (API pública para leer, acceso interno para escribir).

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
Es el clon del template `chatbot-demo` (ver su `README.md` y `docs/`), más lo propio del war room:

```
CLAUDE.md                      este archivo (el playbook de clonado del template se borró, como corresponde)
client.config.ts               config por cliente: slug alephee-catalogo, modelo, región, prompt, topes
core/                          el agente (Python / LlamaIndex Workflows), contrato BYOC /ping y /invocations
  src/agent/                   el chat del template: ChatWorkflow, adaptador BedrockConverse, tools, costo
  src/catalogo/                LO NUESTRO: el agente de catálogo
    modelos.py                 contrato de salida (Pydantic `Publicacion`)
    eventos.py                 MapeoStart / MapeoDone
    llm.py                     crea el BedrockConverse (único módulo que sabe de Bedrock)
    v1.py                      V1 · solo instrucciones: Workflow de un paso, salida por tool `entregar_publicacion`
    datos.py                   carga tablas y dataset (DATA_DIR, por defecto data/mock/)
    evaluacion.py              compara contra `expected`: exactos, precisión, recall, inválidos, duplicados, faltantes
    correr.py                  modo batch: corre una versión sobre el dataset y guarda en resultados/
  tests/                       tests del template + test_catalogo_*.py (con dobles, sin AWS)
packages/                      bff, worker, widget, shared (TypeScript)
apps/web, apps/api             app web de demo (modo mock sin AWS) y stand-in de la API del cliente
infra/sst/                     IaC (SST): Runtime, Gateway, Guardrail, Memory, tablas, colas
data/mock/                     datos MOCK (10 casos con salida esperada inventada, salvo el 01)
data/real/                     datos REALES de WarRoom.zip: 2 tablas + 30 productos con la publicación actual
inputs/                        ejemplos, prompts actuales (index.ts) y WarRoom.zip + WarRoom/ crudo (ignorado por git)
scripts/importar_warroom.py    WarRoom/ → data/real/ (saca relations e _id de Mongo)
decisiones/                    una decisión por archivo, completada en la sala
scripts/correr.sh              atajo del modo batch
resultados/                    salidas de cada corrida (ignorado por git)
```

## Stack y cómo correr
- **Python 3.13 + uv**, **LlamaIndex Workflows** y **`BedrockConverse`** (`llama-index-llms-bedrock-converse` 0.14.18, que ya lista `anthropic.claude-sonnet-5` con tool calling y caché de prompts). Front, BFF e IaC en TypeScript con **SST**.
- **Modelo:** Claude Sonnet 5 en Bedrock, región `us-east-1`, perfil SSO `sandbox` en local. ID **`us.anthropic.claude-sonnet-5`** (verificado 28/09: Converse acepta `us.` y `global.`; sin prefijo da `ValidationException` por falta de throughput on-demand). Ya está en `client.config.ts`.
- **Patrón del template que se respeta:** el workflow no conoce Bedrock (recibe el LLM inyectado), cada step se prueba con dobles, todo en español, comentarios escasos, y **toda capacidad nueva trae su modo mock**.
- **Comandos:**
  ```bash
  aws sso login --profile sandbox          # si la sesión venció
  uv sync && npm install
  uv run pytest core/tests                 # Python, sin AWS
  npm test && npm run typecheck            # TypeScript
  npm run dev                              # chat en modo mock: http://localhost:3000
  scripts/correr.sh --version v1           # batch contra Bedrock + evaluación
  scripts/correr.sh --version v1 --caso 03-valor-en-otro-idioma
  ```
- **Métrica de "La prueba":** un caso es **exacto** si la categoría es correcta, no sobra ni falta ningún atributo, no hay valores fuera de dominio ni duplicados, y los faltantes obligatorios coinciden con los esperados. Además se reportan precisión y recall de atributos, tokens y latencia. El umbral de éxito se acuerda en la sala (decisión 5).
- **Resultado de la V1 sobre el dataset mock (28/09):** 6/10 exactos, precisión 0,92, recall 0,97, **0 valores inválidos**, 0 duplicados, ~5 s por producto, ~3.700 tokens de entrada y ~400 de salida por producto, sin caché. Los 4 que fallan:
  - **09 (sin categoría):** el modelo **inventó la categoría** a partir del nombre ("Calota") aunque el producto no traía categoría de origen, y marcó como faltantes atributos que el caso no esperaba. Es el fallo que justifica la V2: sin categoría de origen, la respuesta tiene que ser determinista.
  - **04 (booleano falso):** mapeó bien `Não`, pero descartó `Tipo de taza = Centro` en vez de llevarlo a `Parcial`. Es discutible: el `expected` mock puede ser demasiado generoso. Revisarlo con el equipo de catálogo.
  - **07 (unidad) y 10 (dato en la descripción):** el modelo eligió la opción "generosa" (convirtió 390 g a 0,39 kg y sacó el color de la descripción). Son decisiones pendientes: si la sala las aprueba, pasan a ser correctas.
- **Cómo sumar V2 y V3:** un Workflow nuevo en `core/src/catalogo/` que reciba `MapeoStart` y devuelva `MapeoDone`, registrado en `VERSIONES` de `correr.py`.
- **Cómo llega al chat (pendiente):** una `FunctionTool` `mapear_producto(sku)` en `core/server.py` que corre el workflow de catálogo; su texto mock va en `apps/web/mock.mjs`. El Dockerfile hoy copia solo `core/`: hay que sumar `data/`.

### Datos reales (WarRoom.zip, recibido el 24/09, importado el 28/09)
- **30 productos de 22 categorías de Shopee, ninguno de Calotas**: 20 publicados y 10 rechazados por Shopee. Cada caso trae el producto, la publicación que genera hoy el proceso (`actual`) y, si fue rechazado, el motivo (`actual.error`).
- **Motivos de rechazo:** obligatorio faltante (Inmetro Certification, GTIN, Manufacturer, Auto-Part Number), "Attribute value is not linked to <atributo>" (valor fuera de la lista del canal) y "Only support to fill one value".
- **Errores del proceso actual que Shopee acepta igual:** valores `-1` publicados como valores en 9 de 30, atributos duplicados en 4 (uno con 9 repetidos) y 2 publicaciones cuya categoría no es la de `reference_category`.
- **`expected` es null en todos:** la publicación de hoy es la línea de base, no la respuesta correcta. Para medir aciertos hay que validar salidas esperadas con el equipo de catálogo, o medir contra reglas de Shopee.
- **Falta para la V2 y la V3:** los atributos por categoría de Shopee (cuáles son obligatorios y la lista de valores válidos) para las 22 categorías. No vinieron en el zip y sin eso no se puede elegir entre los 306 destinos ambiguos ni validar "value is not linked". Alephee los tiene: son los "External Attributes" que hoy pasa al prompt.
- Los archivos crudos pesan ~15 MB, casi todo `relations` (compatibilidades con vehículos), que no hace falta para el mapeo.

### Datos mock
- Todo lo inventado está marcado con `_origen: "mock"`, con `(MOCK)` en el nombre o con SKU `MOCK-*`. Lo que sale del ejemplo real está marcado como tal. **Nunca presentar un dato mock como real.**
- El dataset cubre: caso real, caso feliz, valor en otro idioma, booleano falso, valor fuera de dominio, obligatorio faltante, unidad distinta, categoría sin referencia, producto sin categoría y dato que solo está en la descripción.
- Los casos 07, 08 y 10 tienen `decision_pendiente`: su salida esperada depende de decisiones que se toman en la sala.
- `Material` (legacyId 1726) no está en `reference_attribute` a propósito, para probar el camino que sí necesita modelo.
- Cuando llegue `WarRoom.zip`, se reemplazan las tablas y se suman los 30 productos reales. Los casos mock se pueden quedar como tests de borde.

## Reglas para trabajar en este repo
- **La tabla de referencia manda.** Si `reference_attribute` o `reference_category` tienen el mapeo, se usa sin consultar al modelo. Nunca proponer que el LLM "mejore" un mapeo de la tabla.
- **Nunca inventar valores de atributos.** Si el canal exige un valor que no existe en el origen, marcarlo como faltante con un motivo explícito. No rellenarlo.
- **Los valores de lista deben pertenecer al dominio del canal** (por ejemplo, `Condição do Item` = `Novo` con URN `14703`). Todo valor fuera del dominio se rechaza.
- **Determinismo:** el mismo SKU tiene que dar la misma salida. Preferir la caché por SKU y canal antes que recalcular.
- **No hardcodear las API keys** de OpenAI, AWS ni Alephee. Van en variables de entorno o en un gestor de secretos, y el `.env` va en el `.gitignore`.
- **Datos personales:** los DNI de los asistentes están en el hilo de mail de logística y **no** se copian a este repo.
- Cada versión (V1, V2, V3) se commitea y se tagea antes de pasar a la siguiente, para poder comparar.
- Los datos del catálogo son de Alephee y de sus clientes (GM, concesionarios). No se suben a servicios externos fuera de los acordados.

## Pendientes antes del 1/10
| Qué | Quién | Estado |
|---|---|---|
| Corregir la fecha en el temario (dice 14/10) | Jesus / Gastón | Pendiente |
| Instructivo de instalación de Kiro a Alephee (vencía "una semana antes", o sea, alrededor del 24/09) | Craftech (Juan David o Lucas lo tienen) | **Verificar si ya se envió** |
| Licencias de Kiro: 9 usuarios, falta el AWS Account ID donde se asignan los créditos | Mariale ↔ Rick | Esperando respuesta de Rick (24/09) |
| Tablas de referencia exportadas y 30 productos de ejemplo | Alephee | **Hecho.** Importados a `data/real/` el 28/09 |
| Pedir a Maximiliano los atributos por categoría de Shopee (obligatorios + valores válidos) de las 22 categorías del dataset | Gastón | Pendiente. **Bloquea la V2 y la V3 sobre datos reales** |
| Validar con el equipo de catálogo la salida esperada de al menos los 10 rechazados | Alephee | Pendiente |
| Adaptar el evaluador a los datos reales (reglas de Shopee + comparación contra `actual`) | Gastón | Pendiente |
| Pedirle a Rick un repo de Alephee para dejar el código a las 17:00 | Gastón | Pendiente |
| Pedir a Maximiliano: modelo y parámetros exactos, el código del merge y del lookup de `reference_category`, y la lista de atributos de Calotas en Shopee | Gastón | Pendiente |
| Pedir acceso para integrar: `API_KEY` y `accountId` de prueba de la API v2 (con licencia PIM), y cómo se leen y escriben publicaciones y tablas `reference_*` en la plataforma nueva | Gastón → Maximiliano / Rick | Pendiente |
| Cuenta AWS con Bedrock habilitado y acceso al modelo elegido, para el día del war room | Mariale / Juan David | Pendiente |
| Preparar V1 base "masticada" para no arrancar de cero en la sala | Gastón / Luciano | **Hecho.** Corrida contra Bedrock el 28/09: 6/10 exactos, 0 inválidos |
| Verificar el model ID de Sonnet 5 en Converse y actualizar `client.config.ts` | Gastón | **Hecho** (`us.anthropic.claude-sonnet-5`) |
| Cerrar el clon: prosa que menciona el template (README, `docs/diseno.md`, `docs/notas-tecnicas.md`), secciones internas de `docs/diseno.md`, textos de `apps/web/mock.mjs`, `marca.mjs` (nombre y paleta de Alephee), `promptSistema` y topes en `client.config.ts` | Gastón | Pendiente |
| Integrar el agente de catálogo al chat (`mapear_producto`) + mock | Gastón | Pendiente |
| Crear el repo en `craftech-io` y primer commit | Gastón | Pendiente (esperando OK) |
| Primer deploy a sandbox **desde local** (Docker buildx + ARM64), stage a definir | Gastón | Pendiente |
| Preparar V2 (herramientas: lookup en `reference_*` + normalización de valores) | Gastón / Luciano | Pendiente |
| Checkpoint Gastón / Jesus | Hoy 25/09, 10:30 | — |

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
