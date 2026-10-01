"""Construye docs/warroom/diapositivas.json y decisiones/*.md a partir de literales Python.

El JSON sigue siendo la fuente que leen el generador y el PDF; este script es la forma cómoda de
editarlo sin escapar JSON a mano. `test_el_constructor_reproduce_el_json_commiteado` exige que ambos
coincidan: si se edita el JSON a mano, hay que reflejarlo acá (o borrar este script).

    python3 scripts/construir_diapositivas.py
"""
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]

SECTIONS = [
    {"id": "partida", "title": "01 · Punto de partida", "time": "09:00–09:30", "goal": "Ver el error de hoy y acordar qué construimos", "work_reserve": [["Dolores del equipo y preguntas", 2]]},
    {"id": "diseno", "title": "02 · Diseñar el agente", "time": "09:30–11:15", "goal": "Tomar las decisiones que definen la V1", "work_reserve": [["Pizarra: dudas de AgentCore para Juan David", 5], ["Pausa 11:00", 15]]},
    {"id": "v1", "title": "03 · V1 · el agente responde", "time": "11:15–12:30", "goal": "Construir, correr y leer la primera versión", "work_reserve": [["Corridas sobre otros casos", 25]]},
    {"id": "v2", "title": "04 · V2 · herramientas", "time": "13:15–14:45", "goal": "Decidir qué resuelve la tabla y conectarla", "work_reserve": [["Corrida del lote y lectura", 25]]},
    {"id": "v3", "title": "05 · V3 · control", "time": "15:00–16:15", "goal": "Decidir qué pasa cuando el agente no sabe", "work_reserve": [["Corrida del lote con V3", 20]]},
    {"id": "prueba", "title": "06 · La prueba y el camino", "time": "16:15–17:00", "goal": "Medir contra el criterio y repartir lo que sigue", "work_reserve": [["Documentar decisiones y responsables", 15]]},
]

SLIDES: list[dict] = []
MINUTOS = {"divider": 1, "code": 4, "decision": 4, "demo": 5}


def L(section, kind, title, lead="", label="", items=None, table=None, code=None, decision=None, demo=None,
      objective="", say="", ask="", close="", transition="", minutes=None):
    s = {
        "id": f"s{len(SLIDES) + 1:02d}", "section": section, "title": title, "kind": kind, "lead": lead, "label": label,
        "items": items or [], "question": "", "options": [], "answer": "", "exercise": None, "table": table,
        "notes": {"objective": objective or title, "say": say, "ask": ask, "close": close, "transition": transition},
        "minutes": minutes or MINUTOS.get(kind, 3),
    }
    if code: s["code"] = code
    if decision: s["decision"] = decision
    if demo: s["demo"] = demo
    SLIDES.append(s)


def D(number, question, options, proposal, slug):
    return {"number": number, "question": question, "options": options, "proposal": proposal, "file": f"decisiones/{number:02d}-{slug}.md"}


# ─────────────────────────── 01 · Punto de partida ───────────────────────────
L("partida", "divider", "Un agente que mapea el catálogo a Shopee, decidido paso a paso.",
  lead="War Room · Alephee × Craftech × AWS · 1/10/2026",
  objective="Qué tenemos a las 17:00: agente en local, método repetible, 13 decisiones documentadas",
  say="Después de esta portada: la agenda por temas y, con un producto real, qué entra y qué queremos que salga. A las 17:00 queremos tres cosas: el agente corriendo en local con el código en el repositorio, un método que se pueda repetir para el próximo caso de uso y trece decisiones escritas con su razonamiento. Hoy no se enseña teoría: se diseña y se construye en el orden en que se diseña. Gastón conduce; el grupo decide en cada punto.",
  transition="Lo que vamos a hacer hoy.")

L("partida", "compare", "Lo que vamos a hacer hoy.",
  lead="Decidimos → construimos → medimos. Cada bloque cierra con una versión que funciona.",
  items=["1 · PUNTO DE PARTIDA | El error de hoy, alcance y contrato",
         "2 · DISEÑAR EL AGENTE | Tipo de aplicación, prompt, dónde corre, modelo, stack y criterio de éxito",
         "3 · V1 · EL AGENTE RESPONDE | Solo instrucciones: qué falla y por qué",
         "4 · V2 · HERRAMIENTAS | Las tablas como herramientas, el loop y la caché de prompt",
         "5 · V3 · CONTROL | Guardrails, memoria y caché por SKU",
         "6 · LA PRUEBA | Hoy contra V1, V2 y V3, y el camino a producción"],
  objective="Ubicar al grupo en el recorrido del día, por temas",
  say="Seis bloques. Las decisiones de los dos primeros producen la V1; las de herramientas, la V2; las de control, la V3; y la prueba mide todo contra el criterio que acordamos antes de escribir código. Horarios para quien conduce: 09:00 punto de partida, 09:30 diseño, 11:15 V1, 13:15 V2, 15:00 V3, 16:15 prueba. Pausa a las 11:00, almuerzo 12:30 a 13:15, pausa 14:45. Cierre técnico 17:00 y preguntas hasta las 17:30.",
  transition="Un producto real para ver qué entra y qué queremos que salga.")

L("partida", "table", "De un producto de Alephee a una publicación de Shopee.",
  label="Caso real · SKU 88904447 · Correia dentada · catálogo GM Brasil (Mercado Libre Brasil) → Shopee Brasil",
  table={"headers": ["Entra (Alephee)", "Sale (Shopee)", "Quién lo resuelve"],
         "rows": [["Categoría: Correias Dentadas", "Distribuição e Correias", "La tabla"],
                  ["Condición del ítem: Novo", "Condition: New", "La tabla y la lista del canal"],
                  ["Tiempo de garantía: 6 meses", "Duração da Garantia: 6 Months", "El agente"],
                  ["Código OEM: no viene", "Faltante, con motivo (hoy: ABS Plastic, rechazado por Shopee)", "El guardrail"]]},
  objective="Que todos vean, con un producto real, qué entra y qué queremos que salga",
  say="Esto es lo que queremos lograr. Entra el producto como está en Alephee: los nombres de los atributos están en español porque así los define la plataforma; los valores y la categoría están en portugués porque el catálogo es de GM Brasil sobre la taxonomía de Mercado Libre Brasil. Sale la publicación para Shopee Brasil, que mezcla portugués e inglés según cómo expone cada atributo su API. Cruzar idiomas es parte del problema. Las tres primeras filas coinciden con lo que Alephee publicó hoy para este SKU (categoría 102278, Condition = New valueId 2497, 6 Months valueId 810); la cuarta es la conducta que queremos: hoy en Código OEM salió ABS Plastic y Shopee lo rechazó. La columna de la derecha anticipa el día: tabla, agente, guardrail. El esquema de atributos de Shopee con el que validamos es MOCK derivado de estas publicaciones.",
  ask="¿Qué fila les parece la más difícil de automatizar?",
  transition="Cómo lo hace hoy el proceso actual.")

L("partida", "cards", "Hoy: dos llamadas, un merge y un presupuesto que se agota.",
  items=["Categoría: la tabla reference_category y, si no alcanza, el modelo elige",
         "Atributos: dos llamadas en paralelo (con y sin referencia) y un merge por código",
         "USD 350 por mes: cuando se agota, se publica sin atributos"],
  objective="Entender el proceso actual sin juzgarlo",
  say="Describir el flujo actual tal como lo explicó Maximiliano: la categoría se resuelve por tabla y el modelo entra cuando la tabla no la tiene; los atributos van en dos llamadas en paralelo porque un solo prompt era demasiado largo, y un merge por código prioriza la que usó la referencia. Latencia de 13 segundos en batch: no es una restricción. El punto que duele es el presupuesto: cuando se agota, la publicación sale sin atributos. El modelo exacto y sus parámetros siguen sin confirmar.",
  ask="¿Qué parte de este flujo les da más trabajo hoy?",
  close="Anotar las respuestas en la pizarra: se retoman en la prueba final.",
  transition="Veamos cómo se le pide hoy la categoría al modelo.")

L("partida", "code", "Así se pide hoy la categoría.",
  label="Prompt actual de Alephee · inputs/prompts-actuales/index.ts",
  code={"file": "inputs/prompts-actuales/index.ts", "lines": "4-21", "symbol": "categoryPrompt", "highlight": [20, 21],
        "caption": "Reglas correctas (no inventar, copiar el URN exacto). Lo que se va a revisar: el JSON se pide en el texto y la lista completa de categorías viaja en cada llamada."},
  minutes=3,
  objective="Leer juntos el prompt actual y separar lo que se conserva de lo que se cambia",
  say="Leer las reglas resaltadas: son buenas y se conservan. Señalar tres cosas que vamos a decidir distinto a lo largo del día: la salida es JSON pedido por favor en el texto (decisión 4), la lista completa de categorías viaja en cada llamada y después del producto (decisión sobre caché, bloque V2), y solo usa el nombre de la categoría y del producto, no la descripción. No es una crítica al equipo: es el punto de partida.",
  transition="Qué pasó con esas publicaciones en Shopee.")

L("partida", "table", "Lo que Shopee rechazó y lo que aceptó mal.",
  label="Datos reales · WarRoom.zip del 24/09 · 30 productos",
  table={"headers": ["Caso", "Qué salió", "Qué pasó"],
         "rows": [["88904447", "Código OEM = ABS Plastic", "Rechazado: el valor no pertenece al atributo"],
                  ["93221445", "Inmetro Certification con varios valores", "Rechazado: solo admite un valor"],
                  ["9 de 30", "Valor -1 publicado como valor", "Aceptado por Shopee"],
                  ["98550368", "14 de 15 URN sin sufijo del canal", "Aceptado por Shopee"]]},
  objective="Ver errores reales: los que rechaza el canal y los que acepta igual",
  say="Los 30 productos del zip: 20 publicados y 10 rechazados. El caso 88904447 es el hilo del día: un material (ABS Plastic) copiado al campo Código OEM, que Shopee rechazó porque el valor no está vinculado a ese atributo. El 24581199 publicó Quantity diez veces y Shopee no lo mencionó: lo rechazó por otro obligatorio (Auto-Part Number). Lo peor no es lo que Shopee rechaza, que al menos avisa, sino lo que acepta mal: un -1 publicado como valor en 9 de 30 y URN sin el sufijo del canal. Nadie se entera hasta que un comprador lo ve.",
  ask="¿Cuál de estos errores les parece más grave para el negocio?",
  transition="Cómo vamos a trabajar hoy.")

L("partida", "decision", "¿Qué hace y qué no hace?",
  decision=D(1, "¿Qué alcance tiene el agente del war room?",
             ["A · Un canal (Shopee) y una familia de productos: categoría + atributos",
              "B · Todos los canales conectados (Shopee, Magalu, Tienda Nube…)",
              "C · También título, descripción y marca"],
             "A. Un canal y una familia alcanzan para decidir el método y medirlo. Los prompts de marca, título y descripción son generación libre, no mapeo: quedan fuera. Los otros canales replican el mismo diseño con sus propias tablas.",
             "alcance"),
  minutes=3,
  objective="Cerrar la decisión 1 antes de hablar de contrato",
  say="Presentar las tres opciones con su consecuencia: B multiplica las tablas y los esquemas de canal sin cambiar el método; C mezcla dos problemas distintos, mapear y redactar. Abrir la propuesta solo después de escuchar al grupo. La decisión queda en decisiones/01-alcance.md con su razonamiento.",
  ask="¿Hay alguna familia de productos que convenga más que otra para empezar?",
  close="Registrar la decisión y la familia elegida.",
  transition="Si el alcance es ese, ¿qué entra y qué sale?")

L("partida", "cards", "Entra un producto. Sale una propuesta de publicación.",
  items=["Entrada: el producto de Alephee (SKU, nombre, descripción, categoría legacy, atributos)",
         "Salida: la categoría de Shopee más los atributos con URN, valueId y valor",
         "Y dos listas más: missing (obligatorios sin dato) y rejected (atributos descartados, con motivo)"],
  objective="Decir el contrato en palabras antes de verlo en código",
  say="La salida no es la publicación final: es una propuesta de mapeo. Lo que hoy no existe son las dos listas: qué obligatorio quedó sin dato y por qué, y qué atributo del producto se descartó y por qué. Eso es lo que reemplaza al publicar sin atributos.",
  transition="El mismo contrato, en código.")

L("partida", "code", "El contrato, en código.",
  code={"file": "core/src/catalogo/modelos.py", "lines": "21-37", "symbol": "class Publicacion", "highlight": [31, 34, 36, 37],
        "caption": "Pydantic con extra=\"forbid\": ningún campo fuera del contrato pasa. Los nombres (valueId, legacyId) son los del formato de publicación de Alephee para no traducir."},
  minutes=3,
  objective="Mostrar que el contrato es código que se valida, no un acuerdo verbal",
  say="Recorrer las cuatro partes: category puede ser null si no se resuelve; attributes lleva URN, valueId y value; missing y rejected llevan el motivo. extra=forbid significa que si el modelo agrega un campo que no existe, la salida se rechaza. Este archivo es lo primero que se escribió y lo último que debería cambiar.",
  transition="Decisión 2: cómo se informa lo que no se pudo mapear.")

L("partida", "decision", "¿Qué recibe y qué entrega?",
  decision=D(2, "¿Cómo se informa lo que no se pudo mapear?",
             ["A · No se informa: se publica lo que hay (hoy)",
              "B · missing y rejected con motivo, en la misma salida",
              "C · Un archivo de log aparte que alguien revisa"],
             "B. El faltante viaja con la publicación: quien revisa ve el producto, el atributo y el motivo juntos. Un log aparte se separa del dato y nadie lo mira. La decisión 12 define qué pasa después con esas listas.",
             "contrato"),
  minutes=3,
  objective="Cerrar la decisión 2",
  say="La opción A es el estado actual y su costo ya lo vimos en la tabla de rechazos. La B obliga a que alguien reciba esas listas: quién y cómo es la integración con la plataforma de Alephee, que se trata en el camino a producción. Registrar en decisiones/02-contrato.md.",
  transition="Con alcance y contrato cerrados, diseñamos el agente.")


# ─────────────────────────── 02 · Diseñar el agente ───────────────────────────
L("diseno", "divider", "Diseñar antes de escribir.",
  lead="Siete decisiones que definen la V1",
  objective="Abrir el bloque de diseño",
  say="En este bloque no se corre nada. Se toman las decisiones que la V1 va a implementar a las 11:15: qué tipo de aplicación, cómo se escribe el prompt, dónde corre, qué modelo, con qué stack y cómo se mide. Cada decisión tiene opciones con consecuencias y se cierra antes de pasar a la siguiente.",
  transition="Primero, qué tipos de aplicación existen.")

L("diseno", "compare", "Cuatro formas de usar un modelo.",
  items=["SINGLE PROMPT | Una llamada, una respuesta. Barato y fácil de evaluar; no consulta nada",
         "WORKFLOW | Pasos fijos en código; el modelo participa en uno o dos. Predecible",
         "AGENTE | El modelo decide qué herramienta pedir y cuándo entregar, dentro de un límite de rondas",
         "MULTIAGENTE | Varios agentes con roles distintos. Solo cuando uno no alcanza"],
  objective="Distinguir single prompt, workflow, agente y multiagente",
  say="El proceso actual de Alephee es un workflow: dos llamadas fijas y un merge en código. Un agente se diferencia en que el modelo elige qué consultar y cuándo terminar; el programa le pone el límite. Multiagente es la última opción, no la primera: cada agente extra suma latencia, costo y puntos de fallo.",
  ask="¿El flujo de hoy es single prompt, workflow o agente?",
  close="Workflow: las llamadas y el merge están fijos en código.",
  transition="Las tres versiones del día conviven en el mismo runner.")

L("diseno", "code", "Las tres versiones conviven en el mismo runner.",
  code={"file": "core/src/catalogo/correr.py", "lines": "24-27", "symbol": "_versiones",
        "caption": "Cada versión es un Workflow que recibe MapeoStart y devuelve MapeoDone. Se comparan sobre el mismo dataset con el mismo evaluador."},
  objective="Mostrar que V1, V2 y V3 son intercambiables y comparables",
  say="Lo único que cambia entre versiones es la clase. El runner, el dataset y el evaluador son los mismos: así la comparación de la tarde es justa. Sumar una V4 es registrar una clase más.",
  transition="Decisión 3.")

L("diseno", "decision", "¿Single prompt o agente?",
  label="La opción A ya está en la base preparada (V1) · si gana otra, se discute qué cambia",
  decision=D(3, "¿Con qué tipo de aplicación empezamos?",
             ["A · Single prompt (V1) y agregar herramientas solo cuando un fallo lo justifique",
              "B · Agente con herramientas desde el inicio",
              "C · Workflow determinista sin modelo"],
             "A. La V1 muestra qué resuelve el modelo solo y qué no; cada fallo justifica la capa siguiente y queda documentado. C no alcanza: elegir el valor de lista equivalente (por ejemplo, '1' → Sim) necesita interpretación.",
             "tipo-de-aplicacion"),
  objective="Cerrar la decisión 3",
  say="B es tentador porque ya sabemos que vamos a necesitar herramientas, pero nos quita la evidencia de por qué. C es la pregunta que siempre hay que hacerse: ¿hace falta un modelo? Para la categoría y los campos mapeados por tabla, no; para elegir el valor equivalente de una lista, sí.",
  transition="Si empezamos por un prompt, veamos de qué está hecho.")

L("diseno", "flow", "Un prompt tiene cinco partes.",
  items=["Rol: quién es", "Tarea: qué hace y con qué entrada", "Reglas: qué nunca hace", "Formato: cómo entrega", "Cuando falta dato: qué hace"],
  objective="Dar un esqueleto para leer cualquier prompt",
  say="Las cinco partes sirven para leer el prompt actual y el nuevo. La quinta es la que casi siempre falta: qué hacer cuando no hay dato. Si el prompt no lo dice, el modelo elige por su cuenta, y lo que elige es completar.",
  transition="El prompt de la V1, parte por parte.")

L("diseno", "code", "El prompt de la V1.",
  code={"file": "core/src/catalogo/v1.py", "lines": "22-39", "symbol": "INSTRUCCIONES", "highlight": [28, 32, 34],
        "caption": "Rol, tarea, reglas negativas explícitas (nunca inventes) y qué hacer cuando falta (missing con motivo). Comparar con el prompt actual de la lámina 5."},
  objective="Leer el prompt nuevo con el esqueleto de cinco partes",
  say="Rol en la primera línea; tarea en la segunda; reglas en la lista; el formato no está en el texto porque lo impone la herramienta de entrega (siguiente decisión); y la quinta parte está en las dos reglas de missing y rejected. Las reglas resaltadas son las que el proceso actual no tiene escritas.",
  ask="¿Qué regla agregarían con lo que saben del catálogo?",
  transition="Tres prácticas que cambian el resultado.")

L("diseno", "cards", "Buenas prácticas que cambian el resultado.",
  items=["Lo estático primero y lo variable al final: habilita la caché de prompt (F4, F7)",
         "Salida estructurada por esquema, no JSON pedido en el texto",
         "Decir qué hacer cuando no sabe, no solo qué hacer"],
  objective="Tres prácticas con efecto medible",
  say="La primera tiene efecto directo en costo: Bedrock cachea el prefijo estable del prompt con cachePoint (F4, mínimo 1.024 tokens para Claude Sonnet 5) y OpenAI hace lo mismo de forma automática sobre el prefijo (F7). El prompt actual pone el producto antes de la lista de categorías: el prefijo cambia en cada llamada y no se cachea nada. Reordenarlo ya bajaría el costo sin cambiar de proveedor; hay que medirlo, no darlo por hecho. Fuentes en docs/warroom/fuentes.md.",
  transition="La segunda práctica, en código.")

L("diseno", "code", "La salida es una herramienta con esquema.",
  code={"file": "core/src/catalogo/v1.py", "lines": "41-51", "symbol": "HERRAMIENTA_SALIDA", "highlight": [50],
        "caption": "fn_schema=Publicacion: el modelo solo puede entregar algo que cumpla el contrato. La función nunca se ejecuta; el resultado se lee de la llamada."},
  objective="Mostrar cómo el formato pasa de regla del prompt a contrato",
  say="En vez de pedir JSON válido en el texto, se le da al modelo una herramienta cuyo esquema es la clase Publicacion. El modelo entrega llamando a la herramienta; si lo que entrega no cumple el esquema, falla la validación y se informa el error en vez de publicar algo a medias.",
  transition="Decisión 4.")

L("diseno", "decision", "¿Cómo garantizamos el formato?",
  label="La opción B ya está en la base preparada · si gana otra, se discute qué cambia",
  decision=D(4, "¿Cómo se garantiza que la salida cumpla el contrato?",
             ["A · Pedir JSON en el texto y parsear (hoy)",
              "B · Herramienta con esquema Pydantic: la entrega es una llamada tipada",
              "C · Post-procesar la respuesta con expresiones regulares"],
             "B. El formato deja de ser una regla del prompt y pasa a ser un contrato que el modelo no puede violar. C arregla síntomas: si el modelo omite un campo, la regex no lo inventa.",
             "salida-estructurada"),
  objective="Cerrar la decisión 4",
  say="Preguntar al grupo cuántas veces tuvieron que arreglar un JSON mal formado. La opción B existe en todos los proveedores grandes (tool calling o salida estructurada); no depende de Bedrock.",
  transition="Ahora, dónde va a correr.")

L("diseno", "compare", "Dónde corre: AgentCore o contenedor propio.",
  label="Fuentes F1–F3b en docs/warroom/fuentes.md",
  items=["AGENTCORE RESUELVE | Runtime sin servidores, identidad, memoria, gateway de herramientas y observabilidad, como servicios separados que se usan juntos o no (F2)",
         "DUDAS | Arranque en frío sin cifra publicada, sesiones que terminan a los 15 min de inactividad y 8 h máximo (F3b), costo por CPU y memoria de la sesión (F3), región disponible",
         "ALTERNATIVA | Contenedor o Lambda propios: más control y más trabajo de operación; el agente es el mismo"],
  objective="Presentar AgentCore con sus beneficios y sus dudas, con fuente",
  say="AgentCore Runtime corre el contenedor del agente en una microVM por sesión y cobra por el CPU y la memoria que consume la sesión; el CPU baja a cero mientras espera al modelo (F3). Para un chat eso es ideal. Para un batch de miles de productos la pregunta es otra: ¿conviene una sesión larga en el Runtime o un proceso propio de Alephee que llame a Bedrock? No hay cifra pública de arranque en frío; se mide. Las dudas que no se resuelvan hoy van a Juan David.",
  ask="¿El batch de Alephee tiene horario fijo o corre continuo?",
  transition="El contrato con AgentCore son dos rutas HTTP.")

L("diseno", "code", "El contrato con AgentCore son dos rutas.",
  code={"file": "core/server.py", "lines": "194-199", "symbol": "invocations",
        "caption": "Las dos rutas que exige AgentCore (F1: puerto 8080, imagen ARM64). Hoy este servidor arma el chat del template; conectar el workflow de catálogo (mapear_producto) es un pendiente."},
  objective="Mostrar que el contrato de despliegue es mínimo y está separado del agente",
  say="Esto es todo lo que AgentCore exige del contenedor (F1): un GET de salud y un POST de invocación. Lo que se ve es el servidor del template, que hoy corre el ChatWorkflow del chat; el agente de catálogo corre por el runner batch y todavía no está conectado al chat. El punto: la lógica del agente vive en otro módulo y se prueba sin servidor; el contrato de despliegue no la condiciona.",
  transition="Y la infraestructura que lo declara.")

L("diseno", "code", "La infraestructura declara el Runtime.",
  code={"file": "infra/sst/runtime.ts", "lines": "389-406", "symbol": "bedrockagentcore.Runtime", "highlight": [402, 405, 406],
        "caption": "Imagen ARM64 referenciada por digest, red pública y un rol propio. Se despliega con SST; el modelo llega por variable de entorno."},
  objective="Ver que el despliegue es código y se repite",
  say="Infraestructura como código: el Runtime, su imagen y su rol se declaran acá y se despliegan con un comando. El comentario sobre el digest es una lección aprendida: la validación acepta una referencia que la microVM después no puede resolver. Esto ya está probado en el template de Craftech; para Alephee cambia el slug y la cuenta.",
  transition="Decisión 5.")

L("diseno", "decision", "¿Dónde corre?",
  decision=D(5, "¿Dónde corre el agente?",
             ["A · Hoy en local; el chat de demo en AgentCore; el batch como proceso de Alephee, a decidir con el camino a producción",
              "B · Todo en AgentCore desde el inicio",
              "C · Todo en la infraestructura actual de Alephee"],
             "A. Hoy se construye y se mide en local. El chat va a AgentCore porque es su caso natural. Para el batch hace falta medir sesiones, costo y arranque antes de decidir; se retoma a las 16:15.",
             "donde-corre"),
  objective="Cerrar la decisión 5 dejando el batch como pregunta abierta con dueño",
  say="No forzar la decisión del batch sin datos: anotar qué medir (duración de una corrida de 30 y de 1.000 productos, costo de sesión, arranque) y quién lo mide.",
  transition="Siguiente: cómo elegir el modelo.")

L("diseno", "cards", "Elegir el modelo: qué pesa en este caso.",
  items=["Seguir reglas y usar herramientas sin inventar: es lo que más falla hoy",
         "Costo por token con caché de prompt: el presupuesto actual es de USD 350 por mes",
         "Latencia: no es restricción (hoy el batch tarda 13 s por producto)",
         "Disponible en la región y habilitado en la cuenta"],
  objective="Criterios de elección antes de nombrar modelos",
  say="El orden importa: primero calidad en lo que falla hoy (alucinar valores, ignorar reglas), después costo con caché, y la latencia al final porque es batch. Un modelo más chico puede ganar en costo y perder en reglas: se decide midiendo sobre el dataset, no por intuición.",
  transition="Qué hay disponible en Bedrock.")

L("diseno", "table", "Qué hay en Bedrock.",
  label="Fuente F6 · Models at a glance · verificado el 30/09/2026",
  table={"headers": ["Proveedor", "Familias", "Para este caso"],
         "rows": [["Anthropic", "Claude 5.x (Sonnet 5.5, Opus 5.5, Fable 5.1, Sonnet 5…), 4.x (Haiku 4.5…), 3.x", "Candidato principal: reglas y tool calling. Sonnet 5 elegido el 25/09; 5.5 y Haiku 4.5 a comparar"],
                  ["Amazon", "Nova 2 Lite, Nova Premier, Pro, Lite, Micro", "Alternativa de costo a medir"],
                  ["OpenAI", "GPT-5.x, GPT-6, GPT OSS", "Continuidad con el proveedor actual, dentro de AWS"],
                  ["Meta · Mistral · DeepSeek · Qwen · otros", "Llama 3.x y 4, Mistral Large 3, DeepSeek V3.2, Qwen3…", "Abiertos; evaluar si el costo lo justifica"]]},
  objective="Mostrar el catálogo real de Bedrock sin inventar modelos",
  say="La tabla sale de la página oficial Models at a glance del 30/09 (F6). No es una recomendación de cada uno: es el menú. Lo que importa para elegir es la columna de la derecha y el criterio de la lámina anterior. La disponibilidad por región y la habilitación en la cuenta se verifican en la cuenta que usemos.",
  transition="El módulo que habla con Bedrock.")

L("diseno", "code", "El único módulo que sabe de Bedrock.",
  code={"file": "core/src/catalogo/llm.py", "lines": "7-21", "symbol": "crear_llm", "highlight": [9, 19, 20],
        "caption": "Inference profile us.: sin prefijo, Bedrock responde ValidationException por falta de throughput on-demand (F5). Caché de system y tools activada en el cliente."},
  objective="Mostrar dónde se elige el modelo y por qué el ID lleva prefijo",
  say="El modelo se elige en un solo lugar y llega por variable de entorno. El prefijo us. es un inference profile: Bedrock enruta entre regiones de Estados Unidos y es obligatorio para algunos modelos (F5). Las dos banderas de caché activan los cachePoint en system y tools (F4). Cambiar de modelo es cambiar una variable y volver a correr el dataset.",
  transition="Decisión 6.")

L("diseno", "decision", "¿Qué modelo?",
  label="Tomada el 25/09 (CLAUDE.md, decisión 6) · hoy se valida o se cambia",
  decision=D(6, "¿Con qué modelo construimos y medimos?",
             ["A · Claude Sonnet 5 en Bedrock, vía Converse",
              "B · Un modelo más chico y barato (Claude Haiku 4.5) y medir",
              "C · Seguir con OpenAI y solo reordenar el prompt para la caché"],
             "A para construir hoy: es la decisión del 25/09 y el ID está verificado en Converse. Claude Sonnet 5.5 también está en Bedrock (F6): compararlo, junto con Haiku 4.5 (B), es una corrida más con otra variable de entorno y queda como pendiente con dueño. C mejora el costo pero no resuelve herramientas, contrato ni control.",
             "modelo"),
  objective="Cerrar la decisión 6 con la prueba de Haiku como pendiente",
  say="Lo primero que van a preguntar: por qué Sonnet 5 y no 5.5. Respuesta honesta: la decisión es del 25/09 y el modelo está probado en este repo; 5.5 se compara sobre el mismo dataset, no se adopta a ciegas. Anotar las pruebas de 5.5 y de Haiku 4.5 como tareas con dueño. Si Alephee quiere continuidad con OpenAI, los GPT también están en Bedrock (F6): la arquitectura no cambia.",
  transition="Con qué lo construimos.")

L("diseno", "cards", "Stack y harness.",
  items=["Python + LlamaIndex Workflows: pasos, eventos y herramientas ya resueltos",
         "BedrockConverse: tool calling y caché de prompt sin código propio",
         "Harness de desarrollo: propone cambios en el código; Gastón los revisa y corre los tests"],
  objective="Separar el stack del agente de la herramienta con la que lo construimos",
  say="Dos cosas distintas: el stack con el que corre el agente (Python, LlamaIndex, Bedrock) y el harness con el que lo construimos hoy, un entorno de desarrollo asistido por un modelo que propone cambios. El harness no es el agente ni decide nada: cada cambio que propone pasa por revisión y por los tests. No depende de un proveedor concreto.",
  ask="¿Qué revisarían antes de aceptar un cambio propuesto por el harness?",
  close="Que resuelva la regla acordada, que pase los tests y que no toque datos reales.",
  transition="Un Workflow de un paso, en código.")

L("diseno", "code", "Un Workflow de un paso.",
  code={"file": "core/src/catalogo/v1.py", "lines": "76-83", "symbol": "class MapeoV1", "highlight": [77, 82],
        "caption": "El LLM se inyecta: en los tests es un doble, en producción es Bedrock. El workflow no sabe de proveedores."},
  objective="Mostrar el patrón de inyección que hace testeable al agente",
  say="La clase recibe el LLM por el constructor. Eso permite probar cada paso con un doble sin AWS y correr contra Bedrock cambiando una línea. Es el patrón que se repite en V2 y V3.",
  transition="Decisión 7.")

L("diseno", "decision", "¿Con qué lo construimos?",
  label="Tomada el 28/09 (CLAUDE.md, decisión 9) · hoy se valida",
  decision=D(7, "¿Qué stack usamos para el agente?",
             ["A · Python + LlamaIndex Workflows + BedrockConverse",
              "B · Llamadas directas al SDK, sin framework (como hoy)",
              "C · Otro framework de agentes (Strands, LangGraph…)"],
             "A. Es el stack del template que Craftech ya opera: el workflow no conoce Bedrock y cada paso se prueba con dobles. B repite el código de loop, herramientas y caché que un framework ya trae. C es válido; se elige A por continuidad con lo que ya está probado.",
             "stack"),
  objective="Cerrar la decisión 7",
  say="Dejar claro que la decisión es de continuidad, no de superioridad: AgentCore funciona con cualquier framework (F2). Lo que no se negocia es el patrón: LLM inyectado y pasos testeables.",
  transition="Última decisión antes de construir: cómo sabemos si está bien hecho.")

L("diseno", "cards", "¿Cuándo está bien hecho?",
  label="Esquema de Shopee y salida esperada MOCK · validar con el equipo de catálogo",
  items=["Exacto: categoría correcta, ni sobra ni falta atributo, nada fuera de dominio, sin duplicados y faltantes informados",
         "Además se reportan precisión y recall de atributos, valores inválidos, tokens y segundos",
         "Dataset: 30 productos reales con su publicación actual; el esquema de atributos de Shopee y el expected son simulados"],
  objective="Acordar la métrica antes de escribir código",
  say="La vara es estricta a propósito. Pero el expected es mock: se construyó a partir de la publicación actual limpia, así que hereda sus omisiones y castiga aciertos que hoy nadie mapea. Por eso los exactos van a ser bajos en todas las versiones y hay que leer también inválidos, duplicados y faltantes. El esquema oficial de Shopee y la validación con catálogo son pendientes.",
  transition="La métrica, en código.")

L("diseno", "code", "La métrica en código.",
  code={"file": "core/src/catalogo/evaluacion.py", "lines": "24-34", "symbol": "exacto", "highlight": [27, 30, 31],
        "caption": "Un caso es exacto solo si todo se cumple a la vez. Es determinista: no llama a ningún modelo."},
  objective="Mostrar que la métrica es código que todos pueden leer y discutir",
  say="Siete condiciones en un and. Si alguien discute la vara, se discute acá y se vuelve a evaluar sin llamar al modelo (scripts/reevaluar.py). La evaluación no cambia para favorecer a una versión.",
  transition="Decisiones 8 y 9.")

L("diseno", "decision", "¿Cuál es el número que aceptamos?",
  decision=D(8, "¿Qué criterio de éxito acordamos para la prueba de las 16:15?",
             ["A · Cero valores inválidos, cero duplicados y todo obligatorio informado en los 30; los exactos se reportan pero no son condición hasta validar el expected con catálogo",
              "B · Exactos iguales o mayores al 80 %",
              "C · Solo precisión y recall de atributos"],
             "A. Con expected mock, 'exacto' castiga aciertos que hoy nadie mapea: el 28/09 el proceso actual dio 7 y las versiones 5, 4 y 4. Los inválidos, duplicados y obligatorios sin informar sí son errores seguros y hoy hay 47, 5 y 2. El número final se fija en la sala.",
             "criterio-de-exito"),
  objective="Cerrar la decisión 8 con un número escrito",
  say="Escribir el número en la pizarra antes de la V1. Si el grupo quiere exigir exactos (B), advertir que con el expected mock ninguna versión los supera, incluida la actual (7 de 30), y que el 28/09 las versiones dieron 5, 4 y 4: la prueba quedaría planteada para fallar por la vara, no por el agente.",
  transition="Y con qué datos.")

L("diseno", "decision", "¿Con qué dataset?",
  decision=D(9, "¿Sobre qué datos construimos y medimos?",
             ["A · Los 30 reales del zip, con esquema y expected mock rotulados",
              "B · Solo los 10 casos mock de borde",
              "C · Esperar el esquema oficial de Shopee para empezar"],
             "A. Son productos reales con publicaciones reales y rechazos reales de Shopee. Lo simulado queda rotulado y se valida con catálogo después. Los 10 mock quedan como tests de borde.",
             "dataset"),
  objective="Cerrar la decisión 9 y pasar a construir",
  say="Pedir al grupo que elija el caso guía para las demos (propuesta: 88904447, el del Código OEM). Pausa de 11:00; a las 11:15 se construye la V1 con todo lo decidido.",
  transition="Pausa. Volvemos con la V1.")


# ─────────────────────────── 03 · V1 ───────────────────────────
L("v1", "divider", "V1 · el agente responde.",
  lead="Solo instrucciones. Se espera que falle, y esos fallos justifican lo que sigue.",
  objective="Abrir la V1 con la expectativa correcta",
  say="La V1 implementa las decisiones 1 a 9: single prompt, salida por herramienta con esquema, Claude Sonnet 5 por Converse, LlamaIndex Workflows, medida con el evaluador sobre los 30 reales. No usa las tablas de referencia a propósito: queremos ver qué resuelve el modelo solo. Recordar la regla del día: no se pasa al bloque siguiente con algo roto, pero un resultado de negocio incorrecto no es algo roto, es evidencia.",
  transition="El paso único de la V1.")

L("v1", "code", "Una llamada, una entrega.",
  code={"file": "core/src/catalogo/v1.py", "lines": "83-100", "symbol": "async def mapear", "highlight": [88, 97, 99],
        "caption": "tool_required=True: el modelo tiene que entregar por la herramienta. Si no la llama o la entrega no cumple el contrato, se informa el error; nunca se publica a medias."},
  objective="Recorrer el paso completo: mensaje, llamada, tool call, validación",
  say="Cuatro momentos: se arma el mensaje con el producto y el contexto del canal; una sola llamada al modelo con la herramienta de entrega obligatoria; se buscan las llamadas a entregar_publicacion; se valida contra Publicacion. Las dos salidas de error (no llamó, salida fuera de contrato) son resultados, no excepciones: el runner las cuenta. Lo que no está acá: ninguna tabla, ninguna consulta. Todo lo que el modelo sabe del canal viaja en el mensaje.",
  ask="¿Qué pasa si el modelo responde con texto en vez de llamar a la herramienta?",
  close="MapeoDone con error explícito. El caso cuenta como no entregado, no como publicado.",
  transition="Lo corremos sobre el caso guía.")

L("v1", "demo", "Demo · un caso real por V1.",
  demo={"command": "scripts/correr.sh --version v1 --datos real --caso error-88904447",
        "watch": ["La categoría elegida frente a la de reference_category",
                  "Cada atributo: ¿de dónde salió el valor? ¿Está en la lista del canal?",
                  "missing y rejected: ¿informa lo que no pudo o completó igual?",
                  "Tokens de entrada: todo el contexto del canal viaja en cada llamada"],
        "fallback": "resultados/v1-real-20260928-173758.json (corrida del 28/09, anterior a las correcciones)"},
  objective="Ver una salida real y leerla con el contrato en la mano",
  say="Antes de correr, pedir una predicción: ¿qué va a poner en Código OEM? Correr y leer la salida en el orden de la lista. Si Bedrock no responde (sesión SSO vencida, throttling), abrir la corrida guardada y decirlo: es una corrida vieja, anterior a las correcciones del 28/09. Después, el lote completo corre en segundo plano mientras seguimos.",
  transition="Qué falló y qué capa lo resuelve.")

L("v1", "table", "Qué falló en V1 y qué capa lo resuelve.",
  label="Corrida del 28/09 · 30 reales (fila 1: caso MOCK 09) · anterior a las correcciones · expected MOCK",
  table={"headers": ["Fallo", "Dónde se vio", "Capa que lo resuelve"],
         "rows": [["Categoría inventada cuando no hay referencia", "Caso mock 09 (sin categoría de origen)", "V2 · la tabla por herramienta"],
                  ["Valor fuera de la lista del canal", "19 valores en los 30 reales", "V3 · guardrail"],
                  ["Obligatorio sin informar en missing", "2 casos en los 30 reales", "V3 · guardrail"],
                  ["~22.000 tokens de entrada por producto", "Todos los casos", "V2 · herramientas + caché de prompt"]]},
  objective="Convertir cada fallo de la V1 en la justificación de una capa",
  say="Esto es lo que la V1 compra: evidencia. La categoría inventada es el fallo que justifica la V2: sin referencia, la respuesta tiene que ser determinista, no creativa. Los valores fuera de lista y los obligatorios sin informar justifican la V3: una regla escrita en el prompt no garantiza que se cumpla; hace falta comprobarla en código. Y los 22.000 tokens por producto son el costo de mandar todo el canal en cada llamada. Comparar con la columna Hoy: 47 inválidos.",
  ask="¿Alguno de estos fallos les sorprende? ¿Cuál esperaban?",
  transition="Almuerzo. A las 13:15, herramientas.")


# ─────────────────────────── 04 · V2 ───────────────────────────
L("v2", "divider", "V2 · herramientas.",
  lead="El agente consulta antes de decidir.",
  objective="Retomar después del almuerzo y abrir la V2",
  say="Recapitular en una frase: la V1 responde sola y falla donde necesita datos que no tiene. La V2 le da herramientas para consultar las tablas de referencia y el esquema del canal. El prompt deja de llevar el canal entero: el agente pide solo lo que necesita para este producto.",
  transition="Qué es una herramienta.")

L("v2", "flow", "Una herramienta es una función que el modelo pide y el código ejecuta.",
  items=["El modelo pide buscar_categoria('urn:category:1106872')",
         "El programa ejecuta la función: consulta la tabla",
         "Devuelve {encontrada: true, urn, name} o {encontrada: false, motivo}",
         "El modelo sigue con ese dato, no con su memoria"],
  objective="Definir herramienta sin jerga",
  say="El modelo no ejecuta nada: redacta un pedido con nombre y argumentos, el programa lo ejecuta y le devuelve el resultado como un mensaje más. Por eso la herramienta es determinista y el modelo no. Hay herramientas de lectura (consultar) y de acción (publicar); hoy todas las nuestras son de lectura. Que la herramienta exista no obliga al modelo a usarla ni a respetarla: la V3 revisa la entrega contra el esquema del canal, pero imponer por código lo que dice la tabla de atributos es un pendiente.",
  transition="La fuente se abstrae.")

L("v2", "code", "La fuente se abstrae; las herramientas no cambian.",
  code={"file": "core/src/catalogo/herramientas.py", "lines": "17-34", "symbol": "FuenteCatalogo", "highlight": [17, 25, 26],
        "caption": "Hoy FuenteArchivos lee data/real; mañana una clase que llame a la base o a un endpoint interno de Alephee. Las herramientas y el agente no se tocan."},
  objective="Mostrar el punto de integración con Alephee",
  say="Tres consultas: categoría destino por id legacy, destinos de un atributo legacy y esquema de una categoría del canal. Eso es todo lo que el agente necesita de Alephee. La API pública v2 alcanza para leer el producto (F8) pero no expone estas tablas: la integración real es una FuenteCatalogo nueva contra lo que Maximiliano exponga.",
  ask="¿Dónde viven hoy estas tres consultas en la plataforma de Alephee?",
  transition="Cómo se describe una herramienta.")

L("v2", "code", "Una herramienta bien descrita.",
  code={"file": "core/src/catalogo/herramientas.py", "lines": "42-48", "symbol": "buscar_categoria", "highlight": [44, 45, 48],
        "caption": "El docstring es lo que lee el modelo: qué devuelve, con qué formato de entrada y qué pasa si no encuentra. La respuesta negativa es explícita, nunca vacía."},
  objective="Buenas prácticas de diseño de herramientas",
  say="Tres reglas: nombre que diga qué hace, descripción con un ejemplo del argumento y salida negativa explícita con motivo. Una herramienta que devuelve null cuando no encuentra invita al modelo a inventar; una que devuelve encontrada: false con motivo le da algo que repetir en missing.",
  transition="Decisión 10: qué decide la tabla y qué decide el agente.")

L("v2", "decision", "¿Qué decide la tabla y qué decide el agente?",
  label="En la base preparada: la categoría se fija en código (V3); los campos de la tabla los aplica el modelo por instrucción",
  decision=D(10, "¿Qué decide la tabla y qué decide el agente?",
             ["A · La tabla fija la categoría y los campos; el agente solo elige el valor equivalente de la lista y cubre lo que la tabla no tiene",
              "B · El agente puede corregir la tabla si cree que está mal",
              "C · Todo por tabla; sin modelo"],
             "A. La tabla manda (acuerdo del 25/08 con Juan David). Hoy la categoría se impone en código (V3) y la tabla de atributos la consulta el agente por herramienta, desambiguada por categoría en código; imponer también los campos por código es el siguiente paso. Lo que la tabla no cubre (valores de lista, atributos sin referencia) es lo único que decide el agente.",
             "tabla-vs-agente"),
  objective="Cerrar la decisión 10",
  say="B es el error más común: dejar que el modelo mejore un mapeo que el equipo de catálogo mantiene a mano. Si la tabla está mal, se corrige la tabla. C ya se descartó en la decisión 3. Ser exacto sobre el estado: la V3 fija la categoría en código; los campos mapeados por tabla todavía dependen de que el modelo respete la herramienta, y el guardrail solo revisa el esquema. Si la sala quiere imponerlos por código, es un cambio acotado en _al_entregar y queda como pendiente.",
  transition="El loop del agente y su límite.")

L("v2", "code", "El loop tiene un límite y una salida garantizada.",
  code={"file": "core/src/catalogo/v2.py", "lines": "82-96", "symbol": "MAX_RONDAS", "highlight": [84, 86, 90],
        "caption": "Seis rondas como máximo. En la última solo queda la herramienta de entrega y se desactivan las llamadas en paralelo. Si aun así no entrega, el error es explícito."},
  objective="Mostrar el control del loop agéntico",
  say="Esto es lo que convierte un modelo con herramientas en un agente controlado: un límite de rondas y una última ronda forzada a entregar. Sin esto, un agente puede consultar para siempre o terminar sin respuesta. Seis no es una garantía de calidad: es una garantía de que termina. Lo que entrega todavía puede estar mal; eso es la V3.",
  transition="Dónde se paga el costo: la caché de prompt.")

L("v2", "code", "Caché de prompt: lo estático se paga una vez.",
  code={"file": "core/src/catalogo/v2.py", "lines": "70-80", "symbol": "CachePoint", "highlight": [76, 77],
        "caption": "Instrucciones, herramientas y producto quedan antes del punto de caché: las seis rondas del loop reutilizan ese prefijo en vez de volver a pagarlo (F4)."},
  objective="Conectar la práctica 'estático primero' con el código y con el costo",
  say="El orden del historial es la práctica de la mañana: system fijo, herramientas fijas, el producto y recién después el punto de caché. Bedrock procesa los checkpoints en orden tools → system → messages y cada ronda del loop lee ese prefijo de caché (F4). Mínimo 1.024 tokens para Sonnet 5, que acá se supera. Una ronda que cambia las herramientas invalida la caché: por eso la última ronda cuesta más.",
  transition="Los números de la corrida del 28/09.")

L("v2", "table", "Costo por producto, medido.",
  label="Corrida del 28/09 · 30 reales · anterior a las correcciones · tokens de entrada por producto",
  table={"headers": ["Versión", "Entrada sin caché", "Leída de caché", "Segundos"],
         "rows": [["V1", "~22.000", "—", "12,3"], ["V2", "~1.600", "~12.000", "18,3"]]},
  objective="Mostrar el efecto de herramientas + caché en tokens y latencia",
  say="La V2 paga 1.600 tokens nuevos por producto y lee 12.000 de caché; la V1 pagaba 22.000 nuevos. La latencia sube porque hay varias rondas: es batch, no importa. Lo que falta para hablar de dólares: sumar escritura de caché, salida y reintentos, y la tasa real de reutilización. No inferir ahorro solo de esta tabla.",
  transition="Decisión 11: el costo.")

L("v2", "decision", "¿Cuánto puede costar?",
  label="Abierta: hoy no hay tope ni medición completa en la base preparada",
  decision=D(11, "¿Cómo tratamos la restricción de costo del modelo?",
             ["A · Tope mensual acordado con Alephee y medición por producto: tokens de entrada, salida, caché leída y escrita",
              "B · Sin tope: se mide después",
              "C · El tope de hoy (USD 350) y publicar sin atributos al agotarse"],
             "A. Hoy el tope corta la calidad (C). Con caché de prompt y caché por SKU (decisión 13) el costo por producto baja; el número se fija con una corrida completa medida, no con esta tabla.",
             "costo"),
  objective="Cerrar la decisión 11 con la medición como tarea",
  say="Anotar como pendiente la corrida de medición completa con su dueño. Si el grupo quiere un número hoy, dar el de tokens, no el de dólares.",
  transition="El mismo caso por V2.")

L("v2", "demo", "Demo · el mismo caso por V2.",
  demo={"command": "scripts/correr.sh --version v2 --datos real --caso error-88904447",
        "watch": ["Qué herramientas pidió y en qué orden (herramientas_usadas)",
                  "La categoría ahora sale de la tabla, no del modelo",
                  "Código OEM: ¿sigue siendo ABS Plastic?",
                  "Tokens leídos de caché frente a los nuevos"],
        "fallback": "resultados/v2-real-20260928-181509.json (corrida del 28/09, anterior a las correcciones)"},
  objective="Comparar V1 y V2 sobre el mismo caso",
  say="Mismo caso que a la mañana, para comparar. Predicción antes de correr: ¿va a usar la referencia de atributos? Leer herramientas_usadas primero. Si el modelo entrega algo fuera de lista, señalarlo: la herramienta no obliga; eso lo arregla la V3. Pausa 14:45.",
  transition="Pausa. A las 15:00, control.")


# ─────────────────────────── 05 · V3 ───────────────────────────
L("v3", "divider", "V3 · control.",
  lead="Qué pasa cuando el agente no sabe.",
  objective="Abrir la V3",
  say="La V2 consulta pero no está obligada a respetar lo que consulta. La V3 agrega tres cosas: guardrails en código que revisan cada entrega, memoria de correcciones del equipo de catálogo y caché por SKU para que el mismo producto no se mapee dos veces. Es la versión que reemplaza el publicar sin atributos.",
  transition="Qué es un guardrail acá.")

L("v3", "compare", "Guardrail: una comprobación en código, no otra instrucción.",
  items=["REVISAR | Lista los problemas en lenguaje claro y se los devuelve al agente, que tiene una ronda para corregir",
         "LIMPIAR | Red final: descarta lo inválido con motivo y marca los obligatorios que faltan",
         "NUNCA | Publica un valor fuera de la lista del canal, un -1 ni un duplicado. No verifica que el valor sea verdad: eso sigue siendo del esquema y de catálogo"],
  objective="Diferenciar guardrail de regla del prompt",
  say="Una regla en el prompt es un pedido; un guardrail es una comprobación que no depende de que el modelo obedezca. Dos pasos: primero se le devuelven los problemas al agente para que corrija (una ronda); lo que siga mal se descarta en código. Límite honesto: valida pertenencia al esquema y al dominio por ID; no verifica que el valor sea verdad respecto del producto.",
  transition="Qué mira el validador.")

L("v3", "code", "Qué mira el validador.",
  code={"file": "core/src/catalogo/guardrails.py", "lines": "11-23", "symbol": "_problema", "highlight": [13, 15, 18, 20],
        "caption": "Cuatro comprobaciones por atributo: que exista en la categoría, que tenga dato, que el valueId esté en la lista del canal y que el nombre coincida con ese ID."},
  objective="Leer las cuatro comprobaciones",
  say="Recorrer las cuatro con el caso guía: ABS Plastic en Código OEM pasa la primera (el atributo existe) y la segunda (tiene dato). Shopee lo rechazó con 'value is not linked': el canal sí tiene una lista para ese atributo, pero nuestro esquema MOCK no la tiene, así que la tercera comprobación no puede detectarlo. Ese es el límite: el guardrail detecta lo que el esquema permite detectar. Por eso el esquema oficial de Shopee es un pendiente de primer orden.",
  ask="¿Qué comprobación agregarían con lo que saben del canal?",
  transition="La red final.")

L("v3", "code", "La red final no inventa: descarta y marca.",
  code={"file": "core/src/catalogo/guardrails.py", "lines": "41-57", "symbol": "def limpiar", "highlight": [46, 53, 56],
        "caption": "Lo que no pasa va a rejected con el motivo del guardrail; lo obligatorio sin dato válido va a missing; sin categoría de referencia, se pide revisión."},
  objective="Mostrar que la salida final siempre cumple el contrato",
  say="Después de esta función nunca sale un valor inválido, un duplicado ni un obligatorio sin informar. Lo descartado no desaparece: queda en rejected con el motivo, para que quien revise entienda por qué. Esto es lo que vale medir en la prueba de las 16:15: cero inválidos detectables.",
  transition="Decisión 12.")

L("v3", "decision", "¿Qué hace cuando no sabe?",
  label="La opción B ya está en la base preparada (V3) · C se construye sobre B",
  decision=D(12, "¿Qué hace el agente cuando no puede completar un atributo obligatorio?",
             ["A · Publicar sin el atributo (hoy)",
              "B · Faltante explícito con motivo: la publicación sale con missing y alguien decide",
              "C · Bloquear la publicación hasta revisión humana"],
             "B. Reemplaza el publicar sin atributos. Quién recibe missing y si bloquea o no la publicación es la integración con la plataforma de Alephee: pendiente con dueño. C es una política válida que se puede construir sobre B.",
             "cuando-no-sabe"),
  objective="Cerrar la decisión 12 y dejar la política de revisión como pendiente",
  say="Marcar missing no crea solo un circuito de revisión: hoy es una lista en la salida. Quién la mira, dónde y con qué herramienta es una decisión de producto de Alephee, no del agente. Anotar dueño.",
  transition="Memoria.")

L("v3", "cards", "Memoria: correcciones del equipo de catálogo.",
  items=["Una corrección dice: en esta categoría, este valor del producto va a este atributo con este valor del canal",
         "El agente la consulta como una herramienta más y manda sobre su criterio",
         "Hoy es un archivo JSON local; en producción, AgentCore Memory o una tabla de Alephee"],
  objective="Definir memoria para este agente sin prometer aprendizaje automático",
  say="Memoria acá no es que el agente aprende solo: es que reutiliza correcciones que una persona del equipo de catálogo cargó explícitamente. Se cargan con un comando; el agente las consulta por categoría. Límite honesto: la persistencia existe; que el modelo siempre las respete depende de que las consulte, por eso la instrucción lo exige y el guardrail revisa después.",
  transition="Una corrección también vacía la caché.")

L("v3", "code", "Una corrección vacía la caché.",
  code={"file": "core/src/catalogo/memoria.py", "lines": "31-41", "symbol": "def corregir", "highlight": [34, 35, 40],
        "caption": "La corrección se guarda con autor y fecha y reemplaza a la anterior del mismo atributo. Como puede cambiar cualquier mapeo guardado, la caché de mapeos se vacía."},
  objective="Mostrar la relación entre memoria y caché",
  say="Dos reglas simples: una corrección nueva reemplaza a la anterior para la misma categoría, atributo y valor; y toda corrección invalida la caché completa. Es la invalidación más simple posible; en producción conviene invalidar por categoría.",
  transition="Determinismo y caché por SKU.")

L("v3", "code", "Mismo SKU, misma salida.",
  code={"file": "core/src/catalogo/v3.py", "lines": "62-79", "symbol": "en_cache", "highlight": [65, 66, 73, 74],
        "caption": "La tabla fija la categoría antes de llamar al modelo; sin referencia o sin esquema, se devuelve el faltante sin invocarlo. Si hay caché válida para SKU + categoría legacy, el modelo tampoco se llama."},
  objective="Recorrer el paso de la V3 completo",
  say="Orden del paso: categoría desde la tabla (decisión 10 hecha código), salida temprana si no hay referencia o esquema, caché por SKU y categoría legacy revisada contra el esquema antes de reutilizarla, y recién después el loop de la V2 con guardrails en la entrega. 40 concesionarios venden el mismo SKU de GM: un solo mapeo. Límite: la clave no incluye versión de tablas ni cuenta; eso es la decisión 13.",
  transition="Decisión 13.")

L("v3", "decision", "¿Cómo garantizamos determinismo?",
  label="La opción A ya está en la base preparada (clave SKU + categoría legacy) · falta la invalidación por tablas",
  decision=D(13, "¿Cómo garantizamos que el mismo SKU dé la misma salida?",
             ["A · Caché por SKU + canal; se invalida al corregir o al cambiar las tablas",
              "B · Seed fijo (lo que se intentó hoy; los parámetros exactos siguen sin confirmar)",
              "C · Recalcular siempre y aceptar variación"],
             "A. Un mapeo por SKU y canal. B reduce la variación pero no la elimina y sigue pagando cada corrida. La clave actual es SKU + categoría legacy; falta sumar versión de las tablas y aislamiento por cuenta antes de producción.",
             "determinismo-y-cache"),
  objective="Cerrar la decisión 13 con las extensiones de la clave como pendiente",
  say="Preguntar al grupo qué cambios deberían invalidar la caché: cambio en el producto, en las tablas, en el esquema del canal. Anotar la lista: es la especificación de la clave de producción.",
  transition="Demo: corregir y repetir.")

L("v3", "demo", "Demo · corregir y repetir.",
  demo={"command": "scripts/corregir.sh --categoria <urn-categoria> --urn <urn-atributo> --valor-producto <valor> --value-id <id> --value <nombre>\nscripts/correr.sh --version v3 --datos real --caso error-88904447 --cache",
        "watch": ["buscar_correcciones aparece en herramientas_usadas",
                  "El valor corregido sale tal cual lo cargó catálogo",
                  "rejected explica cada descarte del guardrail",
                  "Segunda corrida del mismo caso: herramientas_usadas = [cache] y cero tokens"],
        "fallback": "resultados/v3-real-20260928-180524.json (corrida del 28/09, anterior a las correcciones)"},
  objective="Ver memoria, guardrails y caché en una sola secuencia",
  say="Elegir con el grupo la corrección a cargar sobre el caso guía (un valor de lista que el modelo eligió mal). Cargarla, correr, leer. Correr de nuevo: debe salir de caché. Si algo falla, abrir la corrida guardada y decir que es vieja.",
  transition="A las 16:15, la prueba.")

# ─────────────────────────── 06 · La prueba y el camino ───────────────────────────
L("prueba", "divider", "La prueba.",
  lead="Hoy contra V1, V2 y V3, sobre los 30, con el criterio de la decisión 8.",
  objective="Abrir la prueba con el criterio acordado a la vista",
  say="Volver a la pizarra: el número de la decisión 8. Las corridas del lote se lanzaron durante los bloques; acá se leen. Si alguna no terminó, se usa la del 28/09 y se dice.",
  transition="Los resultados.")

L("prueba", "table", "Resultados (se completan en vivo).",
  label="Columna Hoy: publicaciones exportadas, expected MOCK. Las demás se llenan con la corrida del día",
  table={"headers": ["Métrica", "Hoy", "V1", "V2", "V3"],
         "rows": [["Casos exactos", "7", "·", "·", "·"], ["Categoría correcta", "28", "·", "·", "·"],
                  ["Valores inválidos (-1 o fuera de lista)", "47", "·", "·", "·"], ["Duplicados", "5", "·", "·", "·"],
                  ["Obligatorios sin informar", "2", "·", "·", "·"]]},
  objective="Leer los resultados contra el criterio, sin maquillar",
  say="Completar las columnas con la corrida del día. Referencia del 28/09, anterior a las correcciones: V1 5 exactos, 19 inválidos; V2 4 exactos, 30 categorías, 9 inválidos; V3 4 exactos, 28 categorías, 0 inválidos, 0 duplicados, 0 obligatorios sin informar. Si los exactos siguen bajos en todas las columnas, decirlo y explicar por qué en la lámina siguiente.",
  transition="Cómo leer la tabla.")

L("prueba", "cards", "Cómo leer la tabla.",
  items=["Exactos bajos en todas las columnas: el expected hereda las omisiones del proceso actual y castiga aciertos que hoy nadie mapea",
         "Inválidos y duplicados sí son errores seguros: la V3 no entrega ninguno detectable por este evaluador (28/09)",
         "Categoría: la V3 dio 28/30 en la corrida vieja; la corrección del 28/09 la fija desde la tabla y hay que volver a medir"],
  objective="Dar la lectura honesta de los resultados",
  say="Conclusión defendible: en este ensayo la V3 elimina los errores que estos controles detectan, pero todavía no demuestra mejor exactitud global contra un expected que es mock. Tenemos evidencia de qué controles ayudan y una lista clara de lo que falta para validar con el canal. Un control puede reducir errores quitando información: mirar control y cobertura juntos.",
  ask="¿Qué evidencia pedirían antes de un piloto con un concesionario?",
  transition="El camino a producción.")

L("prueba", "flow", "Camino a producción.",
  items=["Esquema oficial de Shopee y expected validado con el equipo de catálogo",
         "Integración: la API pública lee el producto (F8); escribir publicaciones y leer tablas necesita acceso interno",
         "Decidir dónde corre el batch (decisión 5) y la política de missing (decisión 12)",
         "Medir el costo completo y fijar el tope (decisión 11); probar Haiku 4.5 (decisión 6)"],
  objective="Convertir los pendientes en tareas con dueño",
  say="Cada punto necesita responsable y fecha; se completan en la última lámina. Retomar las dudas de AgentCore anotadas a la mañana y asignarlas a Juan David. El código queda en el repositorio de Alephee que Rick indique.",
  transition="Las trece decisiones.")

FILAS_DECISIONES = [["1", "Alcance: un canal, una familia, categoría + atributos", "decisiones/01-alcance.md"],
                  ["2", "Contrato: missing y rejected con motivo", "decisiones/02-contrato.md"],
                  ["3", "Tipo de aplicación: single prompt y escalar", "decisiones/03-tipo-de-aplicacion.md"],
                  ["4", "Salida estructurada por herramienta + Pydantic", "decisiones/04-salida-estructurada.md"],
                  ["5", "Dónde corre: local hoy, chat en AgentCore, batch a medir", "decisiones/05-donde-corre.md"],
                  ["6", "Modelo: Claude Sonnet 5; Haiku 4.5 a probar", "decisiones/06-modelo.md"],
                  ["7", "Stack: Python + LlamaIndex Workflows + BedrockConverse", "decisiones/07-stack.md"],
                  ["8", "Criterio de éxito: el número de la pizarra", "decisiones/08-criterio-de-exito.md"],
                  ["9", "Dataset: 30 reales con mock rotulado", "decisiones/09-dataset.md"],
                  ["10", "La tabla manda; el agente elige valores y lo no cubierto", "decisiones/10-tabla-vs-agente.md"],
                  ["11", "Costo: tope acordado y medición por producto", "decisiones/11-costo.md"],
                  ["12", "Cuando no sabe: faltante explícito, nunca inventar", "decisiones/12-cuando-no-sabe.md"],
                  ["13", "Determinismo: caché por SKU + canal con invalidación", "decisiones/13-determinismo-y-cache.md"]]

L("prueba", "table", "Las 13 decisiones (1 a 7).",
  table={"headers": ["N", "Decisión", "Archivo"], "rows": FILAS_DECISIONES[:7]},
  objective="Cerrar con el registro completo: las decisiones de la mañana",
  say="Cada archivo tiene contexto, opciones, decisión y razonamiento. Lo que quedó distinto a la propuesta se escribe tal como se decidió en la sala.",
  transition="Las de la tarde.")

L("prueba", "table", "Las 13 decisiones (8 a 13).",
  table={"headers": ["N", "Decisión", "Archivo"], "rows": FILAS_DECISIONES[7:]},
  objective="Cerrar con el registro completo: las decisiones de la tarde",
  say="Este registro es el método repetible: el próximo caso de uso de Alephee arranca por estas trece preguntas, con las respuestas de hoy como punto de partida.",
  transition="Quién hace qué.")

L("prueba", "divider", "Quién hace qué, para cuándo.",
  lead="Se completa en la sala.",
  objective="Cerrar con responsables y fechas",
  say="Repartir los pendientes del camino a producción entre Alephee, Craftech y AWS, con fecha. Confirmar el repositorio donde queda el código. Agradecer y cerrar a las 17:00; preguntas hasta las 17:30.",
  transition="Fin.")


CONTEXTO = {1: "El agente del war room tiene que servir para decidir el método, no para cubrir todo el catálogo en un día. Alephee publica en varios canales (Shopee, Magalu, Tienda Nube) y hoy además genera marca, título y descripción con otros prompts.",
       2: "Hoy la publicación sale con lo que hay: si falta un obligatorio o el valor no existe, no queda registro. Shopee rechaza algunos casos y acepta otros mal (valores -1, URN sin sufijo).",
       3: "El proceso actual es un workflow fijo (dos llamadas y un merge). Antes de agregar herramientas conviene saber qué resuelve el modelo solo y qué no, para justificar cada capa con evidencia. La base preparada ya implementa la opción A como V1.",
       4: "Los prompts actuales piden JSON válido en el texto y lo parsean. Cuando el modelo agrega texto o omite un campo, el parseo falla o pasa algo incompleto. La base preparada ya implementa la opción B.",
       5: "El agente corre hoy en local. AgentCore Runtime ofrece runtime gestionado, identidad, memoria, gateway y observabilidad (fuentes F1–F3b en docs/warroom/fuentes.md); para un batch largo faltan mediciones de sesión, costo y arranque.",
       6: "Decisión tomada el 25/09 (CLAUDE.md, decisión 6): Claude Sonnet 5 en Bedrock, ID verificado el 28/09. Hoy se valida. Lo que más falla es seguir reglas y no inventar valores. El costo importa (presupuesto de USD 350/mes); la latencia no (batch). Bedrock ofrece también Claude Sonnet 5.5, Haiku 4.5, Nova, GPT, Llama y otros (F6).",
       7: "Decisión tomada el 28/09 (CLAUDE.md, decisión 9). Craftech ya opera un template con Python + LlamaIndex Workflows + BedrockConverse, con el LLM inyectado y pasos probados con dobles. Alephee hoy llama al SDK directo sin framework.",
       8: "La métrica 'exacto' exige categoría correcta, ni sobra ni falta atributo, nada fuera de dominio, sin duplicados y faltantes informados. El expected es mock y hereda omisiones del proceso actual: el 28/09 el proceso actual dio 7 exactos y V1/V2/V3 dieron 5, 4 y 4.",
       9: "El zip del 24/09 trae 30 productos reales con su publicación actual y los rechazos de Shopee. El esquema de atributos de Shopee y el expected se generaron como mock rotulado.",
       10: "Las tablas reference_category y reference_attribute las mantiene el equipo de catálogo. 306 ids legacy apuntan a más de un atributo de Shopee según la categoría. Acuerdo del 25/08: lo que la tabla resuelve no pasa por el modelo. Estado de la base preparada: la categoría se impone en código (V3); los campos de la tabla los aplica el modelo por instrucción y herramienta.",
       11: "Hoy el tope de USD 350/mes corta la calidad: al agotarse se publica sin atributos. La V2 baja los tokens de entrada con herramientas y caché de prompt; falta medir el costo completo.",
       12: "Hoy, un obligatorio sin dato se publica sin el atributo. El guardrail de la V3 ya lo marca en missing con motivo (opción B); bloquear la publicación (C) sería una política construida sobre eso.",
       13: "El mismo SKU de GM lo venden unos 40 concesionarios y hoy se reprocesa para cada uno con resultados distintos. Se agregó un seed (parámetros exactos sin confirmar). La V3 trae caché por SKU + categoría legacy; falta invalidar por versión de tablas y aislar por cuenta."}


def escribir_decisiones():
    for s in SLIDES:
        if s["kind"] != "decision":
            continue
        x = s["decision"]; n = x["number"]
        opciones = "\n".join(f"{i+1}. {o}" for i, o in enumerate(x["options"]))
        estado = f"\n\n**Estado.** {s['label']}" if s.get("label") else ""
        (RAIZ / x["file"]).write_text(f"""# Decisión {n:02d} · {s['title']}

**Contexto.** {CONTEXTO[n]}{estado}

**Pregunta.** {x['question']}

**Opciones.**
{opciones}

**Propuesta para la sala.** {x['proposal']}

**Decisión.** _(se completa el 1/10)_

**Razonamiento.** _(se completa el 1/10)_

**Responsable y fecha.** _(se completa el 1/10)_
""", encoding="utf-8")


def construir() -> dict:
    return {"title": "War Room · Alephee × Craftech × AWS", "date": "2026-10-01", "sections": SECTIONS, "slides": SLIDES}


def escribir():
    (RAIZ / "docs/warroom/diapositivas.json").write_text(json.dumps(construir(), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    escribir_decisiones()
    print(f"{len(SLIDES)} láminas escritas")


if __name__ == "__main__":
    escribir()
