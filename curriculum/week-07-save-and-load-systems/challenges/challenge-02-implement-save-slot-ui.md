# Challenge 2 — Implement a Save-Slot UI

> **Format:** Pygame code. ~2 hours.
> **Deliverable:** A standalone Pygame program `slot_ui.py` plus three example save files.
> **Estimated time:** 2 hours.

This challenge is the UI counterpart to the mini-project's save layer. You build the **save-slot selector** — the screen that appears when the player chooses "Save" or "Load" from the pause menu and is offered three numbered slots.

The mini-project will integrate this UI; this challenge builds it as a standalone widget so you can iterate without the rest of the game in the way.

## What you build

A 600×400 Pygame window that:

1. **Reads** four files from a `saves/` folder: `slot1.json`, `slot2.json`, `slot3.json`, and `autosave.json`. Each file has the shape from Lecture 1 §4 (`schema_version`, `timestamp_iso`, `player_x`, `player_y`, `current_level`, `playtime_seconds`, ...). Missing files are shown as empty slots.
2. **Renders** four rows — three numbered slots plus the autosave at the bottom. Each row shows:
   - The slot number (or "Autosave").
   - The timestamp (relative — "3 days ago" — or ISO, your choice).
   - The level name.
   - The play-time (`HH:MM`).
   - "Empty" if the file is missing.
3. **Highlights** the currently selected slot. **Up/Down** arrows move the selection.
4. **Confirms overwrites.** When the player presses **S** to save into an occupied slot, a modal dialog appears: "Overwrite slot 2? [Y/N]". Yes confirms; No cancels.
5. **Loads silently.** When the player presses **L** to load from a non-empty slot, the slot's payload is written to a file `last_loaded.json` (as a stand-in for "the game now restores from this slot") and the UI flashes "loaded slot 2."
6. **Shows the autosave** as read-only — it is in the list but cannot be *saved into* (only the game's autosave path writes to it). Pressing **S** on the autosave row plays a denied beep / shows a status message.
7. **Quits cleanly** with ESC.

## Acceptance criteria

- [ ] A file `slot_ui.py` exists and runs with `python slot_ui.py`.
- [ ] `python -m py_compile slot_ui.py` succeeds.
- [ ] On first run, the UI creates a `saves/` directory if it does not exist.
- [ ] The UI handles all four files gracefully when missing, malformed, or empty.
- [ ] The selection moves with Up/Down. Selection wraps (Up from slot 1 goes to autosave; Down from autosave goes to slot 1).
- [ ] Pressing **S** on an empty slot writes a synthetic save (you provide the contents — just demonstrate the write path).
- [ ] Pressing **S** on an occupied slot opens an "Overwrite? [Y/N]" modal. Yes overwrites; No cancels.
- [ ] Pressing **L** on an occupied slot writes the slot's payload to `last_loaded.json` and shows a status flash.
- [ ] Pressing **L** on an empty slot shows "slot empty" and does nothing.
- [ ] Pressing **S** on the autosave row is denied; "autosave is read-only" status flash.
- [ ] The HUD shows the current keybindings.

## Design notes

This is a small **state machine** (your Week-5 muscle memory). The UI has three states:

```
                ┌────────────────┐
                │  BROWSING      │
                │  (default)     │
                └───────┬────────┘
                        │
            Up/Down: move cursor
            S on occupied slot: ─────► CONFIRM_OVERWRITE
            S on empty slot:    write save, stay
            L on occupied slot: load, stay
            L on empty slot:    deny, stay

                ┌────────────────┐
                │ CONFIRM_OVERWRITE│
                └───────┬────────┘
                        │
            Y: write save, → BROWSING
            N: cancel, → BROWSING
            ESC: cancel, → BROWSING
```

Implement the FSM with the same `IState` / `enter` / `update` / `handle_event` / `exit` pattern from Week 5. The discipline is the same; the *content* is a UI rather than a player.

## Rendering hints

- Use `pygame.font.SysFont(None, 24)` for slot labels and `pygame.font.SysFont(None, 18)` for the smaller text. The system font is fine for a debug UI.
- The selected slot draws with a coloured rectangle behind its row. Coin Pink (`(236, 72, 153)`) is the C11 brand accent.
- The "Overwrite?" modal is a centred dark-grey rectangle with white text. Around 300×100 px.
- Status flashes (top-right corner) live for 30 frames after firing.

## Format hints

A slot file looks like this:

```json
{
  "schema_version": 1,
  "timestamp_iso": "2026-05-12T19:42:11",
  "player_x": 384.5,
  "player_y": 192.0,
  "current_level": "Throne Room",
  "playtime_seconds": 1247.3
}
```

Render `playtime_seconds` as `HH:MM` (e.g. 1247 seconds → "00:20"). Render `timestamp_iso` as either the ISO string (simplest) or as "3 days ago" using a small helper:

```python
from datetime import datetime

def relative_time(iso: str) -> str:
    """Render a timestamp as 'just now', '5 min ago', '2 days ago'."""
    try:
        then = datetime.fromisoformat(iso)
    except ValueError:
        return iso  # unparseable; show as-is
    delta = (datetime.now() - then).total_seconds()
    if delta < 60:
        return "just now"
    if delta < 3600:
        return f"{int(delta / 60)} min ago"
    if delta < 86400:
        return f"{int(delta / 3600)} hr ago"
    return f"{int(delta / 86400)} days ago"
```

## What to skip

- Mouse input. Keyboard only. Mouse is welcome as a stretch.
- Animations / tweens on the cursor. Static highlighting is fine.
- The actual *game* connecting to this UI. The mini-project does the wiring. This challenge ends at `last_loaded.json`.
- Atomic writes, backup chains, checksums. The mini-project covers them. This challenge is the *UI*, not the persistence layer.

## Stretch goals

If you finish early:

- Add a **delete confirmation** flow. Pressing **D** on an occupied slot opens "Delete slot 2? [Y/N]" — same FSM pattern as overwrite.
- Add a **thumbnail**. Each save stores a 64×36 base64-encoded PNG (you fake it; the mini-project's stretch goal makes it real). Render the thumbnail next to the slot.
- Add a **sort-by-time** option. The slots stay in fixed numerical order, but a flag at the top of the screen sorts by most-recently-saved instead. Press **T** to toggle.
- Make the autosave row visually distinct — different colour band, italic label, an "auto" badge.

## What "done" looks like

You can:

1. Launch the UI.
2. See three empty slots and an empty autosave row.
3. Press **S** on slot 1 — a synthetic save is written. The slot now shows a timestamp and "playtime 00:00."
4. Press **Down**, **Down** to slot 3.
5. Press **S** — the slot fills.
6. Press **Up** back to slot 1.
7. Press **S** again — the "Overwrite?" modal appears.
8. Press **Y** — the modal closes; the slot's timestamp updates.
9. Press **L** — `last_loaded.json` is written; status flashes "loaded slot 1".
10. Press **Down** repeatedly until you reach the autosave row.
11. Press **S** — status flashes "autosave is read-only".
12. Press **ESC** — the window closes cleanly.

## Why this matters

The save UI is the most-touched piece of out-of-game UI in any indie title. Every player who ever saves anything in your game will see this screen. It must be *fast* (no animation gates the input), *legible* (the player needs to spot which slot is recent within two seconds), and *forgiving* (overwrites are reversible only if you backed up, which you did, per Lecture 3 §5).

This challenge is also the first time in C11 that you build a UI *as such* — a screen whose only job is to read state and offer choices. The next time you build one will be the pause menu in Week 8 and the settings screen in Week 11. The discipline is the same: an FSM, a list of rows, a cursor, a modal-confirmation pattern. Get the muscle memory now.

---

*Submit `slot_ui.py` plus the `saves/` folder you used for testing. The mini-project will reuse the file shape verbatim.*
