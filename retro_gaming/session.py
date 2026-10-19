"""Parcours observable de la session d'animation."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SessionState:
    phase: str
    remaining_seconds: float | None
    events: tuple[str, ...]
    messages: tuple[str, ...] = ()


class Session:
    def __init__(self, session_seconds: float = 300, possession_seconds: float = 12):
        if session_seconds <= 0 or possession_seconds <= 0:
            raise ValueError("Les durées de session et de possession doivent être positives.")
        if possession_seconds >= session_seconds:
            raise ValueError("La possession doit être plus courte que la session.")
        self.session_seconds = session_seconds
        self.possession_seconds = possession_seconds
        self._active_seconds: float | None = None

    def advance(
        self, elapsed_seconds: float, animator_action: str | None
    ) -> SessionState:
        """Advance by elapsed time, then observe the current narrative phase."""
        if elapsed_seconds < 0:
            raise ValueError("Le temps écoulé ne peut pas être négatif.")
        if self._active_seconds is None:
            if animator_action != "declencher_mystere":
                return SessionState("laboratoire", None, ())
            self._active_seconds = 0
        else:
            self._active_seconds += elapsed_seconds

        elapsed = self._active_seconds
        remaining = max(0, self.session_seconds - elapsed)
        if elapsed < self.possession_seconds:
            messages = (
                ("ELF // Je vous entends. Restez ensemble.",)
                if elapsed >= self.possession_seconds * 0.65
                else ()
            )
            return SessionState("possession", remaining, (), messages)
        return SessionState(
            "elf",
            remaining,
            (),
            (
                "ELF // C'est moi, Elf. Je retiens cette présence.",
                "Un défi vous attend dans ce laboratoire.",
                "Restez ensemble. Les consignes arrivent bientôt.",
            ),
        )
