"""exercise-03-tune-the-feel.py

Goal
----
Take exercise-02's bouncing-ball-with-juice and add *runtime tuning*
for the three juice parameters that matter most:

  - Shake magnitude scale  (Q / A : +/- 0.1, range 0.0 .. 3.0)
  - Particle count scale   (W / S : +/- 0.1, range 0.0 .. 3.0)
  - Particle lifetime      (E / D : +/- 0.05, range 0.05 .. 1.2 s)

Each parameter is a multiplier on top of the per-hit defaults. With
all three at 1.0 you should see the same juice as exercise-02. Set
shake to 0.0 and you have particles-only. Set particles to 0.0 and
you have shake-only.

This exercise is the spiritual centre of Week 3: stop guessing what
"feel" means, sit with the dials in your hand, and find your own
values. There is no correct answer. There is what you ship.

Expected behaviour
------------------
- 800x600 dark-blue window, identical ball physics to exercise-02.
- A HUD that always shows the three multiplier values and their
  keybindings.
- On every wall hit, the three juice effects fire scaled by the
  current multipliers.
- ESC or window-close quits. R restarts the ball with a fresh
  random direction.

What you learn
--------------
- KEYDOWN one-shot input for incremental adjustments.
- The "everything is a multiplier" pattern for runtime tuning. This
  is the same pattern AAA engines use for designer tools.
- That your taste shifts as you play. The first values you set after
  five seconds will not be the values you ship.

Estimated time
--------------
About 45 minutes.

To complete
-----------
Fill in the ``TODO`` lines. Do not peek at the HINT block at the
bottom until you've spent 15 minutes. Then play with the values for
at least ten more minutes - this is the exercise where the keyboard
work is actually the smaller half.

Run with::

    python exercise-03-tune-the-feel.py
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

import pygame

# ----- Configuration --------------------------------------------------------

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_TITLE = "C11 Week 3 - Tune the Feel"
TARGET_FPS = 60

BACKGROUND = (20, 20, 30)
COIN_PINK = (219, 39, 119)
POWER_CYAN = (6, 182, 212)
HUD_BG = (10, 10, 20)

BALL_RADIUS = 16
INITIAL_SPEED = 380.0
MAX_DT = 1.0 / 30.0

# Base values (the "1.0 multiplier" point).
BASE_SHAKE_PER_SPEED = 0.015      # px of shake per (px/s) of impact speed
BASE_PARTICLE_PER_SPEED = 0.03    # particles per (px/s) of impact speed
BASE_PARTICLE_LIFETIME = 0.45     # seconds


# ----- Screen-shake ---------------------------------------------------------


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


# ----- Particles ------------------------------------------------------------


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
    ball: Ball, bounds_w: int, bounds_h: int
) -> list[tuple[pygame.Vector2, pygame.Vector2, float]]:
    hits: list[tuple[pygame.Vector2, pygame.Vector2, float]] = []
    if ball.pos.x - ball.radius < 0:
        impact_speed = abs(ball.vel.x)
        ball.pos.x = ball.radius
        ball.vel.x = abs(ball.vel.x)
        hits.append((pygame.Vector2(0, ball.pos.y), pygame.Vector2(1, 0), impact_speed))
    elif ball.pos.x + ball.radius > bounds_w:
        impact_speed = abs(ball.vel.x)
        ball.pos.x = bounds_w - ball.radius
        ball.vel.x = -abs(ball.vel.x)
        hits.append((pygame.Vector2(bounds_w, ball.pos.y), pygame.Vector2(-1, 0), impact_speed))
    if ball.pos.y - ball.radius < 0:
        impact_speed = abs(ball.vel.y)
        ball.pos.y = ball.radius
        ball.vel.y = abs(ball.vel.y)
        hits.append((pygame.Vector2(ball.pos.x, 0), pygame.Vector2(0, 1), impact_speed))
    elif ball.pos.y + ball.radius > bounds_h:
        impact_speed = abs(ball.vel.y)
        ball.pos.y = bounds_h - ball.radius
        ball.vel.y = -abs(ball.vel.y)
        hits.append((pygame.Vector2(ball.pos.x, bounds_h), pygame.Vector2(0, -1), impact_speed))
    return hits


def fresh_ball() -> Ball:
    angle = random.uniform(0, math.tau)
    return Ball(
        pos=pygame.Vector2(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2),
        vel=pygame.Vector2(math.cos(angle), math.sin(angle)) * INITIAL_SPEED,
    )


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


# ----- Main loop ------------------------------------------------------------


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 22)

    ball = fresh_ball()
    shake = ScreenShake()
    particles: list[Particle] = []

    shake_scale = 1.0
    particle_scale = 1.0
    particle_lifetime = BASE_PARTICLE_LIFETIME

    dt = 0.0
    running = True
    while running:
        # 1. Input -----------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    ball = fresh_ball()
                # TODO: Q raises shake_scale by 0.1, A lowers by 0.1.
                #       Clamp to [0.0, 3.0]. Same for particle_scale on
                #       W/S. Same for particle_lifetime on E/D with
                #       +/- 0.05 and range [0.05, 1.2].

        # 2. Update ----------------------------------------------------
        ball.update(dt)
        hits = reflect_against_walls(ball, WINDOW_WIDTH, WINDOW_HEIGHT)
        for contact_pos, inward_normal, impact_speed in hits:
            # Shake.
            base_strength = BASE_SHAKE_PER_SPEED * impact_speed
            strength = clamp(base_strength * shake_scale, 0.0, 24.0)
            if strength > 0.0:
                shake.trigger(strength, duration=0.18)

            # Particles.
            base_count = BASE_PARTICLE_PER_SPEED * impact_speed * particle_scale
            count = int(clamp(base_count, 0.0, 64.0))
            if count > 0:
                particles.extend(
                    spawn_burst_directional(
                        contact_pos,
                        inward_normal,
                        count=count,
                        speed=260.0,
                        lifetime=particle_lifetime,
                    )
                )

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
        hud_lines = [
            f"shake_scale     (Q/A): {shake_scale:.2f}",
            f"particle_scale  (W/S): {particle_scale:.2f}",
            f"particle_lifetime (E/D): {particle_lifetime:.2f} s",
            f"alive particles: {len(particles)}    R: restart ball",
        ]
        # Background panel for legibility.
        panel = pygame.Rect(8, 8, 320, 22 * len(hud_lines) + 8)
        pygame.draw.rect(screen, HUD_BG, panel)
        for i, text in enumerate(hud_lines):
            surf = font.render(text, True, POWER_CYAN)
            screen.blit(surf, (16, 12 + i * 22))

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
# Inside the KEYDOWN handler, after the existing ESC/R cases:
#
#     elif event.key == pygame.K_q:
#         shake_scale = clamp(shake_scale + 0.1, 0.0, 3.0)
#     elif event.key == pygame.K_a:
#         shake_scale = clamp(shake_scale - 0.1, 0.0, 3.0)
#     elif event.key == pygame.K_w:
#         particle_scale = clamp(particle_scale + 0.1, 0.0, 3.0)
#     elif event.key == pygame.K_s:
#         particle_scale = clamp(particle_scale - 0.1, 0.0, 3.0)
#     elif event.key == pygame.K_e:
#         particle_lifetime = clamp(particle_lifetime + 0.05, 0.05, 1.2)
#     elif event.key == pygame.K_d:
#         particle_lifetime = clamp(particle_lifetime - 0.05, 0.05, 1.2)
#
# ----------------------------------------------------------------------------
# DEFAULT VALUES TO TRY (PLAYTEST EACH FOR 30 SECONDS)
# ----------------------------------------------------------------------------
# preset name      shake_scale  particle_scale  particle_lifetime
# off:             0.0          0.0             0.05
# minimal:         0.5          0.5             0.30
# default:         1.0          1.0             0.45
# punchy:          1.4          1.2             0.30   (short, fast)
# slow-mo debris:  0.8          1.8             0.95   (lingering)
# all juice:       2.6          2.4             0.85   (probably too much)
#
# Notice that "punchy" and "slow-mo debris" use the SAME particle
# count range but feel completely different - because the *lifetime*
# changes whether particles read as "spark" or as "smoke."
# ----------------------------------------------------------------------------
# A NOTE ON TUNING DISCIPLINE
# ----------------------------------------------------------------------------
# The temptation is to set every value to 3.0 and grin. Resist it.
# Real game-feel work is about finding the MINIMUM value at which an
# effect still does its job. A 3.0 shake on every hit is loud the
# first time, exhausting after thirty seconds, and indistinguishable
# from a 1.5 shake by the player's tenth hit because their visual
# system has adapted.
#
# Tune for the player's tenth hit, not their first.
# ----------------------------------------------------------------------------
# WHAT TO DO ONCE THIS WORKS
# ----------------------------------------------------------------------------
# 1. Play for two minutes with default values (all 1.0, 0.45 s).
# 2. Crank shake to 3.0. Play for two minutes. Is the game still
#    readable? Can you still track the ball?
# 3. Reset, then drop particle_lifetime to 0.05. Play for two minutes.
#    Particles are invisible. Is the loss noticeable? Bring it back to
#    0.45 and notice the *return* of the information.
# 4. Find the values you'd actually ship for a brick-breaker. Write
#    them down. You'll need them for the mini-project this week.
# ----------------------------------------------------------------------------
