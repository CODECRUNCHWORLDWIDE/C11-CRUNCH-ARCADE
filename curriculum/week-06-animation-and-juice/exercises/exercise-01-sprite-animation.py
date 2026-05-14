"""exercise-01-sprite-animation.py

Goal
----
Build a ``SpriteSheet`` loader and an ``Animation`` class from scratch
and drive a small character through three clips: idle (looping), run
(looping, faster), and jump-launch (one-shot, with the ``finished``
flag visible on screen).

Because this is a teaching exercise and we do NOT want to require any
asset downloads, the "sprite sheet" is *procedurally generated* in
code: a 4x3 grid of 32x32 cells, drawn at startup, that imitates a
real Kenney sheet. Each row is a clip; each cell is a frame. The
geometric shapes change shape per frame so you can SEE the animation
advance: idle = a slow breathing circle; run = a marching square with
two leg poses; jump = a rising shape that gets taller per frame.

When you finish the exercise, swapping the procedural sheet for an
actual Kenney sprite sheet is a one-line change to ``load_sheet``.
The architectural commitment is what you build here.

Expected behaviour
------------------
- An 800x480 window with a dark background.
- A 32x32 procedurally-generated sprite sheet is rendered at the top.
- Below it, a Coin-Pink "character" plays the idle clip. Press SPACE
  to switch to the run clip; press J to play jump-launch (one-shot).
- The HUD shows the current clip name, frame index, elapsed seconds,
  and whether the clip is ``finished``. The HUD updates within one
  frame of any state change.
- Console prints every clip change: ``[anim] play(idle_breathing)``.
- ESC quits.

What you learn
--------------
- The ``SpriteSheet`` wrapper (surface + frame_w + frame_h + cols).
- ``Surface.subsurface(rect)`` returning a no-copy view.
- The ``Animation`` class: a list of frame indices, fps, loop flag,
  elapsed_t. ``current_frame()`` returns the right surface every call.
- Frame-rate-independent playback: ``int(elapsed_t * fps)`` not
  ``frame_count += 1``.
- The ``Animator`` library: a dict of clips, ``play(name)``
  idempotency, and the ``restart`` flag for one-shots.
- The ``finished`` flag on ``loop=False`` clips and what to do with it.

Estimated time
--------------
About 45-55 minutes.

To complete
-----------
Read the structure top-to-bottom. The classes are filled in; what
you'll spend time on is the HUD, the procedural sheet generator, and
tuning the clip FPS values until the animation reads well. The HINT
block at the bottom has nudges; don't peek for the first 20 minutes.

Run with::

    python exercise-01-sprite-animation.py
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
WINDOW_TITLE = "C11 Week 6 - Exercise 1 - Sprite-sheet animation"

CELL_W = 32
CELL_H = 32
COLS = 4
ROWS = 3

MAX_DT = 1.0 / 30.0

BACKGROUND = (24, 24, 32)
GROUND = (140, 140, 150)
COIN_PINK = (219, 39, 119)
HUD_BG = (12, 12, 20)
HUD_FG = (220, 220, 230)
POWER_CYAN = (6, 182, 212)
SHEET_FRAME = (90, 90, 100)
SHEET_HIGHLIGHT = (240, 240, 80)


# ----- SpriteSheet ----------------------------------------------------------


@dataclass
class SpriteSheet:
    """A wrapper over a Pygame surface organised as a grid of frames.

    The implementation is a single ``subsurface`` call per ``frame(i)``.
    Subsurface does NOT copy pixels; it returns a view into the parent
    surface. Memory: zero per frame. Time: ~2 microseconds per call on
    a typical machine.
    """

    surface: pygame.Surface
    frame_w: int
    frame_h: int

    @property
    def cols(self) -> int:
        return self.surface.get_width() // self.frame_w

    @property
    def rows(self) -> int:
        return self.surface.get_height() // self.frame_h

    def frame(self, index: int) -> pygame.Surface:
        col = index % self.cols
        row = index // self.cols
        rect = pygame.Rect(col * self.frame_w, row * self.frame_h,
                           self.frame_w, self.frame_h)
        return self.surface.subsurface(rect)


# ----- Animation ------------------------------------------------------------


@dataclass
class Animation:
    """A clip = list of frame indices + fps + loop flag.

    ``elapsed_t`` is in seconds. The current frame is
    ``int(elapsed_t * fps) % len(frames)`` for looping clips, or
    ``min(int(elapsed_t * fps), len(frames) - 1)`` for one-shot clips.
    Frame-rate-independent in two lines.
    """

    sheet: SpriteSheet
    frames: list[int]
    fps: float = 12.0
    loop: bool = True
    elapsed_t: float = 0.0
    finished: bool = False

    def reset(self) -> None:
        self.elapsed_t = 0.0
        self.finished = False

    def update(self, dt: float) -> None:
        if self.finished:
            return
        self.elapsed_t += dt
        if not self.loop:
            total = len(self.frames) / self.fps
            if self.elapsed_t >= total:
                self.elapsed_t = total
                self.finished = True

    def current_index(self) -> int:
        i = int(self.elapsed_t * self.fps)
        if self.loop:
            return i % len(self.frames)
        return min(i, len(self.frames) - 1)

    def current_frame(self) -> pygame.Surface:
        return self.sheet.frame(self.frames[self.current_index()])


# ----- Animator (the library + current clip) -------------------------------


@dataclass
class Animator:
    """A character's animation library plus its current clip reference.

    ``play(name)`` is idempotent: calling it every frame from
    ``RunState.update`` is fine because the same-clip case early-outs.
    The ``restart`` flag forces a reset for one-shots that should
    re-fire from frame 0 (e.g. two jumps in quick succession).
    """

    library: dict[str, Animation]
    current: Optional[Animation] = None
    current_name: str = ""

    def play(self, name: str, restart: bool = False) -> None:
        clip = self.library.get(name)
        if clip is None:
            print(f"[anim] missing clip: {name}")
            return
        if clip is self.current and not restart:
            return  # already playing; don't reset
        print(f"[anim] play({name})")
        self.current = clip
        self.current_name = name
        clip.reset()

    def stop(self) -> None:
        self.current = None
        self.current_name = ""

    def update(self, dt: float) -> None:
        if self.current is not None:
            self.current.update(dt)

    def current_frame(self) -> Optional[pygame.Surface]:
        if self.current is None:
            return None
        return self.current.current_frame()


# ----- Procedural sprite-sheet generator ------------------------------------


def make_procedural_sheet() -> pygame.Surface:
    """Build a 128x96 sprite sheet (4 cols x 3 rows of 32x32 cells)
    procedurally so the exercise doesn't depend on an asset file.

    Row 0: idle. A slow breathing circle (radius 8 -> 10 -> 12 -> 10).
    Row 1: run.  A marching square with two leg poses, alternating.
    Row 2: jump. A rising shape, taller per frame; last frame extra-tall.
    """
    w = CELL_W * COLS
    h = CELL_H * ROWS
    surface = pygame.Surface((w, h), pygame.SRCALPHA)
    surface.fill((0, 0, 0, 0))

    # Row 0 — idle breathing. Four frames of slowly-pulsing circle.
    radii = [8, 10, 12, 10]
    for i, r in enumerate(radii):
        cx = i * CELL_W + CELL_W // 2
        cy = CELL_H // 2
        pygame.draw.circle(surface, COIN_PINK, (cx, cy), r)
        pygame.draw.circle(surface, (255, 255, 255), (cx - 2, cy - 2), 2)

    # Row 1 — run. Four frames: a square body with two leg poses, alternating.
    for i in range(4):
        cx = i * CELL_W + CELL_W // 2
        cy = CELL_H + CELL_H // 2 - 2
        body = pygame.Rect(cx - 8, cy - 12, 16, 16)
        pygame.draw.rect(surface, COIN_PINK, body)
        pygame.draw.rect(surface, (255, 255, 255), (cx - 6, cy - 10, 3, 3))
        # Legs alternate: even frames lean left, odd frames lean right.
        if i % 2 == 0:
            pygame.draw.rect(surface, (160, 30, 90), (cx - 7, cy + 4, 5, 8))
            pygame.draw.rect(surface, (160, 30, 90), (cx + 2, cy + 4, 5, 4))
        else:
            pygame.draw.rect(surface, (160, 30, 90), (cx - 7, cy + 4, 5, 4))
            pygame.draw.rect(surface, (160, 30, 90), (cx + 2, cy + 4, 5, 8))

    # Row 2 — jump-launch one-shot. Four frames of an increasingly tall shape.
    heights = [14, 18, 22, 26]
    for i, body_h in enumerate(heights):
        cx = i * CELL_W + CELL_W // 2
        cy = 2 * CELL_H + CELL_H - 4  # feet at bottom of cell
        body = pygame.Rect(cx - 7, cy - body_h, 14, body_h)
        pygame.draw.rect(surface, COIN_PINK, body)
        pygame.draw.rect(surface, (255, 255, 255), (cx - 5, cy - body_h + 2,
                                                    3, 3))

    return surface


def draw_sheet_preview(screen: pygame.Surface, sheet: SpriteSheet,
                       anim: Animator) -> None:
    """Draw the sprite sheet at the top of the window with the current
    frame highlighted. Useful so the student can SEE which cell is
    playing."""
    sheet_w = sheet.frame_w * sheet.cols
    sheet_h = sheet.frame_h * sheet.rows
    ox = (WINDOW_W - sheet_w * 2) // 2
    oy = 40
    # Scale the sheet 2x so it's readable.
    scaled = pygame.transform.scale(sheet.surface,
                                    (sheet_w * 2, sheet_h * 2))
    screen.blit(scaled, (ox, oy))
    # Frame outlines.
    for i in range(sheet.cols * sheet.rows):
        col = i % sheet.cols
        row = i // sheet.cols
        rect = pygame.Rect(ox + col * sheet.frame_w * 2,
                           oy + row * sheet.frame_h * 2,
                           sheet.frame_w * 2, sheet.frame_h * 2)
        pygame.draw.rect(screen, SHEET_FRAME, rect, 1)
    # Highlight the active frame.
    if anim.current is not None:
        idx = anim.current.frames[anim.current.current_index()]
        col = idx % sheet.cols
        row = idx // sheet.cols
        rect = pygame.Rect(ox + col * sheet.frame_w * 2,
                           oy + row * sheet.frame_h * 2,
                           sheet.frame_w * 2, sheet.frame_h * 2)
        pygame.draw.rect(screen, SHEET_HIGHLIGHT, rect, 3)


# ----- HUD ------------------------------------------------------------------


def draw_hud(screen: pygame.Surface, font: pygame.font.Font,
             anim: Animator, fps: float) -> None:
    pygame.draw.rect(screen, HUD_BG, (0, 0, WINDOW_W, 28))
    if anim.current is not None:
        clip = anim.current
        label = (
            f"clip={anim.current_name:14s}  "
            f"frame={clip.current_index():2d}/{len(clip.frames) - 1:<2d}  "
            f"elapsed={clip.elapsed_t * 1000:6.1f} ms  "
            f"loop={clip.loop!s:5s}  finished={clip.finished!s:5s}  "
            f"fps={fps:5.1f}"
        )
    else:
        label = "clip=<none>"
    screen.blit(font.render(label, True, HUD_FG), (8, 6))
    screen.blit(
        font.render(
            "[SPACE] toggle idle/run  [J] play jump-launch (one-shot)"
            "  [ESC] quit",
            True, POWER_CYAN),
        (8, WINDOW_H - 22))


# ----- Main -----------------------------------------------------------------


def main() -> int:
    pygame.init()
    pygame.display.set_caption(WINDOW_TITLE)
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 14, bold=False)

    # Build the procedural sheet. Note that ``convert_alpha()`` is called
    # AFTER ``set_mode``; the display must exist for the conversion to
    # know its target pixel format.
    raw_sheet = make_procedural_sheet().convert_alpha()
    sheet = SpriteSheet(surface=raw_sheet, frame_w=CELL_W, frame_h=CELL_H)

    # The animation library. Three clips, indexed into the procedural
    # sheet's 4-column grid. Row 0 (frames 0-3) is idle; row 1
    # (frames 4-7) is run; row 2 (frames 8-11) is jump-launch one-shot.
    library = {
        "idle_breathing": Animation(sheet=sheet, frames=[0, 1, 2, 3],
                                    fps=6.0, loop=True),
        "run_loop":       Animation(sheet=sheet, frames=[4, 5, 6, 7],
                                    fps=14.0, loop=True),
        "jump_launch":    Animation(sheet=sheet, frames=[8, 9, 10, 11],
                                    fps=18.0, loop=False),
    }
    anim = Animator(library=library)
    anim.play("idle_breathing")

    # Character draw position (a single "character" shown below the sheet).
    char_x = WINDOW_W // 2 - CELL_W
    char_y = WINDOW_H - 120
    char_scale = 4  # 4x upscale so the 32x32 character reads big

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
                elif ev.key == pygame.K_SPACE:
                    if anim.current_name == "idle_breathing":
                        anim.play("run_loop")
                    else:
                        anim.play("idle_breathing")
                elif ev.key == pygame.K_j:
                    # Always restart so two quick presses re-fire the clip
                    # from frame 0.
                    anim.play("jump_launch", restart=True)

        # Tick the current clip.
        anim.update(dt)

        # When jump-launch finishes, fall back to idle. This is the
        # "one-shot finished -> next clip" pattern from Lecture 1 sec. 8.
        if (anim.current_name == "jump_launch"
                and anim.current is not None
                and anim.current.finished):
            anim.play("idle_breathing")

        # --- Draw ---
        screen.fill(BACKGROUND)
        # Title.
        title = font.render(
            "Sprite-sheet preview (active frame highlighted yellow):",
            True, HUD_FG)
        screen.blit(title, (40, 16))
        draw_sheet_preview(screen, sheet, anim)
        # Character.
        frame = anim.current_frame()
        if frame is not None:
            big = pygame.transform.scale(
                frame, (CELL_W * char_scale, CELL_H * char_scale))
            screen.blit(big, (char_x, char_y - CELL_H * char_scale))
        # Floor reference.
        pygame.draw.line(screen, GROUND, (0, char_y), (WINDOW_W, char_y), 2)

        draw_hud(screen, font, anim, clock.get_fps())
        pygame.display.flip()

    pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())


# ----- HINT (do not peek for at least 20 minutes) --------------------------
#
# 1. The single most common bug in this exercise is forgetting to call
#    ``.convert_alpha()`` on the surface after building it. Without it,
#    every blit composites slowly. Symptom: the FPS HUD shows 60 but
#    the *perceived* motion stutters. Always convert.
#
# 2. The display MUST exist before ``.convert_alpha()`` is called. If
#    you reorder ``set_mode`` and ``make_procedural_sheet`` you will
#    silently get a slower path. Always init display first.
#
# 3. ``play(name)`` is idempotent on purpose. If you find yourself
#    writing ``if anim.current_name != "run_loop": anim.play("run_loop")``
#    in your FSM, delete the ``if``. The library handles the no-op.
#
# 4. The ``restart=True`` flag is for one-shot clips that should re-fire
#    from frame 0 on every entry, even if they "already played." Two
#    quick jumps in a row need this; the second jump should NOT pick up
#    where the first one's clip left off.
#
# 5. The ``finished`` flag is the signal a one-shot clip is done. The
#    code above watches ``jump_launch.finished`` to swap back to idle.
#    In Lecture 1 sec. 8 we wired the same trick to ``JumpState.update``:
#    when ``jump_launch`` finishes, swap to ``jump_airborne`` (no FSM
#    transition; just an animation library change).
#
# 6. The frame-index math is ``int(elapsed_t * fps)``. NOT
#    ``elapsed_t * fps`` (gives a float, not a frame). NOT
#    ``frame_count += 1`` (ties animation to render rate; breaks on a
#    monitor running at 144 fps or a laptop dropping to 30).
#
# 7. To swap the procedural sheet for a real Kenney sheet, replace
#    the ``make_procedural_sheet()`` call with:
#
#        raw_sheet = pygame.image.load("kenney_platformer.png")
#        raw_sheet = raw_sheet.convert_alpha()
#
#    and update ``CELL_W`` / ``CELL_H`` to the sheet's cell size. The
#    rest of the file is unchanged. That is the architectural payoff
#    of building the loader from scratch.
