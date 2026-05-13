"""exercise-01-add-three-juice-touches.py

Goal
----
A single Coin-Pink square sits in the middle of the window. When you
click on it, three things happen at once:

  1. The screen briefly shakes (a decaying camera offset).
  2. A small burst of Coin-Pink particles spawns from the click point.
  3. A short sound effect plays (optional - the file may not exist).

This is the smallest possible "juice on demand" sandbox. Once these
three pieces work in isolation, the mini-project for this week is
mostly bookkeeping: fire the same three effects from the brick-
breaker's collision handler instead of from a mouse click.

Expected behaviour
------------------
- A 800x600 dark-blue window.
- A 120x120 Coin-Pink square centred on screen.
- LMB anywhere: medium juice (shake=6 px, 12 particles, 0.7 volume).
- RMB on the square: BIG juice (shake=14 px, 30 particles, 1.0 volume).
- ESC or window-close quits cleanly.
- The square does NOT move. Only the world is rendered with an offset.

What you learn
--------------
- A self-contained screen-shake class with decaying magnitude.
- A particle as a dataclass with pos, vel, lifetime; a list to manage
  them with the standard "filter dead" idiom.
- Pygame's mixer: ``pre_init`` for low latency, ``Sound.set_volume``.
- How to scope a juice trigger to "what kind of event happened" rather
  than spraying everything for every input.

Estimated time
--------------
About 35 minutes.

To complete
-----------
Fill in the ``TODO`` lines. Do not peek at the HINT block at the
bottom of this file until you've spent 15 minutes.

Run with::

    python exercise-01-add-three-juice-touches.py

Asset note
----------
If you don't have a hit.wav file, the script falls back to silent
mode. To get one quickly:
  - https://sfxr.me/  (browser tool, generate-and-save in 60 seconds)
  - https://freesound.org/  (search "click" or "thud", CC0 only)
Save it as ``assets/audio/hit.wav`` next to this file.
"""

from __future__ import annotations

import math
import os
import random
from dataclasses import dataclass

import pygame

# ----- Configuration --------------------------------------------------------

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_TITLE = "C11 Week 3 - Three Juice Touches"
TARGET_FPS = 60

BACKGROUND = (20, 20, 30)
COIN_PINK = (219, 39, 119)
POWER_CYAN = (6, 182, 212)

SQUARE_SIZE = 120
MAX_DT = 1.0 / 30.0

AUDIO_PATH = os.path.join(os.path.dirname(__file__), "assets", "audio", "hit.wav")


# ----- Screen-shake ---------------------------------------------------------


class ScreenShake:
    """A decaying camera-offset effect.

    ``trigger(strength, duration)`` on an event.
    ``update(dt)`` once a frame.
    ``offset()`` returns the (dx, dy) the world should be blitted at.
    """

    def __init__(self) -> None:
        self.magnitude = 0.0
        self.duration_left = 0.0
        self.duration_total = 0.0

    def trigger(self, strength: float, duration: float = 0.2) -> None:
        # Larger pending shakes win. Smaller ones do not cut off a
        # bigger ongoing shake.
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
        t = self.duration_left / self.duration_total  # 1 -> 0 over the shake
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
        self.vel *= 0.96
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


def spawn_burst(
    at: pygame.Vector2,
    count: int,
    speed: float = 220.0,
    lifetime: float = 0.4,
) -> list[Particle]:
    out: list[Particle] = []
    for _ in range(count):
        angle = random.uniform(0, math.tau)
        v = pygame.Vector2(math.cos(angle), math.sin(angle))
        v *= random.uniform(0.3, 1.0) * speed
        out.append(Particle(pos=pygame.Vector2(at), vel=v, lifetime=lifetime))
    return out


# ----- Main loop ------------------------------------------------------------


def main() -> None:
    # Low-latency audio MUST be configured before pygame.init().
    pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    clock = pygame.time.Clock()

    # ----- Load the optional sound ------------------------------------
    hit_sound: pygame.mixer.Sound | None = None
    if os.path.isfile(AUDIO_PATH):
        try:
            hit_sound = pygame.mixer.Sound(AUDIO_PATH)
            hit_sound.set_volume(0.7)
        except pygame.error:
            hit_sound = None

    # ----- Persistent game state --------------------------------------
    square_rect = pygame.Rect(0, 0, SQUARE_SIZE, SQUARE_SIZE)
    square_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)

    shake = ScreenShake()
    particles: list[Particle] = []

    dt = 0.0
    running = True
    while running:
        # 1. Input -----------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                click_pos = pygame.Vector2(event.pos)
                if event.button == 1:
                    # Medium juice: shake 6, 12 particles, vol 0.7
                    # TODO: trigger a medium shake, spawn a medium burst,
                    #       and play the hit_sound at volume 0.7 if it
                    #       exists. See HINT block.
                    pass
                elif event.button == 3 and square_rect.collidepoint(event.pos):
                    # Big juice: shake 14, 30 particles, vol 1.0
                    # TODO: trigger a big shake, spawn a big burst,
                    #       play the hit_sound at volume 1.0 if it
                    #       exists.
                    pass

        # 2. Update ----------------------------------------------------
        shake.update(dt)
        for p in particles:
            p.update(dt)
        particles = [p for p in particles if p.alive]

        # 3. Render ----------------------------------------------------
        screen.fill(BACKGROUND)
        ox, oy = shake.offset()
        # Square is the world content; it shakes too.
        shaken_square = square_rect.move(ox, oy)
        pygame.draw.rect(screen, COIN_PINK, shaken_square)
        # Particles use the same offset so they shake with the world.
        for p in particles:
            p.draw(screen, (ox, oy))
        # A tiny HUD that does NOT shake (it's UI, not world).
        font = pygame.font.SysFont(None, 22)
        hud = font.render(
            f"LMB anywhere = medium juice    RMB on square = big juice    "
            f"alive particles: {len(particles)}",
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
# Inside the LMB handler:
#     shake.trigger(6.0, duration=0.2)
#     particles.extend(spawn_burst(click_pos, count=12, lifetime=0.4))
#     if hit_sound is not None:
#         hit_sound.set_volume(0.7)
#         hit_sound.play()
#
# Inside the RMB handler:
#     shake.trigger(14.0, duration=0.35)
#     particles.extend(spawn_burst(
#         pygame.Vector2(event.pos), count=30, speed=280.0, lifetime=0.7,
#     ))
#     if hit_sound is not None:
#         hit_sound.set_volume(1.0)
#         hit_sound.play()
#
# ----------------------------------------------------------------------------
# WHY DOES THE SQUARE SHAKE BUT THE HUD DOES NOT?
# ----------------------------------------------------------------------------
# The shake is a *camera* effect. It applies to the world (the square
# and the particles). It does NOT apply to UI overlays - score, lives,
# pause menus. If your UI shakes too, the player loses their anchor
# and the screen reads as "broken" instead of "impacted."
#
# Rule of thumb: anything that lives in world-space gets the shake
# offset. Anything that lives in screen-space (HUD, menus, text) does
# not.
# ----------------------------------------------------------------------------
# WHAT TO DO ONCE THIS WORKS
# ----------------------------------------------------------------------------
# 1. Comment out the screen-shake (`shake.update`/`shake.offset`).
#    Click. Notice the particles alone don't feel as impactful.
# 2. Comment out the particles. Notice the shake without particles
#    feels disorienting - the screen "twitched" but you don't know why.
# 3. Comment out the sound. Notice how much weight the audio carries
#    by itself.
# 4. Restore all three. Notice how the three together communicate
#    "something happened HERE, that big" without you having to think
#    about it.
# 5. Try setting the LMB shake duration to 2.0 seconds. Click once.
#    See how a long shake reads as "the game crashed," not "you hit
#    something." Set it back to 0.2 s.
# ----------------------------------------------------------------------------
