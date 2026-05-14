"""exercise-02-versioned-saves-with-migration.py

Goal
----
Implement a save schema with three versions and a chain of migration
functions that walks an old save up to the current version. The
exercise generates three synthetic save files on disk (v1, v2, and v3)
and demonstrates loading each of them with v3 code, observing that all
three end up as a correct v3 ``GameState`` in memory.

This is the canonical demonstration of Lecture 3 §1-3: every save has
a ``schema_version`` byte, migrations step one version at a time, and
the framework composes the chain.

Expected behaviour
------------------
- A 920x560 window with a dark background.
- Three "save slot" panels stacked vertically. Each panel shows:
    - The on-disk JSON for that slot (rendered as text on the left).
    - The migrated v3 ``GameState`` after loading (rendered on the right).
- The status bar shows which migrations fired during the load.
- Press ``1`` to (re)write slot 1 as a fresh v1 save.
- Press ``2`` to (re)write slot 2 as a fresh v2 save.
- Press ``3`` to (re)write slot 3 as a fresh v3 save.
- Press ``L`` to (re)load all three slots; the panels update to show
  the as-loaded text and the migrated v3 result.
- Press ``X`` to corrupt slot 1's ``schema_version`` to a value with no
  migration path. The load fails loudly and the panel reports the error.
- ESC quits.

What you learn
--------------
- The ``schema_version`` integer as the first byte of every save.
- The migration ladder: ``migrate_v1_to_v2``, ``migrate_v2_to_v3``.
- The ``MIGRATIONS`` dict + ``migrate_to_current`` composer.
- The "additive only in practice" rule: ``coins`` (added in v2) and
  ``equipment`` (added in v3 by splitting inventory) both DEFAULT to
  values that match an older save's lack of the field.
- What happens when migration fails: we raise, the loader catches, the
  UI reports.

Estimated time
--------------
About 55-70 minutes.

To complete
-----------
The migrations and the composer are filled in. What you'll spend time
on is the rendering loop, the slot panels, the corruption test, and
internalising the rule that EACH migration only steps ONE version.

Run with::

    python exercise-02-versioned-saves-with-migration.py
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable

import pygame

# ----- Configuration --------------------------------------------------------

WINDOW_W: int = 920
WINDOW_H: int = 560
TARGET_FPS: int = 60
WINDOW_TITLE: str = "C11 Week 7 - Exercise 2 - Versioned saves + migration"

BG_COLOUR: tuple[int, int, int] = (24, 24, 32)
PANEL_COLOUR: tuple[int, int, int] = (38, 38, 50)
PANEL_BORDER: tuple[int, int, int] = (80, 80, 100)
TEXT_COLOUR: tuple[int, int, int] = (240, 240, 240)
DIM_COLOUR: tuple[int, int, int] = (160, 160, 170)
GOOD_COLOUR: tuple[int, int, int] = (132, 204, 22)
BAD_COLOUR: tuple[int, int, int] = (239, 68, 68)
WARN_COLOUR: tuple[int, int, int] = (251, 191, 36)

SLOT1_PATH: Path = Path("save_ex02_slot1.json")
SLOT2_PATH: Path = Path("save_ex02_slot2.json")
SLOT3_PATH: Path = Path("save_ex02_slot3.json")

CURRENT_SCHEMA_VERSION: int = 3


# ----- Synthetic save shapes (one per version) ------------------------------


def make_v1_save() -> dict:
    """A v1 save: pre-coin-economy. No coins field. No equipment."""
    return {
        "schema_version": 1,
        "timestamp_iso": datetime.now().isoformat(timespec="seconds"),
        "player_x": 100.0,
        "player_y": 240.0,
        "player_hp": 4,
        "player_hp_max": 5,
        # Inventory is a flat list of {id, count}. No "equipment" split.
        "inventory": [
            {"id": "potion_health", "count": 3},
            {"id": "eq_sword_iron", "count": 1},
            {"id": "key_brass", "count": 2},
            {"id": "eq_shield_wood", "count": 1},
        ],
        "current_level": "level_01",
    }


def make_v2_save() -> dict:
    """A v2 save: added ``coins`` for currency."""
    return {
        "schema_version": 2,
        "timestamp_iso": datetime.now().isoformat(timespec="seconds"),
        "player_x": 360.0,
        "player_y": 200.0,
        "player_hp": 5,
        "player_hp_max": 5,
        "inventory": [
            {"id": "potion_health", "count": 1},
            {"id": "eq_sword_steel", "count": 1},
            {"id": "key_brass", "count": 3},
        ],
        "current_level": "level_02",
        # New in v2.
        "coins": 47,
    }


def make_v3_save() -> dict:
    """A v3 save: ``inventory`` and ``equipment`` are separate lists."""
    return {
        "schema_version": 3,
        "timestamp_iso": datetime.now().isoformat(timespec="seconds"),
        "player_x": 540.0,
        "player_y": 320.0,
        "player_hp": 3,
        "player_hp_max": 6,
        "inventory": [
            {"id": "potion_health", "count": 2},
            {"id": "key_brass", "count": 4},
        ],
        # New in v3: equipment is its own list.
        "equipment": [
            {"id": "eq_sword_silver", "count": 1},
            {"id": "eq_shield_bronze", "count": 1},
        ],
        "current_level": "level_03",
        "coins": 128,
    }


# ----- Migrations -----------------------------------------------------------
#
# Each migration steps the dict ONE version forward. It mutates the dict
# in place AND returns it (so callers can chain or assign). The
# ``schema_version`` is updated last so the composer can read it.


def migrate_v1_to_v2(d: dict) -> dict:
    """v2 added ``coins`` for currency. Default existing v1 saves to 0."""
    d["coins"] = 0
    d["schema_version"] = 2
    return d


def migrate_v2_to_v3(d: dict) -> dict:
    """v3 split inventory into inventory + equipment.

    Convention: items with ``id`` starting ``eq_`` are equipment.
    """
    inventory = d.get("inventory", [])
    d["equipment"] = [it for it in inventory if str(it.get("id", "")).startswith("eq_")]
    d["inventory"] = [it for it in inventory if not str(it.get("id", "")).startswith("eq_")]
    d["schema_version"] = 3
    return d


MIGRATIONS: dict[int, Callable[[dict], dict]] = {
    1: migrate_v1_to_v2,
    2: migrate_v2_to_v3,
}


def migrate_to_current(d: dict) -> tuple[dict, list[str]]:
    """Walk a loaded dict through every migration up to CURRENT_SCHEMA_VERSION.

    Returns a tuple of (migrated_dict, list_of_migration_names_fired).
    Raises ``ValueError`` if a version has no migration path.
    """
    fired: list[str] = []
    version = int(d.get("schema_version", 1))
    while version < CURRENT_SCHEMA_VERSION:
        if version not in MIGRATIONS:
            raise ValueError(
                f"no migration from v{version} (current is v{CURRENT_SCHEMA_VERSION})"
            )
        migration = MIGRATIONS[version]
        d = migration(d)
        fired.append(f"v{version} -> v{version + 1}")
        version = int(d["schema_version"])
    return d, fired


# ----- The v3 GameState dataclass ------------------------------------------


@dataclass
class GameStateV3:
    """The CURRENT (v3) on-disk shape."""

    schema_version: int = CURRENT_SCHEMA_VERSION
    timestamp_iso: str = ""
    player_x: float = 0.0
    player_y: float = 0.0
    player_hp: int = 5
    player_hp_max: int = 5
    inventory: list[dict] = field(default_factory=list)
    equipment: list[dict] = field(default_factory=list)
    current_level: str = "level_01"
    coins: int = 0


def gamestate_from_dict_v3(d: dict) -> GameStateV3:
    """Build a v3 GameState from a (post-migration) dict."""
    return GameStateV3(
        schema_version=int(d.get("schema_version", CURRENT_SCHEMA_VERSION)),
        timestamp_iso=str(d.get("timestamp_iso", "")),
        player_x=float(d.get("player_x", 0.0)),
        player_y=float(d.get("player_y", 0.0)),
        player_hp=int(d.get("player_hp", 5)),
        player_hp_max=int(d.get("player_hp_max", 5)),
        inventory=list(d.get("inventory", [])),
        equipment=list(d.get("equipment", [])),
        current_level=str(d.get("current_level", "level_01")),
        coins=int(d.get("coins", 0)),
    )


# ----- File I/O ------------------------------------------------------------


def write_save(path: Path, payload: dict) -> None:
    """Naive write (no atomic-write; see Exercise 3 and the mini-project)."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)


def read_save_raw(path: Path) -> dict:
    """Read the JSON without migrating it. Used by the UI to show the
    on-disk shape."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@dataclass
class SlotView:
    """UI bookkeeping for one slot panel."""

    path: Path
    label: str
    raw_text: str = "(slot empty)"
    migrated: GameStateV3 | None = None
    migrations_fired: list[str] = field(default_factory=list)
    error: str = ""


def load_slot(view: SlotView) -> None:
    """Try to load the slot's file, migrate to v3, and populate the view."""
    view.error = ""
    view.migrated = None
    view.migrations_fired = []
    try:
        raw = read_save_raw(view.path)
        view.raw_text = json.dumps(raw, indent=2, sort_keys=True)
        migrated_dict, fired = migrate_to_current(raw)
        view.migrations_fired = fired
        view.migrated = gamestate_from_dict_v3(migrated_dict)
    except FileNotFoundError:
        view.raw_text = "(slot empty; press 1/2/3 to write a synthetic save)"
    except ValueError as e:
        view.error = str(e)
    except json.JSONDecodeError as e:
        view.error = f"JSON parse error: {e}"


# ----- Rendering helpers ----------------------------------------------------


def render_text_block(
    surface: pygame.Surface,
    font: pygame.font.Font,
    text: str,
    x: int,
    y: int,
    max_lines: int,
    colour: tuple[int, int, int] = TEXT_COLOUR,
    line_height: int = 16,
) -> None:
    """Render up to ``max_lines`` lines of ``text`` starting at (x, y).

    Long files are truncated with an ellipsis line.
    """
    lines = text.splitlines()
    truncated = False
    if len(lines) > max_lines:
        lines = lines[: max_lines - 1]
        truncated = True
    for i, line in enumerate(lines):
        surf = font.render(line, True, colour)
        surface.blit(surf, (x, y + i * line_height))
    if truncated:
        surf = font.render("...", True, DIM_COLOUR)
        surface.blit(surf, (x, y + max_lines * line_height - line_height))


def format_gamestate(gs: GameStateV3) -> str:
    """A compact, fixed-shape rendering of a v3 GameState."""
    lines = [
        f"schema_version : {gs.schema_version}",
        f"timestamp_iso  : {gs.timestamp_iso}",
        f"player_x       : {gs.player_x}",
        f"player_y       : {gs.player_y}",
        f"player_hp      : {gs.player_hp} / {gs.player_hp_max}",
        f"current_level  : {gs.current_level}",
        f"coins          : {gs.coins}",
        f"inventory      : {len(gs.inventory)} items",
    ]
    for it in gs.inventory:
        lines.append(f"    - {it.get('id', '?'):<16} x {it.get('count', '?')}")
    lines.append(f"equipment      : {len(gs.equipment)} items")
    for it in gs.equipment:
        lines.append(f"    - {it.get('id', '?'):<16} x {it.get('count', '?')}")
    return "\n".join(lines)


def render_slot_panel(
    surface: pygame.Surface,
    font_label: pygame.font.Font,
    font_mono: pygame.font.Font,
    view: SlotView,
    panel_rect: pygame.Rect,
) -> None:
    """Draw one slot panel: on-disk raw on the left, migrated v3 on the right."""
    pygame.draw.rect(surface, PANEL_COLOUR, panel_rect, border_radius=4)
    pygame.draw.rect(surface, PANEL_BORDER, panel_rect, width=1, border_radius=4)

    # Label
    label_surf = font_label.render(view.label, True, TEXT_COLOUR)
    surface.blit(label_surf, (panel_rect.x + 8, panel_rect.y + 6))

    # Migrations fired
    if view.error:
        msg = f"  ERROR: {view.error}"
        msg_surf = font_label.render(msg, True, BAD_COLOUR)
        surface.blit(msg_surf, (panel_rect.x + 8 + label_surf.get_width(), panel_rect.y + 6))
    elif view.migrations_fired:
        msg = "  migrations: " + " then ".join(view.migrations_fired)
        msg_surf = font_label.render(msg, True, WARN_COLOUR)
        surface.blit(msg_surf, (panel_rect.x + 8 + label_surf.get_width(), panel_rect.y + 6))
    elif view.migrated is not None:
        msg = "  (no migration needed)"
        msg_surf = font_label.render(msg, True, GOOD_COLOUR)
        surface.blit(msg_surf, (panel_rect.x + 8 + label_surf.get_width(), panel_rect.y + 6))

    # Split the panel in half: left = raw JSON, right = migrated GameState.
    inner_y = panel_rect.y + 30
    inner_h = panel_rect.height - 36
    half_w = (panel_rect.width - 24) // 2
    left_x = panel_rect.x + 8
    right_x = left_x + half_w + 8

    # Left: raw on-disk JSON.
    render_text_block(
        surface, font_mono, view.raw_text, left_x, inner_y,
        max_lines=inner_h // 16, colour=DIM_COLOUR,
    )

    # Right: migrated v3 GameState.
    if view.migrated is not None:
        right_text = format_gamestate(view.migrated)
        render_text_block(
            surface, font_mono, right_text, right_x, inner_y,
            max_lines=inner_h // 16, colour=TEXT_COLOUR,
        )


# ----- Main loop -----------------------------------------------------------


def main() -> int:
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    pygame.display.set_caption(WINDOW_TITLE)
    clock = pygame.time.Clock()
    font_lg = pygame.font.SysFont(None, 22)
    font_md = pygame.font.SysFont(None, 18)
    font_mono = pygame.font.SysFont("Menlo,Consolas,Courier", 14)

    slot1 = SlotView(SLOT1_PATH, "Slot 1 (v1 on disk)")
    slot2 = SlotView(SLOT2_PATH, "Slot 2 (v2 on disk)")
    slot3 = SlotView(SLOT3_PATH, "Slot 3 (v3 on disk)")

    # On first launch, write synthetic saves if any slot is empty.
    for path, maker in ((SLOT1_PATH, make_v1_save),
                        (SLOT2_PATH, make_v2_save),
                        (SLOT3_PATH, make_v3_save)):
        if not path.exists():
            write_save(path, maker())

    for view in (slot1, slot2, slot3):
        load_slot(view)

    running = True
    while running:
        clock.tick(TARGET_FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_1:
                    write_save(SLOT1_PATH, make_v1_save())
                    load_slot(slot1)
                elif event.key == pygame.K_2:
                    write_save(SLOT2_PATH, make_v2_save())
                    load_slot(slot2)
                elif event.key == pygame.K_3:
                    write_save(SLOT3_PATH, make_v3_save())
                    load_slot(slot3)
                elif event.key == pygame.K_l:
                    for view in (slot1, slot2, slot3):
                        load_slot(view)
                elif event.key == pygame.K_x:
                    # Corrupt slot 1: write a schema_version we have no
                    # migration for. The load should fail loudly.
                    bad = make_v1_save()
                    bad["schema_version"] = 99
                    write_save(SLOT1_PATH, bad)
                    load_slot(slot1)

        # ---- Render -----------------------------------------------------
        screen.fill(BG_COLOUR)

        # Header
        header = font_lg.render(
            f"Save format versioning  ::  current = v{CURRENT_SCHEMA_VERSION}",
            True, TEXT_COLOUR,
        )
        screen.blit(header, (12, 8))
        sub = font_md.render(
            "[1/2/3] rewrite slot as v1/v2/v3   [L] reload all   [X] corrupt slot 1   [ESC] quit",
            True, DIM_COLOUR,
        )
        screen.blit(sub, (12, 30))

        panel_h = (WINDOW_H - 80) // 3
        panel_y = 56
        for view in (slot1, slot2, slot3):
            rect = pygame.Rect(12, panel_y, WINDOW_W - 24, panel_h - 8)
            render_slot_panel(screen, font_md, font_mono, view, rect)
            panel_y += panel_h

        pygame.display.flip()

    pygame.quit()
    return 0


# ----- HINT (do not peek for 20 minutes) -----------------------------------
# If a v1 save loads with no equipment, that is CORRECT: v1 saves have
# no equipment items; the v2->v3 migration scans the inventory for
# "eq_*" ids and moves them out. A v1 save's "eq_sword_iron" item
# stays in the inventory through v1->v2 and is moved to equipment in
# v2->v3.
#
# If you press X and the slot 1 panel does NOT show an error message,
# check that ``migrate_to_current`` raises ``ValueError`` when the
# version is not in ``MIGRATIONS``. The composer must not silently fall
# through.
#
# If a migration runs more than once (e.g. v1 -> v2 -> v2 -> v2), check
# that each migration sets ``d["schema_version"]`` to the NEW version
# before returning. The composer reads it to decide whether to stop.
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    sys.exit(main())
