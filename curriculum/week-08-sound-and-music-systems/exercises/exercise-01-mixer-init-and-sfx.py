"""exercise-01-mixer-init-and-sfx.py

Goal
----
Initialise pygame.mixer correctly (pre_init before pygame.init) and
play synthesised test tones on demand. This exercise has NO external
audio assets - every sound is generated in code via pygame.sndarray
and numpy. The point is the mixer plumbing, not the content.

Press 1-8 to play eight different tones. Press SPACE to play all eight
at once (the channel-pool stress test). Press ESC to quit.

What you learn
--------------
- pygame.mixer.pre_init before pygame.init, with explicit parameters.
- pygame.mixer.set_num_channels for explicit channel allocation.
- Generating audio in-memory as a numpy int16 array.
- Constructing a pygame.mixer.Sound from a numpy array via
  pygame.sndarray.make_sound.
- The Sound.play return value (an optional Channel handle).
- The clipping behaviour when multiple loud sounds stack.

Expected behaviour
------------------
- An 800x320 window with a dark background.
- Eight coloured swatches across the bottom, one per tone, labelled
  1 to 8.
- Pressing 1-8 plays the matching tone and flashes the swatch.
- SPACE plays all eight simultaneously; you can hear clipping if the
  master volume is too high.
- The HUD shows current playback channel counts (busy / total).

To complete
-----------
Read top-to-bottom. The exercise is COMPLETE as shipped - run it and
listen. The HINT block at the bottom suggests variations.

Run with::

    python exercise-01-mixer-init-and-sfx.py

If numpy is not installed::

    pip install numpy
"""

from __future__ import annotations

import math
import sys
from typing import Optional

import pygame

try:
    import numpy as np
    NUMPY_OK: bool = True
except ImportError:
    NUMPY_OK = False


# ----- Audio configuration ------------------------------------------------

SAMPLE_RATE_HZ: int = 44100
BIT_DEPTH_SIZE: int = -16     # negative = signed
CHANNELS: int = 2             # stereo
BUFFER_SAMPLES: int = 512

NUM_CHANNELS: int = 16
TONE_DURATION_S: float = 0.30
TONE_FADE_MS: int = 30

# Eight frequencies spanning a major scale (C4 to C5).
TONE_FREQUENCIES_HZ: tuple[float, ...] = (
    261.63,  # C4
    293.66,  # D4
    329.63,  # E4
    349.23,  # F4
    392.00,  # G4
    440.00,  # A4
    493.88,  # B4
    523.25,  # C5
)

# ----- Window configuration -----------------------------------------------

WINDOW_W: int = 800
WINDOW_H: int = 320
TARGET_FPS: int = 60
WINDOW_TITLE: str = "C11 Week 8 - Exercise 1 - Mixer init and SFX"

BG_COLOUR: tuple[int, int, int] = (24, 24, 32)
TEXT_COLOUR: tuple[int, int, int] = (240, 240, 240)
DIM_COLOUR: tuple[int, int, int] = (140, 140, 150)

SWATCH_PALETTE: tuple[tuple[int, int, int], ...] = (
    (236, 72, 153),
    (250, 204, 21),
    (132, 204, 22),
    (45, 212, 191),
    (96, 165, 250),
    (167, 139, 250),
    (244, 114, 182),
    (251, 146, 60),
)

FLASH_FRAMES: int = 18


# ----- Tone synthesis -----------------------------------------------------


def synthesise_tone(
    frequency_hz: float,
    duration_s: float,
    sample_rate_hz: int = SAMPLE_RATE_HZ,
    amplitude: float = 0.55,
) -> "pygame.mixer.Sound":
    """Build a stereo sine-wave pygame.mixer.Sound from scratch.

    The sound has a short attack/release envelope so it does not click
    at the start and end. The envelope is the only thing standing
    between a clean tone and a noticeable digital pop.
    """
    if not NUMPY_OK:
        raise RuntimeError("numpy is required for tone synthesis - install with: pip install numpy")
    n_samples: int = int(sample_rate_hz * duration_s)
    t: "np.ndarray" = np.linspace(0.0, duration_s, n_samples, endpoint=False)
    # Sine wave at the requested frequency.
    wave: "np.ndarray" = np.sin(2.0 * math.pi * frequency_hz * t)
    # Short attack and release to suppress click artefacts at the edges.
    attack_n: int = int(sample_rate_hz * 0.005)   # 5 ms attack
    release_n: int = int(sample_rate_hz * 0.025)  # 25 ms release
    envelope: "np.ndarray" = np.ones(n_samples, dtype=np.float32)
    if attack_n > 0:
        envelope[:attack_n] = np.linspace(0.0, 1.0, attack_n)
    if release_n > 0 and release_n < n_samples:
        envelope[-release_n:] = np.linspace(1.0, 0.0, release_n)
    shaped: "np.ndarray" = wave * envelope * amplitude
    # Scale to int16 range. Stereo: copy mono into both channels.
    int_max: int = 32767
    mono_int16: "np.ndarray" = (shaped * int_max).astype(np.int16)
    stereo_int16: "np.ndarray" = np.column_stack((mono_int16, mono_int16))
    return pygame.sndarray.make_sound(stereo_int16)


def build_tone_bank() -> list["pygame.mixer.Sound"]:
    """Synthesise eight tones from the global frequency list."""
    return [synthesise_tone(freq, TONE_DURATION_S) for freq in TONE_FREQUENCIES_HZ]


# ----- The exercise --------------------------------------------------------


def main() -> int:
    # IMPORTANT: pre_init BEFORE pygame.init.
    pygame.mixer.pre_init(
        frequency=SAMPLE_RATE_HZ,
        size=BIT_DEPTH_SIZE,
        channels=CHANNELS,
        buffer=BUFFER_SAMPLES,
    )
    try:
        pygame.init()
    except pygame.error as e:
        print(f"pygame.init() failed: {e}")
        return 1

    pygame.mixer.set_num_channels(NUM_CHANNELS)

    if not NUMPY_OK:
        print("numpy is required for Exercise 1. Install with: pip install numpy")
        pygame.quit()
        return 1

    screen: pygame.Surface = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    pygame.display.set_caption(WINDOW_TITLE)
    clock: pygame.time.Clock = pygame.time.Clock()
    font_lg: pygame.font.Font = pygame.font.SysFont(None, 28)
    font_sm: pygame.font.Font = pygame.font.SysFont(None, 20)

    tones: list[pygame.mixer.Sound] = build_tone_bank()
    for s in tones:
        s.set_volume(0.65)

    flash_t: list[int] = [0] * len(tones)
    last_played_count: int = 0

    running: bool = True
    while running:
        clock.tick(TARGET_FPS)

        # ---- Events -----------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # Stress test: play all eight at once.
                    for i, sfx in enumerate(tones):
                        ch: Optional[pygame.mixer.Channel] = sfx.play(fade_ms=TONE_FADE_MS)
                        if ch is not None:
                            flash_t[i] = FLASH_FRAMES
                    last_played_count = len(tones)
                else:
                    digit_keys: dict[int, int] = {
                        pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2, pygame.K_4: 3,
                        pygame.K_5: 4, pygame.K_6: 5, pygame.K_7: 6, pygame.K_8: 7,
                    }
                    if event.key in digit_keys:
                        idx: int = digit_keys[event.key]
                        ch_single: Optional[pygame.mixer.Channel] = tones[idx].play(fade_ms=TONE_FADE_MS)
                        if ch_single is not None:
                            flash_t[idx] = FLASH_FRAMES
                            last_played_count = 1

        # ---- Update -----------------------------------------------------
        for i in range(len(flash_t)):
            if flash_t[i] > 0:
                flash_t[i] -= 1

        busy_channels: int = sum(
            1
            for i in range(pygame.mixer.get_num_channels())
            if pygame.mixer.Channel(i).get_busy()
        )

        # ---- Render -----------------------------------------------------
        screen.fill(BG_COLOUR)

        # Swatches across the bottom.
        swatch_count: int = len(tones)
        swatch_w: int = WINDOW_W // (swatch_count + 1)
        swatch_h: int = 80
        swatch_y: int = WINDOW_H - swatch_h - 30
        for i in range(swatch_count):
            cx: int = (swatch_w * (i + 1)) - swatch_w // 2
            base_colour: tuple[int, int, int] = SWATCH_PALETTE[i]
            if flash_t[i] > 0:
                # Lighter while flashing.
                colour: tuple[int, int, int] = tuple(min(255, c + 60) for c in base_colour)  # type: ignore[assignment]
            else:
                colour = base_colour
            rect: pygame.Rect = pygame.Rect(cx - swatch_w // 2 + 6, swatch_y, swatch_w - 12, swatch_h)
            pygame.draw.rect(screen, colour, rect, border_radius=6)
            label: pygame.Surface = font_lg.render(str(i + 1), True, BG_COLOUR)
            screen.blit(label, label.get_rect(center=rect.center))
            freq_label: pygame.Surface = font_sm.render(
                f"{TONE_FREQUENCIES_HZ[i]:.0f} Hz", True, DIM_COLOUR
            )
            screen.blit(freq_label, freq_label.get_rect(midtop=(rect.centerx, rect.bottom + 6)))

        # HUD across the top.
        lines: list[tuple[str, tuple[int, int, int]]] = [
            (f"sample rate: {SAMPLE_RATE_HZ} Hz   channels: {CHANNELS}   buffer: {BUFFER_SAMPLES}",
             TEXT_COLOUR),
            (f"allocated channels: {pygame.mixer.get_num_channels()}    "
             f"busy: {busy_channels}    last play: {last_played_count}",
             TEXT_COLOUR),
            ("[1-8] play tone    [SPACE] play all    [ESC] quit", DIM_COLOUR),
        ]
        y: int = 14
        for text, colour_line in lines:
            surf: pygame.Surface = font_sm.render(text, True, colour_line)
            screen.blit(surf, (16, y))
            y += 24

        pygame.display.flip()

    pygame.quit()
    return 0


# ----- HINT (do not peek for 20 minutes) -----------------------------------
# If the tones sound clicky at the start and end, raise the
# envelope's attack_n and release_n values in synthesise_tone. The
# 5 ms / 25 ms defaults are conservative; some monitors need 10 ms.
#
# If SPACE produces audible clipping, lower the per-Sound volume from
# 0.65 to 0.35. The clipping is the whole point of the stress test -
# it shows you why the bus structure in Exercise 2 sets the master
# bus at ~0.6 rather than 1.0.
#
# If you want to hear the difference between sample rates, change
# SAMPLE_RATE_HZ to 22050 and rerun. The tones will sound noticeably
# duller because the harmonics above 11 kHz are gone.
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    sys.exit(main())
