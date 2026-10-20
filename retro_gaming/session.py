"""Parcours observable de la session d'animation."""

import math
from dataclasses import dataclass
from enum import Enum


class Phase(Enum):
    LABORATOIRE = "laboratoire"
    POSSESSION = "possession"
    ELF = "elf"
    CHOIX = "choix"
    JEU = "jeu"
    RESULTAT = "resultat"
    FIN = "fin"
    ECHEC = "echec"


@dataclass(frozen=True)
class SessionState:
    phase: Phase
    remaining_seconds: float | None
    events: tuple[str, ...]
    messages: tuple[str, ...] = ()
    available_games: tuple[str, ...] = ()
    active_game: str | None = None
    game_result: str | None = None
    timer_visible: bool = False


GAMES = ("maze", "space_combat", "platformer")


class Session:
    def __init__(self, session_seconds: float = 300, possession_seconds: float = 12,
                 warning_seconds: float = 60):
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
        self._choice_open = False
        self._active_game: str | None = None
        self._game_result: str | None = None
        self._lost_games: list[str] = []
        self._takeover_started: float | None = None
        self._returning_elf = False
        self._failed = False

    def advance(self, elapsed_seconds: float, animator_action: str | None,
                game_result: str | None = None) -> SessionState:
        """Advance by elapsed time, then observe the current narrative phase."""
        if not math.isfinite(elapsed_seconds) or elapsed_seconds < 0:
            raise ValueError("Le temps écoulé doit être positif ou nul et fini.")
        if animator_action == "reinitialiser":
            self._active_seconds = None
            self._warning_sent = False
            self._alarm_sent = False
            self._choice_open = False
            self._active_game = None
            self._game_result = None
            self._lost_games = []
            self._takeover_started = None
            self._returning_elf = False
            self._failed = False
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
            self._active_game = None
            self._game_result = None
            return SessionState(Phase.FIN, 0, tuple(events))
        if elapsed < self.possession_seconds:
            messages = ()
            if elapsed >= self.possession_seconds * 0.35:
                messages = ("ENTITE // Ce terminal m'appartient. Vous êtes pris au piège.",)
            if elapsed >= self.possession_seconds * 0.65:
                messages += ("ELF // Je vous entends. Restez ensemble.",)
            return SessionState(Phase.POSSESSION, remaining, tuple(events), messages,
                                timer_visible=True)
        if self._game_result == "defeat":
            self._lost_games.append(self._active_game)
            self._active_game = None
            self._game_result = None
            self._choice_open = False
            self._takeover_started = elapsed
            self._returning_elf = True
        if self._takeover_started is not None:
            if elapsed - self._takeover_started < self.possession_seconds:
                return SessionState(Phase.POSSESSION, remaining, tuple(events),
                                    ("ENTITE // Ce terminal est à moi.",),
                                    timer_visible=True)
            self._takeover_started = None
            if len(self._lost_games) == len(GAMES):
                self._failed = True
            animator_action = None
        if self._failed:
            return SessionState(Phase.ECHEC, remaining, tuple(events),
                                ("ELF // Je suis revenue.", "DEFI ECHOUE"),
                                timer_visible=True)
        if self._active_game is not None:
            if self._game_result is None and game_result in ("victory", "defeat"):
                self._game_result = game_result
            phase = Phase.RESULTAT if self._game_result else Phase.JEU
            messages = (("PARTIE GAGNEE" if self._game_result == "victory" else "PARTIE PERDUE",)
                        if self._game_result else ())
            return SessionState(phase, remaining, tuple(events), messages,
                                active_game=self._active_game, game_result=self._game_result,
                                timer_visible=True)
        if self._choice_open:
            game = animator_action.removeprefix("choisir_") if animator_action else None
            if game in GAMES and game not in self._lost_games and animator_action.startswith("choisir_"):
                self._active_game = game
                return SessionState(Phase.JEU, remaining, tuple(events), active_game=game,
                                    timer_visible=True)
            return SessionState(Phase.CHOIX, remaining, tuple(events),
                                ("ELF // Choisissez un jeu pour m'aider.",),
                                tuple(game for game in GAMES if game not in self._lost_games),
                                timer_visible=True)
        if animator_action == "continuer":
            self._choice_open = True
            return SessionState(Phase.CHOIX, remaining, tuple(events),
                                ("ELF // Choisissez un jeu pour m'aider.",),
                                tuple(game for game in GAMES if game not in self._lost_games),
                                timer_visible=True)
        if self._returning_elf:
            return SessionState(Phase.ELF, remaining, tuple(events), (
                "ELF // Je suis revenue.",
                "Vous avez une nouvelle chance.",
                "Choisissez un autre jeu pour repousser l'entité.",
            ), timer_visible=True)
        return SessionState(Phase.ELF, remaining, tuple(events), (
            "ELF // C'est moi, Elf. Je retiens cette présence.",
            "L'entité a pris le contrôle du laboratoire.",
            "Un défi vous attend dans ce laboratoire.",
            "J'ai besoin de votre aide pour la repousser.",
            "Appuyez sur ENTREE pour choisir un jeu.",
        ), timer_visible=True)
