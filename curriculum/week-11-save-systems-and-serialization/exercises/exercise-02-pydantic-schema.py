"""
Exercise 02 — Pydantic v2 schema validation on load.

Goal
----
Replace Exercise 01's bare dataclass with a Pydantic v2 ``BaseModel``. The model
enforces field types, value ranges, and required-ness on parsed input. A
corrupted save is rejected with a structured ``ValidationError`` instead of
silently producing a half-populated dataclass.

This exercise demonstrates the *schema validation on load* discipline from
Lecture 2 section 3. The save on disk is untrusted input; the loader's first
job is to refuse anything that does not match the schema.

Run
---
    pip install pydantic
    python3 exercise-02-pydantic-schema.py

The script demonstrates a clean round-trip, then attempts three corrupted
loads and proves each is rejected. Prints ``OK`` on success.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, ValidationError


# ---------------------------------------------------------------------------
# Schema.
# ---------------------------------------------------------------------------


class PlayerStateV1(BaseModel):
    """The Pydantic-validated equivalent of Exercise 01's :class:`PlayerState`.

    Field constraints carry the *semantic* meaning that the dataclass version
    lacked. ``current_score`` is bounded at ten million because (a) the game
    logic cannot legitimately produce more and (b) a tampered save with
    ``current_score = 2**63 - 1`` would overflow downstream arithmetic.
    """

    player_name: str = Field(min_length=1, max_length=64)
    current_score: int = Field(ge=0, le=10_000_000)
    session_start_timestamp: int = Field(ge=0)
    highest_score_this_session: int = Field(ge=0, le=10_000_000)
    inventory: list[str] = Field(default_factory=list, max_length=128)


# ---------------------------------------------------------------------------
# Loader and saver.
# ---------------------------------------------------------------------------


def save_state(path: Path, state: PlayerStateV1) -> None:
    """Write ``state`` to ``path`` as canonical JSON.

    Pydantic v2's ``model_dump_json`` produces the same shape as the equivalent
    ``model_dump`` -> ``json.dumps`` pipeline. We pass ``indent=2`` for
    debuggability; in a shipped build the indent goes away.
    """
    blob: str = state.model_dump_json(indent=2)
    path.write_text(blob, encoding="utf-8")


def load_state(path: Path) -> PlayerStateV1:
    """Load and validate ``path`` as a :class:`PlayerStateV1`.

    Raises :class:`ValidationError` if any field fails its constraint. The
    caller is expected to handle that error by falling back to a backup save.
    """
    blob: str = path.read_text(encoding="utf-8")
    return PlayerStateV1.model_validate_json(blob)


def load_dict(d: dict[str, Any]) -> PlayerStateV1:
    """Load ``d`` (an already-parsed dictionary) as a :class:`PlayerStateV1`."""
    return PlayerStateV1.model_validate(d)


# ---------------------------------------------------------------------------
# Demonstration.
# ---------------------------------------------------------------------------


def _attempt_load_and_report(name: str, data: dict[str, Any]) -> bool:
    """Try to validate ``data``; print the outcome; return whether it loaded."""
    try:
        loaded: PlayerStateV1 = load_dict(data)
    except ValidationError as exc:
        first_error: dict[str, Any] = exc.errors()[0]
        loc: str = ".".join(str(p) for p in first_error["loc"])
        print(f"  {name}: REJECTED ({loc}: {first_error['msg']})")
        return False
    print(f"  {name}: ACCEPTED ({loaded.player_name}, score={loaded.current_score})")
    return True


def _demo() -> None:
    """Round-trip a valid state through disk, then exercise three corruptions."""

    valid: PlayerStateV1 = PlayerStateV1(
        player_name="Alex",
        current_score=1240,
        session_start_timestamp=1_715_000_000,
        highest_score_this_session=1240,
        inventory=["red_potion", "iron_key"],
    )

    here: Path = Path(__file__).resolve().parent
    save_path: Path = here / "_exercise02_save.json"

    try:
        save_state(save_path, valid)
        loaded: PlayerStateV1 = load_state(save_path)
        assert loaded == valid, "round-trip mutated the state"
        print("clean round-trip: OK")
    finally:
        if save_path.exists():
            save_path.unlink()

    print("attempting four loads (one valid, three corrupt):")

    accepted_a: bool = _attempt_load_and_report(
        "A valid",
        {
            "player_name": "Alex",
            "current_score": 1240,
            "session_start_timestamp": 1_715_000_000,
            "highest_score_this_session": 1240,
            "inventory": [],
        },
    )
    rejected_b: bool = not _attempt_load_and_report(
        "B negative score",
        {
            "player_name": "Alex",
            "current_score": -50,
            "session_start_timestamp": 1_715_000_000,
            "highest_score_this_session": 1240,
            "inventory": [],
        },
    )
    rejected_c: bool = not _attempt_load_and_report(
        "C overflowed score",
        {
            "player_name": "Alex",
            "current_score": 999_999_999,
            "session_start_timestamp": 1_715_000_000,
            "highest_score_this_session": 1240,
            "inventory": [],
        },
    )
    rejected_d: bool = not _attempt_load_and_report(
        "D missing player_name",
        {
            "current_score": 100,
            "session_start_timestamp": 1_715_000_000,
            "highest_score_this_session": 100,
            "inventory": [],
        },
    )

    assert accepted_a, "A should have been accepted"
    assert rejected_b, "B (negative score) should have been rejected"
    assert rejected_c, "C (overflowed score) should have been rejected"
    assert rejected_d, "D (missing field) should have been rejected"

    print("OK")


if __name__ == "__main__":
    _demo()
