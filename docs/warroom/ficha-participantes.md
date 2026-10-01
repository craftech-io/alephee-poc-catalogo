# Ficha de trabajo en parejas

**Pareja:** ____________________ **Caso del dataset:** ____________________

Gastón conduce la construcción. La pareja decide, prueba y explica su evidencia. Si el entorno no está listo, dirige la prueba en la pantalla principal. Las opciones del HTML no registran votos; votar a mano o por el chat de la reunión.

## Antes de empezar · 10 minutos

Ficha didáctica: DEMO-01, Correa de transmisión, categoría CORREAS, Color Negro, OEM sin dato. Destino inventado: categoría C10, Color A20, V7 Preto (negro), V8 Branco (blanco); OEM obligatorio. **Estos códigos no son datos de Shopee y no se envían a ninguna API.**

- Categoría y atributos que esperamos: ____________________
- Dato que falta: ____________________
- Regla para pedir revisión: ____________________
- Duda para validar con catálogo: ____________________

Puesta en común: 5 minutos. Acordar si se permiten datos de descripciones y conversiones de unidades; registrar umbrales de calidad, cobertura y costo.

## V1 · justificar un valor · 10 minutos

Caso real asignado por Gastón: ____________________

| Dato de origen | Propuesta V1 | Evidencia | Correcto / incorrecto / discutible |
|---|---|---|---|
| | | | |

Si hay entorno preparado: `scripts/correr.sh --version v1 --datos real --caso <id>`.

Puesta en común: 5 minutos. Entregar un veredicto con evidencia, aunque sea “todavía discutible”.

## V2 · verificar una correspondencia · 10 minutos

Ejecutar V1 y V2 sobre **el mismo caso asignado**. Si ya existe una corrida V1 de ese caso, reutilizarla e identificarla.

| Categoría de referencia | Atributo de destino | Valor permitido | Diferencia frente a V1 |
|---|---|---|---|
| | | | |

Con entorno preparado: `scripts/correr.sh --version v2 --datos real --caso <id>`.

Puesta en común: 5 minutos. Explicar qué aportó la herramienta. Separar correspondencia de campos y elección del valor.

## V3 · preparar una propuesta inconsistente · 10 minutos

Usar una copia de la **salida**, sin editar el dataset original. Elegir una alteración: ID/nombre contradictorio; Color duplicado; OEM omitido sin informarlo en `missing` aunque el esquema lo exige.

- Propuesta alterada: ____________________
- Regla que debería detectarla: ____________________
- Resultado que esperamos conservar / descartar / informar: ____________________
- Resultado observado cuando Gastón ejecuta el validador: ____________________

Puesta en común: 5 minutos. Explicar también lo que esta prueba **no** demuestra. El HTML ilustra la decisión; la comprobación del código se ejecuta por separado.

## Cierre · proponer el próximo paso

- Una conclusión respaldada por la comparación: ____________________
- Una afirmación que todavía no podemos sostener: ____________________
- Pendiente prioritario: ____________________
- Evidencia que lo cerraría: ____________________
- Responsable y fecha acordados con las personas presentes: ____________________
