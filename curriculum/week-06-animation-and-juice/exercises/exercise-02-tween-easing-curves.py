"""exercise-02-tween-easing-curves.py

Goal
----
Implement ``lerp`` and five easing curves (``linear``, ``ease_in``,
``ease_out``, ``ease_in_out``, ``ease_out_back``); plot each one across
the top of the window so the *shape* of every curve is visible at a
glance; then drive five small squares left-to-right across the screen
using each of the five curves. Press R to restart.

The point of the exercise: the curves are NOT mysterious. Each one is
a one-line function applied to ``t`` before the ``lerp`` call. Once
you've drawn them on screen with your own code, you'll recognise them
in every commercial game you play. They are NOT going away.

Expected behaviour
------------------
- An 800x480 window.
- Top half of the window: five plots. Each plot shows one easing curve
  graphed from (0,0) to (1,1). A red dot rides along the curve in
  sync with the moving square below it.
- Bottom half: five Coin-Pink squares, each starting at the left edge,
  ending at the right edge. Each square is driven by a 2.5-second
  tween using its corresponding easing curve.
- The HUD shows ``t``, the global elapsed time, and the labels for
  each curve.
- Press R to restart all five tweens at once. Press ESC to quit.

What you learn
--------------
- ``lerp(a, b, t)`` — the two-line function that runs the world.
- Five easing curves, each as a one-line transform of ``t``.
- The ``Tween`` class: start, end, duration, elapsed, ease, value(),
  done().
- Reading a curve plot vs feeling the motion. Pair them.

Estimated time
--------------
About 40-50 minutes.

To complete
-----------
Read the structure top to bottom. The five easing functions are
filled in; what you'll do is read each one until you can write it
from memory (the quiz will ask). Pay attention to ``ease_out_back``
and the overshoot constant (1.70158); that is Penner's number.

Run with::

    python exercise-02-tween-easing-curves.py
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import Callable

import pygame

# ----- Configuration --------------------------------------------------------

WINDOW_W = 800
WINDOW_H = 480
TARGET_FPS = 60
WINDOW_TITLE = "C11 Week 6 - Exercise 2 - Tweens and easing curves"

MAX_DT = 1.0 / 30.0
TWEEN_DURATION = 2.5  # seconds; matches the plot's x-axis

BACKGROUND = (24, 24, 32)
PLOT_BG = (16, 16, 24)
PLOT_GRID = (50, 50, 60)
PLOT_AXIS = (110, 110, 120)
PLOT_CURVE = (240, 240, 230)
PLOT_DOT = (255, 96, 96)
COIN_PINK = (219, 39, 119)
POWER_CYAN = (6, 182, 212)
HUD_BG = (12, 12, 20)
HUD_FG = (220, 220, 230)
LABEL_FG = (200, 200, 210)


# ----- lerp + easing --------------------------------------------------------


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation. The most-used function in game code.

    ``t=0`` -> a. ``t=1`` -> b. ``t=0.5`` -> midpoint. Two lines."""
    return a + (b - a) * t


def linear(t: float) -> float:
    return t


def ease_in(t: float) -> float:
    """Quadratic ease-in. Slow start, fast end. Anticipation curve."""
    return t * t


def ease_out(t: float) -> float:
    """Quadratic ease-out. Fast start, slow end. Settling curve."""
    return 1.0 - (1.0 - t) * (1.0 - t)


def ease_in_out(t: float) -> float:
    """S-curve. Slow start, fast middle, slow end."""
    if t < 0.5:
        return 2.0 * t * t
    return 1.0 - 2.0 * (1.0 - t) * (1.0 - t)


def ease_out_back(t: float, overshoot: float = 1.70158) -> float:
    """Overshoot and settle. Used for 'pop' juice: score counters,
    button presses, coin pickups. The 1.70158 constant is Robert
    Penner's; it gives a ~10% overshoot before settling."""
    s = overshoot
    u = t - 1.0
    return u * u * ((s + 1.0) * u + s) + 1.0


# ----- Tween class ----------------------------------------------------------


@dataclass
class Tween:
    """A value, animated from ``start`` to ``end`` over ``duration``
    seconds, with an easing curve applied to ``elapsed/duration``.

    Six fields. Twelve substantive lines. Drives squash-and-stretch,
    fade-ins, slide-ins, screen-shake-with-decay, and a hundred other
    polish effects. Memorise the shape."""

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

    def t_raw(self) -> float:
        if self.duration <= 0:
            return 1.0
        return max(0.0, min(1.0, self.elapsed / self.duration))

    def value(self) -> float:
        t = self.t_raw()
        return lerp(self.start, self.end, self.ease(t))

    def done(self) -> bool:
        return self.elapsed >= self.duration


# ----- Plot widgets --------------------------------------------------------


@dataclass
class CurvePlot:
    """A small rectangular plot showing one easing curve. The plot
    samples the curve at 80 points and draws line segments between
    them. A red dot rides along the curve based on the parent tween's
    current ``t``."""

    rect: pygame.Rect
    ease: Callable[[float], float]
    label: str

    def draw(self, screen: pygame.Surface, font: pygame.font.Font,
             tween: Tween) -> None:
        # Background.
        pygame.draw.rect(screen, PLOT_BG, self.rect)
        pygame.draw.rect(screen, PLOT_AXIS, self.rect, 1)
        # Grid (4x4).
        for i in range(1, 4):
            gx = self.rect.x + i * self.rect.width // 4
            gy = self.rect.y + i * self.rect.height // 4
            pygame.draw.line(screen, PLOT_GRID,
                             (gx, self.rect.y),
                             (gx, self.rect.bottom), 1)
            pygame.draw.line(screen, PLOT_GRID,
                             (self.rect.x, gy),
                             (self.rect.right, gy), 1)
        # Curve. Note y is inverted: t=0 at bottom, t=1 at top.
        pts: list[tuple[int, int]] = []
        steps = 80
        for k in range(steps + 1):
            t = k / steps
            v = self.ease(t)
            px = self.rect.x + int(t * (self.rect.width - 1))
            py = self.rect.bottom - 1 - int(v * (self.rect.height - 1))
            pts.append((px, py))
        if len(pts) >= 2:
            pygame.draw.lines(screen, PLOT_CURVE, False, pts, 2)
        # Moving dot.
        t = tween.t_raw()
        v = self.ease(t)
        dx = self.rect.x + int(t * (self.rect.width - 1))
        dy = self.rect.bottom - 1 - int(v * (self.rect.height - 1))
        pygame.draw.circle(screen, PLOT_DOT, (dx, dy), 4)
        # Label.
        lbl = font.render(self.label, True, LABEL_FG)
        screen.blit(lbl, (self.rect.x + 2, self.rect.bottom + 2))


# ----- Moving square widgets -----------------------------------------------


@dataclass
class TweenedSquare:
    tween: Tween
    y: int
    size: int = 22
    label: str = ""


def make_squares(plot_y_bottom: int) -> list[TweenedSquare]:
    """Build the five tweened squares, one for each easing curve. Each
    square's tween animates its X position from a left margin to a
    right margin across ``TWEEN_DURATION`` seconds."""
    LEFT_MARGIN = 60
    RIGHT_MARGIN = 60
    start_x = LEFT_MARGIN
    end_x = WINDOW_W - RIGHT_MARGIN
    eases = [
        (linear,        "linear"),
        (ease_in,       "ease_in"),
        (ease_out,      "ease_out"),
        (ease_in_out,   "ease_in_out"),
        (ease_out_back, "ease_out_back"),
    ]
    squares: list[TweenedSquare] = []
    row_h = 28
    base_y = plot_y_bottom + 50
    for i, (ease, label) in enumerate(eases):
        sq = TweenedSquare(
            tween=Tween(start=float(start_x), end=float(end_x),
                        duration=TWEEN_DURATION, ease=ease),
            y=base_y + i * row_h,
            size=20,
            label=label,
        )
        squares.append(sq)
    return squares


def make_plots() -> list[CurvePlot]:
    """Build five small plots across the top of the window."""
    eases = [
        (linear,        "linear"),
        (ease_in,       "ease_in"),
        (ease_out,      "ease_out"),
        (ease_in_out,   "ease_in_out"),
        (ease_out_back, "ease_out_back"),
    ]
    plots: list[CurvePlot] = []
    plot_w = 130
    plot_h = 110
    pad = 16
    total_w = len(eases) * plot_w + (len(eases) - 1) * pad
    start_x = (WINDOW_W - total_w) // 2
    y = 40
    for i, (ease, label) in enumerate(eases):
        rect = pygame.Rect(start_x + i * (plot_w + pad), y, plot_w, plot_h)
        plots.append(CurvePlot(rect=rect, ease=ease, label=label))
    return plots


# ----- HUD ------------------------------------------------------------------


def draw_hud(screen: pygame.Surface, font: pygame.font.Font,
             t_raw: float, fps: float) -> None:
    pygame.draw.rect(screen, HUD_BG, (0, 0, WINDOW_W, 28))
    label = (f"t={t_raw:5.3f}   duration={TWEEN_DURATION:.2f} s   "
             f"fps={fps:5.1f}")
    screen.blit(font.render(label, True, HUD_FG), (8, 6))
    screen.blit(
        font.render("[R] restart all tweens   [ESC] quit",
                    True, POWER_CYAN),
        (8, WINDOW_H - 22))


# ----- Main -----------------------------------------------------------------


def main() -> int:
    pygame.init()
    pygame.display.set_caption(WINDOW_TITLE)
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 14, bold=False)
    small = pygame.font.SysFont("monospace", 12, bold=False)

    plots = make_plots()
    plot_bottom = plots[0].rect.bottom
    squares = make_squares(plot_bottom)

    running = True
    while running:
        raw_dt = clock.tick(TARGET_FPS) / 1000.0
        dt = min(raw_dt, MAX_DT)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    running = False
                elif ev.key == pygame.K_r:
                    for sq in squares:
                        sq.tween.reset()

        # Tick all tweens (they share a duration, so they advance in sync).
        for sq in squares:
            sq.tween.update(dt)

        # All tweens have the same elapsed/duration, so picking the first
        # is fine for the global t indicator.
        t_raw = squares[0].tween.t_raw()

        # --- Draw ---
        screen.fill(BACKGROUND)
        title = font.render(
            "Top: easing curve shapes. Bottom: same curves driving "
            "square motion. Press R to restart.",
            True, HUD_FG)
        screen.blit(title, (24, 16))

        # Plots.
        for i, plot in enumerate(plots):
            plot.draw(screen, small, squares[i].tween)

        # Squares.
        for sq in squares:
            x = int(sq.tween.value())
            pygame.draw.rect(screen, COIN_PINK,
                             (x, sq.y, sq.size, sq.size))
            # Track line.
            pygame.draw.line(screen, PLOT_GRID,
                             (60, sq.y + sq.size // 2),
                             (WINDOW_W - 60, sq.y + sq.size // 2), 1)
            # Label to the right of the square's track.
            lbl = small.render(sq.label, True, LABEL_FG)
            screen.blit(lbl, (WINDOW_W - 56, sq.y + 4))

        draw_hud(screen, font, t_raw, clock.get_fps())
        pygame.display.flip()

    pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())


# ----- HINT (do not peek for at least 20 minutes) --------------------------
#
# 1. ``lerp(a, b, t) = a + (b - a) * t`` is the single most-called
#    function in game code. The camera lerps toward the player. The
#    volume lerps from 0 to 1. The colour lerps from white to red on
#    a hit-flash. Memorise the two lines.
#
# 2. An easing curve is ONE function applied to ``t`` BEFORE the lerp.
#    The output is ``lerp(a, b, ease(t))``. Not ``ease(lerp(a, b, t))``.
#    Easing reshapes the parameter, not the result.
#
# 3. ``ease_in`` and ``ease_out`` are *mirror images*. ``ease_in(t)``
#    is the curve where t=0.5 maps to 0.25 (slow start). ``ease_out(t)``
#    is the curve where t=0.5 maps to 0.75 (fast start). Each is the
#    other reflected across y = 0.5.
#
# 4. ``ease_in_out`` is the *piecewise concatenation* of ``ease_in``
#    (for t<0.5) and ``ease_out`` (for t>=0.5). Sometimes called the
#    S-curve. Used for level fades and portrait swaps.
#
# 5. ``ease_out_back`` is the *overshoot*. The curve passes 1.0
#    before settling back to it. The 1.70158 constant is Robert
#    Penner's; values 1.5-2.0 are reasonable. Bigger = more overshoot.
#    Used for "pop" effects: score counters, button presses, coin
#    pickups, achievement notifications. NEVER use for character
#    motion through the world (the overshoot reads as wobble).
#
# 6. The ``Tween`` class wraps the easing-then-lerp computation in
#    six fields. Notice ``reset()`` and ``done()``: the first lets you
#    re-fire the tween on a state re-entry; the second lets a containing
#    state notice the tween finished and chain to the next effect.
#
# 7. To swap a tween's easing curve at runtime, simply assign:
#       sq.tween.ease = ease_in
#    Try this in your own playground: see what ``ease_in_out`` does
#    when you apply it to a hit-flash colour tween. (Spoiler: it looks
#    wrong; the hit-flash wants ``ease_out`` -- fast start, slow fade.)
