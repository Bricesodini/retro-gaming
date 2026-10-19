"""Window-free space-combat simulation driven by elapsed seconds and player input."""

import math
from dataclasses import dataclass
from enum import Enum


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
class GameState:
    width: int
    height: int
    player_x: float
    player_y: float
    player_half_width: float
    enemies: tuple[Enemy, ...]
    shots: tuple[Shot, ...]
    result: Result


class Game:
    """Public seam: advance by seconds and held buttons, then inspect state."""

    def __init__(self):
        self._enemy_direction = 1
        self._shot_cooldown = 0.0
        self.state = GameState(
            width=960,
            height=640,
            player_x=480.0,
            player_y=570.0,
            player_half_width=24.0,
            enemies=tuple(Enemy(240.0 + column * 120, 92.0 + row * 54)
                          for row in range(2) for column in range(5)),
            shots=(),
            result=Result.PLAYING,
        )

    def advance(self, elapsed_seconds: float,
                player_input: PlayerInput = PlayerInput()) -> GameState:
        if not math.isfinite(elapsed_seconds) or elapsed_seconds < 0:
            raise ValueError("Elapsed time must be finite and nonnegative.")
        if self.state.result is not Result.PLAYING:
            return self.state
        remaining = elapsed_seconds
        while remaining > 0 and self.state.result is Result.PLAYING:
            step = min(remaining, 1 / 120)
            self._step(step, player_input)
            remaining -= step
        if elapsed_seconds == 0 and player_input.shoot:
            self._step(0, player_input)
        return self.state

    def _step(self, seconds: float, player_input: PlayerInput) -> None:
        state = self.state
        direction = int(player_input.right) - int(player_input.left)
        player_x = max(state.player_half_width,
                       min(state.width - state.player_half_width,
                           state.player_x + direction * 360 * seconds))

        cooldown = max(0.0, self._shot_cooldown - seconds)
        shots = list(state.shots)
        if player_input.shoot and cooldown == 0:
            shots.append(Shot(player_x, state.player_y - 24))
            cooldown = 0.25
        self._shot_cooldown = cooldown

        enemies = list(state.enemies)
        if enemies:
            delta_x = self._enemy_direction * 80 * seconds
            left = min(enemy.x for enemy in enemies) + delta_x - 22
            right = max(enemy.x for enemy in enemies) + delta_x + 22
            if left < 20 or right > state.width - 20:
                self._enemy_direction *= -1
                # Reflect the overshoot so movement is independent of frame count.
                if left < 20:
                    delta_x += 2 * (20 - left)
                else:
                    delta_x -= 2 * (right - (state.width - 20))
                enemies = [Enemy(enemy.x + delta_x, enemy.y + 28) for enemy in enemies]
            else:
                enemies = [Enemy(enemy.x + delta_x, enemy.y) for enemy in enemies]

        surviving_shots = []
        for shot in shots:
            next_y = shot.y - 760 * seconds
            hit = next((index for index, enemy in enumerate(enemies)
                        if abs(shot.x - enemy.x) <= 22
                        and next_y <= enemy.y + 13 and shot.y >= enemy.y - 13), None)
            if hit is not None:
                enemies.pop(hit)
            elif next_y >= 0:
                surviving_shots.append(Shot(shot.x, next_y))

        result = Result.PLAYING
        if not enemies:
            result = Result.VICTORY
        elif any(enemy.y + 13 >= state.height for enemy in enemies):
            result = Result.DEFEAT
        self.state = GameState(state.width, state.height, player_x, state.player_y,
                               state.player_half_width, tuple(enemies),
                               tuple(surviving_shots), result)
