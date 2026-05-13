"""exercise-03-keyboard-input.py

Goal
----
The circle from Exercise 2, but the player controls it with WASD.
Movement must:

- Use ``pygame.key.get_pressed`` (the "held" pattern), not ``KEYDOWN``.
- Normalise diagonal movement so the player doesn't move 1.41x faster
  on a diagonal than on a cardinal direction.
- Clamp the circle's centre to the window edges so it can't leave
  the screen.
- Still respect delta time. The circle should feel the same on every
  machine.

Expected behaviour
------------------
- A circle that moves at ``SPEED_PX_PER_S`` pixels per second under
  WASD control.
- Holding two adjacent keys (e.g. W + D) moves the circle diagonally
  at the same speed as one key alone, not 1.41x faster.
- The circle stops at the window edge instead of disappearing off it.
- The window closes cleanly on X / Cmd-Q, or when the player presses
  Escape.

What you learn
--------------
- The two ways Pygame reads input: events (``KEYDOWN`` / ``KEYUP``) vs
  polled state (``key.get_pressed``).
- Why ``KEYDOWN`` is wrong for movement.
- ``pygame.Vector2`` for cleaner vector math.
- Normalising a movement vector so diagonals are correct.
- The ``length_squared() > 0`` idiom to avoid normalising a zero vector.
- Clamping a position to a bounding rectangle.

Estimated time
--------------
35 minutes if Exercise 2 went smoothly.

To complete
-----------
Fill in the ``TODO`` lines.

Run with::

    python exercise-03-keyboard-input.py
"""

from __future__ import annotations

import pygame

# ----- Configuration --------------------------------------------------------

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_TITLE = "C11 Week 1 - WASD Movement"
TARGET_FPS = 60

BACKGROUND = (20, 20, 30)
COIN_PINK = (219, 39, 119)

CIRCLE_RADIUS = 16
SPEED_PX_PER_S = 280.0
MAX_DT = 1.0 / 30.0


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    clock = pygame.time.Clock()

    # Position starts in the middle. Vector2 holds floats internally,
    # which is what we want.
    pos = pygame.Vector2(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)

    dt = 0.0
    running = True
    while running:
        # 1. Input -----------------------------------------------------------
        # One-shot events: window close, Escape to quit.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        # Held-state input: WASD for movement.
        keys = pygame.key.get_pressed()

        # TODO: build a ``direction`` Vector2 starting at (0, 0).
        #       Add +1 to direction.x when K_d is held.
        #       Subtract 1 from direction.x when K_a is held.
        #       Add +1 to direction.y when K_s is held (screen y grows down).
        #       Subtract 1 from direction.y when K_w is held.
        direction = pygame.Vector2(0, 0)

        # TODO: if direction has non-zero length, normalise it so
        #       diagonal movement is the same speed as cardinal.
        #       Use ``direction.length_squared() > 0`` as the guard so
        #       you don't normalise a zero vector (which raises).

        # 2. Update ----------------------------------------------------------
        # TODO: advance ``pos`` by ``direction * SPEED_PX_PER_S * dt``.

        # TODO: clamp pos.x to [CIRCLE_RADIUS, WINDOW_WIDTH - CIRCLE_RADIUS]
        #       and pos.y to [CIRCLE_RADIUS, WINDOW_HEIGHT - CIRCLE_RADIUS]
        #       so the circle cannot leave the window.

        # 3. Render ----------------------------------------------------------
        screen.fill(BACKGROUND)
        pygame.draw.circle(
            screen,
            COIN_PINK,
            (int(pos.x), int(pos.y)),
            CIRCLE_RADIUS,
        )
        pygame.display.flip()

        # 4. Tick + dt -------------------------------------------------------
        dt = min(clock.tick(TARGET_FPS) / 1000.0, MAX_DT)

    pygame.quit()


if __name__ == "__main__":
    main()


# ----------------------------------------------------------------------------
# HINT (read only after 15+ minutes of effort)
# ----------------------------------------------------------------------------
#
# Build the direction:
#     direction = pygame.Vector2(0, 0)
#     if keys[pygame.K_d]: direction.x += 1
#     if keys[pygame.K_a]: direction.x -= 1
#     if keys[pygame.K_s]: direction.y += 1
#     if keys[pygame.K_w]: direction.y -= 1
#     if direction.length_squared() > 0:
#         direction = direction.normalize()
#
# Update:
#     pos += direction * SPEED_PX_PER_S * dt
#     pos.x = max(CIRCLE_RADIUS, min(WINDOW_WIDTH  - CIRCLE_RADIUS, pos.x))
#     pos.y = max(CIRCLE_RADIUS, min(WINDOW_HEIGHT - CIRCLE_RADIUS, pos.y))
#
# ----------------------------------------------------------------------------
# WHY NOT USE KEYDOWN FOR MOVEMENT?
# ----------------------------------------------------------------------------
# ``KEYDOWN`` fires once per physical key press. If you wrote:
#
#     if event.type == pygame.KEYDOWN and event.key == pygame.K_d:
#         pos.x += SPEED_PX_PER_S * dt
#
# ...the circle would jump one tiny step when the player tapped D, then
# stop. The player would have to tap D 60 times a second to keep it
# moving — and the OS key-repeat delay would make even that uneven.
#
# Use ``KEYDOWN`` for things that happen once per press: firing a
# bullet, opening a menu, jumping. Use ``key.get_pressed`` for things
# that happen continuously while held: movement, charging a weapon.
# ----------------------------------------------------------------------------
# WHY ``length_squared() > 0`` AND NOT ``length() > 0``?
# ----------------------------------------------------------------------------
# Both work. ``length_squared`` avoids the square root, which is
# (slightly) faster. More importantly: comparing squared lengths is a
# habit you'll want when we start doing collisions in Week 2 — comparing
# squared distances avoids a ``sqrt`` per pair, and that adds up when
# there are 50 enemies.
# ----------------------------------------------------------------------------
