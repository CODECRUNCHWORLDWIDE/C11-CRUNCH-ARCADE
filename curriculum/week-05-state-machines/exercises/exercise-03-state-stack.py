"""exercise-03-state-stack.py

Goal
----
Implement a pushdown automaton — a state machine with a *stack* of
states instead of a single current state — and use it to drive
top-level game flow: a title screen, a gameplay state, and a pause
overlay. The pause is a *push*; the unpause is a *pop*. The gameplay
state is *suspended*, not replaced; when we pop the pause, gameplay
resumes with its exact prior values (player position, vx, vy).

This is the right shape for any state that *overlays* rather than
*replaces*: pause menus, dialog boxes, options screens, "stunned"
status effects. Each one is a push; the underlying state is
preserved.

Expected behaviour
------------------
- An 800x480 window.
- The game starts on a Title screen ("CRUNCH ARCADE - press ENTER").
  Pressing ENTER pushes a Gameplay state on top.
- In Gameplay, a Coin-Pink square bounces off the window edges with
  a constant velocity. Pressing ESC pushes a Pause state on top.
- In Pause, gameplay freezes (the square stops moving), a dimmed
  overlay is drawn, and "PAUSED - ESC to resume, Q to quit" is shown.
- Pressing ESC pops Pause and gameplay resumes from the *exact frame*
  it was paused on. Pressing Q in Pause pops twice and returns to
  Title.
- From Title, pressing Q quits the program.
- The HUD shows the stack as a comma-separated list:
  ``stack: title``  ->  ``stack: title, gameplay``  ->
  ``stack: title, gameplay, pause``.

What you learn
--------------
- The pushdown automaton: a list of states with push / pop / change.
- Why pause is a *push*, not a transition.
- The "only the top state updates" rule (and the option to update
  beneath-states for things like background animation).
- The "every state draws, bottom-to-top" rule for overlays.
- How a few-line stack on top of the State pattern unlocks a category
  of behaviour that flat FSMs handle awkwardly.

Estimated time
--------------
About 40-50 minutes.

To complete
-----------
Fill in the ``TODO`` lines. Do not peek at the HINT block at the
bottom until you've spent 20 minutes.

Run with::

    python exercise-03-state-stack.py
"""

from __future__ import annotations

import sys
from dataclasses import dataclass

import pygame

# ----- Configuration --------------------------------------------------------

WINDOW_W = 800
WINDOW_H = 480
TARGET_FPS = 60
WINDOW_TITLE = "C11 Week 5 - Exercise 3 - State stack"

MAX_DT = 1.0 / 30.0

BACKGROUND = (24, 24, 32)
COIN_PINK = (219, 39, 119)
POWER_CYAN = (6, 182, 212)
TITLE_FG = (240, 240, 250)
HUD_BG = (12, 12, 20)
HUD_FG = (220, 220, 230)
DIM = (0, 0, 0, 160)


# ----- The state stack ------------------------------------------------------


class GameState:
    """Base class for every state on the stack.

    Subclasses override:
      - ``enter(app)`` once on push
      - ``update(app, dt)`` every frame while on top
      - ``draw(app, screen)`` every frame, regardless of stack position
      - ``exit(app)`` once on pop
      - ``handle_event(app, ev)`` for pygame events while on top
    """

    name = "state"

    def enter(self, app: "App") -> None:
        pass

    def update(self, app: "App", dt: float) -> None:
        pass

    def draw(self, app: "App", screen: pygame.Surface) -> None:
        pass

    def exit(self, app: "App") -> None:
        pass

    def handle_event(self, app: "App", ev: pygame.event.Event) -> None:
        pass


class App:
    """The owner of the stack and shared resources.

    The shared-resource fields (e.g. ``square_x``) are deliberate.
    A pushed Pause state doesn't *destroy* gameplay; it suspends it.
    The square keeps its position because the position lives on App,
    not inside GameplayState's instance.
    """

    def __init__(self):
        self.stack: list[GameState] = []
        self.running: bool = True
        # Shared gameplay world. The Pause state freezes by not
        # advancing this; the Gameplay state advances it on update.
        self.square_x: float = WINDOW_W // 2
        self.square_y: float = WINDOW_H // 2
        self.square_vx: float = 220.0
        self.square_vy: float = 160.0
        self.square_size: int = 40

    # --- Stack operations ---

    def push(self, state: GameState) -> None:
        print(f"[stack] push {type(state).__name__}")
        self.stack.append(state)
        state.enter(self)

    def pop(self) -> None:
        if not self.stack:
            return
        top = self.stack.pop()
        print(f"[stack] pop  {type(top).__name__}")
        top.exit(self)

    def change(self, state: GameState) -> None:
        """Replace the top of the stack."""
        if self.stack:
            top = self.stack.pop()
            print(f"[stack] change: pop {type(top).__name__}")
            top.exit(self)
        self.push(state)

    def stack_summary(self) -> str:
        return ", ".join(type(s).__name__ for s in self.stack)


# ----- Concrete states ------------------------------------------------------


class TitleState(GameState):
    name = "title"

    def enter(self, app: App) -> None:
        # Title is also responsible for *initialising* the gameplay
        # world to a known state. When the user starts a new game, the
        # square always starts at the centre with the canonical speed.
        app.square_x = WINDOW_W // 2
        app.square_y = WINDOW_H // 2
        app.square_vx = 220.0
        app.square_vy = 160.0

    def update(self, app: App, dt: float) -> None:
        pass  # title has no per-frame state

    def draw(self, app: App, screen: pygame.Surface) -> None:
        screen.fill(BACKGROUND)
        font_big = pygame.font.SysFont("monospace", 36, bold=True)
        font_small = pygame.font.SysFont("monospace", 16)
        title = font_big.render("CRUNCH ARCADE", True, COIN_PINK)
        screen.blit(title, title.get_rect(center=(WINDOW_W // 2, 180)))
        sub = font_small.render(
            "ENTER to play   |   Q to quit", True, POWER_CYAN)
        screen.blit(sub, sub.get_rect(center=(WINDOW_W // 2, 240)))

    def handle_event(self, app: App, ev: pygame.event.Event) -> None:
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_RETURN:
                app.push(GameplayState())
            elif ev.key in (pygame.K_q, pygame.K_ESCAPE):
                app.running = False


class GameplayState(GameState):
    name = "gameplay"

    def update(self, app: App, dt: float) -> None:
        # Move the square.
        app.square_x += app.square_vx * dt
        app.square_y += app.square_vy * dt
        # Bounce off walls.
        if app.square_x <= 0:
            app.square_x = 0
            app.square_vx = abs(app.square_vx)
        if app.square_x + app.square_size >= WINDOW_W:
            app.square_x = WINDOW_W - app.square_size
            app.square_vx = -abs(app.square_vx)
        if app.square_y <= 0:
            app.square_y = 0
            app.square_vy = abs(app.square_vy)
        if app.square_y + app.square_size >= WINDOW_H:
            app.square_y = WINDOW_H - app.square_size
            app.square_vy = -abs(app.square_vy)

    def draw(self, app: App, screen: pygame.Surface) -> None:
        screen.fill(BACKGROUND)
        pygame.draw.rect(screen, COIN_PINK, (
            int(app.square_x), int(app.square_y),
            app.square_size, app.square_size))
        font = pygame.font.SysFont("monospace", 14)
        screen.blit(
            font.render("ESC to pause", True, POWER_CYAN), (8, 6))

    def handle_event(self, app: App, ev: pygame.event.Event) -> None:
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                # Pause is a *push*, not a transition. Gameplay is
                # suspended and will resume on the pop.
                app.push(PauseState())


class PauseState(GameState):
    """Overlay state. The state beneath us continues to draw, but does
    NOT update (the convention: only the top state updates, every state
    draws). The result: the square is visible-but-frozen behind the
    pause overlay."""

    name = "pause"

    def draw(self, app: App, screen: pygame.Surface) -> None:
        # Dim the screen.
        overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        overlay.fill(DIM)
        screen.blit(overlay, (0, 0))
        # Text.
        font_big = pygame.font.SysFont("monospace", 36, bold=True)
        font_small = pygame.font.SysFont("monospace", 16)
        title = font_big.render("PAUSED", True, TITLE_FG)
        screen.blit(title, title.get_rect(center=(WINDOW_W // 2, 200)))
        sub = font_small.render(
            "ESC to resume   |   Q to quit to title",
            True, POWER_CYAN)
        screen.blit(sub, sub.get_rect(center=(WINDOW_W // 2, 260)))

    def handle_event(self, app: App, ev: pygame.event.Event) -> None:
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                # Pop pause; gameplay resumes from the suspended frame.
                app.pop()
            elif ev.key == pygame.K_q:
                # Pop pause AND gameplay; back to title.
                app.pop()
                app.pop()


# ----- Render the whole stack ----------------------------------------------


def draw_stack(app: App, screen: pygame.Surface,
               font: pygame.font.Font) -> None:
    # Every state draws, bottom-to-top.
    for state in app.stack:
        state.draw(app, screen)
    # Stack HUD at the bottom.
    pygame.draw.rect(screen, HUD_BG, (0, WINDOW_H - 22, WINDOW_W, 22))
    label = f"stack: {app.stack_summary()}"
    screen.blit(font.render(label, True, HUD_FG), (8, WINDOW_H - 18))


# ----- Main -----------------------------------------------------------------


def main() -> int:
    pygame.init()
    pygame.display.set_caption(WINDOW_TITLE)
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    clock = pygame.time.Clock()
    hud_font = pygame.font.SysFont("monospace", 12)

    app = App()
    app.push(TitleState())

    while app.running and app.stack:
        raw_dt = clock.tick(TARGET_FPS) / 1000.0
        dt = min(raw_dt, MAX_DT)

        # Events go to the top of the stack only.
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                app.running = False
            else:
                if app.stack:
                    app.stack[-1].handle_event(app, ev)

        # Only the top of the stack updates (the "frozen beneath" rule).
        if app.stack:
            app.stack[-1].update(app, dt)

        draw_stack(app, screen, hud_font)
        pygame.display.flip()

    pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())


# ----- HINT (do not peek for at least 20 minutes) --------------------------
#
# 1. The single most important convention in this exercise: *only the
#    top of the stack updates; every state on the stack draws.* That
#    pair of rules is what makes pause-overlay-on-gameplay work. The
#    gameplay state is *still on the stack* when pause is pushed; it
#    just doesn't get its ``update`` call until pause is popped.
#
# 2. The square's position lives on ``App``, not on ``GameplayState``.
#    Why? So that when ``GameplayState`` is suspended (a pause is
#    pushed on top), the position is preserved. If it lived on the
#    instance, you'd have to keep the instance alive — which we do
#    here on the stack, so it would work — but pinning shared state
#    to the App makes the suspension semantics obvious. Per-state
#    data on the instance; world data on the App.
#
# 3. ``app.push(PauseState())`` does NOT call ``GameplayState.exit``.
#    That is the whole point. Pause is a *suspension*. ``exit`` only
#    fires on ``pop``. ``enter`` fires on every ``push``.
#
# 4. ``app.change(SomeState())`` is the classic FSM transition —
#    pop + push as one move. It IS calling exit/enter. Use it for
#    actual state changes (level-complete -> next-level); use push/pop
#    for overlays (gameplay -> pause).
#
# 5. The "every state draws bottom-to-top" rule lets pause overlay
#    the live gameplay frame. Without it, ``PauseState.draw`` would
#    have to take a screenshot of gameplay first. With it, pause
#    simply doesn't ``screen.fill`` — gameplay's draw left the
#    background in place — and then paints its dimmer + text on top.
#
# 6. Pressing Q in pause calls ``app.pop()`` twice — once for
#    pause, once for gameplay. After both pops, the stack is
#    ``[TitleState]`` again. This is the cleanest way to express
#    "abort the current run and return to a parent state."
#
# 7. The TitleState's ``enter`` *initialises* the gameplay world.
#    That is the "entering title resets the run" semantic. Move it
#    into ``GameplayState.enter`` if you want gameplay to always
#    start fresh; leave it in ``TitleState.enter`` if you want
#    pausing-and-resuming to preserve square position (which is what
#    we want here).
