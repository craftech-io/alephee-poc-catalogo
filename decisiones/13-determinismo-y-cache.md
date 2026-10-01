# Decisión 13 · ¿Cómo garantizamos determinismo?

**Contexto.** El mismo SKU de GM lo venden unos 40 concesionarios y hoy se reprocesa para cada uno con resultados distintos. Se intentó con seed. La V3 trae caché por SKU + categoría legacy.

**Pregunta.** ¿Cómo garantizamos que el mismo SKU dé la misma salida?

**Opciones.**
1. A · Caché por SKU + canal; se invalida al corregir o al cambiar las tablas
2. B · Seed y temperatura 0 (lo que se intentó hoy)
3. C · Recalcular siempre y aceptar variación

**Propuesta para la sala.** A. Un mapeo por SKU y canal. B reduce la variación pero no la elimina y sigue pagando cada corrida. La clave actual es SKU + categoría legacy; falta sumar versión de las tablas y aislamiento por cuenta antes de producción.

**Decisión.** _(se completa el 1/10)_

**Razonamiento.** _(se completa el 1/10)_

**Responsable y fecha.** _(se completa el 1/10)_
