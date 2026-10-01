# Decisión 07 · ¿Con qué lo construimos?

**Contexto.** Craftech ya opera un template con Python + LlamaIndex Workflows + BedrockConverse, con el LLM inyectado y pasos probados con dobles. Alephee hoy llama al SDK directo sin framework.

**Pregunta.** ¿Qué stack usamos para el agente?

**Opciones.**
1. A · Python + LlamaIndex Workflows + BedrockConverse
2. B · Llamadas directas al SDK, sin framework (como hoy)
3. C · Otro framework de agentes (Strands, LangGraph…)

**Propuesta para la sala.** A. Es el stack del template que Craftech ya opera: el workflow no conoce Bedrock y cada paso se prueba con dobles. B repite el código de loop, herramientas y caché que un framework ya trae. C es válido; se elige A por continuidad con lo que ya está probado.

**Decisión.** _(se completa el 1/10)_

**Razonamiento.** _(se completa el 1/10)_

**Responsable y fecha.** _(se completa el 1/10)_
