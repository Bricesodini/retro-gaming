"""Original procedural chiptunes and scene beds for the retro gaming session."""

from array import array
import math

import pygame


# Match the mono mixer rate configured by `retro_gaming.app.run()` so timing and
# pitch remain correct when these raw PCM buffers are played.
SAMPLE_RATE = 44100
_MELODIES = {
    "maze": (76, 79, 83, 79, 74, 77, 81, 77, 72, 76, 79, 76, 74, 77, 81, 77),
    "space_combat": (72, 76, 79, 84, 83, 79, 76, 79, 72, 76, 81, 84, 88, 84, 81, 76),
    "platformer": (74, 77, 81, 86, 84, 81, 77, 81, 74, 77, 83, 86, 89, 86, 83, 77),
}
_BASSES = {
    "maze": (48, 55, 53, 55, 46, 53, 50, 53),
    "space_combat": (45, 52, 48, 55, 43, 50, 48, 52),
    "platformer": (43, 50, 47, 53, 41, 48, 45, 50),
}


def _frequency(midi_note: int) -> float:
    return 440.0 * 2 ** ((midi_note - 69) / 12)


def _square(phase: float) -> float:
    return 1.0 if math.sin(phase) >= 0 else -1.0


def _game_track(name: str) -> pygame.mixer.Sound:
    """An original eight-bar arcade cue with changing phrases and bass."""
    motif = _MELODIES[name]
    bass_motif = _BASSES[name]
    melody_phrases = (
        motif,
        tuple(note + (12 if index in (3, 11) else -2 if index % 4 == 3 else 0)
              for index, note in enumerate(motif)),
        tuple(note + (5 if index % 8 < 4 else 7) for index, note in enumerate(motif)),
        tuple(note + (12 if index in (2, 6, 10, 14) else 0)
              for index, note in enumerate(motif)),
    )
    melody = tuple(note for phrase in melody_phrases for note in phrase)
    bass = tuple(note + shift for shift in (0, 2, 5, 0) for note in bass_motif)
    bpm = 126
    step_seconds = 60 / bpm / 2
    total_seconds = step_seconds * len(melody)
    count = round(SAMPLE_RATE * total_seconds)
    samples = array("h")
    for index in range(count):
        elapsed = index / SAMPLE_RATE
        step = min(len(melody) - 1, int(elapsed / step_seconds))
        step_time = elapsed - step * step_seconds
        note_envelope = min(1.0, step_time / 0.006, (step_seconds - step_time) / 0.022)
        melody_wave = _square(2 * math.pi * _frequency(melody[step]) * elapsed)
        quarter = int(elapsed / (step_seconds * 2)) % len(bass)
        bass_envelope = min(1.0, step_time / 0.009, (step_seconds * 2 - (elapsed % (step_seconds * 2))) / 0.035)
        bass_time = elapsed % (step_seconds * 2)
        bass_wave = _square(2 * math.pi * _frequency(bass[quarter]) * bass_time)
        phrase = step // len(motif)
        phrase_gain = (1.0, 0.82, 0.93, 0.88)[phrase]
        undertone = math.sin(2 * math.pi * _frequency(melody[step]) * 2 * elapsed)
        value = (phrase_gain * (0.09 * melody_wave + 0.018 * undertone) * max(0.0, note_envelope) +
                 0.052 * bass_wave * max(0.0, bass_envelope))
        samples.append(max(-32767, min(32767, int(32767 * value))))
    return pygame.mixer.Sound(buffer=samples.tobytes())


def _entity_drone(variant: str) -> pygame.mixer.Sound:
    seconds = 4
    count = SAMPLE_RATE * seconds
    volume = 0.22 if variant == "Mystère" else 0.34
    samples = array("h")
    for index in range(count):
        elapsed = index / SAMPLE_RATE
        swell = 0.72 + 0.28 * math.sin(2 * math.pi * 0.5 * elapsed)
        phase = 2 * math.pi * elapsed
        bed = (0.33 * math.sin(phase * 38) + 0.27 * math.sin(phase * 51) +
               0.22 * math.sin(phase * 76) + 0.12 * math.sin(phase * 114) +
               0.06 * math.sin(phase * 228))
        samples.append(int(32767 * volume * swell * bed))
    return pygame.mixer.Sound(buffer=samples.tobytes())


def _return_clash() -> pygame.mixer.Sound:
    """Compact rising pulse for the quick, distinct Elf/entity rematch."""
    seconds = 2.0
    count = int(SAMPLE_RATE * seconds)
    samples = array("h")
    for index in range(count):
        elapsed = index / SAMPLE_RATE
        beat = elapsed * 6
        pulse = 0.72 + 0.28 * math.sin(2 * math.pi * beat)
        rise = 1.0 + 0.45 * (elapsed / seconds)
        clash = (0.42 * _square(2 * math.pi * 41 * rise * elapsed) +
                 0.28 * math.sin(2 * math.pi * 196 * rise * elapsed) +
                 0.30 * math.sin(2 * math.pi * 294 * rise * elapsed))
        edge = min(1.0, elapsed / 0.06, (seconds - elapsed) / 0.1)
        samples.append(int(32767 * 0.30 * pulse * max(0.0, edge) * clash))
    return pygame.mixer.Sound(buffer=samples.tobytes())


class Soundtrack:
    def __init__(self, variant: str):
        pygame.mixer.set_reserved(1)
        self.channel = pygame.mixer.Channel(0)
        self._current: str | None = None
        self._sounds = {
            "entity": _entity_drone(variant),
            "return": _return_clash(),
            **{f"game:{name}": _game_track(name) for name in _MELODIES},
        }

    def set_scene(self, scene: str | None) -> None:
        if scene == self._current:
            return
        self._current = scene
        if scene is None:
            self.channel.fadeout(260)
        elif scene in self._sounds:
            volume = 0.30 if scene.startswith("game:") else 0.68 if scene == "entity" else 0.58
            self.channel.set_volume(volume)
            self.channel.play(self._sounds[scene], loops=-1, fade_ms=120)
