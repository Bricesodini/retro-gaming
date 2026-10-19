"""Parcours observable de la session d'animation."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SessionState:
    phase: str
    remaining_seconds: float | None
    events: tuple[str, ...]


class Session:
    def advance(self, elapsed_seconds: float) -> SessionState:
        """Observe the session after elapsed real time.

        The laboratory has no active session clock. Future animator actions
        can start one without changing this public observation boundary.
        """
        return SessionState("laboratoire", None, ())
