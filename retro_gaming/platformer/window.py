"""Pygame controls and procedural artwork for the platform round."""

import pygame

from retro_gaming.platformer.game import (
    Game, GameState, PLAYER_HEIGHT, PLAYER_HALF_WIDTH, PlayerInput, Result,
)
from retro_gaming.rendering import draw_centered_label as _label


HEADER = 58
FOOTER = 48
BACKGROUND = (6, 15, 28)
FIELD = (11, 29, 43)
CYAN = (112, 231, 214)
AMBER = (242, 187, 104)
CORAL = (231, 113, 138)
TEXT = (213, 238, 239)
STEEL = (30, 78, 101)
EDGE = (87, 166, 182)


def _draw(surface: pygame.Surface, state: GameState,
          heading: pygame.font.Font, small: pygame.font.Font) -> None:
    level = state.level
    width, height = level.width, level.height + HEADER + FOOTER
    surface.fill(BACKGROUND)
    pygame.draw.rect(surface, FIELD, (0, HEADER, width, level.height))
    for index in range(48):
        x = (index * 233 + 47) % width
        y = HEADER + (index * 149 + 31) % level.height
        pygame.draw.circle(surface, (26, 64, 80), (x, y), 1)

    _label(surface, heading, "ASCENSION", (width // 2, 27), CYAN)
    _label(surface, small, "SORTIE  /  NIVEAU UNIQUE", (width - 150, 29), TEXT)

    for ladder in level.ladders:
        x = round(ladder.x)
        top, bottom = HEADER + round(ladder.top), HEADER + round(ladder.bottom)
        pygame.draw.line(surface, AMBER, (x - 11, top), (x - 11, bottom), 4)
        pygame.draw.line(surface, AMBER, (x + 11, top), (x + 11, bottom), 4)
        for rung in range(top + 11, bottom, 17):
            pygame.draw.line(surface, (157, 123, 78),
                             (x - 11, rung), (x + 11, rung), 3)

    for platform in level.platforms:
        left, top = round(platform.left), HEADER + round(platform.y)
        length = round(platform.right - platform.left)
        pygame.draw.rect(surface, STEEL, (left, top, length, 15))
        pygame.draw.rect(surface, EDGE, (left, top, length, 4))
        for bolt in range(left + 13, left + length - 7, 37):
            pygame.draw.circle(surface, (9, 33, 49), (bolt, top + 10), 2)

    exit_x, exit_y = round(level.exit_x), HEADER + round(level.exit_y)
    pygame.draw.rect(surface, AMBER, (exit_x - 23, exit_y - 48, 46, 48), 3)
    pygame.draw.rect(surface, (47, 70, 73), (exit_x - 17, exit_y - 42, 34, 42))
    pygame.draw.line(surface, CYAN, (exit_x - 9, exit_y - 32),
                     (exit_x + 9, exit_y - 32), 3)
    _label(surface, small, "SORTIE", (exit_x, exit_y - 59), AMBER)

    for obstacle in state.obstacles:
        x, y = round(obstacle.x), HEADER + round(obstacle.y)
        pygame.draw.polygon(surface, CORAL,
                            [(x, y - 24), (x + 14, y - 11),
                             (x + 10, y - 2), (x - 10, y - 2),
                             (x - 14, y - 11)])
        pygame.draw.rect(surface, BACKGROUND, (x - 5, y - 17, 10, 4))
        pygame.draw.circle(surface, AMBER, (x, y - 15), 2)

    x, foot = round(state.player_x), HEADER + round(state.player_y)
    body = pygame.Rect(x - round(PLAYER_HALF_WIDTH),
                       foot - round(PLAYER_HEIGHT),
                       round(PLAYER_HALF_WIDTH * 2), round(PLAYER_HEIGHT))
    pygame.draw.rect(surface, CYAN, body, border_radius=5)
    pygame.draw.rect(surface, BACKGROUND, (x - 6, foot - 18, 12, 5),
                     border_radius=2)
    pygame.draw.circle(surface, AMBER, (x, foot - 7), 3)

    _label(surface, small,
           "BOUGER / GRIMPER : FLECHES OU WASD    SAUTER : ESPACE    QUITTER : ECHAP",
           (width // 2, height - FOOTER // 2), TEXT)
    if state.result is not Result.PLAYING:
        veil = pygame.Surface((width, height), pygame.SRCALPHA)
        veil.fill((4, 13, 22, 220))
        surface.blit(veil, (0, 0))
        won = state.result is Result.VICTORY
        _label(surface, heading, "SORTIE ATTEINTE" if won else "MANCHE PERDUE",
               (width // 2, height // 2 - 26), CYAN if won else CORAL)
        _label(surface, small,
               "PARCOURS TERMINE" if won else "CONTACT OU CHUTE",
               (width // 2, height // 2 + 22), TEXT)
        _label(surface, small, "ECHAP OU FERMER LA FENETRE POUR QUITTER",
               (width // 2, height // 2 + 60), AMBER)


def run() -> None:
    pygame.init()
    try:
        game = Game()
        width = game.state.level.width
        height = game.state.level.height + HEADER + FOOTER
        screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Ascension | Arcade originale")
        heading = pygame.font.SysFont("menlo,monaco,couriernew,monospace", 31,
                                      bold=True)
        small = pygame.font.SysFont("menlo,monaco,couriernew,monospace", 15)
        clock = pygame.time.Clock()
        running = True
        while running:
            elapsed = clock.tick(60) / 1000
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
                up=keys[pygame.K_UP] or keys[pygame.K_w],
                down=keys[pygame.K_DOWN] or keys[pygame.K_s],
                jump=keys[pygame.K_SPACE],
            ))
            _draw(screen, game.state, heading, small)
            pygame.display.flip()
    finally:
        pygame.quit()
