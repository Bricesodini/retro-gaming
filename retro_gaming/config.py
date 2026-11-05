"""External calibration for the retro gaming session."""

import json
import math
from dataclasses import dataclass, field, fields
from pathlib import Path

import pygame



RESET_KEY = pygame.K_SPACE
RESET_MODIFIERS = ("ctrl", "alt", "meta")


MODIFIERS = {
    "ctrl": pygame.KMOD_CTRL,
    "alt": pygame.KMOD_ALT,
    "meta": pygame.KMOD_GUI,
    "shift": pygame.KMOD_SHIFT,
}


@dataclass(frozen=True)
class MazeSettings:
    pellet_goal_percent: float = 100
    ghost_step_seconds: float = 0.45
    power_seconds: float = 6


@dataclass(frozen=True)
class SpaceCombatSettings:
    score_target: int = 3000
    enemy_speed_px_per_second: float = 80
    salvo_interval_seconds: float = 1.3


@dataclass(frozen=True)
class PlatformerSettings:
    goal_progress_percent: float = 100
    barrel_interval_seconds: float = 4
    barrel_speed_px_per_second: float = 85
    barrel_speed_cap_px_per_second: float = 125
    fire_spawn_interval_seconds: float = 14
    fire_speed_px_per_second: float = 26


@dataclass(frozen=True)
class GameSettings:
    maze: MazeSettings = field(default_factory=MazeSettings)
    space_combat: SpaceCombatSettings = field(default_factory=SpaceCombatSettings)
    platformer: PlatformerSettings = field(default_factory=PlatformerSettings)


def _game_settings(data: object) -> GameSettings:
    if not isinstance(data, dict):
        raise ValueError("games doit être un objet JSON")
    unknown = set(data) - {"maze", "space_combat", "platformer"}
    if unknown:
        raise ValueError(f"games contient un jeu inconnu : {', '.join(sorted(unknown))}")

    def read(name: str, settings_type):
        supplied = data.get(name, {})
        if not isinstance(supplied, dict):
            raise ValueError(f"games.{name} doit être un objet JSON")
        defaults = settings_type()
        expected = {item.name for item in fields(defaults)}
        unknown_fields = set(supplied) - expected
        if unknown_fields:
            raise ValueError(f"games.{name} contient un réglage inconnu : {', '.join(sorted(unknown_fields))}")
        values = {}
        for item in fields(defaults):
            value = supplied.get(item.name, getattr(defaults, item.name))
            label = f"games.{name}.{item.name}"
            if item.name == "score_target":
                if type(value) is not int or value <= 0:
                    raise ValueError(f"{label} doit être un entier positif")
            elif (isinstance(value, bool) or not isinstance(value, (int, float))
                  or not math.isfinite(value) or value <= 0):
                raise ValueError(f"{label} doit être un nombre positif et fini")
            elif item.name.endswith("_percent") and value > 100:
                raise ValueError(f"{label} doit être entre 0 et 100")
            values[item.name] = value
        return settings_type(**values)

    maze = read("maze", MazeSettings)
    space = read("space_combat", SpaceCombatSettings)
    platformer = read("platformer", PlatformerSettings)
    if platformer.barrel_speed_cap_px_per_second < platformer.barrel_speed_px_per_second:
        raise ValueError("games.platformer.barrel_speed_cap_px_per_second doit atteindre au moins barrel_speed_px_per_second")
    return GameSettings(maze, space, platformer)


@dataclass(frozen=True)
class Config:
    session_seconds: float
    possession_seconds: float
    warning_seconds: float
    variant: str
    room_digit: int = 4
    games: GameSettings = field(default_factory=GameSettings)

def load_config(path: Path) -> Config:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        session_seconds = float(data["session_seconds"])
        possession_seconds = float(data["possession_seconds"])
        warning_seconds = float(data["warning_seconds"])
        games = _game_settings(data.get("games", {}))
        variant = data["variant"]
        room_digit = data.get("room_digit", 4)
        if type(room_digit) is not int or not 0 <= room_digit <= 9:
            raise ValueError("le chiffre de salle doit être un entier de 0 à 9")
        if variant not in ("Mystère", "Tension"):
            raise ValueError("variant inconnue : choisir Mystère ou Tension")
        if "trigger" in data:
            raise ValueError("trigger n'est plus configurable : Entrée ouvre le dossier")
        if any(not math.isfinite(value) or value <= 0 for value in
               (session_seconds, possession_seconds, warning_seconds)):
            raise ValueError("les durées de session, possession et avertissement doivent être positives et finies")
        if possession_seconds >= session_seconds:
            raise ValueError("la possession doit être plus courte que la session")
        if warning_seconds >= session_seconds:
            raise ValueError("l’avertissement doit être à l’intérieur de la session")
        return Config(session_seconds, possession_seconds, warning_seconds,
                      variant, room_digit, games)
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
        raise ValueError(f"Configuration invalide dans {path} : {error}") from error
