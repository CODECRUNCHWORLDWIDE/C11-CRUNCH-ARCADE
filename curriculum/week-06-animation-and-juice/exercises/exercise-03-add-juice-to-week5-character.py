"""exercise-03-add-juice-to-week5-character.py

Goal
----
Take the four-state-plus-hurt player from Week 5 Exercise 2 and
add a juice pass: squash-and-stretch on jump and land, screen shake
on landing and hit, a dust-particle emitter on land and footstep,
a red hit-flash on damage, and stub sound cues fired from each FSM
transition. The character is the same coloured rectangle. The DIFF
is the feel.

The architectural commitment from Week 5 -- one class per state,
``enter`` plays an effect, ``exit`` stops it -- is what makes this
exercise short. The whole juice pass adds ~120 lines on top of the
Week-5 file; ~40 of those are class definitions for tween, shake,
particle field; the rest are the bindings inside the existing FSM.

Expected behaviour
------------------
- An 800x480 window with a Coin-Pink player on a grey floor at y=380.
- Two red spike blocks on the floor (same as Week 5 ex 2).
- A/D / arrows move; SPACE jumps; ESC quits. R resets the squash
  tweens for tuning experiments.
- On jump: a slight pre-jump squash, an upward stretch in mid-air.
- On land: the character squashes vertically (~0.7 scale_y) and
  recovers with an ``ease_out_back`` overshoot. A 4 px screen shake
  fires for 100 ms. Six dust particles spray from the feet.
- On hit (walk into a spike): hit-flash for 80 ms, 12 Coin-Pink
  particles, an 8 px screen shake for 180 ms, knockback.
- On footstep (every 280 ms while running): three tiny dust particles
  at the feet, no shake.
- Console prints every FSM transition AND every SFX cue fired:
  ``[fsm] IdleState -> RunState`` and ``  [sfx] jump``.

What you learn
--------------
- Wiring squash-and-stretch into ``enter()`` of jump and land.
- Wiring screen shake into ``enter()`` of land and hit.
- Wiring a particle emitter into ``enter()`` and into a per-frame
  footstep timer.
- Wiring SFX stubs into the same hooks. Real ``.wav`` files plug into
  exactly the same code in the mini-project.
- Keeping the character's scale_y as a CHARACTER field (drawn but not
  collided), so the hitbox doesn't deform with the art.

Estimated time
--------------
About 55-70 minutes. The code is short; the TUNING is the work.

To complete
-----------
Read top to bottom; the file is structured as a Week-5-Ex-2 baseline
plus a juice pass. Look for the ``# JUICE`` comments to find every
addition. The HINT block at the bottom has knob-tuning notes; don't
peek until you've played with the defaults for at least 20 minutes.

Run with::

    python exercise-03-add-juice-to-week5-character.py
"""

from __future__ import annotations

import math
import random
import sys
from dataclasses import dataclass, field
from typing import Callable, Optional

import pygame

# ----- Configuration --------------------------------------------------------

WINDOW_W = 800
WINDOW_H = 480
TARGET_FPS = 60
WINDOW_TITLE = "C11 Week 6 - Exercise 3 - Juice pass on Week-5 character"

GROUND_Y = 380
PLAYER_W = 24
PLAYER_H = 32

GRAVITY = 1800.0
JUMP_VEL = 650.0
RUN_SPEED = 240.0
TERMINAL_V = 1200.0

HURT_DURATION = 0.5
HURT_KNOCKBACK_X = 220.0
HURT_KNOCKBACK_Y = -300.0
HURT_DECAY = 0.92
HIT_FLASH_DURATION = 0.08

MAX_DT = 1.0 / 30.0

# Juice knobs. Tune these.
SQUASH_LAUNCH_FROM = 1.0
SQUASH_LAUNCH_TO = 1.18           # vertical stretch on jump
SQUASH_LAUNCH_DUR = 0.10
SQUASH_LAND_FROM = 0.65           # heavy land squash
SQUASH_LAND_TO = 1.0
SQUASH_LAND_DUR = 0.20            # with ease_out_back overshoot
SHAKE_LAND_AMP = 4.0
SHAKE_LAND_DUR = 0.10
SHAKE_HIT_AMP = 8.0
SHAKE_HIT_DUR = 0.18
FOOTSTEP_INTERVAL = 0.28          # seconds between footstep particle bursts
DUST_LAND_COUNT = 8
DUST_FOOTSTEP_COUNT = 3
PARTICLE_HIT_COUNT = 12

BACKGROUND = (24, 24, 32)
GROUND = (140, 140, 150)
GROUND_LINE = (90, 90, 100)
COIN_PINK = (219, 39, 119)
HIT_FLASH_COLOR = (255, 255, 255)
SPIKE = (200, 60, 40)
HUD_BG = (12, 12, 20)
HUD_FG = (220, 220, 230)
POWER_CYAN = (6, 182, 212)
DUST_COLOR = (180, 170, 160)


# ----- lerp + easing (lifted from Exercise 2) -------------------------------


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def linear(t: float) -> float:
    return t


def ease_in(t: float) -> float:
    return t * t


def ease_out(t: float) -> float:
    return 1.0 - (1.0 - t) * (1.0 - t)


def ease_out_back(t: float, overshoot: float = 1.70158) -> float:
    s = overshoot
    u = t - 1.0
    return u * u * ((s + 1.0) * u + s) + 1.0


# ----- Tween ----------------------------------------------------------------


@dataclass
class Tween:
    start: float
    end: float
    duration: float
    elapsed: float = 0.0
    ease: Callable[[float], float] = linear

    def update(self, dt: float) -> None:
        if self.elapsed < self.duration:
            self.elapsed = min(self.elapsed + dt, self.duration)

    def reset(self) -> None:
        self.elapsed = 0.0

    def value(self) -> float:
        if self.duration <= 0:
            return self.end
        t = max(0.0, min(1.0, self.elapsed / self.duration))
        return lerp(self.start, self.end, self.ease(t))

    def done(self) -> bool:
        return self.elapsed >= self.duration


# ----- Screen shake ---------------------------------------------------------


@dataclass
class ScreenShake:
    amplitude: float = 0.0
    duration: float = 0.0
    elapsed: float = 0.0

    def kick(self, amp: float, dur: float) -> None:
        # Don't stomp a stronger shake with a weaker one.
        remaining_amp = self.amplitude * max(
            0.0, 1.0 - (self.elapsed / self.duration if self.duration > 0
                        else 1.0))
        if amp >= remaining_amp:
            self.amplitude = amp
            self.duration = dur
            self.elapsed = 0.0

    def update(self, dt: float) -> None:
        if self.elapsed < self.duration:
            self.elapsed = min(self.elapsed + dt, self.duration)
        if self.elapsed >= self.duration:
            self.amplitude = 0.0
            self.duration = 0.0
            self.elapsed = 0.0

    def offset(self) -> tuple[int, int]:
        if self.amplitude <= 0 or self.duration <= 0:
            return (0, 0)
        remaining = max(0.0, 1.0 - self.elapsed / self.duration)
        amp = self.amplitude * remaining
        return (int(round(random.uniform(-amp, amp))),
                int(round(random.uniform(-amp, amp))))


# ----- Particles ------------------------------------------------------------


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    lifetime: float
    max_lifetime: float
    radius: float = 2.0
    color: tuple[int, int, int] = (200, 200, 220)
    gravity: float = 600.0

    def alive(self) -> bool:
        return self.lifetime > 0

    def update(self, dt: float) -> None:
        self.lifetime -= dt
        self.vy += self.gravity * dt
        self.x += self.vx * dt
        self.y += self.vy * dt


class ParticleField:
    def __init__(self) -> None:
        self.particles: list[Particle] = []

    def emit_dust(self, x: float, y: float, count: int = 6,
                  spread: float = 80.0) -> None:
        for _ in range(count):
            self.particles.append(Particle(
                x=x + random.uniform(-3, 3),
                y=y,
                vx=random.uniform(-spread, spread),
                vy=random.uniform(-160, -50),
                lifetime=random.uniform(0.25, 0.45),
                max_lifetime=0.45,
                radius=random.uniform(1.5, 3.0),
                color=DUST_COLOR,
                gravity=400.0,
            ))

    def emit_hit(self, x: float, y: float, count: int = 12) -> None:
        for _ in range(count):
            angle = random.uniform(0.0, math.tau)
            speed = random.uniform(140.0, 280.0)
            self.particles.append(Particle(
                x=x, y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed - 60,
                lifetime=random.uniform(0.35, 0.7),
                max_lifetime=0.7,
                radius=random.uniform(2.0, 3.5),
                color=COIN_PINK,
                gravity=900.0,
            ))

    def update(self, dt: float) -> None:
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.alive()]

    def draw(self, screen: pygame.Surface,
             camera_offset: tuple[int, int] = (0, 0)) -> None:
        ox, oy = camera_offset
        for p in self.particles:
            alpha_frac = max(0.0, p.lifetime / p.max_lifetime)
            r = max(1, int(p.radius * (0.4 + 0.6 * alpha_frac)))
            pygame.draw.circle(
                screen, p.color,
                (int(p.x) + ox, int(p.y) + oy),
                r)


# ----- SFX stub -------------------------------------------------------------


class SFX:
    """Stub. Prints to console instead of playing audio. The
    mini-project replaces this with a real ``pygame.mixer`` version;
    every call site stays unchanged. That is the architectural
    payoff of binding SFX to FSM ``enter`` / ``exit``."""

    def play_one_shot(self, name: str, volume: float = 1.0) -> None:
        print(f"  [sfx] {name}")

    def play(self, name: str, loop: bool = True,
             volume: float = 1.0) -> None:
        print(f"  [sfx] {name} (loop)")

    def stop(self, name: str) -> None:
        print(f"  [sfx] {name} stop")


# ----- World ----------------------------------------------------------------


class World:
    """Shared juice systems live here so any state can reach them via
    ``char.world``."""

    def __init__(self) -> None:
        self.shake = ScreenShake()
        self.particles = ParticleField()
        self.sfx = SFX()


# ----- State base class -----------------------------------------------------


class State:
    name = "state"

    def enter(self, char: "Character") -> None:
        pass

    def update(self, char: "Character", dt: float) -> None:
        pass

    def exit(self, char: "Character") -> None:
        pass


# ----- Concrete states ------------------------------------------------------


class IdleState(State):
    name = "IdleState"

    def enter(self, char: "Character") -> None:
        char.vx = 0.0
        # JUICE: if we arrived from an airborne state, do the land
        # squash-and-recover. The flag is set by the airborne states
        # before transitioning.
        if char.arrived_airborne:
            _apply_land_juice(char)
            char.arrived_airborne = False

    def update(self, char: "Character", dt: float) -> None:
        char.vx = char.move_input * RUN_SPEED
        if char.move_input != 0:
            char.change_state(RunState())
            return
        if char.jump_pressed_this_frame and char.grounded:
            char.change_state(JumpState())
            return
        if not char.grounded:
            char.change_state(FallState())
            return


class RunState(State):
    name = "RunState"

    def enter(self, char: "Character") -> None:
        char.world.sfx.play("footsteps_loop", loop=True, volume=0.3)
        if char.arrived_airborne:
            _apply_land_juice(char)
            char.arrived_airborne = False
        # Reset the per-state footstep timer so the first footstep
        # particle fires after one full interval, not on entry.
        char.footstep_t = 0.0

    def update(self, char: "Character", dt: float) -> None:
        char.vx = char.move_input * RUN_SPEED
        # JUICE: emit a tiny dust burst on a regular interval while
        # running on the ground.
        char.footstep_t += dt
        if char.footstep_t >= FOOTSTEP_INTERVAL:
            char.footstep_t = 0.0
            char.world.particles.emit_dust(
                x=char.x + PLAYER_W / 2,
                y=char.y + PLAYER_H,
                count=DUST_FOOTSTEP_COUNT,
                spread=40.0)
            char.world.sfx.play_one_shot("footstep", volume=0.4)
        # Transitions.
        if char.move_input == 0:
            char.change_state(IdleState())
            return
        if char.jump_pressed_this_frame and char.grounded:
            char.change_state(JumpState())
            return
        if not char.grounded:
            char.change_state(FallState())
            return

    def exit(self, char: "Character") -> None:
        char.world.sfx.stop("footsteps_loop")


class AirborneState(State):
    name = "AirborneState"

    def update_airborne(self, char: "Character", dt: float) -> None:
        char.vx = char.move_input * RUN_SPEED
        char.vy += GRAVITY * dt
        if char.vy > TERMINAL_V:
            char.vy = TERMINAL_V


class JumpState(AirborneState):
    name = "JumpState"

    def enter(self, char: "Character") -> None:
        char.vy = -JUMP_VEL
        char.grounded = False
        # JUICE: an upward stretch on jump (taller, narrower).
        char.scale_y_tween = Tween(
            start=SQUASH_LAUNCH_FROM, end=SQUASH_LAUNCH_TO,
            duration=SQUASH_LAUNCH_DUR, ease=ease_out)
        char.world.sfx.play_one_shot("jump")

    def update(self, char: "Character", dt: float) -> None:
        self.update_airborne(char, dt)
        if char.vy >= 0:
            char.change_state(FallState())
            return
        if char.grounded:
            char.arrived_airborne = True
            char.change_state(IdleState())
            return


class FallState(AirborneState):
    name = "FallState"

    def enter(self, char: "Character") -> None:
        # JUICE: gentle return-to-neutral scale during the fall. The
        # squash from JumpState's launch decays here.
        char.scale_y_tween = Tween(
            start=char.scale_y_tween.value() if char.scale_y_tween else 1.0,
            end=1.0, duration=0.15, ease=ease_out)

    def update(self, char: "Character", dt: float) -> None:
        self.update_airborne(char, dt)
        if char.grounded:
            char.arrived_airborne = True
            char.change_state(IdleState())
            return


class HurtState(State):
    name = "HurtState"

    def __init__(self, hit_source_x: float):
        self.hit_source_x = hit_source_x
        self.timer = HURT_DURATION

    def enter(self, char: "Character") -> None:
        knockback_dir = -1.0 if self.hit_source_x < char.x else +1.0
        char.vx = knockback_dir * HURT_KNOCKBACK_X
        char.vy = HURT_KNOCKBACK_Y
        char.grounded = False
        char.invincible = True
        # JUICE: hit-flash, shake, particle burst, all bound to enter.
        char.hit_flash_t = HIT_FLASH_DURATION
        char.world.shake.kick(amp=SHAKE_HIT_AMP, dur=SHAKE_HIT_DUR)
        char.world.particles.emit_hit(
            x=char.x + PLAYER_W / 2,
            y=char.y + PLAYER_H / 2,
            count=PARTICLE_HIT_COUNT)
        char.world.sfx.play_one_shot("hit")

    def update(self, char: "Character", dt: float) -> None:
        char.vx *= HURT_DECAY
        char.vy += GRAVITY * dt
        if char.vy > TERMINAL_V:
            char.vy = TERMINAL_V
        self.timer -= dt
        if self.timer <= 0:
            if char.grounded:
                char.arrived_airborne = False
                char.change_state(IdleState())
            else:
                char.change_state(FallState())

    def exit(self, char: "Character") -> None:
        char.invincible = False


# ----- The land-juice helper (used by IdleState and RunState) ---------------


def _apply_land_juice(char: "Character") -> None:
    """Fire all the landing-impact juice as a single function.

    Bound to ``IdleState.enter`` and ``RunState.enter`` when arriving
    from an airborne state. Keeps the two enter() methods short and
    the juice consistent."""
    char.scale_y_tween = Tween(
        start=SQUASH_LAND_FROM, end=SQUASH_LAND_TO,
        duration=SQUASH_LAND_DUR, ease=ease_out_back)
    char.world.shake.kick(amp=SHAKE_LAND_AMP, dur=SHAKE_LAND_DUR)
    char.world.particles.emit_dust(
        x=char.x + PLAYER_W / 2,
        y=char.y + PLAYER_H,
        count=DUST_LAND_COUNT,
        spread=120.0)
    char.world.sfx.play_one_shot("land")


# ----- Character ------------------------------------------------------------


@dataclass
class Character:
    world: World
    x: float = 100.0
    y: float = GROUND_Y - PLAYER_H
    vx: float = 0.0
    vy: float = 0.0
    grounded: bool = True
    move_input: int = 0
    jump_pressed_this_frame: bool = False
    invincible: bool = False
    arrived_airborne: bool = False
    footstep_t: float = 0.0
    hit_flash_t: float = 0.0
    scale_y_tween: Optional[Tween] = None
    state: State = field(default_factory=IdleState)

    def __post_init__(self) -> None:
        # Default squash tween at neutral so the first draw doesn't crash.
        self.scale_y_tween = Tween(start=1.0, end=1.0, duration=0.001)
        self.state.enter(self)

    def change_state(self, new_state: State) -> None:
        print(f"[fsm] {type(self.state).__name__} "
              f"-> {type(new_state).__name__}")
        self.state.exit(self)
        self.state = new_state
        self.state.enter(self)

    def take_hit(self, hit_source_x: float) -> None:
        if self.invincible:
            return
        self.change_state(HurtState(hit_source_x))

    def update(self, dt: float) -> None:
        if self.scale_y_tween is not None:
            self.scale_y_tween.update(dt)
        if self.hit_flash_t > 0:
            self.hit_flash_t = max(0.0, self.hit_flash_t - dt)
        self.state.update(self, dt)


# ----- World physics --------------------------------------------------------


@dataclass
class Spike:
    x: int
    width: int = 32
    height: int = 16

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, GROUND_Y - self.height,
                           self.width, self.height)


SPIKES = [Spike(x=360), Spike(x=540)]


def integrate_and_collide(c: Character, dt: float) -> None:
    c.x += c.vx * dt
    c.y += c.vy * dt
    c.x = max(0, min(WINDOW_W - PLAYER_W, c.x))
    floor_top = GROUND_Y - PLAYER_H
    if c.y >= floor_top:
        c.y = floor_top
        if c.vy > 0:
            c.vy = 0
        c.grounded = True
    else:
        c.grounded = False


def check_spike_hits(c: Character) -> None:
    player_rect = pygame.Rect(int(c.x), int(c.y), PLAYER_W, PLAYER_H)
    for sp in SPIKES:
        if player_rect.colliderect(sp.rect):
            c.take_hit(sp.x + sp.width / 2)
            return


# ----- Render ---------------------------------------------------------------


def draw(screen: pygame.Surface, font: pygame.font.Font, c: Character,
         world: World, fps: float) -> None:
    screen.fill(BACKGROUND)
    sx, sy = world.shake.offset()
    # Ground.
    pygame.draw.rect(screen, GROUND,
                     (0 + sx, GROUND_Y + sy,
                      WINDOW_W, WINDOW_H - GROUND_Y))
    pygame.draw.line(screen, GROUND_LINE,
                     (0 + sx, GROUND_Y + sy),
                     (WINDOW_W + sx, GROUND_Y + sy), 2)
    # Spikes.
    for sp in SPIKES:
        r = sp.rect.move(sx, sy)
        pygame.draw.rect(screen, SPIKE, r)
        for i in range(4):
            tx = r.x + i * 8
            pygame.draw.polygon(screen, SPIKE, [
                (tx, r.y),
                (tx + 4, r.y - 6),
                (tx + 8, r.y),
            ])
    # Particles (also shaken with the world).
    world.particles.draw(screen, camera_offset=(sx, sy))
    # Player.
    scale_y = c.scale_y_tween.value() if c.scale_y_tween else 1.0
    scale_x = 1.0 / max(0.6, scale_y) if scale_y > 1.0 else 1.0 + (1.0 - scale_y) * 0.5
    draw_w = int(PLAYER_W * scale_x)
    draw_h = int(PLAYER_H * scale_y)
    # Feet stay at the same y; the squash compresses upward.
    draw_x = int(c.x + (PLAYER_W - draw_w) / 2) + sx
    draw_y = int(c.y + (PLAYER_H - draw_h)) + sy
    color = HIT_FLASH_COLOR if c.hit_flash_t > 0 else COIN_PINK
    pygame.draw.rect(screen, color,
                     (draw_x, draw_y, draw_w, draw_h))
    # HUD.
    pygame.draw.rect(screen, HUD_BG, (0, 0, WINDOW_W, 28))
    label = (f"state={type(c.state).__name__:11s}  "
             f"sy={scale_y:.2f}  "
             f"shake_amp={world.shake.amplitude:4.1f}  "
             f"particles={len(world.particles.particles):3d}  "
             f"inv={c.invincible!s:5s}  "
             f"fps={fps:5.1f}")
    screen.blit(font.render(label, True, HUD_FG), (8, 6))
    screen.blit(
        font.render(
            "[A/D + SPACE] move/jump   walk into a spike to feel the hit",
            True, POWER_CYAN),
        (8, WINDOW_H - 22))


# ----- Main -----------------------------------------------------------------


def main() -> int:
    pygame.init()
    pygame.display.set_caption(WINDOW_TITLE)
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 14, bold=False)

    world = World()
    c = Character(world=world)

    running = True
    while running:
        raw_dt = clock.tick(TARGET_FPS) / 1000.0
        dt = min(raw_dt, MAX_DT)

        c.jump_pressed_this_frame = False
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    running = False
                elif ev.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP):
                    c.jump_pressed_this_frame = True
                elif ev.key == pygame.K_r:
                    # Reset the squash tween for tuning. Doesn't reset
                    # the FSM; just snaps the visual back to neutral.
                    c.scale_y_tween = Tween(start=1.0, end=1.0,
                                            duration=0.001)

        keys = pygame.key.get_pressed()
        left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        c.move_input = (1 if right else 0) - (1 if left else 0)

        c.update(dt)
        integrate_and_collide(c, dt)
        check_spike_hits(c)
        world.shake.update(dt)
        world.particles.update(dt)

        draw(screen, font, c, world, clock.get_fps())
        pygame.display.flip()

    pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())


# ----- HINT (do not peek for at least 20 minutes) --------------------------
#
# 1. The squash-and-stretch SCALE is on the visual draw only. The
#    collision rect (PLAYER_W x PLAYER_H) does NOT deform. If you find
#    your character clipping through the floor on a heavy squash, you
#    accidentally fed scale_y into integrate_and_collide. Don't. Art
#    deforms, hitbox doesn't.
#
# 2. SQUASH_LAND_FROM = 0.65 means the character flattens to 65% of
#    its height on landing. Crank it to 0.5 for a cartoonish flatten;
#    crank it to 0.85 for a subtle thud. The dose is the work.
#
# 3. ease_out_back gives the overshoot. Without it, the squash recovers
#    linearly and feels rubbery. Swap to ease_out and feel the diff.
#
# 4. SHAKE_LAND_AMP = 4.0 is a "soft" thud. Crank to 8.0 for a "hard"
#    one. Past 12.0 you start losing the screen's readability. Nijman's
#    rule: amplitude 6 for a player hit, amplitude 10 for a heavy NPC
#    hit, amplitude 14+ for explosions. NEVER 24+; that's migraine zone.
#
# 5. The footstep particle interval (FOOTSTEP_INTERVAL = 0.28 s)
#    matches a natural walking cadence at RUN_SPEED = 240 px/s. If you
#    raise the run speed, lower the interval proportionally or the
#    footsteps will lag behind the feet.
#
# 6. The hit-flash is a one-frame WHITE override before reverting to
#    Coin Pink. You can swap it for a Coin-Pink-deep flash if you'd
#    rather (the brand-palette accent). 80 ms is the standard; shorter
#    flashes are less visible, longer ones distract from the knockback.
#
# 7. The "arrived_airborne" flag is the cleanest way to fire land
#    juice from BOTH IdleState.enter and RunState.enter without
#    duplicating the helper call inside the airborne states. Set on
#    the airborne side; read and clear on the grounded side. This is
#    a tiny cross-state field on Character; per Lecture 2 of Week 5,
#    that's the right place for it.
#
# 8. The SFX class is a stub. Replacing it with a real version is six
#    lines and Kenney's Impact Sounds pack (50 MB, CC0, linked in
#    resources.md). Do it in the mini-project; not required here. The
#    point of the stub is that every call site is already wired -- the
#    architectural commitment is in. Lighting it up is mechanical.
