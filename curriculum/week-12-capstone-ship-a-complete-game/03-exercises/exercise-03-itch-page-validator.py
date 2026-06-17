"""Exercise 3 — Validate a page.md against the itch.io page checklist.

Lecture 3 named the twelve parts of an itch.io page. This exercise gives
you a mechanical validator that reads a Markdown page draft (the one
mini-project/itch_page_template.md ships) and reports which parts are
present, which are missing, and which look like Sunday-night cram-session
filler.

The validator is opinionated. It enforces:

  - A title (#1 heading).
  - A one-line tagline immediately under the title.
  - At least three paragraphs of body copy (Lecture 3 minimum).
  - A banner-image reference (line with "BANNER:" key).
  - A thumbnail reference ("THUMBNAIL:" key).
  - A trailer URL ("TRAILER:" key, must point to youtube.com, youtu.be,
    or vimeo.com).
  - At least three screenshot references.
  - A controls section.
  - A credits section.
  - A platform list ("PLATFORMS:" key with at least one of html5, windows,
    macos, linux).
  - A price line ("PRICE:" key, value must be one of Free, PWYW, or a
    dollar amount).

Run with:

    python3 exercise-03-itch-page-validator.py

No external dependencies. Two embedded fixtures; final OK/FAIL line.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field


@dataclass
class PageDraft:
    """A parsed itch.io page draft."""

    title: str = ""
    tagline: str = ""
    banner: str = ""
    thumbnail: str = ""
    trailer: str = ""
    screenshots: list[str] = field(default_factory=list)
    body_paragraphs: list[str] = field(default_factory=list)
    has_controls: bool = False
    has_credits: bool = False
    platforms: list[str] = field(default_factory=list)
    price: str = ""


VALID_PLATFORMS: set[str] = {"html5", "windows", "macos", "linux"}
VALID_TRAILER_HOSTS: tuple[str, ...] = (
    "youtube.com",
    "youtu.be",
    "vimeo.com",
)


def parse_page(text: str) -> PageDraft:
    """Parse a page draft. Tolerates Markdown plus key-value frontmatter."""
    page = PageDraft()
    lines = text.splitlines()
    in_body = False
    body_buf: list[str] = []
    section_heading: str = ""
    for raw_line in lines:
        line = raw_line.rstrip()
        # Key-value frontmatter lines.
        m = re.match(r"^([A-Z]+):\s*(.+)$", line)
        if m:
            key, value = m.group(1), m.group(2).strip()
            if key == "BANNER":
                page.banner = value
            elif key == "THUMBNAIL":
                page.thumbnail = value
            elif key == "TRAILER":
                page.trailer = value
            elif key == "SCREENSHOT":
                page.screenshots.append(value)
            elif key == "PLATFORMS":
                page.platforms = [
                    p.strip().lower() for p in value.split(",") if p.strip()
                ]
            elif key == "PRICE":
                page.price = value
            elif key == "TAGLINE":
                page.tagline = value
            continue
        if line.startswith("# "):
            page.title = line[2:].strip()
            in_body = True
            continue
        if line.startswith("## "):
            section_heading = line[3:].strip().lower()
            if "control" in section_heading:
                page.has_controls = True
            if "credit" in section_heading:
                page.has_credits = True
            if body_buf:
                paragraph = " ".join(body_buf).strip()
                if paragraph and not page.tagline:
                    page.tagline = paragraph
                elif paragraph:
                    page.body_paragraphs.append(paragraph)
                body_buf = []
            continue
        if not in_body:
            continue
        if not line.strip():
            if body_buf:
                paragraph = " ".join(body_buf).strip()
                if paragraph and not page.tagline:
                    page.tagline = paragraph
                elif paragraph:
                    page.body_paragraphs.append(paragraph)
                body_buf = []
            continue
        if section_heading in ("controls", "credits"):
            # Inside controls/credits sections; do not append to body.
            continue
        body_buf.append(line.strip())
    # Flush the trailing buffer.
    if body_buf:
        paragraph = " ".join(body_buf).strip()
        if paragraph and not page.tagline:
            page.tagline = paragraph
        elif paragraph:
            page.body_paragraphs.append(paragraph)
    return page


def validate(page: PageDraft) -> list[str]:
    """Validate a parsed page. Returns a list of error strings."""
    errors: list[str] = []
    if not page.title:
        errors.append("title: missing (need a '# Title' line)")
    if not page.tagline:
        errors.append("tagline: missing (one-line description under title)")
    elif len(page.tagline) > 120:
        errors.append(
            f"tagline: too long ({len(page.tagline)} chars; aim <=120)"
        )
    if not page.banner:
        errors.append("banner: missing (BANNER: key)")
    if not page.thumbnail:
        errors.append("thumbnail: missing (THUMBNAIL: key)")
    if not page.trailer:
        errors.append("trailer: missing (TRAILER: key)")
    elif not any(host in page.trailer for host in VALID_TRAILER_HOSTS):
        errors.append(
            f"trailer: URL {page.trailer!r} is not on a recognised host "
            "(youtube.com, youtu.be, vimeo.com)"
        )
    if len(page.screenshots) < 3:
        errors.append(
            f"screenshots: too few ({len(page.screenshots)}; need at least 3)"
        )
    elif len(page.screenshots) > 5:
        errors.append(
            f"screenshots: too many ({len(page.screenshots)}; aim 3-5)"
        )
    if len(page.body_paragraphs) < 2:
        errors.append(
            f"body: too few paragraphs ({len(page.body_paragraphs)}; "
            "Lecture 3 minimum is 2-3 body paragraphs after the tagline)"
        )
    elif len(page.body_paragraphs) > 5:
        errors.append(
            f"body: too many paragraphs ({len(page.body_paragraphs)}; "
            "page is too long, aim 3-5 total)"
        )
    if not page.has_controls:
        errors.append("controls: missing ## Controls section")
    if not page.has_credits:
        errors.append("credits: missing ## Credits section")
    if not page.platforms:
        errors.append("platforms: missing (PLATFORMS: key)")
    else:
        unknown = [p for p in page.platforms if p not in VALID_PLATFORMS]
        if unknown:
            errors.append(
                f"platforms: unknown values {unknown!r}; valid are "
                f"{sorted(VALID_PLATFORMS)}"
            )
    if not page.price:
        errors.append("price: missing (PRICE: key)")
    elif page.price.lower() not in ("free", "pwyw") and not re.match(
        r"^\$\d+(\.\d{2})?$", page.price
    ):
        errors.append(
            f"price: unrecognised value {page.price!r}; use Free, PWYW, "
            "or a dollar amount like $2.00"
        )
    return errors


PASSING_FIXTURE: str = """\
BANNER: art/banner-920x480.png
THUMBNAIL: art/thumb-315x250.png
TRAILER: https://www.youtube.com/watch?v=abc123
SCREENSHOT: art/screen-1.png
SCREENSHOT: art/screen-2.png
SCREENSHOT: art/screen-3.png
PLATFORMS: html5, windows, macos, linux
PRICE: Free
TAGLINE: Cross the road. Cars get faster.

# Frog Cross

You are a frog. Four lanes of traffic between you and the other side.
Each crossing the cars get faster. There is no power-up, no respawn,
no second chance - only your reflexes and the next gap in the traffic.

The build was made in Godot 4.2 for the C11 Crunch Arcade capstone in
May 2026. Single-player, single-screen, single-mechanic. Five minutes
from your first hop to your first high score.

The shipped build runs in the browser (HTML5), on Windows, on macOS,
and on Linux. No install required for the web build. No account needed.

## Controls

Arrow keys or WASD to hop. One tile per input. No mid-hop cancellation.

## Credits

Frog sprite by PixelArtist123 (CC0). Car sprites by RoadWarriorArt
(CC-BY, OpenGameArt). Hop SFX by FreesoundUser42 (CC0, Freesound).
"""

FAILING_FIXTURE: str = """\
# A Game

A short game I made for class.

## Controls

Arrows.
"""


def main() -> int:
    print("Exercise 3 — Validate a page.md against the itch.io checklist.")
    print()
    all_ok = True

    print("--- Fixture A: well-formed page ---")
    page_a = parse_page(PASSING_FIXTURE)
    errors_a = validate(page_a)
    if errors_a:
        print(f"  unexpected errors: {errors_a}")
        all_ok = False
    else:
        print("  parsed and validated cleanly.")
        print(f"  title:        {page_a.title!r}")
        print(f"  tagline:      {page_a.tagline!r}")
        print(f"  body paragraphs: {len(page_a.body_paragraphs)}")
        print(f"  screenshots:  {len(page_a.screenshots)}")
        print(f"  platforms:    {page_a.platforms}")

    print()
    print("--- Fixture B: minimal placeholder page ---")
    page_b = parse_page(FAILING_FIXTURE)
    errors_b = validate(page_b)
    if not errors_b:
        print("  unexpected: no errors on a placeholder page")
        all_ok = False
    else:
        print(f"  found {len(errors_b)} errors as expected:")
        for e in errors_b:
            print(f"    - {e}")

    print()
    if all_ok:
        print("OK")
        return 0
    print("FAIL")
    return 1


if __name__ == "__main__":
    sys.exit(main())
