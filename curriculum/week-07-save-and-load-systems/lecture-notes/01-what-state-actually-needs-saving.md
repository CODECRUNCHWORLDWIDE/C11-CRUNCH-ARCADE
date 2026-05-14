# Lecture 1 — What State Actually Needs Saving

> **Duration:** ~2 hours of reading + hands-on.
> **Outcome:** You can look at the running `Player`, `World`, and `App` objects in your Week-6 game and sort every field into one of four buckets — *persistent*, *session*, *derived*, *presentation* — and you can name, without hesitation, which buckets go to disk and which never do.

If you only remember one thing from this lecture, remember this:

> **The `Player` object in memory is not the `Player` record on disk. The disk record is a flattened, derived-free, version-stamped subset of the in-memory state. The `to_dict()` / `from_dict()` boundary is the *contract* between the running game and the file system, and that contract is the entire save system.**

The lecture begins with the failure mode every new game programmer falls into — `json.dump(player.__dict__, f)` — and walks through exactly why it explodes the moment you load it back. Then we build the four-category taxonomy, then we write the `GameState` dataclass, then we write the `to_dict()` / `from_dict()` pair, and by the end you can audit any object in any of your weeks-1-through-6 projects and decide which fields belong on disk.

---

## 1. The naive save and why it explodes

Open a Python REPL. Type the following:

```python
import json

class Player:
    def __init__(self):
        self.x = 100.0
        self.y = 200.0
        self.hp = 5

p = Player()
json.dump(p.__dict__, open("save.json", "w"))
```

It works. The file contains `{"x": 100.0, "y": 200.0, "hp": 5}`. You feel clever. You go home.

The next day you add a `pygame.Surface` field for the player's sprite:

```python
class Player:
    def __init__(self):
        self.x = 100.0
        self.y = 200.0
        self.hp = 5
        self.sprite = pygame.image.load("player.png")
```

You run `json.dump(p.__dict__, open("save.json", "w"))` and it throws `TypeError: Object of type Surface is not JSON serializable`. You add a custom encoder that skips `pygame.Surface`. It works. You go home.

The next day you add an `Animator` from Week 6 with a `dict[str, Animation]` of clips. JSON doesn't know how to serialize `Animation`. You add another encoder. It works. The save file is now 40 KB and contains a serialized representation of every loaded animation frame as a base64-encoded PNG.

The week after, you add a `StateMachine` field with a reference to the current `IdleState` instance. The `IdleState` instance has a reference back to the `Player`. JSON throws `ValueError: Circular reference detected`. You add a third encoder. The save file is now 200 KB. Loading it takes four seconds because every Surface decodes from base64. The player's `x` and `y` are buried in the file.

This is the failure mode. You "saved everything." You actually saved 99% useless data and 1% irreplaceable data and you blurred the line between them. Six months later, the irreplaceable 1% — the actual player progress — gets corrupted by a derived field that doesn't match its expected shape, and the save is unloadable. The player loses their progress.

The fix is structural, not tactical. We do not need a smarter encoder. We need a *boundary*.

---

## 2. The four categories of game state

Every field on every object in your game falls into one of four categories. The exercise of categorising them is the first hour of the save-system design.

### 2.1 Persistent state — *must save*

State that **the player has earned** and would be furious to lose. This is what the save file is *for*.

Examples:

- `player.x`, `player.y` — where the player is in the level.
- `player.hp_max` — the player's upgraded health bar (if persistent through upgrades).
- `player.inventory` — the list of items the player has picked up.
- `player.coins` — currency. Bitterly contested by the player.
- `world.current_level` — which level the player is on.
- `world.flags` — "have we met the king yet?" "is the bridge built?" the discrete-state booleans that gate progression.
- `quest_log` — quest state. (A quest log is just a flag dict with prettier names.)
- `playtime_seconds` — wall-clock seconds played. Cheap to track; deeply meaningful to the player.
- `settings.volume`, `settings.keybinds` — *technically* a separate file (`settings.json`, not `save.json`) but in the same category: must persist.

Every field in this bucket goes to disk. Every save round-trip must reproduce it exactly.

### 2.2 Session state — *lost on quit; do not save*

State that is **valid only within the current play session** and would be wrong to restore. Counterintuitively, *not* saving these is a design decision, not a bug.

Examples:

- `player.vx`, `player.vy` — current velocity. A player who saved mid-air will land oddly on load if you restore velocity.
- `player.state_machine.current_state` — the FSM's current state. Saving a `JumpState` is meaningless; on load you want the player in `IdleState`.
- `world.particles` — live particle list from Week 6. Particles are visual flourish; restoring 47 mid-air dust motes is absurd.
- `world.screen_shake_remaining` — same reasoning.
- `player.coyote_time_t`, `player.jump_buffer_t` — Week-6 buffers. Frame-scale state. Never saved.
- Any *transient* timer measured in seconds.

The rule: if the field exists *because of the input the player gave in the last 200 ms*, do not save it.

### 2.3 Derived state — *rebuildable; do not save*

State that **can be reconstructed** from persistent state. Saving derived state is worse than useless — it is *actively dangerous*, because the derived state on disk can drift from its source and become a lie.

Examples:

- `player.hp_fraction` — `hp / hp_max`. Compute on load; do not store.
- `world.tilemap.collision_grid` — derived from `world.current_level`. Rebuild on load by re-loading the tilemap file.
- `player.sprite_sheet` — derived from `player.character_id` plus a sprite-pack path. Rebuild on load.
- `world.lighting_cache` — derived from `world.tiles` plus `world.lights`. Rebuild.
- `inventory.total_weight` — derived from `inventory.items`. Rebuild.
- `quest_log.completed_count` — derived from `quest_log.entries`. Rebuild.

The rule: if the field can be computed from other persistent state, *do not save it*. Saving it doubles the chance of a corruption-by-drift bug.

### 2.4 Presentation state — *never saved*

State that **lives in the rendering layer**. The `pygame.Surface` references, the `pygame.mixer.Sound` channels, the font objects, the `pygame.display` surface itself. These are *bindings to the running process*. They have no meaning outside the process. They cannot be serialized to JSON; they should not be serialized to anything.

Examples:

- `player.sprite_surface` — `pygame.Surface` reference.
- `player.footsteps_sound` — `pygame.mixer.Sound` reference.
- `world.screen` — `pygame.Surface` returned by `pygame.display.set_mode`.
- `app.font_18` — `pygame.font.Font` reference.
- `app.clock` — `pygame.time.Clock` reference.

The rule: if the field's type starts with `pygame.`, it does not go in a save. Ever. Period.

---

## 3. The decision tree

When you are looking at a field and unsure, walk the tree:

```
┌─────────────────────────────────────────────────────────────┐
│  Does this field's value need to survive QUIT-and-RELOAD ?  │
│                                                             │
│       NO ────► Is it a render/audio binding?                │
│                                                             │
│                YES ────► PRESENTATION ── do not save        │
│                                                             │
│                NO ────► Is it derivable from other state?   │
│                                                             │
│                         YES ────► DERIVED ── do not save    │
│                                                             │
│                         NO  ────► SESSION ── do not save    │
│                                                             │
│       YES ────► PERSISTENT ── save it                       │
└─────────────────────────────────────────────────────────────┘
```

Only the "YES" branch hits disk. Everything else stays in memory.

---

## 4. The `GameState` dataclass — the contract

The discipline that follows from §2 is *concrete*: define a single `GameState` dataclass whose fields are exactly the persistent state, and whose serialization is the save file.

```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

SAVE_SCHEMA_VERSION: int = 1


@dataclass
class GameState:
    """The on-disk shape of a player's progress. Persistent state only."""

    # Identity
    schema_version: int = SAVE_SCHEMA_VERSION
    slot_name: str = "default"
    timestamp_iso: str = ""
    playtime_seconds: float = 0.0

    # Player progress
    player_x: float = 0.0
    player_y: float = 0.0
    player_hp: int = 5
    player_hp_max: int = 5

    # Inventory: list of {"id": str, "count": int}
    inventory: list[dict] = field(default_factory=list)

    # World
    current_level: str = "level_01"
    flags: dict[str, bool] = field(default_factory=dict)
```

Four observations.

**Observation A.** The class is *flat*. There are no nested `Player` or `World` dataclasses. The save layer flattens the in-memory hierarchy because the in-memory hierarchy is allowed to change without breaking the save format. Whether the engine stores the player position in `world.entities.player.pos.x` or `player.x` is an *engine* decision; the save file says `player_x`. They are decoupled.

**Observation B.** Every field has a default. This matters when we add migrations in Lecture 3 — a v1 save loaded by v2 code needs *some* value for the v2 fields, and the dataclass default is the right answer.

**Observation C.** The inventory is `list[dict]`, not `list[Item]`. The disk format is *data*, not *code*. An `Item` class has methods and a constructor; a `dict` has keys. The save file stores the keys.

**Observation D.** `schema_version` is field 1. This is the single most important byte of the save format. Lecture 3 explains why.

---

## 5. The `to_dict()` / `from_dict()` boundary

The `GameState` dataclass goes to and from a plain `dict[str, Any]`. From there, `json.dump` (or `msgpack.pack`) handles the file I/O.

```python
from dataclasses import asdict


def gamestate_to_dict(gs: GameState) -> dict:
    """Serialize a GameState to a plain dict of JSON-safe primitives."""
    return asdict(gs)


def gamestate_from_dict(d: dict) -> GameState:
    """Deserialize a dict back to a GameState. Tolerates missing fields."""
    # Use dataclass defaults for any missing field. This is the entire
    # forward-compatibility story for the v1->v1 case.
    defaults = GameState()
    return GameState(
        schema_version=d.get("schema_version", defaults.schema_version),
        slot_name=d.get("slot_name", defaults.slot_name),
        timestamp_iso=d.get("timestamp_iso", defaults.timestamp_iso),
        playtime_seconds=d.get("playtime_seconds", defaults.playtime_seconds),
        player_x=d.get("player_x", defaults.player_x),
        player_y=d.get("player_y", defaults.player_y),
        player_hp=d.get("player_hp", defaults.player_hp),
        player_hp_max=d.get("player_hp_max", defaults.player_hp_max),
        inventory=list(d.get("inventory", defaults.inventory)),
        current_level=d.get("current_level", defaults.current_level),
        flags=dict(d.get("flags", defaults.flags)),
    )
```

`dataclasses.asdict()` is the stdlib helper that walks a dataclass and produces a nested dict of primitives. It is the one-liner side of the boundary. `from_dict()` is hand-written because we want **explicit defaults on every field** — a v0.9 save that does not have `playtime_seconds` should still load, with `playtime_seconds = 0.0`. The hand-written form makes that contract visible.

The two functions live in `save.py`. Nothing in `main.py` knows how the save file is shaped; it knows only `gamestate_to_dict` and `gamestate_from_dict`.

---

## 6. The capture and apply functions

`GameState` is the *contract*. The bridge from the *live game objects* to the contract is two functions:

```python
def capture_state(player, world, app) -> GameState:
    """Pull persistent fields from live objects into a GameState."""
    return GameState(
        schema_version=SAVE_SCHEMA_VERSION,
        slot_name=app.current_slot,
        timestamp_iso=app.now_iso(),
        playtime_seconds=app.playtime_seconds,
        player_x=player.x,
        player_y=player.y,
        player_hp=player.hp,
        player_hp_max=player.hp_max,
        inventory=[{"id": it.id, "count": it.count} for it in player.inventory],
        current_level=world.current_level_id,
        flags=dict(world.flags),
    )


def apply_state(gs: GameState, player, world, app) -> None:
    """Write a loaded GameState into the live game objects."""
    player.x = gs.player_x
    player.y = gs.player_y
    player.vx = 0.0           # session state — reset on load
    player.vy = 0.0
    player.hp = gs.player_hp
    player.hp_max = gs.player_hp_max
    player.inventory = [Item(id=it["id"], count=it["count"])
                        for it in gs.inventory]
    world.load_level(gs.current_level)  # rebuild derived state
    world.flags = dict(gs.flags)
    app.current_slot = gs.slot_name
    app.playtime_seconds = gs.playtime_seconds
    # The FSM resets to IdleState on load. We do not save the current state.
    player.fsm.reset_to_idle()
```

`capture_state` is the *write* boundary. `apply_state` is the *read* boundary. The save file format never appears in either — only `GameState`.

This separation gives you three things:

1. You can test save/load without touching the file system. `apply_state(gamestate_from_dict(gamestate_to_dict(capture_state(...))), ...)` is a unit test.
2. You can swap JSON for MessagePack in `save.py` without touching `capture_state` or `apply_state`. The choice of format is a one-import change.
3. You can change the in-memory `Player` class freely (rename `hp` to `health`, split position into a `Vec2`) without changing the save file. Only `capture_state` and `apply_state` need updating — and the save file on disk stays the same.

This is the architectural payoff. Three functions: `capture_state`, `apply_state`, and the `to_dict` / `from_dict` pair. Everything else in the save system is plumbing.

---

## 7. Why we do not pickle

The Python standard library ships `pickle`, which can serialize almost any Python object — including a live `Player` instance with its `pygame.Surface` field — in three lines:

```python
import pickle
with open("save.pkl", "wb") as f:
    pickle.dump(player, f)
```

It works. The file is small. Loading is fast. **And it is the wrong answer.** Three reasons:

**Reason A — Code execution on load.** `pickle.load` *executes Python code* to reconstruct the object. A pickle file is, semantically, an executable program. Loading an untrusted pickle file is equivalent to running an untrusted script. For local single-player saves the *attacker* is the player themselves (and on their own machine, they can do worse), but if you ever ship cloud-synced saves between two players, a malicious save can pwn the recipient.

**Reason B — It does not survive code changes.** Pickle stores the *class path* (`engine.entities.Player`) and the *attribute dict*. If you rename `Player` to `Character`, every existing pickle file is broken. If you remove an attribute, every existing pickle file is broken. If you split your engine into two modules and `Player` moves, every existing pickle file is broken. Pickle is *brittle to refactoring*, and games refactor constantly.

**Reason C — It is unportable.** A pickle file written in Python 3.11 may or may not load in Python 3.13. A pickle file written on Linux may or may not load on Windows (because of float-representation quirks in some edge cases). And no other language can read it. If you ever want to read a save file from a tool, an analytics pipeline, or a level editor — and you will — pickle is opaque.

JSON has none of these problems. It is data. It is text. It is human-readable, diffable in Git, parseable in any language, and *cannot execute code on load*. The five-times-slower parse on a 10 KB file is not measurable.

The rule: **`pickle` is for in-process IPC. Game saves are JSON or MessagePack.**

---

## 8. A concrete audit of a Week-6 player

Take the Week-6 mini-project player from your repo. Open `main.py`. Find the `Player` class. Walk its `__init__`. For every attribute, write the category in a comment:

```python
class Player:
    def __init__(self, x: float, y: float) -> None:
        # PERSISTENT
        self.x = x
        self.y = y
        self.hp = 5
        self.hp_max = 5
        self.inventory: list[Item] = []

        # SESSION
        self.vx = 0.0
        self.vy = 0.0
        self.facing_left = False
        self.on_ground = False
        self.coyote_time_t = 0.0
        self.jump_buffer_t = 0.0

        # DERIVED
        # (none in this small example)

        # PRESENTATION
        self.animator = Animator(...)
        self.sprite_sheet = SpriteSheet(...)
        self.footsteps_sound = pygame.mixer.Sound(...)
        self.hit_flash_t = 0.0       # this is *visual feedback*, not progress
```

Five persistent fields. Six session fields. Three presentation fields. The save file stores five values out of fourteen. The other nine are recreated, defaulted, or left at zero on load.

This is normal. The persistent set is usually 20-40% of the in-memory state. The remaining 60-80% is session, derived, or presentation, and not saving it is correct.

---

## 9. The "everything is a tree of primitives" rule

`json.dump` accepts six types and only six: `dict`, `list`, `str`, `int`, `float`, `bool`, and `None`. (Technically `dict` keys must be `str`, not `int` — a common Python `json` footgun.)

If your `to_dict()` returns *anything* outside this set, the serializer will choke. The discipline:

- **Coords** → store as two floats (or a list of two floats `[x, y]`).
- **Colours** → store as a list of three or four ints `[r, g, b]` or `[r, g, b, a]`. Never a `pygame.Color`.
- **Sets** → store as a sorted list. Sets do not exist in JSON.
- **Tuples** → store as a list. JSON does not distinguish.
- **Enums** → store the `.value` (usually a string or int).
- **Datetimes** → store the ISO-8601 string (`datetime.isoformat()`).
- **bytes** → store as a base64 string. Rarely needed in a save; common in network packets.
- **Custom dataclasses** → call `asdict()` first.

The "tree of primitives" rule is what the decision tree from §3 enforces. If you save only persistent state, and persistent state is by definition data the player cares about, then the values are necessarily simple — numbers, strings, lists, dicts. The moment you find yourself wanting to serialize a `pygame.Surface`, you have crossed the persistent/presentation line.

---

## 10. What we built and what comes next

By the end of this lecture you should have:

- The four-category taxonomy memorised.
- The `GameState` dataclass typed into your editor.
- The `gamestate_to_dict`, `gamestate_from_dict`, `capture_state`, and `apply_state` functions written.
- An audit of your Week-6 `Player` class showing which fields go on disk.

You do not yet have:

- A version-migration framework (Lecture 3).
- An atomic-write path (Lecture 3).
- A choice between JSON and MessagePack (Lecture 2).
- A three-slot UI (Challenge 2, mini-project).

Lecture 2 will compare JSON, MessagePack, and custom binary on size, speed, and human-readability, and you will pick *one* for your mini-project. (Spoiler: JSON. Always JSON for game saves unless you have measured a specific reason not to.) Lecture 3 will version the format, add migrations, add atomic writes, and add corruption recovery. By Sunday you will have shipped a tiny RPG with a save system that is not embarrassing.

---

## References

- **Glenn Fiedler — *Reading and Writing Packets* (Gaffer On Games).** The disk-save and the network-packet have the same shape, and Fiedler's discipline of "every byte is versioned" is the discipline of this lecture. <https://gafferongames.com/post/reading_and_writing_packets/>
- **RFC 8259 — JSON spec.** Twelve pages; sections 1-4 are the syntax. <https://www.rfc-editor.org/rfc/rfc8259>
- **Python `dataclasses` module — official docs.** The `@dataclass` decorator and `asdict()`. <https://docs.python.org/3/library/dataclasses.html>
- **Python `json` module — official docs.** `json.dump`, `json.load`, and the six types it accepts. <https://docs.python.org/3/library/json.html>
- **Pygame docs.** The `pygame.Surface`, `pygame.mixer.Sound`, and `pygame.font.Font` references — the *presentation* types that never go to disk. <https://www.pygame.org/docs/>

---

*Continue to [Lecture 2 — Serialization Formats and Trade-offs](./02-serialization-formats-trade-offs.md).*
