"""exercise-03-camera-follow.py

Goal
----
A level bigger than the screen, a player you can drive around with the
arrow keys, and a camera that follows them. The camera supports three
follow modes you can switch between live:

  - SNAP  (1) - instant centring on the player
  - LERP  (2) - smooth follow with frame-rate-independent damping
  - DEAD  (3) - dead-zone follow (camera only moves when the player
                exits a central window)

The camera also clamps to the level bounds so you never see past the
edge of the world. Off-screen tiles are culled with integer math, not
``Rect.colliderect``, so a 60x30 tile level draws in well under a
millisecond even on a slow laptop.

Expected behaviour
------------------
- A 960x540 window. The level is 60 cols x 30 rows of 32 px tiles
  (1920 x 960 pixels) - twice as wide as the window and roughly twice
  as tall, so the camera has somewhere to scroll.
- Arrow keys / WASD move the player continuously (px/s, dt-correct).
- Number keys 1/2/3 switch follow modes. The current mode is shown in
  the HUD.
- The camera never reveals the area past the level's edges (clamped).
- Holding SHIFT triples the player speed so you can see the camera
  catch up under stress.
- ESC or window-close quits cleanly.

What you learn
--------------
- The two-line camera (world_to_screen = world - cam).
- Three follow modes side-by-side; the visceral difference between snap
  and lerp.
- The frame-rate-independent lerp factor: ``1 - 0.001 ** (dt * speed)``.
- Clamping to level bounds (one line per axis).
- Integer-math off-screen culling: from O(n_tiles) to O(visible_tiles).
- A dead-zone implementation in fifteen lines.

Estimated time
--------------
About 45-55 minutes.

To complete
-----------
Fill in the ``TODO`` lines. Do not peek at the HINT block at the
bottom of this file until you've spent 20 minutes.

Run with::

    python exercise-03-camera-follow.py
"""

from __future__ import annotations

import math
import random
import sys
from dataclasses import dataclass

import pygame

# ----- Configuration --------------------------------------------------------

TILE = 32
LEVEL_COLS = 60
LEVEL_ROWS = 30
WINDOW_W = 960
WINDOW_H = 540
HUD_HEIGHT = 28
TARGET_FPS = 60
WINDOW_TITLE = "C11 Week 4 - Camera Follow"

BACKGROUND = (24, 24, 32)
WALL = (140, 140, 150)
WALL_EDGE = (90, 90, 100)
DOT = (60, 60, 75)
COIN_PINK = (219, 39, 119)
POWER_CYAN = (6, 182, 212)
HUD_BG = (12, 12, 20)
HUD_FG = (220, 220, 230)
DEADZONE_LINE = (180, 60, 120)

# Player physics (px/s).
PLAYER_SPEED = 240.0
PLAYER_SPRINT_MULT = 3.0

# Camera follow tuning.
LERP_SPEED = 6.0  # higher = catches up faster
DEAD_ZONE_W = 240
DEAD_ZONE_H = 140

MODE_SNAP = "snap"
MODE_LERP = "lerp"
MODE_DEAD = "dead-zone"

MAX_DT = 1.0 / 30.0  # frame-stutter clamp; never integrate over 33 ms


# ----- Level generation -----------------------------------------------------

def build_demo_grid(cols: int, rows: int, seed: int = 1) -> list[list[int]]:
    """Make a deterministic demo level: a perimeter wall plus pillars and
    a few horizontal platforms. Pure integer values; no Tiled needed."""
    random.seed(seed)
    grid = [[0 for _ in range(cols)] for _ in range(rows)]
    for c in range(cols):
        grid[0][c] = 1
        grid[rows - 1][c] = 1
    for r in range(rows):
        grid[r][0] = 1
        grid[r][cols - 1] = 1
    # A couple of horizontal platforms at varying heights.
    for r_band in (6, 12, 18, 24):
        for c in range(2 + (r_band % 5), cols - 2, 7):
            for w in range(min(5, cols - c - 1)):
                grid[r_band][c + w] = 1
    # A handful of standalone pillars to disambiguate camera direction.
    for _ in range(40):
        c = random.randint(3, cols - 4)
        r = random.randint(3, rows - 4)
        if grid[r][c] == 0:
            grid[r][c] = 1
    return grid


# ----- Camera ---------------------------------------------------------------

@dataclass
class Camera:
    x: float = 0.0
    y: float = 0.0
    viewport_w: int = WINDOW_W
    viewport_h: int = WINDOW_H

    def world_to_screen(self, wx: float, wy: float) -> tuple[int, int]:
        return (int(wx - self.x), int(wy - self.y))


def follow_snap(cam: Camera, target_x: float, target_y: float) -> None:
    cam.x = target_x - cam.viewport_w / 2
    cam.y = target_y - cam.viewport_h / 2


def follow_lerp(cam: Camera, target_x: float, target_y: float,
                dt: float, speed: float = LERP_SPEED) -> None:
    desired_x = target_x - cam.viewport_w / 2
    desired_y = target_y - cam.viewport_h / 2
    # Frame-rate-independent lerp: at speed=6, the camera covers ~6 units
    # of "remaining distance per second."
    t = 1.0 - pow(0.001, max(0.0, dt) * speed)
    cam.x += (desired_x - cam.x) * t
    cam.y += (desired_y - cam.y) * t


def follow_dead_zone(cam: Camera, target_x: float, target_y: float,
                     dz_w: int = DEAD_ZONE_W, dz_h: int = DEAD_ZONE_H) -> None:
    cx = cam.viewport_w / 2
    cy = cam.viewport_h / 2
    tx = target_x - cam.x
    ty = target_y - cam.y
    left = cx - dz_w / 2
    right = cx + dz_w / 2
    top = cy - dz_h / 2
    bottom = cy + dz_h / 2
    if tx < left:
        cam.x += tx - left
    if tx > right:
        cam.x += tx - right
    if ty < top:
        cam.y += ty - top
    if ty > bottom:
        cam.y += ty - bottom


def clamp_camera_to_bounds(cam: Camera, level_w: int, level_h: int) -> None:
    cam.x = max(0.0, min(cam.x, max(0, level_w - cam.viewport_w)))
    cam.y = max(0.0, min(cam.y, max(0, level_h - cam.viewport_h)))


# ----- Off-screen culling ---------------------------------------------------

def visible_tile_range(cam: Camera, tile_size: int,
                       grid_w: int, grid_h: int) -> tuple[int, int, int, int]:
    """Compute the inclusive-exclusive grid range visible in the viewport.

    Four int() casts. Two max/min calls each axis. Total cost: about
    1 microsecond. No per-tile work. This is the cull."""
    c0 = max(0, int(cam.x) // tile_size)
    r0 = max(0, int(cam.y) // tile_size)
    c1 = min(grid_w, (int(cam.x) + cam.viewport_w) // tile_size + 1)
    r1 = min(grid_h, (int(cam.y) + cam.viewport_h) // tile_size + 1)
    return (c0, c1, r0, r1)


# ----- Rendering ------------------------------------------------------------

def draw_grid(screen: pygame.Surface, grid: list[list[int]],
              cam: Camera, tile_size: int) -> int:
    """Draw the world-layer tiles. Returns the count of drawn tiles for
    the on-screen HUD (so you can see culling in action)."""
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    c0, c1, r0, r1 = visible_tile_range(cam, tile_size, cols, rows)
    drawn = 0
    for row in range(r0, r1):
        row_data = grid[row]
        wy = row * tile_size - int(cam.y)
        for col in range(c0, c1):
            t = row_data[col]
            if t == 0:
                # Faint dot per empty cell so you can see scrolling clearly.
                wx = col * tile_size - int(cam.x)
                pygame.draw.rect(screen, DOT,
                                 (wx + tile_size // 2 - 1,
                                  wy + tile_size // 2 - 1,
                                  2, 2))
                continue
            wx = col * tile_size - int(cam.x)
            pygame.draw.rect(screen, WALL, (wx, wy, tile_size, tile_size))
            pygame.draw.rect(screen, WALL_EDGE, (wx, wy, tile_size, tile_size), 1)
            drawn += 1
    return drawn


def draw_dead_zone(screen: pygame.Surface, cam: Camera) -> None:
    cx = cam.viewport_w // 2
    cy = cam.viewport_h // 2
    pygame.draw.rect(screen, DEADZONE_LINE,
                     (cx - DEAD_ZONE_W // 2, cy - DEAD_ZONE_H // 2,
                      DEAD_ZONE_W, DEAD_ZONE_H), 1)


def draw_player(screen: pygame.Surface, cam: Camera,
                px: float, py: float, size: int) -> None:
    sx, sy = cam.world_to_screen(px, py)
    pygame.draw.rect(screen, COIN_PINK, (sx, sy, size, size))


def draw_hud(screen: pygame.Surface, font: pygame.font.Font,
             mode: str, drawn: int, total: int,
             px: float, py: float, cam: Camera, fps: float) -> None:
    y = WINDOW_H - HUD_HEIGHT
    pygame.draw.rect(screen, HUD_BG, (0, y, WINDOW_W, HUD_HEIGHT))
    label = (f"mode={mode:<9s}  "
             f"player=({int(px):4d},{int(py):4d})  "
             f"cam=({int(cam.x):4d},{int(cam.y):4d})  "
             f"drawn/total={drawn}/{total}  "
             f"fps={fps:5.1f}   1/2/3 mode  SHIFT sprint  ESC quit")
    text = font.render(label, True, HUD_FG)
    screen.blit(text, (8, y + 6))


# ----- Main -----------------------------------------------------------------

def main() -> int:
    pygame.init()
    pygame.display.set_caption(WINDOW_TITLE)
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 13, bold=False)

    grid = build_demo_grid(LEVEL_COLS, LEVEL_ROWS)
    level_w = LEVEL_COLS * TILE
    level_h = LEVEL_ROWS * TILE
    total_tiles = sum(1 for row in grid for v in row if v != 0)

    # Start the player near the level centre, in an empty cell.
    px, py = (3 * TILE) + 4, (3 * TILE) + 4
    player_size = TILE - 8

    cam = Camera(viewport_w=WINDOW_W, viewport_h=WINDOW_H - HUD_HEIGHT)
    follow_snap(cam, px + player_size / 2, py + player_size / 2)
    clamp_camera_to_bounds(cam, level_w, level_h)

    mode = MODE_LERP
    running = True

    while running:
        dt = clock.tick(TARGET_FPS) / 1000.0
        if dt > MAX_DT:
            dt = MAX_DT

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    running = False
                elif ev.key == pygame.K_1:
                    mode = MODE_SNAP
                elif ev.key == pygame.K_2:
                    mode = MODE_LERP
                elif ev.key == pygame.K_3:
                    mode = MODE_DEAD

        keys = pygame.key.get_pressed()
        speed = PLAYER_SPEED
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            speed *= PLAYER_SPRINT_MULT
        vx = vy = 0.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            vx -= 1.0
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            vx += 1.0
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            vy -= 1.0
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            vy += 1.0
        if vx or vy:
            mag = math.hypot(vx, vy)
            vx, vy = vx / mag, vy / mag
        px += vx * speed * dt
        py += vy * speed * dt
        # Constrain the player to the level bounds. Simple, not collision.
        px = max(0.0, min(px, level_w - player_size))
        py = max(0.0, min(py, level_h - player_size))

        # Camera follow: pass the player's centre.
        target_x = px + player_size / 2
        target_y = py + player_size / 2
        if mode == MODE_SNAP:
            follow_snap(cam, target_x, target_y)
        elif mode == MODE_LERP:
            follow_lerp(cam, target_x, target_y, dt)
        else:
            follow_dead_zone(cam, target_x, target_y)
        clamp_camera_to_bounds(cam, level_w, level_h)

        # Render. Background fill restricted to the playfield (above HUD).
        screen.fill(BACKGROUND)
        playfield = pygame.Rect(0, 0, WINDOW_W, WINDOW_H - HUD_HEIGHT)
        screen.set_clip(playfield)

        drawn = draw_grid(screen, grid, cam, TILE)
        draw_player(screen, cam, px, py, player_size)

        # Visual aid: in dead-zone mode, draw the dead-zone rectangle.
        if mode == MODE_DEAD:
            draw_dead_zone(screen, cam)

        screen.set_clip(None)

        fps = clock.get_fps()
        draw_hud(screen, font, mode, drawn, total_tiles, px, py, cam, fps)
        pygame.display.flip()

    pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())


# ----- HINT (do not peek for at least 20 minutes) ---------------------------
#
# 1. Camera is two floats. world_to_screen subtracts. Screen is always
#    relative to (0, 0). The world is bigger than the screen; the camera
#    is the offset.
#
# 2. The lerp factor "1 - 0.001 ** (dt * speed)" is dt-correct. The naive
#    "cam.x += (desired - cam.x) * 0.1" is NOT - it ties the follow speed
#    to the frame rate, so the camera feels different at 30, 60, and 144
#    fps. Always use the dt-correct version once you understand it.
#
# 3. Dead-zone is "snap, but only if the target is outside the window."
#    Read each axis independently. The four-if version above is the
#    cleanest; one if per edge.
#
# 4. Clamp AFTER follow. Order matters. Follow first, then clamp. If you
#    clamp before, the lerp will fight the clamp and you'll see jitter.
#
# 5. Culling is integer math, not Rect.colliderect. Compute (c0, c1, r0,
#    r1) once from the camera position. Iterate range(r0, r1) and
#    range(c0, c1). Never visit a cell outside that range.
#
# 6. If the player drifts off-screen after a SHIFT sprint, your follow
#    speed is too low - the camera can't catch up. That's fine for snap
#    (no lag possible) and dead-zone (which "snaps" the offset to keep
#    the player in the window), but lerp will visibly lag. Crank
#    LERP_SPEED to 12 if you want a tighter feel.
