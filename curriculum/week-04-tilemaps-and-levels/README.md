# Week 4 — Tilemaps and Levels

You shipped a juiced brick-breaker last week. The simulation is correct. The hits land. The particles spit. The screen shakes in the right amount. Run it now and notice something: the brick layout is still hardcoded in a Python list. If you want a second level, you copy-paste the list, edit the numbers by hand, and pray you didn't typo the width. If you want a *third*, you do it again. By level five your `main.py` is 800 lines of literal grid data and you have stopped wanting to design new levels — the friction has eaten the desire.

This week we fix that. We separate **what the level is** (data) from **what the game does** (code). The brick layout becomes a `.csv` you can edit in any spreadsheet. The platformer layout becomes a `.tmx` or `.json` you can edit in [Tiled](https://www.mapeditor.org/), a free GUI tilemap editor used in real shipped indie games (*Stardew Valley*, *Shovel Knight*, *Owlboy*). Once levels are files, adding a new one is *renaming a file*, not editing source.

Then we deal with the second problem you don't have yet but are about to: levels are bigger than the screen. The brick-breaker fit on one screen because we designed it to. A platformer doesn't. The level is 80 tiles wide, the screen is 25 tiles wide, and you need a **camera** that follows the player and shows the right slice of the world. We build one, and we make it efficient — only the tiles inside the viewport get drawn. This is **off-screen culling**, and on a 32×32 tile world it is the difference between a 60 fps platformer and a 6 fps slideshow.

By end-of-week you ship a **2D platformer prototype with three loadable levels** that you can switch between at the press of a key. The level files are `.csv` (and optionally `.tmx`). The camera follows the player. Tiles outside the viewport never reach the GPU. The same engine loads all three levels because the engine and the data have been separated.

There is still no Godot. We are deepening the Pygame foundation. Godot's tilemap nodes will feel obvious in Week 9 because you wrote one yourself in Week 4.

## Learning objectives

By the end of this week, you will be able to:

- **Explain** why tilemaps are the standard 2D level representation (memory, editor tooling, collision shortcuts, art-reuse) and when *not* to use them (Vlambeer's *Nuclear Throne* style chunked free-form layouts).
- **Load** a 2D level from a `.csv` file: parse the integers, build a grid, draw tile indices to the correct screen cells.
- **Load** a 2D level from a Tiled-exported `.tmx` or `.json` file: parse the layers, the tileset metadata, and any object-layer entities (player spawn, enemies, doors).
- **Implement** a camera that follows a target with a clamp-to-bounds, with optional dead-zone and lerp smoothing.
- **Cull** off-screen tiles using only the viewport rectangle and integer math — no per-tile `Rect.colliderect` calls.
- **Reason** about the frame budget: how many tiles can you draw at 60 fps in pure Pygame (~8000-12000 on a modern laptop without batching), why a culled draw of ~600 tiles is free.
- **Design** a level in Tiled, export it, and load it in your engine in under five minutes once the loader is written.
- **Ship** a 2D platformer prototype with three loadable levels selectable from a level-select screen.

## Prerequisites

This week assumes you have completed **Weeks 1, 2, and 3**. Specifically:

- You have a Week 3 juiced brick-breaker repo and you can run it.
- You can write a Pygame main loop from memory, use `pygame.Vector2`, and `dt`-correct movement.
- You wrote at least one AABB collision routine in Week 2 and you understand why `colliderect` is symmetric and `colliderect` against a moving body is not the same as `move_and_collide`.
- You are comfortable with Python's `csv` and `json` modules. If `with open(path) as f: json.load(f)` is not obvious, do the Python warm-up before continuing.

If any of those are shaky, do the previous week's mini-project before continuing.

## Topics covered

Lecture 1 — The tilemap data format:

- Why tilemaps exist: art reuse, memory, editor tooling, collision shortcuts.
- The grid abstraction: tile-size, tile-index, world-position, screen-position, and the four functions that convert between them.
- CSV as the minimum-viable level format. When it's enough, when it isn't.
- The Tiled `.tmx` (XML) and `.json` formats: layers, tilesets, object layers, GIDs, properties.
- Loading order and gotchas: GID 0 means empty; GIDs are global across all tilesets; flipped/rotated bits live in the top of the GID.
- A pure-Python loader for Tiled JSON in ~80 lines. No PyTMX dependency.

Lecture 2 — Camera and off-screen culling:

- The camera as a 2D offset: world-space minus camera-space equals screen-space. Two functions, three lines each.
- Follow modes: snap, lerp (smooth follow), and dead-zone (camera moves only when the player exits a window).
- Clamping the camera to the level bounds so the player never sees outside the world.
- Off-screen culling: from `O(n_tiles)` to `O(viewport_tiles)`. The integer-math version. Why `colliderect` per tile is *wrong* even though it works.
- Frame budget: 60 fps means 16.6 ms. A 2000-tile level culled to ~600 visible tiles costs ~1.2 ms to draw. The same level uncalled costs ~9 ms and tips you over budget the moment particles arrive.
- Parallax for free: a second tile layer drawn with the camera's offset multiplied by 0.5 gives you depth at zero extra cost.

## Weekly schedule

The schedule below adds up to approximately **35 hours**. Treat it as a target. This is the first heavily-architectural week of C11 — you'll spend more time *designing the loader* than you spent writing the brick-breaker. That is normal. The loader is the thing you'll keep using for the rest of the course.

| Day       | Focus                                            | Lectures | Exercises | Challenges | Quiz/Read | Homework | Mini-Project | Self-Study | Daily Total |
|-----------|--------------------------------------------------|---------:|----------:|-----------:|----------:|---------:|-------------:|-----------:|------------:|
| Monday    | Lecture 1 + CSV loader                           |    2h    |    1.5h   |     0h     |    0.5h   |   1h     |     0h       |    0.5h    |     5.5h    |
| Tuesday   | Tiled install, build a 12x20 test map            |    1h    |    1.5h   |     0h     |    0.5h   |   1h     |     1h       |    0.5h    |     5.5h    |
| Wednesday | Lecture 2 + camera lerp + dead-zone              |    2h    |    1.5h   |     0h     |    0.5h   |   1h     |     1h       |    0h      |     6h      |
| Thursday  | Off-screen culling, frame-budget profiling       |    0h    |    1h     |     2h     |    0.5h   |   1.5h   |     1.5h     |    0h      |     6.5h    |
| Friday    | Build platformer movement + AABB-vs-tilemap      |    0h    |    0h     |     0h     |    0.5h   |   1h     |     2.5h     |    0.5h    |     4.5h    |
| Saturday  | Three-level pipeline, level-select screen, quiz  |    0h    |    0h     |     0h     |    0.5h   |   0h     |     2.5h     |    0h      |     3h      |
| Sunday    | Polish, README, push                             |    0h    |    0h     |     0h     |    0.5h   |   0h     |     2h       |    0h      |     2.5h    |
| **Total** |                                                  | **5h**   | **5.5h**  | **2h**     | **3.5h**  | **5.5h** | **10.5h**    | **1.5h**   | **33.5h**   |

## How to navigate this week

| File | What's inside |
|------|---------------|
| [README.md](./README.md) | This overview (you are here) |
| [resources.md](./resources.md) | Tiled docs, PyTMX, Pygame tilemap tutorials, classic chapters from Nystrom and Schell |
| [lecture-notes/01-the-tilemap-data-format.md](./lecture-notes/01-the-tilemap-data-format.md) | What a tilemap *is*; CSV; Tiled JSON; the four coordinate transforms |
| [lecture-notes/02-camera-and-off-screen-culling.md](./lecture-notes/02-camera-and-off-screen-culling.md) | Camera follow, dead-zones, clamp-to-bounds, culling, parallax, frame budget |
| [exercises/README.md](./exercises/README.md) | Index of short coding drills |
| [exercises/exercise-01-csv-tilemap.py](./exercises/exercise-01-csv-tilemap.py) | Load a 12x20 grid from a CSV string, draw it, no editor required |
| [exercises/exercise-02-tiled-json-loader.py](./exercises/exercise-02-tiled-json-loader.py) | Parse a Tiled-style JSON inline string, draw layers, handle GID 0 (empty) |
| [exercises/exercise-03-camera-follow.py](./exercises/exercise-03-camera-follow.py) | A player-tracking camera with snap, lerp, and dead-zone modes; clamp to bounds |
| [challenges/README.md](./challenges/README.md) | Index of weekly challenges |
| [challenges/challenge-01-3-loadable-levels.md](./challenges/challenge-01-3-loadable-levels.md) | Ship three CSV levels and a level-select screen |
| [quiz.md](./quiz.md) | 10 multiple-choice questions |
| [homework.md](./homework.md) | Six practice problems for the week |
| [mini-project/README.md](./mini-project/README.md) | A 2D platformer prototype with three loadable levels |

## Frame budget for this week

A reminder of what 60 fps actually means, in milliseconds. Every C11 lecture returns to this tile.

```
┌─────────────────────────────────────────────────────────┐
│  FRAME BUDGET — 60 fps target, with a tilemap           │
│                                                         │
│  Input poll:       ~0.2 ms                              │
│  Update (sim):     ~1.5 ms                              │
│  Tilemap collide:  ~0.6 ms (AABB-vs-grid is cheap)      │
│  Particles:        ~0.5 ms                              │
│  Tilemap draw:     ~1.2 ms  (culled to ~600 tiles)      │
│  Entity draw:      ~1.5 ms                              │
│  Camera apply:     ~0.1 ms                              │
│  HUD draw:         ~0.4 ms                              │
│  Audio mix:        ~0.3 ms                              │
│  GPU + present:    ~4.0 ms                              │
│  Headroom:         ~6.3 ms                              │
│  ─────────────────────                                  │
│  Total:           ~16.6 ms / frame                      │
└─────────────────────────────────────────────────────────┘
```

This week, **Tilemap collide** and **Tilemap draw** earn their rows for the first time. Both are cheap *if* you wrote them correctly. The lecture on culling is the difference between the 1.2 ms above and a 9 ms tilemap draw that eats the entire rest of your budget. The lecture on AABB-vs-grid collision is the difference between 0.6 ms and a 4 ms naive loop. Get the budgets in your head now; Week 5 (State machines) and Week 6 (Animation) will be cheap *only because* this week's draw and collide stay cheap.

## Stretch goals

If you finish early and want to push further:

- Install [Tiled](https://www.mapeditor.org/) and re-do at least one of your CSV levels as a `.tmx` with two layers (a background and a collidable foreground). Export as JSON. Load it. Notice that Tiled's level-design ergonomics make the level-design step ten times faster — that is the point of using an editor.
- Add a **parallax background layer**: a second tile layer drawn with `camera_offset * 0.5`. The illusion of depth at zero extra cost.
- Add **animated tiles**: water that has 4 frames and cycles at 8 fps. Tiled supports tile animations natively; if you read the JSON, you'll find an `animation` array per-tile.
- Add **one-way platforms** (a tile that has collision only when the player is above it and moving downward). This is the platformer technique that turns a *prototype* into a *level designer's playground*.
- Read Bob Nystrom's *Game Programming Patterns* chapter on **Spatial Partition**: <https://gameprogrammingpatterns.com/spatial-partition.html>. A uniform grid (which is exactly what a tilemap *is*) is the simplest spatial partition. Notice that you wrote one this week without using that term.

## Voice rules for the week

- We separate **data** from **code**. A level is a file. A level is not a Python literal. This will change the way you think about every subsequent week.
- We credit **Thorbjørn Lindeijer**, who has maintained [Tiled](https://www.mapeditor.org/) since 2008 as free, open-source software. Indie game development would look different without Tiled, and we say so out loud.
- We cite **Bob Nystrom's *Game Programming Patterns*** when we use his terms. He has been writing the canonical free indie-gamedev book for fifteen years. Cite the source.
- We prefer **stdlib loaders** over third-party. A `.csv` is two lines of `csv.reader`. A Tiled `.json` is `json.load`. `pytmx` and `pyscroll` are excellent but optional; this week we write our own loader because the loader is the thing the lecture teaches.

## Up next

Continue to [Week 5 — State machines for characters](../week-05/) once you've pushed your platformer with three loadable levels.

---

*If you find errors in this material, please open an issue or send a PR. Future learners will thank you.*
