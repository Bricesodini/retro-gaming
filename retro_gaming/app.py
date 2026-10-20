"""Procedurally drawn laboratory, gradual possession and Elf contact."""

import argparse
import math
from array import array
from functools import lru_cache
from pathlib import Path

import pygame

from retro_gaming.config import MODIFIERS, RESET_KEY, RESET_MODIFIERS, load_config
from retro_gaming.session import Phase, Session
from retro_gaming.maze import game as maze_game, window as maze_window
from retro_gaming.space_combat import game as space_game, window as space_window
from retro_gaming.platformer import game as platform_game, window as platform_window


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


def _draw_possession(surface: pygame.Surface, elapsed: float, duration: float,
                     messages: tuple[str, ...], variant: str) -> None:
    # The original terminal remains visible beneath a slowly growing disturbance.
    progress = min(1, elapsed / duration)
    _draw_welcome(surface, elapsed, active=True)
    veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    tension = variant == "Tension"
    veil.fill((76, 12, 22, int((64 if tension else 42) * progress)))
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

    if tension:
        # A broad, slowly moving abstract presence in the signal chamber.
        chamber = pygame.Surface((362, 244), pygame.SRCALPHA)
        sway = 7 * math.sin(elapsed * 0.35)
        spread = 115 * progress
        left, right = [], []
        for y in range(45, 211, 11):
            contour = math.sin(math.pi * (y - 45) / 165) ** 0.55
            ripple = 0.12 * math.sin(y * 0.095 + elapsed * 0.45)
            left.append((181 + sway - spread * (contour + ripple), y))
            right.append((181 + sway + spread * (contour - ripple), y))
        outline = left + right[::-1]
        pygame.draw.polygon(chamber, (54, 9, 19, int(215 * progress)), outline)
        pygame.draw.lines(chamber, (203, 79, 82, int(230 * progress)), True, outline, 3)
        surface.blit(chamber, (798, 244))

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
        _label(surface, _font(22, bold=True), messages[-1], (62, 565), WHITE)


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
        _label(surface, _font(25 if index == 0 else 22, bold=index == 0), line, (69, 335 + index * 48), WHITE)
    _label(surface, _font(15), "ENTREE POUR CONTINUER", (69, 583), AMBER)


GAME_LABELS = {
    "maze": ("1", "LABYRINTHE", "Vider le plateau  |  Fleches / WASD"),
    "space_combat": ("2", "COMBAT SPATIAL", "Atteindre le score  |  Fleches / A D + Espace"),
    "platformer": ("3", "PLATEFORMES", "Rejoindre la sortie  |  Fleches / WASD + Espace"),
}


def _draw_choice(surface: pygame.Surface, available_games: tuple[str, ...],
                 remaining: float, warning: bool, test_mode: bool,
                 free_mode: bool = False) -> None:
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
        y = 359 + index * 82
        pygame.draw.line(surface, LINE, (68, y - 13), (1130, y - 13))
        _label(surface, _font(27, True), key, (69, y), AMBER)
        _label(surface, _font(23, True), name, (126, y), WHITE)
        _label(surface, _font(16), instruction, (128, y + 36), GREEN_DIM)
    if not free_mode:
        _draw_session_status(surface, remaining, warning, test_mode)
    elif test_mode:
        _draw_test_mode_badge(surface)


def _new_game(name: str):
    return {"maze": maze_game.Game, "space_combat": space_game.Game,
            "platformer": platform_game.Game}[name]()


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
               remaining: float, warning: bool, test_mode: bool,
               timer_visible: bool, free_mode: bool) -> None:
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
    if timer_visible:
        minutes, seconds = divmod(math.ceil(remaining), 60)
        _label(surface, _font(24, True), f"TEMPS {minutes:02}:{seconds:02}", (956, 24),
               AMBER if warning else GREEN)
    instructions = {
        "maze": ("OBJECTIF : VIDER LE PLATEAU", "FLECHES / WASD : SE DEPLACER"),
        "space_combat": ("OBJECTIF : ATTEINDRE LE SCORE CIBLE", "FLECHES / A D : BOUGER   •   ESPACE : TIRER"),
        "platformer": ("OBJECTIF : REJOINDRE LA PRINCESSE", "FLECHES / WASD : BOUGER / GRIMPER   •   ESPACE : SAUTER"),
    }[name]
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


def _rumble(variant: str) -> pygame.mixer.Sound:
    """Loopable, original low drone with a stronger but still gradual Tension mix."""
    sample_rate = 44100
    seconds = 4
    volume = 0.12 if variant == "Mystère" else 0.32
    samples = array("h")
    for i in range(sample_rate * seconds):
        t = i / sample_rate
        swell = 0.82 + 0.18 * math.sin(2 * math.pi * 0.25 * t)
        if variant == "Mystère":
            value = (0.72 * math.sin(2 * math.pi * 48 * t) +
                     0.28 * math.sin(2 * math.pi * 64 * t))
        else:
            # Midrange harmonics carry the drone on ordinary speakers.
            value = (0.28 * math.sin(2 * math.pi * 48 * t) +
                     0.30 * math.sin(2 * math.pi * 120 * t) +
                     0.26 * math.sin(2 * math.pi * 180 * t) +
                     0.16 * math.sin(2 * math.pi * 240 * t))
        samples.append(int(32767 * volume * swell * value))
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
    _label(surface, _font(24), "ELF // Le temps est ecoule. Rejoignez la salle suivante.", (205, 310), WHITE)
    _label(surface, _font(21), "Animateur : remettre le laboratoire a zero pour l'equipe suivante.", (171, 391), GREEN)
    _label(surface, _font(17), "CONTROLE + OPTION + COMMANDE + BACKSPACE", (419, 474), GREEN_DIM)
    if combined_alerts:
        _label(surface, _font(17, bold=True), "AVERTISSEMENT DE FIN EMIS", (445, 550), AMBER)
    if test_mode:
        _draw_test_mode_badge(surface)


def _draw_victory(surface: pygame.Surface, messages: tuple[str, ...],
                  test_mode: bool) -> None:
    surface.fill(BACKGROUND)
    _draw_grid(surface)
    _label(surface, _font(24, True), "ELF // CONTROLE RETABLI", (381, 165), GREEN)
    _label(surface, _font(44, True), "DEFI REUSSI", (405, 225), WHITE)
    _label(surface, _font(38, True), messages[1], (352, 310), AMBER)
    _label(surface, _font(21), "L'entite annonce son retour. Pour l'instant, jouez librement.",
           (239, 400), GREEN)
    _label(surface, _font(18), "ENTREE POUR ACCEDER AUX TROIS JEUX", (391, 490), WHITE)
    if test_mode:
        _draw_test_mode_badge(surface)


def _draw_failure(surface: pygame.Surface, remaining: float, warning: bool,
                  test_mode: bool) -> None:
    surface.fill(BACKGROUND)
    _draw_grid(surface)
    _label(surface, _font(23, bold=True), "ELF // JE SUIS REVENUE", (421, 171), GREEN)
    _label(surface, _font(44, bold=True), "DEFI ECHOUE", (395, 223), RED)
    _label(surface, _font(24), "Les trois jeux sont perdus. Elf ne peut plus agir.", (262, 310), WHITE)
    _label(surface, _font(21), "Animateur : remettre le laboratoire a zero pour l'equipe suivante.",
           (171, 391), GREEN)
    _label(surface, _font(17), "CONTROLE + OPTION + COMMANDE + BACKSPACE", (419, 474), GREEN_DIM)
    _draw_session_status(surface, remaining, warning, test_mode)


def _reset_matches(event: pygame.event.Event) -> bool:
    return (event.type == pygame.KEYDOWN and event.key == RESET_KEY
            and all(event.mod & MODIFIERS[name] for name in RESET_MODIFIERS)
            and not any(event.mod & flag for name, flag in MODIFIERS.items()
                        if name not in RESET_MODIFIERS))


def run() -> None:
    parser = argparse.ArgumentParser(description="Laboratoire 1986")
    parser.add_argument("--config", type=Path, default=Path(__file__).resolve().parents[1] / "config.json")
    parser.add_argument("--test-mode", action="store_true", help="Accélère les délais à 10 %% sans modifier le fichier de configuration")
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
                          config.warning_seconds * scale, config.room_digit)
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
        drone_channel = None
        if pygame.mixer.get_init():
            sounds = {Phase.ELF: _tone(659, 0.7)}
            drone = _rumble(config.variant)
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
                elif event.type == pygame.KEYDOWN and action != "reinitialiser":
                    if previous_state.phase in (Phase.ELF, Phase.VICTOIRE) and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
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
            if state.phase != previous_phase and pygame.mixer.get_init():
                if state.phase is Phase.POSSESSION:
                    drone_channel = drone.play(loops=-1, fade_ms=700)
                elif drone_channel:
                    drone_channel.fadeout(400)
                    drone_channel = None
            if (state.phase is Phase.POSSESSION and any("ELF" in line for line in state.messages)
                    and not had_contact):
                had_contact = True
                if contact_sound:
                    contact_sound.play()
            previous_phase = state.phase
            previous_state = state
            if state.phase in (Phase.CHOIX, Phase.LIBRE, Phase.VICTOIRE, Phase.FIN):
                game = None
                game_name = None
            if state.phase is Phase.JEU:
                if game is None or game_name != state.active_game:
                    game = _new_game(state.active_game)
                    game_name = state.active_game
                    game_time = 0.0
                else:
                    game.advance(delta, _game_input(state.active_game, pygame.key.get_pressed()))
                    game_time += delta
            if state.phase is Phase.LABORATOIRE:
                _draw_welcome(screen, elapsed)
            elif state.phase is Phase.POSSESSION:
                _draw_possession(screen, (now - phase_started_at) / 1000,
                                 session.possession_seconds, state.messages, config.variant)
            elif state.phase is Phase.ELF:
                _draw_elf(screen, elapsed, state.messages)
            elif state.phase in (Phase.CHOIX, Phase.LIBRE):
                _draw_choice(screen, state.available_games, state.remaining_seconds,
                             warning_active, args.test_mode, state.free_mode)
            elif state.phase in (Phase.JEU, Phase.RESULTAT):
                _draw_game(screen, state.active_game, game.state, game_time,
                           state.remaining_seconds, warning_active, args.test_mode,
                           state.timer_visible, state.free_mode)
            elif state.phase is Phase.VICTOIRE:
                _draw_victory(screen, state.messages, args.test_mode)
            elif state.phase is Phase.FIN:
                _draw_end(screen, args.test_mode, combined_alerts)
            elif state.phase is Phase.ECHEC:
                _draw_failure(screen, state.remaining_seconds, warning_active, args.test_mode)
            else:
                raise AssertionError(f"Phase sans écran : {state.phase}")
            if state.phase in (Phase.POSSESSION, Phase.ELF):
                _draw_session_status(screen, state.remaining_seconds, warning_active, args.test_mode)
            elif state.phase is Phase.LABORATOIRE and args.test_mode:
                _draw_test_mode_badge(screen)
            pygame.display.flip()
            clock.tick(FPS)
    finally:
        _font.cache_clear()
        pygame.quit()
