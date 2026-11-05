"""Police-record terminal, gradual possession and Elf contact."""

import argparse
import math
from array import array
from functools import lru_cache
from pathlib import Path

import pygame

from retro_gaming.config import GameSettings, MODIFIERS, RESET_KEY, RESET_MODIFIERS, load_config
from retro_gaming.session import DOSSIER_OPEN_SECONDS, ENTITY_DELAY_SECONDS, Phase, Session
from retro_gaming.maze import game as maze_game, window as maze_window
from retro_gaming.space_combat import game as space_game, window as space_window
from retro_gaming.platformer import game as platform_game, window as platform_window
from retro_gaming.soundtrack import Soundtrack


WIDTH = 1200
HEIGHT = 960
DISPLAY_WIDTH = 1280
DISPLAY_HEIGHT = 1024
FPS = 30

BACKGROUND = (6, 17, 16)
PANEL = (10, 28, 25)
PANEL_LIGHT = (13, 39, 33)
LINE = (38, 85, 67)
GREEN = (127, 226, 166)
GREEN_DIM = (73, 148, 109)
WHITE = (209, 237, 211)
AMBER = (231, 183, 93)
RED = (169, 79, 73)
RED_DIM = (92, 49, 48)

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


def _draw_keycap(surface: pygame.Surface, text: str, center: tuple[int, int],
                 width: int | None = None, highlighted: bool = True) -> None:
    """Draw a keyboard key as a physical, readable control hint."""
    font = _font(17, bold=True)
    width = width or max(62, font.size(text)[0] + 24)
    rect = pygame.Rect(0, 0, width, 38)
    rect.center = center
    color = GREEN if highlighted else GREEN_DIM
    pygame.draw.rect(surface, (18, 48, 36), rect, border_radius=4)
    pygame.draw.rect(surface, color, rect, 2, border_radius=4)
    label = font.render(text, True, WHITE if highlighted else GREEN_DIM)
    surface.blit(label, label.get_rect(center=rect.center))


def _wrap_text(text: str, font: pygame.font.Font, max_width: int) -> tuple[str, ...]:
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if current and font.size(candidate)[0] > max_width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return tuple(lines)


def _draw_wrapped_text(surface: pygame.Surface, text: str, font: pygame.font.Font,
                       pos: tuple[int, int], color: tuple[int, int, int],
                       max_width: int, line_spacing: int | None = None) -> int:
    spacing = line_spacing or font.get_linesize()
    lines = _wrap_text(text, font, max_width)
    for index, line in enumerate(lines):
        _label(surface, font, line, (pos[0], pos[1] + index * spacing), color)
    return pos[1] + len(lines) * spacing


def _panel(surface: pygame.Surface, rect: pygame.Rect) -> None:
    pygame.draw.rect(surface, PANEL, rect, border_radius=7)
    pygame.draw.rect(surface, LINE, rect, 1, border_radius=7)


def _draw_elf_portrait(surface: pygame.Surface, portrait: pygame.Surface,
                       position: tuple[int, int], size: tuple[int, int]) -> None:
    image = pygame.transform.scale(portrait, size)
    surface.blit(image, position)


def _draw_entity_portrait(surface: pygame.Surface, portrait: pygame.Surface,
                          position: tuple[int, int], size: tuple[int, int],
                          elapsed: float) -> None:
    image = pygame.transform.scale(portrait, size)
    image.set_alpha(min(255, 110 + int(145 * min(1.0, elapsed / 0.3))))
    surface.blit(image, position)


def _draw_grid(surface: pygame.Surface) -> None:
    width, height = surface.get_size()
    for x in range(0, width, 40):
        pygame.draw.line(surface, (11, 35, 29), (x, 0), (x, height))
    for y in range(0, height, 40):
        pygame.draw.line(surface, (11, 35, 29), (0, y), (width, y))


def _present_5_4(screen: pygame.Surface, canvas: pygame.Surface) -> None:
    """Present the 5:4 game canvas at the CRT's native output ratio."""
    screen.fill(BACKGROUND)
    _draw_grid(screen)
    target = pygame.Rect(0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT)
    image = pygame.transform.scale(canvas, target.size)
    screen.blit(image, target)
    pygame.draw.line(screen, GREEN_DIM, (0, target.top - 18),
                     (DISPLAY_WIDTH, target.top - 18), 2)
    pygame.draw.line(screen, LINE, (0, target.bottom + 18),
                     (DISPLAY_WIDTH, target.bottom + 18), 2)


def _draw_station_shell(surface: pygame.Surface) -> None:
    surface.fill((3, 8, 8))
    pygame.draw.rect(surface, (18, 26, 23), pygame.Rect(5, 5, WIDTH - 10, HEIGHT - 10),
                     border_radius=20)
    pygame.draw.rect(surface, (31, 73, 57), pygame.Rect(14, 14, WIDTH - 28, HEIGHT - 28),
                     2, border_radius=16)
    pygame.draw.line(surface, (83, 171, 130), (35, 23), (WIDTH - 35, 23), 2)
    surface.fill(BACKGROUND, pygame.Rect(22, 28, WIDTH - 44, HEIGHT - 56))
    previous_clip = surface.get_clip()
    screen_rect = pygame.Rect(22, 28, WIDTH - 44, HEIGHT - 56)
    surface.set_clip(screen_rect)
    _draw_grid(surface)
    for y in range(screen_rect.top + 2, screen_rect.bottom, 4):
        pygame.draw.line(surface, (5, 16, 14), (screen_rect.left, y),
                         (screen_rect.right, y))
    surface.set_clip(previous_clip)
    pygame.draw.line(surface, GREEN_DIM, (40, 62), (1160, 62), 2)
    _label(surface, _font(14, bold=True), "COMMISSARIAT", (42, 28), GREEN)
    _label(surface, _font(12), "ARCHIVES DE POLICE", (42, 45), GREEN_DIM)
    title = _font(20, bold=True).render("DOSSIERS D'ENQUETE", True, GREEN)
    surface.blit(title, title.get_rect(center=(625, 39)))
    _label(surface, _font(12), "TERMINAL 01", (1034, 35), GREEN_DIM)
    pygame.draw.rect(surface, (23, 70, 53), pygame.Rect(40, 72, 1120, 27), border_radius=2)
    pygame.draw.rect(surface, GREEN_DIM, pygame.Rect(40, 72, 1120, 27), 1, border_radius=2)
    _label(surface, _font(13, bold=True), "ENTREE / ESPACE : VALIDER", (56, 78), BACKGROUND)
    _label(surface, _font(13, bold=True), "ECHAP : QUITTER", (991, 78), BACKGROUND)
    pygame.draw.line(surface, LINE, (40, 859), (1160, 859))
    _label(surface, _font(13), "DOSSIERS NUMERIQUES  /  PERSONNES DISPARUES", (40, 884), GREEN_DIM)
    _label(surface, _font(13), "FERMER : ECHAP", (1000, 884), GREEN_DIM)


def _draw_case_sidebar(surface: pygame.Surface) -> None:
    rect = pygame.Rect(40, 112, 220, 727)
    _panel(surface, rect)
    _label(surface, _font(13, bold=True), "C:\\DOSSIERS\\", (56, 128), GREEN)
    pygame.draw.line(surface, LINE, (55, 153), (245, 153))

    def folder(y: int, label: str, selected: bool = False, indent: int = 0) -> None:
        x = 57 + indent
        if selected:
            pygame.draw.rect(surface, GREEN_DIM, pygame.Rect(51, y - 3, 198, 31))
        color = BACKGROUND if selected else GREEN
        pygame.draw.rect(surface, color, pygame.Rect(x, y + 5, 16, 11))
        pygame.draw.rect(surface, color, pygame.Rect(x + 2, y + 2, 8, 5))
        _label(surface, _font(14, bold=selected), label, (x + 24, y + 1), color)

    folder(183, "_EN_COURS")
    folder(229, "_ARCHIVES")
    folder(275, "PERSONNES_DISPARUES")
    folder(321, "W_BYERS", selected=True, indent=16)
    pygame.draw.line(surface, LINE, (55, 381), (245, 381))
    _label(surface, _font(13), "INCIDENTS", (68, 406), GREEN_DIM)
    _label(surface, _font(13), "PIECES", (68, 445), GREEN_DIM)
    _label(surface, _font(13), "RAPPORTS", (68, 484), GREEN_DIM)


def _draw_case_file(surface: pygame.Surface, portrait: pygame.Surface,
                    opened: bool, elapsed: float = 0.0) -> None:
    body = pygame.Rect(276, 112, 884, 727)
    _panel(surface, body)
    pygame.draw.rect(surface, PANEL_LIGHT, pygame.Rect(body.x + 1, body.y + 1, body.width - 2, 38))
    pygame.draw.line(surface, LINE, (body.x, body.y + 39), (body.right, body.y + 39))
    _label(surface, _font(14, bold=True), "FICHIER : W_BYERS.DOC", (body.x + 18, body.y + 13), GREEN)
    pygame.draw.rect(surface, PANEL_LIGHT, pygame.Rect(body.x + 18, body.y + 50, 132, 29))
    pygame.draw.rect(surface, GREEN_DIM, pygame.Rect(body.x + 18, body.y + 50, 132, 29), 1)
    _label(surface, _font(13, bold=True), "FICHE", (body.x + 58, body.y + 58), WHITE)
    pygame.draw.line(surface, LINE, (body.x + 18, body.y + 81), (body.right - 18, body.y + 81))

    if opened:
        progress = min(1.0, max(0.0, elapsed / DOSSIER_OPEN_SECONDS))
        eased = 1 - (1 - progress) ** 3
        clip = pygame.Rect(body.x + 18, body.y + 88, body.width - 36, body.height - 106)
        visible_width = max(1, round(clip.width * eased))
        animated_clip = pygame.Rect(clip.centerx - visible_width // 2, clip.y,
                                    visible_width, clip.height)
        previous_clip = surface.get_clip()
        surface.set_clip(animated_clip)
        if progress < 0.27:
            _label(surface, _font(18, bold=True), "OUVERTURE DU DOSSIER...",
                   (body.centerx - 135, body.centery - 10), GREEN)
        else:
            image_size = (270, 405)
            image = pygame.transform.scale(portrait, image_size)
            surface.blit(image, (body.x + 45, body.y + 151))
            _label(surface, _font(15, bold=True), "IDENTITE", (body.x + 365, body.y + 180), GREEN_DIM)
            _label(surface, _font(34, bold=True), "WILL BYERS", (body.x + 365, body.y + 220), WHITE)
            pygame.draw.line(surface, LINE, (body.x + 365, body.y + 275),
                             (body.right - 40, body.y + 275), 2)
            _label(surface, _font(15, bold=True), "STATUT", (body.x + 365, body.y + 320), GREEN_DIM)
            status = pygame.Rect(body.x + 365, body.y + 355, 198, 40)
            pygame.draw.rect(surface, (23, 70, 53), status)
            pygame.draw.rect(surface, GREEN_DIM, status, 1)
            _label(surface, _font(20, bold=True), "DISPARU", (status.x + 17, status.y + 10), GREEN)
            _label(surface, _font(13), "DOSSIER OUVERT", (body.x + 365, body.bottom - 38), GREEN_DIM)
        surface.set_clip(previous_clip)
        return

    image = pygame.transform.scale(portrait, (190, 285))
    surface.blit(image, (body.x + 44, body.y + 145))
    _label(surface, _font(14), "IDENTITE", (body.x + 282, body.y + 180), GREEN_DIM)
    _label(surface, _font(29, bold=True), "WILL BYERS", (body.x + 282, body.y + 218), WHITE)
    pygame.draw.line(surface, LINE, (body.x + 282, body.y + 270), (body.right - 36, body.y + 270))
    _label(surface, _font(14, bold=True), "STATUT : DISPARU", (body.x + 282, body.y + 305), AMBER)
    _label(surface, _font(15, bold=True), "POUR OUVRIR LE DOSSIER, APPUYEZ SUR :",
           (body.x + 282, body.y + 410), GREEN_DIM)
    blink_on = elapsed % 1.1 < 0.72
    _draw_keycap(surface, "ENTREE", (body.x + 366, body.y + 490), 150, blink_on)
    _label(surface, _font(14, bold=True), "OU", (body.x + 448, body.y + 484),
           GREEN if blink_on else GREEN_DIM)
    _draw_keycap(surface, "ESPACE", (body.x + 555, body.y + 490), 150, blink_on)


def _draw_welcome(surface: pygame.Surface, elapsed: float,
                  portrait: pygame.Surface) -> None:
    _draw_station_shell(surface)
    _draw_case_sidebar(surface)
    _draw_case_file(surface, portrait, opened=False, elapsed=elapsed)


def _draw_dossier(surface: pygame.Surface, elapsed: float,
                  portrait: pygame.Surface) -> None:
    _draw_station_shell(surface)
    _draw_case_sidebar(surface)
    _draw_case_file(surface, portrait, opened=True, elapsed=elapsed)


def _draw_possession(surface: pygame.Surface, elapsed: float, duration: float,
                     messages: tuple[str, ...], variant: str,
                     entity_portrait: pygame.Surface,
                     case_portrait: pygame.Surface) -> None:
    # The opened police file remains visible beneath a slowly growing disturbance.
    progress = min(1, elapsed / duration)
    _draw_dossier(surface, DOSSIER_OPEN_SECONDS, case_portrait)
    veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    tension = variant == "Tension"
    veil.fill((17, 4, 17, int((112 if tension else 92) + 26 * progress)))
    surface.blit(veil, (0, 0))

    diagnostics = pygame.Rect(40, 244, 738, 624)
    _panel(surface, diagnostics)
    _label(surface, _font(16, bold=True), "JOURNAL DES ANOMALIES", (63, 264), RED)
    pygame.draw.line(surface, RED_DIM, (62, 301), (756, 301))
    anomalies = (
        "CAPTEURS .......... SIGNAL INCONNU",
        "ARCHIVE ........... REPONSE IMPOSSIBLE",
        "CHAMBRE 04 ........ DEMOGORGON DETECTE",
    )
    for index, line in enumerate(anomalies[: max(1, int(progress * 3) + 1)]):
        _label(surface, _font(17), line, (64, 330 + index * 49), RED)

    pygame.draw.rect(surface, PANEL, pygame.Rect(799, 245, 360, 40))
    _label(surface, _font(16, True), "SIGNAL / DEMOGORGON", (819, 263), RED)
    pygame.draw.rect(surface, RED_DIM, pygame.Rect(878, 286, 202, 202), 1)
    _draw_entity_portrait(surface, entity_portrait, (882, 290), (194, 194), elapsed)

    # Interference grows steadily; no full-screen flashes or random jumps.
    for index in range(int(progress * (30 if tension else 9))):
        y = 318 + index * (7 if tension else 39) + int(3 * math.sin(elapsed * 0.8 + index))
        if y < 448:
            displacement = int((18 if tension else 0) * progress * math.sin(elapsed * 0.6 + index))
            pygame.draw.line(surface, (153, 70, 75) if tension else RED_DIM,
                             (795 + displacement, y), (1146, y), 2 if tension else 1)

    # Each branch grows with the phase and bends smoothly, like roots along the bezel.
    for branch in range(10 if tension else 7):
        end = int(4 + progress * 14)
        base_y = 200 + branch * 85
        points = []
        for step in range(end):
            x = int(1199 - step * (9 + branch % 3))
            y = int(base_y + step * (3 if branch % 2 else -3) +
                    (15 if tension else 9) * math.sin(step * 0.6 + branch))
            points.append((x, y))
        if len(points) > 1:
            pygame.draw.lines(surface, RED_DIM, False, points, 2)

    status = pygame.Rect(798, 508, 362, 122)
    _panel(surface, status)
    _label(surface, _font(14), "ETAT DU TERMINAL", (819, 528), RED)
    pygame.draw.circle(surface, RED, (828, 584), 5)
    _label(surface, _font(21, bold=True), "LIAISON PERTURBEE", (845, 570), WHITE)

    if messages:
        box = pygame.Rect(40, 747, 738, 121)
        pygame.draw.rect(surface, PANEL, box, border_radius=7)
        pygame.draw.rect(surface, GREEN, box, 1, border_radius=7)
        _draw_wrapped_text(surface, messages[-1], _font(22, bold=True),
                           (62, 762), WHITE, 690, line_spacing=27)

    # A short signal breach echoes the later Elf/entity clash, then dissolves
    # into the slower possession. The raster noise continues at a lower level.
    _draw_static_glitches(surface, elapsed, 0.38 + 0.85 * (1 - min(1.0, elapsed / 2.4)))
    if elapsed < 2.4:
        _draw_entry_breach(surface, elapsed)
    _draw_red_arrival_flash(surface, elapsed)


def _draw_red_arrival_flash(surface: pygame.Surface, elapsed: float) -> None:
    """One red impact pulse precisely at the start of the entity's arrival."""
    flash_duration = 0.28
    if elapsed >= flash_duration:
        return
    strength = 1.0 - elapsed / flash_duration
    flash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    flash.fill((170, 4, 16, int(118 * max(0.0, strength))))
    surface.blit(flash, (0, 0))


def _draw_static_glitches(surface: pygame.Surface, elapsed: float, intensity: float) -> None:
    """Draw restrained CRT interference without full-screen flashing."""
    beat = int(elapsed * 9)
    noise = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    # Each short burst changes its pattern, avoiding a visibly repeating scan.
    for index in range(13):
        y = (beat * 47 + index * 89 + (index * beat * 13)) % HEIGHT
        height = 1 + (index % 3)
        alpha = int((18 + (index * 17 + beat * 11) % 43) * intensity)
        color = (162, 67, 83, alpha) if index % 2 else (81, 191, 152, alpha)
        left = (beat * (31 + index * 7) + index * 137) % 520
        width = 110 + ((beat * 23 + index * 61) % 320)
        pygame.draw.rect(noise, color, (left, y, width, height))

    # Sparse pixel snow sits mostly over the terminal's darker surfaces.
    for index in range(52):
        x = (beat * 79 + index * 193 + index * index * 7) % WIDTH
        y = (beat * 43 + index * 127 + index * index * 3) % HEIGHT
        alpha = int((24 + (index * 19 + beat * 7) % 54) * intensity)
        pygame.draw.rect(noise, (154, 194, 175, alpha), (x, y, 2, 2))
    surface.blit(noise, (0, 0))


def _draw_entry_breach(surface: pygame.Surface, elapsed: float) -> None:
    """Briefly tear open the signal chart with the return-clash wave motif."""
    strength = max(0.0, 1.0 - elapsed / 2.4)
    center_x = 802 + int(338 * min(1.0, elapsed / 0.75))
    center_y = 385 + int(13 * math.sin(elapsed * 11))
    _draw_signal_strands(surface, 798, 9, 41, center_y, elapsed, amplitude=10, spacing=11)
    for ring in range(3):
        radius = 10 + ring * 18 + int((elapsed * 54) % 22)
        alpha_surface = pygame.Surface((radius * 2 + 4, radius * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(alpha_surface, (*GREEN, int((150 - ring * 34) * strength)),
                           (radius + 2, radius + 2), radius, 1)
        surface.blit(alpha_surface, (center_x - radius - 2, center_y - radius - 2))


def _draw_signal_strands(surface: pygame.Surface, start_x: int, step_x: int,
                         count: int, center_y: int, elapsed: float,
                         amplitude: int = 17, spacing: int = 13) -> None:
    """Shared three-strand pulse used by both possession and the rematch."""
    for strand in range(3):
        points = []
        for step in range(count):
            x = start_x + step * step_x
            y = center_y + strand * spacing + int(amplitude * math.sin(step * 0.48 + elapsed * 9 + strand))
            points.append((x, y))
        color = GREEN if strand != 1 else AMBER
        pygame.draw.lines(surface, color, False, points, 3 if strand == 1 else 2)


def _draw_return_clash(surface: pygame.Surface, elapsed: float,
                       messages: tuple[str, ...], portrait: pygame.Surface,
                       entity_portrait: pygame.Surface) -> None:
    surface.fill((5, 4, 13))
    _draw_grid(surface)
    shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    shade.fill((35, 3, 20, 130))
    surface.blit(shade, (0, 0))
    _label(surface, _font(22, True), "CONFLIT DE SIGNAL  //  REPRISE DU TERMINAL", (54, 42), RED)
    pygame.draw.line(surface, RED_DIM, (54, 80), (1146, 80), 2)

    left = pygame.Rect(62, 156, 345, 448)
    right = pygame.Rect(793, 156, 345, 448)
    pygame.draw.rect(surface, (9, 19, 25), left, border_radius=8)
    pygame.draw.rect(surface, GREEN_DIM, left, 1, border_radius=8)
    pygame.draw.rect(surface, (18, 5, 16), right, border_radius=8)
    pygame.draw.rect(surface, RED_DIM, right, 1, border_radius=8)
    _draw_elf_portrait(surface, portrait, (85, 228), (300, 250))
    _label(surface, _font(18, True), "ELF  /  SIGNAL ALLIE", (88, 562), GREEN)

    _draw_entity_portrait(surface, entity_portrait, (825, 210), (281, 281), elapsed + 0.3)
    _label(surface, _font(18, True), "DEMOGORGON / SIGNAL HOSTILE", (819, 562), RED)

    impact_x = 590 + int(96 * math.sin(elapsed * 5))
    _draw_signal_strands(surface, 405, 9, 42, 358, elapsed)
    pygame.draw.circle(surface, WHITE, (impact_x, 385), 9, 2)
    pygame.draw.circle(surface, GREEN, (impact_x, 385), 22, 1)

    y = 634
    for line in messages:
        y = _draw_wrapped_text(surface, line, _font(20, True), (420, y), WHITE, 690, 26) + 2


def _draw_elf(surface: pygame.Surface, elapsed: float, messages: tuple[str, ...],
               portrait: pygame.Surface) -> None:
    _draw_station_shell(surface)
    for branch in range(5):
        points = [(1198 - i * 13, 225 + branch * 83 + int(7 * math.sin(i * 0.5 + branch))) for i in range(10)]
        pygame.draw.lines(surface, RED_DIM, False, points, 2)
    panel = pygame.Rect(40, 220, 1120, 620)
    pygame.draw.rect(surface, PANEL, panel, border_radius=7)
    pygame.draw.rect(surface, GREEN_DIM, panel, 1, border_radius=7)
    _label(surface, _font(18), "TRANSMISSION RETABLIE  /  ELF", (68, 248), GREEN)
    pygame.draw.line(surface, LINE, (68, 290), (1132, 290))
    _draw_elf_portrait(surface, portrait, (78, 310), (270, 225))
    y = 320
    for index, line in enumerate(messages):
        font = _font(25 if index == 0 else 22, bold=index == 0)
        y = _draw_wrapped_text(surface, line, font, (382, y), WHITE, 750, 30) + 8
    _label(surface, _font(15, True), "APPUYEZ SUR UNE TOUCHE POUR CONTINUER", (382, min(y, 748)), AMBER)
    _draw_keycap(surface, "ENTREE", (489, 804), 140)
    _draw_keycap(surface, "ESPACE", (667, 804), 140)


GAME_LABELS = {
    "maze": ("1", "PAC-MAN", "Vider le plateau  |  Fleches / WASD"),
    "space_combat": ("2", "SPACE INVADERS", "Atteindre le score  |  Fleches / A D + Espace"),
    "platformer": ("3", "DONKEY KONG", "Rejoindre la sortie  |  Fleches / WASD + Espace"),
}


def _draw_choice(surface: pygame.Surface, available_games: tuple[str, ...],
                 remaining: float, warning: bool,
                 free_mode: bool = False, games: GameSettings = GameSettings(),
                 portrait: pygame.Surface | None = None,
                 selected_index: int = 0) -> None:
    _draw_station_shell(surface)
    panel = pygame.Rect(40, 220, 1120, 620)
    _panel(surface, panel)
    title = ("ELF // MODE LIBRE" if free_mode else
             "ELF // NOUVELLE CHANCE" if len(available_games) < 3 else "ELF // J'AI BESOIN DE VOUS")
    _label(surface, _font(25, True), title, (68, 246), WHITE)
    subtitle = ("MODE LIBRE : choisissez un jeu avec les fleches." if free_mode else
                "Choisissez un jeu avec les fleches. Trois vies pour relever le defi.")
    _label(surface, _font(17), subtitle, (68, 288), GREEN)
    for index, game_name in enumerate(available_games):
        key, name, instruction = GAME_LABELS[game_name]
        if game_name == "maze" and games.maze.pellet_goal_percent < 100:
            instruction = f"Ramasser {games.maze.pellet_goal_percent:g}% des pastilles  |  Fleches / WASD"
        elif game_name == "space_combat":
            instruction = f"Atteindre {games.space_combat.score_target} points  |  Fleches / A D + Espace"
        elif game_name == "platformer" and games.platformer.goal_progress_percent < 100:
            instruction = f"Atteindre {games.platformer.goal_progress_percent:g}% du sommet  |  Fleches / WASD + Espace"
        y = 351 + index * 98
        if index == selected_index:
            selected = pygame.Rect(60, y - 8, 780, 72)
            pygame.draw.rect(surface, (15, 47, 36), selected)
            pygame.draw.rect(surface, GREEN, selected, 2)
            pygame.draw.polygon(surface, AMBER,
                                [(76, y + 13), (88, y + 20), (76, y + 27)])
        pygame.draw.line(surface, LINE, (68, y - 13), (1130, y - 13))
        color = WHITE if index == selected_index else GREEN_DIM
        _label(surface, _font(27, True), key, (99, y), AMBER)
        _label(surface, _font(23, True), name, (156, y), color)
        _label(surface, _font(16), instruction, (158, y + 36), GREEN_DIM)
    if portrait:
        _draw_elf_portrait(surface, portrait, (866, 358), (240, 200))
    pygame.draw.line(surface, LINE, (68, 690), (1132, 690))
    _label(surface, _font(15, True), "NAVIGUER", (290, 710), GREEN)
    _draw_keycap(surface, "↑", (432, 732), 40)
    _draw_keycap(surface, "↓", (480, 732), 40)
    _label(surface, _font(15, True), "PUIS LANCER", (535, 710), GREEN)
    _draw_keycap(surface, "ENTREE", (700, 732), 128)
    _label(surface, _font(15, True), "OU", (796, 710), GREEN_DIM)
    _draw_keycap(surface, "ESPACE", (900, 732), 124)


def _new_game(name: str, games: GameSettings):
    if name == "maze":
        return maze_game.Game(pellet_goal_percent=games.maze.pellet_goal_percent,
                              ghost_step_seconds=games.maze.ghost_step_seconds,
                              power_seconds=games.maze.power_seconds)
    if name == "space_combat":
        return space_game.Game(score_target=games.space_combat.score_target,
                               enemy_speed_px_per_second=games.space_combat.enemy_speed_px_per_second,
                               salvo_interval_seconds=games.space_combat.salvo_interval_seconds)
    settings = games.platformer
    level = platform_game.DEFAULT_LEVEL.with_tuning(
        barrel_interval_seconds=settings.barrel_interval_seconds,
        barrel_speed_px_per_second=settings.barrel_speed_px_per_second,
        barrel_speed_cap_px_per_second=settings.barrel_speed_cap_px_per_second,
        fire_spawn_interval_seconds=settings.fire_spawn_interval_seconds,
        fire_speed_px_per_second=settings.fire_speed_px_per_second)
    return platform_game.Game(level, goal_progress_percent=settings.goal_progress_percent)


def _game_input(name: str, keys):
    left = keys[pygame.K_LEFT] or keys[pygame.K_a]
    right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
    if name == "space_combat":
        return space_game.PlayerInput(left=left, right=right, shoot=keys[pygame.K_SPACE])
    up = keys[pygame.K_UP] or keys[pygame.K_w]
    down = keys[pygame.K_DOWN] or keys[pygame.K_s]
    if name == "maze":
        return maze_game.PlayerInput(up=up, down=down, left=left, right=right)
    return platform_game.PlayerInput(left=left, right=right, up=up, down=down,
                                     jump=keys[pygame.K_SPACE])


def _draw_game(surface: pygame.Surface, name: str, state, elapsed: float,
               free_mode: bool, games: GameSettings = GameSettings()) -> None:
    draw = {"maze": maze_window._draw, "space_combat": space_window._draw,
            "platformer": platform_window._draw}[name]
    if name == "maze":
        width = len(state.rows[0]) * maze_window.CELL
        height = len(state.rows) * maze_window.CELL + maze_window.HEADER + maze_window.FOOTER
    elif name == "space_combat":
        width, height = state.width, state.height
    else:
        width = state.level.width
        height = state.level.height + platform_window.HEADER + platform_window.FOOTER
    canvas = pygame.Surface((width, height))
    draw(canvas, state, _font(32, True), _font(16), elapsed)
    scale = min(1120 / width, 780 / height)
    size = (round(width * scale), round(height * scale))
    image = pygame.transform.smoothscale(canvas, size)
    surface.fill(BACKGROUND)
    _draw_grid(surface)
    _label(surface, _font(17, True),
           "COMMISSARIAT  /  MODE LIBRE" if free_mode else
           "COMMISSARIAT  /  DEFI EN COURS", (42, 30), GREEN)
    _label(surface, _font(20, True), f"VIES {state.lives} / 3", (633, 27), WHITE)
    surface.blit(image, ((WIDTH - size[0]) // 2, 102 + (780 - size[1]) // 2))
    instructions = {
        "maze": ("OBJECTIF : VIDER LE PLATEAU", "FLECHES / WASD : SE DEPLACER"),
        "space_combat": ("OBJECTIF : ATTEINDRE LE SCORE CIBLE", "FLECHES / A D : BOUGER   •   ESPACE : TIRER"),
        "platformer": ("OBJECTIF : REJOINDRE LA PRINCESSE", "FLECHES / WASD : BOUGER / GRIMPER   •   ESPACE : SAUTER"),
    }[name]
    if name == "maze" and games.maze.pellet_goal_percent < 100:
        instructions = (f"OBJECTIF : RAMASSER {games.maze.pellet_goal_percent:g}% DES PASTILLES",
                        instructions[1])
    elif name == "platformer" and games.platformer.goal_progress_percent < 100:
        instructions = (f"OBJECTIF : ATTEINDRE {games.platformer.goal_progress_percent:g}% DU SOMMET",
                        instructions[1])
    if free_mode:
        instructions = (instructions[0], "M : CHANGER DE JEU")
    _label(surface, _font(17, True), instructions[0], (42, 886), WHITE)
    _label(surface, _font(15), instructions[1], (42, 923), GREEN)


def _tone(frequency: float, seconds: float, volume: float = 0.13) -> pygame.mixer.Sound:
    sample_rate = 44100
    samples = array("h")
    for i in range(int(sample_rate * seconds)):
        t = i / sample_rate
        envelope = min(1, t / 0.08) * min(1, (seconds - t) / 0.18)
        wobble = 1 + 0.015 * math.sin(t * 9)
        value = math.sin(2 * math.pi * frequency * wobble * t)
        samples.append(int(32767 * volume * envelope * value))
    return pygame.mixer.Sound(buffer=samples.tobytes())


def _draw_test_mode_badge(surface: pygame.Surface) -> None:
    _label(surface, _font(15, bold=True), "MODE TEST", (1045, 721), AMBER)


def _draw_countdown(surface: pygame.Surface, remaining: float, warning: bool,
                    free_mode: bool = False, room_won: bool = False) -> None:
    timer_box = pygame.Rect(792, 7, 367, 86)
    green_mode = free_mode or room_won
    timer_color = ((91, 232, 153) if green_mode else
                   (255, 56, 65) if warning else (255, 80, 80))
    background = (6, 29, 20) if green_mode else (38, 10, 17)
    label_color = (166, 255, 199) if green_mode else (255, 175, 168)
    pygame.draw.rect(surface, background, timer_box, border_radius=5)
    pygame.draw.rect(surface, timer_color, timer_box, 2, border_radius=5)
    _label(surface, _font(14, True), "TEMPS RESTANT", (811, 41), label_color)
    minutes, seconds = divmod(math.ceil(remaining), 60)
    _label(surface, _font(48, bold=True), f"{minutes:02}:{seconds:02}", (955, 20), timer_color)


def _draw_end(surface: pygame.Surface, combined_alerts: bool,
              portrait: pygame.Surface) -> None:
    surface.fill(BACKGROUND)
    _draw_grid(surface)
    _label(surface, _font(44, bold=True), "SESSION TERMINEE", (350, 308), AMBER)
    _draw_wrapped_text(surface, "ELF // Le temps est ecoule. Rejoignez la salle suivante.",
                       _font(24), (205, 395), WHITE, 640, 30)
    _label(surface, _font(21), "Animateur : remettre la borne a zero pour l'equipe suivante.", (171, 476), GREEN)
    _label(surface, _font(17), "CONTROLE + OPTION + COMMANDE + ESPACE", (419, 559), GREEN_DIM)
    if combined_alerts:
        _label(surface, _font(17, bold=True), "AVERTISSEMENT DE FIN EMIS", (445, 635), AMBER)
    _draw_elf_portrait(surface, portrait, (865, 450), (250, 208))


def _draw_victory(surface: pygame.Surface, room_digit: int,
                  portrait: pygame.Surface) -> None:
    surface.fill(BACKGROUND)
    _draw_grid(surface)
    _label(surface, _font(24, True), "ELF // CONTROLE RETABLI", (381, 210), GREEN)
    _label(surface, _font(32, True), "CHIFFRE DE SALLE", (425, 266), WHITE)
    digit = _font(116, True).render(str(room_digit), True, AMBER)
    surface.blit(digit, digit.get_rect(center=(WIDTH // 2, 394)))
    _label(surface, _font(22), "Merci de m'avoir aidée.", (455, 480), GREEN)
    _label(surface, _font(19), "Il est parti… mais je ne crois pas que ce soit fini.",
           (331, 527), WHITE)
    _label(surface, _font(18, True), "APPUYEZ SUR UNE TOUCHE POUR ACCEDER AUX JEUX", (345, 650), WHITE)
    _draw_keycap(surface, "ENTREE", (511, 711), 140)
    _draw_keycap(surface, "ESPACE", (689, 711), 140)
    _draw_elf_portrait(surface, portrait, (858, 505), (260, 217))


def _draw_failure(surface: pygame.Surface, portrait: pygame.Surface) -> None:
    surface.fill(BACKGROUND)
    _draw_grid(surface)
    _label(surface, _font(23, bold=True), "ELF // JE SUIS REVENUE", (421, 276), GREEN)
    _label(surface, _font(44, bold=True), "DEFI ECHOUE", (395, 328), RED)
    _draw_wrapped_text(surface, "Les trois jeux sont perdus. Elf ne peut plus agir.",
                       _font(24), (262, 415), WHITE, 580, 30)
    _label(surface, _font(21), "Animateur : remettre la borne a zero pour l'equipe suivante.",
           (171, 496), GREEN)
    _label(surface, _font(17), "CONTROLE + OPTION + COMMANDE + ESPACE", (419, 559), GREEN_DIM)
    _draw_elf_portrait(surface, portrait, (866, 450), (250, 208))


def _reset_matches(event: pygame.event.Event) -> bool:
    return (event.type == pygame.KEYDOWN and event.key == RESET_KEY
            and all(event.mod & MODIFIERS[name] for name in RESET_MODIFIERS)
            and not any(event.mod & flag for name, flag in MODIFIERS.items()
                        if name not in RESET_MODIFIERS))


def run() -> None:
    parser = argparse.ArgumentParser(description="Borne rétro du commissariat")
    parser.add_argument("--config", type=Path, default=Path(__file__).resolve().parents[1] / "config.json")
    parser.add_argument("--test-mode", action="store_true", help="Accélère les délais à 10 %% sans modifier le fichier de configuration")
    parser.add_argument("--fullscreen", action="store_true", help="Affiche le parcours intégré en plein écran")
    args = parser.parse_args()
    pygame.mixer.pre_init(frequency=44100, size=-16, channels=1)
    pygame.init()
    try:
        config = load_config(args.config)
        flags = pygame.SCALED | pygame.FULLSCREEN if args.fullscreen else 0
        screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT), flags)
        canvas = pygame.Surface((WIDTH, HEIGHT))
        pygame.display.set_caption("Commissariat | Dossiers de police")
        case_portrait_path = Path(__file__).with_name("assets") / "will-byers-portrait.png"
        case_portrait = pygame.image.load(case_portrait_path).convert()
        portrait_path = Path(__file__).with_name("assets") / "elf-portrait.png"
        portrait = pygame.image.load(portrait_path).convert_alpha()
        entity_portrait_path = Path(__file__).with_name("assets") / "demogorgon-portrait.png"
        entity_portrait = pygame.image.load(entity_portrait_path).convert_alpha()
        clock = pygame.time.Clock()
        scale = 0.1 if args.test_mode else 1.0
        session = Session(config.session_seconds * scale, config.possession_seconds * scale,
                          config.warning_seconds * scale, config.room_digit,
                          entity_delay_seconds=ENTITY_DELAY_SECONDS * scale,
                          dossier_open_seconds=DOSSIER_OPEN_SECONDS)
        started_at = pygame.time.get_ticks()
        previous_tick = started_at
        previous_phase = Phase.ACCUEIL
        previous_state = session.advance(0, None)
        game = None
        game_name = None
        selected_game_index = 0
        game_time = 0.0
        phase_started_at = started_at
        had_contact = False
        warning_active = False
        combined_alerts = False
        sounds = None
        contact_sound = None
        soundtrack = None
        if pygame.mixer.get_init():
            sounds = {Phase.ELF: _tone(659, 0.7)}
            soundtrack = Soundtrack(config.variant)
            contact_sound = _tone(493, 0.45)
            warning_sound = _tone(440, 0.7)
            alarm_sound = _tone(220, 1.4, 0.18)
        running = True
        while running:
            action = None
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
                ):
                    running = False
                elif _reset_matches(event):
                    action = "reinitialiser"
                elif event.type == pygame.KEYDOWN and action != "reinitialiser":
                    if (previous_state.phase is Phase.ACCUEIL
                            and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE)):
                        action = "ouvrir_dossier"
                    elif (previous_state.phase in (Phase.ELF, Phase.VICTOIRE)
                          and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE)):
                        action = "continuer"
                    elif previous_state.phase in (Phase.CHOIX, Phase.LIBRE):
                        available_games = previous_state.available_games
                        if available_games and event.key in (pygame.K_UP, pygame.K_w):
                            selected_game_index = (selected_game_index - 1) % len(available_games)
                        elif available_games and event.key in (pygame.K_DOWN, pygame.K_s):
                            selected_game_index = (selected_game_index + 1) % len(available_games)
                        elif available_games and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                            action = f"choisir_{available_games[selected_game_index % len(available_games)]}"
                        selected = {pygame.K_1: "maze", pygame.K_KP1: "maze",
                                    pygame.K_2: "space_combat", pygame.K_KP2: "space_combat",
                                    pygame.K_3: "platformer", pygame.K_KP3: "platformer"}.get(event.key)
                        if selected and selected in available_games:
                            action = f"choisir_{selected}"
                    elif (previous_state.phase is Phase.JEU and previous_state.free_mode
                          and event.key == pygame.K_m):
                        action = "changer_jeu"
            if not running:
                break
            now = pygame.time.get_ticks()
            elapsed = (now - started_at) / 1000
            delta = (now - previous_tick) / 1000
            previous_tick = now
            reported_result = (game.state.result.value if game is not None and
                               previous_state.phase in (Phase.JEU, Phase.RESULTAT) and
                               game.state.result.value != "playing" else None)
            state = session.advance(delta, action, reported_result)
            if action == "reinitialiser":
                game = None
                game_name = None
                game_time = 0.0
                if pygame.mixer.get_init():
                    pygame.mixer.stop()
                had_contact = False
                warning_active = False
                combined_alerts = False
                started_at = now
            if "avertissement" in state.events:
                warning_active = True
                if pygame.mixer.get_init():
                    warning_sound.play()
            if "alarme" in state.events:
                combined_alerts = "avertissement" in state.events
                if pygame.mixer.get_init():
                    if not combined_alerts:
                        pygame.mixer.stop()
                    alarm_sound.play()
            if state.phase != previous_phase and sounds and state.phase in sounds:
                sounds[state.phase].play()
            if state.phase != previous_phase:
                phase_started_at = now
                if state.phase is Phase.CHOIX:
                    selected_game_index = 0
            if (state.phase is Phase.POSSESSION and any("ELF" in line for line in state.messages)
                    and not had_contact):
                had_contact = True
                if contact_sound:
                    contact_sound.play()
            previous_phase = state.phase
            previous_state = state
            if soundtrack:
                scene = None
                if state.phase is Phase.POSSESSION:
                    scene = "return" if state.return_takeover else "entity"
                elif state.phase is Phase.JEU:
                    scene = f"game:{state.active_game}"
                soundtrack.set_scene(scene)
            if state.phase in (Phase.CHOIX, Phase.LIBRE, Phase.VICTOIRE, Phase.FIN):
                game = None
                game_name = None
            if state.phase is Phase.JEU:
                if game is None or game_name != state.active_game:
                    game = _new_game(state.active_game, config.games)
                    game_name = state.active_game
                    game_time = 0.0
                else:
                    game_delta = delta / scale
                    game.advance(game_delta, _game_input(state.active_game, pygame.key.get_pressed()))
                    game_time += game_delta
            if state.phase is Phase.ACCUEIL:
                _draw_welcome(canvas, elapsed, case_portrait)
            elif state.phase is Phase.DOSSIER:
                dossier_elapsed = (now - phase_started_at) / 1000
                _draw_dossier(canvas, dossier_elapsed, case_portrait)
            elif state.phase is Phase.POSSESSION:
                phase_elapsed = (now - phase_started_at) / 1000
                if state.return_takeover:
                    _draw_return_clash(canvas, phase_elapsed, state.messages,
                                       portrait, entity_portrait)
                else:
                    _draw_possession(canvas, phase_elapsed, session.possession_seconds,
                                     state.messages, config.variant, entity_portrait,
                                     case_portrait)
            elif state.phase is Phase.ELF:
                _draw_elf(canvas, elapsed, state.messages, portrait)
            elif state.phase in (Phase.CHOIX, Phase.LIBRE):
                if state.available_games:
                    selected_game_index %= len(state.available_games)
                    _draw_choice(canvas, state.available_games, state.remaining_seconds,
                                 warning_active, state.free_mode, config.games,
                                 portrait, selected_game_index)
            elif state.phase in (Phase.JEU, Phase.RESULTAT):
                _draw_game(canvas, state.active_game, game.state, game_time,
                           state.free_mode, config.games)
            elif state.phase is Phase.VICTOIRE:
                _draw_victory(canvas, config.room_digit, portrait)
            elif state.phase is Phase.FIN:
                _draw_end(canvas, combined_alerts, portrait)
            elif state.phase is Phase.ECHEC:
                _draw_failure(canvas, portrait)
            else:
                raise AssertionError(f"Phase sans écran : {state.phase}")
            if state.timer_visible and state.remaining_seconds is not None:
                _draw_countdown(canvas, state.remaining_seconds, warning_active,
                                state.free_mode, state.room_result == "victory")
            if args.test_mode:
                _draw_test_mode_badge(canvas)
            _present_5_4(screen, canvas)
            pygame.display.flip()
            clock.tick(FPS)
    finally:
        _font.cache_clear()
        pygame.quit()
