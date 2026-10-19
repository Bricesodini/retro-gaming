"""Parcours observable de la session d'animation."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SessionState:
    phase: str
    remaining_seconds: float | None
    events: tuple[str, ...]


class Session:
    def advance(
        self, elapsed_seconds: float, animator_action: str | None
    ) -> SessionState:
        """Observe the session after an animator action and elapsed time.

        Only the welcome phase is implemented. No action starts a session yet,
        and time spent in the laboratory does not start a clock.
        """
        return SessionState("laboratoire", None, ())
