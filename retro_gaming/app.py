"""Procedurally drawn laboratory, gradual possession and Elf contact."""

import argparse
import math
from array import array
from functools import lru_cache
from pathlib import Path

import pygame

from retro_gaming.config import MODIFIERS, RESET_KEY, RESET_MODIFIERS, load_config
from retro_gaming.session import Phase, Session


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


def _draw_welcome(surface: pygame.Surface, elapsed: float, active: bool = False) -> None:
    surface.fill(BACKGROUND)
    _draw_grid(surface)
    pygame.draw.rect(surface, GREEN_DIM, pygame.Rect(0, 0, WIDTH, 6))

    _label(surface, _font(14), "INSTITUT DE RECHERCHE  /  SYSTEME LOCAL", (41, 30), GREEN_DIM)
    _label(surface, _font(14), "ARCHIVE 1986       UNITE 04", (907, 30), GREEN_DIM)
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
    pygame.draw.circle(surface, GREEN, (828, 584), 5)
    _label(surface, _font(22, bold=True), "SYSTEME EN VEILLE", (845, 570), WHITE)

    pygame.draw.line(surface, LINE, (40, 659), (1160, 659))
    _label(surface, _font(14), "SIMULATION  /  DONNEES FICTIVES", (40, 684), AMBER)
    _label(surface, _font(14), "SESSION EN COURS" if active else "SESSION EN ATTENTE", (862, 684), GREEN)
    _label(surface, _font(13), "FERMER : ECHAP OU BOUTON DE LA FENETRE", (40, 721), GREEN_DIM)


def _draw_possession(surface: pygame.Surface, elapsed: float, duration: float, messages: tuple[str, ...]) -> None:
    # The original terminal remains visible beneath a slowly growing disturbance.
    progress = min(1, elapsed / duration)
    _draw_welcome(surface, elapsed, active=True)
    veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    veil.fill((76, 12, 22, int(42 * progress)))
    surface.blit(veil, (0, 0))

    diagnostics = pygame.Rect(40, 244, 738, 386)
    _panel(surface, diagnostics)
    _label(surface, _font(16, bold=True), "JOURNAL DES ANOMALIES", (63, 264), RED)
    pygame.draw.line(surface, RED_DIM, (62, 301), (756, 301))
    anomalies = (
        "CAPTEURS .......... SIGNAL INCONNU",
        "ARCHIVE ........... REPONSE IMPOSSIBLE",
        "CHAMBRE 04 ........ PRESENCE DETECTEE",
    )
    for index, line in enumerate(anomalies[: max(1, int(progress * 3) + 1)]):
        _label(surface, _font(17), line, (64, 330 + index * 49), RED)

    # Sparse interference: no full-screen flashes and no random frame-to-frame jumps.
    for index in range(int(progress * 9)):
        y = 318 + index * 39 + int(3 * math.sin(elapsed * 0.8 + index))
        pygame.draw.line(surface, RED_DIM, (795, y), (1146, y), 1)

    # Each branch grows with the phase and bends smoothly, like roots along the bezel.
    for branch in range(7):
        end = int(4 + progress * 14)
        base_y = 200 + branch * 85
        points = []
        for step in range(end):
            x = int(1199 - step * (9 + branch % 3))
            y = int(base_y + step * (3 if branch % 2 else -3) + 9 * math.sin(step * 0.6 + branch))
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
        _label(surface, _font(24, bold=True), messages[0], (62, 565), WHITE)


def _draw_elf(surface: pygame.Surface, elapsed: float, messages: tuple[str, ...]) -> None:
    _draw_welcome(surface, elapsed, active=True)
    for branch in range(5):
        points = [(1198 - i * 13, 225 + branch * 83 + int(7 * math.sin(i * 0.5 + branch))) for i in range(10)]
        pygame.draw.lines(surface, RED_DIM, False, points, 2)
    panel = pygame.Rect(40, 244, 1120, 386)
    pygame.draw.rect(surface, PANEL, panel, border_radius=7)
    pygame.draw.rect(surface, GREEN_DIM, panel, 1, border_radius=7)
    _label(surface, _font(18), "TRANSMISSION RETABLIE  /  ELF", (68, 272), GREEN)
    pygame.draw.line(surface, LINE, (68, 314), (1132, 314))
    for index, line in enumerate(messages):
        _label(surface, _font(25 if index == 0 else 22, bold=index == 0), line, (69, 348 + index * 68), WHITE)
    _label(surface, _font(15), "ANNONCE DU DEFI  /  EN ATTENTE DE LA SUITE", (69, 573), AMBER)


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


def _draw_session_status(surface: pygame.Surface, remaining: float, warning: bool, test_mode: bool) -> None:
    color = AMBER if warning else GREEN
    pygame.draw.rect(surface, PANEL, pygame.Rect(792, 74, 367, 120), border_radius=7)
    pygame.draw.rect(surface, color, pygame.Rect(792, 74, 367, 120), 1, border_radius=7)
    _label(surface, _font(14), "TEMPS RESTANT", (811, 88), color)
    minutes, seconds = divmod(math.ceil(remaining), 60)
    _label(surface, _font(32, bold=True), f"{minutes:02}:{seconds:02}", (811, 113), WHITE)
    if warning:
        _label(surface, _font(14, bold=True), "FIN DE SESSION PROCHE", (811, 159), AMBER)
    if test_mode:
        _draw_test_mode_badge(surface)


def _draw_end(surface: pygame.Surface, test_mode: bool, combined_alerts: bool) -> None:
    surface.fill(BACKGROUND)
    _draw_grid(surface)
    _label(surface, _font(44, bold=True), "SESSION TERMINEE", (350, 223), AMBER)
    _label(surface, _font(24), "Le temps est ecoule. Merci a cette equipe.", (326, 310), WHITE)
    _label(surface, _font(21), "Animateur : remettre le laboratoire a zero pour l'equipe suivante.", (171, 391), GREEN)
    _label(surface, _font(17), "CONTROLE + OPTION + COMMANDE + BACKSPACE", (419, 474), GREEN_DIM)
    if combined_alerts:
        _label(surface, _font(17, bold=True), "AVERTISSEMENT DE FIN EMIS", (445, 550), AMBER)
    if test_mode:
        _draw_test_mode_badge(surface)


def _reset_matches(event: pygame.event.Event) -> bool:
    return (event.type == pygame.KEYDOWN and event.key == RESET_KEY
            and all(event.mod & MODIFIERS[name] for name in RESET_MODIFIERS)
            and not any(event.mod & flag for name, flag in MODIFIERS.items()
                        if name not in RESET_MODIFIERS))


def run() -> None:
    parser = argparse.ArgumentParser(description="Laboratoire 1986")
    parser.add_argument("--config", type=Path, default=Path(__file__).resolve().parents[1] / "config.json")
    parser.add_argument("--test-mode", action="store_true", help="Accélère les délais à 10 % sans modifier le fichier de configuration")
    args = parser.parse_args()
    pygame.mixer.pre_init(frequency=44100, size=-16, channels=1)
    pygame.init()
    try:
        config = load_config(args.config)
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Laboratoire 1986 | Terminal de surveillance")
        clock = pygame.time.Clock()
        scale = 0.1 if args.test_mode else 1.0
        session = Session(config.session_seconds * scale, config.possession_seconds * scale,
                          config.warning_seconds * scale)
        started_at = pygame.time.get_ticks()
        previous_tick = started_at
        previous_phase = Phase.LABORATOIRE
        had_contact = False
        warning_active = False
        combined_alerts = False
        sounds = None
        contact_sound = None
        if pygame.mixer.get_init():
            sounds = {Phase.POSSESSION: _tone(83, 1.1), Phase.ELF: _tone(659, 0.7)}
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
                elif config.matches(event) and action != "reinitialiser":
                    action = "declencher_mystere"
            if not running:
                break
            now = pygame.time.get_ticks()
            elapsed = (now - started_at) / 1000
            delta = (now - previous_tick) / 1000
            previous_tick = now
            state = session.advance(delta, action)
            if action == "reinitialiser":
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
            if state.phase is Phase.POSSESSION and state.messages and not had_contact:
                had_contact = True
                if contact_sound:
                    contact_sound.play()
            previous_phase = state.phase
            if state.phase is Phase.LABORATOIRE:
                _draw_welcome(screen, elapsed)
            elif state.phase is Phase.POSSESSION:
                _draw_possession(screen, session.session_seconds - state.remaining_seconds, session.possession_seconds, state.messages)
            elif state.phase is Phase.ELF:
                _draw_elf(screen, elapsed, state.messages)
            elif state.phase is Phase.FIN:
                _draw_end(screen, args.test_mode, combined_alerts)
            else:
                raise AssertionError(f"Phase sans écran : {state.phase}")
            if state.phase in (Phase.POSSESSION, Phase.ELF):
                _draw_session_status(screen, state.remaining_seconds, warning_active, args.test_mode)
            elif state.phase is Phase.LABORATOIRE and args.test_mode:
                _draw_test_mode_badge(screen)
            pygame.display.flip()
            clock.tick(FPS)
    finally:
        pygame.quit()
