# Week 4 — Exercises

Short, focused drills. Each one should take 30–55 minutes. Do them in order; later ones build on earlier ones. The point this week is *data, not code* — you'll keep using the same Pygame loop pattern with the level layout moved out of source.

## Index

1. **[Exercise 1 — CSV Tilemap](./exercise-01-csv-tilemap.py)** — load a 12×20 grid from a CSV string, render it, step a player around with the arrow keys. The smallest possible "level is data" sandbox. No external file required; the CSV is inline. (~30-40 min)
2. **[Exercise 2 — Tiled JSON Loader](./exercise-02-tiled-json-loader.py)** — parse a Tiled-style JSON export from an inline string. Two tile layers (background + world) and one object layer (spawn + goal). The loader is ~80 lines and you'll keep reusing it. (~40-50 min)
3. **[Exercise 3 — Camera Follow](./exercise-03-camera-follow.py)** — a level bigger than the window, a player you drive around continuously, and three camera follow modes (snap / lerp / dead-zone) you can switch between live. Off-screen culling baked in. (~45-55 min)

## How to work the exercises

- Read the prompt at the top of each file. Skim, don't memorise.
- **Type the code yourself.** Do not copy-paste from the lecture notes. Muscle memory is the entire point of these drills.
- Run it. See the output. Read the error if it crashed.
- If you get stuck for more than 15 minutes, scroll to the `HINT` block at the bottom of the file. It is commented out for a reason — peeking early stunts the learning.
- Verify each `.py` compiles with `python -m py_compile exercise-XX-name.py` before declaring it done.
- None of the exercises this week require external assets (no Tiled install, no `.wav` files, no PNG tilesets). The synthetic shapes are deliberate — the lecture is the data format, not the art.

## Before you start

Week 3's venv is fine. If you wiped it:

```bash
python -m venv .venv
source .venv/bin/activate    # or: .venv\Scripts\activate on Windows
pip install pygame
```

Confirm Pygame works with `python -c "import pygame; print(pygame.version.ver)"`. You want `2.5.x` or newer.

## What you'll have at the end

- Exercise 1: a `TileMap` dataclass and a `load_csv_from_string` parser. You'll keep both.
- Exercise 2: a `TiledMap`, `TileLayer`, `ObjectEntry` set of dataclasses and `load_tiled_from_string`. You'll lift these straight into the mini-project.
- Exercise 3: a `Camera` class with three follow modes, a `clamp_camera_to_bounds` helper, and a `visible_tile_range` cull. Again — straight into the mini-project.

By the end of Wednesday you have all three pieces. Thursday and Friday glue them into the platformer prototype.
