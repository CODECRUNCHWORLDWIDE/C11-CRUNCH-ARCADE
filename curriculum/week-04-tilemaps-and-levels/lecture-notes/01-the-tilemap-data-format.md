# Lecture 1 — The Tilemap Data Format

> **Duration:** ~2 hours of reading + hands-on.
> **Outcome:** You can describe what a tilemap *is* in five sentences, load a level from a `.csv` file in twenty lines of Python, parse a Tiled `.json` export in about eighty, and convert fluently between the four coordinate systems (tile, world, screen, grid-index).

If you only remember one thing from this lecture, remember this:

> **A level is data, not code.** The moment your level layout lives in a `.csv` or `.json` file instead of a Python literal, you can ship ten levels for the cost you used to spend on one. Editing in a spreadsheet or in Tiled is ten times faster than editing source. The engine doesn't care which level it loads — it just opens the file you point it at.

---

## 1. What is a tilemap?

A tilemap is a 2D grid of small reusable images called **tiles**. The grid is stored as a 2D array of integers. Each integer is an index into a **tileset** — the source image that contains every unique tile, laid out side-by-side. The renderer's job is small: for each cell in the grid, look up the tile at that index in the tileset, and blit it to the corresponding screen rectangle.

That's it. That's the whole abstraction. Three pieces:

1. **A tileset** — one image (`tiles.png`) of many small images.
2. **A grid** — a 2D array of indices into the tileset.
3. **A renderer** — code that walks the grid, looks up each tile, and draws it.

Almost every 2D game you have ever played that has more than one screen of content uses a variant of this idea. *Super Mario Bros.* (1985) is a tilemap with side-scrolling and gravity. *The Legend of Zelda* (1986) is a tilemap with rooms. *Stardew Valley* (2016) is a Tiled-authored tilemap with overlapping layers. *Celeste* (2018) is a hand-authored tilemap with autotiling. The technique is older than most of us and shows no signs of going away.

### Why tilemaps?

Four reasons. Memorise them — they come up in interview questions and in the quiz at the end of this week.

- **Art reuse.** A 32×32 grass tile in a tileset is 4 KB on disk. The same grass tile painted across 2000 cells of a 50×40 world is still 4 KB on disk — only the grid (2000 integers, 8 KB) gets repeated. Compared to one big 1600×1280-pixel painted background (~8 MB), the saving is roughly 1000×. On disk, in RAM, and in artist time.
- **Editor tooling.** Because the level is a grid of indices, you can build a *grid editor* — Tiled, LDtk, Ogmo, RPG Maker — that lets a non-programmer paint levels with the mouse. The editor saves a `.json`. The engine loads it. Designers ship levels without touching code.
- **Collision shortcuts.** AABB-vs-tile collision is dramatically cheaper than AABB-vs-arbitrary-polygon. To check whether a player at `(x, y)` collides with the world, you divide by `TILE_SIZE`, look up the grid cell, and check if it's solid. That's two integer divides and an array lookup. We come back to this in Week 5.
- **Memory locality.** A `list[list[int]]` grid in Python (or a flat `bytearray` for production) is laid out roughly contiguously in memory. The renderer walks it in a tight loop. The CPU prefetcher loves you. Compared to a list of `Brick` objects scattered around the Python heap, the cache hit rate is night and day. Bob Nystrom's *Game Programming Patterns* chapter on **Data Locality** spells this out for you in C++ terms; the same logic transfers to Python with smaller absolute numbers.

### When *not* to use a tilemap

Not every 2D game wants a tilemap. The trap is reaching for the tool because it's the one you have.

- **Free-form pixel-painted backgrounds.** *Hollow Knight* paints its world by hand at high resolution. Tilemaps would not help; the artistic choice is exactly the *absence* of visible grid.
- **Procedurally generated rooms with arbitrary shapes.** *Spelunky* uses *chunked* templates (4×4 cells, each cell is a hand-authored room), which is a tilemap variant — but a pure tilemap with random integers gives you incoherent walls. The chunk is the unit, not the tile.
- **Vector-based games.** Anything that scales smoothly with zoom (*Geometry Wars*, *Limbo*'s silhouettes) is not a tilemap.
- **Worlds where every cell is meaningfully different.** If you're going to hand-paint every 32×32 cell anyway, the grid abstraction stops paying for itself.

A practical rule: **if you can describe your level as "this kind of tile here, that kind there," it's a tilemap.** If you can't, it isn't.

---

## 2. The four coordinate systems (and the four conversion functions)

This is where most beginners trip. There are four coordinate systems in play at any moment, and confusing them produces bugs that look like "my player draws in the wrong place" but are actually "I forgot to subtract the camera." Name them out loud once and the bugs stop:

1. **Tile coordinate** `(col, row)` — integer position in the grid. The top-left tile is `(0, 0)`.
2. **World coordinate** `(wx, wy)` — pixel position *in the level*, *not* on screen. The world is much bigger than the screen. The top-left of the level is `(0, 0)` in world space.
3. **Screen coordinate** `(sx, sy)` — pixel position on the visible window. The top-left of the window is `(0, 0)`.
4. **Grid-flat index** `i = row * cols + col` — when you store the grid as a 1D list, you flatten with this formula. We mostly use `grid[row][col]` (2D list of lists) in this course because Python is happiest there, but real production code is usually flat for cache reasons.

The four conversions you'll write this week:

```python
TILE = 32  # pixels per tile, constant across the level

def tile_to_world(col: int, row: int) -> tuple[int, int]:
    """Tile cell to top-left world pixel."""
    return (col * TILE, row * TILE)

def world_to_tile(wx: float, wy: float) -> tuple[int, int]:
    """World pixel to the tile cell that contains it. Note the // for floor."""
    return (int(wx // TILE), int(wy // TILE))

def world_to_screen(wx: float, wy: float, cam_x: float, cam_y: float) -> tuple[int, int]:
    """Subtract the camera. This is the whole 'camera' abstraction in two lines."""
    return (int(wx - cam_x), int(wy - cam_y))

def screen_to_world(sx: float, sy: float, cam_x: float, cam_y: float) -> tuple[int, int]:
    """Add the camera. Useful for mouse clicks ('which tile did the user click?')."""
    return (int(sx + cam_x), int(sy + cam_y))
```

The four functions above are eight lines of code. They are the only thing standing between you and a working camera + tilemap. We'll re-use them in Lecture 2.

A note on integer math: tile-vs-world conversions are floor-divisions because the world is bigger than the tile and we want to know which *cell contains* the point, not which cell *exactly equals* it. `world_to_tile(35, 17)` with `TILE=32` returns `(1, 0)`, not `(1.09375, 0.53125)`. The latter is meaningless — there is no half-cell. Use `//` (floor division), not `/` (float division).

---

## 3. CSV as the minimum-viable level format

Before we touch Tiled, let's see how little file format you can get away with. The minimum-viable tilemap on disk is a CSV — comma-separated values, the format every spreadsheet exports. You can edit it in LibreOffice Calc, Excel, Google Sheets, or any text editor. There is no XML parser, no JSON parser, no SDK. Python's `csv` module is two lines.

A 12×8 level in CSV looks like this:

```csv
1,1,1,1,1,1,1,1,1,1,1,1
1,0,0,0,0,0,0,0,0,0,0,1
1,0,0,0,2,0,0,0,0,0,0,1
1,0,0,0,0,0,0,0,3,0,0,1
1,0,0,0,0,0,0,0,0,0,0,1
1,0,0,5,5,5,5,5,5,0,0,1
1,1,1,1,1,1,1,1,1,1,1,1
```

That's seven rows of twelve columns. `1` is a solid wall. `0` is empty. `2` is a coin. `3` is the player spawn. `5` is a platform. You decide the meaning. The file is *data*; the engine assigns *semantics* in code.

Loading it is twenty lines of Python:

```python
import csv

def load_csv(path: str) -> list[list[int]]:
    """Read a CSV of integers into a 2D list. Empty cells become 0."""
    grid: list[list[int]] = []
    with open(path, newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            grid.append([int(c) if c.strip() else 0 for c in row])
    # Guard: every row must have the same width. Pad or raise.
    width = max(len(r) for r in grid) if grid else 0
    for r in grid:
        while len(r) < width:
            r.append(0)
    return grid
```

You will write this loader as **Exercise 1**. It is the smallest piece of code in the entire course that demonstrates the data-vs-code separation. Once you have it, you have *levels* — and every brick-breaker, every platformer, every top-down adventure, every roguelike *Crunch Arcade* will ever build runs on a variant of it.

### When CSV is enough

CSV is enough when:

- The level has one layer (no overlapping decorative tiles).
- No tile has metadata more complex than its integer index.
- The level designer is comfortable in a spreadsheet (which is to say: most level designers are comfortable in *something*, and a spreadsheet is the universal lowest common denominator).

CSV stops being enough when:

- You want a background layer and a foreground layer that overlap.
- Tiles need metadata: "this tile is animated," "this tile is one-way," "this tile is a damage zone."
- Designers want to drop *objects* into the world — a player spawn at `(48, 12)`, an enemy at `(96, 80)` — that aren't snapped to the grid.

For the brick-breaker and a single-screen tutorial level, CSV is fine. For the Week-4 platformer, we use Tiled.

---

## 4. Tiled: the editor and its file format

[Tiled](https://www.mapeditor.org/) is a free, open-source 2D tilemap editor by **Thorbjørn Lindeijer**, who has maintained it since 2008. It is the indie-gamedev standard. *Stardew Valley*, *Shovel Knight*, *Owlboy*, *Cuphead's* 2D HUD overlays, and dozens of other shipped indies use Tiled. It runs on macOS, Windows, and Linux. It is donation-funded. If you ship a game using Tiled, throw the project a few dollars.

Install Tiled now if you haven't already. Open the application. Create a new map: 20 wide × 12 high, tile size 32×32, orthogonal orientation. Import a tileset (Kenney's *Platformer Pack Redux* is the right size if you want to follow along with a real asset; otherwise any 256×256 tileset image works). Paint a small layout — a floor, a wall, a couple of platforms. Save as `level-01.tmx`. Now export as JSON: `File → Export As → JSON map files`. Save as `level-01.json`.

Open `level-01.json` in a text editor. You will see something like:

```json
{
  "compressionlevel": -1,
  "height": 12,
  "infinite": false,
  "layers": [
    {
      "data": [0, 0, 0, ..., 1, 1, 1],
      "height": 12,
      "id": 1,
      "name": "ground",
      "opacity": 1,
      "type": "tilelayer",
      "visible": true,
      "width": 20,
      "x": 0,
      "y": 0
    }
  ],
  "nextlayerid": 2,
  "nextobjectid": 1,
  "orientation": "orthogonal",
  "renderorder": "right-down",
  "tileheight": 32,
  "tilesets": [
    {
      "firstgid": 1,
      "source": "platformer-tileset.tsx"
    }
  ],
  "tilewidth": 32,
  "type": "map",
  "version": "1.10",
  "width": 20
}
```

The fields we care about (almost everything else can be ignored at the loader level):

- `width`, `height` — the grid size in tiles.
- `tilewidth`, `tileheight` — the tile size in pixels. (Tiled supports non-square tiles; we don't this week.)
- `layers[]` — an array of layers. Each layer with `"type": "tilelayer"` has a `data` array of length `width * height` (1D, row-major). Each integer is a **GID** (global tile ID).
- `tilesets[]` — an array of tilesets. Each tileset has a `firstgid` and either a `source` (external `.tsx` file) or an inline definition.

### What is a GID?

A **GID** (global tile ID) is the integer in `data`. Two important rules:

1. **GID 0 is always empty.** No tile is drawn. Skip the cell.
2. **GIDs are globally numbered across tilesets.** If your map uses two tilesets — `terrain.png` with 64 tiles and `decorations.png` with 32 — the first tileset gets GIDs 1-64 and the second gets 65-96. The `firstgid` field tells you where each tileset starts.

To convert a GID into a *local* tile index (which tile in *which* tileset), you walk the tilesets sorted by `firstgid` and find the last tileset whose `firstgid <= gid`. Then `local_index = gid - firstgid`. We only need one tileset this week, so `local_index = gid - 1` for all non-zero GIDs.

There is a gotcha: the high three bits of the GID encode **flip flags** (horizontal flip, vertical flip, anti-diagonal flip / 90° rotation). For a first loader you can mask them off:

```python
FLIP_H = 0x80000000
FLIP_V = 0x40000000
FLIP_D = 0x20000000
GID_MASK = 0x1FFFFFFF

def parse_gid(raw_gid: int) -> tuple[int, bool, bool, bool]:
    gid = raw_gid & GID_MASK
    fh = bool(raw_gid & FLIP_H)
    fv = bool(raw_gid & FLIP_V)
    fd = bool(raw_gid & FLIP_D)
    return gid, fh, fv, fd
```

If your map has no flipped tiles, the raw integers are already in the valid GID range and the masking is a no-op. If you used the flip button in Tiled, you'll need to apply `pygame.transform.flip` when drawing.

### Layers

Tiled lets you stack multiple layers. Conventionally:

- **`background`** — non-collidable scenery (sky, distant mountains).
- **`ground`** or **`world`** — the collidable terrain.
- **`decoration`** — non-collidable foreground details that draw *over* the player (sometimes; depends on the layer's z-order).
- **`objects`** — an *object layer*, distinct from tile layers. Holds entities (player spawn, enemy positions, doors) at arbitrary pixel coordinates, not snapped to the grid.

Your engine reads each tile layer in turn and draws it in order. The first layer is drawn first (so the background ends up behind the world). Collision logic only looks at the `ground` layer (or any layer you've marked as collidable via a custom property).

### Object layers

An object layer in Tiled is a list of dictionaries, each describing one entity:

```json
{
  "name": "objects",
  "type": "objectgroup",
  "objects": [
    { "name": "player_spawn", "x": 64, "y": 384, "width": 0, "height": 0, "type": "spawn", "id": 1 },
    { "name": "goal",         "x": 576, "y": 384, "width": 32, "height": 32, "type": "goal", "id": 2 },
    { "name": "enemy_1",      "x": 320, "y": 352, "width": 32, "height": 32, "type": "enemy", "id": 3 }
  ]
}
```

You read this list and instantiate the right Python objects: a `Player` at `(64, 384)`, a `Goal` rect at `(576, 384, 32, 32)`, an `Enemy` at `(320, 352)`. The level designer has dragged these objects around in Tiled with the mouse. You did not write any of these coordinates by hand. This is the win.

---

## 5. A pure-Python Tiled JSON loader

Here is a small but complete loader for a single-tileset, no-flips Tiled map. About 80 lines including comments. You will write this as **Exercise 2** with an inline JSON string so you don't need to install Tiled to do the exercise.

```python
"""Minimal Tiled JSON loader. Pure stdlib. ~80 lines."""

import json
from dataclasses import dataclass, field

@dataclass
class TileLayer:
    name: str
    width: int
    height: int
    data: list[int]            # row-major, length == width * height

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
    width: int                 # in tiles
    height: int                # in tiles
    tile_width: int            # in pixels
    tile_height: int           # in pixels
    tile_layers: list[TileLayer] = field(default_factory=list)
    objects: list[ObjectEntry] = field(default_factory=list)
    # We don't load the tileset image here; that's the renderer's job.

def load_tiled_json(path: str) -> TiledMap:
    with open(path) as f:
        raw = json.load(f)
    m = TiledMap(
        width=raw["width"],
        height=raw["height"],
        tile_width=raw["tilewidth"],
        tile_height=raw["tileheight"],
    )
    for layer in raw["layers"]:
        if layer["type"] == "tilelayer":
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
```

That's the *whole* loader. Eighty lines including the dataclass declarations. No `pip install`. No XML. No third-party dependency. The next step — turning the GIDs into pixel rectangles on the screen — is the *renderer*, which is the subject of Lecture 2.

### Why write your own when PyTMX exists?

[PyTMX](https://github.com/bitcraft/pytmx) is excellent. It is the canonical Pygame tilemap loader. In a real production project we would import it and move on. The reason we write our own this week is pedagogical: **you cannot debug a loader you have not written.** When (not if) your Tiled map shows up rotated, mirrored, or shifted by one tile on every other Friday, the only way to fix it is to know what the file format *says* and what your code *does* with it. After this week you should feel free to switch to PyTMX. Many of you will. The course allows it from Week 5 on.

---

## 6. Putting the loader and the renderer together

Here is the skeleton of the loop. You'll see this pattern in every exercise and in the mini-project.

```python
# === Startup ===
tileset = pygame.image.load("tiles.png").convert_alpha()
TILE_W, TILE_H = 32, 32
COLS_IN_TILESET = tileset.get_width() // TILE_W
tile_surfaces: list[pygame.Surface] = []
# Slice the tileset into individual subsurfaces. GID 1 -> tile_surfaces[0], etc.
for ty in range(tileset.get_height() // TILE_H):
    for tx in range(COLS_IN_TILESET):
        rect = pygame.Rect(tx * TILE_W, ty * TILE_H, TILE_W, TILE_H)
        tile_surfaces.append(tileset.subsurface(rect))

level = load_tiled_json("level-01.json")

# === Render (per frame) ===
for layer in level.tile_layers:
    for row in range(layer.height):
        for col in range(layer.width):
            gid = layer.gid_at(col, row)
            if gid == 0:
                continue
            # No flips, single tileset, firstgid=1 assumption.
            surf = tile_surfaces[gid - 1]
            screen.blit(surf, (col * TILE_W - cam_x, row * TILE_H - cam_y))
```

This is the naive renderer. It draws *every* tile in the layer every frame. That is fine for a 12×20 single-screen tutorial map (240 tiles). It is *not* fine for a 80×24 platformer level (1920 tiles), and it is catastrophic for a 200×100 sprawling world (20,000 tiles). Lecture 2 introduces the fix: **off-screen culling**.

---

## 7. Common loader bugs (and how to find them)

You will hit at least three of these this week. Read them now so you recognise them when they bite.

- **"The map looks shifted by one tile."** You forgot that GID 0 is empty and indexed your tileset starting at 0 instead of `gid - 1`. Symptom: every tile draws the *previous* tile in your tileset.
- **"The map looks rotated 90° / mirrored."** You walked the grid in `(row, col)` order but treated it as `(x, y)` directly in pixels, swapping the axes. Always: `screen.blit(surf, (col * TILE_W, row * TILE_H))`. Col → x. Row → y. Not the other way.
- **"Half the tiles are missing."** Your level has more than one tileset and you only loaded the first. Check `tilesets[]` in the JSON — there might be a second with `firstgid=65`.
- **"Some tiles are giant or distorted."** Tile-size mismatch. You set `TILE = 32` in code, but Tiled saved the map at `tilewidth: 16`. Always read `tile_width` from the file, never hardcode it.
- **"My player draws behind the map."** Z-order bug. You drew the foreground layer before the player. Render in this order: background layers → entities → foreground layers → HUD. Always.

---

## 8. From data to game: where this week is going

Today's reading separates the level (data) from the engine (code). That is the architectural shift. From this lecture forward in the course, **levels live in files**. You will never put a level layout in a `.py` again. (You will *prototype* one in Python sometimes — that's fine. But the moment a level is real, it moves to a file.)

By the end of the week you will have:

- **Exercise 1** — a CSV-driven tilemap renderer. Twelve by twenty grid, four tile types.
- **Exercise 2** — a Tiled JSON loader that handles multiple tile layers and an object layer. Inline JSON string so you don't need to install Tiled to do the exercise.
- **Exercise 3** — a camera that follows a player around a level larger than the screen. (Lecture 2's topic.)
- **Mini-project** — a 2D platformer prototype with three loadable levels. The engine doesn't change between levels; only the data does.

Next time you sit down to design a level, you will open Tiled (or a spreadsheet), not your editor. That's the win. That's the whole point of the week.

---

## 9. Re-read checklist

Before you move to the exercises, you should be able to answer these without looking back:

1. Name the three pieces of the tilemap abstraction (tileset, grid, renderer).
2. Give the four conversion functions (tile↔world, world↔screen) from memory.
3. State what GID 0 means in Tiled.
4. Explain why `gid - 1` is the offset between GID and local tileset index (for a single tileset with `firstgid=1`).
5. Name two situations where CSV is enough and two where it isn't.
6. Recall the difference between a *tile layer* and an *object layer* in Tiled.
7. Explain why we write our own loader this week instead of using PyTMX.

If any of those are shaky, re-read the section in question before moving on. The exercises assume all seven.

---

*Next:* [Lecture 2 — Camera and Off-Screen Culling](./02-camera-and-off-screen-culling.md).
