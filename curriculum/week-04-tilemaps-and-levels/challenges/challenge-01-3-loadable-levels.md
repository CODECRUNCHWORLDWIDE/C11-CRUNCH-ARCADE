# Challenge 1 — Three Loadable Levels

**Time estimate:** ~120 minutes (level design, level-select menu, write-up).

## Problem statement

Ship three CSV-encoded levels and a level-select screen that loads them. The same engine loads all three. Level 1 is a friendly tutorial. Level 2 introduces a vertical-platform challenge. Level 3 is a maze with at least one dead end. The constraint is hard: **only the data files change between levels**. Your loader code stays still.

This is the artefact that distinguishes "I made a tilemap demo" from "I made a level-select-driven game." The whole point of the data-vs-code split is that you can ship more levels by editing files, not by editing source. Three levels is the minimum that proves the loader generalises; doing fewer collapses back into "hardcoded level."

You will produce four artefacts:

1. **Three CSV files** at `levels/level-01.csv`, `levels/level-02.csv`, `levels/level-03.csv`. Each is a comma-separated grid of integers, at least 20 cols × 12 rows.
2. **One level-select screen** at startup. Keys `1`, `2`, `3` load the corresponding level. The screen shows level names and a small thumbnail-ish preview if you want stretch.
3. **One reset key (`R`)** during gameplay returns to the level-select screen. One next-level key (`N`) advances to the next level when you reach the goal.
4. **A 150-200 word write-up** at `challenges/challenge-01/WRITEUP.md` explaining what changes between levels and what *doesn't*.

The write-up is what graduates this from "three CSVs" to "a design artefact about engine/data separation."

## Acceptance criteria

- [ ] A folder `levels/` exists in your repo with at least three `.csv` files: `level-01.csv`, `level-02.csv`, `level-03.csv`.
- [ ] Each level is **at least 20 columns wide and 12 rows tall**. Larger is fine; the engine should not care.
- [ ] The same Python loader function (call it `load_level(path)`) is used for all three. There are no per-level branches in your code (`if level == 1: ...` is a hard fail).
- [ ] A level-select screen shows at startup with the three options. Keys `1`, `2`, `3` load the corresponding level.
- [ ] `R` returns to the level-select screen at any time during play.
- [ ] `N` advances to the next level when the player has reached the goal tile. From Level 3, `N` returns to level-select.
- [ ] Each level has at least one **goal tile** (marked as the same integer in all three CSVs — for example, `9`).
- [ ] Each level has at least one **player spawn** (a different integer — for example, `8`).
- [ ] Level 1 is solvable in under 60 seconds by a first-time player who hasn't seen it. (You'll test this with a friend.)
- [ ] Level 2 contains at least one vertical platform stack that requires a jump to traverse. (Even if you haven't built jump physics yet — the mini-project handles that — the *layout* anticipates it.)
- [ ] Level 3 contains at least one dead end (a corridor with no exit that the player can walk into).
- [ ] A `challenges/challenge-01/WRITEUP.md` of 150-200 words exists and:
  - Names the tile-integer convention you chose (which integers mean wall, spawn, goal, etc.).
  - Explains why the loader doesn't change between levels.
  - Describes the design intent of each level in one sentence.
  - References Lecture 1's data-vs-code shift by name.

## Suggested order of operations

Build incrementally. Each phase ends with a commit.

### Phase 1 — Design Level 1 (~25 min)

1. Pick your tile-integer convention. We suggest: `0` empty, `1` wall, `8` spawn, `9` goal. Document it in a comment at the top of each CSV.
2. Open a spreadsheet (LibreOffice Calc, Google Sheets) and lay out a 25×13 grid. Border = walls. Put a spawn near the left, a goal near the right, a few interior walls.
3. Export as CSV. Save as `levels/level-01.csv`.
4. Commit: `Add level-01: friendly tutorial layout`.

### Phase 2 — Reuse the Exercise-1 loader (~15 min)

1. Copy the `load_csv_from_string` from Exercise 1. Adapt to `load_csv(path)` that opens a file.
2. Verify it loads Level 1 and prints the grid shape.
3. Commit: `Add CSV loader; loads level-01.csv`.

### Phase 3 — Design Levels 2 and 3 (~35 min)

1. Level 2: introduce vertical platforms. Stack `1`s in columns to create platforms the player must jump onto. (The mini-project will add jumping; for the challenge, *walking-up-stairs* is acceptable.)
2. Level 3: a maze. At least one dead end. Width 30+ rows if you want it to feel like a maze.
3. Save both. Commit each level in its own commit.

### Phase 4 — Build the level-select screen (~30 min)

1. A simple Pygame screen that draws three numbered options. On key `1`, `2`, `3`, transition to the gameplay state with the matching level loaded.
2. The transition is a state variable: `game_state in ("select", "playing")`. No fancy state machine yet — that's Week 5.
3. `R` from gameplay returns `game_state = "select"`. `N` after winning advances `level_index` and loads the next file.
4. Commit: `Add level-select screen and state transitions`.

### Phase 5 — Write the write-up (~15 min)

1. Open `challenges/challenge-01/WRITEUP.md`.
2. 150-200 words. Name your tile convention. Explain why the loader doesn't change. Describe each level in one sentence.
3. Commit: `Add WRITEUP for challenge-01`.

## Stretch (any of these for extra polish)

- **A fourth level authored in Tiled.** Re-do one of the three CSVs as a `.tmx` exported to JSON, and add a fourth menu entry. Reuse the Tiled JSON loader from Exercise 2. Notice the friction difference between editing a CSV in a spreadsheet and editing a `.tmx` in Tiled.
- **Preview thumbnails.** On the level-select screen, draw a tiny 100×60 preview of each level so the player can visually pick. This is one extra function: load the CSV, draw it into a small Surface at 4 px per tile, blit beside the menu entry.
- **A "secrets found / coins collected" stat** displayed on the select screen for completed levels. Persist between runs in a `progress.json`. Stretches into Week 7 (save & load) early.
- **Level transitions with a Coin-Pink wipe.** On `N`-pressed, fade or wipe to the next level. Two seconds. Low cost, big polish payoff.

## Hints

<details>
<summary>What if the levels have different sizes?</summary>

That's fine. Your loader returns a `TileMap` whose `cols` and `rows` properties come from the data. The renderer iterates `range(tm.rows)` and `range(tm.cols)` — no hardcoded numbers. The camera bounds are `tm.cols * TILE` and `tm.rows * TILE`. Three different sizes work transparently.

</details>

<details>
<summary>How do I make a maze that isn't just walls?</summary>

Start with a perimeter wall, then *carve* corridors. Two-cell-wide corridors are friendlier than one-cell. Add one or two "rooms" — open areas of 4×4 or 5×5 cells — as visual anchors. A dead end is a corridor that ends in a wall on three sides; the player walks in, realises, and walks back. One dead end is enough; more than three is frustrating.

</details>

<details>
<summary>How do I keep the loader generic when each level has different objects?</summary>

The CSV grid only encodes *static* tiles. For *dynamic* objects (enemies, doors, switches), use a parallel `.json` file with the same base name (`level-01.csv` + `level-01.json`). The CSV is the static layer; the JSON is the object layer. This is exactly Tiled's split between tile layers and object layers — you're reproducing it with two stdlib formats.

For the challenge, this isn't required — just walls, spawn, and goal. But knowing the pattern matters for the mini-project.

</details>

<details>
<summary>What if my level-select code grows ugly?</summary>

It will, slightly. Three lines of `if key == K_1: ...` is fine. If you find yourself writing more than five lines per option, you've over-engineered. The fancy state-machine version is Week 5's job. This week, two states and three keys are enough.

</details>

## What "great" looks like

A friend who has never seen your project sits down. They see the level-select screen, press `1`, play through Level 1 in under a minute. They press `R`, see the menu, press `2`, immediately feel the level design has changed — the layout is *different*, the engine is the *same*. They reach the goal, press `N`, get Level 3, see a maze, walk into the dead end, laugh, retrace. After ten minutes they say: "okay, can I edit the levels?" — and you point them at the `levels/` folder. They open `level-02.csv` in a spreadsheet. They add a wall. They press `2`. The wall is there.

That moment — when a non-programmer changes your game by editing a spreadsheet — is what the data-vs-code shift *means*. It's also the moment that turns this challenge into something you'll point to in your portfolio.
