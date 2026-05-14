# Mini-Project — A Tiny RPG with a Real Save System

> Build a small Pygame RPG with a three-room dungeon, a player who picks up coins and keys, a level-end portal that unlocks the next room — and a *real* save system: three numbered slots, versioned schema, autosave on level transition, atomic writes, backup chain, SHA-256 integrity checks, and a slot-selector UI. Record a 20-second demo. Write a 250-word reflection. Push to GitHub.

This is the artefact this week was building toward. By Sunday you have a tiny but complete RPG whose save system would not embarrass a small indie studio. The *RPG* itself is intentionally minuscule — three rooms, four coin pickups, one key, one locked door — because the *save system* is the substantive code this week.

The mini-project assembles every piece of the week: the `GameState` from Lecture 1, the JSON format from Lecture 2, the migration ladder and atomic-write and checksum from Lecture 3, the three-slot UI from Challenge 2, and (optionally) the cloud-save design from Challenge 1.

**Estimated time:** 10 hours (split across Wednesday → Sunday).

---

## What you will build

A new repo (or a `save-rpg/` subfolder of your portfolio repo), with:

1. **An engine** — Python codebase, ~800-1100 lines, that loads a tiny three-room dungeon and renders a Coin-Pink player who can move (WASD), pick up coins and keys (walk into them), and use a key to open a locked door to the next room.
2. **Three rooms** — minimal level data. Each room is a fixed-size grid with a few walls, some pickups, and an exit portal. Room data lives in `levels/room_01.json`, `levels/room_02.json`, `levels/room_03.json`.
3. **A `GameState` dataclass** — the on-disk contract from Lecture 1, with at least these fields: `schema_version`, `slot_name`, `timestamp_iso`, `playtime_seconds`, `player_x`, `player_y`, `player_hp`, `player_hp_max`, `inventory`, `current_room`, `flags`.
4. **A `save.py` module** — implements the full crash-safe save pipeline: atomic write via `os.replace`, `.bak` rotation, SHA-256 sidecar, schema migration on load, `.bak` fallback on load failure.
5. **A `migrations.py` module** — contains at least one real migration. (You will ship v1 first; then *intentionally* bump to v2 by adding a `coins` field; then write `migrate_v1_to_v2`. The fact that you wrote one *real* migration is the artefact.)
6. **A three-slot save UI** — the screen from Challenge 2, wired into the pause menu. Press **Esc** to pause; the pause menu has Save / Load / Quit. Save opens the slot selector; Load opens the slot selector; Quit asks "save first?".
7. **An autosave** — fires when the player crosses a room boundary. Goes to a dedicated `autosave.json` slot. Never overwrites a manual save.
8. **A "saving..." flash** — when a save fires, a small badge appears in the corner for ~30 frames. The save itself takes ~1 ms; the badge makes the cost visible.
9. **A corruption-recovery path** — on save load, if the primary file's checksum does not match, the loader falls back to `.bak`. If `.bak` is also bad, the loader reports the failure to the player and offers a new game.
10. **A 20-second demo video** at `demo.mp4` showing: starting a fresh game, picking up a coin, saving to slot 1, walking to room 2 (autosave fires), quitting the game, restarting, loading slot 1, confirming progress restored.
11. **A 250-word `REFLECTION.md`** using this week's vocabulary correctly.

You will NOT add:

- Combat / enemies. (Week-11 capstone.)
- Sprite-sheet animation. (Week 6 — reuse a single static sprite per character; this week is about the save, not the look.)
- A complex inventory UI. (Show inventory as a one-line list in the HUD.)
- Cloud sync. (Challenge 1 is paper design only.)
- Encryption / anti-cheat. (Lecture 3 §7 — explicitly out of scope.)

---

## Rules

- **You may** copy from this week's exercises freely — that's why they exist. The `GameState` from Exercise 1, the migration ladder from Exercise 2, and the format choice from Exercise 3 are the starting points.
- **You may** reuse your Week-4 tilemap loader, Week-5 FSM, and Week-6 juice modules if you have them. The mini-project is the *save system*, not a rewrite of the engine.
- **You may NOT** put any `pygame.Surface`, `pygame.mixer.Sound`, or `pygame.font.Font` reference inside a save file. The `to_dict()` boundary catches this; trust the `TypeError` if you fail.
- **You may NOT** use `pickle` for the save format. JSON only. (`gzip` over JSON is fine if your save grows past 50 KB; for this small RPG it will not.)
- **You may NOT** skip the atomic-write pattern. The `os.replace` line is non-negotiable.
- **You may NOT** skip the schema-version stamp. Every save starts with `"schema_version": N`.
- **You must** ship at least *one real migration* (`migrate_v1_to_v2`). The fact that you wrote it — not the complexity of what it does — is the artefact.
- **You must** commit the demo video (or link to it). The video is what proves the system works end-to-end.
- **Python 3.11+, Pygame 2.5+.**
- **Use a virtual environment.**

---

## Acceptance criteria

- [ ] A repo (or subfolder) called `c11-week-07-save-rpg-<yourhandle>`.
- [ ] `python -m py_compile main.py` succeeds with no output.
- [ ] `python -m py_compile save.py migrations.py slot_ui.py` succeeds (or equivalent for whatever your module names are).
- [ ] `python main.py` opens a window with a Coin-Pink player on a three-room map.
- [ ] Player can move with WASD, pick up coins and keys, and walk through an unlocked door to the next room.
- [ ] **Esc** opens a pause menu with Save / Load / Quit options.
- [ ] Save opens a three-slot selector (plus autosave row). Overwriting an occupied slot triggers a confirmation dialog.
- [ ] Load opens the same selector. Loading an empty slot is denied.
- [ ] **Autosave** fires on every room transition. The autosave goes to its own slot and does *not* overwrite slot 1/2/3.
- [ ] **Atomic write:** check by inspecting `saves/`. Each save creates `slot_N.json`, `slot_N.json.bak`, and `slot_N.json.sha256`. There is no `slot_N.json.tmp` after a successful save (it was renamed away).
- [ ] **Schema version:** every save file's JSON contains a `"schema_version": N` field. Confirm with `grep schema_version saves/*.json`.
- [ ] **Migration:** there is at least one v1→v2 migration in `migrations.py`. Manually edit a save's `schema_version` from 2 to 1 and remove the `coins` field; reload; confirm the migration fires and the game still works.
- [ ] **Checksum:** the `.sha256` file contains a 64-character hex digest. Manually edit `slot_1.json` (change one digit); reload; confirm the loader falls back to `.bak`.
- [ ] **`.bak` fallback:** delete `slot_1.json` and rename `slot_1.json.bak` to `slot_1.json`. Reload. Confirm the game still loads (from what is now the primary file).
- [ ] **Saving... flash:** the save badge appears for ~30 frames on save fire. Look in the corner.
- [ ] **HUD** shows: current room name, inventory contents, play-time (HH:MM), and FPS.
- [ ] **`demo.mp4`** — 15-30 seconds, showing the full save / autosave / quit / reload / continue loop.
- [ ] **`REFLECTION.md`** — 250 words at the repo root that:
  - Names the FOUR state categories from Lecture 1 §2 and gives one example field per category from *your* code.
  - Names the migration you implemented and why you chose that particular change.
  - States ONE behaviour of the save system you would want a play-tester to exercise to find a bug.
  - Cites both Lecture 1 (*State to save*) and Lecture 3 (*Versioning and recovery*) by name.
  - Cites either Glenn Fiedler (*Gaffer On Games*) or the JSON RFC 8259 by name.
- [ ] **`CREDITS.md`** — credits for Kenney (if you used Tiny Dungeon for sprites), lecture authors (Fiedler, RFC 8259 authors), and Pygame.
- [ ] **`README.md`** includes:
  - A controls section.
  - A "What this demonstrates" section listing the save-system features (atomic write, versioning, checksum, autosave, slot UI).
  - The demo video inlined (or linked).
  - The asset credits inlined or linked.

---

## Suggested order of operations

Build incrementally rather than trying to write the whole thing at once. Each phase ends with a commit.

### Phase 1 — Scaffold the engine (~1 hour)

1. Create the new repo.
2. Build a 600×400 Pygame window with a `Player` dataclass at (300, 200) and WASD movement. No tiles yet — just a solid background, a player rectangle, the camera at origin.
3. Confirm the loop runs at 60 fps. (Reuse Week 1 / Week 2 boilerplate.)
4. Commit: `Scaffold the engine with a movable player.`

### Phase 2 — Three rooms and pickups (~1.5 h)

1. Define a `Room` dataclass with a name, a list of walls, a list of pickups, and an exit position.
2. Hard-code three rooms. Walls are `pygame.Rect`s; pickups are `Coin` or `Key` records with positions.
3. Player picks up a coin / key by walking into it. Inventory is a `dict[str, int]`.
4. The exit portal advances `current_room` to the next room *if* the player has the required key (room 2's exit requires `key_brass`).
5. Add a HUD showing current room name and inventory contents.
6. Commit: `Three rooms, coins, keys, and a locked-door exit.`

### Phase 3 — The save layer (~2 hours)

1. Define `GameState` in `save.py` per Lecture 1 §4. All persistent fields, no presentation.
2. Implement `gamestate_to_dict` and `gamestate_from_dict`.
3. Implement `capture_state` and `apply_state` against your `Player` and `World`.
4. Implement `write_save` with the atomic-write pattern from Lecture 3 §4: write to `.tmp`, fsync, `os.replace`, then rotate `.bak`.
5. Implement `read_save` with the `.bak` fallback from Lecture 3 §5.
6. Add SHA-256 sidecar files per Lecture 3 §6.
7. Wire **Ctrl-S** to save into slot 1 (no UI yet) and **Ctrl-L** to load.
8. Test: save, walk somewhere, load, confirm the player teleports back. Test: corrupt `slot_1.json` by hand, reload, confirm the loader falls back to `.bak`.
9. Commit: `Save layer with atomic write, backup chain, and checksums.`

### Phase 4 — Schema migration (~1 hour)

1. Define `CURRENT_SCHEMA_VERSION = 1` in `migrations.py` and ship a fresh save in v1.
2. Bump to v2: add a `coins: int` field to `GameState` (separate from the inventory's coin items — this is a quick-access "purse" count).
3. Update `capture_state` to populate `coins` from `inventory.get("coin_gold", 0) + inventory.get("coin_silver", 0)` (or whatever your scheme is).
4. Write `migrate_v1_to_v2` that adds `coins = 0` to any loaded v1 save (or computes it from the inventory if you want to be fancy).
5. Hand-edit a v1 save to remove the `coins` field and change `schema_version` to 1. Reload. Confirm the migration fires.
6. Commit: `Schema v2 with v1->v2 migration.`

### Phase 5 — Three-slot UI (~2 hours)

1. Build the slot selector from Challenge 2 (or reuse it directly). Three numbered slots plus autosave row.
2. Wire **Esc** to open a pause menu with Save / Load / Quit options.
3. Save and Load open the slot selector.
4. The selector handles the "overwrite?" confirmation modal.
5. Commit: `Three-slot save UI wired into pause menu.`

### Phase 6 — Autosave on room transition (~45 min)

1. When `current_room` changes, fire an autosave to `saves/autosave.json`.
2. The autosave uses the same atomic-write pipeline as manual saves.
3. The autosave shows in the slot UI but is not selectable for *save* (read-only) — it is selectable for *load*.
4. Commit: `Autosave on room transition.`

### Phase 7 — Polish, demo, reflection (~1.5 h)

1. Add the "saving..." badge that flashes for 30 frames after a save fires.
2. Tune the playtime counter — incrementing `playtime_seconds` per frame at `dt` is the right shape.
3. Add room-name labels to the world (so the demo video has something to read).
4. Record `demo.mp4`: 20 seconds, with the full save / autosave / quit / reload / continue loop visible.
5. Write `REFLECTION.md` (250 words).
6. Write `README.md` and `CREDITS.md`.
7. Commit: `Polish, demo video, reflection.`
8. Push.

---

## Suggested code layout

```
save-rpg/
├── main.py                      # game loop, player, rooms
├── save.py                      # GameState, capture/apply, write/read
├── migrations.py                # migration ladder
├── slot_ui.py                   # save-slot selector
├── pause_menu.py                # Esc menu (Save/Load/Quit)
├── levels/
│   ├── room_01.json
│   ├── room_02.json
│   └── room_03.json
├── saves/                       # created at runtime
│   ├── slot_01.json
│   ├── slot_01.json.bak
│   ├── slot_01.json.sha256
│   ├── slot_02.json
│   ├── slot_02.json.bak
│   ├── slot_02.json.sha256
│   ├── slot_03.json
│   ├── slot_03.json.bak
│   ├── slot_03.json.sha256
│   ├── autosave.json
│   ├── autosave.json.bak
│   └── autosave.json.sha256
├── assets/                      # CC0 sprites from Kenney (optional)
├── demo.mp4
├── README.md
├── REFLECTION.md
└── CREDITS.md
```

The split between `main.py`, `save.py`, `migrations.py`, `slot_ui.py`, and `pause_menu.py` is the *minimum* sensible separation. You may collapse `pause_menu.py` into `main.py` if you prefer; do not collapse `save.py` or `migrations.py` — those are the artefacts.

---

## Grading rubric (self-assessed)

Score your own submission against this rubric before submitting. If any criterion is below "passing," go back and fix it.

| Criterion | Failing | Passing | Strong |
|---|---|---|---|
| **State taxonomy** | `pygame.Surface` appears in a save file. | All four categories respected; `to_dict` returns only primitives. | A code comment in `save.py` labels each `GameState` field with its category. |
| **JSON discipline** | `pickle` used anywhere; files are one-line. | `json.dump` with `indent=2, sort_keys=True`; files are diffable. | UTF-8 explicit, `ensure_ascii=False` set, file ends with a newline. |
| **Atomic write** | Plain `open(path, "w")`. | `.tmp` + `fsync` + `os.replace`. | Plus `.bak` rotation done in the right order so a crash mid-save never loses both. |
| **Schema versioning** | No version stamp. | `schema_version` field present; one migration implemented. | Migrations dict + composer; covers v1 → v2 → ... cleanly. |
| **Checksums** | No checksum. | SHA-256 sidecar written and verified on load. | Sidecar is also atomically written; tampered files always fall back to `.bak`. |
| **Slot UI** | Save key writes to one hardcoded file. | Three numbered slots + autosave; cursor moves; overwrite confirmation works. | Plus relative timestamps ("3 days ago"), play-time, last-room name, autosave styled distinctly. |
| **Autosave** | Save fires every frame, or never. | Save fires on room transition; goes to a dedicated slot. | Plus an N-minute wall-clock fallback the player can toggle. |
| **Reflection** | Generic; cites no lecture or source. | 250 words; cites Lecture 1 and Lecture 3; names the migration. | Plus a concrete bug the writer found and fixed during testing. |

---

## Stretch goals

If you finish the core mini-project early and want to push further:

- **Implement `gzip`-compressed JSON saves.** The save path becomes `slot_01.json.gz`. Most of the code stays the same; only `open` becomes `gzip.open` with `"wt"`/`"rt"` modes.
- **Add a screenshot thumbnail to each save.** Capture a 64×36 surface, encode as base64 PNG (use `pygame.image.save` to a `BytesIO`, then `base64.b64encode`), embed in the JSON. The slot UI uses it as a thumbnail.
- **Wire the "delete slot" flow.** Pressing **D** on an occupied slot triggers a delete confirmation. On confirm, both `slot_N.json` and `slot_N.json.bak` are removed.
- **Add a saves-folder picker.** Make the saves directory user-configurable. Useful for "play test the migration on a copy" workflows.
- **Implement a "soft autosave" toggle.** Settings menu has Autosave: ON / OFF. Some players prefer to control checkpoint placement.
- **Add a v2 → v3 migration.** Split inventory into inventory + equipment, mimicking Exercise 2's v2 → v3.
- **Watch Jonathan Blow's *Why I Wrote My Own Save System* (linked in resources)** and write a 200-word note on which of his arguments apply to your tiny RPG and which do not (most won't — *The Witness* is a different scale).

---

## Why this matters

By Sunday you have shipped a save system that:

- Stores only persistent state (Lecture 1).
- Uses JSON for human-readable, diffable saves (Lecture 2).
- Versions the schema and migrates old saves forward (Lecture 3 §1-3).
- Survives a crash mid-write (Lecture 3 §4).
- Keeps a previous-good backup (Lecture 3 §5).
- Detects accidental corruption with SHA-256 (Lecture 3 §6).
- Autosaves on safe checkpoints (Lecture 3 §8).
- Presents a three-slot UI with overwrite confirmation (Challenge 2).

That feature set is the same one shipped by *Hollow Knight*, *Stardew Valley*, and *Celeste*. Your *game* is a tenth the size; your *save system* is roughly the same shape. The portability of this week's code is high: drop it into Week 11's capstone with minor renames and the capstone has the save system it needs.

Next week — Audio: Music, SFX, and Mixing — uses a *settings* file (volume per channel, music on/off) saved with the same atomic-write pattern you wrote this week. The save-system code is *engine infrastructure*; you wrote it once and keep it forever.

---

*If you find errors in this material, please open an issue or send a PR. Future learners will thank you.*
