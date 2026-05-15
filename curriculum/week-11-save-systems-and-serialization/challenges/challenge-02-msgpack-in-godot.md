# Challenge 02 — Pure-GDScript MessagePack Round-Trip

**Difficulty:** Stretch. About 200 lines of GDScript across a writer, a reader, and a small test scene.
**Estimated time:** Three to four hours including reading the MessagePack spec.

---

## What you are building

A pure-GDScript implementation of a *subset* of MessagePack that can round-trip the same save dictionaries Exercise 06 round-trips through JSON. No GDExtension, no native library, no external dependencies. Two hundred lines of GDScript that produce and consume bytes interchangeable with `msgpack-python`'s output.

The motivation: Godot ships no built-in MessagePack support as of 4.3. The shipped indie-game options are a GDExtension binding (fast, more build-system overhead) or a pure-GDScript implementation (slower, no extra artefacts to ship). The pure-GDScript option is the right one for projects where save throughput is not the bottleneck — which is most projects.

You do not implement the full MessagePack spec. The spec covers timestamps, raw extension types, 32-bit/64-bit integer variants, and several optional features your save files never produce. You implement the *subset* the cursor demo and the mini-project save actually use: positive integers up to 2^53, negative integers down to -2^31, IEEE 754 doubles, UTF-8 strings up to 2^32-1 bytes, arrays of up to 2^32-1 elements, maps of up to 2^32-1 entries, booleans, and `null`.

---

## The deliverable

Two files in your homework directory:

1. **`challenge-02-msgpack.gd`** — a class with the API:

   ```gdscript
   class_name MsgPack
   static func encode(value: Variant) -> PackedByteArray
   static func decode(bytes: PackedByteArray) -> Variant
   ```

2. **`challenge-02-test.gd`** — a small test runner that, when attached to a `Node` and run as a scene, exercises the encoder and decoder against the subset listed above, prints a pass/fail line per type, and ends with a final `OK` or `FAIL` line. The test runner must also verify *cross-implementation compatibility* against a small Python script that writes bytes with `msgpack.packb` and reads bytes with `msgpack.unpackb`. The Python script is part of the deliverable.

The cross-implementation check is the load-bearing part. A pure-GDScript implementation that round-trips against *itself* but produces non-standard bytes is interesting in isolation and useless in practice. The whole point of MessagePack is the cross-language data exchange; if your bytes do not round-trip through `msgpack-python`, the implementation is not MessagePack.

---

## Constraints

- **Two hundred lines is a target, not a ceiling.** A clean implementation fits in 200 lines. A defensive implementation with full bounds checks lands at 280 lines. Both are acceptable; sub-200 with shortcuts that crash on edge cases is not.

- **Use Godot 4.x typed syntax throughout.** Function signatures specify parameter types and return types. Variables use `var x: T = ...`. The compiler catches more bugs than you might expect.

- **The encoder is the easy half.** The decoder is the hard half. The decoder needs a *cursor* (an index into the byte array that advances) and recursive parsing of array and map contents.

- **Format tags from the spec.** The MessagePack spec at [github.com/msgpack/msgpack/blob/master/spec.md](https://github.com/msgpack/msgpack/blob/master/spec.md) lists every type's one- or two-byte tag. Implement the tags exactly as the spec lists; deviation is a non-conformance bug.

  The minimum subset to implement (in increasing tag value):

  | Format     | Tag       | Notes                                   |
  |------------|-----------|-----------------------------------------|
  | positive fixint | `0x00-0x7f` | Integers 0..127 in one byte         |
  | fixmap     | `0x80-0x8f` | Maps with up to 15 entries              |
  | fixarray   | `0x90-0x9f` | Arrays with up to 15 elements           |
  | fixstr     | `0xa0-0xbf` | Strings with up to 31 bytes             |
  | nil        | `0xc0`    | `null`                                  |
  | false      | `0xc2`    |                                         |
  | true       | `0xc3`    |                                         |
  | float 64   | `0xcb`    | IEEE 754 double, 8 bytes big-endian     |
  | uint 8     | `0xcc`    | Integers 128..255 in two bytes          |
  | uint 16    | `0xcd`    | Integers 256..65535 in three bytes      |
  | uint 32    | `0xce`    | Integers 65536..2^32-1 in five bytes    |
  | int 8      | `0xd0`    | Integers -128..-33                      |
  | int 16    | `0xd1`    | Integers -32768..-129                   |
  | int 32    | `0xd2`    | Integers -2^31..-32769                  |
  | negative fixint | `0xe0-0xff` | Integers -32..-1                  |
  | str 8      | `0xd9`    | Strings 32..255 bytes                   |
  | str 16     | `0xda`    | Strings 256..65535 bytes                |
  | str 32     | `0xdb`    | Strings 65536..2^32-1 bytes             |
  | array 16   | `0xdc`    | Arrays 16..65535 elements               |
  | array 32   | `0xdd`    | Arrays 65536..2^32-1 elements           |
  | map 16     | `0xde`    | Maps 16..65535 entries                  |
  | map 32     | `0xdf`    | Maps 65536..2^32-1 entries              |

  64-bit integers, binary blobs, and extension types are out of scope.

---

## What to verify against `msgpack-python`

Build a small Python script `verify_msgpack.py` that:

1. Takes a path to a file as its argument.
2. Reads the bytes from the file.
3. Calls `msgpack.unpackb(bytes, raw=False, strict_map_key=False)` and prints the resulting Python value as `repr(...)`.

Your GDScript test runner writes encoded bytes to disk, then invokes the Python script via `OS.execute` to confirm the bytes parse correctly. (You can also do the reverse: have the Python script write bytes via `msgpack.packb`, then have your GDScript decoder load them.)

A complete cross-implementation pass verifies both directions: GDScript encodes → Python decodes (matches expected); Python encodes → GDScript decodes (matches expected).

---

## Marking criteria

| Criterion                                            | Points |
|------------------------------------------------------|-------:|
| `MsgPack.encode` covers all listed format tags       |   4    |
| `MsgPack.decode` covers all listed format tags       |   4    |
| Round-trip works for nested arrays of maps           |   2    |
| Cross-impl: GDScript-encoded bytes parse in Python   |   3    |
| Cross-impl: Python-encoded bytes parse in GDScript   |   3    |
| Test runner prints per-type pass/fail lines          |   1    |
| Test runner exits with explicit `OK` or `FAIL`       |   1    |
| **Total**                                            | **18** |

---

## Hints

- **`PackedByteArray.encode_double_be(offset, value)`** writes a big-endian IEEE 754 double starting at `offset`. The corresponding reader is `decode_double_be(offset)`.
- **`PackedByteArray.encode_u8`, `encode_u16_be`, `encode_u32_be`, `encode_s8`, `encode_s16_be`, `encode_s32_be`** are the integer encoders; each has a matching `decode_*`.
- **The `encode_*` methods need a *pre-sized* `PackedByteArray`.** Call `bytes.resize(needed_size)` before writing, or append byte-by-byte with `bytes.append(value)`.
- **Strings convert with `str.to_utf8_buffer()` (string → bytes) and `bytes.get_string_from_utf8()` (bytes → string).**
- **For the decoder, pass a *cursor* by reference.** GDScript's `Array` is reference-typed; a one-element array `var cursor: Array = [0]` lets the helper advance `cursor[0]` and have the caller see the new position.
- **Recursive types need recursive functions.** `_decode_value(bytes, cursor)` reads the tag byte, dispatches to `_decode_array(bytes, cursor)` or `_decode_map(bytes, cursor)` for compound types, and recurses into the elements.

---

## A reflection question for the writeup

Submit, in addition to the two code files, a `challenge-02-writeup.md` of ~400 words covering:

- The single trickiest format to implement, and why. (Most students answer: the integer encoders, because there are seven different integer formats and you have to pick the smallest one that fits.)
- A benchmark: how does your pure-GDScript decoder's parse time compare to `JSON.parse_string` on the same payload? Numbers in microseconds, averaged over at least 100 iterations.
- The recommendation you would make to a future student who has to decide between (a) shipping your pure-GDScript MessagePack and (b) shipping JSON. The right answer is "JSON, unless you have measured save throughput as a problem"; the wrong answer is "always MessagePack."

The reflection matters. The exercise teaches the *technique*; the reflection teaches the *judgement*.
