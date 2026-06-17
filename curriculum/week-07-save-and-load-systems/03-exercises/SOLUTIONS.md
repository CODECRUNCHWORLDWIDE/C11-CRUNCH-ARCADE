# Exercises — Solutions and Common Bugs

The three exercise files in this folder ship with their bodies *filled in*. They are not blanks; they are reference implementations you read, run, and modify. This document is the *teardown* — what each exercise is teaching, what people commonly get wrong when they try to write it themselves, and which lines deserve a second look.

Open each `.py` file alongside the matching section here. Do not skip ahead to the "Common bugs" sub-section until you have run the file at least once and read every line.

---

## Exercise 1 — JSON save/load (`exercise-01-json-save-load.py`)

### What this exercise teaches

- The four-category state taxonomy from Lecture 1 §2, made concrete on a tiny Pygame sandbox.
- The `GameState` dataclass as the *contract* between the live game and the disk.
- The `capture_state` / `apply_state` bridge.
- The "presentation never saved" rule — `pygame.Surface` references do not appear in the save file.
- The "session state resets on load" rule — `player.vx`, `player.vy` go to zero on load.

### What "done" looks like

Open the game. Walk over a few coins. Press **S**. The HUD flashes "saved." Walk somewhere else, pick up more coins, then press **L**. The player teleports back, the extra coins respawn, and the inventory reverts to the saved counts. Confirm `save_ex01.json` exists in the working directory and is readable in a text editor.

### Common bugs

**Bug A — Inventory accumulates instead of replacing.**
Symptom: load restores you to the saved position, but your inventory keeps the items you picked up *after* the save.
Cause: `apply_state` does `inventory.update(gs.inventory)` without first calling `inventory.clear()`. The `update` merges on top instead of replacing.
Fix: always `.clear()` before `.update()` in `apply_state`. Document the discipline at the top of the function.

**Bug B — Coins do not respawn on load.**
Symptom: load restores position and inventory, but the field stays empty.
Cause: `apply_state` rebuilds the list but never marks any coin "alive again." Or, worse, the function uses the *existing* `coins` list and only marks the collected ones dead — leaving the *previously collected* ones (relative to the save) still dead.
Fix: `apply_state` calls `make_initial_coins()` to build a fresh list, then marks dead the indices in `gs.collected_coin_indices`. The fresh list is the source of truth.

**Bug C — `pygame.Surface` appears in the save.**
Symptom: `json.dump` throws `TypeError: Object of type Surface is not JSON serializable`.
Cause: the `Player` dataclass acquired a `sprite: pygame.Surface` field at some point and you `asdict(player)`'d into the save.
Fix: keep `GameState` separate from `Player`. `GameState` is JSON-safe primitives; `Player` is the live in-memory class. Lecture 1 §4 covers this.

**Bug D — Pressing S to save also moves the player.**
Symptom: every time you save, the player drifts downward.
Cause: the **S** keybind clashes between save and move-down.
Fix: see lines 230-238 of the exercise — the held-S movement only triggers when Shift is also held. Awkward but pedagogically pointed: this is the kind of UX clash you discover the moment a real save system meets a real game.

**Bug E — The save file is one giant line.**
Symptom: the JSON works but you cannot read it.
Cause: missing `indent=2` flag on `json.dump`.
Fix: pass `indent=2, sort_keys=True`. The flags cost ~20% of encode time and are worth it for a file you may need to debug in a text editor.

### Things to notice in the code

- Line ~95 (`@dataclass GameState`): no methods, no behaviour, just data. The class is a *record*, not an object.
- Line ~165 (`def capture_state`): reads from live objects, returns a `GameState`. Pure function. Easy to test.
- Line ~178 (`def apply_state`): writes to live objects, no return. The `vx = 0.0` and `vy = 0.0` lines are the "session state resets on load" rule made code.
- Line ~244 (the **L** keybind handler): wraps `load_from_disk` in a `try`/`except FileNotFoundError`. Loading must never crash the game.

### Variations worth trying

1. Add a `playtime_seconds` field to `GameState` and increment it every frame. Confirm the round-trip preserves it within ~1 second of accuracy.
2. Add a third coin colour and a fourth coin position. Save, load, confirm the new colour is respected.
3. Hand-edit `save_ex01.json` in a text editor — change `player_x` to a wildly different value. Reload the game and press **L**. The player should teleport to your edited value. This is the "local saves are player-owned" principle from Lecture 3 §7.

---

## Exercise 2 — Versioned saves with migration (`exercise-02-versioned-saves-with-migration.py`)

### What this exercise teaches

- The `schema_version` integer as the first byte of every save (Lecture 3 §1).
- The migration ladder: `migrate_v1_to_v2`, `migrate_v2_to_v3`, ... one function per step (Lecture 3 §2).
- The `MIGRATIONS` dict + `migrate_to_current` composer.
- The "additive only in practice" rule — new fields default to safe values; old fields stay (Lecture 3 §3).
- How a corrupted version stamp is detected and reported.

### What "done" looks like

Open the demo. Three slot panels show three saves on disk — one v1, one v2, one v3. The left half of each panel shows the raw JSON; the right half shows the migrated v3 `GameState`. The status line above each panel reads "migrations: v1 -> v2 then v2 -> v3" for slot 1, "migrations: v2 -> v3" for slot 2, and "(no migration needed)" for slot 3.

Press **X** to corrupt slot 1's `schema_version` to 99. The slot 1 panel turns red and reads `ERROR: no migration from v99`.

### Common bugs

**Bug A — Migrations run forever.**
Symptom: `migrate_to_current` loops; the program hangs.
Cause: a migration function forgot to update `d["schema_version"]`. The composer reads the version to decide whether to stop; if the version never advances, the loop is infinite.
Fix: every migration sets `d["schema_version"] = NEW_VERSION` *before* returning. Add an assertion at the top of `migrate_to_current` that checks for forward progress and raises if it does not happen.

**Bug B — `eq_sword_iron` ends up in the v3 inventory instead of equipment.**
Symptom: a v1 save loads, and after migration the `inventory` list still contains `eq_*` items.
Cause: the v2-to-v3 migration is supposed to scan the inventory and move `eq_*` items out. Either the predicate is wrong (`startswith("eq")` vs `startswith("eq_")`) or the migration runs in the wrong order.
Fix: confirm the migration filter is `str(it.get("id", "")).startswith("eq_")`. Add a print statement inside the migration to see what it does.

**Bug C — Saving and re-loading slot 1 leaves it as v3 on disk.**
Hold on. That is a *different exercise's* bug — Exercise 2 writes only synthetic saves, it never *saves out* a migrated state. If you accidentally added a "save current state back to disk" feature, you converted the v1 save into a v3 save on disk. The slot 1 panel would then show v3 with no migrations needed. That is correct behaviour for Exercise 2 *if* you intended it — but the exercise's pedagogy depends on the slot 1 file *staying* v1 on disk so you can re-test the migration. Press **1** to rewrite it as v1.

**Bug D — The migration UI shows the wrong list.**
Symptom: the "migrations fired" line says `v1 -> v2` but the migrated state clearly went through both.
Cause: the composer captures fired migrations into a list that is shared across calls (a mutable default argument or a module-level list).
Fix: `fired: list[str] = []` is a local variable inside `migrate_to_current`. Never a default argument.

### Things to notice in the code

- The three `make_v*_save()` functions are *fixtures*, not part of the migration framework. They exist only to seed the demo. In real code you would not have these; you would inherit old saves from real players.
- `MIGRATIONS` is keyed by the *from* version. The dict's `KeyError` when a version is missing is exactly the failure we want.
- The composer returns a list of fired migration names. This is useful both for the UI and for *telemetry* — in a real game you log "migrated v1 save for user X."

### Variations worth trying

1. Add a v4 schema that renames `coins` to `gold`. Write `migrate_v3_to_v4`. The trick: even though we are "renaming," the old `coins` field stays in the dict (the "additive only" rule). The new code stops reading `coins` and reads `gold` instead.
2. Make `migrate_to_current` return the migration *count* in addition to the names. Use it as a metric you would post to a backend.
3. Corrupt slot 2's `schema_version` (e.g. to a string `"two"` instead of `2`). Confirm the composer raises a clear error.

---

## Exercise 3 — MessagePack vs JSON benchmark (`exercise-03-msgpack-vs-json-benchmark.py`)

### What this exercise teaches

- How to write a small, honest micro-benchmark using `time.perf_counter` and `statistics.median`.
- The actual size/speed numbers on *your* machine for JSON, JSON+gzip, and MessagePack.
- That JSON+gzip is competitive with MessagePack on size (Lecture 2 §7).
- That MessagePack is ~3x faster on encode/decode but requires a third-party pip install.

### What "done" looks like

Run the script. You see a table:

```
format          bytes  encode_us  decode_us
JSON              612      25.30      29.80
JSON+gzip         168      69.40      51.20
MessagePack       344       8.10       9.40
```

Numbers will differ by ~30% per machine; ratios are stable.

### Common bugs

**Bug A — The medians swing wildly between runs.**
Symptom: rerun the script and JSON encode goes from 25 µs to 38 µs.
Cause: `ITERATIONS` is too low, or other processes are eating CPU.
Fix: bump `ITERATIONS` to 100,000 (the script runs in ~10 seconds). Close Spotify and your browser. Re-run.

**Bug B — MessagePack benchmark crashes with `ImportError`.**
Symptom: a Python traceback ending in `ModuleNotFoundError: No module named 'msgpack'`.
Cause: the package is not installed in your virtual environment.
Fix: `pip install msgpack`. The script *already* handles the missing-package case gracefully — it skips the MessagePack row and prints "MessagePack skipped: `pip install msgpack` to enable." If you are seeing a traceback, you have edited the gracefully-skipped import block.

**Bug C — JSON+gzip is *bigger* than raw JSON.**
Symptom: the gzip row shows more bytes than the JSON row.
Cause: your payload is too small. gzip adds ~20 bytes of header overhead, so a 50-byte payload compresses to ~70 bytes. Below ~200 bytes of input, gzip is a net loss.
Fix: this is *correct* behaviour. The script's default payload is ~600 bytes, where gzip wins. If you shrunk the payload (removed the inventory and flags), you reproduced the small-payload edge case. Restore the default workload.

**Bug D — The "encode_us" is suspiciously low (< 1 µs).**
Symptom: encode times under 1 microsecond.
Cause: the Python interpreter is hoisting the call out of the loop or caching the result. Either you removed the warm-up or the function being benched is `lambda: None`.
Fix: confirm each call inside the lambda does real work — `lambda: json.dumps(payload, sort_keys=True).encode("utf-8")` is the shape. The `.encode("utf-8")` matters; without it you are timing the unicode conversion, not the full encode.

**Bug E — The script imports `msgpack` even though I do not have it.**
Symptom: the top of the file has `import msgpack` and the script crashes immediately.
Cause: you bypassed the `try`/`except ImportError` block.
Fix: the file is shipped with the right import shape. Do not edit lines 60-67.

### Things to notice in the code

- `time.perf_counter()` not `time.time()`. The former has nanosecond resolution; the latter does not.
- `statistics.median(samples)` not `mean`. Median is robust to outliers (GC pauses, OS interrupts).
- The `bench_format` driver runs *warm-up* iterations before measuring. Without warm-up, the first 50 iterations include cold-cache and JIT effects.
- The output table uses fixed-width formatting (`{value:>10.2f}`) — eyeballable in a terminal.

### Variations worth trying

1. Add a fourth row for `pickle`. Confirm it is *fast* and produces a *small* file — and then re-read Lecture 1 §7 to remember why we do not use it.
2. Shrink the workload (one-item inventory, one-flag world) and confirm the gzip row gets *worse* on size and *much* worse on speed.
3. Inflate the workload (200-item inventory, 500-flag world) and confirm gzip *crushes* raw JSON on size while losing ~3x on speed. This is the Lecture 2 §7 finding made empirical.
4. Add a `struct.pack` custom-binary row. Watch yourself reinvent half of MessagePack. Internalise Lecture 2 §4.

---

## How to extend these exercises into your own week

The exercises are *infrastructure*. The mini-project assembles them into a real save system. Specifically:

- The `GameState` from Exercise 1 + the migration ladder from Exercise 2 + the format choice from Exercise 3 = the save layer of the mini-project.
- The atomic-write, backup-chain, and checksum patterns from Lecture 3 §4-6 are *new* in the mini-project; they do not appear in the exercises. The exercises are deliberately incomplete on this axis so the mini-project has substantive new work.

Read the mini-project README before you write any save code outside these exercises. It tells you the exact file shape and acceptance criteria. The exercises are the parts; the mini-project is the assembly.

---

*If you find errors in these solutions or the exercises themselves, please open an issue.*
