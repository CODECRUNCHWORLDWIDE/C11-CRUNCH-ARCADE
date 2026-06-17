"""exercise-01-json-save-load.py

Goal
----
Implement a complete JSON save/load round-trip in a tiny Pygame
sandbox. A player moves with WASD, picks up coloured coins by walking
over them, and can save and load progress at any time. Save with S,
load with L. The persistent state is the player's (x, y) and inventory
counts; everything else (velocity, animation, particles) is session
state and is reset on load.

This exercise is the canonical implementation of Lecture 1's four
ideas: the ``GameState`` dataclass, the ``to_dict``/``from_dict``
boundary, the ``capture_state``/``apply_state`` bridge, and the rule
that ``pygame.Surface`` references never appear in a save file.

Expected behaviour
------------------
- An 800x480 window with a dark background.
- A Coin-Pink square (the player) is movable with WASD.
- Three coloured coins are scattered on the field: gold, silver, gem.
- Walking over a coin removes it from the field and increments the
  matching inventory counter.
- The HUD shows player coords, inventory counts, last save action.
- S saves to ``save_ex01.json``. The HUD flashes "saved" for 30 frames.
- L loads from ``save_ex01.json``. The player teleports to the saved
  coords, the inventory restores, and any uncollected coins respawn at
  their original positions. The HUD flashes "loaded" for 30 frames.
- R resets to a fresh game (no save round-trip).
- ESC quits.

What you learn
--------------
- The ``GameState`` dataclass and why it is FLAT (no nested objects).
- The ``to_dict``/``from_dict`` boundary using ``dataclasses.asdict``.
- The ``capture_state``/``apply_state`` pair: how a live game maps to
  and from the on-disk record.
- The "presentation never saved" rule: the player's ``pygame.Surface``
  is not in the save file. The colour ID is.
- Reading and writing JSON with ``json.dump`` / ``json.load`` and the
  ``indent=2, sort_keys=True`` defaults for a diffable file.
- The minimal "session state is reset on load" discipline: velocity
  goes to zero on load even though it is part of the live Player.

Estimated time
--------------
About 50-60 minutes.

To complete
-----------
Read the structure top-to-bottom. The ``GameState`` class is filled
in; the ``save_to_disk`` and ``load_from_disk`` helpers are filled in;
the ``capture_state`` and ``apply_state`` bodies are filled in. What
you'll spend time on is wiring the HUD flash, testing the round-trip,
and confirming that "coins respawn on load" feels right. The HINT
block at the bottom has nudges.

Run with::

    python exercise-01-json-save-load.py
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

import pygame

# ----- Configuration --------------------------------------------------------

WINDOW_W: int = 800
WINDOW_H: int = 480
TARGET_FPS: int = 60
WINDOW_TITLE: str = "C11 Week 7 - Exercise 1 - JSON save/load"

PLAYER_SIZE: int = 28
PLAYER_SPEED: float = 220.0  # pixels per second

COIN_RADIUS: int = 10

SAVE_PATH: Path = Path("save_ex01.json")

# Colours
BG_COLOUR: tuple[int, int, int] = (24, 24, 32)
PLAYER_COLOUR: tuple[int, int, int] = (236, 72, 153)     # Coin Pink
TEXT_COLOUR: tuple[int, int, int] = (240, 240, 240)
DIM_COLOUR: tuple[int, int, int] = (140, 140, 150)
SAVE_FLASH_COLOUR: tuple[int, int, int] = (132, 204, 22)
LOAD_FLASH_COLOUR: tuple[int, int, int] = (96, 165, 250)

# Coin palette by id.
COIN_COLOURS: dict[str, tuple[int, int, int]] = {
    "gold":   (250, 204, 21),
    "silver": (203, 213, 225),
    "gem":    (167, 139, 250),
}

# Starting coin positions. Each coin's "id" is its colour key.
INITIAL_COINS: list[tuple[str, float, float]] = [
    ("gold",   180.0, 140.0),
    ("gold",   240.0, 360.0),
    ("silver", 540.0, 200.0),
    ("silver", 660.0, 380.0),
    ("gem",    400.0, 240.0),
    ("gem",    620.0, 100.0),
]

SAVE_SCHEMA_VERSION: int = 1
FLASH_FRAMES: int = 30


# ----- The save contract (Lecture 1) ---------------------------------------


@dataclass
class GameState:
    """The on-disk shape of a player's progress.

    Persistent state ONLY. No pygame.Surface, no velocity, no FSM.
    """

    schema_version: int = SAVE_SCHEMA_VERSION
    timestamp_iso: str = ""

    # Player progress
    player_x: float = 0.0
    player_y: float = 0.0

    # Inventory: dict of {coin_id: count}.
    inventory: dict[str, int] = field(default_factory=dict)

    # Which coin indices have been collected. We store INDICES into the
    # INITIAL_COINS list, not the (x, y) positions themselves; positions
    # are derived from the index. A clean example of "store the minimum
    # that lets you reconstruct the rest."
    collected_coin_indices: list[int] = field(default_factory=list)


def gamestate_to_dict(gs: GameState) -> dict:
    """Convert a GameState to a JSON-safe dict."""
    return asdict(gs)


def gamestate_from_dict(d: dict) -> GameState:
    """Convert a JSON-safe dict back to a GameState.

    Tolerates missing fields by falling back to dataclass defaults.
    This is the entire forward-compatibility story for v1->v1 reads.
    """
    defaults = GameState()
    return GameState(
        schema_version=int(d.get("schema_version", defaults.schema_version)),
        timestamp_iso=str(d.get("timestamp_iso", defaults.timestamp_iso)),
        player_x=float(d.get("player_x", defaults.player_x)),
        player_y=float(d.get("player_y", defaults.player_y)),
        inventory={str(k): int(v) for k, v in d.get("inventory", {}).items()},
        collected_coin_indices=[int(i) for i in d.get("collected_coin_indices", [])],
    )


def save_to_disk(gs: GameState, path: Path) -> None:
    """Write a GameState to disk as readable JSON.

    This is the NAIVE version. Atomic writes, backup chains, and
    checksums are Exercise 2 and the mini-project. Here we just dump.
    """
    with open(path, "w", encoding="utf-8") as f:
        json.dump(gamestate_to_dict(gs), f, indent=2, sort_keys=True)


def load_from_disk(path: Path) -> GameState:
    """Read a GameState from disk.

    Raises ``FileNotFoundError`` if the file does not exist.
    Raises ``json.JSONDecodeError`` if the file is malformed.
    """
    with open(path, "r", encoding="utf-8") as f:
        return gamestate_from_dict(json.load(f))


# ----- Live game objects ----------------------------------------------------


@dataclass
class Player:
    """Live player state. Contains BOTH persistent and session fields."""

    # Persistent (goes in the save)
    x: float = 100.0
    y: float = 240.0

    # Session (NOT in the save)
    vx: float = 0.0
    vy: float = 0.0


@dataclass
class Coin:
    """A pickup on the map. Index into INITIAL_COINS is the identity."""

    index: int
    coin_id: str
    x: float
    y: float
    alive: bool = True


def make_initial_coins() -> list[Coin]:
    """Build the coin field from INITIAL_COINS."""
    return [
        Coin(index=i, coin_id=cid, x=cx, y=cy)
        for i, (cid, cx, cy) in enumerate(INITIAL_COINS)
    ]


# ----- The capture/apply bridge --------------------------------------------


def capture_state(player: Player, coins: list[Coin], inventory: dict[str, int]) -> GameState:
    """Pull persistent fields from live objects into a GameState."""
    collected = [c.index for c in coins if not c.alive]
    return GameState(
        schema_version=SAVE_SCHEMA_VERSION,
        timestamp_iso=datetime.now().isoformat(timespec="seconds"),
        player_x=player.x,
        player_y=player.y,
        inventory=dict(inventory),
        collected_coin_indices=collected,
    )


def apply_state(gs: GameState, player: Player, coins: list[Coin], inventory: dict[str, int]) -> None:
    """Write a loaded GameState into the live game objects."""
    # Persistent: restore from the save.
    player.x = gs.player_x
    player.y = gs.player_y

    # Session: reset on load. The player did not save mid-air.
    player.vx = 0.0
    player.vy = 0.0

    # Inventory: replace contents.
    inventory.clear()
    inventory.update(gs.inventory)

    # Coins: respawn all, then mark collected ones dead.
    fresh = make_initial_coins()
    coins.clear()
    coins.extend(fresh)
    collected_set = set(gs.collected_coin_indices)
    for c in coins:
        if c.index in collected_set:
            c.alive = False


# ----- Game loop ------------------------------------------------------------


def main() -> int:
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    pygame.display.set_caption(WINDOW_TITLE)
    clock = pygame.time.Clock()
    font_lg = pygame.font.SysFont(None, 26)
    font_sm = pygame.font.SysFont(None, 20)

    player = Player()
    coins = make_initial_coins()
    inventory: dict[str, int] = {}

    flash_text: str = ""
    flash_colour: tuple[int, int, int] = TEXT_COLOUR
    flash_t: int = 0
    last_save_iso: str = ""

    running = True
    while running:
        dt = clock.tick(TARGET_FPS) / 1000.0

        # ---- Events -----------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_s:
                    gs = capture_state(player, coins, inventory)
                    save_to_disk(gs, SAVE_PATH)
                    last_save_iso = gs.timestamp_iso
                    flash_text = f"saved -> {SAVE_PATH.name}"
                    flash_colour = SAVE_FLASH_COLOUR
                    flash_t = FLASH_FRAMES
                elif event.key == pygame.K_l:
                    try:
                        gs = load_from_disk(SAVE_PATH)
                        apply_state(gs, player, coins, inventory)
                        last_save_iso = gs.timestamp_iso
                        flash_text = f"loaded <- {SAVE_PATH.name}"
                        flash_colour = LOAD_FLASH_COLOUR
                        flash_t = FLASH_FRAMES
                    except FileNotFoundError:
                        flash_text = "no save file found"
                        flash_colour = DIM_COLOUR
                        flash_t = FLASH_FRAMES
                elif event.key == pygame.K_r:
                    player = Player()
                    coins = make_initial_coins()
                    inventory = {}
                    flash_text = "reset"
                    flash_colour = DIM_COLOUR
                    flash_t = FLASH_FRAMES

        # ---- Input poll for held movement -------------------------------
        keys = pygame.key.get_pressed()
        vx = 0.0
        vy = 0.0
        if keys[pygame.K_a]:
            vx -= 1.0
        if keys[pygame.K_d]:
            vx += 1.0
        if keys[pygame.K_w]:
            vy -= 1.0
        if keys[pygame.K_s]:
            # S is also the save key. We only treat it as movement if
            # SHIFT is held, so a casual S press does not glide the
            # player. This is a deliberate keybind clash: pressing S to
            # save should NOT also move the player.
            if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                vy += 1.0
        # Normalise diagonals so the player does not move sqrt(2)x faster.
        norm = (vx * vx + vy * vy) ** 0.5
        if norm > 0.0:
            vx /= norm
            vy /= norm
        player.vx = vx * PLAYER_SPEED
        player.vy = vy * PLAYER_SPEED

        # ---- Update -----------------------------------------------------
        player.x += player.vx * dt
        player.y += player.vy * dt
        # Clamp inside window
        half = PLAYER_SIZE / 2.0
        if player.x < half:
            player.x = half
        if player.x > WINDOW_W - half:
            player.x = WINDOW_W - half
        if player.y < half:
            player.y = half
        if player.y > WINDOW_H - half:
            player.y = WINDOW_H - half

        # Coin pickup
        for c in coins:
            if not c.alive:
                continue
            dx = player.x - c.x
            dy = player.y - c.y
            if dx * dx + dy * dy <= (COIN_RADIUS + half) ** 2:
                c.alive = False
                inventory[c.coin_id] = inventory.get(c.coin_id, 0) + 1

        if flash_t > 0:
            flash_t -= 1

        # ---- Render -----------------------------------------------------
        screen.fill(BG_COLOUR)

        # Coins
        for c in coins:
            if c.alive:
                colour = COIN_COLOURS[c.coin_id]
                pygame.draw.circle(screen, colour, (int(c.x), int(c.y)), COIN_RADIUS)
                pygame.draw.circle(screen, (0, 0, 0), (int(c.x), int(c.y)), COIN_RADIUS, 1)

        # Player
        prect = pygame.Rect(0, 0, PLAYER_SIZE, PLAYER_SIZE)
        prect.center = (int(player.x), int(player.y))
        pygame.draw.rect(screen, PLAYER_COLOUR, prect, border_radius=4)

        # HUD
        lines: list[tuple[str, tuple[int, int, int]]] = [
            (f"pos: ({player.x:7.1f}, {player.y:7.1f})", TEXT_COLOUR),
            (
                "inv: "
                + ", ".join(f"{k}={v}" for k, v in sorted(inventory.items()))
                if inventory
                else "inv: (empty)",
                TEXT_COLOUR,
            ),
            (f"last save: {last_save_iso or '(none)'}", DIM_COLOUR),
            ("[WASD] move    [S] save    [L] load    [R] reset    [ESC] quit", DIM_COLOUR),
        ]
        y = 10
        for text, colour in lines:
            surf = font_sm.render(text, True, colour)
            screen.blit(surf, (10, y))
            y += 22

        if flash_t > 0:
            surf = font_lg.render(flash_text, True, flash_colour)
            screen.blit(surf, (WINDOW_W - surf.get_width() - 12, 10))

        pygame.display.flip()

    pygame.quit()
    return 0


# ----- HINT (do not peek for 20 minutes) -----------------------------------
# If the load doesn't restore your inventory, check that
# ``apply_state`` ``.clear()``s the live dict before ``.update()``ing
# it. Otherwise you accumulate the on-disk inventory ON TOP of whatever
# is already in memory.
#
# If coins do not respawn on load, check that ``apply_state`` builds a
# fresh list with ``make_initial_coins()`` and THEN marks the collected
# ones dead. The order matters.
#
# If your saved file is missing fields, check that ``capture_state``
# names every field on the dataclass. Forgetting one means the on-disk
# value is the dataclass default forever.
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    sys.exit(main())
