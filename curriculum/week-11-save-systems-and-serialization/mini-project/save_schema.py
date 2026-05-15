"""
Mini-project — the Python schema and migration module.

This module is the canonical reference for the save format. The Godot
``save_manager.gd`` and the Python ``test_migration.py`` both treat this file
as the authoritative description of what a v1 save looks like, what a v2 save
looks like, and how to bridge them.

If a Godot-written save round-trips through this module's loader without
raising, the formats are in sync. The ``test_migration.py`` suite asserts
exactly this property.

Dependencies
------------
- pydantic (v2.x)
- standard library only otherwise

Run
---
This module is importable but not directly executable. The ``_demo`` block at
the bottom is a smoke test that round-trips a sample state through both
schemas; you can run it with ``python3 save_schema.py``.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Literal

from pydantic import BaseModel, Field, ValidationError


# ---------------------------------------------------------------------------
# Constants.
# ---------------------------------------------------------------------------


CURRENT_VERSION: int = 2
SLOT_COUNT: int = 3


# ---------------------------------------------------------------------------
# Schemas.
# ---------------------------------------------------------------------------


class SaveV1(BaseModel):
    """The original schema. Three progression fields plus the version tag."""

    version: Literal[1]
    player_name: str = Field(min_length=1, max_length=64)
    current_score: int = Field(ge=0, le=10_000_000)
    session_start_timestamp: int = Field(ge=0)
    highest_score_this_session: int = Field(ge=0, le=10_000_000)


class SaveV2(BaseModel):
    """The current schema. v2 adds ``current_level``."""

    version: Literal[2]
    player_name: str = Field(min_length=1, max_length=64)
    current_score: int = Field(ge=0, le=10_000_000)
    session_start_timestamp: int = Field(ge=0)
    highest_score_this_session: int = Field(ge=0, le=10_000_000)
    current_level: str = Field(min_length=1, max_length=128)


SaveLatest = SaveV2


class MetaV1(BaseModel):
    """The meta bucket. Lives in its own file, written on settings changes."""

    version: Literal[1]
    settings: "MetaSettings"
    last_used_player_name: str = Field(default="Player 1", min_length=1, max_length=64)


class MetaSettings(BaseModel):
    """The user-tweakable settings inside the meta bucket."""

    master_volume: float = Field(default=1.0, ge=0.0, le=1.0)
    music_volume: float = Field(default=1.0, ge=0.0, le=1.0)
    sfx_volume: float = Field(default=1.0, ge=0.0, le=1.0)
    fullscreen: bool = False


# Pydantic v2 needs the forward reference resolved.
MetaV1.model_rebuild()


# ---------------------------------------------------------------------------
# Migrations.
# ---------------------------------------------------------------------------


def migrate_v1_to_v2(v1_dict: dict[str, Any]) -> dict[str, Any]:
    """Promote a v1 save dictionary to a v2 dictionary.

    The function is pure; it does not mutate its argument. The new field
    ``current_level`` gets the safe default ``"level_01"``.
    """
    assert v1_dict.get("version") == 1, "migrate_v1_to_v2: input is not v1"
    v2_dict: dict[str, Any] = copy.deepcopy(v1_dict)
    v2_dict["version"] = 2
    v2_dict["current_level"] = "level_01"
    return v2_dict


MIGRATIONS: dict[int, Callable[[dict[str, Any]], dict[str, Any]]] = {
    1: migrate_v1_to_v2,
}


def migrate_to_latest(parsed: dict[str, Any]) -> dict[str, Any]:
    """Run the single-step migration chain until ``parsed`` matches ``CURRENT_VERSION``."""
    if "version" not in parsed:
        parsed = dict(parsed)
        parsed["version"] = 1
    current: dict[str, Any] = parsed
    safety: int = 0
    while int(current.get("version", 0)) < CURRENT_VERSION:
        from_version: int = int(current["version"])
        step: Callable[[dict[str, Any]], dict[str, Any]] | None = MIGRATIONS.get(from_version)
        if step is None:
            raise ValueError(f"no migration step registered from version {from_version}")
        current = step(current)
        safety += 1
        if safety > 100:
            raise RuntimeError("migration chain exceeded 100 steps; likely an infinite loop")
    return current


# ---------------------------------------------------------------------------
# Envelope (integrity check, atomic write).
# ---------------------------------------------------------------------------


def canonical_bytes(payload: dict[str, Any]) -> bytes:
    """Deterministic UTF-8 byte rendering of ``payload`` for hashing."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def integrity_tag(payload: dict[str, Any]) -> str:
    """Return ``"sha256:" + hex(sha256(canonical_bytes(payload)))``."""
    return "sha256:" + hashlib.sha256(canonical_bytes(payload)).hexdigest()


def envelope(payload: dict[str, Any]) -> dict[str, Any]:
    """Wrap ``payload`` in the on-disk envelope carrying its integrity tag."""
    return {"payload": payload, "integrity": integrity_tag(payload)}


def open_envelope(parsed: dict[str, Any]) -> dict[str, Any]:
    """Verify the integrity tag and return the inner payload.

    Raises :class:`ValueError` on mismatch or malformed envelope.
    """
    if "payload" not in parsed or "integrity" not in parsed:
        raise ValueError("envelope: missing 'payload' or 'integrity' field")
    payload: dict[str, Any] = parsed["payload"]
    stored: str = parsed["integrity"]
    expected: str = integrity_tag(payload)
    if stored != expected:
        raise ValueError("envelope: integrity mismatch")
    return payload


# ---------------------------------------------------------------------------
# Path helpers.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SavePaths:
    """The three filenames per slot used by the rotation scheme."""

    latest: Path
    previous: Path
    temp: Path

    @classmethod
    def for_slot(cls, directory: Path, slot: int) -> "SavePaths":
        base: Path = directory / f"slot_{slot:02d}.save"
        return cls(
            latest=base,
            previous=base.with_suffix(base.suffix + ".prev"),
            temp=base.with_suffix(base.suffix + ".tmp"),
        )


def meta_path(directory: Path) -> Path:
    return directory / "meta.json"


# ---------------------------------------------------------------------------
# Atomic write and read.
# ---------------------------------------------------------------------------


def write_atomic_with_rotation(paths: SavePaths, payload: dict[str, Any]) -> None:
    """Atomically publish ``payload`` to ``paths.latest``, rotating any previous file."""
    blob: bytes = json.dumps(envelope(payload), sort_keys=True, indent=2).encode("utf-8")
    paths.latest.parent.mkdir(parents=True, exist_ok=True)
    with open(paths.temp, "wb") as f:
        f.write(blob)
        f.flush()
        os.fsync(f.fileno())
    if paths.latest.exists():
        os.replace(paths.latest, paths.previous)
    os.replace(paths.temp, paths.latest)


def load_with_fallback(paths: SavePaths) -> dict[str, Any]:
    """Load from ``paths.latest``; fall back to ``paths.previous`` on failure."""
    last_exc: Exception | None = None
    for candidate in (paths.latest, paths.previous):
        if not candidate.exists():
            continue
        try:
            parsed: dict[str, Any] = json.loads(candidate.read_text(encoding="utf-8"))
            return open_envelope(parsed)
        except (json.JSONDecodeError, ValueError) as exc:
            last_exc = exc
            continue
    if last_exc is not None:
        raise last_exc
    raise FileNotFoundError("no readable save in either latest or previous")


# ---------------------------------------------------------------------------
# Public load / save functions.
# ---------------------------------------------------------------------------


def save_state(directory: Path, slot: int, state: SaveLatest) -> None:
    """Write ``state`` to slot ``slot`` under ``directory`` atomically."""
    paths: SavePaths = SavePaths.for_slot(directory, slot)
    write_atomic_with_rotation(paths, state.model_dump())


def load_state(directory: Path, slot: int) -> SaveLatest:
    """Load slot ``slot`` from ``directory``, migrate, validate."""
    paths: SavePaths = SavePaths.for_slot(directory, slot)
    payload: dict[str, Any] = load_with_fallback(paths)
    migrated: dict[str, Any] = migrate_to_latest(payload)
    return SaveLatest.model_validate(migrated)


def save_meta(directory: Path, meta: MetaV1) -> None:
    """Write the meta bucket to ``directory/meta.json``."""
    path: Path = meta_path(directory)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp: Path = path.with_suffix(path.suffix + ".tmp")
    blob: bytes = json.dumps(envelope(meta.model_dump()), sort_keys=True, indent=2).encode("utf-8")
    with open(tmp, "wb") as f:
        f.write(blob)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def load_meta(directory: Path) -> MetaV1:
    """Load and validate the meta bucket."""
    path: Path = meta_path(directory)
    parsed: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    payload: dict[str, Any] = open_envelope(parsed)
    return MetaV1.model_validate(payload)


# ---------------------------------------------------------------------------
# Demo.
# ---------------------------------------------------------------------------


def _demo() -> None:
    """Round-trip a sample state to confirm the module is internally consistent."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir_name:
        tmpdir: Path = Path(tmpdir_name)

        original: SaveLatest = SaveV2(
            version=2,
            player_name="Alex",
            current_score=1240,
            session_start_timestamp=1_715_000_000,
            highest_score_this_session=1240,
            current_level="forest_03",
        )
        save_state(tmpdir, slot=0, state=original)
        loaded: SaveLatest = load_state(tmpdir, slot=0)
        assert loaded == original, "round-trip mutated state"

        meta_original: MetaV1 = MetaV1(
            version=1,
            settings=MetaSettings(master_volume=0.8, music_volume=0.6),
            last_used_player_name="Alex",
        )
        save_meta(tmpdir, meta_original)
        meta_loaded: MetaV1 = load_meta(tmpdir)
        assert meta_loaded == meta_original, "meta round-trip mutated state"

        # Migration demo: write a v1 file, load it as v2.
        v1_dict: dict[str, Any] = {
            "version": 1,
            "player_name": "Legacy",
            "current_score": 50,
            "session_start_timestamp": 1_700_000_000,
            "highest_score_this_session": 50,
        }
        v1_paths: SavePaths = SavePaths.for_slot(tmpdir, slot=1)
        write_atomic_with_rotation(v1_paths, v1_dict)
        migrated: SaveLatest = load_state(tmpdir, slot=1)
        assert migrated.version == 2
        assert migrated.current_level == "level_01"

    print("OK")


if __name__ == "__main__":
    _demo()
