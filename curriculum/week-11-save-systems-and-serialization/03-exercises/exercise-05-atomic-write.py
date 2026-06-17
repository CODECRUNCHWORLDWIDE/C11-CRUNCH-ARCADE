"""
Exercise 05 — Atomic write, SHA-256 integrity, backup rotation, simulated crash.

Goal
----
Implement the three crash-survival primitives from Lecture 3:

1. Temp-file-plus-rename for atomic publication.
2. SHA-256 of the canonicalised payload, stored alongside, verified on load.
3. Backup rotation: ``save.latest`` -> ``save.previous`` on every successful
   write; loader falls back to ``previous`` if ``latest`` fails to validate.

Plus a *simulated crash test*: write a corrupted ``save.latest``, demonstrate
that the loader rejects it on integrity check, and demonstrate that the
fallback to ``save.previous`` recovers the player's progress.

Run
---
    python3 exercise-05-atomic-write.py

Uses only the standard library. Prints a small ledger of every write and
every load attempt; prints ``OK`` on success.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Path helpers.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SavePaths:
    """The three filenames the rotation scheme uses for a single slot."""

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


# ---------------------------------------------------------------------------
# Canonicalisation and integrity.
# ---------------------------------------------------------------------------


def canonical_bytes(payload: dict[str, Any]) -> bytes:
    """Render ``payload`` as a deterministic UTF-8 byte string.

    ``sort_keys=True`` and ``separators=(",", ":")`` strip every formatting
    degree of freedom: the same logical payload produces the same bytes on
    every machine and every run. The bytes are what we hash.
    """
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def integrity_tag(payload: dict[str, Any]) -> str:
    """Return ``sha256:`` followed by the hex digest of ``canonical_bytes``."""
    digest: str = hashlib.sha256(canonical_bytes(payload)).hexdigest()
    return f"sha256:{digest}"


def envelope(payload: dict[str, Any]) -> dict[str, Any]:
    """Wrap ``payload`` in the on-disk envelope that carries the integrity tag."""
    return {"payload": payload, "integrity": integrity_tag(payload)}


def open_envelope(parsed: dict[str, Any]) -> dict[str, Any]:
    """Verify ``parsed['integrity']`` matches its payload; return the payload.

    Raises :class:`ValueError` on integrity mismatch.
    """
    if "payload" not in parsed or "integrity" not in parsed:
        raise ValueError("envelope: missing 'payload' or 'integrity' field")
    payload: dict[str, Any] = parsed["payload"]
    stored: str = parsed["integrity"]
    expected: str = integrity_tag(payload)
    if stored != expected:
        raise ValueError(f"envelope: integrity mismatch ({stored!r} != {expected!r})")
    return payload


# ---------------------------------------------------------------------------
# Atomic write with rotation.
# ---------------------------------------------------------------------------


def write_atomic_with_rotation(paths: SavePaths, payload: dict[str, Any]) -> None:
    """Write ``payload`` to ``paths.latest`` atomically, rotating the previous.

    The sequence is:

    1. Render the envelope and write it to ``paths.temp``. ``fsync`` to push the
       OS buffer to disk.
    2. If ``paths.latest`` already exists, rotate it to ``paths.previous``.
    3. Rename ``paths.temp`` over ``paths.latest`` to publish.

    A crash before step 3 leaves ``paths.latest`` untouched; a crash between
    steps 2 and 3 leaves ``paths.previous`` populated with the prior good save
    and ``paths.latest`` momentarily absent (the loader handles this).
    """
    blob: bytes = json.dumps(envelope(payload), sort_keys=True, indent=2).encode("utf-8")
    with open(paths.temp, "wb") as f:
        f.write(blob)
        f.flush()
        os.fsync(f.fileno())
    if paths.latest.exists():
        os.replace(paths.latest, paths.previous)
    os.replace(paths.temp, paths.latest)


def load_with_fallback(paths: SavePaths) -> dict[str, Any]:
    """Try ``paths.latest``; fall back to ``paths.previous`` if it is unreadable.

    Returns the *payload* (unwrapped). Raises :class:`FileNotFoundError` if
    neither file is loadable.
    """
    for candidate, label in ((paths.latest, "latest"), (paths.previous, "previous")):
        if not candidate.exists():
            continue
        try:
            parsed: dict[str, Any] = json.loads(candidate.read_text(encoding="utf-8"))
            payload: dict[str, Any] = open_envelope(parsed)
            print(f"  load: {label} accepted")
            return payload
        except (json.JSONDecodeError, ValueError) as exc:
            print(f"  load: {label} rejected ({exc})")
    raise FileNotFoundError("no readable save (latest and previous both failed)")


# ---------------------------------------------------------------------------
# Simulated crash test.
# ---------------------------------------------------------------------------


def corrupt_save(path: Path) -> None:
    """Flip a byte in the middle of ``path`` to simulate disk-level corruption."""
    data: bytearray = bytearray(path.read_bytes())
    if len(data) < 4:
        return
    # Flip a byte inside the payload region so the integrity hash will catch it.
    mid: int = len(data) // 2
    data[mid] = data[mid] ^ 0x40
    path.write_bytes(bytes(data))


# ---------------------------------------------------------------------------
# Demonstration.
# ---------------------------------------------------------------------------


def _demo() -> None:
    here: Path = Path(__file__).resolve().parent
    work_dir: Path = here / "_exercise05_work"
    work_dir.mkdir(exist_ok=True)
    paths: SavePaths = SavePaths.for_slot(work_dir, slot=0)

    try:
        # Write 1: the first save.
        payload_1: dict[str, Any] = {
            "version": 2,
            "player_name": "Alex",
            "current_score": 100,
            "current_level": "level_01",
        }
        print("write 1: first save (no previous yet)")
        write_atomic_with_rotation(paths, payload_1)
        loaded_1: dict[str, Any] = load_with_fallback(paths)
        assert loaded_1 == payload_1

        # Write 2: a second save (rotates the first to .prev).
        payload_2: dict[str, Any] = dict(payload_1, current_score=250, current_level="level_02")
        print()
        print("write 2: second save (first becomes .prev)")
        write_atomic_with_rotation(paths, payload_2)
        loaded_2: dict[str, Any] = load_with_fallback(paths)
        assert loaded_2 == payload_2

        # Write 3: a third save. After this, .latest is write-3 and .prev is write-2.
        payload_3: dict[str, Any] = dict(payload_2, current_score=400, current_level="level_03")
        print()
        print("write 3: third save (.prev becomes write-2)")
        write_atomic_with_rotation(paths, payload_3)

        # Simulated crash: flip a byte in the latest save.
        print()
        print("simulated corruption: flipping a byte in slot_00.save")
        corrupt_save(paths.latest)

        # Load now: latest fails integrity, previous should succeed and equal write-2.
        print("load after corruption:")
        recovered: dict[str, Any] = load_with_fallback(paths)
        assert recovered == payload_2, "fallback should equal write-2, not write-3"
        print(f"  recovered payload: score={recovered['current_score']} level={recovered['current_level']}")
        print(f"  (expected: write-2, which is score=250 level=level_02)")

        print()
        print("OK")
    finally:
        for p in (paths.latest, paths.previous, paths.temp):
            if p.exists():
                p.unlink()
        if work_dir.exists() and not any(work_dir.iterdir()):
            work_dir.rmdir()


if __name__ == "__main__":
    _demo()
