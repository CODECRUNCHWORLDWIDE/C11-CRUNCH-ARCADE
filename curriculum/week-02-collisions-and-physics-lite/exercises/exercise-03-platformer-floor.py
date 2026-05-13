"""exercise-03-platformer-floor.py

Goal
----
A controllable Coin-Pink square that walks left/right with the arrow
keys, jumps with SPACE, and lands on a Power-Up-Cyan floor. This is
the smallest meaningful platformer — three of the four pillars of
2D-platformer movement (move, jump, land) in 150 lines.

Expected behaviour
------------------
- A 800x600 window with a dark-blue background.
- A 32x32 Coin-Pink player square sits on a 800x40 floor near the
  bottom of the window.
- LEFT / RIGHT arrows move the player at 280 px/s.
- SPACE applies an instant upward velocity (jump). The jump only
  works when the player is touching the floor — no double-jumps.
- Gravity pulls the player back down. They land on the floor and
  the jump can fire again.
- The window closes cleanly on X / Cmd-Q / Escape.

What you learn
--------------
- The "is the player on the floor?" check — fundamental to every
  platformer ever.
- Impulse-style jumping: an instant velocity change, no ``dt``.
- The snap-back-and-flip pattern as an actual platformer landing.
- Why we set ``vel.y = 0`` (not reflect it) on a "land" event —
  landing is not a bounce.
- The platformer-floor variant of the AABB resolution code from
  Lecture 1 §6: when the smaller overlap is vertical, snap up.

Estimated time
--------------
45 minutes if Lecture 1 and Exercise 2 are fresh.

To complete
-----------
Fill in the ``TODO`` lines.

Run with::

    python exercise-03-platformer-floor.py
"""

from __future__ import annotations

import pygame

# ----- Configuration --------------------------------------------------------

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_TITLE = "C11 Week 2 - Platformer Floor"
TARGET_FPS = 60

BACKGROUND = (20, 20, 30)
COIN_PINK = (219, 39, 119)
POWER_CYAN = (6, 182, 212)

PLAYER_SIZE = 32
PLAYER_SPEED_PX_PER_S = 280.0
JUMP_IMPULSE_PX_PER_S = 520.0     # instant upward velocity on jump
GRAVITY_PX_PER_S2 = 1400.0        # higher than real gravity — see lecture
MAX_FALL_SPEED = 1800.0           # terminal velocity, prevents tunneling

FLOOR_HEIGHT = 40
MAX_DT = 1.0 / 30.0


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 22)

    # The floor: a static Rect spanning the bottom of the window.
    floor_rect = pygame.Rect(
        0,
        WINDOW_HEIGHT - FLOOR_HEIGHT,
        WINDOW_WIDTH,
        FLOOR_HEIGHT,
    )

    # Player state. Position is the top-left corner of the player's
    # AABB, stored as floats to survive sub-pixel motion.
    player_pos = pygame.Vector2(
        WINDOW_WIDTH * 0.5 - PLAYER_SIZE * 0.5,
        floor_rect.top - PLAYER_SIZE - 80,    # start a bit above the floor
    )
    player_vel = pygame.Vector2(0.0, 0.0)
    on_floor = False

    dt = 0.0
    running = True
    while running:
        # 1. Input -----------------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # Impulse jump: instant velocity change, no dt.
                    # Only allowed when standing on the floor.
                    # TODO: if ``on_floor`` is True, set
                    #       ``player_vel.y = -JUMP_IMPULSE_PX_PER_S``.
                    #       Remember Pygame's y-down convention: up
                    #       is negative.
                    pass

        keys = pygame.key.get_pressed()
        horizontal = 0.0
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            horizontal += 1.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            horizontal -= 1.0
        player_vel.x = horizontal * PLAYER_SPEED_PX_PER_S

        # 2. Update ----------------------------------------------------------
        # Apply gravity.
        # TODO: add ``GRAVITY_PX_PER_S2 * dt`` to ``player_vel.y``.

        # Clamp fall speed to terminal velocity. Prevents tunneling
        # through the floor if the player falls long enough.
        if player_vel.y > MAX_FALL_SPEED:
            player_vel.y = MAX_FALL_SPEED

        # Move horizontally first, then vertically. Resolving one
        # axis at a time is the simplest way to get a stable
        # platformer floor — covered in Lecture 1 §6.
        player_pos.x += player_vel.x * dt
        # Clamp X to the window edges.
        player_pos.x = max(
            0.0,
            min(WINDOW_WIDTH - PLAYER_SIZE, player_pos.x),
        )

        player_pos.y += player_vel.y * dt

        # Floor collision: the only collision in this exercise.
        # Build the player's AABB from the float position.
        player_rect = pygame.Rect(
            int(player_pos.x),
            int(player_pos.y),
            PLAYER_SIZE,
            PLAYER_SIZE,
        )

        on_floor = False  # reset each frame; the check below re-sets it.
        if player_rect.colliderect(floor_rect):
            # Vertical-only landing: snap the player's bottom edge
            # to the floor's top edge, zero out vertical velocity.
            # We do NOT reflect — a player landing is not a bounce.
            # TODO: set ``player_pos.y = floor_rect.top - PLAYER_SIZE``.
            # TODO: set ``player_vel.y = 0.0``.
            # TODO: set ``on_floor = True``.
            pass

        # 3. Render ----------------------------------------------------------
        screen.fill(BACKGROUND)
        pygame.draw.rect(screen, POWER_CYAN, floor_rect)

        # Re-build the rect for drawing after the floor snap.
        player_rect = pygame.Rect(
            int(player_pos.x),
            int(player_pos.y),
            PLAYER_SIZE,
            PLAYER_SIZE,
        )
        pygame.draw.rect(screen, COIN_PINK, player_rect)

        # HUD
        hud_lines = [
            f"vel = ({player_vel.x:+6.1f}, {player_vel.y:+6.1f})  on_floor={on_floor}",
            "LEFT/RIGHT walk   SPACE jump   ESC quit",
        ]
        for i, line in enumerate(hud_lines):
            surface = font.render(line, True, (220, 220, 220))
            screen.blit(surface, (10, 10 + i * 20))

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
# Jump (inside KEYDOWN SPACE):
#     if on_floor:
#         player_vel.y = -JUMP_IMPULSE_PX_PER_S
#
# Gravity (in Update, before moving):
#     player_vel.y += GRAVITY_PX_PER_S2 * dt
#
# Floor landing:
#     player_pos.y = floor_rect.top - PLAYER_SIZE
#     player_vel.y = 0.0
#     on_floor = True
#
# ----------------------------------------------------------------------------
# WHY NOT REFLECT VELOCITY ON LANDING?
# ----------------------------------------------------------------------------
# In Exercise 2, we reflected ``vel.y`` on floor contact because we
# wanted a bouncing ball. Here we want a *standing* player. A
# platformer character that bounces off the floor is a bouncing
# ball, not a character. We set the vertical velocity to zero —
# the equivalent of restitution=0.
#
# If you ever want a "bouncy" platformer character (Yoshi's Story,
# Kirby's Dream Land), it's the same code with a restitution < 1.
# But the default is restitution=0 = clean stop.
# ----------------------------------------------------------------------------
# WHY MOVE X AND Y SEPARATELY?
# ----------------------------------------------------------------------------
# When the player walks into a wall while jumping, you want them to
# slide up the wall, not stop entirely. Moving the axes separately
# and resolving them separately gives that behaviour for free:
#
#     pos.x += vel.x * dt
#     resolve_x_collisions()
#     pos.y += vel.y * dt
#     resolve_y_collisions()
#
# With a single floor and no walls, this exercise doesn't show the
# benefit, but the pattern is what you'll extend to a real tilemap
# in Week 4. Get used to it now.
# ----------------------------------------------------------------------------
# WHY IS GRAVITY HERE 1400 INSTEAD OF 800?
# ----------------------------------------------------------------------------
# Compare to Exercise 2's bouncing ball at gravity=800. The platformer
# character feels much better at higher gravity — about 1400 px/s^2
# in our 600-px-tall window. Why? Because a player wants to feel
# *responsive*: a long, floaty jump arc reads as "loose controls,"
# while a fast, snappy arc reads as "tight controls."
#
# This is part of the reason real-physics Mario would feel terrible:
# Mario's apparent gravity is roughly 2x Earth's when scaled. The
# right value is whatever feels right when playtested. Tune it.
# ----------------------------------------------------------------------------
# WHAT TO DO ONCE THIS WORKS
# ----------------------------------------------------------------------------
# 1. Raise JUMP_IMPULSE to 720. The player feels light. Lower it to
#    300. The player can barely clear a 30-px box.
# 2. Lower GRAVITY to 600. The player feels floaty. Raise it to
#    2200. The player feels heavy and snappy.
# 3. Add a second floor at y=400, 200 px wide, centred. The player
#    should be able to jump onto it. (Hint: walk through Lecture 1
#    §6's resolution code — you'll need the smaller-overlap-axis
#    branch when the player walks INTO the platform from the side.)
# 4. Optional: add a "coyote time" of 0.1 s — for 100 ms after
#    walking off a ledge, the player can still jump. This is one
#    of the most-loved game-feel hacks in 2D platforming history.
# ----------------------------------------------------------------------------
