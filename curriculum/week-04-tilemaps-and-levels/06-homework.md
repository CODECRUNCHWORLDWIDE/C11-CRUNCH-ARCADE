# Week 4 Homework

Six practice problems that revisit the week's topics. The full set should take about **5–6 hours** in total. Work in your Week 4 Git repository so each problem produces at least one commit you can point to later.

The work this week is half-coding, half-content. Get used to producing levels alongside code; level design *is* a deliverable, not a side-quest. This is the week we practise that habit.

Each problem includes:

- A short **problem statement**.
- **Acceptance criteria** so you know when you're done.
- A **hint** if you get stuck.
- An **estimated time**.

---

## Problem 1 — A second CSV level

**Problem statement.** Take your `exercise-01-csv-tilemap.py` and extract the level CSV into a separate `levels/level-01.csv` file. Then design and add `levels/level-02.csv` — a *different* layout, same width and height, same tile-integer convention. Modify the loader to accept a path (not an inline string). On startup, the game loads `level-01.csv`. Pressing `2` switches to `level-02.csv` (the game state is rebuilt; the loader function is called again).

**Acceptance criteria.**

- A folder `homework/p1_two_levels/` exists with `main.py`, `levels/level-01.csv`, `levels/level-02.csv`.
- `python -m py_compile main.py` succeeds.
- The two levels are **visibly different** (don't just transpose one — design something distinct).
- Pressing `1` loads `level-01.csv`. Pressing `2` loads `level-02.csv`. The level swap happens live; the program does not need to restart.
- A `homework/p1_two_levels/NOTES.md` (50-100 words) describes what you changed between the two levels and why.

**Hint.** The loader function becomes `load_csv(path)` that opens and reads the file:

```python
def load_csv(path: str) -> TileMap:
    grid = []
    with open(path, newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            grid.append([int(c.strip()) if c.strip() else 0 for c in row])
    return TileMap(grid=grid)
```

**Estimated time.** 35 minutes.

---

## Problem 2 — Apply the integer-math cull to your CSV renderer

**Problem statement.** Take `exercise-01-csv-tilemap.py` (or your `p1_two_levels/main.py`) and grow the level to **80 cols × 40 rows**. Add a camera that follows the player (lerp mode is fine). Implement off-screen culling with the integer-math `visible_tile_range` from Lecture 2 §4. Profile your draw call with `time.perf_counter` before and after culling, on the same level, and report the speedup.

**Acceptance criteria.**

- A file `homework/p2_culled_renderer.py` exists, runs, and shows a 80×40 level with a camera following the player.
- The culled draw loop only visits cells inside `visible_tile_range`. Verify by printing the cell count drawn per frame.
- A file `homework/p2_culled_profile.md` (75-150 words) contains:
  - The naive draw time (ms) on your machine for a 80×40 level.
  - The culled draw time (ms) on the same machine.
  - The speedup ratio.
  - One sentence explaining why the speedup is real (cite Lecture 2 §4 or §5).

**Hint.** Use `time.perf_counter` like this:

```python
t0 = time.perf_counter()
# ... draw_layer call ...
elapsed_ms = (time.perf_counter() - t0) * 1000.0
```

Average over 60 frames for a stable number. Single-frame measurements bounce all over the place.

**Estimated time.** 55 minutes.

---

## Problem 3 — Tiled JSON with two tile layers AND a parallax background

**Problem statement.** Extend Exercise 2's loader to draw the `background` layer with a *parallax* factor of `0.5` — the background scrolls at half the camera's speed. Confirm by walking the player to the right and watching the background drift behind the foreground. Save as `homework/p3_parallax.py`.

**Acceptance criteria.**

- A file `homework/p3_parallax.py` exists, runs, and renders a two-layer scene where the background scrolls at 0.5× the foreground.
- The foreground draws on top of the background (painter's order).
- The parallax factor lives in a constant at the top of the file (`PARALLAX_BG = 0.5`). Setting it to `1.0` disables parallax; setting it to `0.0` pins the background to the screen.
- A `homework/p3_parallax_note.md` (50-100 words) describes the visual change vs Exercise 2 in plain language.

**Hint.** The parallax is a single multiplication on the camera offset:

```python
bg_cam = Camera(x=cam.x * PARALLAX_BG, y=cam.y * PARALLAX_BG,
                viewport_w=cam.viewport_w, viewport_h=cam.viewport_h)
draw_layer(screen, background, tile_surfaces, bg_cam, TILE)
```

**Estimated time.** 50 minutes.

---

## Problem 4 — AABB-vs-tilemap collision (the platformer essential)

**Problem statement.** Take Exercise 3 (the camera-follow demo) and replace the "constrain to level bounds" with **real tile collision**. The player AABB cannot pass through any tile with `grid[r][c] != 0`. Split the resolution into a horizontal pass (move by `vx * dt`, check x-collisions, snap) and a vertical pass (move by `vy * dt`, check y-collisions, snap). Save as `homework/p4_aabb_grid.py`.

**Acceptance criteria.**

- A file `homework/p4_aabb_grid.py` runs and the player can walk across the floor without falling through, push against walls without phasing through them.
- The collision resolution converts the player's AABB to tile coordinates and only tests the 2-6 tiles under/around the player — not the whole grid.
- Acceptance demo: walk into a corner. The player wedges. Walking up-and-right past the corner re-frees them. No "stuck" states.
- A `homework/p4_aabb_note.md` (75-125 words) explains why splitting horizontal and vertical passes is necessary (hint: diagonal corner case).

**Hint.** The horizontal pass:

```python
px += vx * dt
# Convert AABB to tile range.
left   = int(px // TILE)
right  = int((px + player_w - 1) // TILE)
top    = int(py // TILE)
bottom = int((py + player_h - 1) // TILE)
for tc in range(left, right + 1):
    for tr in range(top, bottom + 1):
        if grid[tr][tc] != 0:
            if vx > 0:
                px = tc * TILE - player_w
            elif vx < 0:
                px = (tc + 1) * TILE
```

Mirror for the vertical pass with `vy` and `py`. Order: horizontal first, then vertical.

**Estimated time.** 1 hour 15 minutes.

---

## Problem 5 — Per-tile properties (which tiles are solid?)

**Problem statement.** In Exercise 2's loader, every non-zero tile in the `world` layer is treated as solid. Make that smarter: read a JSON sidecar `level-properties.json` (you author it by hand) that lists which GIDs are solid, which are damage, which are one-way platforms, and which are decoration. The renderer still draws everything; the collision system only treats the "solid" set as solid. Save as `homework/p5_tile_properties.py` + `homework/p5_tile_properties.json`.

**Acceptance criteria.**

- Two files: `p5_tile_properties.py` (the code) and `p5_tile_properties.json` (the sidecar).
- The sidecar has the shape:
  ```json
  {
    "solid":  [3, 4],
    "damage": [],
    "one_way": [5],
    "decoration": [1, 2]
  }
  ```
- The player can walk through GIDs in the `decoration` set without colliding. They cannot pass through `solid`. (`one_way` and `damage` are optional behaviours; document what you implemented.)
- A `homework/p5_tile_properties_note.md` (50-100 words) explains why the sidecar JSON is a strictly better design than encoding properties in the tile integers themselves.

**Hint.** Build a set of solid GIDs once at load time:

```python
with open("level-properties.json") as f:
    props = json.load(f)
solid_gids = set(props["solid"])

def is_solid(gid: int) -> bool:
    return gid in solid_gids
```

Then `is_solid(world.gid_at(c, r))` replaces `world.gid_at(c, r) != 0` in your collision code.

**Estimated time.** 1 hour.

---

## Problem 6 — Reflection essay

**Problem statement.** Write a 350-450 word reflection at `notes/week-04-reflection.md` answering:

1. Before this week, where did your level data live? After this week, where does it live? Describe a specific moment in the homework or mini-project where moving from code to data unlocked something.
2. The lecture claims "camera is two floats and a subtraction." Did you experience that as obvious or did you have to convince yourself? Describe one bug you hit that was, in retrospect, you forgetting to subtract or to clamp.
3. Off-screen culling is one of the oldest tricks in graphics. Why do you think *every* tilemap tutorial that uses `Rect.colliderect` per tile still works? What's the cost the tutorial doesn't measure?
4. What's one thing you'd add to your platformer prototype if you had another five hours? Why that thing first?

**Acceptance criteria.**

- A file `notes/week-04-reflection.md`, 350-450 words.
- Each numbered question addressed in its own paragraph.
- At least one specific technique mentioned by name (e.g., "the integer-math `visible_tile_range`" rather than "the cull").
- At least one citation of Lecture 1 or Lecture 2 by section number.
- File is committed.

**Hint.** Reflection essays read flat when they're abstract. Write about specific moments: "When I cranked the level from 25×13 to 80×40 my fps dropped from 60 to 11 instantly. The fix was four lines. I keep thinking about that ratio." beats "I learned about culling."

**Estimated time.** 30 minutes.

---

## Time budget recap

| Problem | Estimated time |
|--------:|---------------:|
| 1 | 35 min |
| 2 | 55 min |
| 3 | 50 min |
| 4 | 1 h 15 min |
| 5 | 1 h 0 min |
| 6 | 30 min |
| **Total** | **~5 h 5 min** |

That's about an hour under the 6-hour weekly budget — the rest is for the bugs your loader will produce. Tilemap loaders fail in surprising ways (rotated, mirrored, shifted by one), and the debugging time is real. Budget it.

When you've finished all six, push your repo and open the [mini-project](./07-mini-project/00-overview.md).
