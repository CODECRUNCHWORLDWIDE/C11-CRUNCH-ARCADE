# C11 · Crunch Arcade — Syllabus

**12 weeks · ~36 hrs/week intensive (or scaled) · C1 graduate → ships a polished 2D Godot game**

---

## Program at a glance

| Phase | Weeks | Outcome |
|-------|-------|---------|
| **Phase 1 — The Game Loop** | 01 – 03 | Pygame from scratch, collisions, scoring |
| **Phase 2 — Game Feel** | 04 – 06 | Tilemaps, state machines, animation, juice |
| **Phase 3 — Godot 4** | 07 – 09 | Nodes, scenes, signals, GDScript |
| **Phase 4 — Polish & Ship** | 10 – 12 | Audio, save states, playtest, itch.io |

---

## Weekly breakdown

**Week 1 — The game loop.** Input/update/render. Delta time. Frame rate vs simulation rate. Drawing in Pygame.

- *Mini-project:* A moving circle that respects delta time and reads keyboard input.

**Week 2 — Collisions & physics-lite.** AABB collision. Velocity, acceleration, gravity. The bouncing-ball problem.

- *Mini-project:* Brick-breaker — paddle, ball, bricks, score.

**Week 3 — Game design vocabulary.** What makes a game *feel* good vs feel bad. Game-feel essays. The Doug Church four lenses (qualitative).

- *Mini-project:* Take your Week-2 brick-breaker and add three "feel" touches (screen shake, particle, sound cue, etc.).

**Week 4 — Tilemaps & levels.** Loading levels from files (CSV, JSON, Tiled). Camera follow. Off-screen culling.

- *Mini-project:* A 2D platformer prototype with three loadable levels.

**Week 5 — State machines for characters.** Hand-rolled FSM. Idle / run / jump / fall / hurt. Why state machines beat nested ifs.

- *Mini-project:* A player character with at least four states and clean transitions.

**Week 6 — Animation & juice.** Sprite-sheet animation. Tweening. Easing curves. The "before/after" juice comparison.

- *Mini-project:* Add animation + juice to your Week-5 character.

**Week 7 — Save & load.** JSON save state. Versioning your save format. Migration when fields change.

- *Mini-project:* Save and reload the player's position, score, and unlocks.

**Week 8 — Hello, Godot 4.** Nodes, scenes, signals. GDScript essentials. Why GDScript reads like Python.

- *Mini-project:* Re-build the Week-1 moving circle in Godot.

**Week 9 — Porting a Pygame project to Godot.** Take one of your earlier prototypes and re-implement it in Godot. Notice what Godot makes easier and what Pygame did more cleanly.

- *Mini-project:* The platformer prototype, but in Godot 4.

**Week 10 — Audio.** Sound effects vs music. Audio buses. Triggering on events. Mixing. Loudness.

- *Mini-project:* Three SFX, one looping track, master/SFX/music buses correctly routed.

**Week 11 — Playtesting.** Five testers. Observation protocols. Asking the right questions. Not over-fitting to one person's feedback.

- *Mini-project:* A playtest report with three changes applied.

**Week 12 — Capstone — ship it.** A small polished game (15–20 min gameplay), packaged for at least two platforms, with an itch.io page and a 30-second trailer.

- *Capstone:* Public itch.io URL + repo + trailer + post-mortem.

---

## Weekly load

| Component | hrs/wk |
|-----------|------:|
| Lectures / readings | 6 |
| Hands-on prototype building | 8 |
| Game-feel challenges | 4 |
| Quiz | 3 |
| Homework | 6 |
| Mini-project / capstone polish | 7 |
| Self-study | 2 |
| **Total** | **36** |

---

## License

GPL-3.0.
