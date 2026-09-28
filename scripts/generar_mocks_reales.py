"""Genera lo que el zip de Alephee no trae, derivado de los datos reales. TODO ES MOCK.

    uv run python scripts/generar_mocks_reales.py

1. data/real/shopee_atributos_por_categoria.json: los atributos que Shopee espera por
   categoría (tipo, obligatorio, valores válidos). Sale de lo que aparece en las
   publicaciones de esa categoría, de los rechazos de Shopee (obligatorios y valores
   "not linked") y de alternativas genéricas inventadas para los dominios.
2. `expected` de cada caso de data/real/dataset.json: la publicación actual limpia
   (sin `-1`, sin duplicados, sin valores fuera de dominio, categoría de la tabla) y
   los obligatorios que faltan. Hereda las omisiones del proceso actual: un atributo que
   hoy no se mapea tampoco está en `expected`. Hay que validarlo con el equipo de catálogo.
"""

import json
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
REAL = RAIZ / "data" / "real"

TIPOS_CON_DOMINIO = {"MULTI_COMBO_BOX", "SINGLE_COMBO_BOX", "MULTIPLE_SELECT_COMBO_BOX", "COMBO_BOX", "SINGLE_DROP_DOWN"}
TIPOS_UN_VALOR = {"SINGLE_COMBO_BOX", "COMBO_BOX", "SINGLE_DROP_DOWN", "FREE_TEXT_FIELD", "FREE_TEXT_FILED", "TEXT_FILED"}
SIN_DATO = {"-1", "N/A", ""}

# Valores que Shopee rechazó con "Attribute value is not linked to <atributo>".
NO_VINCULADOS = {
    ("urn:attribute:101780:vendor:shopee", "15963"),  # Lamp technology = Halógena (error-52068151)
    ("urn:attribute:102200:vendor:shopee", "14971"),  # Car brand = Genérica (error-52095432)
    ("urn:attribute:101676:vendor:shopee", "17987"),  # Código OEM = ABS Plastic (error-88904447)
    ("urn:attribute:101752:vendor:shopee", "101752"),  # Chrome: el valueId es el id del atributo (error-26306808)
}

# Obligatorios según los rechazos de Shopee. Manufacturer y GTIN no aparecen en ninguna
# tabla ni publicación: sus URN son inventados.
OBLIGATORIOS = {
    "urn:category:102307:vendor:shopee": [("urn:attribute:102292:vendor:shopee", "Inmetro Certification", "SINGLE_COMBO_BOX")],
    "urn:category:102277:vendor:shopee": [("urn:attribute:102292:vendor:shopee", "Inmetro Certification", "SINGLE_COMBO_BOX")],
    "urn:category:102273:vendor:shopee": [("urn:attribute:102293:vendor:shopee", "Auto-Part Number", "FREE_TEXT_FIELD")],
    "urn:category:102412:vendor:shopee": [("urn:attribute:990101:vendor:shopee", "Manufacturer (MOCK)", "FREE_TEXT_FIELD")],
    "urn:category:102363:vendor:shopee": [("urn:attribute:990102:vendor:shopee", "GTIN (MOCK)", "FREE_TEXT_FIELD")],
}
# Condição do Item es obligatorio en toda categoría donde aparece (supuesto mock).
SIEMPRE_OBLIGATORIO = {"urn:attribute:101638:vendor:shopee"}

ALTERNATIVAS = {"Novo": ["Usado", "Recondicionado"], "Sim": ["Não"], "Não": ["Sim"], "Brasil": ["Importado"]}


def _valido(urn: str) -> bool:
    return urn.endswith(":vendor:shopee")


def _esquemas(casos: list[dict]) -> dict:
    vistos: dict[str, dict[str, dict]] = defaultdict(dict)
    for caso in casos:
        cat = caso["actual"]["category"]
        for a in caso["actual"]["attributes"]:
            if not _valido(a["urn"]):
                continue
            attr = vistos[cat].setdefault(a["urn"], {"urn": a["urn"], "name": None, "type": a["type"], "valores": {}})
            if a["valueId"] not in (None, "0") and a["value"] not in SIN_DATO and (a["urn"], a["valueId"]) not in NO_VINCULADOS:
                attr["valores"][a["valueId"]] = a["value"]

    siguiente_id = iter(range(990500, 999999))
    salida = {}
    for cat, attrs in sorted(vistos.items()):
        lista = []
        for attr in attrs.values():
            valores = [{"id": i, "name": n, "_origen": "visto en publicaciones"} for i, n in attr["valores"].items()]
            if attr["type"] in TIPOS_CON_DOMINIO:
                for v in list(valores):
                    for alt in ALTERNATIVAS.get(v["name"], []):
                        valores.append({"id": str(next(siguiente_id)), "name": alt, "_origen": "mock"})
            lista.append({
                "urn": attr["urn"],
                "type": attr["type"],
                "mandatory": attr["urn"] in SIEMPRE_OBLIGATORIO,
                "maxValues": 1 if attr["type"] in TIPOS_UN_VALOR else None,
                "values": valores if attr["type"] in TIPOS_CON_DOMINIO else [],
                "_origen": "visto en publicaciones",
            })
        for urn, nombre, tipo in OBLIGATORIOS.get(cat, []):
            existente = next((a for a in lista if a["urn"] == urn), None)
            if existente:
                existente["mandatory"], existente["maxValues"] = True, 1
                existente["_origen"] += " + obligatorio según rechazo de Shopee"
            else:
                lista.append({"urn": urn, "name": nombre, "type": tipo, "mandatory": True, "maxValues": 1,
                              "values": [], "_origen": "obligatorio según rechazo de Shopee (URN mock)"})
        salida[cat] = {"urn": cat, "attributes": lista}
    return salida


def _nombres(casos: list[dict], esquemas: dict) -> None:
    for caso in casos:
        cat = caso["actual"]["category"]
        crudo = json.loads((RAIZ / "inputs/warroom-zip/WarRoom" / caso["grupo"].capitalize()
                            / f"{caso['product']['sku']}-publi.json").read_text(encoding="utf-8"))[0]
        nombre_cat = next((c["name"] for c in crudo["categories"] if c["urn"] == cat), None)
        esquemas[cat].setdefault("name", nombre_cat)
        for a in crudo["attributes"]:
            for attr in esquemas[cat]["attributes"]:
                if attr["urn"] == a["urn"] and not attr.get("name"):
                    attr["name"] = a["name"]


def _completar_categorias(casos: list[dict], esquemas: dict, ref_cat: dict) -> None:
    """Si la categoría de la tabla no tiene publicaciones, hereda el esquema de la categoría
    donde el proceso actual terminó publicando (mock)."""
    for caso in casos:
        cats = caso["product"].get("categories") or []
        destino = ref_cat.get(cats[0]["urn"].split(":")[2]) if cats else None
        if destino and destino not in esquemas and caso["actual"]["category"] in esquemas:
            base = esquemas[caso["actual"]["category"]]
            esquemas[destino] = {"urn": destino, "name": f"{base.get('name')} (MOCK: copia del esquema de {base['urn']})",
                                 "attributes": json.loads(json.dumps(base["attributes"]))}


def _desde_producto(caso: dict, urn: str, definicion: dict, ref_attr: dict) -> dict | None:
    """Busca en el producto un atributo legacy que la tabla mapee a `urn` y resuelve su valor."""
    for a in caso["product"].get("attributes") or []:
        legacy = a["urn"].removeprefix("urn:attribute:").split(":")[0]
        if urn not in ref_attr.get(legacy, []) or str(a.get("value")) in SIN_DATO:
            continue
        if not definicion["values"]:
            return {"urn": urn, "valueId": "0", "value": str(a["value"]), "unit": None}
        valor = next((v for v in definicion["values"] if v["name"].casefold() == str(a["value"]).casefold()), None)
        if valor:
            return {"urn": urn, "valueId": valor["id"], "value": valor["name"], "unit": None}
    return None


def _esperado(caso: dict, esquemas: dict, ref_cat: dict, ref_attr: dict) -> dict:
    legacy = caso["product"]["categories"][0]["urn"].split(":")[2] if caso["product"].get("categories") else None
    categoria = ref_cat.get(legacy)
    esquema = {a["urn"]: a for a in esquemas.get(categoria, {}).get("attributes", [])}
    atributos, vistos = [], set()
    for a in caso["actual"]["attributes"]:
        d = esquema.get(a["urn"])
        if d is None or a["urn"] in vistos or a["value"] in SIN_DATO or (a["urn"], a["valueId"]) in NO_VINCULADOS:
            continue
        dominio = {v["id"] for v in d["values"]}
        if dominio and a["valueId"] not in dominio:
            continue
        vistos.add(a["urn"])
        atributos.append({"urn": a["urn"], "valueId": a["valueId"] if dominio else "0", "value": a["value"], "unit": a["unit"]})
    for u, d in esquema.items():
        if d["mandatory"] and u not in vistos and (desde := _desde_producto(caso, u, d, ref_attr)):
            atributos.append(desde)
            vistos.add(u)
    faltantes = [{"urn": u, "reason": "obligatorio sin dato en el producto"}
                 for u, d in esquema.items() if d["mandatory"] and u not in vistos]
    return {"_origen": "derivado de la publicación actual (MOCK), a validar por catálogo",
            "category": categoria, "attributes": atributos, "missing": faltantes, "rejected": []}


def main() -> None:
    archivo = REAL / "dataset.json"
    dataset = json.loads(archivo.read_text(encoding="utf-8"))
    casos = dataset["cases"]
    ref_cat = {f["legacyId"]: f["urn"] for f in json.loads((REAL / "reference_category.json").read_text())["rows"]}
    ref_attr = defaultdict(list)
    for f in json.loads((REAL / "reference_attribute.json").read_text())["rows"]:
        ref_attr[f["legacyId"]].append(f["urn"])

    esquemas = _esquemas(casos)
    _nombres(casos, esquemas)
    _completar_categorias(casos, esquemas, ref_cat)
    (REAL / "shopee_atributos_por_categoria.json").write_text(json.dumps({
        "_nota": "MOCK derivado de los datos reales: ver scripts/generar_mocks_reales.py. Reemplazar por los "
                 "atributos reales de Shopee (los 'External Attributes' que Alephee pasa hoy al prompt).",
        "vendor": "shopee",
        "categories": esquemas,
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    for caso in casos:
        caso["expected"] = _esperado(caso, esquemas, ref_cat, ref_attr)
    dataset["_nota"] += " `expected` generado por scripts/generar_mocks_reales.py (MOCK)."
    archivo.write_text(json.dumps(dataset, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(esquemas)} categorías con esquema · {len(casos)} casos con expected")


if __name__ == "__main__":
    main()
