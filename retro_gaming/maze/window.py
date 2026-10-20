"""Keyboard controls and procedural arcade artwork for the maze."""

import math
import pygame

from retro_gaming.maze.game import Game, GameState, PlayerInput, Result
from retro_gaming.rendering import draw_centered_label as _label
from retro_gaming.soundtrack import Soundtrack

CELL = 36
HEADER = 86
FOOTER = 56
BACKGROUND = (3, 5, 15)
WALL = (12, 19, 46)
WALL_EDGE = (58, 92, 240)
FLOOR = BACKGROUND
PELLET = (255, 205, 154)
PLAYER = (255, 222, 65)
ENEMY = (255, 107, 133)
TEXT = (222, 233, 255)
GHOST_COLORS = ((255, 94, 108), (255, 160, 210), (89, 223, 239), (255, 174, 76))


def _draw(surface: pygame.Surface, state: GameState,
          heading: pygame.font.Font, small: pygame.font.Font, elapsed: float = 0) -> None:
    width = len(state.rows[0]) * CELL
    height = len(state.rows) * CELL + HEADER + FOOTER
    surface.fill(BACKGROUND)
    _label(surface, heading, "PAC-MAN", (width // 2, 23), PLAYER)
    _label(surface, small, f"SCORE {state.score:05}      VIES {state.lives} / 3",
           (width // 2, 51), TEXT)
    count = len(state.pellets) + len(state.power_pellets)
    _label(surface, small, f"{count:03} PASTILLES  •  VIDER LE PLATEAU", (width // 2, 72), PELLET)
    for y, row in enumerate(state.rows):
        for x, cell in enumerate(row):
            if cell == "#":
                rect = pygame.Rect(x * CELL + 2, HEADER + y * CELL + 2, CELL - 4, CELL - 4)
                pygame.draw.rect(surface, WALL, rect, border_radius=7)
                pygame.draw.rect(surface, WALL_EDGE, rect, 2, border_radius=7)
    def center(p):
        return (p.x * CELL + CELL // 2, HEADER + p.y * CELL + CELL // 2)
    for pellet in state.pellets:
        pygame.draw.circle(surface, PELLET, center(pellet), 3)
    for pellet in state.power_pellets:
        pygame.draw.circle(surface, PELLET, center(pellet), 8)
        pygame.draw.circle(surface, PLAYER, center(pellet), 11, 1)
    for i, ghost in enumerate(state.ghosts):
        x, y = center(ghost.position)
        if ghost.mode != "returning":
            color = (64, 86, 239) if ghost.mode == "frightened" else GHOST_COLORS[i % 4]
            pygame.draw.circle(surface, color, (x, y - 3), 13)
            pygame.draw.polygon(surface, color, [(x - 13, y - 3), (x + 13, y - 3),
                                (x + 13, y + 12), (x + 7, y + 8), (x, y + 12),
                                (x - 7, y + 8), (x - 13, y + 12)])
        for offset in (-5, 5):
            pygame.draw.circle(surface, TEXT, (x + offset, y - 3), 4)
            if ghost.mode != "frightened":
                dx, dy = ghost.heading
                pygame.draw.circle(surface, BACKGROUND, (x + offset + dx, y - 3 + dy), 2)
        if ghost.mode == "frightened":
            pygame.draw.lines(surface, TEXT, False, [(x - 7, y + 5), (x - 3, y + 3),
                              (x + 1, y + 5), (x + 5, y + 3), (x + 8, y + 5)], 2)
    x, y = center(state.player)
    pygame.draw.circle(surface, PLAYER, (x, y), 13)
    angle = math.atan2(state.direction[1], state.direction[0])
    opening = 0.3 + 0.25 * abs(math.sin(elapsed * 12))
    pygame.draw.polygon(surface, BACKGROUND, [(x, y),
                        (x + 17 * math.cos(angle - opening), y + 17 * math.sin(angle - opening)),
                        (x + 17 * math.cos(angle + opening), y + 17 * math.sin(angle + opening))])
    status = (f"FANTOMES VULNERABLES  {state.frightened_seconds:.1f} s"
              if state.frightened_seconds > 0.05 else "SUPER-PASTILLE : MANGEZ LES FANTOMES")
    _label(surface, small, status, (width // 2, height - 38), PLAYER)
    _label(surface, small, "FLECHES / WASD  •  ECHAP POUR QUITTER", (width // 2, height - 16), TEXT)
    if state.respawn_seconds > 0.05:
        rect = pygame.Rect(40, height // 2 - 24, width - 80, 48)
        pygame.draw.rect(surface, BACKGROUND, rect)
        _label(surface, heading, "PRET ?", rect.center, PLAYER)
    if state.result is not Result.PLAYING:
        veil = pygame.Surface((width, height), pygame.SRCALPHA)
        veil.fill((3, 5, 15, 220))
        surface.blit(veil, (0, 0))
        won = state.result is Result.VICTORY
        _label(surface, heading, "PLATEAU VIDE" if won else "MANCHE PERDUE",
               (width // 2, height // 2 - 32), PLAYER if won else ENEMY)
        _label(surface, small, f"SCORE {state.score:05}  •  VIES {state.lives} / 3",
               (width // 2, height // 2 + 10), TEXT)
        _label(surface, small, "ECHAP POUR QUITTER", (width // 2, height // 2 + 47), PELLET)


def run() -> None:
    pygame.init()
    try:
        game = Game()
        screen = pygame.display.set_mode((len(game.state.rows[0]) * CELL,
                                          len(game.state.rows) * CELL + HEADER + FOOTER))
        pygame.display.set_caption("Pac-Man | Arcade")
        soundtrack = Soundtrack("Mystère") if pygame.mixer.get_init() else None
        heading = pygame.font.SysFont("menlo,monaco,couriernew,monospace", 28, bold=True)
        small = pygame.font.SysFont("menlo,monaco,couriernew,monospace", 14)
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
                up=keys[pygame.K_UP] or keys[pygame.K_w], down=keys[pygame.K_DOWN] or keys[pygame.K_s],
                left=keys[pygame.K_LEFT] or keys[pygame.K_a], right=keys[pygame.K_RIGHT] or keys[pygame.K_d]))
            if soundtrack:
                soundtrack.set_scene("game:maze" if game.state.result is Result.PLAYING else None)
            _draw(screen, game.state, heading, small, time)
            pygame.display.flip()
    finally:
        if "soundtrack" in locals() and soundtrack:
            soundtrack.set_scene(None)
        pygame.quit()
