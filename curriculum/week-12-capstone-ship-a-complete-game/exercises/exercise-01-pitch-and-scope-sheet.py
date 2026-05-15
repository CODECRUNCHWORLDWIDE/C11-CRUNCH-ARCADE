"""Exercise 1 — Validate a Monday scope sheet against a schema.

The capstone week's first artefact is the Monday scope sheet — a plain-text
document with ten well-named fields that, together, are the contract you make
with yourself for the rest of the week. The scope sheet is the single most
predictive artefact for whether the capstone ships; this exercise gives you a
mechanical validator that rejects malformed sheets and accepts well-formed
ones.

The exercise does three things:

1. Defines a small ScopeSheet dataclass with the ten required fields from
   Lecture 1.
2. Parses a scope sheet from a Markdown-with-keyed-sections format (the same
   format mini-project/scope_sheet_template.md uses).
3. Validates the parsed sheet against the schema and prints a report.

The validator is conservative: missing fields fail, fields shorter than a
sensible minimum fail, fields longer than a sensible maximum warn, and the
asset list is checked for a minimum of 4 entries.

Run with:

    python3 exercise-01-pitch-and-scope-sheet.py

The script ships with two embedded fixtures — one passing and one failing —
and reports on both. The final line is OK on success or FAIL on any
unexpected behaviour.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ScopeSheet:
    """The Monday scope sheet, ten required fields from Lecture 1."""

    pitch: str = ""
    verb: str = ""
    goal: str = ""
    obstacle: str = ""
    loop_length: str = ""
    screen_count: str = ""
    subsystems_used: list[str] = field(default_factory=list)
    subsystems_not_used: list[str] = field(default_factory=list)
    asset_list: list[str] = field(default_factory=list)
    cuts_log: list[str] = field(default_factory=list)


REQUIRED_KEYS: dict[str, str] = {
    "PITCH": "pitch",
    "VERB": "verb",
    "GOAL": "goal",
    "OBSTACLE": "obstacle",
    "LOOP LENGTH": "loop_length",
    "SCREEN COUNT": "screen_count",
    "SUBSYSTEMS USED": "subsystems_used",
    "SUBSYSTEMS INTENTIONALLY NOT USED": "subsystems_not_used",
    "ASSET LIST": "asset_list",
    "CUTS LOG": "cuts_log",
}

LIST_KEYS: set[str] = {
    "subsystems_used",
    "subsystems_not_used",
    "asset_list",
    "cuts_log",
}


def parse_scope_sheet(text: str) -> ScopeSheet:
    """Parse a scope sheet from a keyed-sections plain text document.

    The format is:

        PITCH: one-line value
        VERB: one-line value
        ASSET LIST:
          - line 1
          - line 2

    Whitespace and trailing newlines are tolerated. Unknown keys are ignored
    with a stderr warning so that future additions to the template do not
    silently break parsing.
    """
    sheet = ScopeSheet()
    current_field: Optional[str] = None
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line:
            current_field = None
            continue
        # Single-line "KEY: value" form.
        m = re.match(r"^([A-Z][A-Z \-]+):\s*(.*)$", line)
        if m:
            key_str, value = m.group(1).strip(), m.group(2).strip()
            field_name = REQUIRED_KEYS.get(key_str)
            if field_name is None:
                sys.stderr.write(f"warning: unknown key {key_str!r} ignored\n")
                current_field = None
                continue
            if field_name in LIST_KEYS:
                # The list is on subsequent lines starting with "-".
                current_field = field_name
                if value:
                    # Inline value on the same line is treated as a single
                    # list entry.
                    getattr(sheet, field_name).append(value)
            else:
                setattr(sheet, field_name, value)
                current_field = None
            continue
        # Continuation lines for list values: "  - item" or "- item".
        m = re.match(r"^\s*-\s*(.+)$", line)
        if m and current_field in LIST_KEYS:
            item = m.group(1).strip()
            if item:
                getattr(sheet, current_field).append(item)
            continue
    return sheet


def validate(sheet: ScopeSheet) -> list[str]:
    """Validate a parsed sheet. Returns a list of human-readable errors.

    An empty list means the sheet passes. Errors are written in the
    "<field>: <reason>" form.
    """
    errors: list[str] = []
    if not sheet.pitch:
        errors.append("pitch: missing")
    elif len(sheet.pitch) < 20:
        errors.append(f"pitch: too short ({len(sheet.pitch)} chars; aim 20+)")
    elif len(sheet.pitch) > 200:
        errors.append(f"pitch: too long ({len(sheet.pitch)} chars; aim <=200)")
    if not sheet.verb:
        errors.append("verb: missing")
    elif len(sheet.verb.split()) > 4:
        errors.append("verb: too wordy (one verb, one to three words)")
    if not sheet.goal:
        errors.append("goal: missing")
    if not sheet.obstacle:
        errors.append("obstacle: missing")
    if not sheet.loop_length:
        errors.append("loop_length: missing")
    if not sheet.screen_count:
        errors.append("screen_count: missing")
    # The list-shaped fields each have a minimum-length requirement that
    # encodes the "you should know this on Monday" rule from Lecture 1.
    if len(sheet.subsystems_used) < 3:
        errors.append(
            f"subsystems_used: too few ({len(sheet.subsystems_used)} listed; "
            "Lecture 1 expects at least 3)"
        )
    if len(sheet.subsystems_not_used) < 1:
        errors.append(
            "subsystems_not_used: empty (Lecture 1 expects at least one "
            "intentional non-use)"
        )
    if len(sheet.asset_list) < 4:
        errors.append(
            f"asset_list: too few ({len(sheet.asset_list)} listed; aim 4-15)"
        )
    elif len(sheet.asset_list) > 15:
        errors.append(
            f"asset_list: too many ({len(sheet.asset_list)} listed; the "
            "scope is too big for a one-week build)"
        )
    return errors


PASSING_FIXTURE: str = """\
PITCH: You are a frog. You cross a four-lane highway. Each crossing the cars get 10% faster.
VERB: Hop
GOAL: Reach the top edge of the screen.
OBSTACLE: Cars in four lanes. Speed multiplier increments each crossing.
LOOP LENGTH: 30-90 seconds per run.
SCREEN COUNT: 3 (Title, Playing, Game Over).
SUBSYSTEMS USED:
  - W1 Game loop
  - W2 Collisions
  - W3 Vocab
  - W5 State machine
  - W6 Juice
  - W7 Save
  - W8 Audio
  - W10 Shaders
  - W11 Save (production)
SUBSYSTEMS INTENTIONALLY NOT USED:
  - W4 Tilemap
  - W9 Multiplayer
ASSET LIST:
  - Frog sprite, CC0 OpenGameArt
  - Car sprite x3, CC0 OpenGameArt
  - Road tile, self-drawn
  - Background music loop, CC-BY Freesound
  - SFX hop, splat, gameover, level-up
  - Font Press Start 2P, OFL
CUTS LOG:
  - Mon - cut river level (W4 tilemap, single-screen scope)
  - Mon - cut power-ups (out of scope)
  - Tue - cut multiplayer
"""

FAILING_FIXTURE: str = """\
PITCH: A game.
VERB: do many several various interesting things
GOAL:
OBSTACLE: stuff
LOOP LENGTH: forever
SCREEN COUNT: ?
SUBSYSTEMS USED:
  - W1
ASSET LIST:
  - one sprite
"""


def main() -> int:
    print("Exercise 1 — Validate a Monday scope sheet against a schema.")
    print()
    all_ok = True

    print("--- Fixture A: well-formed scope sheet ---")
    sheet_a = parse_scope_sheet(PASSING_FIXTURE)
    errors_a = validate(sheet_a)
    if errors_a:
        print(f"  unexpected errors: {errors_a}")
        all_ok = False
    else:
        print("  parsed and validated cleanly.")
        print(f"  pitch length: {len(sheet_a.pitch)} chars")
        print(f"  asset list:   {len(sheet_a.asset_list)} entries")
        print(f"  cuts log:     {len(sheet_a.cuts_log)} entries")

    print()
    print("--- Fixture B: malformed scope sheet ---")
    sheet_b = parse_scope_sheet(FAILING_FIXTURE)
    errors_b = validate(sheet_b)
    if not errors_b:
        print("  unexpected: no errors on a malformed sheet")
        all_ok = False
    else:
        print(f"  found {len(errors_b)} validation errors as expected:")
        for err in errors_b:
            print(f"    - {err}")

    print()
    if all_ok:
        print("OK")
        return 0
    print("FAIL")
    return 1


if __name__ == "__main__":
    sys.exit(main())
