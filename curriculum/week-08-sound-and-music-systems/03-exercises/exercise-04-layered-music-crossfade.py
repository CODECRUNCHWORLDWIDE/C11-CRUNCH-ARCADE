"""exercise-04-layered-music-crossfade.py

Goal
----
Play two synthesised music stems IN SYNC on two reserved channels and
crossfade between them when the game-state toggles between "explore"
and "combat." This is the canonical vertical-layering pattern from
Lecture 2 section 3.

Press TAB to toggle the state. The explore stem fades down and the
combat stem fades up over 1.5 seconds. Press SPACE to start or stop
both stems together. Press M to cycle the music-bus volume.
Press ESC to quit.

What you learn
--------------
- Two stems on dedicated, reserved channels so SFX cannot evict them.
- Both stems started on the SAME play() frame so they stay in sync.
- A linear crossfade animated in update_layered_music().
- The state-driven request_combat / request_explore functions that
  set crossfade targets without restarting playback.

Expected behaviour
------------------
- A 900x420 window with two horizontal volume bars labelled "explore"
  and "combat."
- TAB swaps which bar is active; the bars animate the fade over 1.5 s.
- The synthesised "explore" stem is a calm pad; the "combat" stem is
  the same chord with a faster modulation and extra harmonics.
- Both stems loop seamlessly because they are constructed as whole
  numbers of cycles at 44100 Hz.

To complete
-----------
The exercise is COMPLETE as shipped. Run it, press TAB a few times,
listen. Variations are in the HINT block.

Run with::

    python exercise-04-layered-music-crossfade.py

Requires numpy::

    pip install numpy
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass, field
from enum import Enum
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

# Reserve the top two channel indices for the two music layers. SFX
# allocated from the default pool will not evict them.
LAYER_EXPLORE_CHANNEL: int = NUM_CHANNELS - 2
LAYER_COMBAT_CHANNEL: int = NUM_CHANNELS - 1

# Crossfade.
CROSSFADE_MS: int = 1500


# ----- Window configuration -----------------------------------------------

WINDOW_W: int = 900
WINDOW_H: int = 420
TARGET_FPS: int = 60
WINDOW_TITLE: str = "C11 Week 8 - Exercise 4 - Layered music crossfade"

BG_COLOUR: tuple[int, int, int] = (24, 24, 32)
TEXT_COLOUR: tuple[int, int, int] = (240, 240, 240)
DIM_COLOUR: tuple[int, int, int] = (140, 140, 150)

EXPLORE_COLOUR: tuple[int, int, int] = (96, 165, 250)
COMBAT_COLOUR: tuple[int, int, int] = (236, 72, 153)
ACTIVE_GREEN: tuple[int, int, int] = (132, 204, 22)


# ----- Music state --------------------------------------------------------


class MusicState(Enum):
    EXPLORE = "explore"
    COMBAT = "combat"


@dataclass
class LayerCrossfade:
    """The animation state for the crossfade between layers."""

    state: MusicState = MusicState.EXPLORE
    target_explore: float = 1.0
    target_combat: float = 0.0
    from_explore: float = 1.0
    from_combat: float = 0.0
    t_remaining_ms: int = 0
    fade_total_ms: int = CROSSFADE_MS

    def request_combat(self, current_explore: float, current_combat: float) -> None:
        self.state = MusicState.COMBAT
        self.from_explore = current_explore
        self.from_combat = current_combat
        self.target_explore = 0.0
        self.target_combat = 1.0
        self.t_remaining_ms = self.fade_total_ms

    def request_explore(self, current_explore: float, current_combat: float) -> None:
        self.state = MusicState.EXPLORE
        self.from_explore = current_explore
        self.from_combat = current_combat
        self.target_explore = 1.0
        self.target_combat = 0.0
        self.t_remaining_ms = self.fade_total_ms

    def current_levels(self) -> tuple[float, float]:
        """Where on the crossfade ramp are we, returns (explore, combat)."""
        if self.t_remaining_ms <= 0:
            return self.target_explore, self.target_combat
        progress: float = 1.0 - (self.t_remaining_ms / self.fade_total_ms)
        e: float = self.from_explore + (self.target_explore - self.from_explore) * progress
        c: float = self.from_combat + (self.target_combat - self.from_combat) * progress
        return e, c

    def advance(self, dt_ms: int) -> None:
        if self.t_remaining_ms > 0:
            self.t_remaining_ms -= dt_ms
            if self.t_remaining_ms < 0:
                self.t_remaining_ms = 0


# ----- Stem synthesis -----------------------------------------------------


def synthesise_loop(
    base_freq: float,
    overtone_amps: tuple[float, ...],
    modulation_hz: float,
    duration_s: float = 4.0,
    base_amplitude: float = 0.30,
) -> pygame.mixer.Sound:
    """Generate a multi-overtone pad with an amplitude modulator.

    For seamless looping, duration_s should be chosen so the
    modulation completes a whole number of cycles. We round.
    """
    if not NUMPY_OK:
        raise RuntimeError("numpy required - pip install numpy")
    # Round duration so modulation_hz completes whole cycles.
    cycles: int = max(1, round(modulation_hz * duration_s))
    adjusted_duration_s: float = cycles / modulation_hz
    n: int = int(SAMPLE_RATE_HZ * adjusted_duration_s)
    t: "np.ndarray" = np.linspace(0.0, adjusted_duration_s, n, endpoint=False)
    wave: "np.ndarray" = np.zeros(n, dtype=np.float32)
    for i, amp in enumerate(overtone_amps):
        partial: float = (i + 1) * base_freq
        wave += float(amp) * np.sin(2.0 * math.pi * partial * t).astype(np.float32)
    # Amplitude modulation for movement.
    mod: "np.ndarray" = 0.7 + 0.3 * np.sin(2.0 * math.pi * modulation_hz * t)
    shaped: "np.ndarray" = wave * mod * base_amplitude
    # Small attack/release to suppress any edge clicks.
    attack_n: int = int(SAMPLE_RATE_HZ * 0.020)
    release_n: int = int(SAMPLE_RATE_HZ * 0.020)
    env: "np.ndarray" = np.ones(n, dtype=np.float32)
    if attack_n > 0:
        env[:attack_n] = np.linspace(0.0, 1.0, attack_n)
    if release_n > 0 and release_n < n:
        env[-release_n:] = np.linspace(1.0, 0.0, release_n)
    shaped = shaped * env
    mono: "np.ndarray" = np.clip(shaped * 32767, -32767, 32767).astype(np.int16)
    stereo: "np.ndarray" = np.column_stack((mono, mono))
    return pygame.sndarray.make_sound(stereo)


def build_explore_layer() -> pygame.mixer.Sound:
    """Calm pad on A2 with mild modulation."""
    return synthesise_loop(
        base_freq=110.0,
        overtone_amps=(1.0, 0.5, 0.3, 0.15),
        modulation_hz=0.5,
        duration_s=4.0,
        base_amplitude=0.32,
    )


def build_combat_layer() -> pygame.mixer.Sound:
    """Same root, more overtones, faster modulation, brighter."""
    return synthesise_loop(
        base_freq=110.0,
        overtone_amps=(0.7, 0.7, 0.6, 0.5, 0.4, 0.3),
        modulation_hz=2.0,
        duration_s=4.0,
        base_amplitude=0.34,
    )


# ----- The exercise --------------------------------------------------------


def main() -> int:
    pygame.mixer.pre_init(SAMPLE_RATE_HZ, BIT_DEPTH_SIZE, CHANNELS, BUFFER_SAMPLES)
    try:
        pygame.init()
    except pygame.error as e:
        print(f"pygame.init() failed: {e}")
        return 1
    pygame.mixer.set_num_channels(NUM_CHANNELS)

    if not NUMPY_OK:
        print("numpy is required for Exercise 4. Install with: pip install numpy")
        pygame.quit()
        return 1

    screen: pygame.Surface = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    pygame.display.set_caption(WINDOW_TITLE)
    clock: pygame.time.Clock = pygame.time.Clock()
    font_lg: pygame.font.Font = pygame.font.SysFont(None, 26)
    font_sm: pygame.font.Font = pygame.font.SysFont(None, 20)

    explore_sound: pygame.mixer.Sound = build_explore_layer()
    combat_sound: pygame.mixer.Sound = build_combat_layer()

    ch_explore: pygame.mixer.Channel = pygame.mixer.Channel(LAYER_EXPLORE_CHANNEL)
    ch_combat: pygame.mixer.Channel = pygame.mixer.Channel(LAYER_COMBAT_CHANNEL)

    music_bus_volume: float = 0.60
    crossfade: LayerCrossfade = LayerCrossfade()
    music_playing: bool = False

    music_volume_cycle: tuple[float, ...] = (0.60, 0.30, 0.00, 1.00)

    def start_music() -> None:
        # Start both stems on the same call frame to keep them in sync.
        explore_sound.set_volume(music_bus_volume * crossfade.target_explore)
        combat_sound.set_volume(music_bus_volume * crossfade.target_combat)
        ch_explore.play(explore_sound, loops=-1)
        ch_combat.play(combat_sound, loops=-1)

    def stop_music() -> None:
        ch_explore.fadeout(400)
        ch_combat.fadeout(400)

    running: bool = True
    last_text: str = "(press SPACE to start music, TAB to toggle layer)"
    while running:
        dt_ms: int = clock.tick(TARGET_FPS)

        # ---- Events -----------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    if music_playing:
                        stop_music()
                        music_playing = False
                        last_text = "music stopped"
                    else:
                        start_music()
                        music_playing = True
                        last_text = "music started (explore + combat in sync)"
                elif event.key == pygame.K_TAB:
                    e_now, c_now = crossfade.current_levels()
                    if crossfade.state == MusicState.EXPLORE:
                        crossfade.request_combat(e_now, c_now)
                        last_text = "request COMBAT layer (1.5 s crossfade)"
                    else:
                        crossfade.request_explore(e_now, c_now)
                        last_text = "request EXPLORE layer (1.5 s crossfade)"
                elif event.key == pygame.K_m:
                    # Cycle music-bus volume.
                    cur_idx: int = 0
                    best_d: float = 999.0
                    for i, v in enumerate(music_volume_cycle):
                        if abs(v - music_bus_volume) < best_d:
                            best_d = abs(v - music_bus_volume)
                            cur_idx = i
                    music_bus_volume = music_volume_cycle[(cur_idx + 1) % len(music_volume_cycle)]
                    last_text = f"music bus volume -> {music_bus_volume:.2f}"

        # ---- Update -----------------------------------------------------
        crossfade.advance(dt_ms)
        e_lvl, c_lvl = crossfade.current_levels()
        if music_playing:
            ch_explore.set_volume(music_bus_volume * e_lvl)
            ch_combat.set_volume(music_bus_volume * c_lvl)

        # ---- Render -----------------------------------------------------
        screen.fill(BG_COLOUR)

        title: pygame.Surface = font_lg.render(
            f"LAYERED MUSIC - state: {crossfade.state.value.upper()}",
            True, TEXT_COLOUR,
        )
        screen.blit(title, (24, 22))

        # Bars
        bar_x: int = 60
        bar_w: int = WINDOW_W - 120
        bar_h: int = 32

        def draw_bar(y: int, label: str, level: float, colour: tuple[int, int, int]) -> None:
            lbl: pygame.Surface = font_sm.render(label, True, TEXT_COLOUR)
            screen.blit(lbl, (bar_x, y - 22))
            track: pygame.Rect = pygame.Rect(bar_x, y, bar_w, bar_h)
            pygame.draw.rect(screen, (60, 60, 70), track, border_radius=5)
            fill_w: int = int(bar_w * max(0.0, min(1.0, level)))
            fill_rect: pygame.Rect = pygame.Rect(bar_x, y, fill_w, bar_h)
            pygame.draw.rect(screen, colour, fill_rect, border_radius=5)
            num: pygame.Surface = font_sm.render(
                f"{level * music_bus_volume:.2f}  (raw {level:.2f})", True, TEXT_COLOUR
            )
            screen.blit(num, (bar_x + bar_w + 12, y + 6))

        draw_bar(110, "explore layer", e_lvl, EXPLORE_COLOUR)
        draw_bar(190, "combat layer", c_lvl, COMBAT_COLOUR)

        # Status.
        status_lines: list[tuple[str, tuple[int, int, int]]] = [
            (f"music playing: {music_playing}     music bus volume: {music_bus_volume:.2f}",
             ACTIVE_GREEN if music_playing else DIM_COLOUR),
            (f"crossfade remaining: {crossfade.t_remaining_ms} ms",
             TEXT_COLOUR if crossfade.t_remaining_ms > 0 else DIM_COLOUR),
            (f"explore len: {explore_sound.get_length():.3f} s     "
             f"combat len: {combat_sound.get_length():.3f} s",
             TEXT_COLOUR),
        ]
        sy: int = 270
        for text, colour_each in status_lines:
            surf: pygame.Surface = font_sm.render(text, True, colour_each)
            screen.blit(surf, (24, sy))
            sy += 22

        ctl: pygame.Surface = font_sm.render(
            "[SPACE] start/stop   [TAB] toggle layer   [M] music vol   [ESC] quit",
            True, DIM_COLOUR,
        )
        screen.blit(ctl, (24, WINDOW_H - 50))
        last: pygame.Surface = font_sm.render(last_text, True, TEXT_COLOUR)
        screen.blit(last, (24, WINDOW_H - 26))

        pygame.display.flip()

    pygame.quit()
    return 0


# ----- HINT (do not peek for 20 minutes) -----------------------------------
# If the two layers DRIFT out of sync over time, they have different
# sample counts. Confirm explore_sound.get_length() and
# combat_sound.get_length() print equal values. The synthesise_loop
# function rounds to whole modulation cycles for exactly this reason.
#
# If you hear a click at the loop point, the synthesised duration is
# not landing on the modulation's whole-cycle boundary. Increase the
# attack_n / release_n parameters in synthesise_loop to mask edge
# transients.
#
# If TAB does not transition, confirm crossfade.t_remaining_ms is
# being decremented by advance(). The most common bug here is calling
# advance(dt_seconds) instead of advance(dt_ms) - the units must
# match the CROSSFADE_MS constant.
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    sys.exit(main())
