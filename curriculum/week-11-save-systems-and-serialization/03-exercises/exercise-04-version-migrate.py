"""
Exercise 04 — Schema versioning and the v1 -> v2 migration.

Goal
----
Define a v1 schema with two fields, a v2 schema that adds a third field, and a
``migrate_v1_to_v2`` function that bridges the two. Prove a v1 save loads
cleanly into the v2 codebase via the migration; prove a v2 save loads directly
without going through migration; prove the migration is a pure function (no
hidden mutation of inputs).

This exercise implements the *single-step migrations chained in a dispatch
table* pattern from Lecture 2 section 4. Exercise 06's GDScript port reuses
the same pattern in the Godot codebase.

Run
---
    pip install pydantic
    python3 exercise-04-version-migrate.py

Prints the round-trip results and ``OK`` on success.
"""

from __future__ import annotations

import json
import copy
from pathlib import Path
from typing import Any, Callable, Literal

from pydantic import BaseModel, Field, ValidationError


# ---------------------------------------------------------------------------
# Schema v1: the first shipped version.
# ---------------------------------------------------------------------------


class SaveV1(BaseModel):
    """The original schema. Two fields plus a version tag.

    The :class:`Literal` on ``version`` is what gives the loader the
    rejects-mismatched-versions property. A v2 save's ``version: 2`` cannot
    parse as ``SaveV1`` because ``Literal[1]`` only accepts ``1``.
    """

    version: Literal[1]
    player_name: str = Field(min_length=1, max_length=64)
    current_score: int = Field(ge=0, le=10_000_000)


# ---------------------------------------------------------------------------
# Schema v2: adds ``current_level``.
# ---------------------------------------------------------------------------


class SaveV2(BaseModel):
    """The current schema. v2 differs from v1 by one new field.

    ``current_level`` is required at the v2 layer; the migration from v1 has
    to provide a default for the field. The default we chose is
    ``"level_01"`` — the start of the game, the safe under-set.
    """

    version: Literal[2]
    player_name: str = Field(min_length=1, max_length=64)
    current_score: int = Field(ge=0, le=10_000_000)
    current_level: str = Field(min_length=1, max_length=128)


SaveLatest = SaveV2
CURRENT_VERSION: int = 2


# ---------------------------------------------------------------------------
# Migrations.
# ---------------------------------------------------------------------------


def migrate_v1_to_v2(v1_dict: dict[str, Any]) -> dict[str, Any]:
    """Promote a v1 dictionary to v2 shape.

    The function is *pure*: it does not mutate ``v1_dict``. The caller may
    rely on having an untouched v1 around for debugging or rollback.
    """
    assert v1_dict.get("version") == 1, "migrate_v1_to_v2: input is not v1"
    v2_dict: dict[str, Any] = copy.deepcopy(v1_dict)
    v2_dict["version"] = 2
    v2_dict["current_level"] = "level_01"  # safe default; v1 had no level info
    return v2_dict


# The dispatch table. Each entry is a single-step migration from version N to
# N+1. To migrate v1 to v3, the loader runs MIGRATIONS[1] then MIGRATIONS[2].
MIGRATIONS: dict[int, Callable[[dict[str, Any]], dict[str, Any]]] = {
    1: migrate_v1_to_v2,
}


# ---------------------------------------------------------------------------
# Loader.
# ---------------------------------------------------------------------------


def migrate_to_latest(parsed: dict[str, Any]) -> dict[str, Any]:
    """Run every migration step needed to bring ``parsed`` up to ``CURRENT_VERSION``.

    Single-step chain: never write a multi-step migration. If a future v3
    schema is added, append a ``migrate_v2_to_v3`` to ``MIGRATIONS`` and this
    function keeps working.
    """
    current: dict[str, Any] = parsed
    safety_counter: int = 0
    while current.get("version", 0) < CURRENT_VERSION:
        step_from: int = int(current["version"])
        step: Callable[[dict[str, Any]], dict[str, Any]] | None = MIGRATIONS.get(step_from)
        if step is None:
            raise ValueError(f"no migration registered from version {step_from}")
        current = step(current)
        safety_counter += 1
        if safety_counter > 100:
            raise RuntimeError("migration chain exceeded 100 steps; likely an infinite loop")
    return current


def load_save(path: Path) -> SaveLatest:
    """Load a save from disk, migrate as needed, validate against the current schema."""
    parsed: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    if "version" not in parsed:
        parsed["version"] = 1  # convention: unversioned legacy saves are v1
    upgraded: dict[str, Any] = migrate_to_latest(parsed)
    return SaveLatest.model_validate(upgraded)


def save_save(path: Path, state: SaveLatest) -> None:
    """Write a latest-schema save to disk."""
    path.write_text(state.model_dump_json(indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Demonstration.
# ---------------------------------------------------------------------------


def _demo() -> None:
    here: Path = Path(__file__).resolve().parent
    v1_path: Path = here / "_exercise04_v1_save.json"
    v2_path: Path = here / "_exercise04_v2_save.json"

    # Build a v1-shaped save on disk (as if it had been written by an older
    # version of the game).
    v1_dict: dict[str, Any] = {
        "version": 1,
        "player_name": "Alex",
        "current_score": 1240,
    }
    v1_path.write_text(json.dumps(v1_dict, indent=2), encoding="utf-8")

    # Build a native v2 save and write that too.
    v2_state: SaveLatest = SaveV2(
        version=2,
        player_name="Alex",
        current_score=1240,
        current_level="forest_03",
    )
    save_save(v2_path, v2_state)

    try:
        # Loading the v1 file through the migration pipeline should yield a v2 state.
        migrated: SaveLatest = load_save(v1_path)
        print("v1 -> v2 migration result:")
        print(f"  version:       {migrated.version}")
        print(f"  player_name:   {migrated.player_name}")
        print(f"  current_score: {migrated.current_score}")
        print(f"  current_level: {migrated.current_level} (default for v1 saves)")
        assert migrated.version == 2
        assert migrated.player_name == "Alex"
        assert migrated.current_score == 1240
        assert migrated.current_level == "level_01"

        # Loading the v2 file directly should *not* invoke the migration.
        direct: SaveLatest = load_save(v2_path)
        print()
        print("v2 direct-load result:")
        print(f"  version:       {direct.version}")
        print(f"  current_level: {direct.current_level} (taken from disk, not the v1 default)")
        assert direct.current_level == "forest_03"

        # Purity check: the migrator does not mutate its input.
        original_v1: dict[str, Any] = {"version": 1, "player_name": "B", "current_score": 0}
        snapshot: dict[str, Any] = copy.deepcopy(original_v1)
        _ = migrate_v1_to_v2(original_v1)
        assert original_v1 == snapshot, "migration mutated its input dictionary"

        # An attempt to load a malformed v2 save raises ValidationError, not a
        # mid-function crash; this is the property Lecture 2 promised.
        bad_v2: dict[str, Any] = {
            "version": 2,
            "player_name": "",
            "current_score": -1,
            "current_level": "x",
        }
        bad_path: Path = here / "_exercise04_bad_save.json"
        bad_path.write_text(json.dumps(bad_v2), encoding="utf-8")
        try:
            try:
                load_save(bad_path)
            except ValidationError as exc:
                first: dict[str, Any] = exc.errors()[0]
                print()
                print(f"corrupt v2 save rejected at field '{'.'.join(str(p) for p in first['loc'])}'")
        finally:
            if bad_path.exists():
                bad_path.unlink()

        print()
        print("OK")
    finally:
        for p in (v1_path, v2_path):
            if p.exists():
                p.unlink()


if __name__ == "__main__":
    _demo()
