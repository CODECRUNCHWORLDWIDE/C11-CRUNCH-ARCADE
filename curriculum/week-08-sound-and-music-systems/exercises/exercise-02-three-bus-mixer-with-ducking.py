"""exercise-02-three-bus-mixer-with-ducking.py

Goal
----
Build the three-bus mixer from Lecture 2 (master / music / sfx /
voice) in code, wire a synthesised dialogue clip to a duck-event,
and let the user drive volume sliders and trigger SFX or dialogue
to observe the duck.

Press M, S, V to cycle the music / sfx / voice bus volumes (down
then back up). Press D to play a 1.5-second dialogue clip; the
music will duck while it plays and restore on the endevent. Press
1 / 2 to play short and long SFX. Press SPACE to play music; ESC
to quit.

What you learn
--------------
- The Bus dataclass with parent/child links and effective_volume.
- The AudioMixer facade that owns the bus tree.
- Event-driven ducking via Channel.set_endevent and a USEREVENT id.
- Linear fade animation as a per-frame update.
- The duck-during-duck ref-count edge case.

Expected behaviour
------------------
- A 900x420 window with three vertical bus sliders rendered on the
  right and a HUD on the left.
- Pressing M cycles music volume 1.0 -> 0.5 -> 0.0 -> 1.0.
- Pressing D plays a synthesised 1.5 s "dialogue" tone (a square wave
  meant to suggest a voice envelope, not real speech). During the
  clip the music bus fades down to ~0.30; after the clip ends, it
  fades back up.
- The slider bars show real-time effective volume per bus.

To complete
-----------
The exercise is COMPLETE as shipped. Read top to bottom, run it,
listen with headphones. Variations are in the HINT block.

Run with::

    python exercise-02-three-bus-mixer-with-ducking.py

Requires numpy (for tone synthesis)::

    pip install numpy
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass, field
from typing import Optional

import pygame

try:
    import numpy as np
    NUMPY_OK: bool = True
except ImportError:
    NUMPY_OK = False

# ----- Audio configuration ------------------------------------------------

SAMPLE_RATE_HZ: int = 44100
BIT_DEPTH_SIZE: int = -16
CHANNELS: int = 2
BUFFER_SAMPLES: int = 512
NUM_CHANNELS: int = 16

DIALOGUE_END_EVENT: int = pygame.USEREVENT + 1
DIALOGUE_CHANNEL_INDEX: int = 0


# Duck parameters.
DUCK_TARGET_MUSIC_VOLUME: float = 0.30
DUCK_RESTORE_MUSIC_VOLUME: float = 1.00
DUCK_FADE_MS: int = 300


# ----- The Bus and AudioMixer abstractions --------------------------------


@dataclass
class Bus:
    """A named volume multiplier with optional parent."""

    name: str
    volume: float = 1.0
    muted: bool = False
    parent: Optional["Bus"] = None
    children: list["Bus"] = field(default_factory=list)

    def attach(self, child: "Bus") -> "Bus":
        child.parent = self
        self.children.append(child)
        return child

    def effective_volume(self) -> float:
        if self.muted:
            return 0.0
        v: float = self.volume
        p: Optional[Bus] = self.parent
        while p is not None:
            if p.muted:
                return 0.0
            v *= p.volume
            p = p.parent
        return max(0.0, min(1.0, v))

    def set_volume(self, value: float) -> None:
        self.volume = max(0.0, min(1.0, value))


@dataclass
class DuckState:
    active: bool = False
    t_remaining_ms: int = 0
    from_vol: float = 1.0
    to_vol: float = 1.0
    ref_count: int = 0


class AudioMixer:
    """Owns the bus tree and routes plays through it."""

    def __init__(self) -> None:
        self.master: Bus = Bus("master", volume=0.80)
        self.music: Bus = self.master.attach(Bus("music", volume=0.60))
        self.sfx: Bus = self.master.attach(Bus("sfx", volume=1.00))
        self.voice: Bus = self.master.attach(Bus("voice", volume=1.00))
        self.duck: DuckState = DuckState()

    def play_sfx(self, sound: pygame.mixer.Sound) -> Optional[pygame.mixer.Channel]:
        sound.set_volume(self.sfx.effective_volume())
        return sound.play()

    def play_voice(self, sound: pygame.mixer.Sound) -> Optional[pygame.mixer.Channel]:
        sound.set_volume(self.voice.effective_volume())
        ch: pygame.mixer.Channel = pygame.mixer.Channel(DIALOGUE_CHANNEL_INDEX)
        ch.set_endevent(DIALOGUE_END_EVENT)
        ch.play(sound)
        self.begin_duck()
        return ch

    def begin_duck(self) -> None:
        self.duck.ref_count += 1
        if self.duck.ref_count == 1:
            self.duck.active = True
            self.duck.from_vol = self.music.volume
            self.duck.to_vol = DUCK_TARGET_MUSIC_VOLUME
            self.duck.t_remaining_ms = DUCK_FADE_MS

    def end_duck(self) -> None:
        if self.duck.ref_count > 0:
            self.duck.ref_count -= 1
        if self.duck.ref_count == 0:
            self.duck.active = True
            self.duck.from_vol = self.music.volume
            self.duck.to_vol = DUCK_RESTORE_MUSIC_VOLUME
            self.duck.t_remaining_ms = DUCK_FADE_MS

    def update_duck(self, dt_ms: int) -> None:
        if not self.duck.active:
            return
        self.duck.t_remaining_ms -= dt_ms
        if self.duck.t_remaining_ms <= 0:
            self.music.set_volume(self.duck.to_vol)
            self.duck.active = False
            self._reapply_music_volume()
            return
        progress: float = 1.0 - (self.duck.t_remaining_ms / DUCK_FADE_MS)
        v: float = self.duck.from_vol + (self.duck.to_vol - self.duck.from_vol) * progress
        self.music.set_volume(v)
        self._reapply_music_volume()

    def _reapply_music_volume(self) -> None:
        # Propagate to the streaming music subsystem.
        pygame.mixer.music.set_volume(self.music.effective_volume())


# ----- Tone synthesis -----------------------------------------------------


def synthesise_sine(frequency_hz: float, duration_s: float, amplitude: float = 0.55) -> pygame.mixer.Sound:
    """A short sine tone with attack/release."""
    if not NUMPY_OK:
        raise RuntimeError("numpy required - pip install numpy")
    n: int = int(SAMPLE_RATE_HZ * duration_s)
    t: "np.ndarray" = np.linspace(0.0, duration_s, n, endpoint=False)
    wave: "np.ndarray" = np.sin(2.0 * math.pi * frequency_hz * t)
    env: "np.ndarray" = np.ones(n, dtype=np.float32)
    attack_n: int = max(1, int(SAMPLE_RATE_HZ * 0.005))
    release_n: int = max(1, int(SAMPLE_RATE_HZ * 0.025))
    env[:attack_n] = np.linspace(0.0, 1.0, attack_n)
    env[-release_n:] = np.linspace(1.0, 0.0, release_n)
    shaped: "np.ndarray" = wave * env * amplitude
    mono: "np.ndarray" = (shaped * 32767).astype(np.int16)
    stereo: "np.ndarray" = np.column_stack((mono, mono))
    return pygame.sndarray.make_sound(stereo)


def synthesise_dialogue(duration_s: float = 1.5) -> pygame.mixer.Sound:
    """A vaguely speech-like clip: amplitude-modulated mid-frequency tone."""
    if not NUMPY_OK:
        raise RuntimeError("numpy required - pip install numpy")
    n: int = int(SAMPLE_RATE_HZ * duration_s)
    t: "np.ndarray" = np.linspace(0.0, duration_s, n, endpoint=False)
    # Carrier in the speech range (~250 Hz), modulated by a 5 Hz
    # syllable-rate envelope to suggest spoken cadence.
    carrier: "np.ndarray" = np.sin(2.0 * math.pi * 250.0 * t)
    mod: "np.ndarray" = 0.5 + 0.5 * np.sin(2.0 * math.pi * 5.0 * t)
    shaped: "np.ndarray" = carrier * mod * 0.55
    mono: "np.ndarray" = (shaped * 32767).astype(np.int16)
    stereo: "np.ndarray" = np.column_stack((mono, mono))
    return pygame.sndarray.make_sound(stereo)


def synthesise_music_loop(duration_s: float = 4.0) -> pygame.mixer.Sound:
    """A short pad-like loop. Sum of three sine waves."""
    if not NUMPY_OK:
        raise RuntimeError("numpy required - pip install numpy")
    n: int = int(SAMPLE_RATE_HZ * duration_s)
    t: "np.ndarray" = np.linspace(0.0, duration_s, n, endpoint=False)
    wave: "np.ndarray" = (
        0.5 * np.sin(2.0 * math.pi * 220.0 * t)
        + 0.3 * np.sin(2.0 * math.pi * 330.0 * t)
        + 0.2 * np.sin(2.0 * math.pi * 440.0 * t)
    )
    # Soft envelope to ensure no click on loop (sample 0 and sample n-1
    # land exactly at zero by construction since the sines complete
    # whole cycles at integer multiples of duration_s? Not guaranteed.
    # Apply a 30 ms fade in/out to suppress edges.
    attack_n: int = int(SAMPLE_RATE_HZ * 0.030)
    release_n: int = int(SAMPLE_RATE_HZ * 0.030)
    env: "np.ndarray" = np.ones(n, dtype=np.float32)
    env[:attack_n] = np.linspace(0.0, 1.0, attack_n)
    env[-release_n:] = np.linspace(1.0, 0.0, release_n)
    shaped: "np.ndarray" = wave * env * 0.30
    mono: "np.ndarray" = (shaped * 32767).astype(np.int16)
    stereo: "np.ndarray" = np.column_stack((mono, mono))
    return pygame.sndarray.make_sound(stereo)


# ----- Window configuration -----------------------------------------------

WINDOW_W: int = 900
WINDOW_H: int = 420
TARGET_FPS: int = 60
WINDOW_TITLE: str = "C11 Week 8 - Exercise 2 - Three-bus mixer with ducking"

BG_COLOUR: tuple[int, int, int] = (24, 24, 32)
TEXT_COLOUR: tuple[int, int, int] = (240, 240, 240)
DIM_COLOUR: tuple[int, int, int] = (140, 140, 150)
ACTIVE_COLOUR: tuple[int, int, int] = (132, 204, 22)
DUCK_COLOUR: tuple[int, int, int] = (251, 146, 60)


# Cycle order for keypress to set music/sfx/voice volume.
VOLUME_CYCLE: tuple[float, ...] = (1.0, 0.5, 0.0)


def cycle_index(current_value: float) -> int:
    """Find the cycle index closest to the given value."""
    best_i: int = 0
    best_d: float = 999.0
    for i, v in enumerate(VOLUME_CYCLE):
        d: float = abs(current_value - v)
        if d < best_d:
            best_d = d
            best_i = i
    return best_i


def main() -> int:
    pygame.mixer.pre_init(SAMPLE_RATE_HZ, BIT_DEPTH_SIZE, CHANNELS, BUFFER_SAMPLES)
    try:
        pygame.init()
    except pygame.error as e:
        print(f"pygame.init() failed: {e}")
        return 1
    pygame.mixer.set_num_channels(NUM_CHANNELS)

    if not NUMPY_OK:
        print("numpy is required for Exercise 2. Install with: pip install numpy")
        pygame.quit()
        return 1

    screen: pygame.Surface = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    pygame.display.set_caption(WINDOW_TITLE)
    clock: pygame.time.Clock = pygame.time.Clock()
    font_lg: pygame.font.Font = pygame.font.SysFont(None, 26)
    font_sm: pygame.font.Font = pygame.font.SysFont(None, 20)

    mixer: AudioMixer = AudioMixer()

    sfx_short: pygame.mixer.Sound = synthesise_sine(880.0, 0.18)
    sfx_long: pygame.mixer.Sound = synthesise_sine(440.0, 0.60)
    dialogue: pygame.mixer.Sound = synthesise_dialogue(1.5)
    music_loop: pygame.mixer.Sound = synthesise_music_loop(4.0)
    music_channel: pygame.mixer.Channel = pygame.mixer.Channel(15)

    music_playing: bool = False

    running: bool = True
    last_event_text: str = "(no events yet)"
    while running:
        dt_ms: int = clock.tick(TARGET_FPS)

        # ---- Events -----------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == DIALOGUE_END_EVENT:
                mixer.end_duck()
                last_event_text = "dialogue ended -> duck releases"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    if music_playing:
                        music_channel.fadeout(500)
                        music_playing = False
                        last_event_text = "music stopped"
                    else:
                        music_loop.set_volume(mixer.music.effective_volume())
                        music_channel.play(music_loop, loops=-1)
                        music_playing = True
                        last_event_text = "music started (looping pad)"
                elif event.key == pygame.K_m:
                    idx: int = (cycle_index(mixer.music.volume) + 1) % len(VOLUME_CYCLE)
                    mixer.music.set_volume(VOLUME_CYCLE[idx])
                    mixer._reapply_music_volume()
                    if music_playing:
                        music_channel.set_volume(mixer.music.effective_volume())
                    last_event_text = f"music bus volume -> {VOLUME_CYCLE[idx]:.2f}"
                elif event.key == pygame.K_s:
                    idx_s: int = (cycle_index(mixer.sfx.volume) + 1) % len(VOLUME_CYCLE)
                    mixer.sfx.set_volume(VOLUME_CYCLE[idx_s])
                    last_event_text = f"sfx bus volume -> {VOLUME_CYCLE[idx_s]:.2f}"
                elif event.key == pygame.K_v:
                    idx_v: int = (cycle_index(mixer.voice.volume) + 1) % len(VOLUME_CYCLE)
                    mixer.voice.set_volume(VOLUME_CYCLE[idx_v])
                    last_event_text = f"voice bus volume -> {VOLUME_CYCLE[idx_v]:.2f}"
                elif event.key == pygame.K_d:
                    mixer.play_voice(dialogue)
                    last_event_text = "dialogue start -> duck engages"
                elif event.key == pygame.K_1:
                    mixer.play_sfx(sfx_short)
                    last_event_text = "sfx short (880 Hz)"
                elif event.key == pygame.K_2:
                    mixer.play_sfx(sfx_long)
                    last_event_text = "sfx long (440 Hz)"

        # ---- Update -----------------------------------------------------
        mixer.update_duck(dt_ms)
        if music_playing:
            music_channel.set_volume(mixer.music.effective_volume())

        # ---- Render -----------------------------------------------------
        screen.fill(BG_COLOUR)

        # HUD left.
        lines: list[tuple[str, tuple[int, int, int]]] = [
            ("THREE-BUS MIXER", TEXT_COLOUR),
            ("", TEXT_COLOUR),
            (f"master volume:  {mixer.master.volume:.2f}    effective: {mixer.master.effective_volume():.2f}",
             TEXT_COLOUR),
            (f"music  volume:  {mixer.music.volume:.2f}    effective: {mixer.music.effective_volume():.2f}",
             TEXT_COLOUR),
            (f"sfx    volume:  {mixer.sfx.volume:.2f}    effective: {mixer.sfx.effective_volume():.2f}",
             TEXT_COLOUR),
            (f"voice  volume:  {mixer.voice.volume:.2f}    effective: {mixer.voice.effective_volume():.2f}",
             TEXT_COLOUR),
            ("", TEXT_COLOUR),
            (f"duck active: {mixer.duck.active}    ref count: {mixer.duck.ref_count}",
             DUCK_COLOUR if mixer.duck.active else DIM_COLOUR),
            (f"music playing: {music_playing}", TEXT_COLOUR),
            ("", TEXT_COLOUR),
            (f"last event: {last_event_text}", ACTIVE_COLOUR),
            ("", TEXT_COLOUR),
            ("[SPACE] music   [M] music vol   [S] sfx vol   [V] voice vol", DIM_COLOUR),
            ("[1] sfx short   [2] sfx long   [D] dialogue (ducks music)   [ESC] quit", DIM_COLOUR),
        ]
        y: int = 18
        for text, colour_line in lines:
            surf: pygame.Surface = font_sm.render(text, True, colour_line)
            screen.blit(surf, (18, y))
            y += 22

        # Slider visualisation on the right.
        slider_x: int = WINDOW_W - 260
        slider_w: int = 60
        slider_h: int = 240
        slider_y: int = 40
        for i, (name, bus) in enumerate(
            [("master", mixer.master), ("music", mixer.music),
             ("sfx", mixer.sfx), ("voice", mixer.voice)]
        ):
            x: int = slider_x + i * (slider_w + 18)
            # Track
            track: pygame.Rect = pygame.Rect(x, slider_y, slider_w, slider_h)
            pygame.draw.rect(screen, (60, 60, 70), track, border_radius=4)
            # Fill (effective volume)
            fill_h: int = int(slider_h * bus.effective_volume())
            fill_rect: pygame.Rect = pygame.Rect(x, slider_y + slider_h - fill_h, slider_w, fill_h)
            fill_colour: tuple[int, int, int] = (
                DUCK_COLOUR if (name == "music" and mixer.duck.active) else ACTIVE_COLOUR
            )
            pygame.draw.rect(screen, fill_colour, fill_rect, border_radius=4)
            label: pygame.Surface = font_sm.render(name, True, TEXT_COLOUR)
            screen.blit(label, label.get_rect(midtop=(x + slider_w // 2, slider_y + slider_h + 8)))
            value_label: pygame.Surface = font_lg.render(
                f"{bus.effective_volume():.2f}", True, TEXT_COLOUR
            )
            screen.blit(value_label, value_label.get_rect(midtop=(x + slider_w // 2, slider_y - 26)))

        pygame.display.flip()

    pygame.quit()
    return 0


# ----- HINT (do not peek for 20 minutes) -----------------------------------
# If the duck never restores, the DIALOGUE_END_EVENT handler is not
# being called. Confirm two things: (1) the dialogue is played via
# play_voice() (not play_sfx()), and (2) the Channel.set_endevent
# call happened on the SAME channel object that plays the sound.
# The exercise uses pygame.mixer.Channel(0) explicitly to avoid this
# class of mistake.
#
# If multiple dialogue triggers cause the music to stay ducked, the
# ref-count is broken. Check that begin_duck always increments and
# end_duck always decrements, regardless of whether the duck was
# already active.
#
# If the music bus slider visually lags the audible volume, the
# music_channel.set_volume call in the update block is gated by an
# `if music_playing` condition. Confirm that condition is true while
# the music is in the channel.
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    sys.exit(main())
