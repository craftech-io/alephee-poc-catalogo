"""Contrato de salida del agente de catálogo.

Los nombres de campo son los del formato de publicación de Alephee (`valueId`,
`legacyId`), no snake_case: así la salida se compara y se persiste sin traducir.
"""

from pydantic import BaseModel, ConfigDict, Field


class _Estricto(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AtributoMapeado(_Estricto):
    urn: str = Field(description="URN del atributo del canal, copiado exacto de la lista.")
    valueId: str = Field(description="id del valor del dominio del canal, o '0' si el atributo es de texto libre.")
    value: str = Field(description="Nombre del valor tal como figura en el canal.")
    unit: str | None = Field(default=None, description="Unidad aceptada por el canal, o null.")


class Faltante(_Estricto):
    urn: str = Field(description="URN del atributo obligatorio del canal (o 'category').")
    reason: str


class Descartado(_Estricto):
    legacyId: str = Field(description="id del atributo del producto (sin el prefijo urn:attribute:).")
    reason: str


class Publicacion(_Estricto):
    """Resultado del mapeo de un producto a la publicación del canal."""

    category: str | None = Field(description="URN de la categoría del canal, copiado exacto. null si no se puede resolver.")
    attributes: list[AtributoMapeado]
    missing: list[Faltante] = Field(description="Obligatorios del canal (o la categoría) que no se pudieron completar.")
    rejected: list[Descartado] = Field(description="Atributos del producto que se descartan, con el motivo.")
