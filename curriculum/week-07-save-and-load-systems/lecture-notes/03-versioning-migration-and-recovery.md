# Lecture 3 — Versioning, Migration, and Recovery

> **Duration:** ~2 hours of reading + hands-on.
> **Outcome:** You can ship a save format on day one that survives schema changes, crashes during write, and disk corruption — and you can explain *why* each of the three problems requires a different mechanism.

If you only remember one thing from this lecture, remember this:

> **A save file is a contract that survives the *release boundary*. Once a player has v1 saves on disk and you ship v2, the v2 code must load v1 saves without losing any field. The mechanism is a `schema_version` integer and a chain of one-step migration functions. The discipline is more important than the mechanism: never break v1 saves once they exist in the wild.**

The lecture is in three parts. Part one — *versioning* — is the schema discipline that lets your save format evolve. Part two — *atomic writes* — is the file-system discipline that lets your save survive a crash mid-write. Part three — *corruption recovery* — is the integrity discipline that catches disk-level damage and falls back to a known-good backup.

---

## 1. The first byte of every save is `schema_version`

Lecture 1 §4 defined `GameState` with `schema_version: int = 1` as its first field. This is not decoration. It is the most important byte of the file.

When you ship v1 of your game, saves are v1. The schema is exactly the `GameState` fields from Lecture 1.

When you ship v2 of your game — three months later, you add a `coins` field, then six months later you split `inventory` into `inventory` and `equipment` — the saves on player disks are still v1. The *code* changes; the *files* do not (until the player saves again).

Two outcomes are possible:

- **The right outcome.** v2 code reads a v1 save, walks it through `migrate_v1_to_v2`, and presents the player with a v2-shaped state. `coins` defaults to 0; `equipment` defaults to empty. The player's progress is intact. They are pleased.
- **The wrong outcome.** v2 code reads the v1 save, hits a missing field, throws `KeyError`, and the player sees "Save corrupted, please start a new game." The player rage-quits. They tell their friends.

The difference is the `schema_version` byte and the migration ladder.

---

## 2. The migration ladder

The pattern is a chain of one-step migrations. Each function knows how to step *one* version forward. The framework composes them.

```python
from typing import Callable

CURRENT_SCHEMA_VERSION: int = 3


def migrate_v1_to_v2(d: dict) -> dict:
    """v2 added 'coins'. Default existing v1 saves to 0."""
    d["coins"] = 0
    d["schema_version"] = 2
    return d


def migrate_v2_to_v3(d: dict) -> dict:
    """v3 split 'inventory' into 'inventory' and 'equipment'.

    Items with id starting 'eq_' move to 'equipment'.
    """
    inventory = d.get("inventory", [])
    d["equipment"] = [it for it in inventory if it["id"].startswith("eq_")]
    d["inventory"] = [it for it in inventory if not it["id"].startswith("eq_")]
    d["schema_version"] = 3
    return d


MIGRATIONS: dict[int, Callable[[dict], dict]] = {
    1: migrate_v1_to_v2,
    2: migrate_v2_to_v3,
}


def migrate_to_current(d: dict) -> dict:
    """Walk a loaded dict through every migration up to CURRENT_SCHEMA_VERSION."""
    version = d.get("schema_version", 1)
    while version < CURRENT_SCHEMA_VERSION:
        if version not in MIGRATIONS:
            raise ValueError(f"no migration from v{version}")
        d = MIGRATIONS[version](d)
        version = d["schema_version"]
    return d
```

Three rules govern this design.

**Rule A — One step at a time.** `migrate_v1_to_v2` does *not* know about v3. It moves v1 to v2 and stops. The composer (`migrate_to_current`) chains them. This keeps each function small and auditable. The alternative — a giant `migrate_v1_to_v3` function — duplicates logic and goes out of date the moment v4 ships.

**Rule B — Always set the new `schema_version`.** Every migration writes the new version into the dict it returns. The composer reads it to know whether to stop or continue. Forget this and the composer loops forever.

**Rule C — Migrations are *forward only*.** There is no `migrate_v2_to_v1`. A v2-only field cannot be represented in v1. Downgrade is not supported. If a player runs v2, saves, then re-installs v1, the v1 code will throw on the unknown version stamp — and that is the correct behaviour. The save belongs to v2.

---

## 3. Migrations are additive in practice

The pleasant theory: schemas evolve in arbitrary directions.

The practical reality: **you only ever *add* fields, and you *never remove* fields once a player save has them.**

The reason is data integrity. A v1 save has a `legacy_score: int` field. v2 decides scoring works differently and removes the field. A v1 save loaded by v2 code will have `legacy_score: 47` in the dict; the v2 code ignores it. So far so good. But what if a v3 design wants the field back, possibly with a different meaning? The v1 saves have stale values you cannot trust; new v3 saves have correct values. Now the meaning of `legacy_score` depends on the save version that introduced it. You have a foot-gun.

The discipline is simpler: **once a field is in the schema, it stays in the schema forever.** The *code* may stop reading it. The *new code* may overwrite it with a default. The *dataclass* may keep the field for backward compatibility, deprecated but present. But the schema does not lose fields.

If this feels wasteful, remember: a single field on a save file is *four bytes* in the binary case and *twenty bytes* in the JSON case. A "legacy" field accumulates ten times over a five-year game's lifetime, costing 200 bytes per save. The cost is invisible. The benefit — never breaking a v1 save — is enormous.

(In a *database*, you can use `ALTER TABLE DROP COLUMN`. A save file is not a database. The discipline is different.)

---

## 4. The atomic write — surviving a crash mid-write

The migration story handles *schema evolution*. The atomic-write story handles a different failure mode: **the player's machine crashed while the game was writing the save**.

The naive write:

```python
import json
with open("save.json", "w") as f:
    json.dump(state, f)  # crash during this line
```

If the OS crashes mid-write, `save.json` is now *truncated*. The first half of the JSON is on disk; the second half is gone. The closing `}` is missing. On next launch the game opens the file, `json.load` throws `JSONDecodeError`, and the player's last save is gone. There is no previous save. There is no recovery path.

The atomic write fixes this with two old, simple ideas: **write to a temporary file, then rename**, and **fsync before rename**.

```python
import json
import os


def atomic_write_json(path: str, payload: dict) -> None:
    """Write payload to path. Survives a crash mid-write."""
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
```

Three operations, in order:

1. **`json.dump(...)`** writes JSON text into the OS file buffer. May or may not be on disk yet.
2. **`f.flush()` + `os.fsync(fileno)`** force the OS to push the buffer to physical disk. Returns when the bytes are durable.
3. **`os.replace(tmp, path)`** atomically renames the temp file over the canonical name. On POSIX (Linux, macOS) and Windows since Python 3.3, this is a single file-system operation that either fully succeeds or has no effect.

Why this works: after step 2, the temp file is *durable*. After step 3, either the rename committed (and `save.json` is the new content) or it did not (and `save.json` is the *old* content). At no point can `save.json` be half-written. A crash during step 1 or 2 leaves the canonical save untouched.

The `os.replace` call is the line that turns "we have a save system" into "we have a save system that survives a crash." It is two characters longer than `os.rename` and infinitely more useful.

---

## 5. The backup chain

Atomic writes prevent *truncation*. They do not prevent *bad content* — a logic bug that writes a corrupted state, an old save loaded by new code without a migration, a disk-level bit-flip. For these we maintain a *previous-good* copy.

```python
import os


def safe_save(path: str, payload: dict) -> None:
    """Atomic write with rotation to a .bak file."""
    bak = path + ".bak"
    tmp = path + ".tmp"

    # Write new save to a temp file.
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.flush()
        os.fsync(f.fileno())

    # Move the existing save to .bak (if it exists).
    if os.path.exists(path):
        os.replace(path, bak)

    # Commit the new save into place.
    os.replace(tmp, path)
```

After a successful `safe_save`:

- `save.json` — the new save.
- `save.json.bak` — the previous save.
- `save.json.tmp` — does not exist (committed via replace).

On the *next* save, `save.json` becomes the new `.bak`, and the *current* `.bak` is overwritten. The disk holds the two most recent saves at all times.

On load, the primary path is `save.json`. If `save.json` is unreadable — file missing, JSON parse error, schema-version unknown, checksum mismatch (next section) — the loader falls back to `save.json.bak`. If *that* fails too, the loader reports the failure to the player and offers a new game.

```python
def safe_load(path: str) -> dict:
    """Load with .bak fallback."""
    for candidate in (path, path + ".bak"):
        try:
            with open(candidate, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            continue
    raise FileNotFoundError(f"no usable save at {path} or {path}.bak")
```

Two attempts. Most of the time the first attempt succeeds. The second attempt is the *insurance policy* — usually unused, occasionally a portfolio-saving moment.

---

## 6. Checksums — detecting corruption

The atomic write and the backup chain handle *known* failure modes. The third defence handles the *unknown*: bit-flips on disk, partial writes that completed but produced garbage, deliberate tampering.

The mechanism is a cryptographic hash — SHA-256 — stored next to the payload. On write, hash the payload and store the hex digest in a sidecar file. On load, recompute the hash and compare.

```python
import hashlib
import json


def save_with_checksum(path: str, payload: dict) -> None:
    """Write payload with a SHA-256 sidecar."""
    text = json.dumps(payload, indent=2, sort_keys=True)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    atomic_write_text(path, text)
    atomic_write_text(path + ".sha256", digest)


def load_with_checksum(path: str) -> dict:
    """Load payload and verify its SHA-256."""
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    with open(path + ".sha256", "r", encoding="utf-8") as f:
        expected = f.read().strip()
    actual = hashlib.sha256(text.encode("utf-8")).hexdigest()
    if actual != expected:
        raise ValueError(f"checksum mismatch: {actual} != {expected}")
    return json.loads(text)
```

(The `atomic_write_text` helper is the same atomic-write pattern as §4, generalised to a string instead of a JSON payload.)

What this catches:

- **Disk corruption.** A bit flips on the physical medium; SHA-256 catches it with overwhelming probability.
- **Incomplete writes that escaped atomic semantics.** Rare on modern filesystems but not impossible.
- **Manual editing by a non-careful player.** A player who hand-edits the JSON will break the hash. The game refuses to load and falls back to `.bak`.

What this does *not* catch:

- **Determined tampering.** A player who edits the JSON *and* recomputes the SHA-256 will produce a save that passes the check. SHA-256 is not a *signature*; it is a *checksum*. A signature requires a private key the player does not have, and we are not going to ship a private key in our game.
- **Logic bugs.** If the game writes a *valid but wrong* state, the hash matches. SHA-256 is integrity against accident, not correctness against bugs.

The trust model from the Week 7 README applies: **a local save is player-owned**. Anti-cheat is theatre; integrity is real engineering. The checksum is the integrity check, not the anti-cheat. We do not pretend it is more.

---

## 7. The "trust model" rant

A short editorial. A local single-player save lives on a machine the player controls. The player can:

- Open the save in a text editor and change `player_hp: 5` to `player_hp: 99999`.
- Copy `save.json` before a boss fight and restore it if they die.
- Decompile the game binary and patch out the save check entirely.

Three things follow from this:

1. **Anti-cheat for local saves is theatre.** Any obfuscation a developer adds — XOR with a constant, base64, custom format, even encryption with a key shipped in the binary — is broken within minutes by a determined player. Spending engineering hours on this is wasted.
2. **The threat model is *not* malicious players.** It is *accidental damage* — a half-finished write, a disk error, a corrupted directory. Checksums and atomic writes defeat *accidents*; they are not designed to defeat *intent*.
3. **The exception is online competitive play.** If your game has a leaderboard or matchmaking, you cannot trust the client. The fix is *server-side* — the authoritative state lives on a server, the client save is decorative. This is a Week-12 multiplayer topic; for this week's single-player saves, the trust model is "the player owns their save and that is fine."

The C11 position: **build the save system you would want as a player**. Robust against accidents, transparent enough to debug, and *honest* about the fact that the player can edit the file if they want to. Spend the saved engineering hours on game design.

---

## 8. Autosave — when and where

Autosave is a *cadence* problem more than a code problem. The code is one call to `safe_save`. The decisions are:

**When to fire.** Three good triggers:

- **Level boundary.** The cleanest moment. The player has just left one room and the next room is loading. The game state is stable (no half-completed physics steps, no in-flight tweens). Autosave here is invisible.
- **On death / on game over.** Counterintuitive, but: save *the run* up to the moment of death so the post-death menu can offer "retry last room" or "continue from autosave." Some games do this with two slots (death-save and progress-save).
- **Every N minutes of wall-clock.** A fallback for long single-room sessions. Five minutes is the canonical default; some games use ten. *Never* every frame.

**Where to fire.** A dedicated slot, *not* the player's manual slot. Convention: `autosave.json`. The autosave never overwrites a manual save. The player can `Continue` from the autosave or `Load` from any manual slot; the two are independent.

**Mid-frame discipline.** Autosave is a file I/O call. On a local SSD it is ~1 ms. On a slow HDD it can be 10 ms. *Never* fire it inside a physics step or inside the render loop. Fire it at the *start* of the next frame, after the physics step has completed and before render begins, or — best — when the player transitions between game *states* (level→level, alive→dead, playing→pause).

The mini-project this week implements autosave at the level boundary. That is the cleanest demonstration. Other cadences are stretch.

---

## 9. Save slots — the three-slot pattern

Three named slots is the convention for indie games. Four reasons:

1. **Three is enough.** A new game on one slot, a mid-game on another, a near-end on the third. The vast majority of players use one slot; the multi-slot players have three concurrent playthroughs at most.
2. **Three fits on screen.** A slot UI with three rows fits comfortably on a small window. Six slots forces scrolling.
3. **Plus autosave makes four file groups.** `slot1.json`, `slot2.json`, `slot3.json`, `autosave.json`. Each with its `.bak` and `.sha256`. Twelve files. Manageable.
4. **Three slots is the right size for the slot-overwrite confirmation dialog.** With one slot, you cannot recover from an accidental save-over. With six, the player loses track. Three is the sweet spot.

The slot UI presents each slot with:

- **Slot number** (1, 2, 3).
- **Timestamp** of last save (ISO-8601 or "3 days ago").
- **Level name** ("Throne Room").
- **Play-time** ("4h 17m").
- **Empty / Used** status.

On *save*, the player picks a slot. If it is occupied, a confirmation dialog appears: "Overwrite slot 2? [Y/N]". This is the entire interaction.

On *load*, the player picks a slot. The save loads. The game restores to the level named in the save.

Challenge 2 builds this UI. The mini-project uses it.

---

## 10. Putting it all together — the full write path

The complete save-write path combines all of this lecture's ideas:

```python
import json
import hashlib
import os
from pathlib import Path


def write_save(slot_path: Path, gs_dict: dict) -> None:
    """The full crash-safe, checksummed, backed-up save path."""
    text = json.dumps(gs_dict, indent=2, sort_keys=True)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()

    tmp = slot_path.with_suffix(slot_path.suffix + ".tmp")
    bak = slot_path.with_suffix(slot_path.suffix + ".bak")
    sha = slot_path.with_suffix(slot_path.suffix + ".sha256")

    # 1. Write JSON to a temp file with fsync.
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())

    # 2. Rotate current save to .bak (if it exists).
    if slot_path.exists():
        os.replace(slot_path, bak)

    # 3. Commit the new save (atomic rename).
    os.replace(tmp, slot_path)

    # 4. Write the checksum sidecar atomically.
    sha_tmp = sha.with_suffix(sha.suffix + ".tmp")
    with open(sha_tmp, "w", encoding="utf-8") as f:
        f.write(digest)
        f.flush()
        os.fsync(f.fileno())
    os.replace(sha_tmp, sha)
```

And the matching read path:

```python
def read_save(slot_path: Path) -> dict:
    """Load with checksum verification and .bak fallback."""
    bak = slot_path.with_suffix(slot_path.suffix + ".bak")
    sha = slot_path.with_suffix(slot_path.suffix + ".sha256")

    for candidate in (slot_path, bak):
        if not candidate.exists():
            continue
        try:
            with open(candidate, "r", encoding="utf-8") as f:
                text = f.read()
            # Verify checksum if a sidecar exists for the primary file.
            if candidate == slot_path and sha.exists():
                expected = sha.read_text(encoding="utf-8").strip()
                actual = hashlib.sha256(text.encode("utf-8")).hexdigest()
                if actual != expected:
                    continue  # fall through to .bak
            data = json.loads(text)
            return migrate_to_current(data)
        except (json.JSONDecodeError, OSError):
            continue
    raise FileNotFoundError(f"no usable save at {slot_path}")
```

Forty lines of code. Survives a crash mid-write. Survives schema evolution. Survives a single-file corruption. Refuses to load a tampered save without falling back to the previous good copy. This is what a real save system looks like.

---

## 11. What we built and what comes next

By the end of this lecture you should have:

- The schema-version discipline internalised — every save starts with a version stamp on day one.
- The migration ladder pattern memorised — one function per step, composed automatically.
- The atomic-write idiom (`write to tmp`, `fsync`, `os.replace`) ready to type from memory.
- The backup-chain pattern (`save.bak` rotation) understood.
- The checksum sidecar (`.sha256`) understood and its limitations clear (integrity not security).
- The autosave cadence rule (level boundary, not every frame) clear.
- The three-slot pattern clear.

You do not yet have:

- A running implementation that does all of the above. That is the mini-project.
- A UI for browsing slots. That is Challenge 2.
- A cloud-sync protocol. That is Challenge 1 (paper design only).
- A `gzip` integration for large saves. That is a stretch goal in homework.

The mini-project this week — a tiny RPG with three slots, autosave, versioning, and corruption recovery — assembles every piece. By Sunday you have shipped a save system that would not embarrass a small indie studio.

---

## References

- **Glenn Fiedler — *Reading and Writing Packets* (Gaffer On Games).** The version-stamp-and-integrity-check discipline applied to network packets. The save-file shape is identical. <https://gafferongames.com/post/reading_and_writing_packets/>
- **Python `os.replace` — official docs.** The atomic-rename call. <https://docs.python.org/3/library/os.html#os.replace>
- **Python `os.fsync` — official docs.** Force buffers to physical disk. <https://docs.python.org/3/library/os.html#os.fsync>
- **Python `hashlib` module — official docs.** SHA-256 for integrity. <https://docs.python.org/3/library/hashlib.html>
- **LWN.net — *Ensuring data reaches disk*.** A technical write-up on `fsync` semantics. <https://lwn.net/Articles/457667/>
- **Godot — *Saving games* (official docs).** Godot's canonical save tutorial. The algorithms in this lecture port verbatim. <https://docs.godotengine.org/en/stable/tutorials/io/saving_games.html>
- **Pygame docs.** Pygame's types that must never appear in a save. <https://www.pygame.org/docs/>

---

*The lecture series ends here. Continue to the exercises to write the code, the challenges for the design problems, and the mini-project to assemble it all.*
