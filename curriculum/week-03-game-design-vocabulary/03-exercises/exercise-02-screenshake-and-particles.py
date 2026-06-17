"""exercise-02-screenshake-and-particles.py

Goal
----
A Coin-Pink ball bounces around the four walls of the window. Every
time it hits a wall, the screen shakes proportionally to the ball's
speed at impact, and a small burst of particles spawns at the contact
point along the wall's normal direction.

This is the Week 2 bouncing-ball exercise extended with juice. The
collision math is unchanged - reflect velocity, clamp position. The
new bit is: emit an *event* when a wall hit occurs, and three feel
systems (shake, particles, the HUD counter) react to it.

Expected behaviour
------------------
- A 800x600 dark-blue window.
- A 16-px Coin-Pink ball that starts at the centre with a random
  initial velocity around 380 px/s in length.
- On every wall hit, the screen shakes proportionally to ``speed``
  (clamped) and a particle burst is emitted along the inward normal.
- A hit counter in the top-left increments by 1 per wall hit.
- The shake DOES move the ball's drawn position but does NOT alter
  the ball's logical position. The simulation is shake-independent.
- ESC or window-close quits cleanly.

What you learn
--------------
- Wiring the shake/particles systems to a collision *event* rather
  than recomputing them inline. (Preview of the event-bus pattern.)
- Tying juice magnitude to the strength of the triggering event.
  Slow ball -> tiny shake; fast ball -> big shake.
- Decoupling the world transform (shaken) from the simulation
  transform (unshaken). This is the same split a real engine uses.

Estimated time
--------------
About 40 minutes.

To complete
-----------
Fill in the ``TODO`` lines. Do not peek at the HINT block at the
bottom until you've spent 15 minutes.

Run with::

    python exercise-02-screenshake-and-particles.py
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

import pygame

# ----- Configuration --------------------------------------------------------

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_TITLE = "C11 Week 3 - Screenshake + Particles"
TARGET_FPS = 60

BACKGROUND = (20, 20, 30)
COIN_PINK = (219, 39, 119)
POWER_CYAN = (6, 182, 212)

BALL_RADIUS = 16
INITIAL_SPEED = 380.0
MAX_DT = 1.0 / 30.0


# ----- Screen-shake (same class as exercise-01) -----------------------------


class ScreenShake:
    def __init__(self) -> None:
        self.magnitude = 0.0
        self.duration_left = 0.0
        self.duration_total = 0.0

    def trigger(self, strength: float, duration: float = 0.18) -> None:
        if strength > self.magnitude:
            self.magnitude = strength
            self.duration_left = duration
            self.duration_total = duration

    def update(self, dt: float) -> None:
        if self.duration_left > 0.0:
            self.duration_left = max(0.0, self.duration_left - dt)
            if self.duration_left == 0.0:
                self.magnitude = 0.0

    def offset(self) -> tuple[int, int]:
        if self.duration_left <= 0.0 or self.duration_total <= 0.0:
            return (0, 0)
        t = self.duration_left / self.duration_total
        current = self.magnitude * t
        return (
            int(random.uniform(-current, current)),
            int(random.uniform(-current, current)),
        )


# ----- Particles (same dataclass as exercise-01, slight variant) ------------


@dataclass
class Particle:
    pos: pygame.Vector2
    vel: pygame.Vector2
    lifetime: float
    age: float = 0.0
    radius: float = 3.0
    colour: tuple[int, int, int] = COIN_PINK

    @property
    def alive(self) -> bool:
        return self.age < self.lifetime

    def update(self, dt: float) -> None:
        self.pos += self.vel * dt
        self.vel *= 0.94
        self.age += dt

    def draw(self, surface: pygame.Surface, offset: tuple[int, int]) -> None:
        t = 1.0 - (self.age / self.lifetime)
        r = max(1, int(self.radius * t))
        pygame.draw.circle(
            surface,
            self.colour,
            (int(self.pos.x + offset[0]), int(self.pos.y + offset[1])),
            r,
        )


def spawn_burst_directional(
    at: pygame.Vector2,
    normal: pygame.Vector2,
    count: int,
    speed: float = 280.0,
    lifetime: float = 0.45,
    spread_radians: float = math.pi / 2.0,
) -> list[Particle]:
    """Spawn particles in a half-disk around the inward normal.

    The full-circle burst from exercise-01 looks like an explosion at
    rest. A directional burst looks like *spray from an impact* -
    particles bounce away from the wall, not into it.
    """
    base_angle = math.atan2(normal.y, normal.x)
    out: list[Particle] = []
    for _ in range(count):
        angle = base_angle + random.uniform(-spread_radians, spread_radians)
        v = pygame.Vector2(math.cos(angle), math.sin(angle))
        v *= random.uniform(0.35, 1.0) * speed
        out.append(
            Particle(pos=pygame.Vector2(at), vel=v, lifetime=lifetime)
        )
    return out


# ----- Ball -----------------------------------------------------------------


@dataclass
class Ball:
    pos: pygame.Vector2
    vel: pygame.Vector2
    radius: int = BALL_RADIUS

    def update(self, dt: float) -> None:
        self.pos += self.vel * dt


def reflect_against_walls(
    ball: Ball,
    bounds_w: int,
    bounds_h: int,
) -> list[tuple[pygame.Vector2, pygame.Vector2, float]]:
    """Reflect the ball off the four walls and return any contacts.

    Each contact is ``(contact_point, inward_normal, impact_speed)``.
    A frame can produce 0, 1, or (rarely, in a corner) 2 contacts.
    """
    hits: list[tuple[pygame.Vector2, pygame.Vector2, float]] = []

    if ball.pos.x - ball.radius < 0:
        impact_speed = abs(ball.vel.x)
        ball.pos.x = ball.radius
        ball.vel.x = abs(ball.vel.x)
        hits.append(
            (
                pygame.Vector2(0, ball.pos.y),
                pygame.Vector2(1, 0),
                impact_speed,
            )
        )
    elif ball.pos.x + ball.radius > bounds_w:
        impact_speed = abs(ball.vel.x)
        ball.pos.x = bounds_w - ball.radius
        ball.vel.x = -abs(ball.vel.x)
        hits.append(
            (
                pygame.Vector2(bounds_w, ball.pos.y),
                pygame.Vector2(-1, 0),
                impact_speed,
            )
        )

    if ball.pos.y - ball.radius < 0:
        impact_speed = abs(ball.vel.y)
        ball.pos.y = ball.radius
        ball.vel.y = abs(ball.vel.y)
        hits.append(
            (
                pygame.Vector2(ball.pos.x, 0),
                pygame.Vector2(0, 1),
                impact_speed,
            )
        )
    elif ball.pos.y + ball.radius > bounds_h:
        impact_speed = abs(ball.vel.y)
        ball.pos.y = bounds_h - ball.radius
        ball.vel.y = -abs(ball.vel.y)
        hits.append(
            (
                pygame.Vector2(ball.pos.x, bounds_h),
                pygame.Vector2(0, -1),
                impact_speed,
            )
        )

    return hits


# ----- Main loop ------------------------------------------------------------


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    angle = random.uniform(0, math.tau)
    ball = Ball(
        pos=pygame.Vector2(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2),
        vel=pygame.Vector2(math.cos(angle), math.sin(angle)) * INITIAL_SPEED,
    )

    shake = ScreenShake()
    particles: list[Particle] = []
    hit_count = 0

    dt = 0.0
    running = True
    while running:
        # 1. Input -----------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        # 2. Update ----------------------------------------------------
        ball.update(dt)
        hits = reflect_against_walls(ball, WINDOW_WIDTH, WINDOW_HEIGHT)
        for contact_pos, inward_normal, impact_speed in hits:
            hit_count += 1
            # Map impact speed in px/s to a shake magnitude in px.
            # 200 px/s -> 3 px, 800 px/s -> 12 px.
            # TODO: compute a shake strength proportional to
            #       ``impact_speed``. Clamp into [2, 14]. Trigger the
            #       shake. Then spawn a directional burst from
            #       ``contact_pos`` along ``inward_normal`` with a
            #       count proportional to impact_speed (clamp into
            #       [4, 24]).
            pass

        shake.update(dt)
        for p in particles:
            p.update(dt)
        particles = [p for p in particles if p.alive]

        # 3. Render ----------------------------------------------------
        screen.fill(BACKGROUND)
        ox, oy = shake.offset()

        pygame.draw.circle(
            screen,
            COIN_PINK,
            (int(ball.pos.x + ox), int(ball.pos.y + oy)),
            ball.radius,
        )
        for p in particles:
            p.draw(screen, (ox, oy))

        # HUD (NOT shaken).
        hud = font.render(
            f"wall hits: {hit_count}    alive particles: {len(particles)}    "
            f"speed: {ball.vel.length():.0f} px/s",
            True,
            POWER_CYAN,
        )
        screen.blit(hud, (12, 12))

        pygame.display.flip()

        # 4. Tick + dt -------------------------------------------------
        dt = min(clock.tick(TARGET_FPS) / 1000.0, MAX_DT)

    pygame.quit()


if __name__ == "__main__":
    main()


# ----------------------------------------------------------------------------
# HINT (read only after 15+ minutes of effort)
# ----------------------------------------------------------------------------
#
# Inside the per-hit loop:
#
#     # Linear mapping with clamps. 200 px/s -> 3, 800 px/s -> 12.
#     # m(s) = a*s + b  with m(200)=3 and m(800)=12  =>  a=0.015, b=0
#     strength = max(2.0, min(14.0, 0.015 * impact_speed))
#     shake.trigger(strength, duration=0.18)
#
#     # Particle count similarly scaled.
#     count = int(max(4, min(24, impact_speed * 0.03)))
#     particles.extend(spawn_burst_directional(
#         contact_pos, inward_normal, count=count, speed=260.0, lifetime=0.45,
#     ))
#
# ----------------------------------------------------------------------------
# WHY DOES THE PARTICLE COUNT SCALE WITH IMPACT SPEED?
# ----------------------------------------------------------------------------
# A signal needs a quiet baseline to be visible. If every wall hit
# spawns 30 particles, the player's brain filters all of them out.
# If a glancing hit spawns 4 particles and a hard hit spawns 24, the
# *difference* gives the player information about impact strength
# even before they consciously notice the shake.
#
# This is what we mean by "juice is information, not decoration."
# ----------------------------------------------------------------------------
# WHY USE A "DIRECTIONAL" BURST AND NOT A FULL CIRCLE?
# ----------------------------------------------------------------------------
# A full-circle burst at a wall would send half the particles INTO
# the wall, where they instantly clip out of the visible play area.
# That looks broken. A half-disk burst around the inward normal sends
# every particle into the visible play area, which reads as "debris
# bouncing off the wall" - exactly the impression we want.
#
# This is the same reason real impact-FX systems use cone emitters
# instead of point emitters.
# ----------------------------------------------------------------------------
# WHAT TO DO ONCE THIS WORKS
# ----------------------------------------------------------------------------
# 1. Crank up the initial speed to 1200 px/s. Watch the shake max
#    out at 14 px while the ball gets brighter. Is the cap right?
# 2. Set the spread to 2*pi (i.e., full circle). Re-run. Notice how
#    much "wronger" it feels. Reset.
# 3. Remove the inward-normal arg entirely - emit particles with
#    velocity ``-ball.vel`` (radiating backward along the ball's
#    trajectory). This is *also* correct, sometimes more so, for
#    fast objects. Compare side by side.
# 4. Add a 60-ms hit-stop on contact: a frame counter that, when
#    non-zero, makes ``ball.update(dt)`` a no-op. Hit-stop is one of
#    the cheapest tricks in the book; you'll feel the difference.
# ----------------------------------------------------------------------------
