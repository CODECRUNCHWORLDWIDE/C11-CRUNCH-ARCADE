# Mini-Project — A 2D Platformer Prototype with Three Loadable Levels

> Ship a 2D platformer prototype with **three loadable levels**, gravity, jump physics, AABB-vs-grid collision, a follow camera, and off-screen culling. The same engine loads all three levels; only the data files change. Record a 30-second video showing all three. Write a 250-word reflection. Push to GitHub.

This is the artefact this week was building toward. By Sunday you have a small, playable platformer where the levels are *files* and the engine is *code*, and the two are cleanly separable. The mechanic is simple — walk, jump, reach the goal — because the work this week is the *content pipeline*, not new mechanics. Week 5 turns this prototype into a state-machine-driven character; Week 6 adds animation; Week 9 ports the whole thing to Godot. But it all starts with this: levels-as-data.

You will NOT add new mechanics beyond walk+jump+goal. If you find yourself adding enemies, power-ups, or a second movement ability, you've drifted — that's Week 5+ territory. The discipline this week is *level design and engine architecture*, not feature creep.

**Estimated time:** 10.5 hours (split across Wednesday → Sunday).

---

## What you will build

A new repo (or a `platformer/` subfolder of your portfolio repo), with:

1. **An engine** — one Python codebase, ~400-600 lines, that knows nothing about specific levels. It opens a path, loads the level, runs the simulation.
2. **Three levels** — `levels/level-01.csv`, `level-02.csv`, `level-03.csv` (or `.json` if you've installed Tiled). Each ≥ 25 cols × 15 rows. Distinct in design: tutorial, jump challenge, maze with a goal at the far end.
3. **A level-select screen** with three options. Keys `1`, `2`, `3`.
4. **In-game keys:** `R` to restart current level. `N` to advance after reaching the goal. `ESC` to quit.
5. **Player physics:** walk left/right, jump on `SPACE` or `W`, gravity, terminal-velocity clamp. Coyote time (~80 ms) optional but recommended.
6. **AABB-vs-grid collision** that resolves the player out of solid tiles. Split horizontal and vertical passes.
7. **A camera that follows the player** in lerp or dead-zone mode (your choice), clamped to level bounds, with **off-screen culling** baked into the draw loop.
8. **A 30-second comparison video** showing all three levels back-to-back.
9. **A 250-word reflection** in `REFLECTION.md` using this week's vocabulary correctly.

You will NOT add:

- Enemies. (Week 5+.)
- Multiple player states beyond walk/jump. (Week 5.)
- Animation. (Week 6.)
- Save state. (Week 7.)
- Story or progression beyond "you reached the goal." (Capstone weeks.)

---

## Rules

- **You may** copy from this week's exercises freely — that's why they exist.
- **You may** copy the AABB-vs-grid collision skeleton from homework Problem 4 verbatim. It's a single technique; reimplementing it from scratch for the mini-project is wasteful.
- **You may NOT** hardcode any level layout in `.py` files. Every level lives in a `levels/*.csv` (or `levels/*.json`). If you write `LEVEL_DATA = [[1, 1, ...]` in `main.py`, you've failed the brief.
- **You may NOT** write per-level branches (`if level_index == 0: ...`). The engine treats levels identically. Only data differs.
- **You may NOT** add sprite art or animations. Use coloured rectangles and shapes. Week 6 lessons.
- **You must** use a virtual environment.
- **Python 3.11+, Pygame 2.5+.**
- Optional: `Tiled` for one of the three levels. CSV is fine for all three.

---

## Acceptance criteria

- [ ] A repo (or subfolder) called `c11-week-04-platformer-<yourhandle>`.
- [ ] `python -m py_compile main.py` succeeds with no output.
- [ ] `python main.py` opens the window on a level-select screen.
- [ ] Three CSV (or mixed CSV/Tiled-JSON) levels exist in `levels/`.
- [ ] Pressing `1`, `2`, or `3` on the level-select screen loads the corresponding level. The same engine code path handles all three.
- [ ] No per-level branches anywhere in the code (a grep for `level == 0` or `level_index == 1` returns nothing).
- [ ] The player walks (left/right arrow or A/D), jumps (SPACE or W) with gravity, and cannot pass through solid tiles.
- [ ] Reaching the goal tile transitions to a brief "Level Complete" screen with `N` to continue.
- [ ] From Level 3, `N` returns to the level-select screen.
- [ ] `R` at any time during gameplay restarts the current level.
- [ ] The camera follows the player smoothly (lerp or dead-zone — your call), clamped to level bounds.
- [ ] Off-screen tile culling is implemented as integer-math `visible_tile_range`. The draw loop does not visit cells outside the viewport.
- [ ] The HUD shows: current level number, fps, "drawn tiles / total tiles" (so the cull is visible).
- [ ] Each level is **at least 25 cols × 15 rows.** Level 3 should be at least 40 cols × 25 rows to exercise the camera meaningfully.
- [ ] Levels are **designed**, not random. Each has a clear path, a clear goal, and at least one moment of "ah, I see what I have to do."
- [ ] A 25-40 second video at `demo.mp4` (or linked from `README.md`) shows all three levels played back-to-back.
- [ ] A 250-word `REFLECTION.md` at the repo root that:
  - Describes how the engine doesn't change between levels.
  - Names the camera follow mode you chose and why.
  - Cites both lecture notes by name.
  - States ONE thing you would do differently next time.
- [ ] Updated `README.md` includes:
  - A controls section.
  - A levels section (one sentence describing the design intent of each).
  - A "How to add a new level" section in three steps.
  - Credits for any asset packs used (Kenney for art, etc.).

---

## Suggested order of operations

Build incrementally rather than trying to write the whole thing at once. Each phase ends with a commit.

### Phase 1 — Tag the "before" and skeleton (~30 min)

1. Create the repo. Add a `.gitignore` (`.venv`, `__pycache__`, `*.pyc`).
2. Create the folder structure:
   ```
   c11-week-04-platformer-<handle>/
     main.py
     levels/
       level-01.csv
     README.md
     REFLECTION.md
   ```
3. Copy `exercise-01-csv-tilemap.py` into `main.py` as a starting point. Extract the CSV into `level-01.csv`.
4. Commit: `Initial skeleton; one CSV level renders.`

### Phase 2 — The Camera and the cull (~1 h)

1. Copy the `Camera`, `follow_lerp` (or `follow_dead_zone`), `clamp_camera_to_bounds`, and `visible_tile_range` from Exercise 3 into `main.py`.
2. Replace the naive draw loop with the culled version.
3. Grow Level 1 to ~30 cols × 15 rows. Walk the player around with the arrow keys (stepped is fine for now).
4. Verify the HUD shows "drawn/total" tiles and that drawn is roughly the viewport size at all times.
5. Commit: `Add follow camera and integer-math cull.`

### Phase 3 — Continuous movement + gravity + jump (~2 h)

1. Replace stepped (cell-by-cell on keypress) movement with continuous (`px/s`, `dt`-correct) movement.
2. Add a `vy` term and apply gravity each frame: `vy += GRAVITY * dt`. Clamp `vy` to a terminal velocity (~1200 px/s is reasonable).
3. On SPACE-down (or `W`-down), if the player is grounded (you'll define this in Phase 4), set `vy = -JUMP_VEL` (~-650 px/s is reasonable).
4. Don't worry about collisions yet — just integrate. The player will fall through the floor. That's fine for one commit.
5. Commit: `Add continuous movement and gravity.`

### Phase 4 — AABB-vs-grid collision (~2 h)

1. Copy the collision routine from homework Problem 4. Wire it into the update loop.
2. Track `grounded` as a boolean set when a downward vertical collision happens. Reset to `False` before each vertical pass.
3. Jump is now gated on `grounded == True`. Coyote time (optional): allow jumping for ~80 ms after leaving the ground.
4. Walk the player around. Confirm: no falling through floors. No phasing through walls. No getting stuck in corners.
5. Commit: `AABB-vs-grid collision + grounded check.`

### Phase 5 — Design Levels 2 and 3 (~2 h)

1. Open a spreadsheet (or Tiled if you want the practice). Design Level 2: introduces a jump-required platform stack. The player should fail it the first time and succeed the second.
2. Design Level 3: at least 40 cols × 25 rows. Includes a maze, a long horizontal corridor that exercises the camera, and a goal at the far end. Should take 1-2 minutes to clear on first play.
3. Save as `levels/level-02.csv` and `levels/level-03.csv`.
4. Test each by changing the loaded path. Iterate on the design — first draft is never the shipping draft.
5. Commit each level in its own commit: `Add level-02 (jump challenge)` and `Add level-03 (maze)`.

### Phase 6 — Level-select screen + state transitions (~1 h)

1. Introduce a `state` variable that takes values `"select"`, `"playing"`, `"complete"`.
2. Implement the select screen: three labelled options, `1`/`2`/`3` to start a level.
3. Implement the complete screen: shows when the player touches the goal. `N` advances; `R` retries.
4. Implement `R` in `"playing"` to reset the current level.
5. Commit: `Add level-select and complete screens; state transitions.`

### Phase 7 — Record the demo video + write the reflection (~1.5 h)

1. Open a screen recorder (OBS, macOS `Cmd-Shift-5`, Windows Game Bar). Set the capture region to the game window.
2. Play through all three levels back-to-back. Aim for 25-35 seconds total.
3. Export as `demo.mp4`. Commit (or upload externally and link).
4. Write `REFLECTION.md`. 250 words. Cite both lectures. Name your camera follow mode. State one thing you'd do differently.
5. Final commit: `Add demo video and reflection.`
6. Push. Verify the repo URL works on a fresh clone.

---

## Rubric

| Criterion | Weight | What "great" looks like |
|----------|-------:|-------------------------|
| Three levels loaded from data | 25% | Three CSV/JSON files, no per-level code branches. A `diff` between Level 1 and Level 2 shows changes only in `.csv`. |
| Engine architecture (data vs code) | 15% | No level layout in `.py`. The same `load_level(path)` handles all three. |
| Camera + culling | 15% | Smooth follow, clamped, no jitter. `drawn/total` HUD shows the cull is real. |
| Physics (gravity + jump + AABB) | 15% | Walk, jump, land. No phasing. No falling-through-floor. |
| Level design quality | 15% | Each level has a clear design intent visible in 30 seconds of play. |
| Demo video | 8% | 25-40 seconds, all three levels, ≤ 50 MB. |
| Reflection (vocabulary correctness) | 5% | Cites both lectures; names camera mode; uses week's terms correctly. |
| Commit history | 2% | One commit per phase; meaningful messages. |

---

## Stretch (if you finish early)

These are *stretch*. Do **not** lose the main spec chasing them.

- **A fourth level in Tiled.** Install Tiled, build a `.tmx`, export to JSON, add a fourth option to the menu. Reuse the Exercise-2 loader. The friction difference between CSV and Tiled is the single most useful thing to feel firsthand.
- **Parallax background.** Add a second tile layer drawn with `cam * 0.5`. Cheap, big visual win. See homework Problem 3.
- **Coyote time + jump buffering.** Allow jump for ~80 ms after walking off a ledge (*coyote time*). Buffer a jump press for ~80 ms if pressed slightly before landing. These two together are what makes a 2D platformer feel like *Celeste* instead of *NES-era hard*.
- **One-way platforms.** A tile that has collision only when the player is moving downward and is above the tile's top edge. Pairs with a per-tile-property JSON (homework Problem 5).
- **Speed-run timer.** Track wall-clock time per level. Show on the complete screen. Persist best times in `progress.json`. Stretches into Week 7 (save & load).
- **A subtle juice pass.** A coin-pink burst on goal-touch, a tiny shake on landing, a sound cue on jump. You have these systems from Week 3. Reuse, don't reimplement.

---

## What this prepares you for

- **Week 5** (State machines) turns the player into a proper state machine: idle / walk / jump / fall / land / hurt. The walk/jump/grounded checks you write this week become the state-transition edges next week.
- **Week 6** (Animation & juice) adds sprite-sheet animation to the player and the world. Your tilemap renderer already has a draw loop; Week 6 adds a frame index per tile/entity.
- **Week 7** (Save & load) writes the player's progress (`current_level`, `best_times`, `coins_collected`) to a JSON file and re-loads on next run.
- **Week 9** (Pygame → Godot port) takes this platformer and re-implements it in Godot 4. The tilemap loader you wrote translates almost line-for-line to Godot's `TileMap` node. Most of the work in Week 9 is appreciating how much Godot does for free.

---

## Resources

- This week's [Lecture 1](../lecture-notes/01-the-tilemap-data-format.md) and [Lecture 2](../lecture-notes/02-camera-and-off-screen-culling.md).
- The week's [exercises](../exercises/) — copy from them.
- The week's [challenge](../challenges/challenge-01-3-loadable-levels.md) — the level-select pattern is there.
- Tiled — <https://www.mapeditor.org/>
- Kenney — free tilemap packs at <https://kenney.nl/assets/category:Tiles>
- Robert Nystrom — *Game Programming Patterns* (free): <https://gameprogrammingpatterns.com/>

---

## Submission

When done:

1. Push your repo to GitHub with a public URL.
2. Make sure `README.md` links to `demo.mp4` and credits any assets.
3. Make sure `levels/` has three real files.
4. Make sure `python -m py_compile main.py` is clean on a freshly cloned copy.
5. Submit the repo URL on the course tracker.

You separated levels from engine. That is the architectural shift this whole phase has been pushing toward. Next week we make the *character* match — turning a tangle of `grounded` and `vy` checks into a proper state machine that scales to twelve states without becoming spaghetti.
