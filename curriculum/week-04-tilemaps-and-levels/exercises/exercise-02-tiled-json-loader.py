"""exercise-02-tiled-json-loader.py

Goal
----
Parse a Tiled-style JSON map string (no external file, no Tiled
install required) and render its layers in order. The map has a
*background* tile layer, a *world* tile layer, and an *object* layer
holding the player spawn and a goal entity.

Once this exercise runs, you have a loader that handles real Tiled
exports from this point in the course on. The only thing you'd swap
out in production is the inline string for a ``with open(path) as f:
json.load(f)`` call.

Expected behaviour
------------------
- A 800x416 window (25 cols x 13 rows of 32 px tiles, plus HUD).
- The background layer draws first (sky/dirt-coloured cells).
- The world layer draws second (walls and platforms, with collision
  semantics applied below).
- A Coin-Pink player rectangle starts at the object-layer "spawn"
  position. A Power-Up Cyan goal rectangle sits at the object-layer
  "goal" position.
- Arrow keys (or WASD) move the player one cell per keypress.
- The HUD shows the current cell and the goal cell.
- ESC or window-close quits cleanly.

What you learn
--------------
- Parsing Tiled's JSON map format with stdlib ``json``.
- The distinction between *tile layers* (data: list of GIDs) and
  *object layers* (data: list of dicts at arbitrary pixel positions).
- Handling GID 0 = empty.
- A tiny tileset abstraction: a list of pygame.Surface, GID 1 maps to
  index 0.
- Drawing layers in order so the world appears on top of the
  background.

Estimated time
--------------
About 40-50 minutes.

To complete
-----------
Fill in the ``TODO`` lines. Do not peek at the HINT block at the
bottom of this file until you've spent 15 minutes.

Run with::

    python exercise-02-tiled-json-loader.py
"""

from __future__ import annotations

import json
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
WINDOW_TITLE = "C11 Week 4 - Tiled JSON Loader"

BACKGROUND = (24, 24, 32)
COIN_PINK = (219, 39, 119)
POWER_CYAN = (6, 182, 212)
HUD_BG = (12, 12, 20)
HUD_FG = (220, 220, 230)

# Tile palette: index 0 -> GID 1, index 1 -> GID 2, etc. We synthesise the
# tileset in code so the exercise has no external asset dependencies.
TILE_PALETTE = [
    (60, 70, 95),    # 1 - sky (background)
    (52, 70, 50),    # 2 - dirt (background)
    (140, 140, 150), # 3 - stone wall (world)
    (96, 64, 36),    # 4 - dirt wall (world)
    (220, 200, 90),  # 5 - platform (world)
]


# ----- Inline Tiled JSON ----------------------------------------------------
# This is the shape Tiled exports. We keep it small for readability;
# the loader is the lesson, not the level design.

TILED_JSON = r"""
{
  "compressionlevel": -1,
  "width": 25,
  "height": 13,
  "tilewidth": 32,
  "tileheight": 32,
  "infinite": false,
  "orientation": "orthogonal",
  "renderorder": "right-down",
  "type": "map",
  "version": "1.10",
  "nextlayerid": 4,
  "nextobjectid": 4,
  "layers": [
    {
      "id": 1,
      "name": "background",
      "type": "tilelayer",
      "width": 25,
      "height": 13,
      "opacity": 1.0,
      "visible": true,
      "x": 0,
      "y": 0,
      "data": [
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,
        2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,
        2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,
        2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,
        2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2
      ]
    },
    {
      "id": 2,
      "name": "world",
      "type": "tilelayer",
      "width": 25,
      "height": 13,
      "opacity": 1.0,
      "visible": true,
      "x": 0,
      "y": 0,
      "data": [
        3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,
        3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,
        3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,
        3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,
        3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5,5,5,0,0,0,3,
        3,0,0,0,0,5,5,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,
        3,0,0,0,0,0,0,0,0,0,5,5,5,5,0,0,0,0,0,0,0,0,0,0,3,
        3,0,0,5,5,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,
        4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,
        4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,
        4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,
        4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,
        4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4
      ]
    },
    {
      "id": 3,
      "name": "objects",
      "type": "objectgroup",
      "opacity": 1.0,
      "visible": true,
      "x": 0,
      "y": 0,
      "objects": [
        { "id": 1, "name": "spawn", "type": "spawn",
          "x": 64,  "y": 224, "width": 0,  "height": 0 },
        { "id": 2, "name": "goal",  "type": "goal",
          "x": 736, "y": 224, "width": 32, "height": 32 }
      ]
    }
  ],
  "tilesets": [
    { "firstgid": 1, "name": "synthetic", "tilewidth": 32, "tileheight": 32,
      "tilecount": 5, "columns": 5 }
  ]
}
"""

# ----- Data types -----------------------------------------------------------


@dataclass
class TileLayer:
    name: str
    width: int
    height: int
    data: list[int]

    def gid_at(self, col: int, row: int) -> int:
        if not (0 <= col < self.width and 0 <= row < self.height):
            return 0
        return self.data[row * self.width + col]


@dataclass
class ObjectEntry:
    name: str
    type: str
    x: float
    y: float
    width: float
    height: float


@dataclass
class TiledMap:
    width: int
    height: int
    tile_width: int
    tile_height: int
    tile_layers: list[TileLayer] = field(default_factory=list)
    objects: list[ObjectEntry] = field(default_factory=list)

    def find_object(self, name: str) -> ObjectEntry | None:
        for o in self.objects:
            if o.name == name:
                return o
        return None


# ----- Loader ---------------------------------------------------------------

def load_tiled_from_string(text: str) -> TiledMap:
    raw = json.loads(text)
    m = TiledMap(
        width=raw["width"],
        height=raw["height"],
        tile_width=raw["tilewidth"],
        tile_height=raw["tileheight"],
    )
    for layer in raw["layers"]:
        if layer["type"] == "tilelayer":
            # TODO: append a TileLayer with the four fields.
            m.tile_layers.append(TileLayer(
                name=layer["name"],
                width=layer["width"],
                height=layer["height"],
                data=list(layer["data"]),
            ))
        elif layer["type"] == "objectgroup":
            for obj in layer["objects"]:
                m.objects.append(ObjectEntry(
                    name=obj.get("name", ""),
                    type=obj.get("type", ""),
                    x=float(obj["x"]),
                    y=float(obj["y"]),
                    width=float(obj.get("width", 0.0)),
                    height=float(obj.get("height", 0.0)),
                ))
    return m


# ----- Tileset (synthetic) --------------------------------------------------

def build_synthetic_tileset(tile_size: int, palette: list[tuple[int, int, int]]
                            ) -> list[pygame.Surface]:
    """Make one solid-colour surface per palette entry.

    In a real Tiled project, this is replaced with
    ``pygame.image.load("tileset.png")`` and a row of ``subsurface``
    slices, one per tile. The data flow is identical.
    """
    surfs: list[pygame.Surface] = []
    for colour in palette:
        s = pygame.Surface((tile_size, tile_size))
        s.fill(colour)
        # A thin darker border helps you see the grid.
        darker = tuple(max(0, c - 30) for c in colour)
        pygame.draw.rect(s, darker, s.get_rect(), 1)
        surfs.append(s)
    return surfs


# ----- Rendering ------------------------------------------------------------

def draw_layer(screen: pygame.Surface, layer: TileLayer,
               tile_surfaces: list[pygame.Surface], tile_size: int) -> None:
    """Naive walker. No camera, no culling - this exercise stays on
    one screen so the inner loop is simple. Exercise 3 adds both."""
    for row in range(layer.height):
        base = row * layer.width
        for col in range(layer.width):
            gid = layer.data[base + col]
            if gid == 0:
                continue
            # gid - 1 because GID 1 is the first tile (firstgid=1).
            surf = tile_surfaces[gid - 1]
            screen.blit(surf, (col * tile_size, row * tile_size))


# ----- Game logic -----------------------------------------------------------

def is_solid(world_layer: TileLayer, col: int, row: int) -> bool:
    """In this exercise, every non-zero tile in the 'world' layer is solid."""
    return world_layer.gid_at(col, row) != 0


def try_move(world_layer: TileLayer, col: int, row: int,
             dc: int, dr: int) -> tuple[int, int]:
    new_c, new_r = col + dc, row + dr
    if is_solid(world_layer, new_c, new_r):
        return col, row
    return new_c, new_r


def draw_hud(screen: pygame.Surface, font: pygame.font.Font,
             player_col: int, player_row: int,
             goal_col: int, goal_row: int, won: bool) -> None:
    pygame.draw.rect(screen, HUD_BG, (0, ROWS * TILE, WINDOW_W, HUD_HEIGHT))
    state = "WIN" if won else "playing"
    label = (f"player=({player_col:2d},{player_row:2d})   "
             f"goal=({goal_col:2d},{goal_row:2d})   "
             f"state={state}   "
             f"arrows/WASD, R reset, ESC quit")
    text = font.render(label, True, HUD_FG)
    screen.blit(text, (8, ROWS * TILE + 8))


# ----- Main -----------------------------------------------------------------

def main() -> int:
    pygame.init()
    pygame.display.set_caption(WINDOW_TITLE)
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 14, bold=False)

    tile_surfaces = build_synthetic_tileset(TILE, TILE_PALETTE)
    tmap = load_tiled_from_string(TILED_JSON)

    # Tile layers by name for clarity.
    layers_by_name = {ly.name: ly for ly in tmap.tile_layers}
    background = layers_by_name["background"]
    world = layers_by_name["world"]

    # Pull player spawn and goal from the object layer.
    spawn_obj = tmap.find_object("spawn")
    goal_obj = tmap.find_object("goal")
    assert spawn_obj is not None and goal_obj is not None, "level needs spawn+goal"

    def cell_from_object(obj: ObjectEntry) -> tuple[int, int]:
        return (int(obj.x // TILE), int(obj.y // TILE))

    initial_col, initial_row = cell_from_object(spawn_obj)
    goal_col, goal_row = cell_from_object(goal_obj)

    player_col, player_row = initial_col, initial_row
    won = False

    running = True
    while running:
        clock.tick(TARGET_FPS)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    running = False
                elif ev.key == pygame.K_r:
                    player_col, player_row = initial_col, initial_row
                    won = False
                elif not won:
                    if ev.key in (pygame.K_UP, pygame.K_w):
                        player_col, player_row = try_move(world, player_col, player_row, 0, -1)
                    elif ev.key in (pygame.K_DOWN, pygame.K_s):
                        player_col, player_row = try_move(world, player_col, player_row, 0, 1)
                    elif ev.key in (pygame.K_LEFT, pygame.K_a):
                        player_col, player_row = try_move(world, player_col, player_row, -1, 0)
                    elif ev.key in (pygame.K_RIGHT, pygame.K_d):
                        player_col, player_row = try_move(world, player_col, player_row, 1, 0)

        if (player_col, player_row) == (goal_col, goal_row):
            won = True

        screen.fill(BACKGROUND)
        # Background first, then world. Painter's algorithm.
        draw_layer(screen, background, tile_surfaces, TILE)
        draw_layer(screen, world, tile_surfaces, TILE)

        # Goal indicator overlay (the goal lives in the object layer, not the grid).
        gx, gy = goal_col * TILE, goal_row * TILE
        pygame.draw.rect(screen, POWER_CYAN, (gx + 4, gy + 4, TILE - 8, TILE - 8), 3)

        # Player.
        px, py = player_col * TILE, player_row * TILE
        pygame.draw.rect(screen, COIN_PINK,
                         (px + 4, py + 4, TILE - 8, TILE - 8))

        draw_hud(screen, font, player_col, player_row,
                 goal_col, goal_row, won)
        pygame.display.flip()

    pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())


# ----- HINT (do not peek for at least 15 minutes) ---------------------------
#
# 1. json.loads is the stdlib one-liner. Tiled exports are valid JSON; you
#    do not need to install Tiled to do this exercise. The inline string at
#    the top of this file IS a real Tiled JSON shape.
#
# 2. Tile layers and object layers live in the same "layers" array. Branch
#    on layer["type"]: "tilelayer" vs "objectgroup".
#
# 3. The "data" array is 1D, row-major. To index, use data[row * width + col].
#    GID 0 means empty.
#
# 4. "gid - 1" converts a GID into a tileset index, *assuming* firstgid=1
#    and exactly one tileset. Both are true in this exercise. In Exercise 3
#    and the mini-project we keep that assumption; the homework relaxes it.
#
# 5. The object layer spawn/goal positions are in *pixels*, not tile cells.
#    To get the cell, integer-divide by TILE.
#
# 6. If your background draws on TOP of the world, you flipped the draw
#    order. Background first, world second. Always.
