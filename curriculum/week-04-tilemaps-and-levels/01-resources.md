# Week 4 — Resources

Every resource on this page is **free** and **publicly accessible** unless explicitly noted as "excerpts free." No paywalled books, no proprietary PDFs. If a link breaks, please open an issue.

## Required reading (work it into your week)

- **Tiled — User Manual (full).** The whole manual is short and free. Read at minimum the "Introduction," "Working with Layers," and "Object Layers" sections:
  <https://doc.mapeditor.org/en/stable/manual/introduction/>
- **Tiled — JSON Map Format reference.** This is the spec for the file you'll be parsing in Exercise 2 and the mini-project. Bookmark it:
  <https://doc.mapeditor.org/en/stable/reference/json-map-format/>
- **Tiled — TMX Map Format reference.** XML version. Useful even if you only ever export JSON, because the field names match:
  <https://doc.mapeditor.org/en/stable/reference/tmx-map-format/>
- **Pygame docs — `pygame.Rect` and `colliderect`.** You'll bounce here every hour this week:
  <https://www.pygame.org/docs/ref/rect.html>

## Robert Nystrom — *Game Programming Patterns* (free online, full book)

Bob Nystrom's book is one of the best free resources in this whole course. Every chapter is online in full at <https://gameprogrammingpatterns.com/>. The chapters relevant this week:

- **Spatial Partition** (a tilemap *is* a uniform spatial partition; read this and the lecture clicks):
  <https://gameprogrammingpatterns.com/spatial-partition.html>
- **Flyweight** (every grass tile is one `Tile` instance shared across thousands of grid cells; the pattern has a name):
  <https://gameprogrammingpatterns.com/flyweight.html>
- **Data Locality** (why a `list[list[int]]` grid is fast in Python; why nested objects can ruin you):
  <https://gameprogrammingpatterns.com/data-locality.html>
- **Update Method** (still relevant; you're updating an entity list every frame):
  <https://gameprogrammingpatterns.com/update-method.html>

## Pygame tilemap tutorials (free, code-along)

- **Christian Koch — *Pygame Tile-Based Platformer* (full series, free, on YouTube).** The cleanest free Pygame platformer tutorial that uses Tiled. Watch episodes 1-3 for tilemap loading; the rest covers Week-5-and-onward material:
  <https://www.youtube.com/results?search_query=pygame+tile+based+platformer+tutorial>
- **Clear Code — *Platformer with Pygame*** (Mr. Code-er, YouTube; free, ~2 hr total). Uses PyTMX. Watch the loader segments even if you write your own:
  <https://www.youtube.com/@ClearCode>
- **Pygame Wiki — Tile-Based Games.** Short, official, and shows the pygame-native way:
  <https://www.pygame.org/wiki/tom_games2>
- **Pygame Tutorials index.** A grab-bag, but the tile-related entries are gold:
  <https://www.pygame.org/wiki/tutorials>

## Tiled — official tutorials and example maps

- **Tiled — Getting Started.** Build your first map in ten minutes:
  <https://doc.mapeditor.org/en/stable/manual/introduction/>
- **Tiled — Tile Layer vs Object Layer.** The distinction is the single most important conceptual step in the editor:
  <https://doc.mapeditor.org/en/stable/manual/layers/>
- **Tiled — Working with Tilesets.** How to import a tileset image, set the tile-size, mark tiles with custom properties:
  <https://doc.mapeditor.org/en/stable/manual/using-the-tileset-editor/>
- **Tiled — Example Maps (GitHub).** A repo full of `.tmx` and `.json` examples to read and steal from:
  <https://github.com/mapeditor/tiled/tree/master/examples>

## Free tile assets (CC0, the ones you should actually use)

- **Kenney.nl — Tilemap packs.** Tens of CC0 tilemap packs covering platformer, top-down, dungeon, space, and city themes. This is the canonical free-asset source for indie devs and ships in countless tutorials:
  <https://kenney.nl/assets/category:Tiles>
  - Specifically: *1-Bit Pack*, *Platformer Pack Redux*, *Roguelike Pack*. Each is a single `.png` tileset of the right dimensions for Tiled.
- **OpenGameArt.org — Tilemap tag.** Mixed licenses; filter by CC0:
  <https://opengameart.org/art-search?keys=tilemap>
- **itch.io — Tilesets (free filter).** A long tail of free pixel-art tilesets, many CC0:
  <https://itch.io/game-assets/free/tag-tileset>

## Python libraries (you don't need them, but they exist)

You can complete this week using only stdlib `csv` and `json`. The libraries below are excellent and you should know they exist for later, but resist using them this week — the loader is the lecture.

- **PyTMX — Tiled loader for Pygame.** The de-facto Pygame tilemap library. Two-line loader. Use it from Week 5 onward:
  <https://github.com/bitcraft/pytmx>
- **pyscroll — scrolling Pygame tilemap renderer.** Companion to PyTMX. Handles culling and parallax for you:
  <https://github.com/bitcraft/pyscroll>
- **pygame-ce — Pygame Community Edition.** A maintained fork of Pygame with active development. If your `pip install pygame` is acting weird in 2025+, try `pip install pygame-ce`:
  <https://pyga.me/>

## Books and longer-form (free or excerpts free)

- **Robert Nystrom — *Game Programming Patterns* (free, full).** Already linked above. Read **Spatial Partition** and **Flyweight** this week:
  <https://gameprogrammingpatterns.com/>
- **Amit Patel — Red Blob Games — *Grids and Graphs*.** Amit's tutorials are the gold standard for grid-based math. Tilemaps are square grids; if you ever want hex grids (a future week, optional), Amit is where you go:
  <https://www.redblobgames.com/grids/parts/>
- **Jesse Schell — *The Art of Game Design* (chapter excerpts free).** Read the chapter on **Lens of the World** and **Lens of Space**. Both apply to level design:
  <http://www.artofgamedesign.com/>

## Talks and videos (free, on YouTube)

- **GDC — *Designing Levels for a 2D Platformer*** (search GDC Vault for "2D platformer level design"; several free talks):
  <https://www.youtube.com/@Gdconf>
- **Mark Brown — *Game Maker's Toolkit — Boss Keys*** (level structure analysis):
  <https://www.youtube.com/playlist?list=PLc38fcMFcV_s7Lf6xbeRfWYRt7-Vmi_X9>
- **Mark Brown — *Game Maker's Toolkit — Super Mario 3D World's 4 Step Level Design***. Even though this is a 3D platformer, the four-step lesson (introduce → develop → twist → conclude) maps directly to 2D tilemap levels:
  <https://www.youtube.com/watch?v=dBmIkEvEBtA>

## Official Pygame docs you'll bounce to this week

- **`pygame.Surface`** (you'll subsurface a tileset image to get individual tile surfaces):
  <https://www.pygame.org/docs/ref/surface.html>
- **`Surface.subsurface`** (zero-copy view into a parent surface — the canonical way to slice a tileset):
  <https://www.pygame.org/docs/ref/surface.html#pygame.Surface.subsurface>
- **`Surface.blit`** (you'll call this thousands of times per frame):
  <https://www.pygame.org/docs/ref/surface.html#pygame.Surface.blit>
- **`Surface.blits`** (the batched version — once you have a list of `(source, dest)` pairs, `blits` is faster than a Python loop calling `blit`):
  <https://www.pygame.org/docs/ref/surface.html#pygame.Surface.blits>
- **`pygame.Rect`** (the entire week revolves around rectangles):
  <https://www.pygame.org/docs/ref/rect.html>

## Glossary cheat sheet

Keep this open in a tab.

| Term | Plain English |
|------|---------------|
| **Tile** | A small square image (usually 16×16, 32×32, or 64×64) that gets reused across the world. |
| **Tileset** | A single image containing many tiles in a grid. The atlas. |
| **Tile index** | The integer that identifies *which* tile in a tileset (0, 1, 2, ...). |
| **Tile-size** | The pixel dimensions of one tile (e.g. `TILE = 32`). The whole world is measured in multiples of this. |
| **Grid (tilemap)** | A 2D array of tile indices. `grid[row][col] = tile_index`. |
| **GID** | Global tile ID, used by Tiled when a map has multiple tilesets. GID 0 = empty. |
| **Tile coordinate** | `(col, row)` — integer position in the grid. |
| **World coordinate** | `(x_px, y_px)` — pixel position in the level, *not* on screen. |
| **Screen coordinate** | `(sx, sy)` — pixel position on the visible window. `screen = world - camera`. |
| **Camera** | A 2D offset between world-space and screen-space. Two functions, three lines each. |
| **Dead-zone** | A rectangular window around the camera's centre; the camera moves only when the target leaves the window. |
| **Culling** | Skipping the draw of objects outside the viewport. For tilemaps, integer-math culling is `O(visible)`, not `O(total)`. |
| **Parallax** | Layers drawn with a fraction of the camera's offset, creating an illusion of depth. |
| **Tiled** | A free, open-source tilemap editor by Thorbjørn Lindeijer. The indie-gamedev standard since 2008. |
| **TMX / JSON** | The two file formats Tiled exports. TMX is XML; JSON is JSON. We parse JSON this week because Python's `json` module is one line. |

---

*If a link 404s, please [open an issue](https://github.com/CODECRUNCHWORLDWIDE) so we can replace it.*
