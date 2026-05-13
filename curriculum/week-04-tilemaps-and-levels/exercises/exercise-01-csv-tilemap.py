"""exercise-01-csv-tilemap.py

Goal
----
Load a 12x20 tilemap from a CSV string, render it to a Pygame window,
and step a small player rectangle around with the arrow keys. No
external files are required - the CSV is embedded as a string so the
exercise stands alone.

The point is to feel the "data, not code" architectural shift in your
own hands. The level is a CSV. The engine is a Pygame loop. They are
separable. Change the CSV; the engine doesn't change.

Expected behaviour
------------------
- An 800x416 window (25 cols x 13 rows of 32 px tiles, plus a HUD row).
- The level is drawn from a CSV string at the top of the file. Tile
  meanings:
      0 = empty (background colour)
      1 = solid wall (gray)
      2 = coin (yellow)
      3 = player spawn (rendered as background; the player draws on top)
      4 = goal (Power-Up Cyan)
- A 24x24 Coin-Pink player rectangle starts at the cell marked 3.
- Arrow keys (or WASD) move the player one cell at a time per keypress.
  This is a stepped move, not a continuous one - we are not doing
  collisions yet, we are doing data loading.
- The HUD shows the current cell (col, row) in the bottom row.
- ESC or window-close quits cleanly.

What you learn
--------------
- Parsing a CSV with the stdlib ``csv`` module.
- The four coordinate conversions (tile <-> world, world <-> screen).
- A simple grid-walker render loop.
- Why we keep the player as a separate entity, not a tile in the grid.

Estimated time
--------------
About 30-40 minutes.

To complete
-----------
Fill in the ``TODO`` lines. Do not peek at the HINT block at the bottom
of this file until you've spent 15 minutes.

Run with::

    python exercise-01-csv-tilemap.py
"""

from __future__ import annotations

import csv
import io
import sys
from dataclasses import dataclass, field

import pygame

# ----- Configuration --------------------------------------------------------

TILE = 32
COLS = 25
ROWS = 13
HUD_HEIGHT = 32
WINDOW_W = TILE * COLS
WINDOW_H = TILE * ROWS + HUD_HEIGHT
TARGET_FPS = 60
WINDOW_TITLE = "C11 Week 4 - CSV Tilemap"

# Brand-ish colours. Coin Pink (#DB2777) is the C11 mark.
BACKGROUND = (24, 24, 32)
GRID_LINE = (40, 40, 52)
WALL = (140, 140, 150)
COIN = (252, 211, 77)
GOAL = (6, 182, 212)
COIN_PINK = (219, 39, 119)
HUD_BG = (12, 12, 20)
HUD_FG = (220, 220, 230)

# ----- Level data (CSV) -----------------------------------------------------
# Tile meanings: 0 empty, 1 wall, 2 coin, 3 spawn, 4 goal.
# 25 cols x 13 rows. Edit freely; the engine doesn't care.

LEVEL_CSV = """\
1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1
1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1
1,0,3,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,1
1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,4,1
1,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1
1,0,0,0,2,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,1
1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1
1,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,1
1,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,2,0,1
1,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,1
1,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1
1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1
1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1
"""

EMPTY = 0
WALL_T = 1
COIN_T = 2
SPAWN_T = 3
GOAL_T = 4


# ----- Data types -----------------------------------------------------------

@dataclass
class TileMap:
    grid: list[list[int]] = field(default_factory=list)

    @property
    def cols(self) -> int:
        return len(self.grid[0]) if self.grid else 0

    @property
    def rows(self) -> int:
        return len(self.grid)

    def tile_at(self, col: int, row: int) -> int:
        if not (0 <= col < self.cols and 0 <= row < self.rows):
            return WALL_T  # off-grid behaves as solid
        return self.grid[row][col]

    def find_first(self, value: int) -> tuple[int, int] | None:
        for r, row in enumerate(self.grid):
            for c, v in enumerate(row):
                if v == value:
                    return (c, r)
        return None


# ----- Loaders --------------------------------------------------------------

def load_csv_from_string(text: str) -> TileMap:
    """Parse a CSV blob into a TileMap. Empty cells become 0."""
    grid: list[list[int]] = []
    reader = csv.reader(io.StringIO(text))
    for row in reader:
        if not row:
            continue
        # TODO: convert each cell to int (or 0 if blank), append the row.
        # HINT: list comprehension with int(c.strip() or 0).
        parsed = [int(c.strip()) if c.strip() else 0 for c in row]
        grid.append(parsed)
    # Pad ragged rows so every row has the same width.
    if grid:
        width = max(len(r) for r in grid)
        for r in grid:
            while len(r) < width:
                r.append(EMPTY)
    return TileMap(grid=grid)


# ----- Coordinate conversions ----------------------------------------------

def tile_to_world(col: int, row: int) -> tuple[int, int]:
    return (col * TILE, row * TILE)


def world_to_tile(wx: float, wy: float) -> tuple[int, int]:
    return (int(wx // TILE), int(wy // TILE))


# ----- Rendering ------------------------------------------------------------

def draw_tilemap(screen: pygame.Surface, tm: TileMap) -> None:
    for row in range(tm.rows):
        for col in range(tm.cols):
            t = tm.tile_at(col, row)
            x, y = tile_to_world(col, row)
            if t == WALL_T:
                pygame.draw.rect(screen, WALL, (x, y, TILE, TILE))
            elif t == COIN_T:
                pygame.draw.circle(screen, COIN,
                                   (x + TILE // 2, y + TILE // 2), TILE // 4)
            elif t == GOAL_T:
                pygame.draw.rect(screen, GOAL, (x, y, TILE, TILE))
            # SPAWN_T and EMPTY: nothing to draw.
            # Light grid line for visibility.
            pygame.draw.rect(screen, GRID_LINE, (x, y, TILE, TILE), 1)


def draw_player(screen: pygame.Surface, player_col: int, player_row: int) -> None:
    x, y = tile_to_world(player_col, player_row)
    pad = 4
    pygame.draw.rect(
        screen, COIN_PINK,
        (x + pad, y + pad, TILE - 2 * pad, TILE - 2 * pad),
    )


def draw_hud(screen: pygame.Surface, font: pygame.font.Font,
             player_col: int, player_row: int, coins: int) -> None:
    pygame.draw.rect(screen, HUD_BG, (0, ROWS * TILE, WINDOW_W, HUD_HEIGHT))
    label = (f"cell=({player_col:2d},{player_row:2d})   "
             f"coins={coins}   "
             f"keys: arrows/WASD to move, R to reset, ESC to quit")
    text = font.render(label, True, HUD_FG)
    screen.blit(text, (8, ROWS * TILE + 8))


# ----- Game logic -----------------------------------------------------------

def try_move(tm: TileMap, col: int, row: int, dc: int, dr: int) -> tuple[int, int]:
    """Step one cell if the destination isn't a wall. Otherwise stay put."""
    new_c, new_r = col + dc, row + dr
    if tm.tile_at(new_c, new_r) == WALL_T:
        return col, row
    return new_c, new_r


def collect_coin(tm: TileMap, col: int, row: int) -> bool:
    if tm.tile_at(col, row) == COIN_T:
        tm.grid[row][col] = EMPTY
        return True
    return False


# ----- Main -----------------------------------------------------------------

def main() -> int:
    pygame.init()
    pygame.display.set_caption(WINDOW_TITLE)
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 16, bold=False)

    tm_original = load_csv_from_string(LEVEL_CSV)
    tm = TileMap(grid=[row[:] for row in tm_original.grid])  # working copy

    spawn = tm.find_first(SPAWN_T) or (1, 1)
    player_col, player_row = spawn
    coins = 0

    running = True
    while running:
        clock.tick(TARGET_FPS)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    running = False
                elif ev.key in (pygame.K_UP, pygame.K_w):
                    player_col, player_row = try_move(tm, player_col, player_row, 0, -1)
                elif ev.key in (pygame.K_DOWN, pygame.K_s):
                    player_col, player_row = try_move(tm, player_col, player_row, 0, 1)
                elif ev.key in (pygame.K_LEFT, pygame.K_a):
                    player_col, player_row = try_move(tm, player_col, player_row, -1, 0)
                elif ev.key in (pygame.K_RIGHT, pygame.K_d):
                    player_col, player_row = try_move(tm, player_col, player_row, 1, 0)
                elif ev.key == pygame.K_r:
                    tm = TileMap(grid=[row[:] for row in tm_original.grid])
                    spawn = tm.find_first(SPAWN_T) or (1, 1)
                    player_col, player_row = spawn
                    coins = 0

        if collect_coin(tm, player_col, player_row):
            coins += 1

        screen.fill(BACKGROUND)
        draw_tilemap(screen, tm)
        draw_player(screen, player_col, player_row)
        draw_hud(screen, font, player_col, player_row, coins)
        pygame.display.flip()

    pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())


# ----- HINT (do not peek for at least 15 minutes) ---------------------------
#
# 1. The CSV parser fits in five lines because csv.reader handles all the
#    splitting and quoting. Your inner loop is just int conversion.
#
# 2. The grid is grid[row][col]. Easy mistake: writing grid[col][row]. If
#    your map looks rotated 90 degrees, you swapped them.
#
# 3. try_move returns the same (col, row) when the destination is a wall.
#    A no-op move is normal; do not raise.
#
# 4. coin collection mutates the working copy of the grid. That is fine
#    here because we keep tm_original separate for reset. In Week 5 we
#    will separate "static collision layer" from "collectible objects" so
#    we do not have to mutate the grid at all.
#
# 5. If the player rectangle draws under the walls instead of on top,
#    your render order is wrong. Draw the tilemap first, then the player.
