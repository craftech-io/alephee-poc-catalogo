# Decisión 08 · ¿Cuál es el número que aceptamos?

**Contexto.** La métrica 'exacto' exige categoría correcta, ni sobra ni falta atributo, nada fuera de dominio, sin duplicados y faltantes informados. El expected es mock y hereda omisiones del proceso actual: el 28/09 el proceso actual dio 7 exactos y V1/V2/V3 dieron 5, 4 y 4.

**Pregunta.** ¿Qué criterio de éxito acordamos para la prueba de las 16:15?

**Opciones.**
1. A · Cero valores inválidos, cero duplicados y todo obligatorio informado en los 30; los exactos se reportan pero no son condición hasta validar el expected con catálogo
2. B · Exactos iguales o mayores al 80 %
3. C · Solo precisión y recall de atributos

**Propuesta para la sala.** A. Con expected mock, 'exacto' castiga aciertos que hoy nadie mapea: el 28/09 el proceso actual dio 7 y las versiones 5, 4 y 4. Los inválidos, duplicados y obligatorios sin informar sí son errores seguros y hoy hay 47, 5 y 2. El número final se fija en la sala.

**Decisión.** _(se completa el 1/10)_

**Razonamiento.** _(se completa el 1/10)_

**Responsable y fecha.** _(se completa el 1/10)_
