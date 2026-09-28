"""Convierte el WarRoom.zip de Alephee (24/09) al formato de data/.

    uv run python scripts/importar_warroom.py

Lee inputs/warroom-zip/WarRoom/ (no se commitea: son ~15 MB, casi todo `relations`)
y escribe data/real/, que sí se commitea. `expected` queda en null: la publicación de
hoy NO es la respuesta correcta, es la salida del proceso actual (`actual`), y en los
casos de Error trae el motivo del rechazo de Shopee.
"""

import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
ORIGEN = RAIZ / "inputs" / "warroom-zip" / "WarRoom"
DESTINO = RAIZ / "data" / "real"
CAMPOS_PRODUCTO = ("urn", "legacyId", "sku", "name", "description", "categories", "brand", "attributes", "dimensions")


def _tabla(nombre: str) -> dict:
    filas = json.loads((ORIGEN / nombre).read_text(encoding="utf-8"))
    return {
        "_nota": f"Exportación real de Alephee (WarRoom.zip, 24/09): {nombre}. Se quitó el _id de Mongo.",
        "vendor": "shopee",
        "rows": [{"legacyId": f["legacyId"], "urn": f["urn"], "name": f["name"]} for f in filas],
    }


def _sin_ids(valor):
    if isinstance(valor, dict):
        return {k: _sin_ids(v) for k, v in valor.items() if k != "_id"}
    if isinstance(valor, list):
        return [_sin_ids(v) for v in valor]
    return valor


def _actual(publi: dict) -> dict:
    errores = [e for e in publi.get("events", []) if e.get("status") == "error"]
    return {
        "status": publi.get("status"),
        "error": errores[-1]["message"] if errores else None,
        "category": next((c["urn"] for c in publi.get("categories", []) if ":vendor:shopee" in c["urn"]), None),
        "attributes": [
            {"urn": a["urn"], "type": a.get("type"), "valueId": v.get("urn"), "value": v.get("name"), "unit": v.get("unit") or None}
            for a in publi.get("attributes", [])
            for v in a.get("values", [])
        ],
    }


def main() -> None:
    DESTINO.mkdir(parents=True, exist_ok=True)
    for origen, destino in (("shopee.referencecategories.json", "reference_category.json"),
                            ("shopee.referenceattributes.json", "reference_attribute.json")):
        (DESTINO / destino).write_text(json.dumps(_tabla(origen), ensure_ascii=False, indent=1), encoding="utf-8")

    casos = []
    for grupo in ("Publicados", "Error"):
        for archivo in sorted((ORIGEN / grupo).glob("*.json")):
            if archivo.stem.endswith("-publi"):
                continue
            producto = json.loads(archivo.read_text(encoding="utf-8"))[0]
            publi = json.loads(archivo.with_name(f"{archivo.stem}-publi.json").read_text(encoding="utf-8"))[0]
            casos.append({
                "id": f"{grupo.lower()}-{archivo.stem}",
                "grupo": grupo.lower(),
                "product": _sin_ids({k: producto.get(k) for k in CAMPOS_PRODUCTO}),
                "actual": _actual(publi),
                "expected": None,
            })

    dataset = {
        "_nota": "30 productos reales de Alephee (WarRoom.zip, 24/09): 20 publicados y 10 rechazados por Shopee. "
                 "`actual` = lo que genera hoy el proceso; `expected` = null hasta que el equipo de catálogo la valide.",
        "vendor": "shopee",
        "cases": casos,
    }
    (DESTINO / "dataset.json").write_text(json.dumps(dataset, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(casos)} casos → {DESTINO.relative_to(RAIZ)}/")


if __name__ == "__main__":
    main()
