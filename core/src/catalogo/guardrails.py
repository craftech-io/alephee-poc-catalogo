"""Guardrails de la V3: nada sale fuera de contrato, lo diga el modelo o no.

`revisar` devuelve los problemas en lenguaje claro (el agente recibe la lista y tiene una
ronda para corregir). `limpiar` es la red final: descarta lo inválido y marca los
obligatorios que faltan, sin inventar nada.
"""

from .datos import SIN_DATO


def _problema(attr: dict, esquema: dict[str, dict]) -> str | None:
    definicion = esquema.get(attr["urn"])
    if definicion is None:
        return f"{attr['urn']} no es un atributo de esta categoría"
    if str(attr.get("value", "")).strip() in SIN_DATO:
        return f"{attr['urn']} tiene un valor sin dato ('{attr.get('value')}'); no se publica"
    dominio = {v["id"]: v["name"] for v in definicion.get("values", [])}
    if dominio and str(attr.get("valueId")) not in dominio:
        return f"{attr['urn']}: el valor '{attr.get('value')}' no está en la lista del canal"
    if dominio and attr.get("value") != dominio[str(attr.get("valueId"))]:
        return f"{attr['urn']}: el nombre del valor no coincide con su ID en el canal"
    return None


def revisar(publicacion: dict, esquema: dict[str, dict]) -> list[str]:
    problemas = [p for a in publicacion["attributes"] if (p := _problema(a, esquema))]
    if not publicacion["category"]:
        problemas.append("No hay categoría resuelta: se requiere revisión")
    vistos: set[str] = set()
    for a in publicacion["attributes"]:
        if a["urn"] in vistos:
            problemas.append(f"{a['urn']} aparece más de una vez")
        vistos.add(a["urn"])
    faltantes = {m["urn"] for m in publicacion["missing"]}
    for urn, d in esquema.items():
        if d.get("mandatory") and urn not in vistos and urn not in faltantes:
            problemas.append(f"{urn} es obligatorio: complétalo o agrégalo a missing con el motivo")
    return problemas


def limpiar(publicacion: dict, esquema: dict[str, dict]) -> dict:
    atributos, descartados, vistos = [], list(publicacion["rejected"]), set()
    for a in publicacion["attributes"]:
        motivo = _problema(a, esquema) or (f"{a['urn']} duplicado" if a["urn"] in vistos else None)
        if motivo:
            descartados.append({"legacyId": a["urn"], "reason": f"guardrail: {motivo}"})
            continue
        vistos.add(a["urn"])
        atributos.append(a)
    faltantes = [m for m in publicacion["missing"]
                 if m["urn"] not in vistos and not (m["urn"] == "category" and publicacion["category"])]
    ya = {m["urn"] for m in faltantes}
    faltantes += [{"urn": u, "reason": "obligatorio sin dato válido (guardrail)"}
                  for u, d in esquema.items() if d.get("mandatory") and u not in vistos and u not in ya]
    if not publicacion["category"] and "category" not in ya:
        faltantes.append({"urn": "category", "reason": "sin categoría de referencia; requiere revisión"})
    return {**publicacion, "attributes": atributos, "missing": faltantes, "rejected": descartados}
