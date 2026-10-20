"""Original procedural characters, girders and barrels for the climbing arcade."""

import math
import pygame

from retro_gaming.platformer.game import Game, GameState, PlayerInput, Result
from retro_gaming.rendering import draw_centered_label as _label

HEADER = 144
FOOTER = 48
BACKGROUND = (6, 10, 24)
CYAN = (104, 225, 231)
AMBER = (255, 205, 116)
CORAL = (245, 104, 129)
TEXT = (225, 237, 250)
STEEL = (124, 44, 73)
EDGE = (249, 113, 140)


def _barrel(surface, x, foot, rotation=0.0):
    x, y = round(x), round(foot - 12)
    pygame.draw.circle(surface, (151, 83, 46), (x, y), 12)
    pygame.draw.circle(surface, AMBER, (x, y), 12, 2)
    pygame.draw.circle(surface, (67, 38, 32), (x, y), 8, 2)
    for offset in (0, math.pi / 2):
        dx, dy = round(8 * math.cos(rotation + offset)), round(8 * math.sin(rotation + offset))
        pygame.draw.line(surface, AMBER, (x - dx, y - dy), (x + dx, y + dy), 2)


def _fire(surface, x, foot, time, direction=1, scale=1.0, eyes=True):
    x, foot = round(x), round(foot)
    wave = math.sin(time * 10 + x * .03)
    points = [(-13, -2), (-15, -13), (-8, -10), (-7, -25 - wave * 3),
              (-1, -19), (5, -30 + wave * 2), (7, -17), (13, -21), (15, -6), (10, 0)]
    pygame.draw.polygon(surface, (255, 111, 60), [(x + dx * scale, foot + dy * scale) for dx, dy in points])
    pygame.draw.polygon(surface, AMBER, [(x - 8 * scale, foot - 2), (x - 6 * scale, foot - 13 * scale),
                        (x, foot - 10 * scale), (x + 3 * scale, foot - 21 * scale), (x + 8 * scale, foot - 2)])
    if eyes:
        for dx in (-5, 5):
            pygame.draw.rect(surface, TEXT, (x + dx - 3, foot - 14, 6, 6))
            pygame.draw.rect(surface, BACKGROUND, (x + dx - 1 + direction, foot - 13, 3, 4))
        step = round(math.sin(time * 15) * 2)
        pygame.draw.line(surface, (255, 111, 60), (x - 8, foot - 2), (x - 10, foot + step), 4)
        pygame.draw.line(surface, (255, 111, 60), (x + 8, foot - 2), (x + 10, foot - step), 4)


def _ape(surface, x, foot, state):
    """A readable anticipation, forward throw, and recovery tied to real launches."""
    fur, shade, face = (166, 101, 62), (104, 59, 45), (255, 205, 135)
    throwing = state.ape_action == "throw"
    lean = 4 if throwing else 0
    for bx, by in ((x - 42, foot), (x - 42, foot - 24), (x - 18, foot)):
        _barrel(surface, bx, by)
    pygame.draw.ellipse(surface, shade, (x - 28 + lean, foot - 58, 59, 58))
    pygame.draw.ellipse(surface, fur, (x - 24 + lean, foot - 63, 48, 54))
    pygame.draw.ellipse(surface, face, (x - 13 + lean, foot - 39, 28, 28))
    pygame.draw.circle(surface, fur, (x + lean, foot - 66), 23)
    pygame.draw.ellipse(surface, shade, (x - 21 + lean, foot - 76, 42, 28))
    pygame.draw.ellipse(surface, face, (x - 17 + lean, foot - 73, 34, 25))
    pygame.draw.line(surface, shade, (x - 13 + lean, foot - 71), (x + 13 + lean, foot - 71), 5)
    for dx in (-8, 8):
        pygame.draw.rect(surface, BACKGROUND, (x + dx - 3 + lean, foot - 69, 6, 5))
    pygame.draw.rect(surface, BACKGROUND, (x - 8 + lean, foot - 54, 16, 4))
    left_hand = (x - 34, foot - 9)
    right_hand = (x + 34, foot - 9)
    if state.ape_action == "windup":
        phase = max(0, min(1, (state.launch_progress - .7) / .3))
        right_hand = (x + 25 + phase * 17, foot - 43 + phase * 32)
        _barrel(surface, right_hand[0], right_hand[1] + 10, phase * 2)
    elif throwing:
        right_hand = (x + 49, foot - 20)
    for shoulder, hand in (((x - 20 + lean, foot - 44), left_hand),
                           ((x + 20 + lean, foot - 44), right_hand)):
        pygame.draw.line(surface, fur, shoulder, hand, 17)
        pygame.draw.circle(surface, face, (round(hand[0]), round(hand[1])), 8)
    for dx in (-21, 8):
        pygame.draw.rect(surface, fur, (x + dx + lean, foot - 10, 16, 11))


def _princess(surface, x, foot, time):
    sway = round(math.sin(time * 3) * 2)
    pygame.draw.polygon(surface, CORAL, [(x, foot - 32), (x + 16 + sway, foot - 2), (x - 16 + sway, foot - 2)])
    pygame.draw.circle(surface, AMBER, (x, foot - 39), 9)
    pygame.draw.lines(surface, AMBER, False, [(x - 9, foot - 47), (x - 9, foot - 55),
                      (x - 3, foot - 51), (x, foot - 58), (x + 4, foot - 51), (x + 9, foot - 55),
                      (x + 9, foot - 47)], 3)
    pygame.draw.line(surface, TEXT, (x - 12, foot - 24), (x + 12, foot - 24), 3)
    pygame.draw.lines(surface, AMBER, False, [(x - 10, foot - 26), (x - 20, foot - 30),
                      (x - 22 + sway, foot - 41)], 4)


def _player(surface, x, foot, state):
    facing = state.player_facing
    gait = math.sin(state.pose_seconds * 18)
    motion = state.player_motion
    stride = round(gait * 5) if motion in ("walk", "climb") else 0
    def point(dx, dy):
        return (round(x + facing * dx), round(foot + dy))
    leg_y = -3 if motion == "jump" else 0
    # Knees and alternating boots carry the gait; climbing uses raised hands.
    for side in (-1, 1):
        pygame.draw.line(surface, CYAN, point(side * 5, -11), point(side * 5 + stride * side, leg_y - abs(stride)), 6)
        pygame.draw.line(surface, (85, 128, 187), point(side * 5 + stride * side, leg_y - abs(stride)),
                         point(side * 5 + stride * side + 4, leg_y - abs(stride)), 4)
    pygame.draw.rect(surface, CORAL, (x - 9, foot - 24, 18, 12))
    pygame.draw.rect(surface, CYAN, (x - 7, foot - 18, 14, 10))
    pygame.draw.rect(surface, AMBER, (x - 7, foot - 33, 14, 11))
    pygame.draw.rect(surface, CORAL, (x - 9, foot - 36, 17, 5))
    pygame.draw.line(surface, CORAL, point(-7, -31), point(12, -31), 3)
    pygame.draw.rect(surface, BACKGROUND, (*point(3, -29), 3, 3))
    for side in (-1, 1):
        hand_y = -30 + stride * side if motion == "climb" else -29 if motion == "jump" else -13 + stride * side
        pygame.draw.line(surface, AMBER, point(side * 8, -21), point(side * 13, hand_y), 4)


def _draw(surface: pygame.Surface, state: GameState,
          heading: pygame.font.Font, small: pygame.font.Font, elapsed: float = 0) -> None:
    level = state.level
    width, height = level.width, level.height + HEADER + FOOTER
    surface.fill(BACKGROUND)
    _label(surface, heading, "ASCENSION", (150, 27), AMBER)
    _label(surface, small, f"VIES {state.lives} / 3   •   SOMMET {round(state.progress * 100):02}%",
           (width - 210, 24), TEXT)
    _label(surface, small, "REJOIGNEZ LA PRINCESSE  •  BARRIQUES ET FLAMMES EN APPROCHE",
           (width // 2, 51), CYAN)
    for ladder in level.ladders:
        x = round(ladder.x)
        top, bottom = HEADER + round(ladder.top), HEADER + round(ladder.bottom)
        pygame.draw.line(surface, CYAN, (x - 10, top), (x - 10, bottom), 3)
        pygame.draw.line(surface, CYAN, (x + 10, top), (x + 10, bottom), 3)
        for rung in range(top + 9, bottom, 12):
            pygame.draw.line(surface, CYAN, (x - 10, rung), (x + 10, rung), 2)
    for platform in level.walkable_platforms:
        left, right = round(platform.left), round(platform.right)
        y1, y2 = HEADER + platform.height_at(left), HEADER + platform.height_at(right)
        pygame.draw.polygon(surface, STEEL, [(left, y1), (right, y2), (right, y2 + 13), (left, y1 + 13)])
        pygame.draw.line(surface, EDGE, (left, y1), (right, y2), 3)
        pygame.draw.line(surface, EDGE, (left, y1 + 13), (right, y2 + 13), 2)
        for bolt in range(left, right - 17, 24):
            a = HEADER + platform.height_at(bolt)
            b = HEADER + platform.height_at(bolt + 24)
            pygame.draw.lines(surface, EDGE, False, [(bolt, a), (bolt + 12, (a + b) / 2 + 13),
                              (bolt + 24, b)], 1)
    top = level.platforms[-1]
    _ape(surface, round(level.ape_x), round(HEADER + top.height_at(level.ape_x)), state)
    exit_x, exit_y = round(level.exit_x), HEADER + round(level.exit_y)
    _princess(surface, exit_x, exit_y, state.elapsed_seconds)
    _label(surface, small, "PRINCESSE", (exit_x, exit_y - 73), AMBER)
    if level.fire_interval is not None:
        ox, oy = round(level.oil_x), HEADER + round(level.platforms[0].height_at(level.oil_x))
        pygame.draw.rect(surface, (55, 94, 116), (ox - 17, oy - 30, 34, 30))
        for band in (-27, -7):
            pygame.draw.line(surface, CYAN, (ox - 17, oy + band), (ox + 17, oy + band), 3)
        _fire(surface, ox, oy - 28, state.elapsed_seconds, scale=.8, eyes=False)
    for enemy in state.fire_enemies:
        _fire(surface, enemy.x, HEADER + enemy.y, state.elapsed_seconds, enemy.direction)
    for barrel in state.barrels:
        _barrel(surface, barrel.x, HEADER + barrel.y, barrel.rotation)
    _player(surface, round(state.player_x), HEADER + round(state.player_y), state)
    _label(surface, small, "FLECHES / WASD : BOUGER ET GRIMPER    ESPACE : SAUTER",
           (width // 2, height - 33), TEXT)
    _label(surface, small, "ECHAP POUR QUITTER", (width // 2, height - 13), AMBER)
    if state.respawn_seconds > 0.05:
        _label(surface, heading, "PRET ?", (width // 2, height // 2), AMBER)
    if state.result is not Result.PLAYING:
        veil = pygame.Surface((width, height), pygame.SRCALPHA)
        veil.fill((6, 10, 24, 220))
        surface.blit(veil, (0, 0))
        won = state.result is Result.VICTORY
        _label(surface, heading, "PRINCESSE REJOINTE" if won else "MANCHE PERDUE",
               (width // 2, height // 2 - 26), AMBER if won else CORAL)
        _label(surface, small, f"VIES {state.lives} / 3", (width // 2, height // 2 + 18), TEXT)
        _label(surface, small, "ECHAP POUR QUITTER", (width // 2, height // 2 + 53), CYAN)


def run() -> None:
    pygame.init()
    try:
        game = Game()
        screen = pygame.display.set_mode((game.state.level.width, game.state.level.height + HEADER + FOOTER))
        pygame.display.set_caption("Ascension | Arcade originale")
        heading = pygame.font.SysFont("menlo,monaco,couriernew,monospace", 30, bold=True)
        small = pygame.font.SysFont("menlo,monaco,couriernew,monospace", 15)
        clock = pygame.time.Clock()
        running, time = True, 0.0
        while running:
            elapsed = clock.tick(60) / 1000
            time += elapsed
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    running = False
            if not running:
                break
            keys = pygame.key.get_pressed()
            game.advance(elapsed, PlayerInput(
                left=keys[pygame.K_LEFT] or keys[pygame.K_a], right=keys[pygame.K_RIGHT] or keys[pygame.K_d],
                up=keys[pygame.K_UP] or keys[pygame.K_w], down=keys[pygame.K_DOWN] or keys[pygame.K_s],
                jump=keys[pygame.K_SPACE]))
            _draw(screen, game.state, heading, small, time)
            pygame.display.flip()
    finally:
        pygame.quit()
