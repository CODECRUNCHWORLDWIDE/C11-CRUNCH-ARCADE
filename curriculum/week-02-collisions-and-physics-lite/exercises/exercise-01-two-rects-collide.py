"""exercise-01-two-rects-collide.py

Goal
----
Two rectangles share a window. One is controlled by the player with
WASD. The other sits still in the middle. When the player rectangle
overlaps the static rectangle, the static rectangle turns red. When
the player rectangle is not overlapping, it returns to its original
Power-Up-Cyan colour.

Expected behaviour
------------------
- A 800x600 window with a dark-blue background.
- A 60x40 Coin-Pink rectangle the player drives with WASD at 280 px/s.
  Diagonals are normalised; the player rect cannot leave the window.
- A 120x80 Power-Up-Cyan rectangle parked at the centre of the window.
- When the two rectangles' edges overlap, the static one switches to
  a "hit" red. As soon as they no longer overlap, it switches back.
- The window closes cleanly on X / Cmd-Q / Escape.

What you learn
--------------
- The four-comparison AABB overlap test, by hand.
- How ``pygame.Rect.colliderect`` does the same thing in C.
- Pygame's half-open right/bottom semantics (touching edges do NOT
  count as overlap — try it and see).
- Storing logical position as a ``Vector2`` and the drawn ``Rect`` as
  a derived value, so float fractions don't get rounded away.

Estimated time
--------------
About 35 minutes if Week 1 went smoothly.

To complete
-----------
Fill in the ``TODO`` lines. Do not peek at the HINT block at the
bottom of this file until you've spent 15 minutes.

Run with::

    python exercise-01-two-rects-collide.py
"""

from __future__ import annotations

import pygame

# ----- Configuration --------------------------------------------------------

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_TITLE = "C11 Week 2 - Two Rects Collide"
TARGET_FPS = 60

BACKGROUND = (20, 20, 30)
COIN_PINK = (219, 39, 119)
POWER_CYAN = (6, 182, 212)
HIT_RED = (220, 38, 38)

PLAYER_W, PLAYER_H = 60, 40
STATIC_W, STATIC_H = 120, 80
SPEED_PX_PER_S = 280.0
MAX_DT = 1.0 / 30.0


def aabb_overlap(
    a_left: float,
    a_top: float,
    a_right: float,
    a_bottom: float,
    b_left: float,
    b_top: float,
    b_right: float,
    b_bottom: float,
) -> bool:
    """The four-comparison overlap test, by hand.

    Two AABBs overlap if and only if they overlap on BOTH X and Y axes.
    Touching-only-at-an-edge is not overlap; we use strict ``<`` to
    match Pygame's own ``colliderect`` semantics.
    """
    # TODO: return True if the two rectangles overlap. Hint: four
    #       comparisons combined with ``and``. See Lecture 1 §2.
    return False  # replace this stub


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    clock = pygame.time.Clock()

    # ----- Game state ------------------------------------------------------
    # Logical position as a float Vector2 (Week 1 lesson). We derive the
    # integer-pixel Rect we draw each frame from this position.
    player_pos = pygame.Vector2(WINDOW_WIDTH * 0.25, WINDOW_HEIGHT * 0.5)

    static_rect = pygame.Rect(0, 0, STATIC_W, STATIC_H)
    static_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)

    dt = 0.0
    running = True
    while running:
        # 1. Input -----------------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        keys = pygame.key.get_pressed()
        direction = pygame.Vector2(0, 0)
        if keys[pygame.K_d]:
            direction.x += 1
        if keys[pygame.K_a]:
            direction.x -= 1
        if keys[pygame.K_s]:
            direction.y += 1
        if keys[pygame.K_w]:
            direction.y -= 1
        if direction.length_squared() > 0:
            direction = direction.normalize()

        # 2. Update ----------------------------------------------------------
        player_pos += direction * SPEED_PX_PER_S * dt
        # Clamp the centre into the window.
        player_pos.x = max(PLAYER_W / 2, min(WINDOW_WIDTH - PLAYER_W / 2, player_pos.x))
        player_pos.y = max(PLAYER_H / 2, min(WINDOW_HEIGHT - PLAYER_H / 2, player_pos.y))

        # Build the drawn rect from the float centre.
        player_rect = pygame.Rect(0, 0, PLAYER_W, PLAYER_H)
        player_rect.center = (int(player_pos.x), int(player_pos.y))

        # TODO: call your ``aabb_overlap`` function above to determine
        #       whether the player and static rects overlap. Use the
        #       ``.left``, ``.top``, ``.right``, ``.bottom`` properties
        #       of each Rect.
        is_colliding = False  # replace with a call to aabb_overlap(...)

        # ----- Sanity check: compare to Pygame's built-in -----------------
        # If your implementation disagrees with Pygame's, one of them
        # is wrong. (Spoiler: it isn't Pygame.) Toggle this assert on
        # while you debug; remove it once your test agrees.
        # assert is_colliding == player_rect.colliderect(static_rect)

        static_colour = HIT_RED if is_colliding else POWER_CYAN

        # 3. Render ----------------------------------------------------------
        screen.fill(BACKGROUND)
        pygame.draw.rect(screen, static_colour, static_rect)
        pygame.draw.rect(screen, COIN_PINK, player_rect)
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
# aabb_overlap:
#     return (
#         a_left   < b_right  and
#         b_left   < a_right  and
#         a_top    < b_bottom and
#         b_top    < a_bottom
#     )
#
# Inside the loop:
#     is_colliding = aabb_overlap(
#         player_rect.left,  player_rect.top,
#         player_rect.right, player_rect.bottom,
#         static_rect.left,  static_rect.top,
#         static_rect.right, static_rect.bottom,
#     )
#
# ----------------------------------------------------------------------------
# WHY STRICT < AND NOT <=?
# ----------------------------------------------------------------------------
# Pygame Rects are half-open intervals: a Rect with x=10, width=20
# covers pixels 10..29 inclusive. Pixel 30 is NOT in the Rect. The
# overlap test must reflect that — if A.right == B.left, the two rects
# share no pixels, so they do not overlap.
#
# Try changing your ``<`` to ``<=`` and walk the player rect against
# the static rect from outside. With ``<=`` the static rect turns red
# while the player rect is one pixel away. That feels wrong because
# it is.
# ----------------------------------------------------------------------------
# WHY STORE POSITION AS A VECTOR2 INSTEAD OF JUST USING THE RECT?
# ----------------------------------------------------------------------------
# Pygame Rects store integer pixel coordinates. ``player_rect.x = x +
# vel.x * dt`` truncates ``vel.x * dt`` to an int. At 280 px/s and
# 60 fps, that fraction is ~4.67 — round-trip to int gives 4, losing
# 0.67 px/frame. Over 100 frames that's a 67-pixel drift compared to
# wall-clock-correct movement.
#
# Store the *logical* position as a float Vector2. Build the drawn
# Rect from it each frame by setting ``.center``. The Rect is a view;
# the Vector2 is the truth.
# ----------------------------------------------------------------------------
# WHAT TO DO ONCE THIS WORKS
# ----------------------------------------------------------------------------
# 1. Walk the player rect along the static rect's edge. The static
#    rect should NOT light up until the player rect is genuinely
#    overlapping by at least one pixel.
# 2. Try moving the player into a corner of the static rect. Notice
#    that the test fires the instant any overlap exists.
# 3. Uncomment the assert that compares your function to Pygame's.
#    Confirm they agree on every frame for at least one minute of
#    movement.
# 4. Optional: change ``static_rect`` to a tuple of 4 rects in the
#    four corners of the window. Detect overlap against any of them.
#    You'll find yourself wanting ``Rect.collidelist`` — meet your
#    new friend.
# ----------------------------------------------------------------------------
