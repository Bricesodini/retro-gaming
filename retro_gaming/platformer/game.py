"""Window-free platform round advanced by elapsed seconds and held buttons."""

import math
from dataclasses import dataclass
from enum import Enum


WALK_SPEED = 170.0
CLIMB_SPEED = 145.0
JUMP_SPEED = 430.0
GRAVITY = 950.0
PLAYER_HALF_WIDTH = 10.0
PLAYER_HEIGHT = 25.0
OBSTACLE_HALF_WIDTH = 13.0
OBSTACLE_HEIGHT = 23.0


class Result(Enum):
    PLAYING = "playing"
    VICTORY = "victory"
    DEFEAT = "defeat"


@dataclass(frozen=True)
class Platform:
    left: float
    right: float
    y: float


@dataclass(frozen=True)
class Ladder:
    x: float
    top: float
    bottom: float


@dataclass(frozen=True)
class Obstacle:
    x: float
    y: float
    left: float
    right: float
    speed: float


@dataclass(frozen=True)
class Level:
    width: int
    height: int
    platforms: tuple[Platform, ...]
    ladders: tuple[Ladder, ...]
    exit_x: float
    exit_y: float
    start_x: float
    start_y: float
    obstacles: tuple[Obstacle, ...]


DEFAULT_LEVEL = Level(
    width=860, height=640,
    platforms=(
        Platform(50, 810, 570), Platform(80, 830, 450),
        Platform(30, 780, 330), Platform(80, 830, 210),
        Platform(30, 780, 90),
    ),
    ladders=(
        Ladder(730, 450, 570), Ladder(150, 330, 450),
        Ladder(710, 210, 330), Ladder(160, 90, 210),
    ),
    exit_x=720, exit_y=90, start_x=110, start_y=570,
    obstacles=(
        Obstacle(350, 450, 240, 760, 84),
        Obstacle(570, 330, 250, 680, 96),
        Obstacle(330, 210, 240, 750, 78),
    ),
)


@dataclass(frozen=True)
class PlayerInput:
    left: bool = False
    right: bool = False
    up: bool = False
    down: bool = False
    jump: bool = False


@dataclass(frozen=True)
class GameState:
    level: Level
    player_x: float
    player_y: float  # feet position
    obstacles: tuple[Obstacle, ...]
    result: Result


class Game:
    """Advance one round; the state is observable without opening Pygame."""

    def __init__(self, level: Level = DEFAULT_LEVEL):
        self.state = GameState(level, level.start_x, level.start_y,
                               level.obstacles, Result.PLAYING)
        self._vertical_speed = 0.0
        self._jump_held = False
        self._obstacle_directions = [1] * len(level.obstacles)

    def advance(self, elapsed_seconds: float,
                player_input: PlayerInput = PlayerInput()) -> GameState:
        if not math.isfinite(elapsed_seconds) or elapsed_seconds < 0:
            raise ValueError("Elapsed time must be finite and nonnegative.")
        if self.state.result is not Result.PLAYING:
            return self.state
        jump_pressed = player_input.jump and not self._jump_held
        self._jump_held = player_input.jump
        remaining = elapsed_seconds
        while remaining > 1e-10 and self.state.result is Result.PLAYING:
            step = min(remaining, 1 / 120)
            self._step(step, player_input, jump_pressed)
            jump_pressed = False
            remaining -= step
        return self.state

    def _step(self, seconds: float, buttons: PlayerInput,
              jump_pressed: bool) -> None:
        state = self.state
        level = state.level
        x, y = state.player_x, state.player_y
        grounded = any(platform.left - PLAYER_HALF_WIDTH < x < platform.right + PLAYER_HALF_WIDTH
                       and abs(y - platform.y) < 0.5 for platform in level.platforms)
        ladder = next((ladder for ladder in level.ladders
                       if abs(x - ladder.x) <= 15
                       and ladder.top - 1 <= y <= ladder.bottom + 1), None)
        climbing = ladder is not None and buttons.up != buttons.down
        if climbing:
            x = ladder.x
            y = max(ladder.top, min(ladder.bottom,
                                    y + (int(buttons.down) - int(buttons.up))
                                    * CLIMB_SPEED * seconds))
            self._vertical_speed = 0.0
        else:
            x += (int(buttons.right) - int(buttons.left)) * WALK_SPEED * seconds
            if jump_pressed and grounded:
                self._vertical_speed = -JUMP_SPEED
                grounded = False
            if not grounded:
                previous_y = y
                self._vertical_speed += GRAVITY * seconds
                y += self._vertical_speed * seconds
                if self._vertical_speed >= 0:
                    landing = [platform.y for platform in level.platforms
                               if previous_y <= platform.y <= y
                               and platform.left - PLAYER_HALF_WIDTH < x < platform.right + PLAYER_HALF_WIDTH]
                    if landing:
                        y = min(landing)
                        self._vertical_speed = 0.0

        obstacles = []
        for index, obstacle in enumerate(state.obstacles):
            direction = self._obstacle_directions[index]
            position = obstacle.x + direction * obstacle.speed * seconds
            # Reflect at the patrol ends, including overshoot on a long step.
            if position > obstacle.right:
                position = obstacle.right - (position - obstacle.right)
                direction = -1
            elif position < obstacle.left:
                position = obstacle.left + (obstacle.left - position)
                direction = 1
            self._obstacle_directions[index] = direction
            obstacles.append(Obstacle(position, obstacle.y, obstacle.left,
                                      obstacle.right, obstacle.speed))

        contact = any(abs(x - obstacle.x) < PLAYER_HALF_WIDTH + OBSTACLE_HALF_WIDTH
                      and y > obstacle.y - OBSTACLE_HEIGHT
                      and y - PLAYER_HEIGHT < obstacle.y
                      for obstacle in obstacles)
        result = (Result.DEFEAT if contact or y > level.height + PLAYER_HEIGHT
                  else Result.VICTORY if abs(x - level.exit_x) <= 22
                  and abs(y - level.exit_y) <= 2
                  else Result.PLAYING)
        self.state = GameState(level, x, y, tuple(obstacles), result)
