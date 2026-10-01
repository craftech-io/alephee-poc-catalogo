# Revisión del warroom desde el lugar del oyente

Revisión del 28/09/2026. La propuesta tiene sentido: partir de un problema de catálogo, construir por capas y contrastar resultados. El principal ajuste es alinear lo que se promete con lo que se demuestra. Hoy la evidencia sostiene mejoras en controles específicos; todavía no demuestra una mejora global del mapeo ni una publicación aceptada por Shopee.

## Mejoras aplicadas después del diagnóstico

El 30/09 se rediseñó el deck como una cadena de 13 decisiones con el código del repositorio en pantalla y sin quizzes ni consignas en parejas; ver [diseno-presentacion.md](warroom/diseno-presentacion.md). El párrafo siguiente describe la versión del 29/09.

Se creó una [presentación local](presentacion-warroom.html), ampliada el 29/09 a 43 diapositivas en 7 secciones, con preguntas, respuestas revelables, temporizadores, notas y PDF estático actualizado. Se actualizó el guion y la entrada del README. El material usa un harness de desarrollo genérico y pasó dos revisiones editoriales independientes, documentadas en `warroom/revision-agentes.md`.

V3 ahora resuelve e impone la categoría desde la referencia antes de consultar al modelo; si falta referencia o esquema, devuelve la necesidad de revisión sin invocarlo. El validador rechaza nombres contradictorios con el ID del dominio, informa categoría ausente y elimina faltantes ya resueltos. La caché se revisa contra la categoría y el esquema antes de reutilizarla; aún necesita invalidación por cambios del producto y de las referencias de atributos.

El diagnóstico siguiente describe el estado anterior a estos cambios. Sus corridas y cifras se conservan como evidencia histórica, sin presentarlas como mediciones del código corregido. Se agregaron cinco tests de regresión y los 32 tests del catálogo pasan. Nueva corrida contra Bedrock pendiente.

## Alcance de esta revisión

Revisados: `CLAUDE.md`, README y estructura del proyecto; prompts originales; datos y generador de expectativas; implementación V1–V3, herramientas, memoria, evaluador y runner; corridas guardadas; integración pendiente del chat. También se leyeron el [temario de validación AWS](https://docs.google.com/document/d/1bZbFmeoRltffTDj9lr48_JAFz9lAlRVww5CunzLx-Vg/edit), el [borrador previo](https://docs.google.com/document/d/142WUJ5VZUFnG1h8cAmtV5Gegiy6BEKmHAS_EppAlKOg/edit) y las [notas y transcripción del checkpoint del 25/09](https://docs.google.com/document/d/1w7Pm0ODvm7_yAnhhPqh-N8B1TfMhptJsKguoisGVgkQ/edit).

No se encontró el archivo o enlace de la presentación de 16 diapositivas mencionada en `CLAUDE.md`, ni un guion independiente. Por tanto, esta revisión evalúa la narrativa disponible y propone un guion; no afirma haber revisado el diseño visual o las notas del deck original. No es una auditoría completa de la infraestructura heredada.

## Qué conservar

- El problema concreto de Alephee y ejemplos de errores observables.
- La distinción entre reglas de tablas y decisiones que requieren interpretación.
- El acuerdo de criterios antes de comparar resultados.
- Las versiones ejecutables y el registro de decisiones.
- El cierre con responsables y próximos pasos.

## Cambios prioritarios

| Prioridad | Lo que pensaría el oyente | Evidencia y ajuste |
|---|---|---|
| Alta | «¿Esto ya publica en Shopee?» | Se genera una propuesta local de categoría y atributos. No hay integración de escritura ni aceptación del canal demostrada. Usar “propuesta de mapeo” y mostrar faltantes y descartes. |
| Alta | «¿Cómo saben qué respuesta es correcta?» | Los productos y referencias son reales; el esquema del canal y `expected` son simulados y derivados parcialmente de las publicaciones actuales. Explicarlo antes de los resultados, en la misma diapositiva. Validar un subconjunto con catálogo y obtener el esquema oficial. |
| Alta | «¿Por qué V3 tiene menos categorías correctas que V2?» | V2 logra 30/30; V3, 28/30 en las corridas disponibles. Mostrarlo y tratarlo como regresión a resolver. No afirmar que cada versión mejora todas las dimensiones. |
| Alta | «Si la tabla manda, ¿por qué decide todavía el modelo?» | Los lookups son deterministas, pero el LLM elige invocarlos y redacta la salida final. No existe una imposición final de categoría contra la referencia. Separar el diseño objetivo de lo implementado. |
| Alta | «¿Cero inválidos significa cero inventos?» | El control verifica pertenencia al esquema cargado y al dominio por ID; no comprueba toda la evidencia del producto. Un ID permitido con texto contradictorio pasa. Decir “0 valores inválidos detectados por este evaluador en esta corrida”. |
| Alta | «¿Qué voy a hacer yo durante ocho horas?» | El temario enumera bloques técnicos, pero deja implícita la participación. Cada bloque debe pedir una decisión o una predicción concreta y terminar con una evidencia visible. |
| Media | «¿Empezamos de cero si ya hay tres versiones?» | Hay código preparado y tags V1–V3. Presentarlo como base preparada para experimentar y tomar decisiones juntos; evita fingir una construcción desde hoja en blanco. |
| Media | «¿Por qué vemos Calotas si los casos son otros?» | Los 30 casos abarcan 22 categorías y ninguno es de Calotas. Usar un producto del lote como hilo conductor. Si se conserva Calotas, presentarlo como ejemplo previo, separado del lote evaluado. |
| Media | «¿Aprende solo cuando alguien escribe en el chat?» | La memoria almacena correcciones cargadas explícitamente mediante CLI y una caché local. Cambiar “aprende del usuario” por “reutiliza correcciones registradas por catálogo”. |
| Media | «¿Cuánto ahorra?» | Hay tokens y tiempos del agente, pero no una comparación de costo completa y equivalente con el proceso actual. Presentar ahorro como hipótesis pendiente de medición. |
| Media | «¿El chat que veo es este agente?» | `core/server.py` no conecta `mapear_producto`; el mock mantiene ejemplos de Ciclos Aurora. La demo verificable del catálogo es batch. Integrar y ensayar el chat antes de incluirlo como recorrido principal. |
| Media | «¿Qué pasa si una demo falla?» | “Nunca avanzar con algo roto” puede bloquear la jornada. Diferenciar una ejecución rota de un resultado de negocio incorrecto. Preparar una corrida guardada identificada como tal y un límite de tiempo para reparar el entorno. |

## Resultados que se pueden mostrar

Se reevaluaron las cuatro salidas guardadas contra el mismo `expected` actual, sin llamar a Bedrock ni modificar las corridas originales.

**30 productos reales; esquema de validación y respuestas esperadas simulados. Categoría correcta significa coincidencia con la referencia adoptada, no certificación de Shopee.**

| Métrica | Publicaciones históricas | V1 | V2 | V3 |
|---|---:|---:|---:|---:|
| Casos exactos contra `expected` | 7/30 | 5/30 | 4/30 | 4/30 |
| Categorías coincidentes | 28/30 | 26/30 | 30/30 | 28/30 |
| Valores inválidos según evaluador | 47 | 19 | 9 | 0 |
| URN repetidos, sumados por caso | 5 | 0 | 0 | 0 |
| Faltantes esperados no informados | 2 | 2 | 0 | 0 |
| Precisión de atributos | 0,698 | 0,621 | 0,662 | 0,705 |
| Recall de atributos | 0,966 | 0,676 | 0,662 | 0,662 |
| Segundos medios por producto | No medido en esta prueba | 12,30 | 18,31 | 23,24 |

Archivos utilizados en `resultados/`: `actual-real-20260928-174021.json`, `v1-real-20260928-173758.json`, `v2-real-20260928-181509.json`, `v3-real-20260928-180524.json`.

La baseline de 9 exactos corresponde a una evaluación anterior: no mezclarla con los 7 de la expectativa actual. El resumen guardado de V1 informa 4 exactos; reevaluado hoy da 5. Mantener identificados dataset, evaluador, commit y corrida cuando se congelen los resultados.

La opción `--version actual` lee publicaciones exportadas: no vuelve a ejecutar el sistema de Alephee. Sus 0 segundos y 0 tokens son del replay local, no del proceso productivo. Los 13 segundos citados en contexto fueron informados en una reunión y no son una medición comparable.

El `expected` hereda omisiones del proceso actual. Puede penalizar atributos adicionales correctos y favorecer a la baseline. La precisión y el recall son provisionales; tampoco conviene descartarlos selectivamente porque no acompañen el relato. Un control puede reducir errores eliminando información: se deben mirar control y cobertura juntos.

Conclusión oral defendible: “En este ensayo, V3 elimina los errores que detectan estos controles, pero todavía no demuestra mejor exactitud global y deja dos categorías distintas de la referencia. Tenemos evidencia de qué controles ayudan y trabajo pendiente antes de validar con el canal”.

## Límites técnicos que afectan al relato

1. **La tabla aún no gobierna toda la salida por código.** En `v2.py` las reglas están en las instrucciones. En `v3.py` se valida contra la categoría entregada por el modelo, sin contrastarla con la categoría de referencia del producto. Los casos `publicados-24579729` y `publicados-42566753` muestran el desvío en V3. Prioridad: fijar la categoría mediante lookup antes del modelo y verificarla al entregar; aplicar el mismo principio a las correspondencias inequívocas de atributos.
2. **Validez de dominio no equivale a verdad.** `guardrails._problema` acepta un `valueId` existente aunque el texto diga otra cosa; no verifica procedencia del valor, unidades ni consistencia completa. Reproducción local: dominio `1 = Novo`, salida `1 = Usado` → ningún problema detectado. Con categoría nula y listas vacías, `limpiar` tampoco agrega por sí solo el faltante de categoría.
3. **Marcar `missing` no crea un circuito de revisión.** Existe la representación de faltantes, no una integración demostrada que bloquee publicación y asigne la revisión a una persona. Acordar la política en la sala y describir la integración como pendiente.
4. **La caché solo identifica SKU y categoría legacy.** Cambios del producto, tablas o esquema no forman parte de su clave; no hay aislamiento por canal/cuenta. Sirve para demostrar reutilización bajo datos fijos. Antes de ampliar el alcance, definir versión de insumos, invalidación y aislamiento. Además, el runner la habilita con `--cache`; no atribuirle beneficios a las corridas sin esa opción.
5. **Las correcciones también dependen de que el LLM consulte y respete la herramienta.** La persistencia existe; la aplicación obligatoria por código no está demostrada. Evitar prometer que toda corrección siempre prevalece.
6. **Seis rondas máximas no garantizan una entrega.** La última limita las herramientas, pero aún puede haber error de contrato, agotamiento o necesidad de corrección sin otra ronda disponible. Ensayar el camino de error y mostrarlo como resultado de ejecución.
7. **El costo requiere completar la medición.** Incluir entrada, salida, lectura y creación de caché, reintentos y tasa real de reutilización. El resumen del runner no agrega creación de caché aunque el adaptador la recoge por caso. No inferir dólares solo de la caída de tokens de entrada sin caché.

Se ejecutaron los tests existentes del catálogo: **27 pasaron**. Se reprodujeron los dos límites del validador arriba descritos con datos sintéticos y sin AWS. Esto valida comportamiento local; no valida el esquema oficial ni una publicación real. No se modificó la implementación durante esta revisión.

## Experiencia del participante

El hilo del día debería contestar, en orden: qué error queremos evitar, cómo sabremos si mejoramos, qué parte resuelve una regla, qué parte requiere interpretación, cuándo debemos detenernos y qué falta para usarlo.

Usar tres casos: uno correcto, uno con valor incompatible y uno con obligatorio ausente. Mantener el mismo caso principal entre versiones; el lote de 30 queda para comprobar si la mejora se generaliza dentro de la muestra. No recorrer treinta JSON en pantalla.

Dinámica acordada con Gastón el 29/09: una construcción compartida conducida por él, con ejercicios cortos en parejas para decidir, ejecutar casos y validar resultados. En cada bloque: mostrar entrada y resultado esperado; pedir una predicción; ejecutar; comparar; registrar una decisión. No se requiere rotar a quien programa ni que cada asistente construya un agente completo. Pedir aportes de quienes están remotos antes de cerrar decisiones. Las consignas están en el guion.

La teoría de agentes debe entrar después de que el grupo vea un error real. Explicar herramienta como una consulta a una fuente conocida, guardrail como una comprobación por código y memoria como correcciones persistidas o reutilización de un resultado. Diferenciar caché de resultados y caché de prompts.

## Ajustes del material antes de compartirlo

- El temario de Drive conserva “Miércoles 14 de octubre”; el contexto del repo fija jueves 1/10. Corregir también el horario y confirmar si 17:00 es cierre técnico y 17:30 fin del evento.
- Reemplazar “hoja en blanco”, “bot”, “guardials”, “para que sea agéntico” y “aprenda del usuario” por la conducta concreta que se verá.
- Resolver la duplicación entre “cuándo está bien hecho” y “criterios de éxito”; un solo acuerdo con calidad, cobertura y costo.
- Elegir explícitamente entre una familia en profundidad y el lote heterogéneo de 22 categorías. Propuesta: tres casos guiados y el lote como ensayo exploratorio.
- Poner almuerzo y pausas en agenda; reservar el cierre y el ensayo del lote, evitando que dependan del tiempo sobrante.
- Preparar una pantalla de resultados legible: dato de origen, propuesta, motivo y decisión. JSON y arquitectura completa en el apéndice.
- Actualizar el README de entrada para que Alephee encuentre primero el runner del catálogo y sus limitaciones. El README actual sigue describiendo el chatbot genérico.

La propuesta de diapositivas y notas para hablar está en [guion-warroom-propuesto.md](guion-warroom-propuesto.md). Es una propuesta nueva basada en el material revisado, pendiente de contrastar con el guion y el deck originales.
