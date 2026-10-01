# V2 del agente de catálogo · diseño

Fecha: 2026-10-01 · Autor: Gastón Zarate (con Claude) · Estado: aprobado en conversación, pendiente de revisión escrita

## Objetivo

La V2 junta lo que en el diseño anterior eran la V2 (las tablas de referencia como herramientas) y la V3 (validación en código, correcciones del equipo de catálogo y caché por SKU). Se construye sobre la V1 (`docs/superpowers/specs/2026-10-01-v1-catalog-agent-design.md`) sin modificarla: mismo contrato `Listing`, mismo cierre `MappingCompleted`, mismo experimento en Langfuse.

Punto de partida medido el 1/10 en Langfuse, sobre los 30 productos reales y con la salida esperada MOCK:

| Métrica | Proceso de hoy | V1 |
|---|---|---|
| Casos exactos | 7 | 4 |
| Categoría correcta | 28 | 28 |
| Valores inválidos | 47 | 3 |
| Duplicados | 5 | 0 |
| Precisión / recall | 0,70 / 0,97 | 0,70 / 0,55 |

La V1 casi elimina inválidos y duplicados, pero deja muchos atributos sin mapear (recall 0,55) y elige la categoría entre 23 opciones que siempre incluyen la correcta. La V2 resuelve con las tablas lo que las tablas saben, y deja al modelo solo lo que necesita interpretación.

La V2 está terminada cuando:

1. pasan los tests (pytest, sin AWS ni Langfuse);
2. corrieron `v2-mock` y `v2-real` en Langfuse, al lado de `current` y `v1`;
3. sobre los 30 reales: cero valores inválidos, cero duplicados y cero obligatorios sin informar, con más recall que la V1;
4. el chat desplegado (stage `warroom`) responde con `map_product_v2`, y una corrección cargada con `scripts/correct.sh` cambia el resultado del mismo SKU.
5. los tests e2e pasan contra los servicios reales de la cuenta sandbox y contra el chat desplegado;
6. las láminas del deck describen solo lo que existe: arquitectura, comandos, pruebas y números de V1 y V2.

## Decisiones tomadas en el brainstorming

| Tema | Decisión |
|---|---|
| Alcance | Una sola versión, V2, con tablas, validación, correcciones y caché |
| Qué resuelve el código | La categoría (`reference_category`) y los campos que mapea `reference_attribute`, filtrados por la categoría. El código además copia los campos de texto libre y resuelve los de lista con coincidencia exacta de valor. Eso viaja como "ya resuelto" y gana sobre el agente |
| Motor | `FunctionAgent` de LlamaIndex dentro de un Workflow con steps |
| Herramientas del agente | `lookup_corrections(attribute_urn, product_value)` y `submit_listing(Listing)`, que valida en código y devuelve los problemas para que el agente corrija |
| Correcciones y caché | DynamoDB en la cuenta sandbox, dos tablas nuevas en el stack de SST |
| Chat | Dos herramientas: `map_product_v1` y `map_product_v2` |
| Código | En inglés, como la V1 |
| Tests e2e | Dos niveles: el agente contra Bedrock y DynamoDB, y el chat desplegado contra el BFF |
| Presentación | La V2 incluye revisar las 58 láminas y adaptarlas a la arquitectura, las pruebas y los números reales |

## Componentes

Todo lo nuevo vive en `core/src/catalog/`:

| Archivo | Responsabilidad |
|---|---|
| `reference.py` | Carga `reference_category` y `reference_attribute` desde `DATA_DIR`. `category_for(product)` resuelve la categoría de Shopee desde `product.categories[0].urn` (`urn:category:<id>` contra el `legacyId` pelado). `targets_for(legacy_attribute_id, category_schema)` devuelve el atributo de Shopee de la tabla que pertenece a esa categoría (306 ids legacy apuntan a más de un atributo; el filtro por categoría los desambigua). `tables_version(directory)` es un hash corto de los dos archivos. |
| `worklist.py` | `build_worklist(product, category, schema, reference) -> Worklist`: `resolved` (atributos que el código ya resolvió, con `MappedAttribute`), `to_decide` (atributos mapeados por tabla cuyo valor necesita interpretación, con el valor del producto y la lista de valores válidos), `unmapped_product` (atributos del producto sin destino) y `uncovered_channel` (atributos de la categoría que la tabla no cubre, con tipo, obligatoriedad, `maxValues` y valores). Los valores `-1`, `N/A` y vacío cuentan como sin dato. |
| `guardrails.py` | `validate(listing, schema, category) -> list[str]`: URN fuera de la categoría, valor sin dato, valor fuera de lista, nombre que no coincide con su id, duplicados, más valores que `maxValues`, obligatorio que no está ni en `attributes` ni en `missing`, y categoría distinta de la de la tabla. `clean(listing, schema, category) -> Listing`: fija la categoría de la tabla, descarta lo inválido a `rejected` con motivo y agrega a `missing` los obligatorios que faltan. Nunca inventa valores. |
| `store.py` | `CorrectionStore` (`find(category, attribute_urn, product_value)`, `put(...)`, `list(category)`) y `MappingCache` (`get(key)`, `put(key, listing)`, `invalidate_category(...)`), cada uno con implementación DynamoDB y en memoria. `product_value` se normaliza (`casefold` y `strip`) en la clave. |
| `v2.py` | `MappingV2(Workflow)` con los steps de abajo. Recibe inyectados el LLM, el prompt, los esquemas, la referencia, el almacén de correcciones y la caché. |
| `prompts/catalog-v2-system.txt` | Semilla del prompt en inglés; en Langfuse como `catalog-v2-system`, label `production`. |

Cambios en piezas existentes:

- `events.py`: eventos intermedios `CacheMissed`, `WorkReady`, `AgentDone`; `MappingCompleted` suma `source: str = "model"` (valores `cache`, `tables`, `agent`, y `model` para la V1). Cambio compatible: la V1 no lo setea.
- `experiment.py`: `--version v2`; la tarea arma `MappingV2` con los almacenes según el entorno.
- `chat_tool.py`: `create_catalog_tools` devuelve `map_product_v1` y `map_product_v2`.
- `infra/sst/catalogo.ts`: las dos tablas DynamoDB, enlazadas al Runtime con variables `CATALOG_CORRECTIONS_TABLE` y `CATALOG_CACHE_TABLE` y permisos acotados (`GetItem`, `Query`, `PutItem` en las dos; `DeleteItem` en la caché). Se importa desde `sst.config.ts`.
- `scripts/correct.sh`: carga una corrección y vacía la caché de esa categoría.

## Flujo del Workflow

```
MappingRequested(product)
  ↓
[check_cache]  clave: SKU + categoría de origen + versión de las tablas + versión del prompt
  ├─ hit y validate() sin problemas → MappingCompleted(source="cache")          sin modelo
  ↓ CacheMissed
[resolve]      categoría por tabla; esquema; worklist
  ├─ sin referencia o sin esquema → MappingCompleted(missing: category, source="tables")   sin modelo
  ↓ WorkReady(category, schema, worklist)
[run_agent]    FunctionAgent(system: catalog-v2-system, tools: lookup_corrections, submit_listing)
  ↓ AgentDone(last_submission, valid)
[finalize]     merge(resolved gana) → clean() → caché → MappingCompleted(source="agent")
```

### `run_agent`

- El mensaje de usuario lleva la categoría, el esquema de la categoría y la worklist en JSON compacto con orden determinista. Los atributos `resolved` van marcados como fijos.
- `submit_listing` recibe un `Listing`. Primero lo junta con `resolved` (lo resuelto por código gana), después corre `validate()`. Si hay problemas, la herramienta lanza una excepción con la lista en lenguaje claro: `FunctionAgent` devuelve ese error al modelo como resultado de la herramienta y el modelo corrige. Si no hay problemas, la herramienta es `return_direct` y el agente termina.
- Cada entrega, válida o no, se guarda en un registro por corrida para que `finalize` tenga la última.
- `lookup_corrections` devuelve la corrección del equipo de catálogo para esa categoría, atributo y valor del producto, o "no correction". El prompt exige consultarla antes de elegir un valor de lista y usarla tal cual si existe.
- Límite: `max_iterations=5`. En `llama-index-core` 0.14.24, al llegar al límite `FunctionAgent` lanza `WorkflowRuntimeError` (con `early_stopping_method="force"`): el step lo captura y sigue con la última entrega. `FunctionAgent` solo fuerza una herramienta en la primera llamada (`initial_tool_choice`), así que la entrega garantizada se resuelve en `finalize`, no en el agente.
- Memoria del agente con `token_limit` explícito (el default recorta en silencio).

### `finalize`

- Sin ninguna entrega: `MappingCompleted(listing=None, error=..., source="agent")`.
- Con entrega: `merge` con `resolved`, `clean()`, `put` en la caché solo si la entrega final pasa `validate()` sin problemas, y `MappingCompleted(listing, source="agent")`.

## Correcciones y caché

| Tabla | Clave | Atributos |
|---|---|---|
| `corrections` | PK `category_urn` · SK `attribute_urn#product_value` | `value_id`, `value`, `author`, `created_at` |
| `mapping_cache` | PK `sku#legacy_category` · SK `tables_version#prompt_version` | `listing` (JSON), `created_at` |

- On-demand, en la cuenta sandbox (033545611835), stage `warroom`.
- Invalidación: si cambian las tablas o el prompt, cambia la clave; al cargar una corrección, `scripts/correct.sh` borra la caché de esa categoría.
- El experimento local toma los nombres de las tablas de los outputs del deploy (`.sst/outputs.json`) o de `CATALOG_CORRECTIONS_TABLE` y `CATALOG_CACHE_TABLE`. Sin ellos usa los almacenes en memoria y lo avisa.
- Si DynamoDB falla en una corrida, la V2 sigue sin caché y sin correcciones, y deja el aviso en el log y en la traza.

Demo de la sala:

```bash
scripts/correct.sh --category <urn> --attribute <urn> --product-value <valor> --value-id <id> --value <nombre>
scripts/experiment.sh --version v2 --data mock --case <id>
```

## Prompt

- `catalog-v2-system` en Langfuse con semilla en el repo, igual que la V1. Incluye: los atributos `resolved` no se tocan; para cada `to_decide`, consultar `lookup_corrections` y elegir el valor equivalente de la lista; completar `uncovered_channel` solo si un atributo del producto es claramente el mismo concepto; nunca inventar ni traducir valores; los obligatorios sin dato van a `missing` con motivo; entregar con `submit_listing` y, si devuelve problemas, corregirlos y volver a entregar.
- El chat desplegado usa la semilla (el Runtime no tiene claves de Langfuse, decisión del 1/10).

## Chat

- `map_product_v1(sku)` y `map_product_v2(sku)`: el modelo del chat elige según lo que pida el usuario; por defecto, el prompt del chat pide usar la V2.
- Siguen las reglas de la V1: solo el dataset mock salvo `CATALOG_ALLOW_REAL_DATA=1`; nunca una excepción al chat.
- El prompt del chat (`client.config.ts`) suma la mención de las dos herramientas sin pasar el límite de 2.048 caracteres en base64 de AgentCore.

## Errores

| Situación | Comportamiento |
|---|---|
| Producto sin categoría o fuera de la tabla | `missing: category`, sin modelo |
| Categoría sin esquema | `missing: category` con motivo "sin esquema", sin modelo |
| Entrega inválida | `submit_listing` devuelve los problemas y el agente corrige |
| Iteraciones agotadas | `finalize` limpia la última entrega |
| Sin ninguna entrega | `MappingCompleted(listing=None, error=...)` |
| Credenciales de AWS vencidas | Corta el experimento entero (como la V1) |
| DynamoDB no responde | Sigue sin caché ni correcciones, con aviso |

## Tests

Con pytest, sin AWS ni Langfuse, antes del código:

- `reference`: categoría por tabla; destino de atributo filtrado por categoría, incluido un id con varios destinos; producto sin categoría.
- `worklist`: texto libre copiado; coincidencia exacta de lista; valores sin dato; separación de `to_decide`, `unmapped_product` y `uncovered_channel`.
- `guardrails`: cada problema de `validate`; `clean` nunca deja inválidos ni duplicados y fija la categoría de la tabla.
- `store`: almacenes en memoria; normalización del valor; invalidación por categoría.
- `MappingV2` con un doble del LLM compatible con `FunctionAgent`: caché hit; sin categoría; entrega válida al primer intento; entrega inválida corregida en el segundo; iteraciones agotadas; sin ninguna entrega; lo resuelto por código gana; la corrección se usa.
- `chat_tool`: las dos herramientas.
- `experiment`: `--version v2`.
- Humo real con un caso contra Bedrock antes del experimento completo.

## Tests e2e

Corren contra servicios reales, fuera de la suite normal. Se marcan con `@pytest.mark.e2e` y se saltean salvo con `RUN_E2E=1`. Se lanzan con `scripts/e2e.sh`, que carga el `.env` y usa el perfil `sandbox`. Usan solo el dataset mock: no suben datos reales.

**Nivel 1 · el agente contra Bedrock y DynamoDB** (`core/tests/e2e/test_e2e_mapping.py`):

- V1 sobre `01-real-calota-aro14`: devuelve `MappingCompleted` con un `Listing` tipado y la categoría Calotas.
- V2 sobre los 10 casos mock: todo `Listing` con categoría pasa `validate()` sin problemas (cero inválidos, cero duplicados, obligatorios informados); `09-sin-categoria` sale con `source="tables"` y `missing: category`, sin llamar al modelo.
- Caché: una segunda corrida del mismo SKU sale con `source="cache"`. Usa las tablas DynamoDB del stage `warroom` si están configuradas; si no, el almacén en memoria del mismo proceso.
- Correcciones: el test carga una corrección propia en DynamoDB para un caso, corre la V2, verifica que el valor corregido aparece en el `Listing` y borra la corrección y la caché de esa categoría al terminar, pase o falle.
- Se saltea con un motivo claro si no hay credenciales de AWS.

**Nivel 2 · el chat desplegado** (`core/tests/e2e/test_e2e_chat.py`):

- Toma la URL del BFF de `.sst/outputs.json` (o de `API_URL`) y el secreto de `CHAT_HMAC_SECRET` del `.env`.
- Firma un token igual que `apps/web/sign.mjs`, manda "Mapea el SKU 94701411 con la V2" con el mismo contrato que usa `apps/web` (`POST` y `GET /mensajes`) y espera la respuesta, con un tope de 120 segundos.
- Verifica que la respuesta nombra la categoría Calotas y que no es un error.
- Se saltea con un motivo claro si no hay URL del BFF o secreto.

Los tests e2e nunca imprimen secretos ni el token.

## Presentación

La V2 incluye adaptar el deck (`docs/warroom/diapositivas.json`, generado con `old/deck-tools/regenerar_deck.py` y `old/deck-tools/exportar_pdf.py`) para que cada lámina diga solo lo que existe.

- **Revisión completa:** las 58 láminas, una por una, contra el código, la infraestructura desplegada y los resultados de Langfuse. Cada comando que aparece tiene que existir y funcionar; cada número tiene que venir de una corrida identificada; cada decisión tiene que coincidir con lo construido.
- **Bloques:** los bloques "04 · V2 · herramientas" y "05 · V3 · control" se fusionan en "04 · V2 · tablas y control" (13:15 a 16:15), y la agenda de la lámina 2 pasa a cinco bloques.
- **Arquitectura:** el diagrama "El agente por dentro" se reemplaza por "La V2 por dentro" (steps `check_cache`, `resolve`, `run_agent` y `finalize`, las dos herramientas, DynamoDB y Langfuse). El diagrama de infraestructura suma las tablas `corrections` y `mapping_cache` y las herramientas `map_product_v1` y `map_product_v2`.
- **Código:** láminas que leen el código real de la V2: la worklist, `submit_listing`, `validate`, la clave de la caché, los steps del Workflow y un test e2e.
- **Pruebas:** una lámina "Cómo lo probamos" con los tres niveles: tests unitarios, experimentos en Langfuse y tests e2e, con sus comandos.
- **Demos:** la demo de la V2 y la de "corregir y repetir" usan `scripts/experiment.sh --version v2` y `scripts/correct.sh`; la demo del chat usa `map_product_v2`.
- **Números:** la tabla de resultados completa las columnas Hoy y V1 con las corridas del 1/10 y la columna V2 con su experimento; la lámina de costo usa los tokens de las trazas.
- **Decisiones:** las decisiones 10 a 13 y las tablas finales describen la V2 tal como quedó.
- **Texto:** el texto nuevo pasa por la skill humanizer: frases cortas, sin rayas, sin construcciones del tipo "no es X, es Y".
- **Verificación:** regenerar HTML, guion y PDF, y revisar en el navegador cada diagrama y cada lámina nueva.

## Fuera de alcance

Integración con la API de Alephee, esquema oficial de Shopee, política de revisión de `missing`, bloqueo de la publicación, más de un canal.

## Riesgos y pendientes

- `FunctionAgent` y la herramienta que valida lanzando excepción: verificar en la implementación que el error vuelve al modelo como texto y que `return_direct` solo corta con la entrega válida (en `llama-index-core` 0.14.24, `aggregate_tool_results` ignora las salidas `is_error` para `return_direct`).
- El doble del LLM para `FunctionAgent` tiene que ser una subclase de `FunctionCallingLLM` (el campo `llm` del agente es Pydantic).
- La salida esperada y el esquema de Shopee siguen siendo MOCK.
- Las tablas DynamoDB suman recursos al stage `warroom`; se borran con `npx sst remove --stage warroom`.
- Las herramientas del deck viven fuera de git (`old/deck-tools/`): si se pierden, se recuperan de la rama `backup/pre-reinicio`.
- Los tests e2e de nivel 2 dependen de que el deploy del stage `warroom` esté completo.
