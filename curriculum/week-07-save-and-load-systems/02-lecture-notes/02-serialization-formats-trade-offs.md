# Lecture 2 — Serialization Formats and Trade-offs

> **Duration:** ~2 hours of reading + hands-on.
> **Outcome:** You can choose between JSON, MessagePack, and a custom binary format for any given persistence problem, defending the choice on three axes — file size, write/read time, and human-readability — and you can implement the JSON and MessagePack round-trips from memory.

If you only remember one thing from this lecture, remember this:

> **For a game save, JSON is the default. MessagePack is the answer when the JSON save grows past a few megabytes or the autosave shows up on the profiler. Custom binary is the answer for network packets and replay files, not saves. Pickle is never the answer.**

The lecture compares the three formats on the same `GameState` dataclass from Lecture 1, runs a benchmark in Exercise 3, and gives you a decision rule you can apply without re-running the benchmark every project.

---

## 1. The three formats

We compare three formats. Each handles the same `GameState` from Lecture 1.

| Format         | Type   | Library                | Bytes (small save) | Encode time | Decode time | Human-readable | Cross-language |
|----------------|--------|------------------------|-------------------:|------------:|------------:|:---------------|:---------------|
| JSON           | text   | stdlib `json`          | ~600 B             | ~25 µs      | ~30 µs      | Yes            | Yes            |
| MessagePack    | binary | `msgpack` (PyPI)       | ~340 B             | ~8 µs       | ~10 µs      | No             | Yes            |
| Custom binary  | binary | stdlib `struct`        | ~120 B             | ~3 µs       | ~3 µs       | No             | Per-impl       |
| Pickle (avoid) | binary | stdlib `pickle`        | ~280 B             | ~5 µs       | ~7 µs       | No             | Python-only    |

The numbers in this table come from Exercise 3. They will reproduce on your machine within ±30%. The *ratios* are stable across hardware: MessagePack is ~2x smaller and ~3x faster than JSON; custom binary is ~5x smaller and ~10x faster than JSON; pickle is comparable to MessagePack and disqualified for the reasons in Lecture 1 §7.

---

## 2. JSON — the default

JSON is the *text* format defined in **RFC 8259** (Bray, ed., December 2017). It is twelve pages. It defines exactly seven value types: `object`, `array`, `string`, `number`, `true`, `false`, and `null`. Python's stdlib `json` module maps these to `dict`, `list`, `str`, `int`/`float`, `True`, `False`, and `None`.

### 2.1 The round trip

```python
import json
from save import GameState, gamestate_to_dict, gamestate_from_dict


def save_json(gs: GameState, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(gamestate_to_dict(gs), f, indent=2, sort_keys=True)


def load_json(path: str) -> GameState:
    with open(path, "r", encoding="utf-8") as f:
        return gamestate_from_dict(json.load(f))
```

Four lines per direction. The `indent=2` and `sort_keys=True` flags produce a file that diffs cleanly in Git and can be read by a human in a text editor. Both flags cost about 20% of encode time and are worth it.

### 2.2 What a JSON save looks like

```json
{
  "current_level": "level_03",
  "flags": {
    "met_king": true,
    "bridge_built": false
  },
  "inventory": [
    {"id": "coin", "count": 12},
    {"id": "key_brass", "count": 1}
  ],
  "player_hp": 4,
  "player_hp_max": 5,
  "player_x": 384.5,
  "player_y": 192.0,
  "playtime_seconds": 1247.3,
  "schema_version": 1,
  "slot_name": "slot_01",
  "timestamp_iso": "2026-05-12T19:42:11"
}
```

You can read it. You can edit it in a text editor. You can `grep` for `met_king`. You can `git diff` it across two playthroughs. These are not party tricks. They are the reason JSON is the right default for game saves.

### 2.3 What JSON cannot do

JSON has *no* binary type. There is no way to embed raw bytes — a screenshot, a compressed level, a hash digest — without base64-encoding it first, which inflates by ~33%.

JSON has *no* distinction between integers and floats. `12` and `12.0` decode to different Python types depending on whether the source had a decimal point. Most of the time this is fine. Occasionally it bites — your save writes `playtime_seconds: 0` for a fresh game, your code expects a `float`, and the type check fails.

JSON has *no* date type. Timestamps go in as ISO strings.

JSON is *strictly* UTF-8 (when written without escapes). Pass `ensure_ascii=False` to `json.dump` if you want non-ASCII characters in player names; pass the default if you want safe-everywhere ASCII output.

JSON does *not* preserve key order in the spec. Python's `json.load` preserves insertion order (since Python 3.7), and `sort_keys=True` makes it deterministic on write. Other languages may not.

### 2.4 When to use JSON

For game saves: **always, unless you have measured a reason not to.**

For settings files (volume, keybinds): always.

For level data (tilemaps, entity placement) that humans edit: always.

For network packets in a real-time game: no — JSON's text overhead is too high. Use MessagePack or a custom format.

For replay files (a recording of every input frame for two minutes): no — the file grows to hundreds of kilobytes and a binary format compresses better.

---

## 3. MessagePack — the binary JSON

MessagePack is a *binary* format that maps one-to-one to JSON's type system. The spec is six pages. Every JSON value has a corresponding MessagePack value; the conversion is lossless in both directions.

The "binary" qualifier matters in two ways. First, MessagePack files are not text — opening one in a text editor gives you garbage. Second, MessagePack adds two types JSON lacks: a real `bin` (raw bytes) type and a real integer-vs-float distinction.

### 3.1 The round trip

```python
import msgpack
from save import GameState, gamestate_to_dict, gamestate_from_dict


def save_msgpack(gs: GameState, path: str) -> None:
    payload = msgpack.packb(gamestate_to_dict(gs), use_bin_type=True)
    with open(path, "wb") as f:
        f.write(payload)


def load_msgpack(path: str) -> GameState:
    with open(path, "rb") as f:
        payload = f.read()
    return gamestate_from_dict(msgpack.unpackb(payload, raw=False))
```

Note the `wb` and `rb` modes — binary, not text. The `use_bin_type=True` and `raw=False` flags opt into MessagePack 2.0 type semantics (distinguishing `str` from `bytes`). Without them you get a 2010-era format that conflates the two; opt in.

### 3.2 What a MessagePack save looks like

```
8b a1 6e a8 6c 65 76 65 6c 5f 30 33 a5 66 6c 61
67 73 82 a8 6d 65 74 5f 6b 69 6e 67 c3 ad 62 72
69 64 67 65 5f 62 75 69 6c 74 c2 ...
```

Hex bytes. You cannot read it. You cannot edit it in a text editor. You can decode it programmatically; `msgpack.unpackb` is the only practical reader.

The *upside*: it is roughly half the size of the equivalent JSON. The `met_king: true` boolean is one byte instead of fifteen. Numbers are packed as varints, not as decimal text. Strings carry a length prefix instead of being delimited by quotes.

### 3.3 When to use MessagePack

For game saves: **when JSON shows up on the profiler.** If your save is 2 KB and saves in 1 ms, JSON is correct. If your save is 500 KB and the save stutter is 30 ms, switch to MessagePack and the stutter halves.

For autosave files specifically: **maybe.** Autosaves run more often than manual saves, so the per-write cost matters more. If you have a measurable stutter on autosave, MessagePack is the cheapest fix.

For network packets: **yes.** Real-time multiplayer absolutely uses a binary format. MessagePack is one of three reasonable choices (the others are FlatBuffers and Protobuf). C11 does not cover networking; if you ever do, remember MessagePack.

For interchange with other languages: **yes.** MessagePack has high-quality libraries in C, C++, Go, Rust, JavaScript, and Java. JSON is more universal but MessagePack is universal *enough*.

### 3.4 The installation note

MessagePack is *not* in the Python stdlib. The reference implementation is on PyPI:

```bash
pip install msgpack
```

This is the only third-party package we install this week. The C-accelerated path requires a wheel; for any modern Python on macOS, Linux, or Windows, `pip install msgpack` is one command and zero compilation.

---

## 4. Custom binary — fastest, smallest, most fragile

The third option is to write the bytes yourself with `struct.pack`. The stdlib `struct` module turns a tuple of numbers into a fixed-layout byte string and back.

### 4.1 The round trip

```python
import struct


# A toy format: "C11SAVEv1" magic, then 4 floats (x, y, hp, hp_max).
def save_binary(x: float, y: float, hp: int, hp_max: int, path: str) -> None:
    payload = b"C11SAVEv1" + struct.pack("<ffii", x, y, hp, hp_max)
    with open(path, "wb") as f:
        f.write(payload)


def load_binary(path: str) -> tuple[float, float, int, int]:
    with open(path, "rb") as f:
        payload = f.read()
    assert payload[:9] == b"C11SAVEv1", "wrong magic"
    return struct.unpack("<ffii", payload[9:])
```

The `<ffii` format string means: little-endian, then two 32-bit floats, then two 32-bit ints. The file is exactly 25 bytes: 9 bytes of magic + 16 bytes of payload.

### 4.2 Why custom binary is a bad fit for game saves

Three reasons.

**Reason A — Schema rigidity.** The format string `<ffii` is the schema. If you add a `coins` field, every existing save is now misaligned and `struct.unpack` will either crash or silently produce garbage. You can fix this with version bytes and per-version unpackers — and at that point you have re-invented MessagePack, badly.

**Reason B — Dynamic data is awkward.** An inventory of `N` items has `N * 16` bytes plus a length prefix. You can write the code; it is just bookkeeping. But it is *not* what `struct` is for. `struct` is for fixed-shape records.

**Reason C — Debugging is painful.** A JSON save can be opened in any editor. A MessagePack save can be dumped with `msgpack.unpackb`. A custom binary save needs *your* unpacker to be debugged with *your* unpacker. When something goes wrong at 11pm three weeks before launch, the format that lets you eyeball the file wins.

### 4.3 When custom binary *is* the right answer

Custom binary belongs in three places:

- **Network packets.** Real-time multiplayer. Bit-packed integers, fixed shape, every byte counts.
- **Replay files.** A two-minute replay of every input frame is fifteen thousand records. Bit-packed binary fits this perfectly; JSON would be hundreds of KB.
- **Image/audio file containers.** PNG, OGG, WAV. These *are* custom binary formats; we just don't write them ourselves.

For game saves: no. Use JSON.

---

## 5. Pickle — covered for "why not"

We mentioned `pickle` in Lecture 1 §7 and we will mention it again. Pickle is not a serialization format; it is a *Python object graph snapshot*. It executes Python code on load. It encodes class paths and attribute dicts directly.

- **It executes code on load.** A malicious pickle file is a malicious Python script.
- **It does not survive refactoring.** Rename `Player` to `Character` and every old pickle is broken.
- **It is Python-only.** No tool, no editor, no other language reads it.

`pickle` is the right answer for *one* thing: passing Python objects between processes via `multiprocessing.Queue`. That is in-process IPC under your own control. A *save file* is none of those.

The C11 rule: **`pickle` is for `multiprocessing`. Game saves are JSON or MessagePack.**

---

## 6. The size/speed/readability triangle

Here is the trade-off geometry, in plain English:

```
                READABILITY
                    ▲
                    │
                    │      JSON
                    │       ●
                    │
                    │
                    │
                    │
                    │
                    │    MessagePack
                    │         ●
                    │
                    │                 Custom binary
                    │                       ●
                    │─────────────────────────────► SPEED + SIZE
                    │
```

JSON gives you readability and cross-language at the cost of size and speed.
MessagePack gives you size and speed at the cost of readability.
Custom binary gives you maximum size and speed at the cost of *everything else*.

You pick *two*. For game saves, "readability and cross-language" wins. For network packets, "size and speed" wins. The trade-off is structural; you cannot have all three.

---

## 7. Compression — the orthogonal axis

Compression is *orthogonal* to format choice. You can gzip a JSON file or a MessagePack file or a custom binary file. The gain depends on the format's redundancy.

JSON compresses *extremely* well. The format is repetitive — every record repeats its key names — and gzip exploits exactly this kind of redundancy. A 200 KB JSON save typically gzips to ~25-35 KB, a ~6-8x reduction.

MessagePack compresses moderately well. Keys are still repeated (the format is still self-describing), but the binary type prefixes are less compressible than JSON's text. Expect ~2-3x reduction.

Custom binary barely compresses at all. The bytes are already dense; gzip has nothing to remove.

The implication: **JSON + gzip is competitive with raw MessagePack on file size**, and ships with stdlib only. If your save is large enough that file size matters, the cheapest fix is one line:

```python
import gzip
import json

# Save
with gzip.open(path, "wt", encoding="utf-8") as f:
    json.dump(payload, f)

# Load
with gzip.open(path, "rt", encoding="utf-8") as f:
    payload = json.load(f)
```

Change `open` to `gzip.open` and add the `.gz` extension. Your 200 KB save is now 30 KB and remains readable (via `gunzip save.json.gz | jq .`).

For game saves, JSON + gzip is the *correct* answer for files larger than ~50 KB. Below 50 KB, raw JSON is fine.

---

## 8. The Pygame-specific rule

Pygame ships several types that must *never* appear in a save file:

- `pygame.Surface` — the image data. Derived from a sprite-sheet path.
- `pygame.mixer.Sound` — the audio data. Derived from a `.wav` path.
- `pygame.font.Font` — the font binding. Derived from a font path.
- `pygame.time.Clock` — the frame clock. Process-local.
- `pygame.Rect` — *technically* serializable (four ints) but conventionally *not* saved. Store the bounding coords as a list-of-four-ints if you must.

The discipline from Lecture 1 §2.4 catches all of these. If you put a `pygame.Surface` in your `GameState`, `json.dump` throws `TypeError`, and the message tells you exactly where the violation is. The error message *is* the design enforcement; trust it.

A worked-out anti-pattern:

```python
# WRONG — the Surface is derived from "level_03.png", which is a string.
@dataclass
class GameStateWrong:
    level_surface: pygame.Surface  # 200 KB of pixel data per save?

# RIGHT — store the level ID, rebuild the Surface on load.
@dataclass
class GameStateRight:
    current_level: str  # "level_03"
```

The right shape stores 8 bytes ("level_03" plus quotes plus key). The wrong shape stores 200 KB of pixel data that the game already has on disk in `assets/levels/level_03.png`. Saving a derived asset *and* the source of truth is a corruption-by-drift bug waiting to happen.

---

## 9. The benchmark protocol

Exercise 3 runs a benchmark with this shape:

1. Build a `GameState` with realistic contents — 20-item inventory, 30-flag world, modest-size strings.
2. Serialize 10,000 times in JSON, record the median microseconds per op and the bytes-on-disk.
3. Serialize 10,000 times in MessagePack, record the same.
4. Serialize 10,000 times in a hand-written `struct.pack` form, record the same.
5. (Stretch) Serialize 10,000 times in JSON + gzip, record the same.
6. Print a table. Eyeball the ratios.

The 10,000-iteration count is the lower bound for stable medians on a modern CPU. Lower counts swing wildly with OS noise. Higher counts are fine; the benchmark takes ~2 seconds at 10,000.

Reporting medians (not means) is deliberate. Median is robust to GC pauses, OS interrupts, and the one slow iteration that always shows up. Mean is misleading on micro-benchmarks. (If you want the mean *and* the median *and* the p95 and p99, use `statistics.quantiles`. For Exercise 3 the median is enough.)

---

## 10. The decision rule

You now have enough information to pick a format without re-running the benchmark for every project. The rule, in three lines:

1. **Game save, < 50 KB:** JSON. Always.
2. **Game save, > 50 KB:** JSON + gzip. Stdlib only.
3. **Hot path (autosave every few seconds, profile shows the encode/decode), and you can install one package:** MessagePack.

Three lines. The rule covers ~98% of indie game saves. The 2% it does not cover — replay files, network packets, asset containers — is out of scope this week.

---

## 11. What we built and what comes next

By the end of this lecture you should have:

- The three formats in your head, with the size/speed/readability trade-off internalised.
- The JSON round-trip and the MessagePack round-trip written or at least sketched.
- The decision rule (§10) memorised.
- The Pygame-specific "never save a Surface" discipline internalised.

You do not yet have:

- A version-migration framework (Lecture 3).
- Atomic writes and crash safety (Lecture 3).
- Corruption detection (Lecture 3).
- Save slots and autosave (mini-project + Challenge 2).

Lecture 3 closes the loop. By the end of Lecture 3 you have all the pieces for a real, robust save system; the mini-project is the assembly.

---

## References

- **RFC 8259 — JSON spec (IETF, 2017).** <https://www.rfc-editor.org/rfc/rfc8259>
- **MessagePack specification.** <https://github.com/msgpack/msgpack/blob/master/spec.md>
- **Python `json` module — official docs.** <https://docs.python.org/3/library/json.html>
- **Python `msgpack` library (PyPI).** <https://github.com/msgpack/msgpack-python>
- **Python `struct` module — official docs.** <https://docs.python.org/3/library/struct.html>
- **Python `gzip` module — official docs.** <https://docs.python.org/3/library/gzip.html>
- **Glenn Fiedler — *Serialization Strategies* (Gaffer On Games).** The three-strategy taxonomy; we use the "read-or-write function" strategy via `to_dict()`/`from_dict()`. <https://gafferongames.com/post/serialization_strategies/>
- **Pygame docs.** The types that must *not* appear in a save. <https://www.pygame.org/docs/>

---

*Continue to [Lecture 3 — Versioning, Migration, and Recovery](./03-versioning-migration-and-recovery.md).*
