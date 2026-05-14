# Week 7 Homework

Six practice problems that revisit the week's topics. The full set should take about **5-6 hours** in total. Work in your Week 7 Git repository so each problem produces at least one commit you can point to later.

The work this week splits between *reading the file format* (problems 1-3) and *engineering its robustness* (problems 4-6). The mini-project assembles the whole thing; these homework problems are the parts.

Each problem includes:

- A short **problem statement**.
- **Acceptance criteria** so you know when you're done.
- A **hint** if you get stuck.
- An **estimated time**.

---

## Problem 1 — Audit a real game's `Player` for save fields

**Problem statement.** Take the `Player` class from your Week-6 mini-project (the juiced FSM-driven character). Open `main.py` (or wherever the class lives). Walk every attribute on `__init__` and annotate it with a comment indicating its category from Lecture 1 §2: `# PERSISTENT`, `# SESSION`, `# DERIVED`, or `# PRESENTATION`. Save the annotated file as `homework/p1_player_audit.py`. At the bottom, in a docstring, write a short summary: "N persistent fields, M session fields, K presentation fields. The save layer would store the persistent set."

**Acceptance criteria.**

- A file `homework/p1_player_audit.py` exists.
- Every attribute on `Player.__init__` has a `# CATEGORY` comment.
- The docstring at the bottom names the counts and lists the persistent fields explicitly.
- No category is empty. (If your Week-6 player has no derived state, write `# (none)` in that section.)

**Hint.** Velocity is session. `pygame.Surface` and `pygame.mixer.Sound` are presentation. Position and hp are persistent. Any `_t` timer measured in seconds is session. Animation clips are *derived* from a character-id plus a sprite-sheet path.

**Estimated time.** 30 minutes.

---

## Problem 2 — Round-trip equality test for `GameState`

**Problem statement.** Write a small unit test in `homework/p2_roundtrip_test.py` that does the following:

1. Constructs a `GameState` with non-default values for every field.
2. Calls `gamestate_to_dict` to convert to a dict.
3. Calls `json.dumps` and `json.loads` to round-trip the dict through a string.
4. Calls `gamestate_from_dict` to rebuild a new `GameState`.
5. Asserts the two `GameState` instances are equal field-by-field.

The test should run from the command line (`python homework/p2_roundtrip_test.py`) and print "PASS" or fail loudly with the first mismatched field.

**Acceptance criteria.**

- A file `homework/p2_roundtrip_test.py` exists and runs.
- The test exercises every field on `GameState` with a non-default value.
- A failure prints the field name and both values; success prints "PASS" with the field count.
- `python -m py_compile homework/p2_roundtrip_test.py` succeeds.

**Hint.** Dataclasses compare field-by-field with `==` out of the box. So `assert gs1 == gs2` is the whole test. The interesting work is constructing a `gs1` with rich-enough non-default values that you would catch a missing field in `gamestate_from_dict`. Include a multi-item inventory, a multi-key flags dict, and a non-zero `playtime_seconds`.

**Estimated time.** 45 minutes.

---

## Problem 3 — Hand-write a v0 → v1 migration

**Problem statement.** A *prior version of yourself* shipped a v0 of the RPG with this save format:

```json
{
  "pos": [200.0, 140.0],
  "hp": 4,
  "level": "level_01"
}
```

No `schema_version`, no `timestamp_iso`, no `playtime_seconds`, no inventory. The new code is v1 (the Lecture 1 §4 `GameState`). Write `migrate_v0_to_v1` that turns the v0 dict into a v1 dict. Include sensible defaults for the missing fields (timestamp `""`, playtime `0.0`, inventory `[]`).

Then write a small script `homework/p3_migrate_v0.py` that:

1. Writes a synthetic v0 save to `homework/v0_save.json`.
2. Reads it back, runs `migrate_v0_to_v1`, and prints the resulting v1 dict.

**Acceptance criteria.**

- A `migrate_v0_to_v1` function exists in `homework/p3_migrate_v0.py`.
- The migration transforms `"pos": [x, y]` into `"player_x": x` and `"player_y": y`.
- The migration adds defaults for every v1 field the v0 dict lacks.
- The migration sets `schema_version` to 1.
- The script runs and prints the migrated dict; a quick eyeball confirms all v1 fields are present.

**Hint.** The trick is that v0 stored position as a *list of two floats*; v1 stores them as two separate fields. The migration unpacks `pos = d.pop("pos")` and writes `d["player_x"] = pos[0]`. The `.pop` removes the old key so the v1 dict is *clean*. (Removing the key from the migration is OK; we are talking about a *legacy* v0 field that no v1 code reads. The Lecture 3 §3 "additive only" discipline applies to fields *we are keeping*; here we are absorbing v0 fields into v1 shape.)

**Estimated time.** 50 minutes.

---

## Problem 4 — Verify the atomic-write actually survives a crash

**Problem statement.** Write `homework/p4_atomic_write_test.py` that:

1. Implements the atomic-write pattern from Lecture 3 §4 in a function `atomic_write_json(path, payload)`.
2. Calls the function with a large payload (a dict with 1000 keys, say).
3. Mid-write — using a `multiprocessing.Process` child — has the *child* perform the write, then the parent kills the child with `proc.terminate()` after a 1 ms sleep (before the write can finish).
4. Inspects the file system: does `save.json` exist? Does `save.json.tmp` exist? What about both?
5. Repeats the kill-mid-write 100 times. Reports how often `save.json` is left in a *valid* state (parses as JSON) vs left missing vs left as a `.tmp` orphan.

**Acceptance criteria.**

- A file `homework/p4_atomic_write_test.py` exists and runs.
- The test reports a count out of 100: "valid: N, missing: M, tmp_orphan: K". The total is 100.
- `valid + missing` is 100 — there are never *truncated* `save.json` files (because of the atomic rename). The `tmp_orphan` count may be non-zero but is *harmless* — it just means the child died after writing the temp file but before the rename. The canonical `save.json` is never corrupt.
- A short reflection (a `homework/p4_note.md`, 50-100 words) on what the experiment proves about `os.replace`.

**Hint.** This is a *forensic* exercise. The point is to *see* that no matter when the child gets killed, the canonical `save.json` is either (a) the *old* contents, (b) the *new* contents, or (c) missing if it never existed — but *never* half-written. The `.tmp` orphan is a debris file you can `os.unlink` on game startup.

**Estimated time.** 70 minutes.

---

## Problem 5 — Checksum mismatch end-to-end

**Problem statement.** Write `homework/p5_checksum_e2e.py` that:

1. Implements `save_with_checksum(path, payload)` from Lecture 3 §6.
2. Implements `load_with_checksum(path)` likewise.
3. Round-trips a save through both, asserting the load returns the same payload.
4. Then *corrupts* the save file (open it, change one byte, write it back) and calls `load_with_checksum` again. The function should raise `ValueError("checksum mismatch")` — assert this happens.
5. Prints "PASS — checksums detect corruption" on success.

**Acceptance criteria.**

- A file `homework/p5_checksum_e2e.py` exists and runs.
- The clean round-trip succeeds silently.
- The corrupted-load attempt raises `ValueError` with `"checksum mismatch"` in the message.
- The script prints "PASS" only after BOTH assertions succeed.

**Hint.** Corrupting "one byte" is easier than it sounds. Open the JSON file in text mode, read it, replace `"player_x": 384.5` with `"player_x": 384.6`, write it back. The hash will not match. The exception will fire.

**Estimated time.** 40 minutes.

---

## Problem 6 — Compress and measure

**Problem statement.** Take a copy of `exercise-03-msgpack-vs-json-benchmark.py` and modify the workload: instead of the 20-item inventory and 30-flag world, generate **a 5000-item flag dict** (`flag_0001` through `flag_5000`, half `True` and half `False`). Run the benchmark and report the four rows: JSON, JSON+gzip, MessagePack, and MessagePack+gzip. (Yes, you can gzip MessagePack too. The gain is smaller than for JSON.)

Then write `homework/p6_compression.md` (75-125 words) summarising:

1. The four sizes-on-disk.
2. The compression ratio for each binary format.
3. Whether the result agrees with Lecture 2 §7's claim that JSON+gzip is competitive with MessagePack on size for typical game saves.
4. One sentence on which format you would pick for *this* specific workload.

**Acceptance criteria.**

- A file `homework/p6_compression.py` runs and prints the four-row table.
- The table includes byte counts for all four formats.
- The 5000-flag workload makes the gzip wins *obvious* (the JSON+gzip row should be at least 8x smaller than the raw JSON row).
- A `homework/p6_compression.md` exists with the four numbers and the one-sentence pick.

**Hint.** Generate the flag dict with `{f"flag_{i:04d}": (i % 2 == 0) for i in range(5000)}`. The MessagePack+gzip implementation is `gzip.compress(msgpack.packb(payload, use_bin_type=True))`. That is one line.

**Estimated time.** 55 minutes.

---

## What you should have at the end of homework

A `homework/` folder containing:

- `p1_player_audit.py` — your Week-6 player annotated by category.
- `p2_roundtrip_test.py` — a passing round-trip equality test.
- `p3_migrate_v0.py` — a v0 → v1 migration script.
- `p4_atomic_write_test.py` + `p4_note.md` — atomic-write stress test and reflection.
- `p5_checksum_e2e.py` — checksum integrity end-to-end.
- `p6_compression.py` + `p6_compression.md` — the compression measurement.

Each problem produces one or two commits. By Sunday this folder is a portfolio-worthy demonstration that you understand every layer of a real save system — state taxonomy, round-trip discipline, migration, atomic writes, integrity checks, and compression — in code you wrote, on numbers you measured.

The mini-project then assembles the parts.

---

*If you are short on time, prioritise problems 2 (round-trip), 4 (atomic write), and 5 (checksum). These three are the engineering core. Problems 1, 3, and 6 are valuable but slightly more peripheral.*
