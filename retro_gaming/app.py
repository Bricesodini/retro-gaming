"""Original, procedurally drawn welcome screen for the 1986 laboratory."""

import math
from functools import lru_cache

import pygame

from retro_gaming.session import Session


WIDTH = 1200
HEIGHT = 760
FPS = 30

BACKGROUND = (6, 17, 16)
PANEL = (10, 28, 25)
PANEL_LIGHT = (13, 39, 33)
LINE = (38, 85, 67)
GREEN = (127, 226, 166)
GREEN_DIM = (73, 148, 109)
WHITE = (209, 237, 211)
AMBER = (231, 183, 93)

DIAGNOSTICS = (
    "MEMOIRE CENTRALE .............. STABLE",
    "MATRICE DE CONTROLE ............ NOMINALE",
    "CANAL D'OBSERVATION ............ OUVERT",
    "PRESSION CHAMBRE 04 ........... STABLE",
    "LIAISON CAPTEURS ............... ETABLIE",
    "REGISTRE D'ARCHIVES ............ INDEXE",
    "SYNCHRONISATION RESEAU ......... NOMINALE",
    "INTEGRITE DES DONNEES .......... CONFIRMEE",
    "CYCLE DE VEILLE ................ EN COURS",
)


@lru_cache(maxsize=None)
def _font(size: int, bold: bool = False) -> pygame.font.Font:
    return pygame.font.SysFont("menlo,monaco,couriernew,monospace", size, bold=bold)


def _label(
    surface: pygame.Surface,
    font: pygame.font.Font,
    text: str,
    pos: tuple[int, int],
    color: tuple[int, int, int],
) -> None:
    surface.blit(font.render(text, True, color), pos)


def _panel(surface: pygame.Surface, rect: pygame.Rect) -> None:
    pygame.draw.rect(surface, PANEL, rect, border_radius=7)
    pygame.draw.rect(surface, LINE, rect, 1, border_radius=7)


def _draw_grid(surface: pygame.Surface) -> None:
    for x in range(0, WIDTH, 40):
        pygame.draw.line(surface, (11, 35, 29), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, 40):
        pygame.draw.line(surface, (11, 35, 29), (0, y), (WIDTH, y))


def _draw_signal(surface: pygame.Surface, elapsed: float) -> None:
    chart = pygame.Rect(798, 244, 362, 244)
    _panel(surface, chart)
    font = _font(16)
    _label(surface, font, "SIGNAL / CHAMBRE 04", (819, 263), GREEN)
    pygame.draw.line(surface, LINE, (819, 300), (1139, 300))
    for y in (341, 386, 431):
        pygame.draw.line(surface, (24, 57, 46), (819, y), (1139, y), 1)
    points = []
    for x in range(820, 1140, 3):
        phase = (x - 820) / 28 + elapsed * 1.5
        pulse = math.sin(phase) * 9 + math.sin(phase * 0.31) * 5
        points.append((x, int(390 + pulse)))
    pygame.draw.lines(surface, GREEN_DIM, False, points, 2)
    pygame.draw.circle(surface, GREEN, points[-1], 3)
    _label(surface, _font(13), "FLUX REGULIER   |   04.82 mV", (819, 454), GREEN_DIM)


def _draw_diagnostics(surface: pygame.Surface, elapsed: float) -> None:
    panel = pygame.Rect(40, 244, 738, 386)
    _panel(surface, panel)
    _label(surface, _font(16), "JOURNAL DES DIAGNOSTICS", (63, 263), GREEN)
    _label(surface, _font(13), "DEFIL. AUTO  /  CANAL LOCAL", (498, 266), GREEN_DIM)
    pygame.draw.line(surface, LINE, (62, 300), (756, 300))

    count = int(elapsed / 1.45) + 1
    visible = min(count, 10)
    start = count - visible
    for row in range(visible):
        sequence = start + row
        timestamp = f"{(sequence * 7) // 60:02}:{(sequence * 7) % 60:02}"
        message = DIAGNOSTICS[sequence % len(DIAGNOSTICS)]
        y = 320 + row * 27
        _label(surface, _font(15), timestamp, (63, y), GREEN_DIM)
        _label(surface, _font(15), message, (125, y), WHITE if row == visible - 1 else GREEN_DIM)
    if int(elapsed * 2) % 2 == 0:
        _label(surface, _font(17), "_", (65, 598), GREEN)


def _draw_welcome(surface: pygame.Surface, elapsed: float, phase: str) -> None:
    surface.fill(BACKGROUND)
    _draw_grid(surface)
    pygame.draw.rect(surface, GREEN_DIM, pygame.Rect(0, 0, WIDTH, 6))

    _label(surface, _font(14), "INSTITUT DE RECHERCHE  /  SYSTEME LOCAL", (41, 30), GREEN_DIM)
    _label(surface, _font(14), "ARCHIVE 1986       UNITE 04", (907, 30), GREEN_DIM)
    pygame.draw.line(surface, LINE, (40, 62), (1160, 62))

    _label(surface, _font(42, bold=True), "LABORATOIRE", (41, 91), WHITE)
    _label(surface, _font(42, bold=True), "1986", (41, 139), GREEN)
    _label(surface, _font(16), "TERMINAL DE SURVEILLANCE  /  ETAT DES SYSTEMES", (367, 159), GREEN_DIM)
    pygame.draw.rect(surface, GREEN, pygame.Rect(41, 215, 1119, 2))

    _draw_diagnostics(surface, elapsed)
    _draw_signal(surface, elapsed)

    status = pygame.Rect(798, 508, 362, 122)
    _panel(surface, status)
    _label(surface, _font(14), "ETAT DU TERMINAL", (819, 528), GREEN_DIM)
    pygame.draw.circle(surface, GREEN, (828, 584), 5)
    _label(surface, _font(22, bold=True), "SYSTEME EN VEILLE", (845, 570), WHITE)

    pygame.draw.line(surface, LINE, (40, 659), (1160, 659))
    _label(surface, _font(14), "SIMULATION  /  DONNEES FICTIVES", (40, 684), AMBER)
    _label(surface, _font(14), "SESSION EN ATTENTE", (862, 684), GREEN)
    _label(surface, _font(13), "FERMER : ECHAP OU BOUTON DE LA FENETRE", (40, 721), GREEN_DIM)

    # Kept explicit: the display observes the session without starting it.
    assert phase == "laboratoire"


def run() -> None:
    pygame.init()
    try:
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Laboratoire 1986 | Terminal de surveillance")
        clock = pygame.time.Clock()
        session = Session()
        started_at = pygame.time.get_ticks()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
                ):
                    running = False
            if not running:
                break
            elapsed = (pygame.time.get_ticks() - started_at) / 1000
            state = session.advance(elapsed)
            _draw_welcome(screen, elapsed, state.phase)
            pygame.display.flip()
            clock.tick(FPS)
    finally:
        pygame.quit()
