"""Fixed-step climbing arcade, independent of the Pygame presentation."""

import math
from dataclasses import dataclass, replace
from enum import Enum

WALK_SPEED = 170.0
CLIMB_SPEED = 145.0
JUMP_SPEED = 360.0
GRAVITY = 950.0
PLAYER_HALF_WIDTH = 10.0
PLAYER_HEIGHT = 25.0
BARREL_RADIUS = 12.0
TICK = 1 / 120


class Result(Enum):
    PLAYING = "playing"
    VICTORY = "victory"
    DEFEAT = "defeat"


@dataclass(frozen=True)
class Platform:
    left: float
    right: float
    y: float  # height of the left end; screen coordinates increase downward
    slope: float = 0.0

    def height_at(self, x: float) -> float:
        return self.y + (x - self.left) * self.slope


@dataclass(frozen=True)
class Ladder:
    x: float
    top: float
    bottom: float


@dataclass(frozen=True)
class Barrel:
    x: float
    y: float  # bottom, as for the player's feet
    platform: int
    direction: int = 1
    speed: float = 110.0
    phase: str = "rolling"
    serial: int = 1
    ladder: int = -1
    rotation: float = 0.0
    vertical_speed: float = 0.0


@dataclass(frozen=True)
class FireEnemy:
    x: float
    y: float
    platform: int
    direction: int = -1
    speed: float = 44.0
    ladder: int = -1
    target_platform: int = -1
    turn_seconds: float = 0.0


@dataclass(frozen=True)
class Level:
    width: int
    height: int
    platforms: tuple[Platform, ...]  # bottom to top
    ladders: tuple[Ladder, ...]
    exit_x: float  # princess
    exit_y: float
    start_x: float
    start_y: float
    barrels: tuple[Barrel, ...] = ()
    barrel_interval: float | None = None  # no launcher in small test scenes
    barrel_speed: float = 110.0
    ape_x: float = 90.0
    fire_enemies: tuple[FireEnemy, ...] = ()
    fire_interval: float | None = None
    oil_x: float = 65.0
    rescue_platform: Platform | None = None
    barrel_speed_limit: float = 170.0
    fire_limit: int = 4
    fire_speed: float = 40.0

    @property
    def walkable_platforms(self) -> tuple[Platform, ...]:
        return self.platforms + ((self.rescue_platform,) if self.rescue_platform is not None else ())

    def with_tuning(self, *, barrel_interval_seconds: float,
                    barrel_speed_px_per_second: float,
                    barrel_speed_cap_px_per_second: float,
                    fire_spawn_interval_seconds: float,
                    fire_speed_px_per_second: float) -> "Level":
        """Apply session tuning to new hazards and those already on the level."""
        barrel_factor = barrel_speed_px_per_second / self.barrel_speed
        fire_factor = fire_speed_px_per_second / self.fire_speed
        return replace(
            self, barrel_interval=barrel_interval_seconds,
            barrel_speed=barrel_speed_px_per_second,
            barrel_speed_limit=barrel_speed_cap_px_per_second,
            fire_interval=fire_spawn_interval_seconds,
            fire_speed=fire_speed_px_per_second,
            barrels=tuple(replace(barrel, speed=barrel.speed * barrel_factor)
                          for barrel in self.barrels),
            fire_enemies=tuple(replace(enemy, speed=enemy.speed * fire_factor)
                              for enemy in self.fire_enemies),
        )


# Six alternating ramps keep the ape on the upper left while every climb
# approaches the next ladder uphill, against the descending barrels.
_GIRDERS = tuple(Platform(40, 820, y, slope)
                 for y, slope in ((590, -.025), (471, .025), (402, -.025),
                                  (283, .025), (214, -.025), (95, .025)))
_LADDER_X = (750, 110, 750, 110, 750)
_RESCUE_PLATFORM = Platform(610, 800, 20)
DEFAULT_LEVEL = Level(
    860, 640, _GIRDERS,
    tuple(Ladder(x, _GIRDERS[i + 1].height_at(x), _GIRDERS[i].height_at(x))
          for i, x in enumerate(_LADDER_X))
    + (Ladder(750, _RESCUE_PLATFORM.y, _GIRDERS[-1].height_at(750)),),
    650, _RESCUE_PLATFORM.y, 110, _GIRDERS[0].height_at(110),
    barrels=(Barrel(600, _GIRDERS[0].height_at(600), 0, direction=-1, speed=85),),
    barrel_interval=4.0,
    barrel_speed=85.0,
    fire_enemies=(FireEnemy(420, _GIRDERS[2].height_at(420), 2, speed=28),
                  FireEnemy(620, _GIRDERS[4].height_at(620), 4, speed=24)),
    fire_interval=14.0,
    rescue_platform=_RESCUE_PLATFORM,
    barrel_speed_limit=125.0,
    fire_limit=3,
    fire_speed=26.0,
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
    player_y: float
    barrels: tuple[Barrel, ...]
    result: Result
    lives: int = 3
    respawn_seconds: float = 0.0
    climbing: bool = False
    progress: float = 0.0
    launch_interval: float = 3.2
    barrels_launched: int = 0
    fire_enemies: tuple[FireEnemy, ...] = ()
    fire_spawned: int = 0
    elapsed_seconds: float = 0.0
    player_motion: str = "idle"
    player_facing: int = 1
    pose_seconds: float = 0.0
    ape_action: str = "idle"
    throw_seconds: float = 0.0
    launch_progress: float = 0.0


class Game:
    """Held controls + elapsed seconds expose all gameplay without a window."""

    def __init__(self, level: Level = DEFAULT_LEVEL, goal_progress_percent: float = 100):
        if (isinstance(goal_progress_percent, bool)
                or not isinstance(goal_progress_percent, (int, float))
                or not math.isfinite(goal_progress_percent)
                or not 0 < goal_progress_percent <= 100):
            raise ValueError("Goal progress percent must be between 0 and 100.")
        self._goal_progress_percent = goal_progress_percent
        self.state = GameState(level, level.start_x, level.start_y, level.barrels,
                               Result.PLAYING, launch_interval=level.barrel_interval or 0,
                               fire_enemies=level.fire_enemies)
        self._vertical_speed = self._pending = self._launch_elapsed = 0.0
        self._jump_held = self._jump_pending = False
        self._previous_input = PlayerInput()
        self._fire_elapsed = 0.0

    def advance(self, elapsed_seconds: float,
                player_input: PlayerInput = PlayerInput()) -> GameState:
        if not math.isfinite(elapsed_seconds) or elapsed_seconds < 0:
            raise ValueError("Elapsed time must be finite and nonnegative.")
        if self.state.result is not Result.PLAYING or elapsed_seconds == 0:
            return self.state
        # Preserve short taps on either side of a simulation tick boundary.
        if player_input != self._previous_input and self._pending > 1e-10:
            self._step(self._pending, self._previous_input, self._jump_pending)
            self._jump_pending = False
            self._pending = 0
            if self.state.result is not Result.PLAYING:
                return self.state
        self._previous_input = player_input
        self._jump_pending |= player_input.jump and not self._jump_held
        self._jump_held = player_input.jump
        self._pending += elapsed_seconds
        while self._pending + 1e-10 >= TICK and self.state.result is Result.PLAYING:
            self._pending = max(0, self._pending - TICK)
            self._step(TICK, player_input, self._jump_pending)
            self._jump_pending = False
        return self.state

    def _step(self, seconds: float, buttons: PlayerInput, jump_pressed: bool) -> None:
        state = self.state
        if state.respawn_seconds > 1e-10:
            self.state = replace(state, respawn_seconds=max(0, state.respawn_seconds - seconds))
            return
        level = state.level
        x, y = state.player_x, state.player_y
        support = next((p for p in level.walkable_platforms if p.left <= x <= p.right
                        and abs(y - p.height_at(x)) < 0.5), None)
        candidates = [l for l in level.ladders if abs(x - l.x) <= 15
                      and l.top - 1 <= y <= l.bottom + 1]
        # At the shared endpoint, up continues into the higher ladder section.
        ladder = min(candidates, key=lambda l: l.top if buttons.up else -l.bottom if buttons.down else 0,
                     default=None)
        vertical = int(buttons.down) - int(buttons.up)
        horizontal = int(buttons.right) - int(buttons.left)
        climbing = ladder is not None and (vertical != 0 or state.climbing) and not horizontal and not jump_pressed
        if climbing:
            x = ladder.x
            y = max(ladder.top, min(ladder.bottom, y + vertical * CLIMB_SPEED * seconds))
            self._vertical_speed = 0
        else:
            x += horizontal * WALK_SPEED * seconds
            if jump_pressed and (support is not None or state.climbing):
                self._vertical_speed = -JUMP_SPEED
                support = None
            if support is not None and support.left <= x <= support.right:
                y = support.height_at(x)
            else:
                previous_y = y
                self._vertical_speed += GRAVITY * seconds
                y += self._vertical_speed * seconds
                if self._vertical_speed >= 0:
                    landing = [p.height_at(x) for p in level.walkable_platforms if p.left <= x <= p.right
                               and previous_y - 0.5 <= p.height_at(x) <= y]
                    if landing:
                        y = min(landing)
                        self._vertical_speed = 0
        ascent = max(1, level.start_y - level.exit_y)
        progress = max(0, min(1, (level.start_y - y) / ascent))
        base_interval = level.barrel_interval or 3.2
        # Keep the early ascent's ramp, but cap the increase in launch pressure.
        interval = max(1.0, base_interval * 0.8, base_interval * (1 - 0.6 * progress))
        barrels = []
        for b in state.barrels:
            moved = self._move_barrel(b, seconds)
            if moved is not None:
                barrels.append(moved)
        launched = state.barrels_launched
        throw_seconds = max(0, state.throw_seconds - seconds)
        if level.barrel_interval is not None:
            self._launch_elapsed += seconds
            if self._launch_elapsed + 1e-10 >= interval:
                self._launch_elapsed = 0
                launched += 1
                throw_seconds = 0.3
                top = level.platforms[-1]
                release_x = level.ape_x + (40 if top.slope >= 0 else -40)
                barrels.append(Barrel(release_x, top.height_at(release_x), len(level.platforms) - 1,
                                      direction=1 if top.slope >= 0 else -1,
                                      speed=level.barrel_speed * (1 + 0.3 * progress), serial=launched))
        fire_enemies = tuple(self._move_fire(enemy, seconds, x, y) for enemy in state.fire_enemies)
        fire_spawned = state.fire_spawned
        if level.fire_interval is not None and len(fire_enemies) < level.fire_limit:
            self._fire_elapsed += seconds
            if self._fire_elapsed + 1e-10 >= level.fire_interval:
                self._fire_elapsed = 0
                fire_spawned += 1
                fire_enemies += (FireEnemy(level.oil_x, level.platforms[0].height_at(level.oil_x), 0,
                                           speed=level.fire_speed * (1 + progress * 0.3)),)
        fire_contact = any(abs(x - enemy.x) < 19 and y > enemy.y - 24
                           and y - PLAYER_HEIGHT < enemy.y for enemy in fire_enemies)
        oil_y = level.platforms[0].height_at(level.oil_x)
        oil_contact = (level.fire_interval is not None and abs(x - level.oil_x) < 25
                       and y > oil_y - 55 and y - PLAYER_HEIGHT < oil_y)
        contact = fire_contact or oil_contact or any(abs(x - b.x) < PLAYER_HALF_WIDTH + BARREL_RADIUS - 2
                      and y > b.y - BARREL_RADIUS * 2 and y - PLAYER_HEIGHT < b.y for b in barrels)
        grounded = any(p.left <= x <= p.right and abs(y - p.height_at(x)) < 0.5 for p in level.walkable_platforms)
        motion = ("climb" if climbing and vertical else "idle" if climbing else
                  "jump" if not grounded else "walk" if horizontal else "idle")
        launch_progress = self._launch_elapsed / interval if level.barrel_interval is not None else 0
        action = "throw" if throw_seconds > 1e-10 else "windup" if launch_progress >= .7 else "idle"
        state = replace(state, player_x=x, player_y=y, barrels=tuple(barrels), climbing=climbing,
                        elapsed_seconds=state.elapsed_seconds + seconds,
                        player_motion=motion, player_facing=horizontal or state.player_facing,
                        pose_seconds=state.pose_seconds + seconds if motion == state.player_motion else 0,
                        ape_action=action, throw_seconds=throw_seconds, launch_progress=launch_progress,
                        progress=progress, launch_interval=interval, barrels_launched=launched,
                        fire_enemies=fire_enemies, fire_spawned=fire_spawned)
        if contact or y > level.height + PLAYER_HEIGHT:
            lives = state.lives - 1
            state = replace(state, lives=lives, player_x=level.start_x, player_y=level.start_y,
                            barrels=level.barrels, fire_enemies=level.fire_enemies, climbing=False, progress=0,
                            player_motion="hurt", pose_seconds=0, ape_action="idle", throw_seconds=0, launch_progress=0,
                            result=Result.PLAYING if lives else Result.DEFEAT,
                            respawn_seconds=1.0 if lives else 0.0)
            self._vertical_speed = self._launch_elapsed = self._fire_elapsed = 0
        elif ((self._goal_progress_percent < 100 and (climbing or grounded)
               and progress * 100 >= self._goal_progress_percent)
              or (abs(x - level.exit_x) <= 22 and abs(y - level.exit_y) <= 3)):
            state = replace(state, result=Result.VICTORY)
        self.state = state

    def _move_fire(self, enemy: FireEnemy, seconds: float,
                   player_x: float, player_y: float) -> FireEnemy:
        level = self.state.level
        cooldown = max(0, enemy.turn_seconds - seconds)
        if enemy.ladder >= 0:
            ladder = level.ladders[enemy.ladder]
            destination = level.platforms[enemy.target_platform].height_at(ladder.x)
            direction_y = 1 if destination > enemy.y else -1
            y = enemy.y + direction_y * enemy.speed * 1.1 * seconds
            if (y - destination) * direction_y >= 0:
                return replace(enemy, y=destination, platform=enemy.target_platform,
                               ladder=-1, target_platform=-1, turn_seconds=1.0)
            return replace(enemy, y=y)
        platform = level.platforms[enemy.platform]
        player_floor = min(range(len(level.platforms)),
                           key=lambda i: abs(player_y - level.platforms[i].height_at(player_x)))
        target_x = player_x
        route = None
        if player_floor != enemy.platform and cooldown <= 1e-10:
            target_floor = enemy.platform + (1 if player_floor > enemy.platform else -1)
            other = level.platforms[target_floor]
            routes = [(i, ladder) for i, ladder in enumerate(level.ladders)
                      if abs(min(platform.height_at(ladder.x), other.height_at(ladder.x)) - ladder.top) < 1
                      and abs(max(platform.height_at(ladder.x), other.height_at(ladder.x)) - ladder.bottom) < 1]
            if routes:
                route = min(routes, key=lambda item: abs(enemy.x - item[1].x))
                target_x = route[1].x
        direction = 1 if target_x > enemy.x else -1
        distance = enemy.speed * seconds
        x = enemy.x + max(-distance, min(distance, target_x - enemy.x))
        x = max(platform.left + 12, min(platform.right - 12, x))
        if route is not None and abs(x - target_x) <= 1:
            return replace(enemy, x=target_x, y=platform.height_at(target_x), direction=direction,
                           ladder=route[0], target_platform=target_floor, turn_seconds=0)
        return replace(enemy, x=x, y=platform.height_at(x), direction=direction, turn_seconds=cooldown)

    def _move_barrel(self, b: Barrel, seconds: float) -> Barrel | None:
        level = self.state.level
        platform = level.platforms[b.platform]
        if b.phase == "rolling":
            direction = 1 if platform.slope > 0 else -1 if platform.slope < 0 else b.direction
            speed = min(level.barrel_speed_limit, b.speed + GRAVITY * abs(platform.slope) * seconds)
            b = replace(b, direction=direction, speed=speed)
            x = b.x + direction * speed * seconds
            if b.serial % 3 == 0 and b.platform > 0:
                for i, ladder in enumerate(level.ladders):
                    if (abs(ladder.top - platform.height_at(ladder.x)) < 1
                            and min(b.x, x) <= ladder.x <= max(b.x, x)):
                        return replace(b, x=ladder.x, y=ladder.top, phase="ladder", ladder=i)
            if x < platform.left or x > platform.right:
                edge = platform.left if x < platform.left else platform.right
                return replace(b, x=edge, y=platform.height_at(edge), phase="falling", vertical_speed=0,
                               rotation=b.rotation + (edge - b.x) / BARREL_RADIUS)
            return replace(b, x=x, y=platform.height_at(x), rotation=b.rotation + (x - b.x) / BARREL_RADIUS)
        vertical_speed = b.speed * 1.4 if b.phase == "ladder" else b.vertical_speed + GRAVITY * seconds
        y = b.y + vertical_speed * seconds
        b = replace(b, vertical_speed=vertical_speed)
        if b.platform == 0:
            return None if y > level.height + 30 else replace(b, y=y)
        lower = level.platforms[b.platform - 1]
        landing = (level.ladders[b.ladder].bottom if b.phase == "ladder" else lower.height_at(b.x))
        if y >= landing:
            return replace(b, y=landing, platform=b.platform - 1, phase="rolling", ladder=-1, vertical_speed=0,
                           direction=1 if lower.slope > 0 else -1 if lower.slope < 0 else -b.direction)
        return replace(b, y=y, rotation=b.rotation + seconds * b.direction * 5)
