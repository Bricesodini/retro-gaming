"""Pygame controls and procedural artwork for the standalone maze."""

import pygame

from retro_gaming.maze.game import Game, GameState, PlayerInput, Result


CELL = 44
HEADER = 66
FOOTER = 42
BACKGROUND = (6, 15, 28)
WALL = (28, 74, 102)
WALL_EDGE = (91, 174, 188)
FLOOR = (12, 29, 43)
PELLET = (242, 187, 104)
PLAYER = (112, 231, 214)
ENEMY = (231, 113, 138)
TEXT = (213, 238, 239)


def _label(surface: pygame.Surface, font: pygame.font.Font, value: str,
           center: tuple[int, int], color: tuple[int, int, int]) -> None:
    image = font.render(value, True, color)
    surface.blit(image, image.get_rect(center=center))


def _draw(surface: pygame.Surface, state: GameState,
          heading: pygame.font.Font, small: pygame.font.Font) -> None:
    width = len(state.rows[0]) * CELL
    height = len(state.rows) * CELL + HEADER + FOOTER
    surface.fill(BACKGROUND)
    _label(surface, heading, "LABYRINTHE", (width // 2, 26), PLAYER)
    _label(surface, small, f"PASTILLES RESTANTES  {len(state.pellets):02}",
           (width // 2, 53), TEXT)
    for y, row in enumerate(state.rows):
        for x, cell in enumerate(row):
            rect = pygame.Rect(x * CELL, HEADER + y * CELL, CELL, CELL)
            if cell == "#":
                pygame.draw.rect(surface, WALL, rect)
                pygame.draw.rect(surface, WALL_EDGE, rect.inflate(-5, -5), 2,
                                 border_radius=6)
            else:
                pygame.draw.rect(surface, FLOOR, rect)
                pygame.draw.rect(surface, (20, 45, 59), rect, 1)
    for pellet in state.pellets:
        center = (pellet.x * CELL + CELL // 2,
                  HEADER + pellet.y * CELL + CELL // 2)
        pygame.draw.circle(surface, PELLET, center, 4)
    for enemy in state.enemies:
        x = enemy.x * CELL + CELL // 2
        y = HEADER + enemy.y * CELL + CELL // 2
        pygame.draw.polygon(surface, ENEMY,
                            [(x, y - 15), (x + 16, y), (x, y + 15), (x - 16, y)])
        pygame.draw.circle(surface, BACKGROUND, (x, y), 4)
    player_center = (state.player.x * CELL + CELL // 2,
                     HEADER + state.player.y * CELL + CELL // 2)
    pygame.draw.circle(surface, PLAYER, player_center, 15)
    pygame.draw.circle(surface, FLOOR, player_center, 6)
    _label(surface, small, "FLECHES OU WASD POUR BOUGER  •  ECHAP POUR QUITTER",
           (width // 2, height - FOOTER // 2), TEXT)
    if state.result is not Result.PLAYING:
        veil = pygame.Surface((width, height), pygame.SRCALPHA)
        veil.fill((4, 13, 22, 213))
        surface.blit(veil, (0, 0))
        won = state.result is Result.VICTORY
        _label(surface, heading, "PLATEAU VIDE" if won else "MANCHE PERDUE",
               (width // 2, height // 2 - 27), PLAYER if won else ENEMY)
        _label(surface, small,
               "TOUTES LES PASTILLES RAMASSEES" if won else "CONTACT AVEC UN ADVERSAIRE",
               (width // 2, height // 2 + 22), TEXT)
        _label(surface, small, "ECHAP OU FERMER LA FENETRE POUR QUITTER",
               (width // 2, height // 2 + 60), PELLET)


def run() -> None:
    pygame.init()
    try:
        game = Game()
        width = len(game.state.rows[0]) * CELL
        height = len(game.state.rows) * CELL + HEADER + FOOTER
        screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Labyrinthe original | Manche 01")
        heading = pygame.font.SysFont("menlo,monaco,couriernew,monospace", 30,
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
                up=keys[pygame.K_UP] or keys[pygame.K_w],
                down=keys[pygame.K_DOWN] or keys[pygame.K_s],
                left=keys[pygame.K_LEFT] or keys[pygame.K_a],
                right=keys[pygame.K_RIGHT] or keys[pygame.K_d],
            ))
            _draw(screen, game.state, heading, small)
            pygame.display.flip()
    finally:
        pygame.quit()
