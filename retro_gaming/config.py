"""External calibration for the laboratory demonstration."""

import json
import math
from dataclasses import dataclass
from pathlib import Path

import pygame


RESET_KEY = pygame.K_BACKSPACE
RESET_MODIFIERS = ("ctrl", "alt", "meta")


MODIFIERS = {
    "ctrl": pygame.KMOD_CTRL,
    "alt": pygame.KMOD_ALT,
    "meta": pygame.KMOD_GUI,
    "shift": pygame.KMOD_SHIFT,
}


@dataclass(frozen=True)
class Config:
    session_seconds: float
    possession_seconds: float
    warning_seconds: float
    trigger_key: int
    trigger_modifiers: tuple[str, ...]
    variant: str

    def matches(self, event: pygame.event.Event) -> bool:
        return (
            event.type == pygame.KEYDOWN
            and event.key == self.trigger_key
            and all(event.mod & MODIFIERS[name] for name in self.trigger_modifiers)
            and not any(
                event.mod & flag
                for name, flag in MODIFIERS.items()
                if name not in self.trigger_modifiers
            )
        )


def load_config(path: Path) -> Config:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        session_seconds = float(data["session_seconds"])
        possession_seconds = float(data["possession_seconds"])
        warning_seconds = float(data["warning_seconds"])
        variant = data["variant"]
        if variant not in ("Mystère", "Tension"):
            raise ValueError("variant inconnue : choisir Mystère ou Tension")
        trigger = data["trigger"]
        key = pygame.key.key_code(trigger["key"])
        modifiers = tuple(trigger["modifiers"])
        if not modifiers or len(set(modifiers)) != len(modifiers):
            raise ValueError("la liste des modificateurs doit être unique et non vide")
        if any(name not in MODIFIERS for name in modifiers):
            raise ValueError("modificateur inconnu (ctrl, alt, meta, shift)")
        if key == RESET_KEY and set(modifiers) == set(RESET_MODIFIERS):
            raise ValueError("le déclenchement ne peut pas utiliser le raccourci de remise à zéro (Ctrl + Option + Commande + Backspace)")
        if any(not math.isfinite(value) or value <= 0 for value in
               (session_seconds, possession_seconds, warning_seconds)):
            raise ValueError("les durées de session, possession et avertissement doivent être positives et finies")
        if possession_seconds >= session_seconds:
            raise ValueError("la possession doit être plus courte que la session")
        if warning_seconds >= session_seconds:
            raise ValueError("l’avertissement doit être à l’intérieur de la session")
        return Config(session_seconds, possession_seconds, warning_seconds, key, modifiers, variant)
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
        raise ValueError(f"Configuration invalide dans {path} : {error}") from error
