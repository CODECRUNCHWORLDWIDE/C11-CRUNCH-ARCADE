# Week 7 — Save and Load Systems

Last week you painted the muscles. The Week-5 player now feels like a *character*, not a rectangle, and the before-and-after video proves it. The juice pass is the most-loved week of the course, and we are going to spend exactly zero of this week's hours adding more polish to it.

This week we solve the *most overlooked subsystem in indie game development*: writing the player's progress to disk in a way that survives a power outage, a version upgrade, and a half-finished save written during a crash. There are three games on every C11 student's portfolio. The first two will lose a player's progress within six months of release. We are going to make sure yours is not one of them.

Saving feels boring on the spec. It looks like one function: `json.dump(state, file)`. It is *not* one function. It is a serialization format, a schema version, a migration ladder, an atomic write strategy, a slot manager, an autosave cadence, a corruption detector, and a recovery path. Get any one of them wrong and a player who put forty hours into your game will hit Continue and watch their save reset to zero. That player will not come back, and they will tell their friends.

We do not start from "I'll figure it out." We start from the *Gaffer On Games* posts on serialization, the JSON RFC 8259, the MessagePack specification, the Pygame docs, and Godot's save-game documentation — five sources, all free, all linked in `resources.md`. By Sunday you ship a tiny RPG with **three save slots, schema versioning, autosave on level-end, an atomic write, and a corruption-recovery path that falls back to the previous good save**. The RPG itself is comically small — a player on a 3-room map who picks up coins. The *save system* is real, and it is the artefact.

There is still no Godot. Pygame remains the substrate; the algorithms in this week's lectures will port verbatim to Godot's `FileAccess` API in Week 9.

## Learning objectives

By the end of this week, you will be able to:

- **Distinguish** the four kinds of state a game holds — persistent (must save), session (lost on quit), derived (rebuildable), and presentation (never saved) — and decide which fields go on disk and which do not.
- **Implement** a save round-trip in JSON: serialize a `GameState` dataclass to a file, read it back, and confirm field-by-field equality. The function-pair is twenty lines and is the spine of the week.
- **Compare** three serialization formats — JSON, MessagePack, custom binary (`struct.pack`) — on three axes: file size, write/read time, and human-readability. The benchmark is in Exercise 3.
- **Version** a save format by writing a `schema_version` integer at the top of every save and writing a chain of migration functions `v1_to_v2`, `v2_to_v3`, ... that step a stale save up to the current version.
- **Detect** save corruption two ways: checksum mismatch (SHA-256 of the payload, stored next to it) and shape mismatch (the JSON parses but lacks a required field).
- **Recover** from corruption by maintaining a `save.bak` previous-good copy and a `save.tmp` write-in-progress sentinel. The atomic-write pattern: write to `.tmp`, fsync, rename to canonical. Survives a crash mid-write.
- **Implement** autosave: a checkpoint fires when the player crosses a level boundary or every N seconds. The autosave writes to a dedicated slot (`autosave.json`), never overwrites a manual save.
- **Design** a three-slot save UI: three named slots, each with a timestamp, a level name, and a play-time counter. The slot selector is a small FSM (your Week-5 muscle memory still works).
- **Reason** about the *trust model* of a save file — a local save is player-owned, so anti-cheat protection is theatre, but checksum-based corruption detection is real engineering. The two are not the same.
- **Frame-budget** the save system: a JSON save of a small RPG state is ~2 KB and takes ~1 ms to write. Autosave is *free* if you do it on a level boundary, not every frame.

## Prerequisites

This week assumes you have completed **Weeks 1–6**. Specifically:

- You have a Week-6 mini-project repo with a juiced FSM-driven player on a tilemap. You can run it.
- You are comfortable with Python dataclasses (`@dataclass`) and `dict`/`list` literals.
- You have read or written JSON in any context. If you have not, skim [RFC 8259](https://www.rfc-editor.org/rfc/rfc8259) — it is twelve pages and you only need the syntax diagram on page 6.
- You know what a hash function is, at the level of "SHA-256 turns a blob of bytes into a 32-byte fingerprint and the same blob always produces the same fingerprint."
- You can install one third-party package with `pip install msgpack` inside a virtual environment.

If any of those are shaky, do the previous week's mini-project before continuing.

## Topics covered

Lecture 1 — What state actually needs saving:

- The four state categories: persistent, session, derived, presentation. Examples and the "do I save this?" decision tree.
- The `GameState` dataclass — the *contract* between the running game and the disk. One file, one class, one schema version.
- Why the `Player` object in memory is not the `Player` record on disk. The disk record is a flattened, derived-free, version-stamped subset.
- The `to_dict()` / `from_dict()` pair as the boundary. Inside: live `pygame.Surface` references, FSM instances, sound channels. Outside: ints, floats, strings, lists, dicts.
- Why you do *not* pickle. Pickle is fast, executes arbitrary code on load, and is unportable. JSON is slower, safe, and readable. The trade-off is firmly on the JSON side for game saves.
- Inventory as a list-of-dicts, not a list-of-objects. The disk format is data, not code.
- The "everything is a tree of primitives" rule: if your `to_dict()` returns anything that isn't an `int`, `float`, `str`, `bool`, `None`, `list`, or `dict`, the serializer will choke and you have a bug.

Lecture 2 — Serialization formats and trade-offs:

- **JSON** (RFC 8259): the default. Text, human-readable, diffable, no binary types, ~2x larger than native. Library: stdlib `json`.
- **MessagePack** (msgpack spec): a binary JSON-compatible format. ~30-50% smaller than JSON, faster to parse, still cross-language. Library: `msgpack`.
- **Custom binary** (`struct.pack`): fastest, smallest, fragile. Useful for replay files and network packets, *not* for game saves. We cover the shape so you can recognise it.
- **Pickle**: do not use for saves. Briefly covered for "why not."
- **The size/speed/readability triangle**: pick two. JSON gives you readability and cross-language at the cost of size. MessagePack gives you size and speed at the cost of human-readability. Custom binary gives you size and speed at the cost of *everything else*.
- Benchmark protocol: serialize the same `GameState` 10,000 times in each format, report bytes-on-disk and median microseconds-per-op. Exercise 3 ships the benchmark; you tune the workload.
- Compression as the orthogonal axis: `gzip` over JSON is the *real* answer for big saves. Compresses a 200 KB JSON save to 30 KB. Stdlib only.
- The Pygame angle: nothing in `pygame.Surface` or `pygame.mixer.Sound` should ever be in a save. Those are *derived* from a level ID and a sprite path. Save the IDs.

Lecture 3 — Versioning, migration, and corruption recovery:

- The first byte of every save is a schema-version stamp. Day-one. Even if your save has one field, version it.
- The migration ladder: a chain of `migrate_v1_to_v2`, `migrate_v2_to_v3` functions that each *only* know how to step one version. The framework composes them. Saves from v1 walk through `v1→v2`, `v2→v3`, ... to current.
- Why migrations are *additive only* in practice: renaming `hp` to `health` is a migration; *removing* `hp` once a player save has it is data loss. Plan for fields to live forever; let the *code* stop reading them.
- The atomic write: write to `save.tmp`, `os.fsync`, `os.replace` (which is atomic on POSIX and Windows since Python 3.3) to the canonical name. Survives a crash mid-write.
- The backup chain: before overwriting `save.json`, rename it to `save.json.bak`. After a successful write, the `.bak` is the last-known-good. On load failure, fall back to `.bak`.
- Corruption detection: SHA-256 the payload, store the digest in a sidecar `save.json.sha256`. On load, recompute and compare. Mismatch ⇒ refuse to load, fall back to `.bak`.
- The "trust model" rant: a *local* save is player-owned. A determined player will edit it. Anti-cheat for single-player saves is theatre and consumes development time better spent on game design. Checksums are not anti-cheat — they are *integrity* checks against disk corruption, not against malice.
- Autosave cadence: on level boundary (no risk of mid-physics-frame state), on death, on every N minutes of wall-clock if you must. *Not* every frame. Autosave goes to its own slot so it cannot trample a manual save.
- The three-slot pattern: `slot1.json`, `slot2.json`, `slot3.json`, `autosave.json`. Plus the `.bak` per slot. Plus the `.sha256` per file. Looks like a lot. Adds up to ~12 files on disk and ~80 lines of code.

## Weekly schedule

The schedule below adds up to approximately **34 hours**. Treat it as a target. Save systems are deceptively quick to write a v1 of and deceptively slow to make robust. The work this week is the second half.

| Day       | Focus                                            | Lectures | Exercises | Challenges | Quiz/Read | Homework | Mini-Project | Self-Study | Daily Total |
|-----------|--------------------------------------------------|---------:|----------:|-----------:|----------:|---------:|-------------:|-----------:|------------:|
| Monday    | Lecture 1 + state taxonomy + `to_dict`/`from_dict`|    2h    |    1.5h   |     0h     |    0.5h   |   1h     |     0h       |    0.5h    |     5.5h    |
| Tuesday   | Lecture 2 + JSON round-trip exercise             |    2h    |    1.5h   |     0h     |    0.5h   |   1h     |     0.5h     |    0h      |     5.5h    |
| Wednesday | Lecture 3 + versioning + migration               |    2h    |    1.5h   |     0.5h   |    0.5h   |   1h     |     1h       |    0h      |     6.5h    |
| Thursday  | MessagePack benchmark + atomic write             |    0h    |    1.5h   |     1h     |    0.5h   |   1h     |     1.5h     |    0h      |     5.5h    |
| Friday    | Wire save/load into a tiny RPG                   |    0h    |    0h     |     0.5h   |    0.5h   |   1h     |     2.5h     |    0.5h    |     5h      |
| Saturday  | Slots, autosave, corruption recovery, quiz       |    0h    |    0h     |     0h     |    0.5h   |   0.5h   |     2.5h     |    0h      |     3.5h    |
| Sunday    | Polish, README, push                             |    0h    |    0h     |     0h     |    0.5h   |   0h     |     2h       |    0h      |     2.5h    |
| **Total** |                                                  | **6h**   | **6h**    | **2h**     | **3.5h**  | **5.5h** | **10h**      | **1h**     | **34h**     |

## How to navigate this week

| File | What's inside |
|------|---------------|
| [README.md](./00-overview.md) | This overview (you are here) |
| [resources.md](./01-resources.md) | Gaffer On Games posts, RFC 8259, MessagePack spec, Pygame docs, Godot save-game docs |
| [lecture-notes/01-what-state-actually-needs-saving.md](./02-lecture-notes/01-what-state-actually-needs-saving.md) | The four state categories; `GameState` as the contract; `to_dict`/`from_dict` discipline; why not pickle |
| [lecture-notes/02-serialization-formats-trade-offs.md](./02-lecture-notes/02-serialization-formats-trade-offs.md) | JSON vs MessagePack vs custom binary; the size/speed/readability triangle; compression; the Pygame-specific rules |
| [lecture-notes/03-versioning-migration-and-recovery.md](./02-lecture-notes/03-versioning-migration-and-recovery.md) | Schema versions; migration ladders; atomic writes; backup chains; checksums; the trust model |
| [exercises/exercise-01-json-save-load.py](./03-exercises/exercise-01-json-save-load.py) | A Pygame game with player x/y/inventory that round-trips through JSON. Save with S, load with L |
| [exercises/exercise-02-versioned-saves-with-migration.py](./03-exercises/exercise-02-versioned-saves-with-migration.py) | Three versions of a save schema and a migration ladder that walks v1 saves to v3 |
| [exercises/exercise-03-msgpack-vs-json-benchmark.py](./03-exercises/exercise-03-msgpack-vs-json-benchmark.py) | Serialize the same `GameState` 10,000 times in JSON and MessagePack; report bytes and microseconds |
| [exercises/SOLUTIONS.md](./03-exercises/SOLUTIONS.md) | Solution discussion and the "common bugs" list for each exercise |
| [challenges/challenge-01-cloud-save-with-conflict-resolution.md](./04-challenges/challenge-01-cloud-save-with-conflict-resolution.md) | Design (paper, not code) a cloud-sync protocol with last-write-wins, vector-clock, and three-way merge variants |
| [challenges/challenge-02-implement-save-slot-ui.md](./04-challenges/challenge-02-implement-save-slot-ui.md) | A Pygame three-slot save selector with timestamps, play-time, and a confirm-overwrite dialog |
| [quiz.md](./05-quiz.md) | 10 multiple-choice questions |
| [homework.md](./06-homework.md) | Six practice problems for the week |
| [mini-project/README.md](./07-mini-project/00-overview.md) | A tiny RPG with three save slots, schema versioning, autosave, and corruption recovery |

## Frame budget for this week

A reminder of what 60 fps actually means, in milliseconds. The save system does not run every frame — but when it does run, it must not stall the loop.

```
┌─────────────────────────────────────────────────────────┐
│  FRAME BUDGET — 60 fps target, with save system idle    │
│                                                         │
│  Input poll:       ~0.2 ms                              │
│  FSM dispatch:     ~0.1 ms                              │
│  Update (sim):     ~1.4 ms                              │
│  Animation tick:   ~0.3 ms                              │
│  Particles:        ~0.6 ms                              │
│  Render (entity):  ~1.5 ms                              │
│  HUD draw:         ~0.4 ms                              │
│  Audio mix:        ~0.4 ms                              │
│  Save system:      ~0.0 ms  (sleeping, no I/O)          │
│  GPU + present:    ~4.0 ms                              │
│  Headroom:         ~7.7 ms                              │
│  ─────────────────────                                  │
│  Total:           ~16.6 ms / frame                      │
└─────────────────────────────────────────────────────────┘
```

When a save *does* fire — on a level boundary, on death, on Ctrl-S — it costs roughly **1.0 ms** for a small RPG (2 KB JSON write to local SSD). That is one frame of stutter on a 60 fps target. The mini-project ships with a status-line "saving..." flash so the player sees the cost. The professional move is to write the save on a background thread; we will not implement that this week (Week 12 — concurrency), but we mention it so you know the technique exists.

If your save ever shows up as a multi-millisecond bump on a profiler, it is because you serialized something you shouldn't have — usually a `pygame.Surface` or a large derived list. Fix the `to_dict` boundary, not the serializer.

## Stretch goals

If you finish early and want to push further:

- **Read Glenn Fiedler's *Gaffer On Games* post "Reading and Writing Packets" in full.** It is the network-packet version of this week's lecture and the algorithms are identical. The serialization framework Fiedler describes is the canonical reference; you will meet it again if you ever write multiplayer code.
- **Implement `gzip` compression** over JSON saves. Stdlib `gzip.open(path, "wt")` is a one-line drop-in for `open(path, "w")`. Measure the compressed size against the raw JSON on a 50 KB save. Expect ~10x compression for a typical inventory + map state.
- **Add a `screenshot` field to your saves.** Capture a 320×180 `pygame.Surface`, encode it as a base64 PNG, and embed it in the save JSON. The save-slot UI uses it as a thumbnail. The save grows by ~8 KB; the UX gain is large.
- **Implement a "soft autosave" toggle in the settings menu.** Some players prefer no autosave (they want to control when checkpoints land). Respect the toggle; default it on.
- **Read Godot's official *Saving games* page (linked in `resources.md`)** and identify the *three* differences from our Pygame approach. (Hint: `FileAccess.open`, the engine's `ConfigFile` for simple key/value, and the `ResourceSaver` for tres/tscn — all three are Pygame's `open()` and `json.dump()` wearing different clothes.)
- **Watch Jonathan Blow's *Why I Wrote My Own Save System* talk (2018, free on YouTube).** Forty-five minutes; Blow explains why *The Witness*'s save system reads and writes 200 MB of memory snapshots in 16 ms. You will not copy his approach — it is overkill for a Pygame project — but the design reasoning is excellent.
- **Implement a save-slot delete confirmation dialog.** Three keypresses, twelve lines. The point is to wire a transient confirmation FSM into your slot UI.

## Voice rules for the week

- We define **save corruption** as "the file on disk does not faithfully represent the player's progress." It is *not* the same as save *cheating*. The two are different problems; this week we solve corruption.
- We credit **Glenn Fiedler** (Gaffer On Games) whose serialization essays are the canonical free reference on packet/save layout. The C11 syllabus borrows his "every byte is versioned" discipline directly.
- We credit **RFC 8259** (Bray, ed., December 2017) for JSON. JSON is not a vibe; it is a twelve-page IETF document, and reading it once will save you a debugging hour later.
- We credit the **MessagePack spec** (msgpack-spec on GitHub) for the binary-JSON wire format. It is six pages and worth one careful read.
- We prefer **atomic writes via `os.replace`** to "just `open()` and hope." `os.replace` is the line of code that turns "we have a save system" into "we have a save system that survives a crash."
- We do *not* pickle game saves. Pickle is for in-process IPC and `multiprocessing` queues. Game saves are JSON or MessagePack. This is non-negotiable.
- We *never* embed a `pygame.Surface` or a `pygame.mixer.Sound` in a save. Those are derived from level data; the save stores the level ID and the engine rebuilds them.
- We **respect the player's data**. A player who put forty hours into your game is owed a save system that survives a kernel panic, a quit-during-write, and a version upgrade. Mid-tier indie games routinely fail at this; you will not.

## Up next

Continue to [Week 8 — Audio: Music, SFX, and Mixing](../week-08/) once you've pushed your three-slot save system. The atomic-write pattern you write this week is the boilerplate every shippable game copies in.

---

*If you find errors in this material, please open an issue or send a PR. Future learners will thank you.*
