# C11 · Crunch Arcade — Brand Guide

> **Voice:** craft-shop, indie-dev, low-ego. The voice of someone who has shipped a small game and learned what's hard.
> **Feel:** pixel-tight, primary colors used sparingly, CRT-scanline texture as accent (never as decoration).

Extends the family brand. C11-specific overrides only.

---

## Identity

- **Full name:** Crunch Arcade — Game Development
- **Program code:** C11
- **Full title in copy:** *C11 · Crunch Arcade*
- **Tagline (short):** Ship a small game you're proud of.
- **Tagline (long):** A free, open-source twelve-week 2D game-development track with Python (Pygame) and Godot 4 — game loops, juice, audio, save states, and a real itch.io launch.
- **Canonical URL:** `codecrunchglobal.vercel.app/course-c11-arcade`
- **License:** GPL-3.0

---

## Where C11 diverges from the family palette

Inherits Ink/Parchment/Gold. Adds two restrained accents — **Coin Pink** (the C11 mark, level-up moments, achievement badges) and **Power-Up Cyan** (interactive widgets, "playable" buttons):

| Role | Name | Hex | Use |
|------|------|-----|-----|
| Accent | Coin Pink | `#DB2777` | The C11 mark, milestone callouts, "you shipped" indicators |
| Accent deep | Coin Pink deep | `#9D174D` | Hover |
| Accent | Power-Up Cyan | `#06B6D4` | Playable buttons, interactive embeds |
| Accent soft | Coin Pink soft | `#FBCFE8` | Background of achievement chips |

```css
:root {
  --coin:        #DB2777;
  --coin-deep:   #9D174D;
  --coin-soft:   #FBCFE8;
  --power-cyan:  #06B6D4;
}
```

### Typography

EB Garamond display, Lora body. **For UI chrome and any "in-game" labels, use a system pixel font** (DejaVu Sans Mono is a safe fallback if you don't ship a custom pixel font). Game-feel demands typography matches the game's scale — but the curriculum body remains in Lora/EB Garamond.

---

## Recurring page elements

### The "frame budget" tile

Every game-feel lecture includes a small budget breakdown for that frame at 60 fps:

```
┌─────────────────────────────────────────────────────────┐
│  FRAME BUDGET — 60 fps target                           │
│                                                         │
│  Input poll:       ~0.2 ms                              │
│  Update (sim):     ~2.0 ms                              │
│  Collision:        ~1.5 ms                              │
│  Render:           ~6.0 ms                              │
│  GPU + present:    ~4.0 ms                              │
│  Headroom:         ~3.0 ms                              │
│  ─────────────────────                                  │
│  Total:           ~16.6 ms / frame                      │
└─────────────────────────────────────────────────────────┘
```

Always mono. Always sums to ≤16.6 ms for 60 fps targets (8.3 ms for 120 fps).

### The juice-comparison strip

Almost every game-feel lecture has a side-by-side "before juice / after juice" GIF or video. Both label the same player action. The point is to make "juice" measurable, not vibes-based.

---

## Voice rules

- **No "easy."** Games are not easy to make.
- **Distinguish a prototype from a game.** A prototype proves a mechanic. A game does that + level design + audio + UX + polish.
- **Credit Kenney.** When using public-domain assets from kenney.nl, credit by name. Always.
- **No "AAA-killer" hype.** This track ships small games; we celebrate that.
- **Playtest data > opinion.** "Three of five testers paused at the same point" beats "I think it's confusing."

---

## Course page conventions

The course page (`course-c11-arcade.html`, future) uses parchment with a stylized CRT-scanline overlay on the hero (extremely subtle — 4% opacity). The 12-week ladder appears as a sequence of "stages" in the style of an arcade-game level select. Coin Pink accents on milestone deliverables.

---

*GPL-3.0. Fork freely.*
