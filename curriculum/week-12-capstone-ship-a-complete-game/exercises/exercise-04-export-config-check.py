"""Exercise 4 — Parse a Godot export_presets.cfg and verify four targets.

Lecture 2 walked through configuring the four shipped targets — HTML5,
Windows Desktop, macOS, and Linux/X11. The Godot editor writes the four
presets to export_presets.cfg in the project root; this exercise parses
that file and reports which of the four targets are present, which are
missing, and which are misconfigured.

The validator checks:

  - All four target platforms are present.
  - Each preset has an export_path.
  - The HTML5 preset has Threads disabled (itch.io HTML5 hosting requires
    threads-off by default; see Lecture 2).
  - No preset has encryption enabled (the capstone ships unencrypted; if
    you turned encryption on by accident, you would lock yourself out of
    the build).

Run with:

    python3 exercise-04-export-config-check.py

No external dependencies; the parser is a small hand-written INI reader
tailored to Godot's export_presets.cfg dialect.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field


@dataclass
class Preset:
    """A single Godot export preset."""

    name: str = ""
    platform: str = ""
    runnable: bool = False
    export_path: str = ""
    options: dict[str, str] = field(default_factory=dict)


@dataclass
class PresetFile:
    """The whole parsed export_presets.cfg file."""

    presets: list[Preset] = field(default_factory=list)


REQUIRED_PLATFORMS: dict[str, str] = {
    "Web": "HTML5",
    "Windows Desktop": "Windows",
    "macOS": "macOS",
    "Linux/X11": "Linux",
}


def parse_export_presets(text: str) -> PresetFile:
    """Parse Godot's export_presets.cfg file.

    The format is INI-style with two kinds of section headers per preset:

        [preset.N]
        key="value"

        [preset.N.options]
        nested/key=value

    We collect both into a Preset object indexed by N.
    """
    presets: dict[int, Preset] = {}
    current_index: int | None = None
    is_options: bool = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith(";"):
            continue
        m = re.match(r"^\[preset\.(\d+)(\.options)?\]$", line)
        if m:
            current_index = int(m.group(1))
            is_options = bool(m.group(2))
            if current_index not in presets:
                presets[current_index] = Preset()
            continue
        if current_index is None:
            continue
        m = re.match(r"^([\w\-/\.]+)=(.*)$", line)
        if not m:
            continue
        key, value = m.group(1), m.group(2).strip()
        # Strip surrounding quotes on string values.
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        preset = presets[current_index]
        if is_options:
            preset.options[key] = value
        else:
            if key == "name":
                preset.name = value
            elif key == "platform":
                preset.platform = value
            elif key == "runnable":
                preset.runnable = value.lower() == "true"
            elif key == "export_path":
                preset.export_path = value
    return PresetFile(presets=[presets[i] for i in sorted(presets)])


def validate(pf: PresetFile) -> list[str]:
    """Validate a parsed preset file. Returns a list of errors."""
    errors: list[str] = []
    if not pf.presets:
        errors.append("no presets found; export_presets.cfg is empty")
        return errors
    present_platforms = {p.platform for p in pf.presets}
    for godot_name, friendly_name in REQUIRED_PLATFORMS.items():
        if godot_name not in present_platforms:
            errors.append(
                f"missing target {friendly_name} (Godot platform "
                f"name {godot_name!r})"
            )
    for p in pf.presets:
        if not p.export_path:
            errors.append(
                f"preset {p.name!r} ({p.platform}): export_path is empty"
            )
        if p.options.get("encryption/encrypted", "false").lower() == "true":
            errors.append(
                f"preset {p.name!r}: encryption is enabled; the capstone "
                "ships unencrypted"
            )
        if p.platform == "Web":
            threads = p.options.get(
                "variant/thread_support", "false"
            ).lower()
            if threads == "true":
                errors.append(
                    f"preset {p.name!r}: threads enabled; itch.io HTML5 "
                    "hosting does not serve cross-origin isolation headers "
                    "(see Lecture 2)"
                )
    return errors


PASSING_FIXTURE: str = """\
[preset.0]
name="Web"
platform="Web"
runnable=true
custom_features=""
export_filter="all_resources"
export_path="dist/web/index.html"

[preset.0.options]
variant/thread_support=false
encryption/encrypted=false

[preset.1]
name="Windows"
platform="Windows Desktop"
runnable=true
export_filter="all_resources"
export_path="dist/windows/MyGame.exe"

[preset.1.options]
encryption/encrypted=false
application/console_wrapper=false

[preset.2]
name="macOS"
platform="macOS"
runnable=true
export_filter="all_resources"
export_path="dist/macos/MyGame.app"

[preset.2.options]
encryption/encrypted=false
application/bundle_identifier="com.capstone.mygame"

[preset.3]
name="Linux"
platform="Linux/X11"
runnable=true
export_filter="all_resources"
export_path="dist/linux/MyGame.x86_64"

[preset.3.options]
encryption/encrypted=false
"""

FAILING_FIXTURE: str = """\
[preset.0]
name="Web"
platform="Web"
runnable=true
export_path=""

[preset.0.options]
variant/thread_support=true
encryption/encrypted=true

[preset.1]
name="macOS"
platform="macOS"
runnable=true
export_path="dist/macos/MyGame.app"

[preset.1.options]
encryption/encrypted=false
"""


def main() -> int:
    print("Exercise 4 — Parse export_presets.cfg and verify four targets.")
    print()
    all_ok = True

    print("--- Fixture A: four-target export_presets.cfg ---")
    pf_a = parse_export_presets(PASSING_FIXTURE)
    errors_a = validate(pf_a)
    if errors_a:
        print(f"  unexpected errors: {errors_a}")
        all_ok = False
    else:
        print(f"  parsed {len(pf_a.presets)} presets; all four targets present")
        for p in pf_a.presets:
            print(f"    - {p.name:8} ({p.platform:15}) -> {p.export_path}")

    print()
    print("--- Fixture B: two-target file with bad settings ---")
    pf_b = parse_export_presets(FAILING_FIXTURE)
    errors_b = validate(pf_b)
    if not errors_b:
        print("  unexpected: no errors on a broken preset file")
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
