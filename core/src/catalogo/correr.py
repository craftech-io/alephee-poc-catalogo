"""Corre una versión del agente de catálogo sobre un dataset y la evalúa (modo batch).

    scripts/correr.sh --version v1                      # 10 casos mock
    scripts/correr.sh --version v1 --datos real         # 30 productos de WarRoom.zip
    scripts/correr.sh --version actual --datos real     # el proceso de hoy, sin llamar al modelo
    scripts/correr.sh --version v1 --caso 03-valor-en-otro-idioma
"""

import argparse
import asyncio
import json
import os
import time
from datetime import datetime

from botocore.exceptions import BotoCoreError, ClientError

from .datos import RAIZ, cargar_atributos_canal, cargar_dataset
from .evaluacion import evaluar_caso, resumir

VACIA = {"category": None, "attributes": [], "missing": [], "rejected": []}


def _versiones() -> dict:
    from . import v1

    return {"v1": v1.MapeoV1}


def _proceso_actual(caso: dict) -> dict:
    """La publicación que genera hoy Alephee, en el contrato del agente. Nunca informa
    faltantes: hoy publica igual."""
    actual = caso.get("actual")
    if not actual:
        return {"publicacion": None, "uso": {}, "error": "El caso no trae la publicación actual (dataset mock)"}
    publicacion = {
        "category": actual["category"],
        "attributes": [{k: a[k] for k in ("urn", "valueId", "value", "unit")} for a in actual["attributes"]],
        "missing": [],
        "rejected": [],
    }
    return {"publicacion": publicacion, "uso": {}, "error": None}


async def _correr(version: str, casos: list[dict], datos: str) -> None:
    llm = None
    if version != "actual":
        from .llm import crear_llm

        llm = crear_llm()
        print(f"{version} · {llm.model} · {llm.region_name} · perfil {llm.profile_name} · datos {datos}\n")
    else:
        print(f"proceso actual de Alephee · datos {datos}\n")

    filas, resultados = [], []
    for caso in casos:
        inicio = time.monotonic()
        if llm is None:
            salida = _proceso_actual(caso)
        else:
            try:
                done = await _versiones()[version](llm=llm, timeout=180).run(producto=caso["product"])
                salida = {"publicacion": done.publicacion, "uso": done.uso, "error": done.error}
            except (ClientError, BotoCoreError) as exc:
                if "sso" in str(exc).lower() or "credential" in str(exc).lower():
                    raise SystemExit(f"Credenciales de AWS vencidas o ausentes: {exc}\n"
                                     f"Correr: aws sso login --profile {llm.profile_name}") from exc
                salida = {"publicacion": None, "uso": {}, "error": f"Bedrock: {exc}"}
        salida["segundos"] = round(time.monotonic() - inicio, 2)

        esperado = caso["expected"]
        atributos = cargar_atributos_canal(esperado["category"])
        resultado = evaluar_caso(salida["publicacion"] or VACIA, esperado, atributos)
        resultados.append(resultado)
        filas.append({"caso": caso["id"], **salida, "exacto": resultado.exacto, "evaluacion": resultado.__dict__})

        marca = "OK " if resultado.exacto else "ERR"
        pendiente = " (decisión pendiente)" if caso.get("decision_pendiente") else ""
        detalle = salida["error"] or (
            f"tp={resultado.tp} fp={resultado.fp} fn={resultado.fn} inválidos={len(resultado.invalidos)}"
            f" duplicados={len(resultado.duplicados)}"
        )
        print(f"[{marca}] {caso['id']}{pendiente}: {detalle} · {salida['segundos']}s")

    resumen = resumir(resultados)
    for clave in ("prompt_tokens", "completion_tokens", "cache_read_input_tokens"):
        resumen[clave] = sum(f["uso"].get(clave, 0) for f in filas)
    resumen["segundos_promedio"] = round(sum(f["segundos"] for f in filas) / len(filas), 2)
    print("\n" + json.dumps(resumen, ensure_ascii=False, indent=2))

    carpeta = RAIZ / "resultados"
    carpeta.mkdir(exist_ok=True)
    archivo = carpeta / f"{version}-{datos}-{datetime.now():%Y%m%d-%H%M%S}.json"
    archivo.write_text(
        json.dumps({"version": version, "datos": datos, "modelo": llm.model if llm else None,
                    "resumen": resumen, "casos": filas}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\nDetalle en {archivo.relative_to(RAIZ)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version", choices=["actual", *_versiones()], default="v1")
    parser.add_argument("--datos", choices=["mock", "real"], default="mock")
    parser.add_argument("--caso", help="id de un caso del dataset; por defecto corre todos")
    args = parser.parse_args()

    os.environ.setdefault("DATA_DIR", str(RAIZ / "data" / args.datos))
    casos = [c for c in cargar_dataset() if not args.caso or c["id"] == args.caso]
    if not casos:
        raise SystemExit(f"No existe el caso {args.caso}")
    asyncio.run(_correr(args.version, casos, args.datos))


if __name__ == "__main__":
    main()
