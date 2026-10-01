# V1 del agente de catálogo · diseño

Fecha: 2026-10-01 · Autor: Gastón Zarate (con Claude) · Estado: aprobado en conversación, pendiente de revisión escrita

## Objetivo

Mapear un producto del catálogo de Alephee (taxonomía de Mercado Libre) a una publicación de Shopee: categoría y atributos. La V1 es la primera de tres versiones que se construyen de a una sobre el template `craftech-io/chatbot-demo`. Es una **llamada estructurada sin herramientas**: muestra qué resuelve el modelo solo, y sus fallos justifican la V2 (agente con herramientas) y la V3 (control).

La V1 está terminada cuando:

1. pasan los tests (pytest, sin AWS ni Langfuse);
2. corrió un experimento en Langfuse sobre los 30 productos reales, con la línea de base del proceso actual (`current`) al lado;
3. el chat desplegado en la cuenta sandbox responde "mapea el SKU …" corriendo la V1 contra Bedrock;
4. la traza de ese pedido se ve en Langfuse.

## Decisiones tomadas en el brainstorming

| Tema | Decisión |
|---|---|
| Punto de partida | Template `chatbot-demo` bajado de nuevo. El código anterior está en `old/` (fuera de git) y en la rama `backup/pre-reinicio` (tag `pre-reinicio`). `docs/` quedó como estaba, sin las láminas de código. |
| Idioma | **Todo el código en inglés**: identificadores, archivos, eventos, docstrings y comentarios. Contradice la convención del template (todo en español); es decisión de Gastón. El chat del template existente no se traduce. |
| Contexto del modelo | Todo en el prompt: el catálogo de Shopee (categorías, atributos, valores válidos) y el producto. La V1 no ve las tablas `reference_*`. |
| Motor | `as_structured_llm(Listing).achat(messages)` de LlamaIndex, no `FunctionAgent`. Sin herramientas no hace falta un agente; `FunctionAgent` entra en la V2. |
| Contrato del Workflow | Cierra con una subclase tipada de `StopEvent` (`MappingCompleted`) cuyo campo `listing` es el modelo Pydantic `Listing`. `run()` devuelve ese objeto tal cual (`workflows/handler.py`: `stop_event.result if type(stop_event) is StopEvent else stop_event`). |
| Steps | Dos: `prepare` y `map`. |
| Prompt de sistema | En inglés, guardado en **Langfuse** (`catalog-v1-system`, label `production`). El repo guarda una copia inicial como semilla y fallback. |
| Evaluación | En **Langfuse Cloud** (`us.cloud.langfuse.com`): datasets, `run_experiment` y evaluadores propios. Reemplaza al runner batch y al conteo de tokens propio. |
| Datos | `data/real` y `data/mock` traídos de `old/` sin cambios. |
| Chat | Herramienta `map_product(sku)` en el chat del template. |
| Deploy | Entra en la V1: stage `warroom` en la cuenta sandbox (`033545611835`, perfil `sandbox`, `us-east-1`). |

### Condiciones que vienen con esas decisiones

- **Residencia de datos.** Con Langfuse Cloud, los 30 productos reales de GM, el prompt y las respuestas del modelo salen de AWS a un tercero. Cambia la decisión del 28/09 (trazas solo en CloudWatch) y la regla del repo de no subir datos de Alephee a servicios no acordados. **Confirmarlo con Rick antes de subir el dataset real.** Hasta entonces se puede trabajar con el dataset mock.
- **Secretos.** Las claves de Langfuse se leen de `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY` y `LANGFUSE_BASE_URL`. Gastón las carga en `.env` (ya ignorado por git) y en Secrets Manager (`alephee-catalogo/langfuse`); en el deploy van como secretos de SST. Nunca se escriben en código, docs ni commits. Las claves pegadas en la conversación del 1/10 se rotan.
- **Prompt editable fuera del repo.** Si alguien edita el prompt en Langfuse, la V1 cambia sin commit. Cada experimento registra nombre y versión del prompt.

## Paso 0 · Clonado del template

Antes del código, se corre el clonado del template (`scripts/clonar-para-cliente.sh`, conducido por la skill `clonar-para-cliente`) con las decisiones ya tomadas el 28/09: slug `alephee-catalogo`, auth del chat por HMAC, remoto en GitHub `craftech-io`. El script borra su propio `CLAUDE.md` y `.claude/`; el `CLAUDE.md` del proyecto se rehace a partir de `old/CLAUDE.md`, actualizado al reinicio.

## Componentes

Todo lo nuevo vive en `core/src/catalog/`:

| Archivo | Responsabilidad | Depende de |
|---|---|---|
| `models.py` | `Listing`, `MappedAttribute`, `MissingAttribute`, `RejectedAttribute` (Pydantic, `extra="forbid"`). Los campos conservan los nombres del formato de Alephee: `category`, `attributes[].urn/valueId/value/unit`, `missing[].urn/reason`, `rejected[].legacyId/reason`. | pydantic |
| `events.py` | `MappingRequested(StartEvent)` con `product: dict`; `ContextReady(Event)` con los mensajes; `MappingCompleted(StopEvent)` con `listing: Listing | None` y `error: str | None`. Ningún campo se llama `result`. | workflows |
| `llm.py` | `create_llm()`: `BedrockConverse` con `us.anthropic.claude-sonnet-5`, región y perfil del entorno. Único módulo que sabe de Bedrock. | llama-index-llms-bedrock-converse |
| `data.py` | Carga el dataset y los esquemas de Shopee desde `DATA_DIR` (`data/real` o `data/mock`); busca un producto por SKU. | — |
| `prompts.py` | `get_system_prompt(name)`: lee el prompt de Langfuse por label con fallback a la semilla en `core/src/catalog/prompts/<name>.txt`; devuelve texto y versión. | langfuse |
| `v1.py` | `MappingV1(Workflow)`: steps `prepare` y `map`. Recibe el LLM y el prompt inyectados. | models, events, data |
| `tracing.py` | `setup_tracing()`: cliente de Langfuse y `LlamaIndexInstrumentor` de OpenInference. Idempotente. La usan el experimento y el chat. | langfuse, openinference |
| `evaluation.py` | Evaluadores de Langfuse por ítem y por corrida (ver "Evaluación"). Funciones puras sobre `Listing` y `expected`. | models |
| `experiment.py` | CLI: sube los datasets a Langfuse de forma idempotente y corre `run_experiment` para una versión (`v1` o `current`). | data, v1, evaluation, tracing |
| `chat_tool.py` | `create_catalog_tools()`: la `FunctionTool` `map_product(sku)`. | data, v1, llm |

Fuera del paquete: `data/` (de `old/`), `scripts/experiment.sh`, `scripts/sync_prompts.py` (sube la semilla del prompt a Langfuse si no existe), tests en `core/tests/test_catalog_*.py`.

## Flujo de datos de la V1

```
MappingRequested(product)
   │
   ▼
[prepare]  system (prompt de Langfuse)
           user: catálogo de Shopee · CachePoint (TTL de 5 minutos: `BedrockConverse` 0.14.18 no pasa el `ttl` a Converse) · producto
   │ ContextReady(messages)
   ▼
[map]      as_structured_llm(Listing).achat(messages)
   │
   ▼
MappingCompleted(listing: Listing | None, error: str | None)
```

**`prepare`** arma los mensajes en orden fijo:

1. `system`: el prompt de sistema de Langfuse.
2. `user`, primer bloque: el catálogo de Shopee (cada categoría con esquema, sus atributos con tipo, obligatoriedad, `maxValues` y valores válidos) en JSON compacto con orden determinista. Es igual para todos los productos.
3. `CachePoint` (TTL de 5 minutos: `BedrockConverse` 0.14.18 no pasa el `ttl` a Converse).
4. `user`, último bloque: el producto (`sku`, `name`, `categories`, `brand`, `attributes` y los primeros 1.500 caracteres de `description`; hay descripciones de hasta 19.000).

**`map`** hace una sola llamada estructurada y devuelve el `Listing` validado. No hay reintentos: la V1 muestra lo que hace el modelo solo. Se usa `as_structured_llm(...).achat(messages)` y no `astructured_predict(prompt_template)` porque recibe los mensajes tal cual, con el `CachePoint`; con plantilla no está garantizado que el bloque sobreviva.

**Tokens, costo y latencia** no viajan en el evento: los registra Langfuse en la traza de cada producto (OpenInference captura el uso que devuelve Bedrock) y el experimento los agrega por corrida.

### Cómo funciona la caché de prompt

Fuente: [AWS, Prompt caching for faster model inference](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html).

- Bedrock guarda el prefijo anterior al `cachePoint`, procesado en orden `tools` → `system` → `messages`. Cambiar algo antes de la marca invalida la caché.
- Claude Sonnet 5 exige al menos 1.024 tokens antes de la marca; el catálogo de la V1 tiene unos 20.000.
- TTL de 5 minutos por defecto, que se renueva con cada acierto; Sonnet 5 acepta 1 hora (`"ttl": "1h"`), que conviene para un batch con pausas.
- La escritura en caché puede costar más que la entrada normal; la lectura cuesta menos. La respuesta lo informa en `cacheReadInputTokens` y `cacheWriteInputTokens`.
- No hay garantía de acierto; con inferencia entre regiones puede haber más escrituras.

A verificar en la implementación: que `as_structured_llm` conserve el bloque.

## Prompt de sistema en Langfuse

Fuente: [Langfuse, Prompt management](https://langfuse.com/docs/prompt-management/get-started).

- Nombre `catalog-v1-system`, tipo `text`, label `production`. Cada `create_prompt` con el mismo nombre crea una versión nueva.
- La V1 lo lee con `get_prompt("catalog-v1-system", label="production", fallback=<semilla>)`. El SDK lo cachea en memoria y sigue con la última versión si Langfuse no responde.
- Semilla en `core/src/catalog/prompts/catalog-v1-system.txt`; `scripts/sync_prompts.py` la sube si el prompt no existe en Langfuse. Los tests usan la semilla y nunca llaman a Langfuse.
- El prompt incluye: rol, tarea, que la categoría y los URN se copian exactos del catálogo, que los valores de lista salen del dominio del canal, que los valores del producto no se traducen, que `-1`, `N/A` o vacío significan sin dato, que nunca se inventan valores, cuándo va un obligatorio a `missing` y un atributo del producto a `rejected`, y que cada atributo del canal aparece una sola vez.
- A verificar en la implementación: si la versión del prompt se puede enlazar a cada generación de la traza que manda OpenInference. Si no se puede, queda al menos en los metadatos del experimento.

## Evaluación en Langfuse

Fuentes: [Langfuse, Experiments via SDK](https://langfuse.com/docs/evaluation/experiments/experiments-via-sdk) · [referencia del SDK](https://python.reference.langfuse.com/langfuse/experiment).

**Datasets.** `alephee-shopee-real` (30 productos) y `alephee-shopee-mock` (10 casos de borde). Cada ítem:

- `input`: el producto de Alephee (el importador ya sacó `relations`);
- `expected_output`: el `expected` del caso;
- `metadata`: id del caso, `origin` (`real` o `mock`), `decision_pending`, `expected_is_mock: true` y, en los reales, la publicación actual de Alephee (`actual`).

El id del ítem es el id del caso, así que volver a subir no duplica.

**Experimentos.** `scripts/experiment.sh --version v1|current --data real|mock [--case <id>]` corre `dataset.run_experiment` con:

- tarea `v1`: corre `MappingV1` sobre el ítem y devuelve el `Listing`; tarea `current`: devuelve la publicación actual de Alephee sin llamar al modelo;
- metadatos: modelo, nombre y versión del prompt, commit del repo;
- `max_concurrency=4`, para no chocar con el límite de Bedrock.

**Evaluadores por ítem:** `exact` (misma regla del deck: categoría correcta, ningún atributo de más ni de menos, ningún valor fuera de dominio, ningún duplicado, mismos faltantes esperados), `category_ok`, `invalid_values` (`-1` o fuera de la lista del canal), `duplicates`, `missing_ok`, `precision`, `recall`.

**Evaluadores por corrida:** cantidad de exactos, de categorías correctas, de inválidos y de duplicados; precisión y recall totales.

La lógica de la métrica se reescribe en inglés a partir de `old/core/src/catalogo/evaluacion.py`; los tests de la métrica se portan de `old/core/tests/test_catalogo_evaluacion.py`.

## Chat del template

- `map_product(sku)` busca el producto en `data/real` y después en `data/mock`, corre `MappingV1` y devuelve el `Listing` en JSON con nombres de categoría y atributo. Si el SKU no existe o la V1 falla, devuelve un mensaje claro y nunca lanza una excepción al chat (el patrón de `crear_tools_usuario`).
- Se registra en `armar_tools` de `core/server.py` como herramienta fija: no depende del usuario ni del Gateway.
- El prompt del chat en `client.config.ts` suma que, ante un pedido de mapeo, use `map_product`.
- El `core/Dockerfile` suma `COPY data/ ./data/`.
- Modo local sin AWS: `examples/demo-client/mock.mjs` suma un escenario "mapea el SKU …" con una publicación de ejemplo rotulada como mock. No corre la V1.

## Deploy en sandbox

- Stage `warroom` en la cuenta sandbox. No es `production`: `removal: remove`, se puede destruir entero.
- Secretos de SST (los carga Gastón con `npx sst secret set … --stage warroom`): `ClientHmacSecret`, `ObservabilidadOtlpEndpoint` (`https://us.cloud.langfuse.com/api/public/otel/v1/traces`) y `ObservabilidadOtlpHeaders` (con `%20` en vez de espacio, ver `docs/langfuse.md`).
- `client.config.ts`: `observabilidad.destino: "otlp"`, `contenidoEnTrazas: true`, `muestreo: 1`.
- Imagen ARM64 (Docker buildx) y `npx sst deploy --stage warroom` desde local.
- Prueba: el demo-client contra la Function URL del BFF con HMAC (`API_URL` y `CHAT_HMAC_SECRET`).

## Errores

| Situación | Comportamiento |
|---|---|
| Bedrock devuelve error o la salida no cumple `Listing` | `MappingCompleted(listing=None, error=...)`; en el experimento el ítem cuenta como no exacto y el error va como comentario del score |
| Sesión SSO vencida o sin credenciales | El experimento corta entero con el comando `aws sso login --profile sandbox` |
| Langfuse no responde | El prompt sale de la caché del SDK o de la semilla; el exportador de trazas falla aparte sin romper el mapeo |
| SKU inexistente en el chat | `map_product` responde que no está en el dataset |

## Tests

Con pytest, sin AWS ni Langfuse, escritos antes del código (TDD):

- `Listing` rechaza campos de más y acepta el ejemplo real de `data/real`.
- `prepare`: orden system → catálogo → `CachePoint` → producto; descripción recortada a 1.500; catálogo determinista.
- `map`: con un doble del LLM devuelve `MappingCompleted` con el `Listing`; con una salida inválida, `listing=None` y error.
- `prompts`: sin Langfuse usa la semilla.
- Evaluadores: los casos de la métrica del deck.
- `map_product`: SKU inexistente, error de la V1 y respuesta correcta, con un Workflow doble.
- `server.py`: la herramienta queda registrada.
- Humo real contra Bedrock con un caso (`--case`) antes del experimento completo.

## Fuera de alcance de la V1

Tablas de referencia como herramientas (V2), `FunctionAgent` (V2), guardrails, memoria de correcciones y caché por SKU (V3), integración con la API de Alephee, y volver a poner las láminas de código del deck (se hace cuando el código nuevo exista).

## Riesgos y pendientes

- **La categoría de la V1 es optimista.** El catálogo del prompt tiene solo las 23 categorías con esquema, armado a partir de los mismos 30 productos: la respuesta correcta siempre está entre las opciones. `reference_category` apunta a 337 categorías de Shopee y Shopee tiene más. Decisión de Gastón (1/10): se mantienen las 23 y todo resultado de categoría de la V1 se presenta rotulado así. No se compara de igual a igual con el proceso actual.
- Confirmar con Rick la subida de datos reales a Langfuse Cloud.
- El `expected` de los 30 reales y el esquema de Shopee siguen siendo mock: los exactos son una cota, no una verdad.
- Verificar en la implementación el `ttl` del `CachePoint`, que `as_structured_llm` conserve el bloque y el enlace prompt-traza.
- La sesión SSO de `sandbox` dura pocas horas: renovarla antes de cada tanda.
