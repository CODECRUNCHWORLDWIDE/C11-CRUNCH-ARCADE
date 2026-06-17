# Mini-Project — Bolt a Complete Save System onto a Prior-Week Game

**Time budget:** Saturday plus part of Sunday, ~10 to 12 hours.
**Weight:** 25% of the week.
**Deliverable:** The save-system code, a sample scene that exercises it, and a short recording (or written log) showing a v1 save being loaded and migrated to v2 in a running game.

---

## What you are building

Take any prior-week game (Week 8 audio prototype, Week 9 multiplayer cursor demo, or the Week 10 polish-pass build) and add a complete save system that:

1. **Persists at two cadences.** A manual save (player-triggered, written to slot 0, 1, or 2). An autosave (engine-triggered on every scene transition, written to a free-save slot).
2. **Uses two buckets.** A meta file (`meta.json`) for settings and key bindings. A run file per slot (`slot_00.save`, etc.) for the active playthrough.
3. **Survives a crash.** Writes are atomic via temp-file-plus-rename. Each successful write rotates the previous good save to `slot_NN.save.prev`. A failed load of `slot_NN.save` falls back to `slot_NN.save.prev`.
4. **Survives corruption.** Every save carries a SHA-256 integrity tag. A tampered or corrupted file is rejected on load and the rotation backup is used instead.
5. **Survives schema changes.** The schema starts at v1 with three fields. Mid-week you bump it to v2, adding a new field. The migration step is registered in the dispatch table; v1 saves on disk load into v2 codebases without data loss.
6. **Validates on load.** A GDScript `_validate_save_dict` (mirroring Pydantic on the Python side) inspects every field's type and range before any other code touches the loaded dict.
7. **Has tests.** A `pytest` suite in `test_migration.py` round-trips, mutates, validates, and migrates against the Python schema in `save_schema.py`.

The Godot side ships as `save_manager.gd` (the autoload singleton) plus a sample scene that demonstrates manual save, autosave, and the corruption-recovery flow. The Python side ships as `save_schema.py` plus `test_migration.py`. The two sides agree on the on-disk format; a save written by Godot must round-trip through the Python schema and back.

---

## The artefacts

```
mini-project/
├── README.md                 (this file)
├── save_manager.gd           (the Godot autoload singleton)
├── save_schema.py            (Pydantic v1 + v2 schemas, migration, validator)
├── test_migration.py         (pytest suite)
└── (in your project)
    ├── sample_scene.tscn     (you build this; demonstrates the loop)
    └── README-recording.md   (you write this; describes the recording)
```

You build the `sample_scene.tscn` and the `README-recording.md` in your own project tree, since the embedded scene depends on which prior-week project you chose.

---

## The schema

We adopt the cursor-demo schema from Lecture 1 as the canonical example. Adapt it to your prior-week project's actual fields; the *structure* of the manifest is what matters, not the specific fields.

**Meta bucket (`meta.json`):**

```json
{
  "version": 1,
  "settings": {
    "master_volume": 0.8,
    "music_volume": 0.6,
    "sfx_volume": 1.0,
    "fullscreen": false
  },
  "last_used_player_name": "Player 1"
}
```

**Run bucket v1 (`slot_NN.save` before the schema bump):**

```json
{
  "version": 1,
  "player_name": "Player 1",
  "current_score": 0,
  "session_start_timestamp": 0,
  "highest_score_this_session": 0
}
```

**Run bucket v2 (after the schema bump):**

```json
{
  "version": 2,
  "player_name": "Player 1",
  "current_score": 0,
  "session_start_timestamp": 0,
  "highest_score_this_session": 0,
  "current_level": "level_01"
}
```

The v1 → v2 migration adds `current_level = "level_01"` for any v1 save loaded into the v2 codebase. Mid-week, you "ship" v1, write a save, "ship" v2, and load the old save. The migration runs once; the in-memory state is correct; the next save writes the v2 shape back.

If your prior-week game has different progression fields (a Week 10 polish build with a high-score table, say), adapt the v2 schema to fit. The shape of the migration is what matters: one new field, one one-line migration function, one Pydantic v2 schema with `Literal[2]` on the version.

---

## What to record / write up

A 30- to 60-second screen recording (or, if you cannot record, a written transcript with screenshots) demonstrating:

1. **Manual save and load.** Player presses S; "saved!" indicator; player closes the game; player relaunches; saved state is restored.
2. **Autosave on transition.** Player crosses a transition (or any event you wire to "autosave"); the autosave file updates; player relaunches; autosave state is restored.
3. **Crash recovery.** You force-quit the game between writes (Cmd-Q on macOS during a save operation is the easiest way to reproduce; the temp file is left orphaned but the production file is untouched); player relaunches; the previous save loads.
4. **Schema migration.** You write a v1-formatted save by hand in a text editor (delete the `current_level` field, change `version` to 1); player launches; the v1 file is migrated to v2 in memory; the v2 write on the next save updates the file on disk.

The recording is short; the *demonstration* is the deliverable. A 30-second clip with all four flows is sufficient.

Submit the recording (as a `.mp4` of under 50 MB, or as `README-recording.md` with screenshots and a transcript) in the same directory as your save-manager files.

---

## Acceptance criteria

The mini-project passes if all of the following are true:

- **G1.** `save_manager.gd` is registered as an autoload named `SaveManager`. Calling `SaveManager.save_to_slot(0, state_dict)` from any scene works.
- **G2.** A v1 save on disk loads correctly in the v2 codebase. The `current_level` field has the default `"level_01"`.
- **G3.** A v2 save on disk loads correctly in the v2 codebase. The `current_level` field is the value from disk.
- **G4.** A corrupted save (one bit flipped) is rejected by the integrity check. The previous backup loads.
- **G5.** The meta and run buckets are in separate files. Corrupting one does not affect the other.
- **G6.** The Python `pytest` suite in `test_migration.py` passes on your machine.
- **G7.** The sample scene exercises at least manual-save and a load-from-disk on launch.
- **G8.** The recording (or written equivalent) demonstrates all four flows listed above.

Half-credit is available for partial deliveries. A working manual-save without atomic writes is worth more than a missing project; an autosave without migration is worth more than a working autosave that crashes on a v1 file.

---

## How to grade your own work before submitting

Run this checklist on your own machine before declaring the mini-project complete:

1. **Open the project. Start a new game. Press S to save.** Inspect the file at `OS.get_user_data_dir().path_join("saves/slot_00.save")` — does it have the expected JSON structure with a `payload` and an `integrity` field?
2. **Close the game. Relaunch. Press L to load.** Does the game continue from the save point?
3. **In a text editor, change `current_score` to `999999` in the save file** (also recompute the SHA-256 if you want; the homework's HMAC challenge would catch that case). Relaunch. Does the loader reject the tampered file (if you did not recompute the hash) or accept it (if you did)?
4. **Manually write a v1 save** (`{"version": 1, "player_name": "Test", "current_score": 100}`) at the slot path. Relaunch. Does the game load the save and treat it as v2 with the default `current_level`?
5. **Run `python3 -m pytest test_migration.py`.** Do all tests pass?

If all five steps work, you have a complete save system. If any of them fail, the failure is your bug; debug before submitting.

---

## Common rabbit-holes (avoid)

- **"I'll integrate Steam Cloud."** Out of scope. The save system you build this week is *cloud-portable* by design (atomic writes to a stable path); the Steam Cloud integration is configuration in the Steamworks portal, not code in your game. We mention it in Lecture 3 and survey it in `resources.md`; we do not implement it.
- **"I'll encrypt the save."** Out of scope this week. The HMAC challenge in `challenges/challenge-01-hmac-signed-saves.md` is the closest we go. Full encryption introduces a key-management story that is its own week of work.
- **"I'll port the whole thing to MessagePack."** Out of scope. JSON is fine for the mini-project. Challenge 02 covers pure-GDScript MessagePack as a stretch; if you finish the mini-project early, do that.
- **"I'll save the entire scene tree."** Re-read Lecture 1 section 2. Save the *progression*, not the *engine state*. Saving the scene tree is the path to a 500-MB save in three patches.
- **"I'll skip the migration because my game only has v1."** Then you do not learn the migration. Bump the schema mid-week; write a v1 save by hand; load it. The pattern is the deliverable, not the absence of pattern.

---

## A note on choice of base game

The mini-project assumes a prior-week project with at least *some* persistable state. The Week 9 cursor demo persists very little (just the player name and the score); the Week 10 polish-pass build persists more (player choice of which shader effects to apply, a high-score record). If you have neither, use the cursor demo from Week 9 and add a *score* field to give the save something interesting to do.

If you are taking the course out of order and have not built a prior-week game, the `mini-project/sample_game/` referenced in this README is *not* shipped — you have to build a minimal scene yourself. A 30-line scene with a player name field, a score counter, a save button, and a load button is sufficient. The save system is the deliverable, not the game.

---

## What the next week builds on

Week 12 (input remapping and accessibility) will persist key bindings, accessibility flags, and the user's font-size preference. These all go in your *meta* bucket; the run bucket is unchanged. The save system you ship this week is the substrate. Week 13 (audio polish) will persist the user's mixer preferences — also meta. Week 14 (game feel) will persist a "tutorial seen" flag — also meta. By Week 15 your meta bucket will have ten fields and your run bucket will be unchanged from this week.

The point is that the *meta bucket* grows over the course; the *run bucket* settles after this week. Investing the time now to get the meta bucket right pays back for the rest of the course.
