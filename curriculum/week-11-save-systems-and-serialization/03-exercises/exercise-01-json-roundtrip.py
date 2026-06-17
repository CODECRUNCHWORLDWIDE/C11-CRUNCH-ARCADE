"""
Exercise 01 — JSON round-trip of a small game state.

Goal
----
Build the smallest interesting save: a dataclass for the cursor-demo player state,
serialise it to JSON with ``json.dumps``, deserialise it back with ``json.loads``,
and prove the round-trip is loss-less for the data we care about.

This exercise establishes the baseline. Exercise 02 replaces the dataclass with a
Pydantic model that validates the parsed dictionary; Exercise 03 swaps JSON for
MessagePack and compares sizes; Exercise 04 adds versioning and a migration step;
Exercise 05 adds atomic writes and SHA-256 integrity; Exercise 06 ports the
substrate to GDScript inside Godot.

Run
---
    python3 exercise-01-json-roundtrip.py

The script prints what it wrote and what it read, asserts they match, and prints
``OK`` on success.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Domain types: the smallest interesting cursor-demo state.
# ---------------------------------------------------------------------------


@dataclass
class PlayerState:
    """The persisted state of a single cursor-demo session.

    The fields are deliberately small. Anything that can be derived from these
    at load time (cached colour, computed multipliers, the live network handle)
    is not in the dataclass and not in the save.
    """

    player_name: str = "Player 1"
    current_score: int = 0
    session_start_timestamp: int = 0
    highest_score_this_session: int = 0
    inventory: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Serialisation primitives.
# ---------------------------------------------------------------------------


def state_to_json(state: PlayerState) -> str:
    """Serialise ``state`` to a stable JSON string.

    ``sort_keys=True`` makes the output deterministic so the same logical state
    always produces the same bytes. Determinism matters in Exercise 05, where we
    hash the serialised bytes for integrity checking.
    """
    as_dict: dict[str, Any] = asdict(state)
    return json.dumps(as_dict, sort_keys=True, indent=2)


def json_to_state(blob: str) -> PlayerState:
    """Parse ``blob`` and reconstruct a :class:`PlayerState`.

    This loader is *not* schema-validated. A malformed input raises
    ``json.JSONDecodeError`` (from the parser) or ``TypeError`` (from the
    dataclass constructor seeing unexpected keyword arguments). Exercise 02
    upgrades the loader to Pydantic and gets explicit validation.
    """
    parsed: dict[str, Any] = json.loads(blob)
    return PlayerState(**parsed)


# ---------------------------------------------------------------------------
# Round-trip and disk I/O helpers.
# ---------------------------------------------------------------------------


def round_trip(state: PlayerState) -> PlayerState:
    """Serialise ``state`` to a string and parse it back, returning the result.

    A round-trip is the simplest property test of a serialisation scheme: if
    ``round_trip(s) != s``, the format is lossy. JSON is loss-less for our
    fields by design (every type maps directly to a JSON type).
    """
    blob: str = state_to_json(state)
    return json_to_state(blob)


def write_save(path: Path, state: PlayerState) -> None:
    """Write ``state`` to ``path`` as pretty-printed JSON.

    This loader writes directly to the production path, which Lecture 3 warned
    against. Exercise 05 fixes it with the temp-file-plus-rename pattern.
    """
    blob: str = state_to_json(state)
    path.write_text(blob, encoding="utf-8")


def read_save(path: Path) -> PlayerState:
    """Read a save from ``path`` and return the reconstructed state."""
    blob: str = path.read_text(encoding="utf-8")
    return json_to_state(blob)


# ---------------------------------------------------------------------------
# Demonstration / smoke test.
# ---------------------------------------------------------------------------


def _demo() -> None:
    """Build a sample state, round-trip it in memory, then round-trip via disk."""

    original: PlayerState = PlayerState(
        player_name="Alex",
        current_score=1240,
        session_start_timestamp=1_715_000_000,
        highest_score_this_session=1240,
        inventory=["red_potion", "iron_key", "lockpick"],
    )

    # In-memory round-trip.
    after_string: PlayerState = round_trip(original)
    assert after_string == original, "in-memory round-trip mutated the state"

    # Disk round-trip. We write to a sibling file of this script.
    here: Path = Path(__file__).resolve().parent
    save_path: Path = here / "_exercise01_save.json"
    try:
        write_save(save_path, original)
        loaded: PlayerState = read_save(save_path)
        assert loaded == original, "disk round-trip mutated the state"
        print("wrote:", state_to_json(original))
        print("read: ", state_to_json(loaded))
    finally:
        if save_path.exists():
            save_path.unlink()

    print("OK")


if __name__ == "__main__":
    _demo()
