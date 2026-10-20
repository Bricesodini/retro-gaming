"""Deterministic grid arcade, observable without a Pygame window."""

import math
from collections import deque
from dataclasses import dataclass, replace
from enum import Enum

PLAYER_STEP_SECONDS = 0.15
ENEMY_STEP_SECONDS = 0.45
POWER_SECONDS = 6.0
DIRECTIONS = ((1, 0), (0, 1), (-1, 0), (0, -1))
BEHAVIORS = ("chase", "ambush", "alternate", "roam")
DEFAULT_ROWS = (
    "###############",
    "#P...........o#",
    "#.###.#.#.###.#",
    "#.....#.#.....#",
    "#.###.#.#.###.#",
    "#...#.....#...#",
    "###.#.###.#.###",
    "#o....EEEE....#",
    "#.###.###.###.#",
    "#...#.....#...#",
    "#.#.#.###.#.#.#",
    "#.#.........#.#",
    "#.###.#.#.###.#",
    "#o....#.#....o#",
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
class Ghost:
    position: Position
    home: Position
    behavior: str
    mode: str = "hunting"
    return_seconds: float = 0.0
    heading: tuple[int, int] = (0, 0)


@dataclass(frozen=True)
class GameState:
    rows: tuple[str, ...]
    player: Position
    pellets: frozenset[Position]
    ghosts: tuple[Ghost, ...]
    result: Result
    power_pellets: frozenset[Position] = frozenset()
    lives: int = 3
    score: int = 0
    frightened_seconds: float = 0.0
    respawn_seconds: float = 0.0
    direction: tuple[int, int] = (1, 0)

    @property
    def enemies(self) -> tuple[Position, ...]:
        return tuple(g.position for g in self.ghosts if g.mode != "returning")


class Game:
    """Advance held inputs and elapsed seconds; terminal states stay visible."""

    def __init__(self, rows: tuple[str, ...] = DEFAULT_ROWS,
                 pellet_goal_percent: float = 100,
                 ghost_step_seconds: float = ENEMY_STEP_SECONDS,
                 power_seconds: float = POWER_SECONDS):
        if not rows or not rows[0] or any(len(r) != len(rows[0]) for r in rows):
            raise ValueError("Maze rows must have one nonempty width.")
        if (isinstance(pellet_goal_percent, bool) or not isinstance(pellet_goal_percent, (int, float))
                or not math.isfinite(pellet_goal_percent) or not 0 < pellet_goal_percent <= 100):
            raise ValueError("Pellet goal percent must be between 0 and 100.")
        for name, value in (("Ghost step seconds", ghost_step_seconds), ("Power seconds", power_seconds)):
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be positive and finite.")
        players = [Position(x, y) for y, row in enumerate(rows)
                   for x, cell in enumerate(row) if cell == "P"]
        if len(players) != 1:
            raise ValueError("Maze must have one player start.")
        self._start = players[0]
        homes = [Position(x, y) for y, row in enumerate(rows)
                 for x, cell in enumerate(row) if cell == "E"]
        self.state = GameState(
            rows, self._start,
            frozenset(Position(x, y) for y, row in enumerate(rows)
                      for x, cell in enumerate(row) if cell == "."),
            tuple(Ghost(p, p, BEHAVIORS[i % 4]) for i, p in enumerate(homes)),
            Result.PLAYING,
            frozenset(Position(x, y) for y, row in enumerate(rows)
                      for x, cell in enumerate(row) if cell == "o"),
        )
        self._pellet_goal_percent = pellet_goal_percent
        self._pellet_total = len(self.state.pellets) + len(self.state.power_pellets)
        self._ghost_step_seconds = ghost_step_seconds
        self._power_seconds = power_seconds
        self._player_elapsed = self._enemy_elapsed = self._time = 0.0

    def advance(self, elapsed_seconds: float,
                player_input: PlayerInput = PlayerInput()) -> GameState:
        if not math.isfinite(elapsed_seconds) or elapsed_seconds < 0:
            raise ValueError("Elapsed time must be finite and nonnegative.")
        remaining = elapsed_seconds
        while remaining > 1e-10 and self.state.result is Result.PLAYING:
            if self.state.respawn_seconds > 1e-10:
                pause = min(remaining, self.state.respawn_seconds)
                self.state = replace(self.state, respawn_seconds=max(0, self.state.respawn_seconds - pause))
                remaining -= pause
                continue
            step = min(remaining, PLAYER_STEP_SECONDS - self._player_elapsed,
                       self._ghost_step_seconds - self._enemy_elapsed)
            self._player_elapsed += step
            self._enemy_elapsed += step
            self._time += step
            self._timers(step)
            remaining -= step
            if self._player_elapsed + 1e-10 >= PLAYER_STEP_SECONDS:
                self._player_elapsed = 0
                self._move_player(player_input)
            if (self.state.result is Result.PLAYING and not self.state.respawn_seconds
                    and self._enemy_elapsed + 1e-10 >= self._ghost_step_seconds):
                self._enemy_elapsed = 0
                self._move_ghosts()
        return self.state

    def _timers(self, seconds: float) -> None:
        power = max(0, self.state.frightened_seconds - seconds)
        ghosts = []
        for g in self.state.ghosts:
            remaining = max(0, g.return_seconds - seconds)
            mode = ("returning" if remaining > 1e-10 else
                    "frightened" if power > 1e-10 else "hunting")
            ghosts.append(replace(g, return_seconds=remaining, mode=mode))
        self.state = replace(self.state, ghosts=tuple(ghosts), frightened_seconds=power)

    def _move_player(self, buttons: PlayerInput) -> None:
        direction = self._direction(buttons)
        if direction is None:
            return
        target = Position(self.state.player.x + direction[0], self.state.player.y + direction[1])
        if not self._is_floor(target):
            return
        state = self.state
        is_power = target in state.power_pellets
        score = state.score + (50 if is_power else 10 if target in state.pellets else 0)
        self.state = replace(state, player=target, direction=direction, score=score,
                             pellets=state.pellets - {target}, power_pellets=state.power_pellets - {target},
                             frightened_seconds=self._power_seconds if is_power else state.frightened_seconds)
        if is_power:
            self._timers(0)
        self._contact()
        collected = self._pellet_total - len(self.state.pellets) - len(self.state.power_pellets)
        if (self.state.result is Result.PLAYING and not self.state.respawn_seconds
                and self._pellet_total > 0
                and collected * 100 >= self._pellet_total * self._pellet_goal_percent):
            self.state = replace(self.state, result=Result.VICTORY)

    def _move_ghosts(self) -> None:
        ghosts = []
        for index, g in enumerate(self.state.ghosts):
            if g.mode == "returning":
                ghosts.append(g)
                continue
            options = [(Position(g.position.x + dx, g.position.y + dy), (dx, dy))
                       for dx, dy in DIRECTIONS
                       if self._is_floor(Position(g.position.x + dx, g.position.y + dy))]
            forward = [(p, d) for p, d in options if d != (-g.heading[0], -g.heading[1])]
            options = forward or options
            if not options:
                ghosts.append(g)
                continue
            target = self.state.player
            if g.behavior == "ambush":
                dx, dy = self.state.direction
                target = Position(target.x + 3 * dx, target.y + 3 * dy)
            elif g.behavior == "alternate" and int(self._time / 4) % 2 == 0:
                target = Position(len(self.state.rows[0]) - 2, 1)
            elif g.behavior == "roam":
                corners = (Position(1, 1), Position(len(self.state.rows[0]) - 2, 1),
                           Position(len(self.state.rows[0]) - 2, len(self.state.rows) - 2),
                           Position(1, len(self.state.rows) - 2))
                target = corners[(int(self._time / 3) + index) % 4]
            distances = self._distances(target)
            def distance(option):
                return distances.get(option[0], 1000)
            position, heading = (max(options, key=distance) if g.mode == "frightened"
                                 else min(options, key=distance))
            ghosts.append(replace(g, position=position, heading=heading))
        self.state = replace(self.state, ghosts=tuple(ghosts))
        self._contact()

    def _distances(self, target: Position) -> dict[Position, int]:
        # Project an ambush point inside a wall onto the closest walkable tile.
        floors = [Position(x, y) for y, row in enumerate(self.state.rows)
                  for x, cell in enumerate(row) if cell != "#"]
        target = min(floors, key=lambda p: abs(p.x - target.x) + abs(p.y - target.y))
        distances = {target: 0}
        queue = deque([target])
        while queue:
            p = queue.popleft()
            for dx, dy in DIRECTIONS:
                q = Position(p.x + dx, p.y + dy)
                if q not in distances and self._is_floor(q):
                    distances[q] = distances[p] + 1
                    queue.append(q)
        return distances

    def _contact(self) -> None:
        touching = [g for g in self.state.ghosts if g.position == self.state.player and g.mode != "returning"]
        if any(g.mode == "hunting" for g in touching):
            lives = self.state.lives - 1
            self.state = replace(self.state, lives=lives, frightened_seconds=0,
                                 result=Result.PLAYING if lives else Result.DEFEAT,
                                 player=self._start if lives else self.state.player,
                                 ghosts=tuple(Ghost(g.home, g.home, g.behavior) for g in self.state.ghosts),
                                 respawn_seconds=1.0 if lives else 0.0)
            self._player_elapsed = self._enemy_elapsed = 0.0
        elif touching:
            self.state = replace(self.state, score=self.state.score + 200 * len(touching),
                                 ghosts=tuple(replace(g, position=g.home, mode="returning", return_seconds=2.0)
                                              if g in touching else g for g in self.state.ghosts))

    def _is_floor(self, p: Position) -> bool:
        return (0 <= p.y < len(self.state.rows) and 0 <= p.x < len(self.state.rows[0])
                and self.state.rows[p.y][p.x] != "#")

    @staticmethod
    def _direction(buttons: PlayerInput) -> tuple[int, int] | None:
        for active, direction in ((buttons.up, (0, -1)), (buttons.down, (0, 1)),
                                  (buttons.left, (-1, 0)), (buttons.right, (1, 0))):
            if active:
                return direction
        return None
