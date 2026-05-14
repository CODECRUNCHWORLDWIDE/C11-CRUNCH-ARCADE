"""exercise-03-spatial-attenuation-and-panning.py

Goal
----
Place three SFX emitters in 2D space and a movable "listener" (the
player). Walk around the field and observe distance attenuation
(volume falls off with distance) and stereo panning (sounds shift
left/right based on horizontal offset from the listener).

Press E to fire the emitter the listener is closest to. Press 1, 2,
or 3 to fire a specific emitter. Press SPACE to fire all three.
Press R to reset the listener to centre. WASD moves the listener.
ESC quits.

What you learn
--------------
- The distance_attenuation curve: linear from min_distance to
  max_distance, clamped at the ends.
- The horizontal_pan curve: linear from -pan_distance to
  +pan_distance, producing (left, right) volume pair.
- The two distinct API calls: Sound.set_volume(scalar) for the bus
  multiplier, and Channel.set_volume(left, right) for the pan.
- The early-out optimisation: if attenuation is zero, skip the play
  entirely.

Expected behaviour
------------------
- A 900x600 window with three coloured emitter squares fixed on the
  field and a movable cross-hair "listener" (the player).
- Each emitter has a faint ring drawn at its min_distance and
  max_distance for visual reference.
- Firing an emitter from far away produces a quiet, panned tone.
- Firing the same emitter from on top produces a loud centred tone.
- The HUD shows the most recent (volume, left_pan, right_pan) values.

To complete
-----------
The exercise is COMPLETE as shipped. Walk around, fire emitters,
listen. The HINT block suggests variations.

Run with::

    python exercise-03-spatial-attenuation-and-panning.py

Requires numpy::

    pip install numpy
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass
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


# Window and world.
WINDOW_W: int = 900
WINDOW_H: int = 600
TARGET_FPS: int = 60
WINDOW_TITLE: str = "C11 Week 8 - Exercise 3 - Spatial attenuation and panning"

PLAYER_SPEED: float = 240.0    # px/sec
PLAYER_SIZE: int = 18

PAN_DISTANCE: float = 350.0
MIN_DISTANCE: float = 60.0
MAX_DISTANCE: float = 420.0


# ----- Visual configuration -----------------------------------------------

BG_COLOUR: tuple[int, int, int] = (24, 24, 32)
TEXT_COLOUR: tuple[int, int, int] = (240, 240, 240)
DIM_COLOUR: tuple[int, int, int] = (140, 140, 150)
PLAYER_COLOUR: tuple[int, int, int] = (236, 72, 153)

EMITTER_PALETTE: tuple[tuple[int, int, int], ...] = (
    (250, 204, 21),    # yellow
    (132, 204, 22),    # green
    (96, 165, 250),    # blue
)

# ----- Data ----------------------------------------------------------------


@dataclass
class Emitter:
    name: str
    colour: tuple[int, int, int]
    x: float
    y: float
    frequency_hz: float


# ----- Spatial helpers (the lecture's distance + pan functions) -----------


def distance_attenuation(
    listener_x: float, listener_y: float,
    source_x: float, source_y: float,
    min_distance: float = MIN_DISTANCE,
    max_distance: float = MAX_DISTANCE,
) -> float:
    """Return a volume scalar in [0, 1] based on listener-to-source distance."""
    dx: float = source_x - listener_x
    dy: float = source_y - listener_y
    d: float = math.sqrt(dx * dx + dy * dy)
    if d <= min_distance:
        return 1.0
    if d >= max_distance:
        return 0.0
    return 1.0 - (d - min_distance) / (max_distance - min_distance)


def horizontal_pan(
    listener_x: float, source_x: float, pan_distance: float = PAN_DISTANCE,
) -> tuple[float, float]:
    """Return (left, right) volume scalars in [0, 1] from horizontal offset."""
    dx: float = source_x - listener_x
    p: float = max(-1.0, min(1.0, dx / pan_distance))
    left: float = (1.0 - p) * 0.5
    right: float = (1.0 + p) * 0.5
    return left, right


def play_spatial(
    sound: pygame.mixer.Sound,
    listener_x: float, listener_y: float,
    source_x: float, source_y: float,
    bus_volume: float = 1.0,
) -> tuple[Optional[pygame.mixer.Channel], float, float, float]:
    """Play sound at world position. Returns (channel, attenuation, left, right)."""
    att: float = distance_attenuation(listener_x, listener_y, source_x, source_y)
    if att <= 0.0:
        return None, 0.0, 0.0, 0.0
    left, right = horizontal_pan(listener_x, source_x)
    sound.set_volume(bus_volume * att)
    ch: Optional[pygame.mixer.Channel] = sound.play()
    if ch is not None:
        ch.set_volume(left, right)
    return ch, att, left, right


# ----- Tone synthesis -----------------------------------------------------


def synthesise_tone(frequency_hz: float, duration_s: float = 0.40, amplitude: float = 0.55) -> pygame.mixer.Sound:
    if not NUMPY_OK:
        raise RuntimeError("numpy required - pip install numpy")
    n: int = int(SAMPLE_RATE_HZ * duration_s)
    t: "np.ndarray" = np.linspace(0.0, duration_s, n, endpoint=False)
    wave: "np.ndarray" = np.sin(2.0 * math.pi * frequency_hz * t)
    attack_n: int = int(SAMPLE_RATE_HZ * 0.008)
    release_n: int = int(SAMPLE_RATE_HZ * 0.040)
    env: "np.ndarray" = np.ones(n, dtype=np.float32)
    env[:attack_n] = np.linspace(0.0, 1.0, attack_n)
    env[-release_n:] = np.linspace(1.0, 0.0, release_n)
    shaped: "np.ndarray" = wave * env * amplitude
    mono: "np.ndarray" = (shaped * 32767).astype(np.int16)
    stereo: "np.ndarray" = np.column_stack((mono, mono))
    return pygame.sndarray.make_sound(stereo)


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
        print("numpy is required for Exercise 3. Install with: pip install numpy")
        pygame.quit()
        return 1

    screen: pygame.Surface = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    pygame.display.set_caption(WINDOW_TITLE)
    clock: pygame.time.Clock = pygame.time.Clock()
    font_lg: pygame.font.Font = pygame.font.SysFont(None, 26)
    font_sm: pygame.font.Font = pygame.font.SysFont(None, 20)

    emitters: list[Emitter] = [
        Emitter("yellow", EMITTER_PALETTE[0], 180.0, 200.0, 660.0),
        Emitter("green",  EMITTER_PALETTE[1], 720.0, 180.0, 440.0),
        Emitter("blue",   EMITTER_PALETTE[2], 450.0, 480.0, 330.0),
    ]
    tones: list[pygame.mixer.Sound] = [
        synthesise_tone(e.frequency_hz) for e in emitters
    ]

    # Bus multiplier representing an "sfx bus at 1.0 with master 0.8".
    bus_volume: float = 0.80

    player_x: float = WINDOW_W / 2.0
    player_y: float = WINDOW_H / 2.0
    last_text: str = "(walk around and press 1/2/3, E, or SPACE)"

    running: bool = True
    while running:
        dt: float = clock.tick(TARGET_FPS) / 1000.0

        # ---- Events -----------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    player_x = WINDOW_W / 2.0
                    player_y = WINDOW_H / 2.0
                    last_text = "listener reset"
                elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                    idx: int = {pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2}[event.key]
                    e_target: Emitter = emitters[idx]
                    _, att, left, right = play_spatial(
                        tones[idx], player_x, player_y, e_target.x, e_target.y, bus_volume
                    )
                    last_text = (
                        f"emit {e_target.name}: att={att:.2f}  "
                        f"left={left:.2f}  right={right:.2f}"
                    )
                elif event.key == pygame.K_e:
                    # Fire closest.
                    nearest_i: int = 0
                    nearest_d: float = 1e9
                    for i, em_iter in enumerate(emitters):
                        dx: float = em_iter.x - player_x
                        dy: float = em_iter.y - player_y
                        d: float = math.sqrt(dx * dx + dy * dy)
                        if d < nearest_d:
                            nearest_d = d
                            nearest_i = i
                    e_near: Emitter = emitters[nearest_i]
                    _, att2, l2, r2 = play_spatial(
                        tones[nearest_i], player_x, player_y, e_near.x, e_near.y, bus_volume
                    )
                    last_text = (
                        f"emit nearest ({e_near.name}): att={att2:.2f}  "
                        f"left={l2:.2f}  right={r2:.2f}"
                    )
                elif event.key == pygame.K_SPACE:
                    for i, em_each in enumerate(emitters):
                        play_spatial(
                            tones[i], player_x, player_y, em_each.x, em_each.y, bus_volume
                        )
                    last_text = "fired all three emitters"

        # ---- Movement ---------------------------------------------------
        keys = pygame.key.get_pressed()
        vx: float = 0.0
        vy: float = 0.0
        if keys[pygame.K_a]:
            vx -= 1.0
        if keys[pygame.K_d]:
            vx += 1.0
        if keys[pygame.K_w]:
            vy -= 1.0
        if keys[pygame.K_s]:
            vy += 1.0
        norm: float = math.sqrt(vx * vx + vy * vy)
        if norm > 0.0:
            vx /= norm
            vy /= norm
        player_x += vx * PLAYER_SPEED * dt
        player_y += vy * PLAYER_SPEED * dt
        half: float = PLAYER_SIZE / 2.0
        if player_x < half:
            player_x = half
        if player_x > WINDOW_W - half:
            player_x = WINDOW_W - half
        if player_y < half:
            player_y = half
        if player_y > WINDOW_H - half:
            player_y = WINDOW_H - half

        # ---- Render -----------------------------------------------------
        screen.fill(BG_COLOUR)

        # Emitter rings and squares.
        for em_render in emitters:
            cx: int = int(em_render.x)
            cy: int = int(em_render.y)
            pygame.draw.circle(screen, (60, 60, 70), (cx, cy), int(MAX_DISTANCE), 1)
            pygame.draw.circle(screen, (90, 90, 100), (cx, cy), int(MIN_DISTANCE), 1)
            rect_em: pygame.Rect = pygame.Rect(cx - 12, cy - 12, 24, 24)
            pygame.draw.rect(screen, em_render.colour, rect_em, border_radius=4)
            label_em: pygame.Surface = font_sm.render(em_render.name, True, TEXT_COLOUR)
            screen.blit(label_em, label_em.get_rect(midtop=(cx, cy + 16)))

        # Player.
        prect: pygame.Rect = pygame.Rect(
            int(player_x - PLAYER_SIZE / 2), int(player_y - PLAYER_SIZE / 2),
            PLAYER_SIZE, PLAYER_SIZE,
        )
        pygame.draw.rect(screen, PLAYER_COLOUR, prect, border_radius=3)

        # Live attenuation table for each emitter.
        table_y: int = 10
        title: pygame.Surface = font_lg.render("LIVE ATTENUATION + PAN", True, TEXT_COLOUR)
        screen.blit(title, (12, table_y))
        table_y += 30
        for em_table in emitters:
            att_now: float = distance_attenuation(player_x, player_y, em_table.x, em_table.y)
            l_now, r_now = horizontal_pan(player_x, em_table.x)
            line: pygame.Surface = font_sm.render(
                f"{em_table.name:>6}: att={att_now:5.2f}  L={l_now:5.2f}  R={r_now:5.2f}",
                True, em_table.colour,
            )
            screen.blit(line, (12, table_y))
            table_y += 22

        # Status and controls.
        controls_y: int = WINDOW_H - 60
        ctl: pygame.Surface = font_sm.render(
            "[WASD] move  [1/2/3] fire  [E] fire nearest  [SPACE] all  [R] reset  [ESC] quit",
            True, DIM_COLOUR,
        )
        screen.blit(ctl, (12, controls_y))
        last: pygame.Surface = font_sm.render(last_text, True, TEXT_COLOUR)
        screen.blit(last, (12, controls_y + 24))

        pygame.display.flip()

    pygame.quit()
    return 0


# ----- HINT (do not peek for 20 minutes) -----------------------------------
# If sounds are always centred, you forgot to call
# Channel.set_volume(left, right) after Sound.set_volume(scalar).
# The Sound's volume is a SINGLE scalar; the two-arg form for stereo
# pan lives only on the Channel.
#
# If sounds fade out too quickly when you walk a short distance, the
# MAX_DISTANCE is too small for the window. Bump it to 500-600 px.
#
# If you cannot hear the pan effect at all, your laptop speakers are
# probably summing left and right to mono. Use headphones. This is
# the bug the README's "Prerequisites" section warned you about.
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    sys.exit(main())
