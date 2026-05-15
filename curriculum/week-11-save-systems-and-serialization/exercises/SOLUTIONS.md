# Exercise Solutions — Week 11

This file walks through every exercise in the week. Each section follows the same shape: *what the exercise is testing*, *the design call*, *common student mistakes*, and *the marking criteria*. The actual solution code is in the corresponding `.py` or `.gd` file; this file is the editorial commentary.

Treat the exercises as cumulative. Each one builds on the substrate the previous ones established. By Exercise 06, you have ported the entire pipeline to GDScript.

---

## Exercise 01 — JSON Round-Trip

**File:** `exercise-01-json-roundtrip.py`

### What it tests

The simplest property of a serialisation scheme: that `parse(serialise(x)) == x` for the data you care about. JSON is loss-less for the types we use (strings, integers, lists of strings) and the exercise demonstrates that — both in memory and across a disk write.

### The design call

We use `json.dumps(..., sort_keys=True, indent=2)` for two reasons. `sort_keys=True` makes the output deterministic, which matters in Exercise 05 when we hash the bytes for integrity. `indent=2` makes the JSON readable in a text editor, which matters for the dev-build use case (QA hand-edits saves).

The dataclass is plain `@dataclass` with type-annotated fields. We *do not* yet validate on load; an unexpected key in the parsed dictionary would raise a `TypeError` from the dataclass constructor. Exercise 02 fixes that with Pydantic.

### Common mistakes

- **Forgetting `sort_keys=True`.** The round-trip still works, but the test loses determinism. Different runs produce different byte orders depending on Python's dict iteration order.
- **Writing to a temp variable and forgetting to assert equality.** Without the `assert loaded == original`, the test claims success even if the round-trip silently dropped the inventory.
- **Saving the dataclass directly via `dataclass`'s `__repr__`.** `repr(state)` is not JSON; it is Python source code. Use `asdict(state)` first.

### Marking criteria

| Criterion                                            | Points |
|------------------------------------------------------|-------:|
| `state_to_json` and `json_to_state` exist and round-trip | 2     |
| Disk round-trip with cleanup                         |   2    |
| `sort_keys=True` for determinism                     |   1    |
| Assertions catch a mutated round-trip                |   1    |
| Script prints what it did and ends with `OK`         |   1    |
| **Total**                                            | **7**  |

---

## Exercise 02 — Pydantic Schema

**File:** `exercise-02-pydantic-schema.py`

### What it tests

The *schema validation on load* discipline from Lecture 2 section 3. The save on disk is untrusted input; the loader must verify the parsed dictionary matches the schema before any other code sees it.

### The design call

We use Pydantic v2's `BaseModel` with `Field` constraints. The constraints carry semantic meaning that bare Python type hints lack: `current_score` is not just an `int`, it is an integer in `[0, 10_000_000]`. The bounds are derived from the game's design: ten million is more points than any legitimate game produces, so a save with that value is either a wild outlier (worth investigating) or a tampered file (worth rejecting).

`Literal[1]` on `version` (anticipating Exercise 04) is how Pydantic distinguishes schema versions. A v1 save's `"version": 1` cannot parse as `SaveV2` (which has `Literal[2]`); the loader uses this to dispatch to the appropriate migration step.

### Common mistakes

- **Using `pydantic.BaseModel` from Pydantic v1.** Pydantic v2 is a near-complete rewrite. `model_validate` (v2) replaces `parse_obj` (v1); `model_dump_json` (v2) replaces `.json()` (v1). The v1 API is deprecated but still works in v2 with deprecation warnings; check your imports.
- **Catching `Exception` instead of `ValidationError`.** Pydantic raises a structured `ValidationError` that lists every field that failed. Catching `Exception` loses the structure.
- **Forgetting that Pydantic's `model_validate_json` includes JSON parsing.** You do not need a separate `json.loads`; the model accepts raw JSON bytes.

### Marking criteria

| Criterion                                            | Points |
|------------------------------------------------------|-------:|
| Pydantic v2 `BaseModel` with at least three constrained fields | 2 |
| Valid round-trip works                               |   1    |
| At least three different corruptions are rejected    |   2    |
| Each rejection prints the offending field name       |   1    |
| Script prints what it did and ends with `OK`         |   1    |
| **Total**                                            | **7**  |

---

## Exercise 03 — MessagePack vs JSON

**File:** `exercise-03-msgpack-vs-json.py`

### What it tests

The empirical comparison of the two formats. Lecture 2 claimed MessagePack is 2x to 3x smaller and 2x to 4x faster. The exercise produces the numbers on the student's own machine and confirms the ratios.

### The design call

We build a payload that is representative — 100 inventory entries with three fields each, 50 quest flags, a small player block. The exact numbers do not matter; the *shape* matters. A payload of all integers makes MessagePack look maximally good (one byte per small int); a payload of all long strings makes the formats look more equal (both formats encode strings as length-plus-bytes).

The benchmark runs 200 iterations of parse and reports the average. On a 2022-era laptop, the JSON parse is ~150 microseconds and the MessagePack parse is ~50 microseconds — the 3x ratio Lecture 2 promised. On older or slower machines, the absolute times are higher but the ratio is preserved.

### Common mistakes

- **Comparing the wrong metric.** Bytes-on-disk and parse-time are two different metrics; do not collapse them into one "speed" number. Report both.
- **Timing the wrong thing.** A common mistake is to time `json.dumps`, not `json.loads`. We are interested in *load* speed because every game launch loads; *save* speed matters less because saves are infrequent.
- **Trusting a single iteration.** The first parse is slower than subsequent parses because of cache warming. Loop at least 100 times and average.

### Marking criteria

| Criterion                                            | Points |
|------------------------------------------------------|-------:|
| Representative payload (lists, dicts, nested types)  |   1    |
| Both formats round-trip                              |   2    |
| Sizes are reported                                   |   1    |
| Parse times are reported and averaged                |   2    |
| Final recommendation matches the lecture (dev = JSON, ship = MessagePack) | 1 |
| **Total**                                            | **7**  |

---

## Exercise 04 — Version Migrate

**File:** `exercise-04-version-migrate.py`

### What it tests

The *single-step migrations chained in a dispatch table* pattern from Lecture 2 section 4. The exercise defines a v1 schema, a v2 schema, a `migrate_v1_to_v2` function, and a loader that picks the right migration.

### The design call

The dispatch table is `MIGRATIONS: dict[int, Callable[[dict], dict]]`. Each entry is a single-step migration from version N to N+1. To migrate v1 to v3, the loader runs `MIGRATIONS[1]` then `MIGRATIONS[2]`. We do not write `migrate_v1_to_v3` even when it would be a one-line shortcut, because the day v4 ships the shortcut becomes a maintenance burden.

The migration function is *pure*: it does not mutate its input. The mini-project's tests rely on this property; the input is preserved for the post-migration validator.

### Common mistakes

- **Mutating the input dictionary.** Pydantic's `model_validate` requires a clean dict; passing a mutated v1 dict (with `version` updated to 2) is the kind of bug that surfaces only when the loader's call site changes.
- **Looping forever in the migration chain.** The safety counter catches this; without it, a typo in the migration table (`MIGRATIONS[1] = lambda x: x` — does not advance the version) causes an infinite loop.
- **Failing to handle unversioned legacy saves.** The convention is `if "version" not in parsed: parsed["version"] = 1`. Without this, the first save your game ever wrote is unloadable after the first patch.

### Marking criteria

| Criterion                                            | Points |
|------------------------------------------------------|-------:|
| Two `BaseModel`s with `Literal[1]` and `Literal[2]`  |   1    |
| `migrate_v1_to_v2` is pure (does not mutate input)   |   2    |
| Dispatch-table loader works                          |   2    |
| v1 file on disk loads via migration                  |   1    |
| v2 file loads directly without migration             |   1    |
| **Total**                                            | **7**  |

---

## Exercise 05 — Atomic Write

**File:** `exercise-05-atomic-write.py`

### What it tests

The three crash-survival primitives from Lecture 3: temp-file-plus-rename, SHA-256 integrity, and backup rotation. The simulated-crash test demonstrates that flipping a byte in `save.latest` causes the loader to fall back to `save.previous` and recover the player's prior progress.

### The design call

Canonicalisation matters: `json.dumps(payload, sort_keys=True, separators=(",", ":"))` is the byte form we hash. The same logical payload produces the same bytes on every machine and every run. Without `sort_keys=True`, Python's dict iteration order would change the hash and the integrity check would reject every save the moment it crossed a Python version boundary.

The envelope shape is `{"payload": ..., "integrity": "sha256:..."}` rather than embedding the hash inside the payload. The shape makes the hash trivially identifiable and the verification straightforward. An alternative is to put the hash in a separate file (`save.json` and `save.json.sha256`), which adds a write but lets non-Python tools recognise the format. Either works; the embedded version is the simpler default.

The backup rotation is the rule from Lecture 3 section 3: every successful write of `latest` is preceded by a rotation of the previous `latest` to `previous`. The loader tries `latest` first; on failure, falls back to `previous`. The cost is two extra renames per write.

### Common mistakes

- **Hashing the formatted JSON instead of canonical JSON.** A formatted JSON (with `indent=2`) has different bytes from a canonical JSON. Hashing the formatted version means a re-format invalidates the integrity tag. Always hash the *canonical* form.
- **Forgetting `fsync`.** Without `fsync`, the rename can succeed and the file's bytes can still be in the OS write-back queue. A power loss right after the rename leaves the production file pointing at not-yet-flushed bytes.
- **Using `os.rename` instead of `os.replace`.** `os.rename` raises on older Windows when the target exists. `os.replace` is the cross-platform "rename and replace" that works on every supported Python.
- **Not cleaning up the temp file on failure.** A crash between the temp write and the rename leaves an orphan `save.tmp`. The next successful write overwrites it, but until then there is a stale file on disk. Optional cleanup-on-startup is a polish item.

### Marking criteria

| Criterion                                            | Points |
|------------------------------------------------------|-------:|
| Temp-file-plus-rename pattern with `os.replace`      |   2    |
| `fsync` is called before the rename                  |   1    |
| SHA-256 integrity over canonicalised payload         |   2    |
| Rotation: latest -> previous on each successful write|   2    |
| Simulated crash recovers via the previous backup     |   2    |
| **Total**                                            | **9**  |

---

## Exercise 06 — Save Manager (GDScript)

**File:** `exercise-06-save-manager.gd`

### What it tests

The complete substrate, ported to GDScript. The autoload pattern (a singleton registered in Project Settings → Autoload) makes the manager callable from any scene without instantiation.

### The design call

The substrate mirrors the Python exercises one-to-one: the same envelope shape, the same SHA-256 tag (via `HashingContext`), the same three-file rotation (`latest`, `previous`, `temp`), the same single-step migration chain. The validator is the GDScript analogue of Pydantic — a hand-written `_validate_save_dict` that checks every field's type and range. Verbose, predictable, easy to audit.

`OS.get_user_data_dir()` gives the per-OS user-data directory. On macOS it is `~/Library/Application Support/Godot/app_userdata/<project>`; on Windows it is `%APPDATA%/Godot/app_userdata/<project>`; on Linux it is `~/.local/share/godot/app_userdata/<project>`. Saving to this directory means the saves survive the project being moved on disk.

### Common mistakes

- **Forgetting to register the autoload.** Without the autoload, `SaveManager.save_to_slot(0, ...)` is an undefined identifier. The fix is in Project Settings → Autoload, *not* in the script itself.
- **Calling `FileAccess.open` and forgetting to `close()`.** Godot does not flush until close. Open-without-close means the bytes are still in the engine's buffer when the rename happens; the rename publishes an empty file.
- **Using `JSON.parse_string` and not checking for `null`.** GDScript's JSON parser returns `null` on failure rather than raising. The check is `if parsed == null: push_error(...)`; without it, the loader silently produces a zero-keyed dictionary and the game initialises with default state.
- **Not duplicating the input dictionary in the migration step.** GDScript dictionaries are reference-typed; `var x = d` aliases the same dictionary. Use `d.duplicate(true)` to deep-copy.

### Marking criteria

| Criterion                                            | Points |
|------------------------------------------------------|-------:|
| Autoload-registered singleton with `save_to_slot` / `load_from_slot` | 2 |
| Atomic write (temp + rename via `DirAccess.rename`)  |   2    |
| SHA-256 integrity via `HashingContext`               |   2    |
| Backup rotation on each successful write             |   2    |
| `_validate_save_dict` covers every field             |   2    |
| `_migrate_v1_to_v2` matches the Python version       |   2    |
| **Total**                                            | **12** |

---

## Total points across all exercises

| Exercise                          | Points |
|-----------------------------------|-------:|
| 01 — JSON Round-Trip              |   7    |
| 02 — Pydantic Schema              |   7    |
| 03 — MessagePack vs JSON          |   7    |
| 04 — Version Migrate              |   7    |
| 05 — Atomic Write                 |   9    |
| 06 — Save Manager (GDScript)      |  12    |
| **Total**                         | **49** |

Convert to the gradebook with `(points / 49) * exercise_weight`. The exercises are 20% of the week; full credit at 49/49 is 20%, half credit at 24/49 is 10%.

---

## A final note on debugging

When a save round-trip fails, the bug is almost always one of:

1. **Determinism.** The same logical payload produced different bytes on save and load, breaking the integrity check. Fix: `sort_keys=True` on serialise, sort on hash.
2. **Encoding.** The file was written as bytes but read as text, or vice versa. Fix: pick one (text with `encoding="utf-8"`) and use it everywhere.
3. **The temp file outlived its purpose.** A crashed write left an orphan `save.tmp` that the next load picked up. Fix: do not look at `save.tmp` in the loader; ignore it.
4. **The migration ran twice.** A loader called `migrate_to_latest` on an already-migrated dict and the second call hit a state the migration could not handle. Fix: the loop in `migrate_to_latest` exits when `version == CURRENT_VERSION`; do not call the function on a value already at current.

When in doubt, `print(canonical_bytes(payload).decode())` and compare. The bug is in the bytes.
