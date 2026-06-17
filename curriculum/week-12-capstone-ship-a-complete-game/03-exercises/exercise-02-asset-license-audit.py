"""Exercise 2 — Audit a CREDITS.md against the asset-licensing rules.

Every asset shipped in the capstone has to carry a licence and (for CC-BY
family licences) an author attribution. Lecture 3 listed the CC licence
taxonomy and warned about the contaminating effect of CC-BY-SA in code
that may eventually be commercialised, and the unsafety of CC-BY-NC in
anything that may eventually be paid.

This exercise parses a CREDITS.md formatted as Lecture 3 prescribed and
reports:

  - assets missing a licence
  - CC-BY assets missing an author
  - CC-BY-SA assets (with a contamination warning)
  - CC-BY-NC assets (with a hard "do not ship" failure if the game is
    intended to be sold; for a free release the warning is informational)
  - unrecognised licence strings

Run with:

    python3 exercise-02-asset-license-audit.py

No external dependencies. The script ships with two embedded fixtures and
prints OK or FAIL on the final line.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from typing import Optional


@dataclass
class Asset:
    """A single asset entry from CREDITS.md."""

    name: str
    licence: str
    author: Optional[str]
    url: Optional[str]


KNOWN_LICENCES: set[str] = {
    "CC0",
    "CC-BY",
    "CC-BY-SA",
    "CC-BY-NC",
    "CC-BY-NC-SA",
    "CC-BY-ND",
    "OFL",       # Open Font License (Press Start 2P et al.)
    "MIT",       # most open-source code
    "Apache-2.0",
    "GPL",
    "Public Domain",
    "Self-drawn",
    "Self-made",
}

# Licences that require an attributed author in the credits line.
ATTRIBUTION_REQUIRED: set[str] = {
    "CC-BY",
    "CC-BY-SA",
    "CC-BY-NC",
    "CC-BY-NC-SA",
    "CC-BY-ND",
}

# Licences that warn (commercial contamination, non-commercial restriction).
WARN_LICENCES: set[str] = {"CC-BY-SA", "CC-BY-NC", "CC-BY-NC-SA"}


def parse_credits(text: str) -> list[Asset]:
    """Parse a CREDITS.md following the Lecture 3 template.

    The format is bullet lines of the form:

        - **Name**, descriptor. CC-BY by "AuthorName" on Platform.
          URL

    The first sentence's last comma-separated chunk is the licence-and-author.
    The trailing line, if it begins with "http", is the URL.
    """
    assets: list[Asset] = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        m = re.match(r"^-\s*\*\*(.+?)\*\*,?\s*(.*)$", line)
        if m:
            name = m.group(1).strip()
            rest = m.group(2)
            licence, author = _extract_licence_and_author(rest)
            url: Optional[str] = None
            # The asset's URL may be on the next non-empty indented line.
            j = i + 1
            while j < len(lines) and lines[j].strip() == "":
                j += 1
            if j < len(lines):
                next_line = lines[j].strip()
                if next_line.startswith("http"):
                    url = next_line
                    i = j
            assets.append(
                Asset(name=name, licence=licence, author=author, url=url)
            )
        i += 1
    return assets


def _extract_licence_and_author(rest: str) -> tuple[str, Optional[str]]:
    """Pull the licence and author from the descriptor text.

    Tries to be lenient: matches "<LIC> by \"Name\"", "<LIC>, by Name",
    "<LIC> from Source", and bare "<LIC>".
    """
    licence_pattern = (
        r"\b(CC0|CC-BY-NC-SA|CC-BY-NC|CC-BY-SA|CC-BY-ND|CC-BY|OFL|MIT|"
        r"Apache-2\.0|GPL|Public Domain|Self-drawn|Self-made)\b"
    )
    m = re.search(licence_pattern, rest)
    if not m:
        return "UNKNOWN", None
    licence = m.group(1)
    after = rest[m.end():]
    author_match = re.search(
        r'by\s+"([^"]+)"|by\s+([A-Z][\w\-]+(?:\s+[A-Z][\w\-]+)*)',
        after,
    )
    if author_match:
        author = author_match.group(1) or author_match.group(2)
        return licence, author.strip()
    return licence, None


@dataclass
class AuditReport:
    """The result of auditing a CREDITS.md."""

    total_assets: int
    errors: list[str]
    warnings: list[str]

    @property
    def passed(self) -> bool:
        """True if the audit recorded no errors. Warnings do not fail."""
        return not self.errors


def audit(
    assets: list[Asset],
    *,
    commercial_intent: bool = False,
) -> AuditReport:
    """Audit a parsed asset list. Returns errors and warnings.

    The commercial_intent flag escalates CC-BY-NC warnings to errors; for
    a free itch.io release (the default) NC is informational.
    """
    errors: list[str] = []
    warnings: list[str] = []
    if not assets:
        errors.append("no asset entries found; CREDITS.md is empty")
        return AuditReport(total_assets=0, errors=errors, warnings=warnings)
    for a in assets:
        if a.licence == "UNKNOWN":
            errors.append(
                f"asset {a.name!r}: licence missing or unrecognised"
            )
            continue
        if a.licence not in KNOWN_LICENCES:
            errors.append(
                f"asset {a.name!r}: unknown licence {a.licence!r}"
            )
            continue
        if a.licence in ATTRIBUTION_REQUIRED and not a.author:
            errors.append(
                f"asset {a.name!r}: {a.licence} requires an author "
                "attribution; none found"
            )
        if a.licence in WARN_LICENCES:
            if a.licence in {"CC-BY-NC", "CC-BY-NC-SA"} and commercial_intent:
                errors.append(
                    f"asset {a.name!r}: {a.licence} is non-commercial; "
                    "the build is marked for commercial release"
                )
            else:
                warnings.append(
                    f"asset {a.name!r}: {a.licence} carries restrictions "
                    "(see Lecture 3 on licence taxonomy)"
                )
    return AuditReport(
        total_assets=len(assets), errors=errors, warnings=warnings
    )


PASSING_FIXTURE: str = """\
# Credits

## Art

- **Frog sprite**, 32x32, 4 directions. CC0 by "PixelArtist123" on OpenGameArt.
  https://opengameart.org/content/cute-frog-sprite
- **Car sprites**, 64x32, 3 variants. CC-BY by "RoadWarriorArt" on OpenGameArt.
  https://opengameart.org/content/road-cars-pack
- **Road tile**, 32x32. Self-drawn by "Capstone Student".

## Audio

- **Hop SFX**. CC0 by "FreesoundUser42" on Freesound.
  https://freesound.org/people/FreesoundUser42/sounds/12345/
- **Background music loop**. CC-BY by "AmbientCreator99" on Freesound.
  https://freesound.org/people/AmbientCreator99/sounds/67890/

## Fonts

- **Press Start 2P**, pixel-art font. OFL by "Cody Boisclair".

## Tools

- **Godot 4.2.2-stable**. MIT by "Godot Engine contributors".
"""

FAILING_FIXTURE: str = """\
# Credits

## Art

- **Frog sprite**, 32x32. (no licence stated)
- **Car sprite**. CC-BY on OpenGameArt.
- **Truck sprite**. CC-BY-NC by "ContestArtist".
- **Background image**. CC-BY-SA by "TileBaron".
- **Sound pack**. Bogus-License-9000 by "FreesoundUser42".
"""


def main() -> int:
    print("Exercise 2 — Audit a CREDITS.md against asset-licensing rules.")
    print()
    all_ok = True

    print("--- Fixture A: clean CREDITS.md ---")
    assets_a = parse_credits(PASSING_FIXTURE)
    report_a = audit(assets_a, commercial_intent=False)
    print(f"  parsed {report_a.total_assets} asset entries")
    if report_a.errors:
        print(f"  unexpected errors: {report_a.errors}")
        all_ok = False
    else:
        print("  no errors.")
    if report_a.warnings:
        print(f"  {len(report_a.warnings)} warnings (informational):")
        for w in report_a.warnings:
            print(f"    - {w}")

    print()
    print("--- Fixture B: malformed CREDITS.md (commercial intent set) ---")
    assets_b = parse_credits(FAILING_FIXTURE)
    report_b = audit(assets_b, commercial_intent=True)
    print(f"  parsed {report_b.total_assets} asset entries")
    if not report_b.errors:
        print("  unexpected: no errors on a malformed credits file")
        all_ok = False
    else:
        print(f"  found {len(report_b.errors)} errors as expected:")
        for e in report_b.errors:
            print(f"    - {e}")
    if report_b.warnings:
        print(f"  plus {len(report_b.warnings)} warnings:")
        for w in report_b.warnings:
            print(f"    - {w}")

    print()
    if all_ok:
        print("OK")
        return 0
    print("FAIL")
    return 1


if __name__ == "__main__":
    sys.exit(main())
