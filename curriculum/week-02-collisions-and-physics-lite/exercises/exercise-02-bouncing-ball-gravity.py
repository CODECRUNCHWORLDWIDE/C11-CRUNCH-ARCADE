"""exercise-02-bouncing-ball-gravity.py

Goal
----
A circle that falls under gravity, bounces on a floor, and comes to
rest after a few seconds. The bounce loses energy each contact
(restitution < 1), and a "rest threshold" prevents the won't-settle
bug where floating-point noise makes the ball forever-twitch on the
floor.

Expected behaviour
------------------
- A 800x600 window with a dark-blue background.
- A 16-px Coin-Pink ball appears near the top, with a small initial
  rightward velocity.
- The ball accelerates downward under gravity (~800 px/s^2).
- When the ball hits the floor (bottom of the window), it reflects
  vertically with a restitution coefficient of 0.75.
- When the ball hits the left or right wall, it reflects horizontally
  with the same restitution.
- After about 3-5 seconds the ball comes to rest on the floor and
  stops jittering.
- Press R to re-launch the ball from a random position with a fresh
  velocity. Press SPACE to toggle gravity on/off (off makes the ball
  a Week-1 bouncer in zero-g).
- The window closes cleanly on X / Cmd-Q / Escape.

What you learn
--------------
- Semi-implicit Euler integration: update velocity first, then
  position. One line of difference from forward Euler, strictly
  better for gravity.
- Gravity as a constant downward acceleration.
- Reflection on bounce: ``vel.y = -vel.y * RESTITUTION``.
- The rest-threshold fix for the won't-settle bug.
- One-shot key events vs polled key state, side by side.

Estimated time
--------------
40 minutes if Lecture 2 is fresh.

To complete
-----------
Fill in the ``TODO`` lines.

Run with::

    python exercise-02-bouncing-ball-gravity.py
"""

from __future__ import annotations

import random

import pygame

# ----- Configuration --------------------------------------------------------

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_TITLE = "C11 Week 2 - Bouncing Ball (Gravity Edition)"
TARGET_FPS = 60

BACKGROUND = (20, 20, 30)
COIN_PINK = (219, 39, 119)
POWER_CYAN = (6, 182, 212)

BALL_RADIUS = 16
GRAVITY_PX_PER_S2 = 800.0      # downward acceleration
RESTITUTION = 0.75             # 1.0 = perfect bounce; 0.0 = stick
REST_THRESHOLD = 30.0          # below this |vel|, snap to zero on bounce
MAX_DT = 1.0 / 30.0


def random_launch_velocity() -> pygame.Vector2:
    """A small rightward-or-leftward initial velocity, not pure-vertical."""
    vx = random.uniform(-200.0, 200.0)
    # Avoid near-zero horizontal velocity for visual interest.
    if abs(vx) < 60.0:
        vx = 60.0 if vx >= 0.0 else -60.0
    return pygame.Vector2(vx, 0.0)


def random_launch_position() -> pygame.Vector2:
    """Somewhere in the top quarter of the window."""
    return pygame.Vector2(
        random.uniform(BALL_RADIUS, WINDOW_WIDTH - BALL_RADIUS),
        random.uniform(BALL_RADIUS, WINDOW_HEIGHT * 0.25),
    )


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 22)

    pos = random_launch_position()
    vel = random_launch_velocity()
    gravity_on = True

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
                elif event.key == pygame.K_r:
                    # Re-launch from a fresh position and velocity.
                    pos = random_launch_position()
                    vel = random_launch_velocity()
                elif event.key == pygame.K_SPACE:
                    gravity_on = not gravity_on

        # 2. Update ----------------------------------------------------------
        # Build the acceleration vector for this frame.
        acc = pygame.Vector2(0.0, GRAVITY_PX_PER_S2 if gravity_on else 0.0)

        # TODO: semi-implicit Euler step.
        #   1. Add ``acc * dt`` to ``vel`` (velocity update FIRST).
        #   2. Add ``vel * dt`` to ``pos`` (position uses the new velocity).

        # ----- Floor bounce -------------------------------------------------
        if pos.y + BALL_RADIUS > WINDOW_HEIGHT:
            # Snap-back-and-flip pattern from Lecture 1 §6.
            pos.y = WINDOW_HEIGHT - BALL_RADIUS
            # TODO: reflect ``vel.y`` and multiply by ``RESTITUTION``.
            #       Hint: ``vel.y = -vel.y * RESTITUTION``.

            # TODO: apply the rest-threshold fix.
            #   If ``abs(vel.y) < REST_THRESHOLD``, set ``vel.y = 0.0``.

        # ----- Ceiling bounce (so a zero-g toggle doesn't escape) ----------
        if pos.y - BALL_RADIUS < 0:
            pos.y = BALL_RADIUS
            vel.y = -vel.y * RESTITUTION

        # ----- Wall bounces -------------------------------------------------
        if pos.x - BALL_RADIUS < 0:
            pos.x = BALL_RADIUS
            vel.x = -vel.x * RESTITUTION
            if abs(vel.x) < REST_THRESHOLD:
                vel.x = 0.0
        if pos.x + BALL_RADIUS > WINDOW_WIDTH:
            pos.x = WINDOW_WIDTH - BALL_RADIUS
            vel.x = -vel.x * RESTITUTION
            if abs(vel.x) < REST_THRESHOLD:
                vel.x = 0.0

        # 3. Render ----------------------------------------------------------
        screen.fill(BACKGROUND)
        # Floor indicator.
        pygame.draw.line(
            screen,
            POWER_CYAN,
            (0, WINDOW_HEIGHT - 1),
            (WINDOW_WIDTH, WINDOW_HEIGHT - 1),
            2,
        )
        pygame.draw.circle(
            screen,
            COIN_PINK,
            (int(pos.x), int(pos.y)),
            BALL_RADIUS,
        )

        # HUD: print the live physics state so you can see the rest
        # threshold fire. This is your physics debugger for the week.
        hud_lines = [
            f"vel = ({vel.x:+7.1f}, {vel.y:+7.1f}) px/s",
            f"gravity: {'ON' if gravity_on else 'OFF'}   restitution: {RESTITUTION}",
            "R re-launch   SPACE toggle gravity   ESC quit",
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
# Semi-implicit Euler:
#     vel += acc * dt
#     pos += vel * dt
#
# Floor bounce:
#     vel.y = -vel.y * RESTITUTION
#     if abs(vel.y) < REST_THRESHOLD:
#         vel.y = 0.0
#
# ----------------------------------------------------------------------------
# WHY SEMI-IMPLICIT EULER AND NOT FORWARD EULER?
# ----------------------------------------------------------------------------
# Forward Euler:
#     pos += vel * dt           # uses OLD velocity
#     vel += acc * dt           # then updates velocity
#
# Semi-implicit Euler:
#     vel += acc * dt           # update velocity FIRST
#     pos += vel * dt           # use NEW velocity
#
# Both produce a ball that falls and bounces, but semi-implicit
# conserves energy much better — its total kinetic + potential
# energy doesn't drift over time the way forward Euler's does.
# For our restitution=0.75 ball that's not visually different over
# 30 seconds. For a frictionless oscillating system (a pendulum, a
# spring) the difference is dramatic: forward Euler explodes,
# semi-implicit settles.
#
# It's one line of difference. Use semi-implicit. Always.
# ----------------------------------------------------------------------------
# WHY THE REST THRESHOLD?
# ----------------------------------------------------------------------------
# Once the ball loses enough energy, its vertical velocity after the
# bounce is, say, 8 px/s upward. Next frame it falls back, hits the
# floor at ~21 px/s downward (gravity added). Reflects to ~16 px/s
# upward. And so on. Each bounce is shorter and shorter, but it
# never reaches zero — and visually the ball jitters by one pixel
# on the floor.
#
# Worse: every frame the collision branch fires. If you log the
# branch you'll see hundreds of bounces per second once the ball
# is "resting." That's wasted work and visual noise.
#
# The threshold cuts this off. Below 30 px/s on the bounce, we
# call it zero. The ball goes still. Game-feel improves and the
# bug disappears.
# ----------------------------------------------------------------------------
# WHAT TO DO ONCE THIS WORKS
# ----------------------------------------------------------------------------
# 1. Change RESTITUTION to 1.0. The ball never settles. Notice the
#    bounce-height returns to the launch height each cycle — a
#    perfectly elastic bounce.
# 2. Change RESTITUTION to 0.3. The ball thuds twice and stops.
# 3. Change GRAVITY to 200. The ball floats. Tune until it feels
#    like a moon-jump.
# 4. Toggle gravity OFF with SPACE while the ball is in motion.
#    The ball becomes a Week-1 zero-g bouncer.
# 5. Optional: add a small horizontal drag while on the ground so
#    the ball comes to a horizontal stop too. Hint: when
#    ``pos.y + BALL_RADIUS == WINDOW_HEIGHT``, multiply ``vel.x``
#    by ~0.98 each frame. Or use the frame-rate-correct
#    ``math.exp(-rate * dt)`` form from Lecture 2 §8.
# ----------------------------------------------------------------------------
