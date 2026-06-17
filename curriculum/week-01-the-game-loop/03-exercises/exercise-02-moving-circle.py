"""exercise-02-moving-circle.py

Goal
----
A circle that crosses the screen at exactly 200 pixels per second,
regardless of what monitor it's running on. When it leaves the right
edge, it wraps to the left and starts over.

The whole point of this exercise is to **prove** that delta-time-scaled
movement works. Run the program on every machine you have access to.
Time the circle with a stopwatch on each. It should take the same
~4 seconds to cross an 800-px window on every one.

Expected behaviour
------------------
- An 800x600 window with a dark-blue background.
- A 16-px Coin-Pink circle moves rightward at 200 px/s.
- When the circle leaves the right edge, it reappears at the left.
- The window closes cleanly on X / Cmd-Q.
- The terminal prints the running fps and frame budget once per second
  so you can see whether you're hitting the 16.6 ms target.

What you learn
--------------
- How to get ``dt`` (delta time) from ``pygame.time.Clock``.
- Why position is a float, not an int.
- The pattern ``pos += speed * dt`` for kinematic motion.
- Clamping ``dt`` to avoid the "I tabbed out for 10 seconds" warp.
- Measuring frame budget with ``time.perf_counter``.

Estimated time
--------------
Around 30 minutes if you read Lecture 2 first. Closer to an hour if
you skipped Lecture 2 (please go back).

To complete
-----------
Fill in the ``TODO`` lines. Do not peek at the HINT until you've spent
15 minutes.

Run with::

    python exercise-02-moving-circle.py
"""

from __future__ import annotations

import time

import pygame

# ----- Configuration --------------------------------------------------------

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_TITLE = "C11 Week 1 - Moving Circle"
TARGET_FPS = 60

BACKGROUND = (20, 20, 30)
COIN_PINK = (219, 39, 119)

CIRCLE_RADIUS = 16
SPEED_PX_PER_S = 200.0      # pixels per second, NOT per frame
MAX_DT = 1.0 / 30.0         # clamp dt at ~33ms; see Lecture 2 §4


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    clock = pygame.time.Clock()

    # ----- Game state ------------------------------------------------------
    # Note: floats. At 200 px/s and 60 fps, each frame's increment is
    # 200 * (1/60) ~= 3.33 px. An ``int`` cannot hold the fractional
    # component, and the error accumulates.
    x = 0.0
    y = float(WINDOW_HEIGHT // 2)

    dt = 0.0
    fps_print_accumulator = 0.0
    frames_since_print = 0
    last_loop_ms = 0.0

    running = True
    while running:
        loop_start = time.perf_counter()

        # 1. Input -----------------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 2. Update ----------------------------------------------------------
        # TODO: advance ``x`` by ``SPEED_PX_PER_S * dt``.

        # TODO: when ``x`` exceeds ``WINDOW_WIDTH + CIRCLE_RADIUS``,
        #       wrap it to ``-CIRCLE_RADIUS`` so the circle re-enters
        #       from the left edge smoothly.

        # 3. Render ----------------------------------------------------------
        screen.fill(BACKGROUND)

        # TODO: draw a Coin-Pink circle at (x, y) with radius
        #       ``CIRCLE_RADIUS``. Cast x and y to ``int`` for drawing.

        pygame.display.flip()

        # 4. Tick + dt -------------------------------------------------------
        # ``clock.tick(60)`` returns ms since previous call.
        # Divide by 1000 -> seconds. Then clamp with MAX_DT.
        raw_dt = clock.tick(TARGET_FPS) / 1000.0
        dt = min(raw_dt, MAX_DT)

        # ----- Telemetry (so you can SEE the frame budget) -----------------
        last_loop_ms = (time.perf_counter() - loop_start) * 1000.0
        fps_print_accumulator += raw_dt
        frames_since_print += 1
        if fps_print_accumulator >= 1.0:
            avg_fps = frames_since_print / fps_print_accumulator
            print(
                f"fps={avg_fps:5.1f}  "
                f"last frame {last_loop_ms:5.2f} ms  "
                f"budget at 60 fps = 16.6 ms"
            )
            fps_print_accumulator = 0.0
            frames_since_print = 0

    pygame.quit()


if __name__ == "__main__":
    main()


# ----------------------------------------------------------------------------
# HINT (read only after 15+ minutes of effort)
# ----------------------------------------------------------------------------
#
# Update:
#     x += SPEED_PX_PER_S * dt
#     if x > WINDOW_WIDTH + CIRCLE_RADIUS:
#         x = -CIRCLE_RADIUS
#
# Render:
#     pygame.draw.circle(
#         screen,
#         COIN_PINK,
#         (int(x), int(y)),
#         CIRCLE_RADIUS,
#     )
#
# ----------------------------------------------------------------------------
# WHY THE WRAP IS AT WINDOW_WIDTH + CIRCLE_RADIUS, NOT WINDOW_WIDTH
# ----------------------------------------------------------------------------
# The circle's centre is at ``x``. The circle is visible from
# ``x - radius`` to ``x + radius``. We want the *whole* circle to leave
# the screen before we wrap it. So we wait until ``x > WINDOW_WIDTH +
# radius``, and then we put the circle at ``-radius`` so it slides in
# smoothly from the left, instead of teleporting on screen halfway.
#
# This is the kind of detail that separates "feels right" from "feels
# janky". Almost-right looks worse than obviously-wrong.
# ----------------------------------------------------------------------------
# WHAT IF YOUR FPS IS NOT 60?
# ----------------------------------------------------------------------------
# Read the fps print line. On a healthy machine on battery, expect
# 60.0 +/- 0.5. On a stressed machine you may see 30s or 50s. On a
# 144 Hz monitor with VSync, you might see ~144 if tick is misconfigured.
# The circle's *speed* should still feel the same — that's the whole
# point of dt. Verify it.
# ----------------------------------------------------------------------------
