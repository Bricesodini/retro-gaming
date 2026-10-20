"""Pygame input and original procedural artwork for the space-combat wave."""

import pygame

from retro_gaming.rendering import draw_centered_label as _label
from retro_gaming.space_combat.game import (
    DEFAULT_SCORE_TARGET, ENEMY_HALF_HEIGHT, ENEMY_HALF_WIDTH, Game, GameState, PlayerInput, Result,
)


BACKGROUND = (5, 13, 24)
PANEL = (10, 29, 42)
CYAN = (108, 227, 226)
PALE = (211, 244, 241)
AMBER = (240, 184, 103)
RED = (230, 106, 111)


def _draw_ship(surface: pygame.Surface, x: float, y: float) -> None:
    x, y = round(x), round(y)
    pygame.draw.polygon(surface, CYAN, [(x, y - 28), (x - 23, y + 19),
                                        (x - 11, y + 13), (x + 11, y + 13),
                                        (x + 23, y + 19)])
    pygame.draw.polygon(surface, PANEL, [(x, y - 15), (x - 6, y + 7),
                                         (x + 6, y + 7)])
    pygame.draw.line(surface, AMBER, (x - 9, y + 20), (x + 9, y + 20), 3)


def _draw_enemy(surface: pygame.Surface, x: float, y: float) -> None:
    x, y = round(x), round(y)
    pygame.draw.polygon(surface, RED, [(x - ENEMY_HALF_WIDTH, y - 7),
                                       (x - 10, y - ENEMY_HALF_HEIGHT),
                                       (x + 10, y - ENEMY_HALF_HEIGHT),
                                       (x + ENEMY_HALF_WIDTH, y - 7),
                                       (x + 16, y + 10), (x + 8, y + 6),
                                       (x, y + ENEMY_HALF_HEIGHT), (x - 8, y + 6),
                                       (x - 16, y + 10)])
    pygame.draw.line(surface, BACKGROUND, (x - 8, y - 3), (x + 8, y - 3), 3)


def _draw(surface: pygame.Surface, state: GameState,
          heading: pygame.font.Font, small: pygame.font.Font, elapsed: float = 0) -> None:
    surface.fill(BACKGROUND)
    # Different depths scroll at different speeds; the field continues after a result.
    for index in range(95):
        x = (index * 311 + 67) % state.width
        y = round((index * 197 + 39 + elapsed * (14 + index % 3 * 13)) % state.height)
        shade = 41 + (index * 31) % 55
        pygame.draw.circle(surface, (shade, shade + 14, shade + 25), (x, y),
                           1 + (index % 17 == 0))
    pygame.draw.line(surface, (33, 77, 90), (20, state.height - 2),
                     (state.width - 20, state.height - 2), 2)
    _label(surface, small, f"COMBAT SPATIAL   /   VAGUE {state.wave:02}", (240, 26), CYAN)
    _label(surface, small, f"SCORE {state.score:05} / {state.score_target:05}",
           (state.width - 220, 26), PALE)
    _label(surface, small, f"VIES {state.lives} / 3   •   ATTEINDRE LE SCORE CIBLE",
           (state.width // 2, 54), AMBER)
    for block in state.shelters:
        rect = pygame.Rect(round(block.x - 5), round(block.y - 5), 11, 11)
        pygame.draw.rect(surface, CYAN if block.health == 2 else (57, 137, 150), rect)
        if block.health == 1:
            pygame.draw.line(surface, BACKGROUND, rect.topleft, rect.bottomright, 2)
    for shot in state.enemy_shots:
        x, y = round(shot.x), round(shot.y)
        pygame.draw.lines(surface, RED, False, [(x - 5, y - 12), (x + 5, y - 3), (x - 5, y + 6), (x, y + 12)], 4)
        pygame.draw.circle(surface, AMBER, (x, y + 12), 3)
    for enemy in state.enemies:
        _draw_enemy(surface, enemy.x, enemy.y)
    for shot in state.shots:
        pygame.draw.line(surface, AMBER, (round(shot.x), round(shot.y + 8)),
                         (round(shot.x), round(shot.y - 8)), 3)
    _draw_ship(surface, state.player_x, state.player_y)
    _label(surface, small, "DEPLACER :  ← →  OU  A / D       TIRER : ESPACE",
           (state.width // 2, state.height - 17), PALE)
    if state.respawn_seconds > 0.05:
        _label(surface, heading, "PRET ?", (state.width // 2, state.height // 2), CYAN)
    if state.result is not Result.PLAYING:
        veil = pygame.Surface((state.width, state.height), pygame.SRCALPHA)
        veil.fill((4, 13, 22, 215))
        surface.blit(veil, (0, 0))
        won = state.result is Result.VICTORY
        _label(surface, heading, "OBJECTIF ATTEINT" if won else "MANCHE PERDUE",
               (state.width // 2, state.height // 2 - 30), CYAN if won else RED)
        _label(surface, small,
               f"SCORE {state.score:05} / {state.score_target:05}   •   VIES {state.lives} / 3",
               (state.width // 2, state.height // 2 + 25), PALE)
        _label(surface, small, "ECHAP OU FERMER LA FENETRE POUR QUITTER",
               (state.width // 2, state.height // 2 + 67), AMBER)


def run(score_target: int = DEFAULT_SCORE_TARGET) -> None:
    pygame.init()
    try:
        game = Game(score_target=score_target)
        screen = pygame.display.set_mode((game.state.width, game.state.height))
        pygame.display.set_caption("Combat spatial | Vague 01")
        heading = pygame.font.SysFont("menlo,monaco,couriernew,monospace", 46, bold=True)
        small = pygame.font.SysFont("menlo,monaco,couriernew,monospace", 18)
        clock = pygame.time.Clock()
        running = True
        time = 0.0
        while running:
            elapsed = clock.tick(60) / 1000
            time += elapsed
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
                ):
                    running = False
            if not running:
                break
            keys = pygame.key.get_pressed()
            game.advance(elapsed, PlayerInput(
                left=keys[pygame.K_LEFT] or keys[pygame.K_a],
                right=keys[pygame.K_RIGHT] or keys[pygame.K_d],
                shoot=keys[pygame.K_SPACE],
            ))
            _draw(screen, game.state, heading, small, time)
            pygame.display.flip()
    finally:
        pygame.quit()
