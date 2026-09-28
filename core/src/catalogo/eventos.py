"""Eventos de los workflows de mapeo. Compartidos por V1, V2 y V3."""

from workflows.events import StartEvent, StopEvent


class MapeoStart(StartEvent):
    producto: dict


class MapeoDone(StopEvent):
    """Fin del mapeo de un producto.

    Los campos no se llaman `result`: colisionaría con el de `StopEvent` (ver
    `agent/events.py`).
    """

    publicacion: dict | None
    uso: dict = {}
    error: str | None = None
    herramientas_usadas: list[str] = []
