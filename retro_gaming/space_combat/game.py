"""Fixed-step space combat; the public simulation does not depend on Pygame."""

import math
from dataclasses import dataclass, replace
from enum import Enum

ENEMY_HALF_WIDTH = 22
ENEMY_HALF_HEIGHT = 13
DEFAULT_SCORE_TARGET = 3000
TICK = 1 / 120


class Result(Enum):
    PLAYING = "playing"
    VICTORY = "victory"
    DEFEAT = "defeat"


@dataclass(frozen=True)
class PlayerInput:
    left: bool = False
    right: bool = False
    shoot: bool = False


@dataclass(frozen=True)
class Enemy:
    x: float
    y: float


@dataclass(frozen=True)
class Shot:
    x: float
    y: float


@dataclass(frozen=True)
class ShelterBlock:
    x: float
    y: float
    health: int = 2


@dataclass(frozen=True)
class GameState:
    width: int
    height: int
    player_x: float
    player_y: float
    player_half_width: float
    enemies: tuple[Enemy, ...]
    shots: tuple[Shot, ...]
    result: Result
    enemy_shots: tuple[Shot, ...] = ()
    shelters: tuple[ShelterBlock, ...] = ()
    lives: int = 3
    score: int = 0
    wave: int = 1
    score_target: int = DEFAULT_SCORE_TARGET
    respawn_seconds: float = 0.0


def _formation() -> tuple[Enemy, ...]:
    return tuple(Enemy(240 + col * 120, 100 + row * 54)
                 for row in range(2) for col in range(5))


class Game:
    """A round lasts three lives or until the configured score is reached."""

    def __init__(self, score_target: int = DEFAULT_SCORE_TARGET,
                 enemy_speed_px_per_second: float = 80,
                 salvo_interval_seconds: float = 1.3):
        if isinstance(score_target, bool) or not isinstance(score_target, int) or score_target <= 0:
            raise ValueError("Score target must be a positive integer.")
        for name, value in (("Enemy speed", enemy_speed_px_per_second),
                            ("Salvo interval", salvo_interval_seconds)):
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be positive and finite.")
        self._enemy_speed_px_per_second = enemy_speed_px_per_second
        self._salvo_interval_seconds = salvo_interval_seconds
        self.state = GameState(
            960, 640, 480.0, 570.0, 24.0, _formation(), (), Result.PLAYING,
            shelters=tuple(ShelterBlock(center + (col - 3) * 12, 475 + row * 12)
                           for center in (180, 360, 600, 780)
                           for row in range(3) for col in range(7)
                           if not (row == 2 and 2 <= col <= 4)),
            score_target=score_target,
        )
        self._enemy_direction = 1
        self._shot_cooldown = self._pending = self._salvo_elapsed = 0.0
        self._salvo_number = 0
        self._previous_input = PlayerInput()

    def advance(self, elapsed_seconds: float,
                player_input: PlayerInput = PlayerInput()) -> GameState:
        if not math.isfinite(elapsed_seconds) or elapsed_seconds < 0:
            raise ValueError("Elapsed time must be finite and nonnegative.")
        if self.state.result is not Result.PLAYING:
            return self.state
        if elapsed_seconds == 0:
            if player_input.shoot and self._pending > 1e-10:
                self._step(self._pending, self._previous_input)
                self._pending = 0
            if (self.state.result is Result.PLAYING and player_input.shoot
                    and self._shot_cooldown <= 1e-10 and not self.state.respawn_seconds):
                self.state = replace(self.state, shots=self.state.shots + (Shot(self.state.player_x, self.state.player_y - 24),))
                self._shot_cooldown = 0.25
            return self.state
        # Finish time held under the previous buttons before changing controls.
        if player_input != self._previous_input and self._pending > 1e-10:
            self._step(self._pending, self._previous_input)
            self._pending = 0
            if self.state.result is not Result.PLAYING:
                return self.state
        self._previous_input = player_input
        self._pending += elapsed_seconds
        while self._pending + 1e-10 >= TICK and self.state.result is Result.PLAYING:
            self._pending = max(0, self._pending - TICK)
            self._step(TICK, player_input)
        return self.state

    def _step(self, seconds: float, buttons: PlayerInput) -> None:
        state = self.state
        if state.respawn_seconds > 1e-10:
            self.state = replace(state, respawn_seconds=max(0, state.respawn_seconds - seconds))
            return
        direction = int(buttons.right) - int(buttons.left)
        x = max(state.player_half_width, min(state.width - state.player_half_width,
                                             state.player_x + direction * 360 * seconds))
        shots = list(state.shots)
        self._shot_cooldown = max(0, self._shot_cooldown - seconds)
        if buttons.shoot and self._shot_cooldown <= 1e-10:
            shots.append(Shot(x, state.player_y - 24))
            self._shot_cooldown = 0.25

        enemies = list(state.enemies)
        delta_x = self._enemy_direction * (self._enemy_speed_px_per_second + (state.wave - 1) * 12) * seconds
        left = min(e.x for e in enemies) + delta_x - ENEMY_HALF_WIDTH
        right = max(e.x for e in enemies) + delta_x + ENEMY_HALF_WIDTH
        descent = 0
        if left < 20 or right > state.width - 20:
            self._enemy_direction *= -1
            delta_x += 2 * (20 - left) if left < 20 else -2 * (right - (state.width - 20))
            descent = 28
        enemies = [Enemy(e.x + delta_x, e.y + descent) for e in enemies]

        enemy_shots = list(state.enemy_shots)
        self._salvo_elapsed += seconds
        if self._salvo_elapsed + 1e-10 >= max(0.7, self._salvo_interval_seconds - (state.wave - 1) * 0.08):
            self._salvo_elapsed = 0
            # Only the lowest invader in a column fires; three columns per salvo.
            columns = sorted({round(e.x, 4) for e in enemies})
            for column in columns[self._salvo_number % 2::2]:
                shooter = max((e for e in enemies if round(e.x, 4) == column), key=lambda e: e.y)
                enemy_shots.append(Shot(shooter.x, shooter.y + 18))
            self._salvo_number += 1

        blocks = list(state.shelters)
        def hit_shelter(shot, next_y):
            hits = [(i, b) for i, b in enumerate(blocks) if abs(shot.x - b.x) <= 7
                    and min(shot.y, next_y) <= b.y + 6 and max(shot.y, next_y) >= b.y - 6]
            if not hits:
                return False
            i, b = min(hits, key=lambda pair: abs(pair[1].y - shot.y))
            if b.health == 1:
                blocks.pop(i)
            else:
                blocks[i] = replace(b, health=b.health - 1)
            return True

        surviving_shots = []
        score = state.score
        for shot in shots:
            y = shot.y - 760 * seconds
            if hit_shelter(shot, y):
                continue
            hits = [(i, e) for i, e in enumerate(enemies) if abs(shot.x - e.x) <= ENEMY_HALF_WIDTH
                    and y <= e.y + ENEMY_HALF_HEIGHT and shot.y >= e.y - ENEMY_HALF_HEIGHT]
            if hits:
                i, _ = max(hits, key=lambda pair: pair[1].y)
                enemies.pop(i)
                score += 100
            elif y >= 0:
                surviving_shots.append(Shot(shot.x, y))
        incoming = []
        contact = False
        for shot in enemy_shots:
            y = shot.y + (230 + 15 * (state.wave - 1)) * seconds
            if hit_shelter(shot, y):
                continue
            if abs(shot.x - x) <= state.player_half_width and shot.y <= state.player_y + 19 and y >= state.player_y - 24:
                contact = True
            elif y < state.height:
                incoming.append(Shot(shot.x, y))
        # A descending formation erodes bunkers too, so it never hides inside them.
        blocks = [b for b in blocks if not any(abs(e.x - b.x) < 28 and abs(e.y - b.y) < 20 for e in enemies)]
        invasion = any(e.y + ENEMY_HALF_HEIGHT >= state.player_y - 24 for e in enemies)
        state = replace(state, player_x=x, enemies=tuple(enemies), shots=tuple(surviving_shots),
                        enemy_shots=tuple(incoming), shelters=tuple(blocks), score=score)
        if score >= state.score_target:
            state = replace(state, result=Result.VICTORY)
        elif contact or invasion:
            lives = state.lives - 1
            state = replace(state, lives=lives, player_x=480.0, shots=(), enemy_shots=(),
                            enemies=_formation() if invasion else state.enemies,
                            respawn_seconds=1.0 if lives else 0.0,
                            result=Result.PLAYING if lives else Result.DEFEAT)
            self._shot_cooldown = self._salvo_elapsed = 0
            if invasion:
                self._enemy_direction = 1
        if state.result is Result.PLAYING and not state.enemies:
            state = replace(state, wave=state.wave + 1, enemies=_formation(), shots=(), enemy_shots=())
            self._enemy_direction = 1
            self._salvo_elapsed = 0
        self.state = state
