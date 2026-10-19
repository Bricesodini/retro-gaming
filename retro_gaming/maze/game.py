"""Window-free maze rules driven by elapsed seconds and held directions."""

import math
from dataclasses import dataclass
from enum import Enum


PLAYER_STEP_SECONDS = 0.15
ENEMY_STEP_SECONDS = 0.45
ENEMY_DIRECTIONS = ((1, 0), (0, 1), (-1, 0), (0, -1))
DEFAULT_ROWS = (
    "###############",
    "#P............#",
    "#.###.###.###.#",
    "#...#...#...#.#",
    "###.#.#.#.#.#.#",
    "#...#.#...#...#",
    "#.###.#####.###",
    "#.....#.....E.#",
    "#.###.#.###.#.#",
    "#.............#",
    "###############",
)


class Result(Enum):
    PLAYING = "playing"
    VICTORY = "victory"
    DEFEAT = "defeat"


@dataclass(frozen=True)
class Position:
    x: int
    y: int


@dataclass(frozen=True)
class PlayerInput:
    up: bool = False
    down: bool = False
    left: bool = False
    right: bool = False


@dataclass(frozen=True)
class GameState:
    rows: tuple[str, ...]
    player: Position
    pellets: frozenset[Position]
    enemies: tuple[Position, ...]
    result: Result


class Game:
    """Advance a maze round and inspect its public state without a window."""

    def __init__(self, rows: tuple[str, ...] = DEFAULT_ROWS):
        if not rows or any(len(row) != len(rows[0]) for row in rows):
            raise ValueError("Maze rows must have one nonempty width.")
        players = [Position(x, y) for y, row in enumerate(rows)
                   for x, cell in enumerate(row) if cell == "P"]
        if len(players) != 1:
            raise ValueError("Maze must have one player start.")
        self.state = GameState(
            rows=rows,
            player=players[0],
            pellets=frozenset(Position(x, y) for y, row in enumerate(rows)
                              for x, cell in enumerate(row) if cell == "."),
            enemies=tuple(Position(x, y) for y, row in enumerate(rows)
                          for x, cell in enumerate(row) if cell == "E"),
            result=Result.PLAYING,
        )
        self._player_elapsed = 0.0
        self._enemy_elapsed = 0.0
        self._enemy_headings = [0] * len(self.state.enemies)

    def advance(self, elapsed_seconds: float,
                player_input: PlayerInput = PlayerInput()) -> GameState:
        if not math.isfinite(elapsed_seconds) or elapsed_seconds < 0:
            raise ValueError("Elapsed time must be finite and nonnegative.")
        if self.state.result is not Result.PLAYING:
            return self.state
        remaining = elapsed_seconds
        while remaining > 1e-10 and self.state.result is Result.PLAYING:
            until_player = PLAYER_STEP_SECONDS - self._player_elapsed
            until_enemy = (ENEMY_STEP_SECONDS - self._enemy_elapsed
                           if self.state.enemies else math.inf)
            step = min(remaining, until_player, until_enemy)
            self._player_elapsed += step
            self._enemy_elapsed += step
            remaining -= step
            if self._player_elapsed + 1e-10 >= PLAYER_STEP_SECONDS:
                self._player_elapsed = 0.0
                self._move_player(player_input)
            if (self.state.result is Result.PLAYING and self.state.enemies
                    and self._enemy_elapsed + 1e-10 >= ENEMY_STEP_SECONDS):
                self._enemy_elapsed = 0.0
                self._move_enemies()
        return self.state

    def _move_player(self, player_input: PlayerInput) -> None:
        direction = self._direction(player_input)
        if direction is None:
            return
        next_position = Position(self.state.player.x + direction[0],
                                 self.state.player.y + direction[1])
        if not self._is_floor(next_position):
            return
        pellets = self.state.pellets - {next_position}
        result = (Result.DEFEAT if next_position in self.state.enemies else
                  Result.VICTORY if not pellets else Result.PLAYING)
        self.state = GameState(self.state.rows, next_position, pellets,
                               self.state.enemies, result)

    def _move_enemies(self) -> None:
        positions = []
        for index, enemy in enumerate(self.state.enemies):
            for turn in range(4):
                heading = (self._enemy_headings[index] + turn) % 4
                dx, dy = ENEMY_DIRECTIONS[heading]
                next_position = Position(enemy.x + dx, enemy.y + dy)
                if self._is_floor(next_position):
                    self._enemy_headings[index] = heading
                    positions.append(next_position)
                    break
            else:
                positions.append(enemy)
        enemies = tuple(positions)
        result = (Result.DEFEAT if self.state.player in enemies
                  else self.state.result)
        self.state = GameState(self.state.rows, self.state.player,
                               self.state.pellets, enemies, result)

    def _is_floor(self, position: Position) -> bool:
        return (0 <= position.y < len(self.state.rows)
                and 0 <= position.x < len(self.state.rows[0])
                and self.state.rows[position.y][position.x] != "#")

    @staticmethod
    def _direction(player_input: PlayerInput) -> tuple[int, int] | None:
        if player_input.up:
            return 0, -1
        if player_input.down:
            return 0, 1
        if player_input.left:
            return -1, 0
        if player_input.right:
            return 1, 0
        return None
