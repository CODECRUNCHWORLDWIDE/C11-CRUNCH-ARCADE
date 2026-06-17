"""uv-playground.py

Goal
----
A CPU-side visualiser for the UV-coordinate transformations that every
fragment shader in this week's curriculum uses. The script renders a
512x512 window where each pixel's colour is the result of running a
tiny "shader-like" function on that pixel's UV coordinate.

Why we do this CPU-side
-----------------------
A fragment shader running on the GPU is essentially impossible to debug
with print statements; the closest you can do is write the intermediate
vec2 as a colour and squint at it. This script lets you put the same
math in a Python function, run it on the CPU, and `print()` whatever
you like. It also runs without a GPU, which matters if you are working
on a thin client or a Chromebook.

The trade-off is speed: a 512x512 CPU "shader" runs at maybe 5 frames
per second in pure Python. That is fine for understanding; not fine for
shipping. The point is the math, not the speed.

What you learn
--------------
- The UV coordinate system: (0,0) at top-left, (1,1) at bottom-right.
- Common UV transforms: centre, scale, polar, radial-distance.
- How a "fragment function" looks when written in Python: it takes
  uv (a 2-tuple of floats) and time (a float) and returns rgb (a
  3-tuple of floats in 0..1).
- The visual signature of each transform. After this exercise you can
  read a GLSL `length(UV - 0.5)` and know what it draws before running it.

Expected behaviour
------------------
The script opens a Pygame window. The window cycles through six
"effects" once every 4 seconds:
  1. UV as red-green.
  2. Centred UV (origin at middle).
  3. Radial distance from centre.
  4. Polar angle.
  5. Animated wave (sin of UV.y over time).
  6. Stripes (mod of UV.x times a frequency).

Each effect is a one-line function body. Press SPACE to step manually
between effects; press 1-6 to jump directly; press Q to quit.

To run
------
    pip install pygame
    python3 uv-playground.py

To complete
-----------
Read each effect's docstring, run the script, and verify the visual
matches the math. Then add a seventh effect of your own and observe.

The python3 -m py_compile check
-------------------------------
This file must compile cleanly with `python3 -m py_compile uv-playground.py`.
We use only the standard library plus pygame. No type-checker is required.

References
----------
- *The Book of Shaders*, chapter 4 *Running your shader*:
  https://thebookofshaders.com/04/
- *The Book of Shaders*, chapter 6 *Shapes*:
  https://thebookofshaders.com/06/
- Pygame docs, *pygame.surfarray*:
  https://www.pygame.org/docs/ref/surfarray.html
"""

from __future__ import annotations

import math
import sys
from typing import Callable, Tuple

import pygame


# A "fragment function" takes a uv (vec2-like, two floats in 0..1) and
# a time (float, seconds), and returns an rgb triple (three floats in 0..1).
FragmentFn = Callable[[Tuple[float, float], float], Tuple[float, float, float]]


# Window size. Larger = prettier; slower to render. 256 is a good speed
# compromise; 512 is the recommended quality setting.
WINDOW_SIZE: int = 256

# Pixel size on screen. Each rendered "fragment" is upscaled by this
# factor so a 256x256 render fills a 768x768 window.
PIXEL_SCALE: int = 3


# =====================================================================
# Effect 1: UV as red-green.
# =====================================================================
# This is the canonical "debug your UV" shader. Red = U; green = V.
# After running this once, you have a visceral feel for the coordinate
# system: top-left is black, top-right is red, bottom-left is green,
# bottom-right is yellow.
def effect_uv_as_rg(uv: Tuple[float, float], time: float) -> Tuple[float, float, float]:
    """Plot UV as red-green channels. Top-left=black, bottom-right=yellow."""
    u, v = uv
    return (u, v, 0.0)


# =====================================================================
# Effect 2: Centred UV.
# =====================================================================
# Shift the origin to the centre of the screen. The four quadrants are
# now distinguishable: top-left has u<0 and v<0, etc.
# We map -1..+1 to 0..1 for display by halving and adding 0.5.
def effect_centred_uv(uv: Tuple[float, float], time: float) -> Tuple[float, float, float]:
    """Plot centred UV. Origin is at the screen centre; corners are extreme."""
    u, v = uv
    cu: float = (u - 0.5) * 2.0  # -1..+1
    cv: float = (v - 0.5) * 2.0
    return (cu * 0.5 + 0.5, cv * 0.5 + 0.5, 0.0)


# =====================================================================
# Effect 3: Radial distance.
# =====================================================================
# Distance from the centre. 0 at centre, ~0.71 at corners.
# Multiplying by sqrt(2) brings the corners to 1.0 for a clean gradient.
def effect_radial_distance(uv: Tuple[float, float], time: float) -> Tuple[float, float, float]:
    """Plot the distance from screen-centre. Centre is black; corners are white."""
    u, v = uv
    du: float = u - 0.5
    dv: float = v - 0.5
    d: float = math.sqrt(du * du + dv * dv) * math.sqrt(2.0)
    return (d, d, d)


# =====================================================================
# Effect 4: Polar angle.
# =====================================================================
# The angle from the centre, normalised to 0..1.
# atan2(y, x) returns -pi..+pi; we shift to 0..2pi and divide by 2pi.
# Visually: a colour wheel where each angular slice has a distinct hue.
def effect_polar_angle(uv: Tuple[float, float], time: float) -> Tuple[float, float, float]:
    """Plot the polar angle from the screen centre as a colour wheel."""
    u, v = uv
    du: float = u - 0.5
    dv: float = v - 0.5
    if du == 0.0 and dv == 0.0:
        return (0.0, 0.0, 0.0)
    angle: float = math.atan2(dv, du)  # -pi..+pi
    norm: float = (angle + math.pi) / (2.0 * math.pi)  # 0..1
    # Convert angle to rgb via a simple HSV-like rotation.
    r: float = 0.5 + 0.5 * math.cos(angle)
    g: float = 0.5 + 0.5 * math.cos(angle + 2.0 * math.pi / 3.0)
    b: float = 0.5 + 0.5 * math.cos(angle + 4.0 * math.pi / 3.0)
    return (r, g, b)


# =====================================================================
# Effect 5: Animated wave (sin of UV.y over time).
# =====================================================================
# The same math as the screen-wave shader, run on the CPU. Each pixel's
# brightness is sin(uv.y * frequency + time * speed) mapped to 0..1.
# Watch the horizontal bands scroll vertically. This is exactly what
# exercise-05 does on the GPU, but here you can put print() in.
def effect_animated_wave(uv: Tuple[float, float], time: float) -> Tuple[float, float, float]:
    """Plot a sine wave in UV.y, animated over time. The shader-wave effect, on CPU."""
    u, v = uv
    frequency: float = 12.0
    speed: float = 2.0
    value: float = 0.5 + 0.5 * math.sin(v * frequency * 2.0 * math.pi + time * speed)
    return (value, value, value * 0.8)


# =====================================================================
# Effect 6: Stripes (mod of UV.x times a frequency).
# =====================================================================
# A square-wave pattern. Each fragment's brightness is 1 if the fractional
# part of uv.x * frequency is below 0.5; 0 otherwise. This is the basis of
# checkerboard, scan-line, and barcode-style patterns.
def effect_stripes(uv: Tuple[float, float], time: float) -> Tuple[float, float, float]:
    """Plot vertical stripes at a fixed frequency. The basis of scan-line effects."""
    u, _ = uv
    frequency: float = 16.0
    frac: float = (u * frequency) % 1.0
    value: float = 1.0 if frac < 0.5 else 0.0
    return (value, value, value)


# =====================================================================
# Effect registry and switching.
# =====================================================================

EFFECTS: list[Tuple[str, FragmentFn]] = [
    ("UV as red-green", effect_uv_as_rg),
    ("Centred UV",      effect_centred_uv),
    ("Radial distance", effect_radial_distance),
    ("Polar angle",     effect_polar_angle),
    ("Animated wave",   effect_animated_wave),
    ("Vertical stripes", effect_stripes),
]


# =====================================================================
# Renderer.
# =====================================================================
# render_effect runs the fragment function once per pixel in the
# WINDOW_SIZE x WINDOW_SIZE grid and writes the result into a Pygame
# surface. The result is then blit'd at PIXEL_SCALE to the display.
#
# Pure-Python double-loop. Slow (a few fps at 256x256). The point is
# clarity, not speed.

def render_effect(fragment_fn: FragmentFn, time: float, surface: pygame.Surface) -> None:
    """Run fragment_fn at every UV in the grid and write to surface."""
    width: int = surface.get_width()
    height: int = surface.get_height()
    pixels = pygame.surfarray.pixels3d(surface)
    inv_w: float = 1.0 / float(width)
    inv_h: float = 1.0 / float(height)

    for py in range(height):
        v: float = float(py) * inv_h
        for px in range(width):
            u: float = float(px) * inv_w
            rgb = fragment_fn((u, v), time)
            # Clamp to 0..1 and convert to 0..255.
            r: int = max(0, min(255, int(rgb[0] * 255.0)))
            g: int = max(0, min(255, int(rgb[1] * 255.0)))
            b: int = max(0, min(255, int(rgb[2] * 255.0)))
            pixels[px, py, 0] = r
            pixels[px, py, 1] = g
            pixels[px, py, 2] = b

    # `del pixels` releases the lock so we can blit.
    del pixels


# =====================================================================
# Main loop.
# =====================================================================

def main() -> int:
    pygame.init()
    screen: pygame.Surface = pygame.display.set_mode(
        (WINDOW_SIZE * PIXEL_SCALE, WINDOW_SIZE * PIXEL_SCALE + 40)
    )
    pygame.display.set_caption("UV playground - press 1..6 to switch, SPACE to step, Q to quit")
    clock: pygame.time.Clock = pygame.time.Clock()
    font: pygame.font.Font = pygame.font.SysFont("monospace", 18)

    # The "render surface" — the small image we paint pixel-by-pixel.
    # Blit'd at PIXEL_SCALE to the display each frame.
    render_surface: pygame.Surface = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE))

    current_effect_index: int = 0
    auto_cycle: bool = True
    auto_cycle_period_s: float = 4.0
    time_in_current_effect: float = 0.0

    start_time_ms: int = pygame.time.get_ticks()
    last_frame_ms: int = start_time_ms

    running: bool = True
    while running:
        now_ms: int = pygame.time.get_ticks()
        elapsed_s: float = (now_ms - start_time_ms) / 1000.0
        delta_s: float = (now_ms - last_frame_ms) / 1000.0
        last_frame_ms = now_ms

        time_in_current_effect += delta_s
        if auto_cycle and time_in_current_effect > auto_cycle_period_s:
            current_effect_index = (current_effect_index + 1) % len(EFFECTS)
            time_in_current_effect = 0.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    current_effect_index = (current_effect_index + 1) % len(EFFECTS)
                    time_in_current_effect = 0.0
                elif event.key == pygame.K_a:
                    auto_cycle = not auto_cycle
                elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3,
                                   pygame.K_4, pygame.K_5, pygame.K_6):
                    idx: int = event.key - pygame.K_1
                    if idx < len(EFFECTS):
                        current_effect_index = idx
                        time_in_current_effect = 0.0

        effect_name, fragment_fn = EFFECTS[current_effect_index]
        render_effect(fragment_fn, elapsed_s, render_surface)

        # Upscale the render surface to fill the window.
        scaled = pygame.transform.scale(
            render_surface,
            (WINDOW_SIZE * PIXEL_SCALE, WINDOW_SIZE * PIXEL_SCALE),
        )
        screen.fill((0, 0, 0))
        screen.blit(scaled, (0, 0))

        # Label and instructions.
        label = font.render(
            "[{}/{}] {}  (SPACE=next, A=auto={}, Q=quit)".format(
                current_effect_index + 1, len(EFFECTS), effect_name, "on" if auto_cycle else "off"
            ),
            True, (255, 255, 255),
        )
        screen.blit(label, (10, WINDOW_SIZE * PIXEL_SCALE + 8))

        pygame.display.flip()
        clock.tick(15)  # 15 fps cap — the renderer is too slow for higher.

    pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
