"""
Mini-project — the pytest suite.

Exercises every code path in ``save_schema.py``:

- Schema validation: well-formed saves accepted, malformed saves rejected.
- Round-trip: a state written to disk loads back equal.
- Migration: a v1 save on disk loads as v2 in memory.
- Atomic write: a successful write rotates the previous good save.
- Corruption recovery: a tampered ``latest`` falls back to ``previous``.

Run
---
    pip install pydantic pytest
    python3 -m pytest test_migration.py -v

All tests should pass on macOS, Linux, and Windows.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from save_schema import (
    CURRENT_VERSION,
    MetaSettings,
    MetaV1,
    SavePaths,
    SaveV1,
    SaveV2,
    canonical_bytes,
    integrity_tag,
    load_meta,
    load_state,
    load_with_fallback,
    migrate_to_latest,
    migrate_v1_to_v2,
    open_envelope,
    save_meta,
    save_state,
    write_atomic_with_rotation,
)


# ---------------------------------------------------------------------------
# Fixtures.
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_v2() -> SaveV2:
    """A representative v2 state used by many tests."""
    return SaveV2(
        version=2,
        player_name="Alex",
        current_score=1240,
        session_start_timestamp=1_715_000_000,
        highest_score_this_session=1240,
        current_level="forest_03",
    )


@pytest.fixture
def sample_v1_dict() -> dict[str, Any]:
    """A representative v1 save *as a dict* (the on-disk shape)."""
    return {
        "version": 1,
        "player_name": "Legacy",
        "current_score": 50,
        "session_start_timestamp": 1_700_000_000,
        "highest_score_this_session": 50,
    }


# ---------------------------------------------------------------------------
# Schema-validation tests.
# ---------------------------------------------------------------------------


class TestSchema:
    def test_v2_accepts_well_formed(self, sample_v2: SaveV2) -> None:
        # The fixture itself is the test: construction succeeded.
        assert sample_v2.version == 2
        assert sample_v2.player_name == "Alex"

    def test_v2_rejects_empty_player_name(self) -> None:
        with pytest.raises(ValidationError):
            SaveV2(
                version=2,
                player_name="",
                current_score=0,
                session_start_timestamp=0,
                highest_score_this_session=0,
                current_level="level_01",
            )

    def test_v2_rejects_negative_score(self) -> None:
        with pytest.raises(ValidationError):
            SaveV2(
                version=2,
                player_name="Alex",
                current_score=-10,
                session_start_timestamp=0,
                highest_score_this_session=0,
                current_level="level_01",
            )

    def test_v2_rejects_overflowed_score(self) -> None:
        with pytest.raises(ValidationError):
            SaveV2(
                version=2,
                player_name="Alex",
                current_score=999_999_999,
                session_start_timestamp=0,
                highest_score_this_session=0,
                current_level="level_01",
            )

    def test_v1_and_v2_versions_are_distinct(self) -> None:
        # A v2 dict cannot validate as SaveV1.
        with pytest.raises(ValidationError):
            SaveV1.model_validate(
                {
                    "version": 2,
                    "player_name": "Alex",
                    "current_score": 0,
                    "session_start_timestamp": 0,
                    "highest_score_this_session": 0,
                }
            )

    def test_meta_with_defaults(self) -> None:
        meta: MetaV1 = MetaV1(version=1, settings=MetaSettings())
        assert meta.last_used_player_name == "Player 1"
        assert meta.settings.master_volume == 1.0

    def test_meta_rejects_out_of_range_volume(self) -> None:
        with pytest.raises(ValidationError):
            MetaV1(version=1, settings=MetaSettings(master_volume=2.5))


# ---------------------------------------------------------------------------
# Migration tests.
# ---------------------------------------------------------------------------


class TestMigration:
    def test_v1_to_v2_purity(self, sample_v1_dict: dict[str, Any]) -> None:
        snapshot: dict[str, Any] = dict(sample_v1_dict)
        _ = migrate_v1_to_v2(sample_v1_dict)
        assert sample_v1_dict == snapshot, "migration mutated its input"

    def test_v1_to_v2_adds_current_level(self, sample_v1_dict: dict[str, Any]) -> None:
        v2: dict[str, Any] = migrate_v1_to_v2(sample_v1_dict)
        assert v2["version"] == 2
        assert v2["current_level"] == "level_01"

    def test_chain_handles_v1(self, sample_v1_dict: dict[str, Any]) -> None:
        upgraded: dict[str, Any] = migrate_to_latest(sample_v1_dict)
        assert upgraded["version"] == CURRENT_VERSION
        SaveV2.model_validate(upgraded)  # must validate at v2

    def test_chain_handles_v2_passthrough(self, sample_v2: SaveV2) -> None:
        upgraded: dict[str, Any] = migrate_to_latest(sample_v2.model_dump())
        assert upgraded["version"] == 2
        assert upgraded["current_level"] == sample_v2.current_level

    def test_chain_handles_unversioned(self) -> None:
        unversioned: dict[str, Any] = {
            "player_name": "Legacy",
            "current_score": 5,
            "session_start_timestamp": 0,
            "highest_score_this_session": 5,
        }
        upgraded: dict[str, Any] = migrate_to_latest(unversioned)
        assert upgraded["version"] == CURRENT_VERSION


# ---------------------------------------------------------------------------
# Integrity envelope tests.
# ---------------------------------------------------------------------------


class TestEnvelope:
    def test_canonical_bytes_is_deterministic(self) -> None:
        d1: dict[str, Any] = {"a": 1, "b": 2}
        d2: dict[str, Any] = {"b": 2, "a": 1}
        assert canonical_bytes(d1) == canonical_bytes(d2)

    def test_integrity_tag_format(self) -> None:
        tag: str = integrity_tag({"x": 1})
        assert tag.startswith("sha256:")
        assert len(tag) == len("sha256:") + 64

    def test_open_envelope_accepts_good(self) -> None:
        payload: dict[str, Any] = {"x": 1, "y": "hello"}
        parsed: dict[str, Any] = {"payload": payload, "integrity": integrity_tag(payload)}
        result: dict[str, Any] = open_envelope(parsed)
        assert result == payload

    def test_open_envelope_rejects_bad_hash(self) -> None:
        payload: dict[str, Any] = {"x": 1}
        parsed: dict[str, Any] = {"payload": payload, "integrity": "sha256:deadbeef"}
        with pytest.raises(ValueError):
            open_envelope(parsed)

    def test_open_envelope_rejects_missing_fields(self) -> None:
        with pytest.raises(ValueError):
            open_envelope({"payload": {"x": 1}})
        with pytest.raises(ValueError):
            open_envelope({"integrity": "sha256:x"})


# ---------------------------------------------------------------------------
# Atomic write and rotation tests.
# ---------------------------------------------------------------------------


class TestAtomicWrite:
    def test_round_trip(self, tmp_path: Path, sample_v2: SaveV2) -> None:
        save_state(tmp_path, slot=0, state=sample_v2)
        loaded: SaveV2 = load_state(tmp_path, slot=0)
        assert loaded == sample_v2

    def test_rotation_after_two_writes(self, tmp_path: Path, sample_v2: SaveV2) -> None:
        save_state(tmp_path, slot=0, state=sample_v2)

        updated: SaveV2 = sample_v2.model_copy(update={"current_score": sample_v2.current_score + 1})
        save_state(tmp_path, slot=0, state=updated)

        paths: SavePaths = SavePaths.for_slot(tmp_path, slot=0)
        assert paths.latest.exists()
        assert paths.previous.exists()

        # The previous file should still parse as the original state.
        parsed: dict[str, Any] = json.loads(paths.previous.read_text(encoding="utf-8"))
        previous_payload: dict[str, Any] = open_envelope(parsed)
        previous_state: SaveV2 = SaveV2.model_validate(previous_payload)
        assert previous_state.current_score == sample_v2.current_score

    def test_corruption_falls_back(self, tmp_path: Path, sample_v2: SaveV2) -> None:
        save_state(tmp_path, slot=0, state=sample_v2)
        updated: SaveV2 = sample_v2.model_copy(update={"current_score": sample_v2.current_score + 1})
        save_state(tmp_path, slot=0, state=updated)

        # Corrupt the latest file.
        paths: SavePaths = SavePaths.for_slot(tmp_path, slot=0)
        data: bytearray = bytearray(paths.latest.read_bytes())
        mid: int = len(data) // 2
        data[mid] = data[mid] ^ 0x40
        paths.latest.write_bytes(bytes(data))

        # Now load. The fallback should return the original (unupdated) state.
        recovered: SaveV2 = load_state(tmp_path, slot=0)
        assert recovered.current_score == sample_v2.current_score


# ---------------------------------------------------------------------------
# Meta bucket tests.
# ---------------------------------------------------------------------------


class TestMeta:
    def test_round_trip(self, tmp_path: Path) -> None:
        meta: MetaV1 = MetaV1(
            version=1,
            settings=MetaSettings(master_volume=0.5, music_volume=0.7),
            last_used_player_name="Alex",
        )
        save_meta(tmp_path, meta)
        loaded: MetaV1 = load_meta(tmp_path)
        assert loaded == meta


# ---------------------------------------------------------------------------
# Cross-file integration: Godot-written save round-trip simulation.
# ---------------------------------------------------------------------------


class TestGodotCompat:
    """Simulate the Godot side by hand-constructing the on-disk shape.

    The Godot ``save_manager.gd`` produces a file with exactly this structure:
    a JSON envelope ``{"payload": <state>, "integrity": "sha256:<hex>"}`` where
    ``<state>`` is the un-Pydantic-validated dict. This test confirms the
    Python loader accepts that shape.
    """

    def test_godot_shape_is_accepted(self, tmp_path: Path) -> None:
        state_dict: dict[str, Any] = {
            "version": 2,
            "player_name": "Godot",
            "current_score": 500,
            "session_start_timestamp": 1_715_500_000,
            "highest_score_this_session": 500,
            "current_level": "godot_level_2",
        }
        paths: SavePaths = SavePaths.for_slot(tmp_path, slot=2)
        write_atomic_with_rotation(paths, state_dict)

        loaded: SaveV2 = load_state(tmp_path, slot=2)
        assert loaded.player_name == "Godot"
        assert loaded.current_level == "godot_level_2"
