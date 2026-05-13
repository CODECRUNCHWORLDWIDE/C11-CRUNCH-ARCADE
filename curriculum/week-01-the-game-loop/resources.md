# Week 1 — Resources

Every resource on this page is **free** and **publicly accessible**. No paywalled books, no proprietary PDFs. If a link breaks, please open an issue.

## Required reading (work it into your week)

- **Pygame — Getting started**: <https://www.pygame.org/wiki/GettingStarted>
- **Pygame — `pygame.display`**: <https://www.pygame.org/docs/ref/display.html>
- **Pygame — `pygame.event`**: <https://www.pygame.org/docs/ref/event.html>
- **Pygame — `pygame.time`** (this is where `Clock` lives): <https://www.pygame.org/docs/ref/time.html>
- **Pygame — `pygame.key`**: <https://www.pygame.org/docs/ref/key.html>
- **Pygame — `pygame.draw`** (skim only — we use `circle` and `rect` this week): <https://www.pygame.org/docs/ref/draw.html>

## The classic essays — game-loop literature

You will not invent the patterns we cover; people have been thinking about this since the 1970s. Read the canon.

- **Bob Nystrom — *Game Programming Patterns*** (free online edition):
  - [Game Loop](https://gameprogrammingpatterns.com/game-loop.html) — required this week.
  - [Update Method](https://gameprogrammingpatterns.com/update-method.html) — also required.
  - The rest of the book is paywalled in print but **the entire web edition is free**.
- **Glenn Fiedler — Fix Your Timestep!** — the canonical essay on fixed-timestep simulation:
  <https://gafferongames.com/post/fix_your_timestep/>
  Skim it this week. Re-read it Week 2 when we cover physics.

## Pygame tutorials worth your time

Most Pygame tutorials online are old, copy-pasted, or written for Pygame 1.x. These are the ones we recommend in 2026:

- **Real Python — *Make a 2D Side-Scroller Game With Pygame*** (free article):
  <https://realpython.com/pygame-a-primer/>
- **Pygame's own tutorial — *Line by Line Chimp*** (somewhat dated but the canonical first walkthrough):
  <https://www.pygame.org/docs/tut/ChimpLineByLine.html>
- **DaFluffyPotato** on YouTube — the most respected indie Pygame channel; pixel-art platformer focus:
  <https://www.youtube.com/@DaFluffyPotato>
- **Clear Code** on YouTube — long-form Pygame tutorials, very methodical:
  <https://www.youtube.com/@ClearCode>

## The Coding Train

Daniel Shiffman's videos are JavaScript / p5.js, **not Pygame**, but his explanation of the game loop, vectors, and physics is unmatched. Watch them for the ideas, then implement in Python.

- **The Coding Train channel**: <https://thecodingtrain.com/>
- **The Nature of Code** (free book + videos) — chapters 1–3 cover vectors, forces, and oscillation, which is most of what a 2D game needs:
  <https://natureofcode.com/>

## Official Python docs (you'll bounce here from time to time)

- **`time` module** (`time.perf_counter` is the gold standard for measuring elapsed time):
  <https://docs.python.org/3/library/time.html>
- **`math` module**:
  <https://docs.python.org/3/library/math.html>

## Other engines — same loop, different syntax

In Week 8 you'll switch to Godot. The loop is the same; the names change. Bookmark these now.

- **Godot — `_process(delta)`**:
  <https://docs.godotengine.org/en/stable/getting_started/step_by_step/scripting_first_script.html>
- **Godot — `_physics_process(delta)`** (the fixed-timestep version):
  <https://docs.godotengine.org/en/stable/tutorials/scripting/idle_and_physics_processing.html>
- **Unity — `Update()` vs `FixedUpdate()`** (for context only — we do not teach Unity in C11):
  <https://docs.unity3d.com/Manual/ExecutionOrder.html>

## Free books (chapter-level, not whole books)

- **Al Sweigart — *Making Games With Python & Pygame*** (free PDF, slightly dated but solid foundations):
  <https://inventwithpython.com/pygame/>
- **Al Sweigart — *Invent Your Own Computer Games With Python***:
  <https://inventwithpython.com/invent4thed/>
- **The Nature of Code** (already linked above):
  <https://natureofcode.com/>

## Asset libraries (we'll use these for years)

You don't need art this week — circles and rectangles only — but it's worth bookmarking now.

- **Kenney.nl** — public-domain (CC0) game-asset packs, the default for everyone in this course:
  <https://kenney.nl/>
- **OpenGameArt.org** — community-uploaded; check each asset's licence:
  <https://opengameart.org/>
- **itch.io free assets**: <https://itch.io/game-assets/free>

## Tools you'll install this week

- **Python 3.11 or newer**: <https://www.python.org/downloads/>
- **Pygame (vanilla, version 2.5 or newer)**: `pip install pygame`
- **A code editor**: VS Code or PyCharm Community Edition — both free.

## Glossary cheat sheet

Keep this open in a tab.

| Term | Plain English |
|------|---------------|
| **Game loop** | The infinite loop that runs your game. Input, update, render, repeat. |
| **Tick** | One iteration of the game loop. Often used interchangeably with "frame". |
| **Frame** | One redraw of the screen. At 60 fps you produce 60 frames per second. |
| **Frame rate** | How often you redraw — `fps`, frames per second. |
| **Simulation rate** | How often you update the game world. Sometimes equal to frame rate; sometimes not. |
| **Delta time (dt)** | The wall-clock seconds elapsed since the last frame. Used to scale movement. |
| **Fixed timestep** | A simulation step of constant length, decoupled from the render rate. The right way to do physics. |
| **VSync** | Synchronisation of frame presentation with the monitor's refresh. Prevents tearing; caps your fps. |
| **Frame budget** | The time you have per frame. At 60 fps, ~16.6 ms. At 144 fps, ~6.9 ms. |
| **Event queue** | An OS-managed list of events (input, resize, quit) you must drain every frame. |
| **Surface** (Pygame) | A 2D pixel buffer. The "screen" is a Surface, every sprite image is a Surface. |
| **`display.flip()`** | Hand the back-buffer to the OS to present on screen. |

---

*If a link 404s, please [open an issue](https://github.com/CODE-CRUNCH-CLUB) so we can replace it.*
