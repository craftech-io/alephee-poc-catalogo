# Guion del warroom · por diapositiva

Versión del 29/09/2026 · 9 diapositivas · 7 secciones. Fuente única: `docs/warroom/diapositivas.json`. Se regenera con `python3 scripts/generar_presentacion.py`.

[Presentación interactiva](presentacion-warroom.html) · [PDF estático](presentacion-warroom.pdf) · [Ficha de participantes](warroom/ficha-participantes.md)

## Dinámica acordada

Gastón conduce una construcción compartida. En parejas, el equipo toma decisiones, ejecuta casos y valida resultados. No se exige programar un agente completo ni rotar a quien conduce. Si falla un entorno, la pareja dirige su prueba en la pantalla principal. Pedir devoluciones de participantes remotos.

Las selecciones, respuestas revelables y temporizadores son ayudas locales de facilitación. No reciben votos remotos ni ejecutan el agente. Las pruebas reales se corren en el repositorio. Los ejemplos DEMO-01 usan reglas e IDs inventados; los resultados históricos siguen rotulados como anteriores a las correcciones nuevas.

## Mapa y tiempos

| Sección | Horario | Diapositivas | Resultado |
|---|---|---|---|
| 01 · Punto de partida | 09:00–09:30 | 1–9 | Ver el error de hoy y acordar qué construimos |

Pausa 11:00–11:15; almuerzo 12:30–13:15; pausa 14:45–15:00. El bloque V3 incluye preparación de comparación 16:00–16:15. Margen de preguntas 17:00–17:30 sujeto a confirmación logística.

Los minutos por diapositiva son una pauta para explicaciones y consignas, no un cronograma adicional: el resto de cada bloque se dedica a construcción compartida, demos y discusión. Preservar la hora de cierre. Si falta tiempo, abreviar teoría ya comprendida y abrir las respuestas directamente; mantener prácticas y conclusiones.

## Distribución completa dentro de cada bloque

| Bloque | Diapositivas, consignas y demos | Trabajo reservado | Total |
|---|---:|---|---:|
| 01 · Punto de partida | 29 min | Dolores del equipo y preguntas: 10 min | 39 min |
| 02 · Diseñar el agente | 0 min | Pizarra: tipos de aplicación y dónde corre: 15 min; Pausa 11:00: 15 min | 30 min |
| 03 · V1 · el agente responde | 0 min | Corridas sobre otros casos: 25 min | 25 min |
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

## Fundamento editorial y revisión

Ver [revisión de los dos agentes](warroom/revision-agentes.md). Se aplican principios de claridad, audiencia y explicación de Garr Reynolds, Nancy Duarte y Lee LeFever; el número de diapositivas, los tiempos y las parejas son decisiones de esta sesión.
