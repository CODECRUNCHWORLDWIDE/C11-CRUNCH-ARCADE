"""exercise-03-msgpack-vs-json-benchmark.py

Goal
----
Serialize the same ``GameState`` 10,000 times in JSON, JSON+gzip, and
MessagePack, and report bytes-on-disk plus median microseconds per
encode/decode. Run as a console script (no pygame needed). Use the
results to internalise the size/speed trade-off from Lecture 2 §6.

This exercise is INTENTIONALLY headless. The point is to look at
numbers in a terminal, not to draw pixels. It also runs without the
``msgpack`` package installed -- if msgpack is missing, the script
gracefully skips that benchmark and prints an install instruction.

Expected behaviour
------------------
- Run from a terminal::

      python exercise-03-msgpack-vs-json-benchmark.py

- The script builds a realistic ``GameState`` (20-item inventory,
  30-flag world), runs each format 10,000 times, and prints a table::

      format          bytes      encode_us   decode_us
      JSON              612        25.3        29.8
      JSON+gzip         168        69.4        51.2
      MessagePack       344         8.1         9.4

- Numbers will differ by hardware. The RATIOS are stable: MessagePack
  is ~2x smaller than JSON; gzip-compressed JSON is ~3-4x smaller than
  raw JSON; the binary formats are 2-4x faster on encode/decode.

What you learn
--------------
- The actual size/speed numbers on YOUR machine, not in the abstract.
- How to write a small, honest benchmark with ``time.perf_counter``
  and ``statistics.median``.
- Why we report the MEDIAN, not the mean. Mean is misleading on
  micro-benchmarks because of GC pauses and OS interrupts.
- Why we serialize the SAME object 10,000 times instead of 10,000
  different objects: the variable we want to measure is the
  serializer's per-call cost, not the data variation.
- The "JSON + gzip is competitive with MessagePack on size" finding
  from Lecture 2 §7, in numbers from your own laptop.

Estimated time
--------------
About 45-55 minutes.

To complete
-----------
The benchmark loop is filled in. What you'll spend time on is reading
the output, scaling the workload (try ``ITERATIONS = 1000`` and
``ITERATIONS = 100000`` and watch the medians stabilise), and
optionally adding a fourth format -- ``struct.pack`` custom binary --
following the pattern. The HINT block at the bottom has nudges.

References
----------
- RFC 8259 (JSON): https://www.rfc-editor.org/rfc/rfc8259
- MessagePack spec: https://github.com/msgpack/msgpack/blob/master/spec.md
- Python `time.perf_counter`: https://docs.python.org/3/library/time.html#time.perf_counter
- Python `statistics.median`: https://docs.python.org/3/library/statistics.html
"""

from __future__ import annotations

import gzip
import json
import statistics
import sys
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Callable

# Optional dependency. We gracefully skip MessagePack benchmarks if
# the package is not installed.
try:
    import msgpack  # type: ignore[import-not-found]

    HAS_MSGPACK: bool = True
except ImportError:
    HAS_MSGPACK = False


# ----- Configuration --------------------------------------------------------

ITERATIONS: int = 10_000
WARMUP_ITERATIONS: int = 100


# ----- The GameState we benchmark ------------------------------------------


@dataclass
class GameState:
    """A realistic, modest-size save: 20-item inventory, 30-flag world."""

    schema_version: int = 1
    slot_name: str = "slot_01"
    timestamp_iso: str = "2026-05-12T19:42:11"
    playtime_seconds: float = 1247.3

    player_x: float = 384.5
    player_y: float = 192.0
    player_hp: int = 4
    player_hp_max: int = 5

    inventory: list[dict] = field(default_factory=list)
    equipment: list[dict] = field(default_factory=list)
    coins: int = 47

    current_level: str = "level_03"
    flags: dict[str, bool] = field(default_factory=dict)


def make_realistic_state() -> GameState:
    """Build a save with realistic contents."""
    inventory_ids = [
        "potion_health", "potion_mana", "potion_speed", "key_brass",
        "key_silver", "key_gold", "coin_copper", "coin_silver",
        "coin_gold", "scroll_fire", "scroll_ice", "scroll_heal",
        "rune_strength", "rune_defence", "rune_focus",
        "letter_king", "letter_blacksmith", "map_dungeon_1",
        "map_dungeon_2", "trinket_lucky",
    ]
    equipment_ids = [
        "eq_sword_silver", "eq_shield_bronze",
        "eq_helm_leather", "eq_boots_swift",
    ]
    flag_keys = [
        "met_king", "bridge_built", "dragon_slain", "blacksmith_freed",
        "library_opened", "tomb_sealed", "lighthouse_lit", "shipwright_paid",
        "stable_repaired", "wizard_appeased", "harbour_guarded", "cellar_cleared",
        "garden_planted", "well_unblocked", "merchant_returned", "knight_armed",
        "scholar_calmed", "thief_caught", "ghost_dispelled", "well_blessed",
        "altar_lit", "watchtower_manned", "barracks_painted", "tavern_renamed",
        "fishing_pier_built", "marsh_drained", "windmill_turned", "loom_repaired",
        "kiln_rebuilt", "courtyard_swept",
    ]

    return GameState(
        inventory=[{"id": iid, "count": (i % 5) + 1}
                   for i, iid in enumerate(inventory_ids)],
        equipment=[{"id": eid, "count": 1} for eid in equipment_ids],
        flags={k: (i % 3 == 0) for i, k in enumerate(flag_keys)},
    )


# ----- The four benchmarks --------------------------------------------------


def bench_json_encode(payload: dict) -> bytes:
    return json.dumps(payload, sort_keys=True).encode("utf-8")


def bench_json_decode(buf: bytes) -> dict:
    return json.loads(buf.decode("utf-8"))


def bench_json_gzip_encode(payload: dict) -> bytes:
    return gzip.compress(json.dumps(payload, sort_keys=True).encode("utf-8"))


def bench_json_gzip_decode(buf: bytes) -> dict:
    return json.loads(gzip.decompress(buf).decode("utf-8"))


def bench_msgpack_encode(payload: dict) -> bytes:
    return msgpack.packb(payload, use_bin_type=True)


def bench_msgpack_decode(buf: bytes) -> dict:
    return msgpack.unpackb(buf, raw=False)


# ----- The benchmark driver ------------------------------------------------


def time_op_us(op: Callable[[], Any], iterations: int) -> float:
    """Run ``op`` ``iterations`` times and return the median per-call
    duration in microseconds. Warm-up runs come from the caller."""
    samples: list[float] = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        op()
        t1 = time.perf_counter()
        samples.append((t1 - t0) * 1_000_000.0)
    return statistics.median(samples)


@dataclass
class BenchResult:
    name: str
    bytes_on_disk: int
    encode_us: float
    decode_us: float


def bench_format(
    name: str,
    payload: dict,
    encode: Callable[[dict], bytes],
    decode: Callable[[bytes], dict],
    iterations: int = ITERATIONS,
) -> BenchResult:
    """Run encode/decode benchmarks for one format."""
    # Warm-up: prime caches and let any JIT/import work settle.
    for _ in range(WARMUP_ITERATIONS):
        buf = encode(payload)
        decode(buf)

    # Measure encode.
    buf = encode(payload)
    encode_us = time_op_us(lambda: encode(payload), iterations)

    # Measure decode.
    decode_us = time_op_us(lambda: decode(buf), iterations)

    return BenchResult(
        name=name,
        bytes_on_disk=len(buf),
        encode_us=encode_us,
        decode_us=decode_us,
    )


def print_table(results: list[BenchResult]) -> None:
    """Print a fixed-width table of results."""
    header = f"{'format':<14}  {'bytes':>8}  {'encode_us':>10}  {'decode_us':>10}"
    print(header)
    print("-" * len(header))
    for r in results:
        print(
            f"{r.name:<14}  "
            f"{r.bytes_on_disk:>8}  "
            f"{r.encode_us:>10.2f}  "
            f"{r.decode_us:>10.2f}"
        )


# ----- main ----------------------------------------------------------------


def main() -> int:
    print("=" * 64)
    print("C11 Week 7 - Exercise 3 - Serialization benchmark")
    print("=" * 64)
    print(f"iterations per measurement: {ITERATIONS:,}")
    print(f"warm-up iterations:         {WARMUP_ITERATIONS}")
    print()

    state = make_realistic_state()
    payload = asdict(state)

    results: list[BenchResult] = []

    # JSON
    results.append(bench_format(
        "JSON", payload, bench_json_encode, bench_json_decode,
    ))

    # JSON + gzip
    results.append(bench_format(
        "JSON+gzip", payload, bench_json_gzip_encode, bench_json_gzip_decode,
    ))

    # MessagePack (optional)
    if HAS_MSGPACK:
        results.append(bench_format(
            "MessagePack", payload, bench_msgpack_encode, bench_msgpack_decode,
        ))
    else:
        print("(MessagePack skipped: `pip install msgpack` to enable.)")
        print()

    print_table(results)
    print()

    # Headline ratios (computed from results).
    json_row = next((r for r in results if r.name == "JSON"), None)
    if json_row is not None:
        print("Ratios vs JSON (smaller / faster is better):")
        for r in results:
            size_ratio = r.bytes_on_disk / json_row.bytes_on_disk
            enc_ratio = r.encode_us / json_row.encode_us
            dec_ratio = r.decode_us / json_row.decode_us
            print(
                f"  {r.name:<14}  "
                f"size = {size_ratio:>5.2f}x  "
                f"encode = {enc_ratio:>5.2f}x  "
                f"decode = {dec_ratio:>5.2f}x"
            )
        print()

    # Decision rule reminder (from Lecture 2 §10).
    print("Decision rule (Lecture 2 §10):")
    print("  1) Game save < 50 KB:  JSON. Always.")
    print("  2) Game save > 50 KB:  JSON + gzip. Stdlib only.")
    print("  3) Hot path + one pip install:  MessagePack.")
    print()
    print("End of benchmark.")
    return 0


# ----- HINT (do not peek for 20 minutes) -----------------------------------
# If your medians wobble more than ~10% run-to-run, try:
#   - ITERATIONS = 100_000 (the median stabilises with more samples).
#   - Closing other apps (Spotify, Chrome) -- the OS scheduler steals
#     time slices that show up as wider tails.
#   - Running ``python -X dev exercise-03-msgpack-vs-json-benchmark.py``
#     to disable some debug overhead. (Then re-enable; this is a learning
#     exercise, not a production benchmark.)
#
# If you want a fourth row, add ``struct.pack`` custom-binary. The
# challenge is encoding the inventory and flags, which have variable
# length. Hint: length-prefix every list, then write each item's
# fields in order. The format string for one item is ``<H10sI``
# (uint16 id-length, 10-byte id, uint32 count). Lecture 2 §4 covers
# why this is brittle -- you will find out firsthand.
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    sys.exit(main())
