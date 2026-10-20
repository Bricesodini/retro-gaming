"""Procedurally drawn laboratory, gradual possession and Elf contact."""

import argparse
import math
from array import array
from functools import lru_cache
from pathlib import Path

import pygame

from retro_gaming.config import GameSettings, MODIFIERS, RESET_KEY, RESET_MODIFIERS, load_config
from retro_gaming.session import Phase, Session
from retro_gaming.maze import game as maze_game, window as maze_window
from retro_gaming.space_combat import game as space_game, window as space_window
from retro_gaming.platformer import game as platform_game, window as platform_window
from retro_gaming.soundtrack import Soundtrack


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
RED = (169, 79, 73)
RED_DIM = (92, 49, 48)

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


def _draw_welcome(surface: pygame.Surface, elapsed: float, active: bool = False) -> None:
    surface.fill(BACKGROUND)
    _draw_grid(surface)
    pygame.draw.rect(surface, GREEN_DIM, pygame.Rect(0, 0, WIDTH, 6))

    _label(surface, _font(14), "INSTITUT DE RECHERCHE  /  SYSTEME LOCAL", (41, 30), GREEN_DIM)
    _label(surface, _font(14), "ARCHIVE 1986       UNITE 04", (646, 30), GREEN_DIM)
    pygame.draw.line(surface, LINE, (40, 62), (1160, 62))

    _label(surface, _font(42, bold=True), "LABORATOIRE", (41, 91), WHITE)
    _label(surface, _font(42, bold=True), "1986", (41, 139), GREEN)
    _label(surface, _font(14), "TERMINAL DE SURVEILLANCE  /  ETAT DES SYSTEMES", (367, 159), GREEN_DIM)
    pygame.draw.rect(surface, GREEN, pygame.Rect(41, 215, 1119, 2))

    _draw_diagnostics(surface, elapsed)
    _draw_signal(surface, elapsed)

    status = pygame.Rect(798, 508, 362, 122)
    _panel(surface, status)
    _label(surface, _font(14), "ETAT DU TERMINAL", (819, 528), GREEN_DIM)
    pygame.draw.circle(surface, RED if active else GREEN, (828, 584), 5)
    _label(surface, _font(22, bold=True), "SIGNAL INCONNU" if active else "SYSTEME EN VEILLE",
           (845, 570), WHITE)

    pygame.draw.line(surface, LINE, (40, 659), (1160, 659))
    _label(surface, _font(14), "SIMULATION  /  DONNEES FICTIVES", (40, 684), AMBER)
    _label(surface, _font(14), "SESSION EN COURS" if active else "SESSION EN ATTENTE", (862, 684), GREEN)
    _label(surface, _font(13), "FERMER : ECHAP OU BOUTON DE LA FENETRE", (40, 721), GREEN_DIM)


def _draw_arrival_wait(surface: pygame.Surface, elapsed: float,
                       arrival_seconds: float) -> None:
    _draw_welcome(surface, elapsed, active=True)
    box = pygame.Rect(40, 508, 738, 122)
    pygame.draw.rect(surface, (33, 7, 12), box, border_radius=8)
    pygame.draw.rect(surface, RED, box, 3, border_radius=8)
    _label(surface, _font(20, bold=True), "SIGNAL INCONNU DETECTE", (62, 530), RED)
    _label(surface, _font(18), "INTRUSION DANS", (62, 578), WHITE)
    _label(surface, _font(38, bold=True), f"{math.ceil(arrival_seconds):02d} s",
           (550, 553), RED)


def _draw_possession(surface: pygame.Surface, elapsed: float, duration: float,
                     messages: tuple[str, ...], variant: str,
                     entity_portrait: pygame.Surface) -> None:
    # The original terminal remains visible beneath a slowly growing disturbance.
    progress = min(1, elapsed / duration)
    _draw_welcome(surface, elapsed, active=True)
    veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    tension = variant == "Tension"
    veil.fill((17, 4, 17, int((112 if tension else 92) + 26 * progress)))
    surface.blit(veil, (0, 0))

    diagnostics = pygame.Rect(40, 244, 738, 386)
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
        box = pygame.Rect(40, 533, 738, 97)
        pygame.draw.rect(surface, PANEL, box, border_radius=7)
        pygame.draw.rect(surface, GREEN, box, 1, border_radius=7)
        _draw_wrapped_text(surface, messages[-1], _font(22, bold=True),
                           (62, 548), WHITE, 690, line_spacing=27)

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
    _draw_welcome(surface, elapsed, active=True)
    for branch in range(5):
        points = [(1198 - i * 13, 225 + branch * 83 + int(7 * math.sin(i * 0.5 + branch))) for i in range(10)]
        pygame.draw.lines(surface, RED_DIM, False, points, 2)
    panel = pygame.Rect(40, 244, 1120, 386)
    pygame.draw.rect(surface, PANEL, panel, border_radius=7)
    pygame.draw.rect(surface, GREEN_DIM, panel, 1, border_radius=7)
    _label(surface, _font(18), "TRANSMISSION RETABLIE  /  ELF", (68, 272), GREEN)
    pygame.draw.line(surface, LINE, (68, 314), (1132, 314))
    _draw_elf_portrait(surface, portrait, (78, 326), (270, 225))
    y = 335
    for index, line in enumerate(messages):
        font = _font(25 if index == 0 else 22, bold=index == 0)
        y = _draw_wrapped_text(surface, line, font, (382, y), WHITE, 750, 30) + 8
    _label(surface, _font(15), "ENTREE POUR CONTINUER", (382, min(y, 583)), AMBER)


GAME_LABELS = {
    "maze": ("1", "PAC-MAN", "Vider le plateau  |  Fleches / WASD"),
    "space_combat": ("2", "SPACE INVADERS", "Atteindre le score  |  Fleches / A D + Espace"),
    "platformer": ("3", "DONKEY KONG", "Rejoindre la sortie  |  Fleches / WASD + Espace"),
}


def _draw_choice(surface: pygame.Surface, available_games: tuple[str, ...],
                 remaining: float, warning: bool, test_mode: bool,
                 free_mode: bool = False, games: GameSettings = GameSettings(),
                 portrait: pygame.Surface | None = None) -> None:
    _draw_welcome(surface, 0, active=True)
    panel = pygame.Rect(40, 244, 1120, 386)
    _panel(surface, panel)
    title = ("ELF // MODE LIBRE" if free_mode else
             "ELF // NOUVELLE CHANCE" if len(available_games) < 3 else "ELF // J'AI BESOIN DE VOUS")
    _label(surface, _font(25, True), title, (68, 267), WHITE)
    subtitle = ("Les trois jeux sont accessibles jusqu'au depart." if free_mode else
                "Choisissez un jeu. Trois vies pour relever le defi.")
    _label(surface, _font(17), subtitle, (68, 307), GREEN)
    for index, game_name in enumerate(available_games):
        key, name, instruction = GAME_LABELS[game_name]
        if game_name == "maze" and games.maze.pellet_goal_percent < 100:
            instruction = f"Ramasser {games.maze.pellet_goal_percent:g}% des pastilles  |  Fleches / WASD"
        elif game_name == "space_combat":
            instruction = f"Atteindre {games.space_combat.score_target} points  |  Fleches / A D + Espace"
        elif game_name == "platformer" and games.platformer.goal_progress_percent < 100:
            instruction = f"Atteindre {games.platformer.goal_progress_percent:g}% du sommet  |  Fleches / WASD + Espace"
        y = 359 + index * 82
        pygame.draw.line(surface, LINE, (68, y - 13), (1130, y - 13))
        _label(surface, _font(27, True), key, (69, y), AMBER)
        _label(surface, _font(23, True), name, (126, y), WHITE)
        _label(surface, _font(16), instruction, (128, y + 36), GREEN_DIM)
    if portrait:
        _draw_elf_portrait(surface, portrait, (866, 349), (240, 200))
    if free_mode and test_mode:
        _draw_test_mode_badge(surface)


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
               test_mode: bool,
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
    scale = min(1120 / width, 580 / height)
    size = (round(width * scale), round(height * scale))
    image = pygame.transform.smoothscale(canvas, size)
    surface.fill(BACKGROUND)
    _draw_grid(surface)
    _label(surface, _font(17, True),
           "LABORATOIRE 1986  /  MODE LIBRE" if free_mode else
           "LABORATOIRE 1986  /  DEFI EN COURS", (42, 30), GREEN)
    _label(surface, _font(20, True), f"VIES {state.lives} / 3", (633, 27), WHITE)
    surface.blit(image, ((WIDTH - size[0]) // 2, 102 + (580 - size[1]) // 2))
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
    _label(surface, _font(17, True), instructions[0], (42, 690), WHITE)
    _label(surface, _font(15), instructions[1], (42, 722), GREEN)
    if test_mode:
        _draw_test_mode_badge(surface)


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


def _draw_countdown(surface: pygame.Surface, remaining: float, warning: bool) -> None:
    timer_box = pygame.Rect(792, 7, 367, 86)
    timer_color = (255, 56, 65) if warning else (255, 109, 80)
    pygame.draw.rect(surface, (38, 10, 17), timer_box, border_radius=5)
    pygame.draw.rect(surface, timer_color, timer_box, 2, border_radius=5)
    _label(surface, _font(14, True), "TEMPS RESTANT", (811, 41), (255, 175, 168))
    minutes, seconds = divmod(math.ceil(remaining), 60)
    _label(surface, _font(48, bold=True), f"{minutes:02}:{seconds:02}", (955, 20), timer_color)


def _draw_end(surface: pygame.Surface, test_mode: bool, combined_alerts: bool,
              portrait: pygame.Surface) -> None:
    surface.fill(BACKGROUND)
    _draw_grid(surface)
    _label(surface, _font(44, bold=True), "SESSION TERMINEE", (350, 223), AMBER)
    _draw_wrapped_text(surface, "ELF // Le temps est ecoule. Rejoignez la salle suivante.",
                       _font(24), (205, 310), WHITE, 640, 30)
    _label(surface, _font(21), "Animateur : remettre le laboratoire a zero pour l'equipe suivante.", (171, 391), GREEN)
    _label(surface, _font(17), "CONTROLE + OPTION + COMMANDE + ESPACE", (419, 474), GREEN_DIM)
    if combined_alerts:
        _label(surface, _font(17, bold=True), "AVERTISSEMENT DE FIN EMIS", (445, 550), AMBER)
    _draw_elf_portrait(surface, portrait, (865, 335), (250, 208))
    if test_mode:
        _draw_test_mode_badge(surface)


def _draw_victory(surface: pygame.Surface, room_digit: int, test_mode: bool,
                  portrait: pygame.Surface) -> None:
    surface.fill(BACKGROUND)
    _draw_grid(surface)
    _label(surface, _font(24, True), "ELF // CONTROLE RETABLI", (381, 165), GREEN)
    _label(surface, _font(44, True), "DEFI REUSSI", (405, 225), WHITE)
    _label(surface, _font(38, True), f"CHIFFRE DE SALLE : {room_digit}", (352, 310), AMBER)
    _draw_wrapped_text(surface, "L'entite annonce son retour. Pour l'instant, jouez librement.",
                       _font(21), (239, 400), GREEN, 590, 28)
    _label(surface, _font(18), "ENTREE POUR ACCEDER AUX TROIS JEUX", (391, 490), WHITE)
    _draw_elf_portrait(surface, portrait, (858, 341), (260, 217))
    if test_mode:
        _draw_test_mode_badge(surface)


def _draw_failure(surface: pygame.Surface, test_mode: bool, portrait: pygame.Surface) -> None:
    surface.fill(BACKGROUND)
    _draw_grid(surface)
    _label(surface, _font(23, bold=True), "ELF // JE SUIS REVENUE", (421, 171), GREEN)
    _label(surface, _font(44, bold=True), "DEFI ECHOUE", (395, 223), RED)
    _draw_wrapped_text(surface, "Les trois jeux sont perdus. Elf ne peut plus agir.",
                       _font(24), (262, 310), WHITE, 580, 30)
    _label(surface, _font(21), "Animateur : remettre le laboratoire a zero pour l'equipe suivante.",
           (171, 391), GREEN)
    _label(surface, _font(17), "CONTROLE + OPTION + COMMANDE + ESPACE", (419, 474), GREEN_DIM)
    _draw_elf_portrait(surface, portrait, (866, 345), (250, 208))


def _reset_matches(event: pygame.event.Event) -> bool:
    return (event.type == pygame.KEYDOWN and event.key == RESET_KEY
            and all(event.mod & MODIFIERS[name] for name in RESET_MODIFIERS)
            and not any(event.mod & flag for name, flag in MODIFIERS.items()
                        if name not in RESET_MODIFIERS))


def _ordinary_key(event: pygame.event.Event) -> bool:
    return (event.type == pygame.KEYDOWN
            and not _reset_matches(event)
            and event.key not in (pygame.K_ESCAPE, pygame.K_LCTRL, pygame.K_RCTRL,
                                  pygame.K_LALT, pygame.K_RALT, pygame.K_LGUI,
                                  pygame.K_RGUI, pygame.K_LSHIFT, pygame.K_RSHIFT))


def run() -> None:
    parser = argparse.ArgumentParser(description="Laboratoire 1986")
    parser.add_argument("--config", type=Path, default=Path(__file__).resolve().parents[1] / "config.json")
    parser.add_argument("--test-mode", action="store_true", help="Accélère les délais à 10 %% sans modifier le fichier de configuration")
    parser.add_argument("--fullscreen", action="store_true", help="Affiche le parcours intégré en plein écran")
    args = parser.parse_args()
    pygame.mixer.pre_init(frequency=44100, size=-16, channels=1)
    pygame.init()
    try:
        config = load_config(args.config)
        flags = pygame.SCALED | pygame.FULLSCREEN if args.fullscreen else 0
        screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
        pygame.display.set_caption("Laboratoire 1986 | Terminal de surveillance")
        portrait_path = Path(__file__).with_name("assets") / "elf-portrait.png"
        portrait = pygame.image.load(portrait_path).convert_alpha()
        entity_portrait_path = Path(__file__).with_name("assets") / "demogorgon-portrait.png"
        entity_portrait = pygame.image.load(entity_portrait_path).convert_alpha()
        clock = pygame.time.Clock()
        scale = 0.1 if args.test_mode else 1.0
        session = Session(config.session_seconds * scale, config.possession_seconds * scale,
                          config.warning_seconds * scale, config.room_digit,
                          signal_seconds=10 * scale)
        started_at = pygame.time.get_ticks()
        previous_tick = started_at
        previous_phase = Phase.LABORATOIRE
        previous_state = session.advance(0, None)
        game = None
        game_name = None
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
                    if (previous_state.phase is Phase.LABORATOIRE
                            and previous_state.remaining_seconds is None
                            and _ordinary_key(event)):
                        action = "declencher_mystere"
                    elif previous_state.phase in (Phase.ELF, Phase.VICTOIRE) and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        action = "continuer"
                    elif previous_state.phase in (Phase.CHOIX, Phase.LIBRE):
                        selected = {pygame.K_1: "maze", pygame.K_KP1: "maze",
                                    pygame.K_2: "space_combat", pygame.K_KP2: "space_combat",
                                    pygame.K_3: "platformer", pygame.K_KP3: "platformer"}.get(event.key)
                        if selected:
                            action = f"choisir_{selected}"
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
            if state.phase is Phase.LABORATOIRE:
                if state.arrival_seconds is not None:
                    _draw_arrival_wait(screen, elapsed, state.arrival_seconds)
                else:
                    _draw_welcome(screen, elapsed)
            elif state.phase is Phase.POSSESSION:
                phase_elapsed = (now - phase_started_at) / 1000
                if state.return_takeover:
                    _draw_return_clash(screen, phase_elapsed, state.messages,
                                       portrait, entity_portrait)
                else:
                    _draw_possession(screen, phase_elapsed, session.possession_seconds,
                                     state.messages, config.variant, entity_portrait)
            elif state.phase is Phase.ELF:
                _draw_elf(screen, elapsed, state.messages, portrait)
            elif state.phase in (Phase.CHOIX, Phase.LIBRE):
                _draw_choice(screen, state.available_games, state.remaining_seconds,
                             warning_active, args.test_mode, state.free_mode, config.games,
                             portrait)
            elif state.phase in (Phase.JEU, Phase.RESULTAT):
                _draw_game(screen, state.active_game, game.state, game_time,
                           args.test_mode, state.free_mode, config.games)
            elif state.phase is Phase.VICTOIRE:
                _draw_victory(screen, config.room_digit, args.test_mode, portrait)
            elif state.phase is Phase.FIN:
                _draw_end(screen, args.test_mode, combined_alerts, portrait)
            elif state.phase is Phase.ECHEC:
                _draw_failure(screen, args.test_mode, portrait)
            else:
                raise AssertionError(f"Phase sans écran : {state.phase}")
            if state.timer_visible and state.remaining_seconds is not None:
                _draw_countdown(screen, state.remaining_seconds, warning_active)
            elif state.phase is Phase.LABORATOIRE and args.test_mode:
                _draw_test_mode_badge(screen)
            pygame.display.flip()
            clock.tick(FPS)
    finally:
        _font.cache_clear()
        pygame.quit()
