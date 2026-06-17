"""exercise-01-fsm-from-nested-ifs.py

Goal
----
Refactor a tangle of nested ``if`` statements into a hand-rolled FSM
with an ``Enum`` of states, an ``Enum`` of events, and a transition
table. The character is a four-state player (idle / run / jump / fall)
running across a small in-memory tile floor. No tilemap loading; the
ground is a single y-coordinate line so the lesson stays focussed on
the state machine.

The point is to feel the architectural shift in your own hands. The
"before" version is at the bottom of this file (commented out, with a
HINT block). Read it first, *then* implement the FSM at the top.

Expected behaviour
------------------
- An 800x480 window with a Coin-Pink player rectangle on a grey
  "floor" line at y = 380.
- Arrow keys (or A/D) move the player left/right. SPACE jumps.
- The HUD prints the current FSM state in the bottom-left. Walk and
  watch it change: ``idle`` -> ``run`` -> ``jump`` -> ``fall`` -> ``idle``.
- Console prints every transition with the triggering event:
  ``[fsm] idle --MOVE_PRESSED--> run``
- ESC or window-close quits cleanly.

What you learn
--------------
- The ``State`` and ``Event`` enums in 10 lines.
- The ``TRANSITIONS`` dict mapping ``(from_state, event)`` to
  ``to_state``.
- The four-phase update: collect events, decide transitions, run
  per-state behaviour, render.
- Why illegal transitions should log loudly rather than silently
  no-op.

Estimated time
--------------
About 40-50 minutes.

To complete
-----------
Fill in the ``TODO`` lines. Do not peek at the HINT block at the
bottom of this file until you've spent 20 minutes.

Run with::

    python exercise-01-fsm-from-nested-ifs.py
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from enum import Enum, auto

import pygame

# ----- Configuration --------------------------------------------------------

WINDOW_W = 800
WINDOW_H = 480
TARGET_FPS = 60
WINDOW_TITLE = "C11 Week 5 - Exercise 1 - FSM from nested ifs"

GROUND_Y = 380
PLAYER_W = 24
PLAYER_H = 32

GRAVITY = 1800.0
JUMP_VEL = 650.0
RUN_SPEED = 240.0
TERMINAL_V = 1200.0

MAX_DT = 1.0 / 30.0  # frame-stutter clamp

# Brand-ish colours. Coin Pink is the C11 mark.
BACKGROUND = (24, 24, 32)
GROUND = (140, 140, 150)
GROUND_LINE = (90, 90, 100)
COIN_PINK = (219, 39, 119)
HUD_BG = (12, 12, 20)
HUD_FG = (220, 220, 230)
POWER_CYAN = (6, 182, 212)

DEBUG_FSM = True  # print illegal transitions

# ----- The FSM --------------------------------------------------------------


class State(Enum):
    IDLE = auto()
    RUN = auto()
    JUMP = auto()
    FALL = auto()


class Event(Enum):
    MOVE_PRESSED = auto()
    MOVE_RELEASED = auto()
    JUMP_PRESSED = auto()
    LANDED = auto()
    FELL_OFF_EDGE = auto()
    APEX_REACHED = auto()


# (from_state, event) -> to_state
# Beginners often forget some of these. If a transition is missing the
# event becomes a no-op (or, with DEBUG_FSM on, a logged warning).
TRANSITIONS: dict[tuple[State, Event], State] = {
    (State.IDLE, Event.MOVE_PRESSED): State.RUN,
    (State.IDLE, Event.JUMP_PRESSED): State.JUMP,
    (State.IDLE, Event.FELL_OFF_EDGE): State.FALL,
    (State.RUN, Event.MOVE_RELEASED): State.IDLE,
    (State.RUN, Event.JUMP_PRESSED): State.JUMP,
    (State.RUN, Event.FELL_OFF_EDGE): State.FALL,
    (State.JUMP, Event.APEX_REACHED): State.FALL,
    (State.JUMP, Event.LANDED): State.IDLE,  # cut-short jump
    (State.FALL, Event.LANDED): State.IDLE,
}


# ----- Data types -----------------------------------------------------------


@dataclass
class Character:
    x: float = 100.0
    y: float = GROUND_Y - PLAYER_H
    vx: float = 0.0
    vy: float = 0.0
    state: State = State.IDLE

    grounded: bool = True
    was_grounded: bool = True

    # Input state for this frame and the previous frame.
    move_input: int = 0  # -1 left, 0 still, +1 right
    last_move_input: int = 0
    jump_pressed_this_frame: bool = False


# ----- Phase 1 — Collect events --------------------------------------------


def collect_events(c: Character) -> list[Event]:
    """Turn raw input + physics deltas into transition events."""
    events: list[Event] = []
    # Movement key edges.
    if c.move_input != 0 and c.last_move_input == 0:
        events.append(Event.MOVE_PRESSED)
    if c.move_input == 0 and c.last_move_input != 0:
        events.append(Event.MOVE_RELEASED)
    # Jump key edge.
    if c.jump_pressed_this_frame:
        events.append(Event.JUMP_PRESSED)
    # Physics-derived events.
    if c.grounded and not c.was_grounded:
        events.append(Event.LANDED)
    if not c.grounded and c.was_grounded:
        events.append(Event.FELL_OFF_EDGE)
    if c.state == State.JUMP and c.vy >= 0:
        events.append(Event.APEX_REACHED)
    return events


# ----- Phase 2 — Decide transitions ----------------------------------------


def apply_transitions(c: Character, events: list[Event]) -> None:
    """For each event, look up the transition; if found, fire it."""
    for ev in events:
        key = (c.state, ev)
        if key in TRANSITIONS:
            new_state = TRANSITIONS[key]
            print(f"[fsm] {c.state.name.lower()} "
                  f"--{ev.name}--> {new_state.name.lower()}")
            on_transition(c, c.state, new_state, ev)
            c.state = new_state
        else:
            if DEBUG_FSM:
                # Many events are legitimately ignored in their current
                # state (e.g. JUMP_PRESSED while in FALL). Mute the most
                # common ones to keep the log readable.
                if (c.state, ev) not in {
                    (State.JUMP, Event.JUMP_PRESSED),
                    (State.FALL, Event.JUMP_PRESSED),
                    (State.JUMP, Event.MOVE_PRESSED),
                    (State.JUMP, Event.MOVE_RELEASED),
                    (State.FALL, Event.MOVE_PRESSED),
                    (State.FALL, Event.MOVE_RELEASED),
                    (State.JUMP, Event.FELL_OFF_EDGE),
                    (State.FALL, Event.FELL_OFF_EDGE),
                    (State.IDLE, Event.LANDED),
                    (State.RUN, Event.LANDED),
                    (State.IDLE, Event.APEX_REACHED),
                    (State.RUN, Event.APEX_REACHED),
                    (State.FALL, Event.APEX_REACHED),
                    (State.IDLE, Event.MOVE_RELEASED),
                    (State.RUN, Event.MOVE_PRESSED),
                }:
                    print(f"[fsm] illegal: {c.state.name.lower()} "
                          f"got {ev.name}; ignored")


def on_transition(c: Character, old: State, new: State, ev: Event) -> None:
    """Side effects on transition. Sound, animation, velocity kicks."""
    if new == State.JUMP:
        c.vy = -JUMP_VEL
        c.grounded = False
        print("  [sfx] jump")
    elif new == State.IDLE and old in (State.JUMP, State.FALL):
        print("  [sfx] land")


# ----- Phase 3 — Per-state behaviour ---------------------------------------


def run_state(c: Character, dt: float) -> None:
    """Advance physics according to the current state."""
    # Horizontal velocity is input-driven in all four states.
    c.vx = c.move_input * RUN_SPEED

    # Gravity applies when airborne.
    if c.state in (State.JUMP, State.FALL):
        c.vy += GRAVITY * dt
        if c.vy > TERMINAL_V:
            c.vy = TERMINAL_V


# ----- Phase 4 — Physics and ground check ----------------------------------


def integrate_and_collide(c: Character, dt: float) -> None:
    """Apply velocity, snap to ground, update grounded flag."""
    c.was_grounded = c.grounded
    c.x += c.vx * dt
    c.y += c.vy * dt
    # Keep in window horizontally.
    c.x = max(0, min(WINDOW_W - PLAYER_W, c.x))
    # Snap to ground.
    floor_top = GROUND_Y - PLAYER_H
    if c.y >= floor_top:
        c.y = floor_top
        if c.vy > 0:
            c.vy = 0
        c.grounded = True
    else:
        c.grounded = False


# ----- Render --------------------------------------------------------------


def draw(screen: pygame.Surface, font: pygame.font.Font, c: Character,
         fps: float) -> None:
    screen.fill(BACKGROUND)
    # Ground.
    pygame.draw.rect(screen, GROUND,
                     (0, GROUND_Y, WINDOW_W, WINDOW_H - GROUND_Y))
    pygame.draw.line(screen, GROUND_LINE,
                     (0, GROUND_Y), (WINDOW_W, GROUND_Y), 2)
    # Player.
    pygame.draw.rect(screen, COIN_PINK,
                     (int(c.x), int(c.y), PLAYER_W, PLAYER_H))
    # HUD.
    pygame.draw.rect(screen, HUD_BG, (0, 0, WINDOW_W, 28))
    label = (f"state={c.state.name.lower():4s}  "
             f"grounded={c.grounded!s:5s}  "
             f"vx={c.vx:+7.1f}  vy={c.vy:+7.1f}  "
             f"fps={fps:5.1f}  "
             f"[A/D + SPACE]")
    screen.blit(font.render(label, True, HUD_FG), (8, 6))
    state_label = font.render(
        f"current state: {c.state.name}", True, POWER_CYAN)
    screen.blit(state_label, (8, WINDOW_H - 22))


# ----- Main ----------------------------------------------------------------


def main() -> int:
    pygame.init()
    pygame.display.set_caption(WINDOW_TITLE)
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 14, bold=False)

    c = Character()
    running = True
    while running:
        raw_dt = clock.tick(TARGET_FPS) / 1000.0
        dt = min(raw_dt, MAX_DT)

        c.last_move_input = c.move_input
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

        events = collect_events(c)
        apply_transitions(c, events)
        run_state(c, dt)
        integrate_and_collide(c, dt)

        draw(screen, font, c, clock.get_fps())
        pygame.display.flip()

    pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())


# ----- HINT (do not peek for at least 20 minutes) --------------------------
#
# 1. The "before" version of this character update is the tangle of
#    booleans you wrote in Week 4: ``is_jumping``, ``is_running``,
#    ``grounded``, with the ``if grounded and not is_jumping and ...``
#    cascade. Stare at it. Count the booleans. Notice how many places
#    set each one. That is the smell.
#
# 2. The FSM replaces three booleans with one ``State`` enum value.
#    Boolean combinations become unrepresentable; only one state at a
#    time is possible *by construction*.
#
# 3. The TRANSITIONS dict deliberately omits some entries — e.g.
#    ``(State.JUMP, Event.JUMP_PRESSED)``. That omission is the reason
#    you cannot double-jump. The guard is the absence of an entry,
#    not an ``if not is_jumping`` check.
#
# 4. on_transition is where side effects on entry live: setting
#    ``vy = -JUMP_VEL`` for the JUMP entry, printing a [sfx] message
#    on landing. Side effects scattered through ``run_state`` are a
#    classic state-leak bug. Keep them in transition handlers.
#
# 5. APEX_REACHED is fired by collect_events when ``state == JUMP`` and
#    ``vy >= 0`` — i.e. gravity has just won. The event then transitions
#    JUMP -> FALL. This is *one* way to model the apex; another is to
#    have FallState be triggered structurally inside the state's
#    update method (Exercise 2 does that).
#
# 6. The "log on illegal transition" pattern catches real bugs. The
#    explicit mute-set above is for *expected* drops — events that we
#    know happen often and aren't bugs. Resist the urge to mute the
#    whole log; the noise tells you when the FSM and the world have
#    drifted.
#
# 7. If you find yourself wanting a fifth state ("crouch", say), the
#    edits are mechanical: add to State, add the entry/exit events to
#    Event, add the rows to TRANSITIONS, optionally add a branch in
#    on_transition. Five edits, all in known places. Compare to the
#    nested-if version where adding crouch is "I don't even know where
#    to start."
