"""Reevalúa una corrida guardada contra el `expected` actual, sin volver a llamar al modelo.

    uv run python scripts/reevaluar.py resultados/v1-real-20260928-173758.json

Sirve cuando cambia el dataset esperado (por ejemplo, tras corregir scripts/generar_mocks_reales.py).
"""

import json
import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "core" / "src"))


def main() -> None:
    corrida = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    os.environ["DATA_DIR"] = str(RAIZ / "data" / corrida.get("datos", "mock"))
    from catalogo.datos import cargar_atributos_canal, cargar_dataset
    from catalogo.evaluacion import evaluar_caso, resumir

    casos = {c["id"]: c for c in cargar_dataset()}
    vacia = {"category": None, "attributes": [], "missing": [], "rejected": []}
    resultados = []
    for fila in corrida["casos"]:
        esperado = casos[fila["caso"]]["expected"]
        resultados.append(evaluar_caso(fila["publicacion"] or vacia, esperado, cargar_atributos_canal(esperado["category"])))
    resumen = resumir(resultados)
    for clave in ("prompt_tokens", "completion_tokens", "cache_read_input_tokens", "segundos_promedio"):
        resumen[clave] = corrida["resumen"].get(clave)
    print(json.dumps({"version": corrida["version"], **resumen}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
