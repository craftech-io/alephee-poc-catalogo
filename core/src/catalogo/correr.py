"""Corre una versión del agente de catálogo sobre el dataset y la evalúa (modo batch).

    scripts/correr.sh --version v1
    scripts/correr.sh --version v1 --caso 03-valor-en-otro-idioma
"""

import argparse
import asyncio
import json
import time
from datetime import datetime

from botocore.exceptions import BotoCoreError, ClientError

from . import v1
from .datos import RAIZ, cargar_atributos_canal, cargar_dataset
from .evaluacion import evaluar_caso, resumir
from .llm import crear_llm

VERSIONES = {"v1": v1.MapeoV1}
VACIA = {"category": None, "attributes": [], "missing": [], "rejected": []}


async def _correr(version: str, casos: list[dict]) -> None:
    llm = crear_llm()
    atributos = cargar_atributos_canal()
    filas, resultados = [], []
    print(f"{version} · {llm.model} · {llm.region_name} · perfil {llm.profile_name}\n")

    for caso in casos:
        inicio = time.monotonic()
        try:
            done = await VERSIONES[version](llm=llm, timeout=120).run(producto=caso["product"])
            salida = {"publicacion": done.publicacion, "uso": done.uso, "error": done.error}
        except (ClientError, BotoCoreError) as exc:
            salida = {"publicacion": None, "uso": {}, "error": f"Bedrock: {exc}"}
        salida["segundos"] = round(time.monotonic() - inicio, 2)

        resultado = evaluar_caso(salida["publicacion"] or VACIA, caso["expected"], atributos)
        resultados.append(resultado)
        filas.append({"caso": caso["id"], **salida, "exacto": resultado.exacto, "evaluacion": resultado.__dict__})

        marca = "OK " if resultado.exacto else "ERR"
        pendiente = " (decisión pendiente)" if caso.get("decision_pendiente") else ""
        detalle = salida["error"] or (
            f"tp={resultado.tp} fp={resultado.fp} fn={resultado.fn} inválidos={len(resultado.invalidos)}"
        )
        print(f"[{marca}] {caso['id']}{pendiente}: {detalle} · {salida['segundos']}s")

    resumen = resumir(resultados)
    for clave in ("prompt_tokens", "completion_tokens", "cache_read_input_tokens"):
        resumen[clave] = sum(f["uso"].get(clave, 0) for f in filas)
    resumen["segundos_promedio"] = round(sum(f["segundos"] for f in filas) / len(filas), 2)
    print("\n" + json.dumps(resumen, ensure_ascii=False, indent=2))

    carpeta = RAIZ / "resultados"
    carpeta.mkdir(exist_ok=True)
    archivo = carpeta / f"{version}-{datetime.now():%Y%m%d-%H%M%S}.json"
    archivo.write_text(
        json.dumps({"version": version, "modelo": llm.model, "resumen": resumen, "casos": filas},
                   ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\nDetalle en {archivo.relative_to(RAIZ)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version", choices=VERSIONES, default="v1")
    parser.add_argument("--caso", help="id de un caso del dataset; por defecto corre todos")
    args = parser.parse_args()

    casos = [c for c in cargar_dataset() if not args.caso or c["id"] == args.caso]
    if not casos:
        raise SystemExit(f"No existe el caso {args.caso}")
    asyncio.run(_correr(args.version, casos))


if __name__ == "__main__":
    main()
