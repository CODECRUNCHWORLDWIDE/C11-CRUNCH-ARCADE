# Week 11 Homework

**Three problems plus a 500-word write-up.** Budget about 4 to 6 hours. The problems are graded; the write-up is graded harder. The whole homework is 25% of the week.

The problems below are independent of the mini-project. They are graded individually; the mini-project is graded as a single artefact at the end of the week.

---

## Problem 1 — Design the save manifest for a non-trivial game

Pick a published game whose progression you know well. (Suggestions: *Stardew Valley*, *Hollow Knight*, *Hades*, *Slay the Spire*, *Dead Cells*. Avoid games where the save format is publicly documented in detail; the exercise is the design, not the recall.)

Produce a `problem-01-save-manifest.md` that contains:

1. **A two-bucket manifest.** Meta state and run state in two separate JSON-shaped schemas. Use Pydantic v2 syntax (`class StardewMeta(BaseModel): ...`) for the schemas; include field types and reasonable `Field(min/max)` constraints.
2. **The save-point pattern.** Pick one of the four (manual / autosave / quicksave / checkpoint) or a hybrid; defend the pick in one paragraph. The defence should reference the game's loop, not just "it feels right."
3. **The write cadence estimate.** How many writes per hour of gameplay? Round to a power of ten; the rough magnitude is what matters.
4. **The "what we deliberately do not save" list.** Five items. Each item with a one-sentence justification of why it is reconstructible from what *is* saved.

The schemas do not need to round-trip a real save from the actual game. They are *designs*, not implementations. We are testing whether you can produce a save manifest, not whether you can reverse-engineer one.

### Marking — Problem 1

| Criterion                                            | Points |
|------------------------------------------------------|-------:|
| Both buckets present with typed fields               |   3    |
| Save-point pattern defended with reference to game loop |   2    |
| Write-cadence estimate is order-of-magnitude reasonable |   1    |
| "Not saved" list has five items with rationales      |   3    |
| File compiles as a Pydantic v2 module (the schemas import without error) | 1 |
| **Total**                                            | **10** |

---

## Problem 2 — Migrate v2 to v3

Take the v2 schema from Exercise 04 (the cursor-demo `SaveV2` with `player_name`, `current_score`, `session_start_timestamp`, `highest_score_this_session`, and `current_level`). Imagine the game has shipped, and now in development you need to add a new feature: **inventory**. The v3 save schema adds an `inventory: list[dict[str, int]]` field where each dict is `{"item_id": <string>, "count": <int>}`.

Produce `problem-02-migrate-v2-to-v3.py` that:

1. Defines `SaveV3` (a Pydantic model) with the new field.
2. Defines `migrate_v2_to_v3(v2: dict) -> dict` that adds an empty inventory list to v2 saves.
3. Registers the new migration in the `MIGRATIONS` dispatch table.
4. Demonstrates: a v1 save on disk loads through the chain (v1 → v2 → v3), a v2 save on disk loads through one migration step, a v3 save loads without migration.
5. Includes assertions that prove all three paths produce equivalent in-memory state, modulo the inventory field's default-vs-explicit value.

The script must run with `python3 problem-02-migrate-v2-to-v3.py` and print `OK` on success.

### Marking — Problem 2

| Criterion                                            | Points |
|------------------------------------------------------|-------:|
| `SaveV3` schema with the new field constrained       |   2    |
| `migrate_v2_to_v3` is pure (does not mutate input)   |   2    |
| Migration table updated correctly                    |   1    |
| All three load paths demonstrated                    |   3    |
| Assertions verify the chain produced correct state   |   1    |
| Script runs and prints `OK`                          |   1    |
| **Total**                                            | **10** |

---

## Problem 3 — Crash-test your atomic write

Take Exercise 05's `write_atomic_with_rotation` and write a *crash-injection test* that proves the atomicity guarantee holds. The test uses Python's `os.fork` (on POSIX) or a subprocess (cross-platform) to simulate a crash at three specific moments:

1. After the temp file is written but before the rotation rename.
2. After the rotation rename but before the publish rename.
3. After the publish rename but before any in-process bookkeeping completes.

For each moment, the test:

- Starts with `save.latest` containing a known good "previous" state.
- Forks (or spawns a subprocess) that invokes `write_atomic_with_rotation` with a "new" state, configured to crash at the chosen moment via a `crash_after: str` parameter you add to the function.
- Waits for the child to die.
- In the parent, calls `load_with_fallback` and asserts that the loaded state is *either* the known good previous *or* the new state — never a half-written file, never an unreadable file.

Produce `problem-03-crash-test.py`. The script must run on macOS and Linux (Windows-only solutions are not accepted; use `os.fork` or `multiprocessing` to be cross-platform). It must run for under 30 seconds total and end with `OK` if all three injection points pass.

A passing test does not prove correctness in all cases (you cannot test every possible crash moment). It proves the *common* failure modes are handled and gives confidence in the implementation.

### Marking — Problem 3

| Criterion                                            | Points |
|------------------------------------------------------|-------:|
| Crash injection works at all three moments           |   3    |
| Each injection demonstrably terminates the writer process |   1 |
| The parent recovers either the new or the previous   |   3    |
| No iteration ever loads a half-written file          |   3    |
| Script runs under 30 seconds on a typical machine    |   1    |
| Script prints `OK`                                   |   1    |
| **Total**                                            | **12** |

---

## Write-up — 500 words on the save-format-is-forever problem

Submit `homework-writeup.md`, ~500 words. The prompt:

> *"A save format is a contract with your future self." Lecture 2 made this claim. Pick a published game that has, over its life, ended up patching, migrating, or breaking its save format. Describe what happened (one paragraph). Describe the consequences for players (one paragraph). Describe what the developer would have had to do differently in version 1.0 to avoid the consequence (one paragraph). End with a sentence on what *you* will do differently in your own projects as a result.*

Suggested games to write about (each has documented save-format incidents in publicly available patch notes or developer blogs):

- *No Man's Sky* (multiple post-launch save format changes; community-built save editors broke and were rebuilt).
- *Minecraft Java Edition* (the chunk format has changed across major versions; backwards compatibility was a multi-year engineering effort).
- *Skyrim* (the `.ess` format was extended in patches; mods sometimes wrote to fields the engine did not yet handle).
- *Stardew Valley* (the save format has accumulated a `version` field over time; ConcernedApe has spoken about migration mistakes in interviews).
- *Crusader Kings 3* (DLC introduces new gameplay systems that the save format had to absorb).

Or pick another game you know well. The criterion is that the save-format change is *documented* somewhere you can cite, not just inferred.

### Marking — Write-up

| Criterion                                            | Points |
|------------------------------------------------------|-------:|
| Specific game named with citation                    |   2    |
| Save-format incident clearly described               |   3    |
| Player-consequence paragraph                         |   2    |
| Developer-side what-should-have-happened paragraph   |   3    |
| Final sentence on personal practice                  |   1    |
| Within 50 words of the 500-word target               |   1    |
| **Total**                                            | **12** |

---

## Total points

| Component             | Points |
|-----------------------|-------:|
| Problem 1             |  10    |
| Problem 2             |  10    |
| Problem 3             |  12    |
| Write-up              |  12    |
| **Total**             | **44** |

The homework is 25% of the week's grade. `(points / 44) * 25` is your contribution to the week's overall score.

---

## Submission

Submit a single directory `week-11-homework/` containing:

```
week-11-homework/
├── problem-01-save-manifest.md
├── problem-02-migrate-v2-to-v3.py
├── problem-03-crash-test.py
└── homework-writeup.md
```

Compile-check the Python files with `python3 -m py_compile <file>` before submitting. Both Python problems should run end-to-end and produce an `OK` line. The graders will run each script; a failure to even *start* counts as zero for that problem.

---

## A note on collaboration

The homework is individual. You may discuss approaches with classmates (the design questions in Problem 1 and the write-up especially benefit from peer feedback), but the artefacts you submit must be your own work. Two students submitting identical Pydantic schemas in Problem 1 is suspicious; identical write-ups is grounds for a zero on the homework.

The exercises and the mini-project allow more collaboration; the homework is the individual checkpoint.
