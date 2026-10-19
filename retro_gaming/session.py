"""Parcours observable de la session d'animation."""

import math
from dataclasses import dataclass
from enum import Enum


class Phase(Enum):
    LABORATOIRE = "laboratoire"
    POSSESSION = "possession"
    ELF = "elf"
    FIN = "fin"


@dataclass(frozen=True)
class SessionState:
    phase: Phase
    remaining_seconds: float | None
    events: tuple[str, ...]
    messages: tuple[str, ...] = ()


class Session:
    def __init__(self, session_seconds: float = 300, possession_seconds: float = 12,
                 warning_seconds: float = 60, variant: str = "Mystère"):
        if variant not in ("Mystère", "Tension"):
            raise ValueError("Variante inconnue : choisir Mystère ou Tension.")
        if any(not math.isfinite(value) or value <= 0 for value in
               (session_seconds, possession_seconds, warning_seconds)):
            raise ValueError("Les durées de session, de possession et d'avertissement doivent être positives et finies.")
        if possession_seconds >= session_seconds:
            raise ValueError("La possession doit être plus courte que la session.")
        if warning_seconds >= session_seconds:
            raise ValueError("L'avertissement doit être avant la fin et à l'intérieur de la session.")
        self.session_seconds = session_seconds
        self.possession_seconds = possession_seconds
        self.warning_seconds = warning_seconds
        self._active_seconds: float | None = None
        self._warning_sent = False
        self._alarm_sent = False

    def advance(self, elapsed_seconds: float, animator_action: str | None) -> SessionState:
        """Advance by elapsed time, then observe the current narrative phase."""
        if not math.isfinite(elapsed_seconds) or elapsed_seconds < 0:
            raise ValueError("Le temps écoulé doit être positif ou nul et fini.")
        if animator_action == "reinitialiser":
            self._active_seconds = None
            self._warning_sent = False
            self._alarm_sent = False
            return SessionState(Phase.LABORATOIRE, None, ())
        if self._active_seconds is None:
            if animator_action != "declencher_mystere":
                return SessionState(Phase.LABORATOIRE, None, ())
            self._active_seconds = 0
        else:
            self._active_seconds += elapsed_seconds

        elapsed = self._active_seconds
        remaining = max(0, self.session_seconds - elapsed)
        events = []
        if remaining <= self.warning_seconds and not self._warning_sent:
            events.append("avertissement")
            self._warning_sent = True
        if remaining == 0 and not self._alarm_sent:
            events.append("alarme")
            self._alarm_sent = True
        if remaining == 0:
            return SessionState(Phase.FIN, 0, tuple(events))
        if elapsed < self.possession_seconds:
            messages = (
                ("ELF // Je vous entends. Restez ensemble.",)
                if elapsed >= self.possession_seconds * 0.65
                else ()
            )
            return SessionState(Phase.POSSESSION, remaining, tuple(events), messages)
        return SessionState(
            Phase.ELF,
            remaining,
            tuple(events),
            (
                "ELF // C'est moi, Elf. Je retiens cette présence.",
                "Un défi vous attend dans ce laboratoire.",
                "Restez ensemble. Les consignes arrivent bientôt.",
            ),
        )
