"""Compara la salida del agente contra la salida esperada del dataset.

Es determinista: no llama a ningún modelo. Sirve para "La prueba" del war room y para
comparar V1, V2 y V3 sobre el mismo dataset.
"""

from collections import Counter
from dataclasses import dataclass, field


@dataclass
class ResultadoCaso:
    categoria_ok: bool
    tp: int
    fp: int
    fn: int
    invalidos: list[str] = field(default_factory=list)
    duplicados: list[str] = field(default_factory=list)
    faltantes_no_detectados: list[str] = field(default_factory=list)
    faltantes_de_mas: list[str] = field(default_factory=list)

    @property
    def exacto(self) -> bool:
        return (
            self.categoria_ok
            and self.fp == 0
            and self.fn == 0
            and not self.invalidos
            and not self.duplicados
            and not self.faltantes_no_detectados
            and not self.faltantes_de_mas
        )


def _clave(attr: dict, atributos_canal: dict[str, dict]) -> tuple:
    """Identidad de un atributo mapeado: por valueId si el canal tiene dominio, por texto si es libre."""
    definicion = atributos_canal.get(attr["urn"])
    if definicion and definicion.get("values"):
        return (attr["urn"], str(attr.get("valueId")))
    return (attr["urn"], str(attr.get("value", "")).strip(), attr.get("unit") or None)


def _es_invalido(attr: dict, atributos_canal: dict[str, dict]) -> bool:
    definicion = atributos_canal.get(attr["urn"])
    if definicion is None:
        return True
    dominio = {v["id"] for v in definicion.get("values", [])}
    return bool(dominio) and str(attr.get("valueId")) not in dominio


def evaluar_caso(pred: dict, esperado: dict, atributos_canal: dict[str, dict]) -> ResultadoCaso:
    attrs_pred = pred.get("attributes") or []
    claves_pred = Counter(_clave(a, atributos_canal) for a in attrs_pred)
    claves_esp = Counter(_clave(a, atributos_canal) for a in esperado["attributes"])
    tp = sum((claves_pred & claves_esp).values())

    conteo_urn = Counter(a["urn"] for a in attrs_pred)
    faltantes_pred = {m["urn"] for m in pred.get("missing") or []}
    faltantes_esp = {m["urn"] for m in esperado["missing"]}

    return ResultadoCaso(
        categoria_ok=pred.get("category") == esperado["category"],
        tp=tp,
        fp=sum(claves_pred.values()) - tp,
        fn=sum(claves_esp.values()) - tp,
        invalidos=[a["urn"] for a in attrs_pred if _es_invalido(a, atributos_canal)],
        duplicados=sorted(urn for urn, n in conteo_urn.items() if n > 1),
        faltantes_no_detectados=sorted(faltantes_esp - faltantes_pred),
        faltantes_de_mas=sorted(faltantes_pred - faltantes_esp),
    )


def resumir(resultados: list[ResultadoCaso]) -> dict:
    tp = sum(r.tp for r in resultados)
    fp = sum(r.fp for r in resultados)
    fn = sum(r.fn for r in resultados)
    return {
        "casos": len(resultados),
        "exactos": sum(r.exacto for r in resultados),
        "categoria_ok": sum(r.categoria_ok for r in resultados),
        "precision": round(tp / (tp + fp), 3) if tp + fp else 0.0,
        "recall": round(tp / (tp + fn), 3) if tp + fn else 0.0,
        "invalidos": sum(len(r.invalidos) for r in resultados),
        "duplicados": sum(len(r.duplicados) for r in resultados),
        "faltantes_no_detectados": sum(len(r.faltantes_no_detectados) for r in resultados),
    }
