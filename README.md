# C11 · Crunch Arcade — Game Development

> A free, open-source **12-week game-development track** for engineers (mostly Python users) who want to ship a small game they're proud of. From the game-loop primitives in pure Pygame to a polished 2D Godot game with sound, save states, and a deploy you can share with friends.

[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](LICENSE)
[![Python · Pygame · Godot](https://img.shields.io/badge/stack-Python_·_Pygame_·_Godot-DB2777.svg)](#stack)
[![Built in the open](https://img.shields.io/badge/built-in%20the%20open-DB2777.svg)](https://github.com/CODECRUNCHWORLDWIDE)

C11 is **dedicated game-dev**. It used to share a code with C# Foundations; that course is now [C9 · Crunch Sharp](../C9-CRUNCH-SHARP/). C11 focuses on 2D indie game development with Python (Pygame) for the fundamentals and Godot 4 (GDScript) for the polished capstone.

We don't teach Unity here. Unity is excellent and lives under [C9 · Crunch Sharp](../C9-CRUNCH-SHARP/) where the C# ecosystem belongs. Choose the right one for your career goal.

---

## Pathway summary

- **Full-time:** 12 weeks · ~36 hrs/week · ~432 hours
- **Working-engineer pace:** 6 months · ~18 hrs/week
- **Evening / undergraduate pace:** 1 year · ~9 hrs/week

See [`SYLLABUS.md`](SYLLABUS.md).

---

## What you will be able to do at the end of 12 weeks

- **Implement a game loop** from scratch: input, update, render, in the right order, at the right rate.
- **Reason about delta-time** so your game feels the same on a 60 Hz laptop and a 144 Hz desktop.
- **Build collisions** that don't lie: AABB, swept tests, separating-axis basics.
- **Animate sprites** properly: state machines, keyframes, easing.
- **Design tilemaps** and load them from data files, not hardcoded arrays.
- **Manage scenes** — title, gameplay, pause, game-over — with clean transitions.
- **Build a Godot 4 project** with nodes, scenes, signals, GDScript.
- **Ship a small game** end-to-end with sound effects, music, persistent save state, and a packaged build.
- **Playtest with structure** — five testers, three behaviors observed, two changes applied.
- **Read other people's small games** without intimidation.

---

## Who this is for

- **C1 graduate** who wanted to make games the whole time.
- **Self-taught Python user** ready for something more visual.
- **Computer-science student** who wants to apply concepts (state machines, math, data structures) to something tangible.
- **Game-jam aspirant** preparing to ship under deadline.

Not for: people targeting AAA gamedev jobs (do C9 + Unity, or learn Unreal in C++; we don't teach those at scale), nor people focused on game *art* over game programming (this is the engineering side).

---

## Prerequisites

- **C1 Weeks 1–7** (Python, OOP).
- Comfortable terminal + git.
- A computer that can run Godot 4 (~modern; 4GB RAM minimum).
- Patience. Game polish is 80% of the work and 0% of the fun in the first hour.

---

## What you ship

By the end of the 12 weeks, your `crunch-arcade-portfolio-<yourhandle>` GitHub repo contains:

1. A **pure-Python game loop** drawing a moving circle (Week 1).
2. A **paddle / ball / bricks** game in Pygame with collision and scoring (Week 3).
3. A **2D platformer prototype** with a tilemap, jump physics, and one enemy (Week 5).
4. A **state-machine character** with idle / run / jump / hurt animations (Week 6).
5. A **save-load system** that survives a crash (Week 7).
6. A **Godot 4 port** of one of the earlier prototypes (Week 9).
7. A **sound-and-music integration** with at least three SFX and one looping track (Week 10).
8. A **playtest report** with five testers' notes and your three resulting changes (Week 11).
9. **Capstone:** a small polished 2D Godot game (15–20 minutes of gameplay), packaged for at least two platforms, with a public itch.io page (Week 12).

---

## Tools (all free, all open-source)

| Tool | Role |
|------|------|
| **Python 3.11+** | Foundations weeks |
| **Pygame** | Pure-Python game-loop work |
| **Pyxel / Arcade** *(optional)* | Mentioned as alternatives |
| **Godot 4** | The polished capstone |
| **GDScript** | Godot's scripting language (Python-like) |
| **Aseprite community** *(free)* or **Krita** *(free)* | Pixel art |
| **LMMS · Bosca Ceoil · ChipTone** | Free audio tools |
| **Tiled** | Free tilemap editor |
| **itch.io** | Free distribution platform |
| **OBS Studio** | Recording playtests / trailers |

Optional but useful: **a controller** (Xbox / 8BitDo) for testing real input. Most laptops have keyboard input; controllers reveal bugs.

---

## On art assets

Game polish needs art. C11 is not an art course. For all the curriculum's exercises and the capstone, we point at **public-domain or CC0 asset libraries**:

- **Kenney.nl** — extensive CC0 game-asset packs: <https://kenney.nl/>
- **OpenGameArt.org** — community-uploaded; check each asset's license.
- **itch.io free assets** — a wide community library; check each license.

Do NOT use copyrighted assets (Nintendo sprites, official Pokémon art, etc.) even "just to test." It feels safe; it isn't. Use Kenney's free packs as a default.

---

## Next track after C11

- **[C12 · Crunch 3D](../C12-CRUNCH-3D/)** — for 3D visualization and technical art.
- **[C9 · Crunch Sharp](../C9-CRUNCH-SHARP/)** — if your future is Unity / C# game dev.
- **[C16 · Crunch Pro Web Backend](../C16-CRUNCH-PRO-WEB-BACKEND/)** — if your game grows into a multiplayer service.

---

## License

GPL-3.0.

---

*C11 is part of the Code Crunch open-source curriculum.* [Master catalog ↗](../MASTER-CURRICULUM.md) · [Brand family ↗](../../assets/brand/BRAND-FAMILY.md)


---

<!-- CCWW:AUTO-INDEX:START — generated by scripts/restructure_course_repos.py; edit ABOVE this marker -->

## Course at a glance

| Section | Count |
| --- | --- |
| Curriculum entries | 13 |
| Projects | 0 |
| Past sessions | 1 |

## Curriculum

- [SYLLABUS](curriculum/SYLLABUS.md)
- [week 01 the game loop](curriculum/week-01-the-game-loop/README.md)
- [week 02 collisions and physics lite](curriculum/week-02-collisions-and-physics-lite/README.md)
- [week 03 game design vocabulary](curriculum/week-03-game-design-vocabulary/README.md)
- [week 04 tilemaps and levels](curriculum/week-04-tilemaps-and-levels/README.md)
- [week 05 state machines](curriculum/week-05-state-machines/README.md)
- [week 06 animation and juice](curriculum/week-06-animation-and-juice/README.md)
- [week 07 save and load systems](curriculum/week-07-save-and-load-systems/README.md)
- [week 08 sound and music systems](curriculum/week-08-sound-and-music-systems/README.md)
- [week 09 multiplayer fundamentals](curriculum/week-09-multiplayer-fundamentals/README.md)
- [week 10 shaders and visual effects](curriculum/week-10-shaders-and-visual-effects/README.md)
- [week 11 save systems and serialization](curriculum/week-11-save-systems-and-serialization/README.md)
- [week 12 capstone ship a complete game](curriculum/week-12-capstone-ship-a-complete-game/README.md)

## In this course

- **Community** — [community/](community/)
- **Curriculum** — [curriculum/](curriculum/)
- **Projects** — [projects/](projects/)
- **Resources** — [resources/](resources/)
- **Past sessions** — [past-sessions/](past-sessions/)

<!-- CCWW:AUTO-INDEX:END -->
