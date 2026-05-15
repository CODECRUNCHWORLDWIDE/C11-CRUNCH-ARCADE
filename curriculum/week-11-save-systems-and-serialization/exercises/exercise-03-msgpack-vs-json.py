"""
Exercise 03 — MessagePack vs JSON: size and parse-speed comparison.

Goal
----
Take a realistic save dictionary, serialise it both as JSON and as MessagePack,
measure each format's on-the-wire size and each format's parse time, and print
a small report. The numbers vary by machine but the ratio is stable: MessagePack
is 2x to 3x smaller and 2x to 4x faster to parse on typical save shapes.

Lecture 2 sketched the comparison; this exercise produces the numbers on the
student's own machine. The takeaway is twofold: (a) JSON is the right answer
for dev builds where the size cost is invisible; (b) MessagePack is the right
answer for shipped builds where it is not.

Run
---
    pip install msgpack
    python3 exercise-03-msgpack-vs-json.py

The script prints the bytes, the parse time, and a ratio. Prints ``OK`` on
success.
"""

from __future__ import annotations

import json
import time
from typing import Any

import msgpack


# ---------------------------------------------------------------------------
# A realistic test payload.
# ---------------------------------------------------------------------------


def build_payload() -> dict[str, Any]:
    """Construct a save shape representative of a typical mid-game state.

    The payload has 100 inventory entries (each an item ID and a count), 50
    quest flags, and a small player block. The shape exercises every JSON-ish
    type: strings, integers, floats, nested objects, arrays of objects, and
    booleans.
    """
    inventory: list[dict[str, Any]] = [
        {"item_id": f"item_{i:03d}", "count": (i * 7) % 99, "is_quest_item": (i % 11 == 0)}
        for i in range(100)
    ]
    quest_flags: dict[str, bool] = {
        f"quest_flag_{i:02d}": (i % 3 == 0) for i in range(50)
    }
    player: dict[str, Any] = {
        "name": "Alex of the Eternal Save File",
        "level": 47,
        "experience": 123_456,
        "hp": 380,
        "hp_max": 420,
        "position": {"x": 1024.5, "y": 768.25, "z": 0.0},
        "active_buffs": ["sturdy", "lucky", "wellfed"],
    }
    return {
        "version": 2,
        "player": player,
        "inventory": inventory,
        "quest_flags": quest_flags,
        "session_start_timestamp": 1_715_000_000,
        "current_level": "town_square",
    }


# ---------------------------------------------------------------------------
# Measurement.
# ---------------------------------------------------------------------------


def measure_json(payload: dict[str, Any], iterations: int) -> tuple[bytes, float]:
    """Serialise once, then time ``iterations`` parses of the resulting bytes.

    Returns the encoded bytes and the average per-parse time in seconds.
    """
    encoded: bytes = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    start: float = time.perf_counter()
    for _ in range(iterations):
        json.loads(encoded)
    elapsed: float = time.perf_counter() - start
    return encoded, elapsed / iterations


def measure_msgpack(payload: dict[str, Any], iterations: int) -> tuple[bytes, float]:
    """The MessagePack counterpart of :func:`measure_json`."""
    encoded: bytes = msgpack.packb(payload, use_bin_type=True)
    start: float = time.perf_counter()
    for _ in range(iterations):
        msgpack.unpackb(encoded, raw=False)
    elapsed: float = time.perf_counter() - start
    return encoded, elapsed / iterations


def round_trip_check_json(payload: dict[str, Any]) -> None:
    """Confirm JSON round-trips loss-lessly for our payload."""
    blob: bytes = json.dumps(payload).encode("utf-8")
    back: Any = json.loads(blob)
    assert back == payload, "JSON round-trip mutated payload"


def round_trip_check_msgpack(payload: dict[str, Any]) -> None:
    """Confirm MessagePack round-trips loss-lessly for our payload."""
    blob: bytes = msgpack.packb(payload, use_bin_type=True)
    back: Any = msgpack.unpackb(blob, raw=False)
    assert back == payload, "MessagePack round-trip mutated payload"


# ---------------------------------------------------------------------------
# Demonstration.
# ---------------------------------------------------------------------------


def _demo() -> None:
    payload: dict[str, Any] = build_payload()

    round_trip_check_json(payload)
    round_trip_check_msgpack(payload)

    iterations: int = 200
    json_blob, json_time = measure_json(payload, iterations)
    msgpack_blob, msgpack_time = measure_msgpack(payload, iterations)

    size_ratio: float = len(json_blob) / max(len(msgpack_blob), 1)
    speed_ratio: float = json_time / max(msgpack_time, 1e-12)

    print("payload shape:")
    print(f"  inventory entries: {len(payload['inventory'])}")
    print(f"  quest flags:       {len(payload['quest_flags'])}")
    print()
    print(f"JSON size:        {len(json_blob):>6} bytes")
    print(f"MessagePack size: {len(msgpack_blob):>6} bytes")
    print(f"size ratio:       {size_ratio:.2f}x (JSON is this much larger)")
    print()
    print(f"JSON parse:       {json_time * 1e6:>7.1f} us avg ({iterations} iters)")
    print(f"MessagePack parse:{msgpack_time * 1e6:>7.1f} us avg ({iterations} iters)")
    print(f"speed ratio:      {speed_ratio:.2f}x (JSON is this much slower)")
    print()
    print("recommendation:")
    print("  - dev build, modding-friendly:    use JSON.")
    print("  - shipped build, size-sensitive:  use MessagePack.")

    assert len(msgpack_blob) < len(json_blob), "MessagePack should be smaller"
    print("OK")


if __name__ == "__main__":
    _demo()
