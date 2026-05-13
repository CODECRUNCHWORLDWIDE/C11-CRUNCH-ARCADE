# Week 1 — The Game Loop

Welcome to **C11 · Crunch Arcade**. Week 1 is unusual: we will not build "a real game" yet. We are going to write a window with a coloured rectangle and a moving circle, and we are going to obsess over the three lines of code that make it possible.

Most "how to make a game in Pygame" tutorials skip what we cover this week. They paste 80 lines of boilerplate, call it the "main loop", and never explain why it has to look that way. By Friday you will know exactly what every line of that boilerplate does, why the order of `input → update → render` is non-negotiable, and why moving a sprite "N pixels per frame" is a bug in every game ever shipped that hadn't heard of delta time.

There is no Godot yet. No physics. No collision. Just: a window, a clock, and a circle that moves at the same speed on a 60 Hz laptop and a 144 Hz desktop. Nail this and the rest of the course rests on solid ground. Skip it and Week 4's tilemap is going to feel like a black box.

## Learning objectives

By the end of this week, you will be able to:

- **Explain** the game-loop triple — input, update, render — and why that order is the only one that produces a game that responds to its player.
- **Open** a Pygame window from a blank file, pump the event queue, and shut it down cleanly so the OS doesn't think your app froze.
- **Distinguish** between *frame rate* (how often you redraw) and *simulation rate* (how often the game world updates), and explain why naively coupling them is a bug.
- **Implement** delta-time-based movement so a sprite traverses the screen in the same wall-clock time on a 60 Hz monitor and a 144 Hz monitor.
- **Read** keyboard input two ways — event-based (`KEYDOWN`) for one-shot actions, polled (`get_pressed`) for held movement — and pick the right one for the job.
- **Reason** about the frame budget: at 60 fps you have roughly 16.6 ms per frame, and every system you add eats into that.
- **Compare** Pygame's loop to the equivalent in other engines (Godot's `_process(delta)`, Unity's `Update()`) so when you switch in Week 8 it feels like a renaming exercise, not a rewrite.

## Prerequisites

This week assumes you have completed **C1 weeks 1–7** or have equivalent skill. Specifically:

- Comfortable in a terminal — you can `cd`, `ls`, run `python` and `pip install` something.
- You've written Python with classes, functions, and basic OOP.
- You can read a stack trace without panicking.
- You have Python 3.11 or newer installed.

If any of those are shaky, stop and review the relevant C1 week before continuing. C11 will not slow down.

## Topics covered

- Why a game is fundamentally a loop, not a script that ends.
- The input → update → render triple, in that order, forever.
- What the OS does when your process stops pumping events (hint: it puts a spinner on it).
- `pygame.init()`, `pygame.display.set_mode()`, `pygame.event.get()`, `pygame.display.flip()`, `pygame.quit()` — the five calls you need to know cold.
- Frame rate vs simulation rate — they are not the same thing and conflating them is the most common Pygame bug.
- The naive "N pixels per frame" bug, demonstrated on a borrowed 144 Hz monitor.
- Delta time: scale movement by elapsed real time so the game feels the same everywhere.
- `pygame.time.Clock` and how `tick(60)` actually works.
- Game-loop hygiene: clamping delta time so the "I tabbed out for 10 seconds" warp doesn't ruin a playtest.
- The fixed-timestep pattern for physics — touched on this week, deep dive in Week 2.
- Frame-budget thinking — what 16.6 ms feels like and what eats it.
- Keyboard input two ways: event polling for press/release, state polling for "is it held?".
- A high-level look at what `display.flip()` actually does on the GPU.
- The render-loop equivalent in other engines, for transferability.

## Weekly schedule

The schedule below adds up to approximately **36 hours**. Treat it as a target. Some sections click in 20 minutes, others take 3 hours. That is normal. Game-feel work is non-linear; if you find yourself tweaking the same magic number for an hour, that is not lost time — that is the work.

| Day       | Focus                                         | Lectures | Exercises | Challenges | Quiz/Read | Homework | Mini-Project | Self-Study | Daily Total |
|-----------|-----------------------------------------------|---------:|----------:|-----------:|----------:|---------:|-------------:|-----------:|------------:|
| Monday    | The loop, events, drawing                     |    2h    |    1.5h   |     0h     |    0.5h   |   1h     |     0h       |    0.5h    |     5.5h    |
| Tuesday   | Delta time, the Clock, the budget             |    2h    |    1.5h   |     1h     |    0.5h   |   1h     |     0h       |    0.5h    |     6.5h    |
| Wednesday | Keyboard input, WASD movement                 |    0h    |    1.5h   |     1h     |    0.5h   |   1.5h   |     1h       |    0h      |     5.5h    |
| Thursday  | Bouncing-ball challenge, polish               |    0h    |    1h     |     2h     |    0.5h   |   1h     |     2h       |    0.5h    |     7h      |
| Friday    | Mini-project deep work                        |    0h    |    0h     |     0h     |    0.5h   |   1.5h   |     2.5h     |    0.5h    |     5h      |
| Saturday  | Mini-project polish, quiz                     |    0h    |    0h     |     0h     |    0.5h   |   0h     |     2.5h     |    0h      |     3h      |
| Sunday    | Review, write up, push                        |    0h    |    0h     |     0h     |    0.5h   |   0h     |     2h       |    0h      |     2.5h    |
| **Total** |                                               | **4h**   | **5.5h**  | **4h**     | **3.5h**  | **6h**   | **10h**      | **2h**     | **35h**     |

## How to navigate this week

| File | What's inside |
|------|---------------|
| [README.md](./README.md) | This overview (you are here) |
| [resources.md](./resources.md) | Pygame docs, free Game Programming Patterns chapters, Coding Train videos |
| [lecture-notes/01-the-game-loop-and-why-it-exists.md](./lecture-notes/01-the-game-loop-and-why-it-exists.md) | What a game loop is and why every engine has one |
| [lecture-notes/02-delta-time-and-the-fixed-timestep.md](./lecture-notes/02-delta-time-and-the-fixed-timestep.md) | Why "N pixels per frame" is a bug, and what to do instead |
| [exercises/README.md](./exercises/README.md) | Index of short coding drills |
| [exercises/exercise-01-blank-window.py](./exercises/exercise-01-blank-window.py) | Open a Pygame window, fill it with a colour, quit cleanly |
| [exercises/exercise-02-moving-circle.py](./exercises/exercise-02-moving-circle.py) | A circle that crosses the screen using delta time |
| [exercises/exercise-03-keyboard-input.py](./exercises/exercise-03-keyboard-input.py) | Move the circle with WASD |
| [challenges/README.md](./challenges/README.md) | Index of weekly challenges |
| [challenges/challenge-01-bouncing-ball.md](./challenges/challenge-01-bouncing-ball.md) | A circle that bounces off all four edges, with a twist |
| [quiz.md](./quiz.md) | 10 multiple-choice questions |
| [homework.md](./homework.md) | Six practice problems for the week |
| [mini-project/README.md](./mini-project/README.md) | Full spec for the "Crunch Dot" moving-circle mini-game |

## Frame budget for this week

A reminder of what 60 fps actually means, in milliseconds. Every lecture in this course returns to this tile.

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

This week's project will not get anywhere near these numbers — a single circle on a 800×600 window has milliseconds of headroom to spare. But every week from now on, when something feels slow, you come back to this table and ask which row you blew past.

## Stretch goals

If you finish early and want to push further:

- Read Bob Nystrom's *Game Programming Patterns* chapter on the [Game Loop](https://gameprogrammingpatterns.com/game-loop.html) and the [Update Method](https://gameprogrammingpatterns.com/update-method.html) — both free online.
- Read Glenn Fiedler's classic [Fix Your Timestep!](https://gafferongames.com/post/fix_your_timestep/) essay. It is dense. Skim now, re-read after Week 2.
- Re-implement the moving circle in [Pyxel](https://github.com/kitao/pyxel) or [Arcade](https://api.arcade.academy/) and write a 200-word note on what felt different.
- Look at Godot's [`Node._process`](https://docs.godotengine.org/en/stable/classes/class_node.html#class-node-method-process) docs and identify the `delta` parameter — you'll meet it again in Week 8.
- Profile your loop with `cProfile` and find the hottest call. There's almost certainly one surprise in there.

## Voice rules for the week

- We do not say "easy." Games are not easy to make. We say "small" or "tractable."
- We distinguish a **prototype** (proves a mechanic works) from a **game** (mechanic + level design + audio + UX + polish).
- We credit asset authors by name. If you grab a sprite from [Kenney.nl](https://kenney.nl/), credit goes in the README.
- We trust playtest data over our own opinion. "Three of five testers paused at the same point" beats "I think it feels good."

## Up next

Continue to [Week 2 — Collisions & Physics-Lite](../week-02-collisions-and-physics-lite/) once you've pushed your mini-project to GitHub.

---

*If you find errors in this material, please open an issue or send a PR. Future learners will thank you.*
