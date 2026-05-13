"""exercise-02-character-with-states.py

Goal
----
Re-implement the four-state player from Exercise 1 using the State
pattern (Nystrom, *Game Programming Patterns*, ch. State). One class
per state. Three lifecycle methods (``enter``, ``update``, ``exit``).
The character holds a reference to its current state and delegates
its own ``update(dt)`` to that state.

Same physical behaviour as Exercise 1, but the per-state behaviour is
now next to the per-state name. Reading ``JumpState`` tells you the
whole story of what the character does while jumping. No grep across
the file.

Bonus: this exercise introduces an ``AirborneState`` parent class so
``JumpState`` and ``FallState`` share their physics body, which is the
seed of the hierarchical FSM in Lecture 2 §4. We also add a fifth
state, ``HurtState``, triggered by walking into a spike block on the
floor. The HurtState has clear ``enter`` / ``exit`` side effects
(invincibility on / off) — the classic asymmetric pair the State
pattern makes visible.

Expected behaviour
------------------
- An 800x480 window. A Coin-Pink player on a grey floor at y = 380.
- Two red spike blocks are drawn on the floor. Walk into one and the
  player flashes red, gets knocked back, and is briefly invincible
  (``HurtState``). The HUD shows ``hurt`` during this time.
- Arrow keys / A / D move; SPACE jumps; ESC quits.
- The HUD prints the *class name* of the current state ("IdleState",
  "RunState", "JumpState", "FallState", "HurtState"). Walk and watch
  it change.
- Console prints transitions: ``[fsm] IdleState -> RunState``.

What you learn
--------------
- The State base class with three methods.
- One class per state; transitions are decided inside the source
  state's ``update`` method.
- The ``AirborneState`` parent: shared physics for jump and fall.
- Per-state data on the state instance (``HurtState.timer``) versus
  on the character (``Character.invincible``).
- Asymmetric ``enter`` / ``exit`` side effects done right.

Estimated time
--------------
About 45-55 minutes.

To complete
-----------
Fill in the ``TODO`` lines. Do not peek at the HINT block at the
bottom until you've spent 20 minutes.

Run with::

    python exercise-02-character-with-states.py
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import Optional

import pygame

# ----- Configuration --------------------------------------------------------

WINDOW_W = 800
WINDOW_H = 480
TARGET_FPS = 60
WINDOW_TITLE = "C11 Week 5 - Exercise 2 - Character with states"

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

MAX_DT = 1.0 / 30.0

BACKGROUND = (24, 24, 32)
GROUND = (140, 140, 150)
GROUND_LINE = (90, 90, 100)
COIN_PINK = (219, 39, 119)
HURT_FLASH = (255, 80, 100)
SPIKE = (200, 60, 40)
HUD_BG = (12, 12, 20)
HUD_FG = (220, 220, 230)
POWER_CYAN = (6, 182, 212)


# ----- State base class -----------------------------------------------------


class State:
    """Three lifecycle methods. Subclasses override what they need."""

    name = "state"

    def enter(self, char: "Character") -> None:
        pass

    def update(self, char: "Character", dt: float) -> None:
        pass

    def exit(self, char: "Character") -> None:
        pass


# ----- Grounded states ------------------------------------------------------


class IdleState(State):
    name = "IdleState"

    def enter(self, char: "Character") -> None:
        char.vx = 0.0

    def update(self, char: "Character", dt: float) -> None:
        # Read input -> vx.
        char.vx = char.move_input * RUN_SPEED
        # Transitions out of idle.
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

    def update(self, char: "Character", dt: float) -> None:
        char.vx = char.move_input * RUN_SPEED
        # Transitions out of run.
        if char.move_input == 0:
            char.change_state(IdleState())
            return
        if char.jump_pressed_this_frame and char.grounded:
            char.change_state(JumpState())
            return
        if not char.grounded:
            char.change_state(FallState())
            return


# ----- Airborne superstate --------------------------------------------------


class AirborneState(State):
    """Shared physics for jump and fall (and, in your stretch, wall-slide)."""

    name = "AirborneState"

    def update_airborne(self, char: "Character", dt: float) -> None:
        # Horizontal control is preserved in the air.
        char.vx = char.move_input * RUN_SPEED
        # Gravity.
        char.vy += GRAVITY * dt
        if char.vy > TERMINAL_V:
            char.vy = TERMINAL_V


class JumpState(AirborneState):
    name = "JumpState"

    def enter(self, char: "Character") -> None:
        char.vy = -JUMP_VEL
        char.grounded = False
        print("  [sfx] jump")

    def update(self, char: "Character", dt: float) -> None:
        self.update_airborne(char, dt)
        # Apex reached -> fall.
        if char.vy >= 0:
            char.change_state(FallState())
            return
        # Landed during the upward arc (cut-short jump on a low ceiling).
        if char.grounded:
            char.change_state(IdleState())
            return


class FallState(AirborneState):
    name = "FallState"

    def update(self, char: "Character", dt: float) -> None:
        self.update_airborne(char, dt)
        if char.grounded:
            char.change_state(IdleState())
            return


# ----- Hurt state -----------------------------------------------------------


class HurtState(State):
    """Triggered by walking into a spike. Brief stagger + invincibility."""

    name = "HurtState"

    def __init__(self, hit_source_x: float):
        self.hit_source_x = hit_source_x
        self.timer = HURT_DURATION

    def enter(self, char: "Character") -> None:
        # Knockback away from the source. Per-state data (timer) lives
        # on self; cross-state data (invincible) lives on char.
        knockback_dir = -1.0 if self.hit_source_x < char.x else +1.0
        char.vx = knockback_dir * HURT_KNOCKBACK_X
        char.vy = HURT_KNOCKBACK_Y
        char.grounded = False
        char.invincible = True
        print("  [sfx] hit; [vfx] flash red")

    def update(self, char: "Character", dt: float) -> None:
        # Decay knockback over time.
        char.vx *= HURT_DECAY
        char.vy += GRAVITY * dt
        if char.vy > TERMINAL_V:
            char.vy = TERMINAL_V
        self.timer -= dt
        if self.timer <= 0:
            if char.grounded:
                char.change_state(IdleState())
            else:
                char.change_state(FallState())

    def exit(self, char: "Character") -> None:
        char.invincible = False


# ----- Character ------------------------------------------------------------


@dataclass
class Character:
    x: float = 100.0
    y: float = GROUND_Y - PLAYER_H
    vx: float = 0.0
    vy: float = 0.0
    grounded: bool = True
    move_input: int = 0
    jump_pressed_this_frame: bool = False
    invincible: bool = False
    state: State = field(default_factory=IdleState)

    def __post_init__(self) -> None:
        self.state.enter(self)

    def change_state(self, new_state: State) -> None:
        print(f"[fsm] {type(self.state).__name__} "
              f"-> {type(new_state).__name__}")
        self.state.exit(self)
        self.state = new_state
        self.state.enter(self)

    def take_hit(self, hit_source_x: float) -> None:
        if self.invincible:
            return  # already hurt; ignore.
        self.change_state(HurtState(hit_source_x))

    def update(self, dt: float) -> None:
        self.state.update(self, dt)


# ----- World ---------------------------------------------------------------


@dataclass
class Spike:
    x: int
    width: int = 32
    height: int = 16

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, GROUND_Y - self.height, self.width,
                           self.height)


SPIKES = [Spike(x=360), Spike(x=540)]


def integrate_and_collide(c: Character, dt: float) -> None:
    """Pure physics; the state machine decides what physics happens."""
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
    """Apply HURT when the player touches a spike, but only if airborne
    didn't take care of it. Damage on contact, regardless of state."""
    player_rect = pygame.Rect(int(c.x), int(c.y), PLAYER_W, PLAYER_H)
    for sp in SPIKES:
        if player_rect.colliderect(sp.rect):
            c.take_hit(sp.x + sp.width / 2)
            return


# ----- Render ---------------------------------------------------------------


def draw(screen: pygame.Surface, font: pygame.font.Font, c: Character,
         fps: float, flash_t: float) -> None:
    screen.fill(BACKGROUND)
    pygame.draw.rect(screen, GROUND,
                     (0, GROUND_Y, WINDOW_W, WINDOW_H - GROUND_Y))
    pygame.draw.line(screen, GROUND_LINE,
                     (0, GROUND_Y), (WINDOW_W, GROUND_Y), 2)
    # Spikes.
    for sp in SPIKES:
        pygame.draw.rect(screen, SPIKE, sp.rect)
        # Triangle tips.
        for i in range(4):
            tx = sp.x + i * 8
            pygame.draw.polygon(screen, SPIKE, [
                (tx, GROUND_Y - sp.height),
                (tx + 4, GROUND_Y - sp.height - 6),
                (tx + 8, GROUND_Y - sp.height),
            ])
    # Player. Flash red during hurt.
    color = HURT_FLASH if (c.invincible and flash_t % 0.12 < 0.06) else COIN_PINK
    pygame.draw.rect(screen, color,
                     (int(c.x), int(c.y), PLAYER_W, PLAYER_H))
    # HUD.
    pygame.draw.rect(screen, HUD_BG, (0, 0, WINDOW_W, 28))
    label = (f"state={type(c.state).__name__:12s}  "
             f"grounded={c.grounded!s:5s}  "
             f"vx={c.vx:+7.1f}  vy={c.vy:+7.1f}  "
             f"inv={c.invincible!s:5s}  fps={fps:5.1f}")
    screen.blit(font.render(label, True, HUD_FG), (8, 6))
    screen.blit(
        font.render("[A/D + SPACE] - walk into a spike to feel HurtState",
                    True, POWER_CYAN),
        (8, WINDOW_H - 22))


# ----- Main -----------------------------------------------------------------


def main() -> int:
    pygame.init()
    pygame.display.set_caption(WINDOW_TITLE)
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 14, bold=False)

    c = Character()
    flash_t = 0.0
    running = True
    while running:
        raw_dt = clock.tick(TARGET_FPS) / 1000.0
        dt = min(raw_dt, MAX_DT)
        flash_t += dt

        c.jump_pressed_this_frame = False
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    running = False
                elif ev.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP):
                    c.jump_pressed_this_frame = True

        keys = pygame.key.get_pressed()
        left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        c.move_input = (1 if right else 0) - (1 if left else 0)

        c.update(dt)
        integrate_and_collide(c, dt)
        check_spike_hits(c)

        draw(screen, font, c, clock.get_fps(), flash_t)
        pygame.display.flip()

    pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())


# ----- HINT (do not peek for at least 20 minutes) --------------------------
#
# 1. The five classes all subclass ``State``. Each one defines as many
#    of ``enter`` / ``update`` / ``exit`` as it needs and leaves the
#    rest as the base-class no-op. The point is that the *slot* is
#    visible; you choose to fill it or not. Forgetting an exit on a
#    state that has an enter side effect is a code-review red flag.
#
# 2. ``change_state`` runs three things in order: exit(old), set the
#    new, enter(new). The order matters. Run enter before exit and the
#    new state's setup runs on a stale character; run set before exit
#    and ``self.state`` is the new state when the old's ``exit`` runs.
#
# 3. ``JumpState.enter`` sets ``vy = -JUMP_VEL``. This is the
#    canonical "side effect lives in the transition" example. Do NOT
#    set ``vy = -JUMP_VEL`` in the input handler. Do NOT set it in
#    ``RunState.update`` when the jump key is pressed. Set it where
#    the character *becomes* a jumper.
#
# 4. ``HurtState.__init__`` takes the source's x. Per-state state goes
#    on the instance: ``self.timer``. Cross-state state goes on the
#    character: ``char.invincible``. Why the split? Because
#    ``IdleState`` after-the-fact needs to know "am I still invincible
#    from a recent hit?" and ``IdleState`` can't reach into a
#    ``HurtState`` instance that has been replaced.
#
# 5. ``take_hit`` is a *method on the character*, not a transition.
#    Damage is the canonical "this can happen anywhere" event. Other
#    candidates: ``set_dead``, ``apply_pickup``. Don't proliferate
#    these; one or two is fine, ten is a smell.
#
# 6. ``check_spike_hits`` deliberately calls ``take_hit`` regardless
#    of the current state. The ``invincible`` flag on the character
#    is what prevents double-hits. The state machine prevents
#    "ill-defined transition"; the invincible flag prevents
#    "well-defined but spammed".
#
# 7. The ``AirborneState`` parent is the seed of the hierarchical FSM
#    in Lecture 2. Try adding a ``WallSlideState(AirborneState)`` that
#    halves gravity when ``char.touching_wall``. The change is one
#    class; the parent does the rest. That is what HFSMs give you.
