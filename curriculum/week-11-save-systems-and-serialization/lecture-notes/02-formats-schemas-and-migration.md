# Lecture 2 — Formats, Schemas, and the Migration Story

> **Duration:** ~2 hours of reading plus hands-on with one format.
> **Outcome:** You can name four save formats shipped games actually use and defend the choice; you can refuse two formats by name and cite the reason; you can write a v1 schema, a v2 schema, and a single-step migration function.

If you only remember one thing from this lecture, remember this:

> **A format is forever. The first save your game writes is the format you migrate, patch, and apologise for for the rest of the game's life. Pick a format with a serialisation library on at least three platforms, a public spec, and a default that does not execute code on load.**

The lecture begins with a tour of the four formats we *do* use (JSON, MessagePack, Godot resources, Protobuf), narrows to the two formats we refuse (pickle, BinaryFormatter), and ends with the migration story — the discipline that makes a save file from a year ago load correctly in this year's build.

We lean on the MessagePack specification and the Pydantic v2 documentation throughout. The pickle and BinaryFormatter sections cite the vendors' own deprecation notices.

---

## 1. The four formats we use

The formats below are ordered by *frequency-in-actual-shipped-games*, not by quality. JSON is the most common because it is the easiest to debug; MessagePack ships in many AAA games because it is the cheapest binary that is not a foot-gun.

### 1.1 JSON

The lingua franca. Every programming language has a parser. Every text editor renders it readably. Every git diff over a JSON file is meaningful to a human reading the diff.

The data model is exactly: `null`, `true`/`false`, IEEE 754 double-precision float (encoded as ASCII), string (Unicode, UTF-8 in transport), array, object (string-keyed map). That is the whole specification. Anything that does not fit one of those six types has to be encoded as one of them (typically a string for dates, an object for tuples).

The Python module is `json` in the standard library. The Godot type is `JSON`, also built in. Both produce and consume the same bytes; both ship in every install. No dependency, no build step, no version skew.

The cost is **size** and **parse speed**.

Size: a 64-bit float encodes as up to 17 characters of ASCII versus 8 bytes binary; a typical save with 100 floats and 200 strings is 2x to 3x larger as JSON than as MessagePack. A 50 KB JSON save is a 15 KB MessagePack save.

Parse speed: a JSON parser walks the input byte-by-byte; a binary parser reads a length prefix and `memcpy`s. Both are fast on modern hardware (under a millisecond for a 50 KB save), but the binary parser is 2x to 4x faster, and on slow storage the difference shows up.

**Use JSON for:**

- Every prototype and dev build.
- Games where modding-by-hand-editing is a feature, not a bug.
- Games where the QA team needs to hand-write a save to repro a bug.
- Settings files, regardless of game stage.

**Stop using JSON when:** the save is large enough (>100 KB) for the size cost to be visible, or the player should not be able to edit the save trivially.

### 1.2 MessagePack

A binary format with exactly JSON's data model and roughly half its size. The spec is short (~600 lines of markdown), the library support is universal (Python, GDScript via a small native library, C#, JavaScript, Rust, Go, every other language a game ships in), and the design intent is *"binary JSON without giving up portability."*

The on-wire format uses one-byte type tags followed by the encoded payload. An integer in 0..127 is one byte. A short string is one tag byte plus the bytes of the string. A float is one tag byte plus 8 bytes IEEE 754. Maps and arrays carry a length prefix; the parser does not have to scan for delimiters.

The Python library is `msgpack` on PyPI, MIT-licensed, available in every distro and PyPI mirror. Installation is `pip install msgpack`; usage is `msgpack.packb(value)` and `msgpack.unpackb(blob)`.

Godot ships no built-in MessagePack support as of 4.3. The options are:

1. A pure-GDScript implementation. Two hundred lines; the stretch challenge for the week.
2. A GDExtension binding to the C library. Faster, more setup, an extra build artefact to ship per platform.
3. A round-trip through a Python tool (the dev computes the MessagePack, ships the bytes in the game's data folder, the game reads the bytes and round-trips through its hand-written or extension-based parser).

For an indie game shipping cross-platform, the second option is the production answer; the first option is good enough for an indie game shipping on PC only.

**Use MessagePack for:**

- Shipped games where the player should not trivially edit saves.
- Games where save size matters (large-state simulation games, save-bloat-prone roguelikes).
- Inter-process or networked persistence where parse speed matters.

**Stop using MessagePack when:** debuggability matters more than size, or the deployment environment lacks a library binding. JSON is the fallback every time.

### 1.3 Godot's `Resource` save (`.tres` / `.res`)

The native format. `ResourceSaver.save(resource, path)` serialises any `Resource` subclass; `ResourceLoader.load(path)` deserialises it back. The output is either `.tres` (text, INI-ish) or `.res` (binary, Godot-internal).

The data model is *whatever Godot's `Resource` system supports* — which is a superset of JSON's, including typed arrays, packed scenes, NodePaths, Color, Vector2/3/4, Quaternion, and any user-defined `Resource` subclass with `@export` properties.

The cost is **portability**. The format is a Godot-engine format; reading it outside of Godot requires either an unofficial port or running Godot in headless mode. If your game ships only inside Godot and your tooling pipeline is entirely Godot-based, this is fine. If you have a Python tool that generates QA test saves, this is a problem.

The other cost is **version pinning**. The `.tres` and `.res` formats have changed between Godot 3.x and 4.x; a save written in 4.0 may not load in 4.1 if the engine team changed the layout. The release notes call this out when it happens; the practical answer is to migrate the save format at engine-upgrade time.

**Use Godot resources for:**

- All-Godot pipelines where every saved object is already a `Resource`.
- Settings that are best expressed as exported properties on a singleton.
- Small one-developer projects where the convenience outweighs the lock-in.

**Stop using Godot resources when:** any non-Godot tool needs to read or write the save, or the project ships across multiple engine versions in production simultaneously.

### 1.4 Protocol Buffers (Protobuf)

A schema-first format. You write a `.proto` file describing the message structure. The protobuf compiler (`protoc`) generates loader code in every language you target. The wire format is a tightly-packed binary; the schema is the source of truth.

Protobuf's strengths are *cross-language* and *schema-versioning-as-a-first-class-concern*. Adding a new field to a message is a backwards-compatible operation by design; the field number is the identity, and old readers ignore unknown fields. Removing a field is also backwards-compatible if you reserve the field number to prevent reuse.

The cost is the **toolchain**. You need `protoc` installed. You need to commit `.proto` files and generated stubs. You need a build step that re-runs `protoc` when the `.proto` changes. None of these is hard; all of these are friction for a one-developer project.

**Use Protobuf for:**

- Games with a server component where the same message round-trips between server (Go, Java, C++) and client (Godot, Unity).
- Projects where schema-versioning *is* a contract — usually live-service games with frequent server updates.
- Pipelines where multiple tools (a level editor, a balance-tuning sheet, the runtime) all need to read the same format.

**Stop using Protobuf when:** the project is single-engine and single-developer. The toolchain overhead is not paid back.

### 1.5 Summary table

| Format          | Size     | Parse speed | Debuggable? | Cross-language?       | Engine lock-in? | Schema migration?      |
|-----------------|----------|-------------|-------------|-----------------------|-----------------|------------------------|
| JSON            | Large    | Fast        | Yes         | Yes (universal)       | None            | Manual                 |
| MessagePack     | Small    | Faster      | No (binary) | Yes (most languages)  | None            | Manual                 |
| Godot Resource  | Variable | Fastest     | `.tres` yes | No (Godot only)       | High            | Manual / engine-coupled|
| Protobuf        | Smallest | Fastest     | No (binary) | Yes (every language)  | None            | First-class            |

For a typical indie game shipping cross-platform on PC, the dev build uses JSON, the shipped build uses MessagePack, and Protobuf is the right answer only when there is a server.

---

## 2. The two formats we refuse

The two formats below are convenient for an afternoon and dangerous for the rest of the game's life. We name them, we cite the vendors' own deprecation notices, and we refuse them. There is no "but in this one case it is okay." There is no case.

### 2.1 Python's `pickle`

`pickle.dumps(obj)` serialises any Python object — including bound methods, classes, lambdas with closures — to a byte stream. `pickle.loads(data)` deserialises the byte stream back. Convenient. Dangerous.

The mechanism: a pickle stream is a stack-based bytecode. One of its opcodes, `REDUCE`, invokes any callable the pickle says to invoke, with arguments the pickle provides. An attacker who controls the bytes of the pickle controls the call. The standard exploit is one line of pickle that loads `os.system` and calls it with the attacker's command string.

The Python documentation says, at the top of the `pickle` module page:

> The pickle module is not secure. Only unpickle data you trust. It is possible to construct malicious pickle data which will execute arbitrary code during unpickling.

This is the vendor's own statement. Quoted verbatim from the standard library.

In the context of a save file: a save file is, by definition, input the program reads from disk into memory. The disk is controlled by the user. The user can be the player (who edits their own save, fine), can be a malicious actor who replaces a player's save (cloud sync replay attacks have been used as a vector for this), can be a malicious mod author who ships a save file as part of a mod. In all three cases, calling `pickle.loads` on the save's bytes is *executing code from the file*.

A pickle-based save system is not a save system. It is a remote-code-execution vulnerability with a benign-sounding name.

**The rule: never use `pickle.load` or `pickle.loads` on data the game read from disk.**

The replacement is **JSON** for everything pickle was being used for. The migration is mechanical: replace `dataclass` instances with Pydantic `BaseModel` instances (or use the `dataclasses-json` library if you cannot adopt Pydantic), `pickle.dumps(x)` with `x.model_dump_json()`, and `pickle.loads(b)` with `MyModel.model_validate_json(b)`. The same code; safer bytes.

### 2.2 .NET's `BinaryFormatter`

The .NET analogue of pickle. Same data model — *every type in the runtime, including those whose constructors execute side-effecting code*. Same vulnerability — *deserialising attacker-controlled bytes constructs attacker-named types*. Same vendor response — Microsoft has *removed* `BinaryFormatter` from .NET 9 entirely.

Microsoft's own deprecation page:

> The BinaryFormatter type is dangerous and is not recommended for data processing. Applications should stop using BinaryFormatter as soon as possible, even if they believe the data they're processing to be trustworthy.

CVE history is extensive: CVE-2017-9805 (Apache Struts via XStream, a similar mechanism), the entire "insecure deserialisation" category in the OWASP Top 10, multiple .NET-specific CVEs every year.

The replacement is **System.Text.Json** for everything (the built-in JSON serialiser in modern .NET) or **MessagePack-CSharp** for binary needs. Both are typed-and-validated; neither constructs arbitrary types.

**The rule: never call `BinaryFormatter.Deserialize` on bytes that came from outside the program's own memory.**

### 2.3 The pattern

Both formats embody the same anti-pattern: *deserialise to whatever type the bytes ask for*. Any format with this property is unsafe for untrusted input. Other formats with the same property: PHP's `unserialize`, Ruby's `Marshal.load`, Java's `ObjectInputStream.readObject`. All have CVE histories. All should be refused for save files.

The safe pattern is: *parse to a typed schema*. The schema is committed in the program's source code. Anything in the file that does not match the schema is rejected. The deserialiser cannot construct types the schema does not name. Pydantic does this. Protobuf does this. System.Text.Json with `[JsonConverter]` attributes does this. MessagePack with a schema layer (e.g. `msgpack-typed-decoder`) does this.

JSON without a schema layer is a middle case: the parser produces only the six JSON types, none of which are dangerous, but the *application code that reads the parsed dict* can still misinterpret values (the `gold = -2_000_000_000` case from the README). The fix is to add a schema layer — Pydantic on Python, custom validators on GDScript — between the parser and the game.

---

## 3. Schema validation on load

The save file on disk is untrusted input. The file may have been corrupted (a half-written file from a crash), modified (the player edited it), or invented (a tool generated it). The loader's first job is to verify that the parsed dictionary matches the schema before any other code touches it.

### 3.1 Pydantic on Python

Pydantic v2's `BaseModel` is the canonical Python answer. Define the schema as a class:

```python
from pydantic import BaseModel, Field
from typing import Literal

class SaveV2(BaseModel):
    version: Literal[2]
    player_name: str = Field(min_length=1, max_length=64)
    current_score: int = Field(ge=0, le=10_000_000)
    session_start_timestamp: int = Field(ge=0)
    highest_score_this_session: int = Field(ge=0)
    current_level: str = Field(min_length=1, max_length=128)
```

Load with validation:

```python
import json
from pathlib import Path

def load_v2(path: Path) -> SaveV2:
    raw: str = path.read_text(encoding="utf-8")
    parsed: dict = json.loads(raw)
    return SaveV2.model_validate(parsed)
```

A malformed save raises `pydantic.ValidationError` with a structured list of every field that failed. The game catches the error, presents a "save is corrupted, load backup?" prompt, and falls back to the previous-good save.

The `Literal[2]` on the `version` field is what makes the loader reject v1 saves at v2's loader: a v1 save's `"version": 1` field does not match `Literal[2]`. The loader for v1 has its own model, `SaveV1`, with `Literal[1]`. The migration function bridges the two; we cover that next.

### 3.2 Hand-written validation in GDScript

GDScript has no Pydantic. The equivalent is a function that walks the parsed dictionary and checks each field's type, range, and presence:

```gdscript
func _validate_save_dict(d: Dictionary) -> bool:
    if not d.has("version"):
        push_error("save: missing 'version' field")
        return false
    if not (d["version"] is int):
        push_error("save: 'version' is not int")
        return false
    if not d.has("player_name"):
        push_error("save: missing 'player_name' field")
        return false
    if not (d["player_name"] is String):
        push_error("save: 'player_name' is not String")
        return false
    if d["player_name"].length() == 0 or d["player_name"].length() > 64:
        push_error("save: 'player_name' wrong length")
        return false
    # ... and so on for every field
    return true
```

The function is verbose. It is the verbosity that earns its keep: every field's contract is in one place, in the source code, readable as a single contiguous block. When QA reports "the loader accepted a save with a 600-character name," the fix is a one-line edit in a known location.

The mini-project's `save_manager.gd` ships a complete `_validate_save_dict` for the v2 schema. Reuse the pattern.

### 3.3 What validation *cannot* catch

Validation enforces the *schema*; it cannot enforce *semantic invariants* the schema does not name. A save with `current_score = 10_000_000` (the upper bound) is valid by schema; a save with `current_score = 10_000_000` and `levels_played = 0` is suspicious by semantics. The latter is a game-logic check, not a schema check.

The line is judgement. Schema checks are cheap and total; semantic checks are expensive and partial. Most games run schema checks on every load and semantic checks only on a "load a save from a different player" path. The mini-project covers schema checks; semantic checks are noted in the homework.

---

## 4. The migration story

The hardest single discipline in save systems is making sure the save you wrote yesterday loads correctly tomorrow when you have changed the schema. Migration is the discipline.

### 4.1 The version field

Every save file carries a top-level integer `version` field. The field is the first thing the loader reads:

```python
def load(path: Path) -> SaveLatest:
    raw: str = path.read_text(encoding="utf-8")
    parsed: dict = json.loads(raw)
    version: int = parsed["version"]
    return _migrate_to_latest(parsed, from_version=version)
```

The version field is monotonically increasing. v1, v2, v3, ... — never reused, never skipped, never decremented.

Adding a field is a minor version bump (v1 → v2). Removing a field is a major event (v2 → v3); even though Python's JSON does not enforce structure, removing a field that the game's *code* once read is a behaviour change.

Renaming a field is *two* migrations: first add the new field copying from the old (v2 → v3), ship a version that writes both, then drop the old field in a later version (v3 → v4). Always two steps; never one.

### 4.2 Single-step migrations, chained

The discipline that scales: write *one* migration function per version step. Never write a `migrate_v1_to_v3`. If a v1 save needs to become v3, the loader runs `migrate_v1_to_v2` and then `migrate_v2_to_v3`.

```python
MIGRATIONS: dict[int, callable] = {
    1: migrate_v1_to_v2,
    2: migrate_v2_to_v3,
    3: migrate_v3_to_v4,
}

def _migrate_to_latest(parsed: dict, from_version: int) -> SaveLatest:
    current: dict = parsed
    while current["version"] < CURRENT_VERSION:
        step = MIGRATIONS[current["version"]]
        current = step(current)
    return SaveLatest.model_validate(current)
```

The win: each migration step is small (one or two field changes), each is independently testable, and the dispatch table is the migration history. The first time you have to support a five-version-old save in a shipped game, this code is the difference between a one-day patch and a one-week project.

### 4.3 A complete v1-to-v2 example

The cursor demo from Lecture 1 introduces `current_level` in v2. The migration:

```python
def migrate_v1_to_v2(v1: dict) -> dict:
    assert v1["version"] == 1
    v2: dict = dict(v1)
    v2["version"] = 2
    v2["current_level"] = "level_01"  # safe default for a v1 save
    return v2
```

The default `"level_01"` is the start of the game; if the v1 save had progressed past level 1, the player loses some progress. The acceptable answer when v1 has no information to derive the field from. The alternative — inferring from `current_score` — risks miscategorising and giving the player a wrong level; better to under-set safely than over-set wrongly.

The exercises walk through several flavours of this pattern. The mini-project ships exactly this migration as a tested unit.

### 4.4 What if the version field is missing

The first save your game ever wrote may not have had a `version` field at all (especially likely if you bootstrapped from a "save the dict, load the dict" prototype). The loader has to handle this:

```python
def load(path: Path) -> SaveLatest:
    parsed: dict = json.loads(path.read_text())
    if "version" not in parsed:
        parsed["version"] = 1  # treat unversioned saves as v1
    return _migrate_to_latest(parsed, from_version=parsed["version"])
```

The choice to call unversioned saves "v1" is a convention; the alternative is to call them "v0" and have a `migrate_v0_to_v1` that adds the field. Either works. The discipline is to *handle* the unversioned case explicitly rather than crash on the missing key.

If you are starting a new game today and following this lecture from week zero, every save starts at v1 and the issue does not arise. The migration discussion is for the day after the first patch.

### 4.5 What never to do

A short list of migration anti-patterns. Each has shipped in a real game; each has caused a real save-file outage. None is hypothetical.

- **Branching on field presence to determine the version.** ("If the save has `current_level`, it is v2, else v1.") This works for two versions and stops working at three; by v4 the branching tree is unmaintainable.
- **Mutating saves on disk without writing them back.** The migration runs in memory, the player plays, the save is written. The on-disk file is v1 until the player saves; the in-memory copy is v2. Different fields will diverge.
- **Writing a one-step `v1_to_vN` migration for "speed."** Speed is not the issue. Maintainability is. The chain of single-step migrations is the maintainable form.
- **Removing migrations after "everyone has upgraded."** You do not know everyone has upgraded. Some player's Steam install has been offline for two years. Keep migrations forever.
- **Forgetting to bump the version on a schema change.** Adding a field without bumping the version means two different shipped builds can write incompatible "v1" files. The version is bumped *every time* a schema changes, not just on big changes.

---

## 5. Recap

We covered:

- Four formats we use: JSON for dev/mods, MessagePack for ship, Godot resources for all-Godot, Protobuf for server-client.
- Two formats we refuse: pickle in Python, BinaryFormatter in .NET. Both because *deserialise to attacker-named types is equivalent to code execution*.
- Schema validation on load: Pydantic on Python, hand-written `_validate_save_dict` on GDScript. The save on disk is untrusted input; validate before use.
- The migration discipline: a `version` field, single-step migrations chained in a dispatch table, no "removing migrations after everyone has upgraded."

Lecture 3 picks up the *runtime* concerns: atomic writes, integrity checks, backup rotation, and the conceptual survey of the three cloud-save services games actually ship against.
