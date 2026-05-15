# Week 11 — Save Systems and Serialization

Last week the GPU started doing your bidding. Three fragment shaders bolted onto a Week 9 multiplayer demo turned a flat prototype into something that read as a finished game. A screen-shake, a hit-flash, and a one-shot dissolve transition — the polish tripod — were the deliverable, and the toolbox of eleven `.gdshader` files is the artefact you keep. This week we leave the GPU and the rendering frame entirely behind and open the slowest, most error-prone, most often-shipped-broken subsystem in a game: the part that writes the player's progress to disk.

A save system sounds boring. It is not. It is the subsystem that, when it fails, deletes thirty hours of a player's life. It is the subsystem that gets read on the cold launch path of every session, so its parser has to be fast. It is the subsystem that survives across patches — version 1.4's save file has to load in version 1.5 with new fields added — and across hardware — the same save has to round-trip between a Steam Deck and a Windows desktop on Steam Cloud. And it is the subsystem where a 20-line shortcut taken in week one of development calcifies into a six-month migration project the day the game ships its first DLC. Saves are the place where games most often go wrong precisely because they look easy.

The single best free reading on the topic is the *Godot 4.x* "Saving games" tutorial at [docs.godotengine.org/en/stable/tutorials/io/saving_games.html](https://docs.godotengine.org/en/stable/tutorials/io/saving_games.html) — the engine's own production reference, with the three approaches (config files, JSON, custom resources) laid out side by side. The *MessagePack specification* at [github.com/msgpack/msgpack/blob/master/spec.md](https://github.com/msgpack/msgpack/blob/master/spec.md) is the canonical reference for the most common compact binary format shipped games actually use. The *Pydantic v2* documentation at [docs.pydantic.dev/latest/](https://docs.pydantic.dev/latest/) is the canonical reference for schema-validated Python parsing — the tool every Python tooling pipeline in a modern studio uses on the loader side. And the *Steamworks documentation on Steam Cloud* at [partner.steamgames.com/doc/features/cloud](https://partner.steamgames.com/doc/features/cloud) is the canonical reference for the cloud-save service you will eventually integrate against. Four free sources, all linked in `resources.md`, all cited in the lectures.

By Sunday you take a small game from a prior week — Week 8's audio prototype, Week 9's networked cursor demo, or the Week 10 polish-pass build are all good candidates — and bolt on a complete save system. The system supports a manual save slot, an autosave triggered on level transition, a v1 format, a v2 format, and a migration path that loads v1 saves into v2 memory without data loss. It writes atomically. It validates on load with Pydantic on the Python tools side and a hand-written schema check on the GDScript side. It survives corruption. It is, in other words, a save system that would survive a real player base.

This week is editorial in tone because the topic is full of well-meaning shortcuts that ship as foot-guns. *Pickle* in Python and *BinaryFormatter* in .NET are convenient for an afternoon and dangerous for the next decade — both deserialise to arbitrary objects, both execute attacker-controlled code, both have been the root of remote-code-execution CVEs in shipped products. We name them. We refuse them. We do not bury the warning in a footnote.

## Learning objectives

By the end of this week, you will be able to:

- **Choose** between a manual-save-point design and an autosave-on-transition design, and **defend** the choice given a concrete game's loop. Manual saves push the responsibility to the player and reward planning; autosaves remove that cognitive load at the cost of larger save files and more failure surface. Most modern games ship both. You will know which kind a Dark Souls bonfire is (a hybrid: manual checkpoint trigger, autosave write), which kind a Stardew Valley bed-end-of-day is (autosave on transition), and which kind a roguelike permadeath is (autosave on every action). The three loops produce three different file-write cadences and three different failure modes.
- **Pick** a save file format that matches the game's stage of development, and **state the trade-off**. JSON for prototypes, dev builds, modding-friendly games, and anything where the QA team needs to hand-edit a save to repro a bug. MessagePack for shipped builds that need a 2x to 3x size reduction without giving up cross-platform compatibility. Godot's built-in binary `Resource` format for projects that live entirely inside Godot's type system. Protobuf for cross-engine pipelines (server in Go, client in Godot) where schema-versioning is a first-class concern. You will write at least JSON and MessagePack, read about the others, and be able to defend your pick.
- **Refuse** any code that calls `pickle.load` on user-controlled data, `BinaryFormatter.Deserialize` on .NET, or `yaml.load` without the `SafeLoader`. All three are remote-code-execution primitives. You will know the CVE numbers for the most famous incidents (CVE-2017-12852 for Python's Pickle-in-Ansible exposure, CVE-2017-9805 for the BinaryFormatter-flavoured Struts attack) and the standard talking point: *deserialisation of attacker-controlled bytes into arbitrary types is, by construction, code execution*. The mitigation is to *not* use a format that supports it.
- **Version** a save file's schema with a top-level integer `version` field and an explicit migration table that maps `(from_version, to_version) -> migration_function`. You will write a v1 schema, a v2 schema (adding a new field with a sensible default), and a `migrate_v1_to_v2` function. You will know why a *single-step migration table* beats both "always-load-latest" branching and "rewrite every load" duplication.
- **Validate** a parsed save in memory before letting any game code touch it. In Python, with Pydantic v2's `BaseModel.model_validate(parsed_dict)`. In GDScript, with a hand-written `_validate_save_dict(d)` function that checks every field's type and range. Validation is the difference between "the player's save file looked fine but their gold count is now negative two billion" and "the loader rejected the file and offered to load the most-recent-good backup."
- **Survey** the three big cloud-save services — *Steam Cloud* on Steam, *Google Play Saves* on Android, *iCloud Key-Value Storage* and *iCloud Documents* on Apple platforms — at the conceptual level. You will not implement any of them this week (each requires platform-specific SDKs, store accounts, and signing keys), but you will know which API call goes in which place, what each service guarantees about consistency, and which one's quota and conflict-resolution model is the most foot-gun-laden (it is, for the record, Steam Cloud, whose silent-overwrite-on-conflict default has eaten more saves than any other single design decision in PC games).
- **Write** to disk atomically using the temp-file-plus-rename pattern. Never write directly to the production save path; always write to a sibling temp file in the same directory, `fsync` it, then `rename`. On POSIX `rename` is atomic; on Windows `MoveFileEx` with `MOVEFILE_REPLACE_EXISTING` and `MOVEFILE_WRITE_THROUGH` is the equivalent. The pattern is the single change that eliminates ~95% of "my save is corrupted" reports.
- **Detect** corruption with an integrity check. The simple version is a CRC32 or SHA-256 of the payload, stored alongside the payload, verified on load. The full version is a *signature* (HMAC-SHA-256 with a per-install secret key) to prevent casual tampering on cheating-relevant fields. You will implement the simple version this week; the signature variant is a stretch challenge.
- **Recover** from corruption by keeping a most-recent-good backup. Every successful load promotes the loaded file to `save.latest`. Every write rotates `save.latest` to `save.previous` before writing `save.latest`. On a load failure of `save.latest`, the loader falls back to `save.previous`. The rotation is two extra rename calls and the difference between "game crashes on launch" and "game loads the autosave from twelve minutes ago."
- **Cite** the four free references — *Godot 4.x* saving-games docs, *MessagePack* spec, *Pydantic v2* docs, *Steamworks Steam Cloud* docs — and explain which is for the engine integration, which is for the on-disk format, which is for the loader-side validation, and which is for the cloud-replication layer.

## Prerequisites

This week assumes you have completed **Weeks 1-10**. Specifically:

- You have a working Godot 4.x install (4.2 or newer). Godot 4.2 ships `FileAccess`, `DirAccess`, and `JSON.parse_string` / `JSON.stringify`, which is what you will use for the GDScript half of the week. No external Godot plugins are needed.
- You have Python 3.11+ installed with `pip` working. The Python tools half installs three packages: `pydantic` (v2.x), `msgpack`, and `pytest`. Everything else is in the standard library.
- You have at least one prior-week mini-project in a state you can extend. Week 8 (audio), Week 9 (multiplayer cursor), or the Week 10 polish-pass build are all suitable starting points. The worked example uses a stripped-down Week 9 cursor demo with three persisted fields (player name, score, latest level). You do not have to use that one; you can use yours.
- You are comfortable enough with GDScript to write a class with typed members, attach a script to an autoload singleton, and call a function across scenes. Week 5 (state machines) covered the autoload pattern; we lean on it for the `SaveManager` singleton.
- You have read the Godot "Saving games" docs page once before Monday. Twenty minutes; it is short and dense, and it sets the vocabulary the lectures use.

If any of those are shaky, do the previous week's mini-project before continuing.

## Topics covered

Lecture 1 — When and what to save:

- The taxonomy of save points. *Manual* save points (the player chooses); *autosave* on transition (the engine chooses); *quicksave* (a key binding for the impatient); *checkpoint* (a hybrid — the engine chooses *when*, the player chose to *trigger*). Each pattern produces a different file-write cadence and a different player-trust contract. We name each one with a shipped example.
- The cost of saving frequently. A save write is a disk I/O on the main thread by default; on an SSD the cost is sub-millisecond and invisible, on a slow USB drive it is 200 ms and a visible stall. Autosaves on transitions cost nothing perceptible because transitions already have a loading screen; autosaves *during* gameplay either run on a thread or risk a frame hitch. Both options exist; the latter is more work to do correctly.
- What to actually persist. The principle is: persist the *minimum derivable to reconstruct the player's progression and intent*, not the entire game state. A character's HP at the last save point — yes. The position of every projectile in mid-flight — no. The principle pays for itself the first time a save format change requires migrating a million saves; small saves migrate fast.
- The two-bucket model: *meta* state (settings, key bindings, achievements, run history) and *run* state (the current playthrough). Meta is small, slow-changing, written on every settings panel close. Run is large, fast-changing, written on checkpoints. We keep them in two files. Settings corruption should never delete the run; run corruption should never delete settings.

Lecture 2 — Formats, schemas, and the migration story:

- JSON, the lingua franca. Every language reads it, every text editor edits it, every git diff is meaningful. The cost is size (a `float64` is 17 characters as ASCII versus 8 bytes binary) and parse speed (JSON parsers are fast but not free). Use it for dev builds and modding-friendly releases.
- MessagePack, the JSON-shaped binary. Same data model as JSON, 2x to 3x smaller on disk, 2x to 4x faster to parse. Use it for shipped builds where the player should not be hand-editing saves. The spec is short, the library support is universal, and the design intent is *"binary JSON without giving up portability."*
- Godot's built-in `Resource` save (`ResourceSaver.save`, `.tres`/`.res`). The native format for an all-Godot project. `.tres` is text (good for git, bad for tampering resistance); `.res` is binary (the opposite). Convenient when every saved object is already a Godot `Resource`; awkward when half the save lives in plain dictionaries.
- Protobuf, the schema-first option. You write a `.proto` schema file; the compiler generates loader code in every language you ship to. The right choice for a project where the same save round-trips between a Go server and a Godot client, or where backwards/forwards compatibility is a contract with QA. Heavier toolchain than MessagePack; lighter than fully custom binary.
- The two formats we *refuse*. **Pickle** in Python: deserialises to arbitrary callables; loading an attacker's pickle is loading their `__reduce__`-returned code. **BinaryFormatter** in .NET: same problem, same root cause, an entire CVE category named after it ("insecure deserialisation"). Both are deprecated by their own vendors. Microsoft has explicitly deprecated `BinaryFormatter` in .NET 5+; the Python core team has CVE-disclaimed `pickle` in the standard library docs for two decades.
- Versioning, in the small. Every save file carries a top-level integer `version` field. Adding a field is a minor version bump and a migration that fills the field with a default. Removing a field is a major version bump and a migration that drops the field on load. Renaming a field is two migrations: first add the new field copying the old's value, ship a version, then drop the old field in a later version. The discipline is the discipline.
- Schema validation on load. The save file on disk is *untrusted input*. Pydantic on the Python tools side does it for free; on the GDScript side, you write a `_validate(d: Dictionary) -> bool` function and call it before any other code touches `d`. A validator that rejects 100% of malformed saves is more valuable than the most clever loader.

Lecture 3 — Atomicity, integrity, cloud, recovery:

- The temp-file-plus-rename pattern. Write to `save.tmp` in the same directory as `save.json`. `fsync` the file descriptor. Close. `rename("save.tmp", "save.json")`. The rename is the only step that *publishes* the new save; if the program crashes between the open and the rename, `save.json` is still the previous good state. On POSIX `rename` is atomic; on Windows you use `os.replace` (Python) or `MoveFileEx` (Win32) for the same guarantee.
- Why never write directly to the production path. Because a crash between `open(path, "w")` and the first `write` truncates the file to zero bytes. A crash mid-write leaves a half-written file. Both states are unloadable; both are the dominant cause of "the game corrupted my save."
- Integrity checking. Append a CRC32 or SHA-256 of the payload to the file, separately from the payload. On load, recompute the hash from the payload bytes and compare. A mismatch means corruption — disk error, half-written bytes, manual tampering — and the loader rejects the file. We use SHA-256 because it is in the standard library on both sides and the cost is invisible at save sizes under a megabyte.
- Backup rotation. Promote `save.latest` → `save.previous` before every successful write. On a failed load of `save.latest`, fall back to `save.previous`. Three files on disk (`save.latest`, `save.previous`, plus the in-flight `save.tmp`) and two extra renames is the entire cost.
- Cloud, at the conceptual level. Steam Cloud syncs a configurable set of paths in the user's `userdata/<appid>/remote/` directory between machines and the cloud. Google Play Saves stores a per-user snapshot that the client app uploads and downloads explicitly. iCloud Key-Value Storage syncs a small bag of key-value pairs across the user's Apple devices (1 MB total quota). iCloud Documents syncs files. Each service has its own conflict-resolution model — Steam Cloud uses last-write-wins by default and exposes a callback if you opt in to conflict detection; Google Play Saves exposes a snapshot conflict and forces the app to pick; iCloud Key-Value Storage broadcasts change notifications. None of the three is "free magic"; all three need explicit handling in the game.

## Weekly schedule

The schedule below adds up to approximately **33 hours**. Treat it as a target. Save systems are the rare topic where the *design* takes longer than the *code*; expect Monday and Tuesday to feel slower than the rest of the week.

| Day       | Focus                                              | Lectures | Exercises | Challenges | Quiz/Read | Homework | Mini-Project | Self-Study | Daily Total |
|-----------|----------------------------------------------------|---------:|----------:|-----------:|----------:|---------:|-------------:|-----------:|------------:|
| Monday    | Lecture 1 + the two-bucket model                   |    2h    |    1.5h   |     0h     |    0.5h   |   1h     |     0h       |    0.5h    |     5.5h    |
| Tuesday   | Lecture 2 + JSON / MessagePack / Pydantic          |    2h    |    1.5h   |     0h     |    0.5h   |   1h     |     0.5h     |    0h      |     5.5h    |
| Wednesday | Schema v1, schema v2, the migration table          |    0h    |    2h     |     0.5h   |    0.5h   |   1h     |     1h       |    0.5h    |     5.5h    |
| Thursday  | Lecture 3 + atomic writes + backup rotation        |    2h    |    1h     |     0.5h   |    0.5h   |   0.5h   |     1.5h     |    0h      |     6h      |
| Friday    | Steam Cloud / Play Saves / iCloud survey + read    |    0h    |    1h     |     1h     |    0.5h   |   0.5h   |     2h       |    0.5h    |     5.5h    |
| Saturday  | Mini-project — bolt the system onto a prior game   |    0h    |    0h     |     0h     |    0h     |   0h     |     4.5h     |    0.5h    |     5h      |
| Sunday    | Mini-project recording + quiz + write-up           |    0h    |    0h     |     0h     |    1h     |   0.5h   |     1.5h     |    0h      |     3h      |
| **Total** |                                                    | **6h**   | **7h**    | **2h**     | **3.5h**  | **4.5h** | **11h**      | **2h**     | **36h**     |

An overshoot on Wednesday is normal — the migration table is the conceptual centre of the week and rewards a slow afternoon. An undershoot on Friday is normal — the cloud survey is reading, not coding.

## Files in this folder

| File / Folder                                              | What it is                                                                               |
|------------------------------------------------------------|------------------------------------------------------------------------------------------|
| `README.md`                                                | This file. The week's contract.                                                          |
| `resources.md`                                             | Annotated reading list. Godot saving-games docs, MessagePack spec, Pydantic v2, Steam Cloud. |
| `lecture-notes/01-when-and-what-to-save.md`                | Manual vs autosave vs checkpoint, what to persist, the two-bucket model.                 |
| `lecture-notes/02-formats-schemas-and-migration.md`        | JSON, MessagePack, Protobuf, Godot resources; pickle and BinaryFormatter as anti-patterns; versioning. |
| `lecture-notes/03-atomicity-integrity-cloud-recovery.md`   | Temp-file-plus-rename, checksums, backup rotation, the cloud-save survey.                |
| `exercises/exercise-01-json-roundtrip.py`                  | Define a small game state, serialise to JSON, deserialise, assert equality.              |
| `exercises/exercise-02-pydantic-schema.py`                 | Re-do exercise 1 with Pydantic v2 validation. Reject a hand-corrupted save.              |
| `exercises/exercise-03-msgpack-vs-json.py`                 | Same data, both formats; print sizes and parse times; recommend a winner.                |
| `exercises/exercise-04-version-migrate.py`                 | A v1 save with two fields, a v2 save with three, a `migrate_v1_to_v2` function.          |
| `exercises/exercise-05-atomic-write.py`                    | Temp-file-plus-rename. SHA-256 integrity. Backup rotation. A simulated-crash test.       |
| `exercises/exercise-06-save-manager.gd`                    | The Godot `SaveManager` autoload. JSON, slots, atomic write, migration.                  |
| `exercises/SOLUTIONS.md`                                   | Walk-through of every exercise.                                                          |
| `challenges/challenge-01-hmac-signed-saves.md`             | Stretch: add an HMAC-SHA-256 signature with a per-install key.                           |
| `challenges/challenge-02-msgpack-in-godot.md`              | Stretch: build a tiny pure-GDScript MessagePack writer/reader and round-trip a save.     |
| `quiz.md`                                                  | 20 multiple-choice and short-answer questions.                                           |
| `homework.md`                                              | The week's structured homework. Three problems plus a write-up.                          |
| `mini-project/README.md`                                   | The spec: take a prior week's game, bolt on the complete save system.                    |
| `mini-project/save_manager.gd`                             | The full save manager, slots, atomic write, v1/v2 migration.                             |
| `mini-project/save_schema.py`                              | The Pydantic schemas for v1 and v2 plus the migration function.                          |
| `mini-project/test_migration.py`                           | A `pytest` suite that round-trips, mutates, validates, and migrates.                     |

## How to run any Python file in this folder

```bash
python3 -m venv venv
source venv/bin/activate
pip install pydantic msgpack pytest
cd exercises
python3 exercise-01-json-roundtrip.py
```

Every `.py` file in this folder is independently executable. None imports another exercise. Each prints a small report of what it did and a final `OK` line on success.

## How to run any GDScript file in this folder

1. Open Godot 4.2+ (or newer).
2. Create a new 2D scene with a `Node` root.
3. In *Project Settings* → *Autoload*, add `exercises/exercise-06-save-manager.gd` as `SaveManager`.
4. Attach a script to the root node that calls `SaveManager.save_to_slot(0)` and `SaveManager.load_from_slot(0)`.
5. Run the scene. Watch the *Output* tab.

The mini-project includes a full sample scene.

## Grading

| Component             | Weight |
|-----------------------|-------:|
| Quiz (20 questions)   |   15%  |
| Homework (3 problems) |   25%  |
| Exercises (6 files)   |   20%  |
| Challenges (2 files)  |   15%  |
| Mini-project          |   25%  |
| **Total**             | **100%** |

A pass is 70%. The mini-project is the single largest weight; a recording (or, equivalently, a written log) showing a v1 save being loaded and migrated to v2 in a real running game is the deliverable that counts.

## Common pitfalls

A short list of pitfalls that catch first-time save-system students. None is fatal; all are easy to fix once recognised.

- **The save file is empty.** You opened it with `open(path, "w")` and the program crashed before any `write` call. Switch to the temp-file-plus-rename pattern; the production path is never opened for writing.
- **The save file is half-written.** Same root cause. Same fix. The temp file may be half-written; the production file is not.
- **The migration runs every time, even on already-up-to-date saves.** Your loader does not check the `version` field. Check it. If `data["version"] == CURRENT_VERSION`, skip migration.
- **The migration runs in the wrong order.** You wrote `migrate_v1_to_v3` and forgot that a v1 save in the field needs to first become a v2 save. Always chain single-step migrations: v1 → v2 → v3 — never write a `v1 → v3` shortcut, even when it would be one line.
- **Pydantic rejects a save that *should* be valid.** A field type is wrong in the schema or a default is missing. Run the schema's `model_json_schema()` and compare against the actual save's keys.
- **`JSON.parse_string` in GDScript silently returns `null`.** The input was not valid JSON. Add a check: `if parsed == null: push_error("...")`. Godot does not raise; you must check.
- **The SHA-256 check rejects a save that was just written.** You serialised with `sort_keys=False` and the second serialisation produced different bytes. Always pass `sort_keys=True` (Python `json`) or sort manually (GDScript) before hashing.
- **The Steam Cloud sync overwrote the more-recent save.** Steam Cloud's default is last-writer-wins by *file mtime as reported by the OS that wrote it*. A clock skew between two machines is enough to lose data. Steam exposes a per-file conflict callback when you opt in via the Steamworks API; for any non-trivial game, opt in.
- **The atomic rename works on macOS and Linux but not on Windows.** Plain `os.rename` raises if the target exists on older Python versions on Windows. Use `os.replace`, which is the cross-platform replacement-rename in Python 3.3+.

When in doubt, the debug trick from Lecture 3 applies: print the path the loader is reading, print the version it read, print the keys it parsed. The bug is almost always one of those three.

## A note on the next week

Week 12 picks up *input remapping and accessibility*. You will give the player a settings panel that lets them rebind every key and gamepad button, persist the binding through Week 11's save system (the settings bucket, not the run bucket), and ship the result with the three platform-required accessibility toggles (large-text, colour-blind mode, screen-shake reduction). The save system you built this week is the substrate on which the accessibility work sits; without it, the settings panel resets to default on every launch.

The skills compound across weeks. Week 9 gave you the network. Week 10 gave you the polish. Week 11 gives you the persistence. Week 12 will give you the accessibility settings that ride on top of the persistence. By the end of the course the toolbox is big enough that a "small persistence pass" on a prototype takes a single afternoon, and the difference between a project a player will give thirty hours of their life to and a project they will quit after fifteen minutes is whether the persistence layer survives a crash.

Save your `save_manager.gd`. Reuse it. Build a personal library. By the time you have shipped a few projects with the systems built this week, you will have a small folder of tested loaders, migration helpers, and atomic-write utilities that handle 95% of persistence cases you reach for. That folder is more valuable than any single project's save system. It is the working substrate of a professional.
