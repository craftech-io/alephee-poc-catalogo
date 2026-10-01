# Decisión 04 · ¿Cómo garantizamos el formato?

**Contexto.** Los prompts actuales piden JSON válido en el texto y lo parsean. Cuando el modelo agrega texto o omite un campo, el parseo falla o pasa algo incompleto.

**Pregunta.** ¿Cómo se garantiza que la salida cumpla el contrato?

**Opciones.**
1. A · Pedir JSON en el texto y parsear (hoy)
2. B · Herramienta con esquema Pydantic: la entrega es una llamada tipada
3. C · Post-procesar la respuesta con expresiones regulares

**Propuesta para la sala.** B. El formato deja de ser una regla del prompt y pasa a ser un contrato que el modelo no puede violar. C arregla síntomas: si el modelo omite un campo, la regex no lo inventa.

**Decisión.** _(se completa el 1/10)_

**Razonamiento.** _(se completa el 1/10)_

**Responsable y fecha.** _(se completa el 1/10)_
