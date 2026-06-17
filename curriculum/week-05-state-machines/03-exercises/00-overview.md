# Week 5 — Exercises

Short, focused drills. Each one should take 40–55 minutes. Do them in order; later ones build on earlier ones. The point this week is *state, not booleans* — you'll keep using the same Pygame loop pattern with the character's behaviour modes promoted from a tangle of flags into a real state machine.

## Index

1. **[Exercise 1 — FSM from nested ifs](./exercise-01-fsm-from-nested-ifs.py)** — refactor a 60-line tangle of nested `if`s into a hand-rolled FSM. Four states (`idle`/`run`/`jump`/`fall`), an `Enum` of events, a `TRANSITIONS` dict, and a four-phase update. The HUD prints the current state; the console logs every transition. (~40-50 min)
2. **[Exercise 2 — Character with states](./exercise-02-character-with-states.py)** — re-implement the same four-state player using the State pattern (one class per state, `enter`/`update`/`exit` lifecycle). Adds an `AirborneState` parent for `JumpState` and `FallState`, plus a fifth state, `HurtState`, triggered by walking into a spike on the floor. (~45-55 min)
3. **[Exercise 3 — State stack](./exercise-03-state-stack.py)** — implement a pushdown automaton and use it for top-level game flow: a Title state, a Gameplay state (a bouncing square), and a Pause overlay. Pausing is a *push*; unpausing is a *pop*; gameplay resumes from the exact frame it was suspended on. (~40-50 min)

## How to work the exercises

- Read the prompt at the top of each file. Skim, don't memorise.
- **Type the code yourself.** Do not copy-paste from the lecture notes. Muscle memory is the entire point of these drills.
- Run it. See the output. Read the error if it crashed.
- If you get stuck for more than 20 minutes, scroll to the `HINT` block at the bottom of the file. It is commented out for a reason — peeking early stunts the learning.
- Verify each `.py` compiles with `python -m py_compile exercise-XX-name.py` before declaring it done.
- None of the exercises this week require external assets (no sprite sheets, no `.wav` files, no PNG tilesets). The character is a coloured rectangle on purpose — the lecture is the state machine, not the art. (Week 6 paints the muscles.)

## Before you start

Week 4's venv is fine. If you wiped it:

```bash
python -m venv .venv
source .venv/bin/activate    # or: .venv\Scripts\activate on Windows
pip install pygame
```

Confirm Pygame works with `python -c "import pygame; print(pygame.version.ver)"`. You want `2.5.x` or newer.

## What you'll have at the end

- Exercise 1: a hand-rolled FSM with `State` / `Event` enums, a `TRANSITIONS` dict, and a four-phase update. You'll keep both the dict pattern and the four-phase shape.
- Exercise 2: a `State` base class and four-to-five concrete subclasses (`IdleState`, `RunState`, `JumpState`, `FallState`, `HurtState`). You'll lift these *directly* into the mini-project as a starting point.
- Exercise 3: a `GameState` base class and an `App` with a `stack: list[GameState]`. You'll use this exact pattern for the pause menu in the mini-project, the level-complete overlay in Week 6, and the dialog system in Week 10.

By the end of Wednesday you have all three pieces. Thursday and Friday glue them into the mini-project — a four-state player running on top of your Week 4 tilemap, with a working pause overlay.

## A note on style

The exercises in this week are deliberately *longer than Week 4's*. The State pattern is a class-heavy shape, and the boilerplate around `enter`/`update`/`exit` lookups is the whole point — you're feeling the surface area of the abstraction. If the class definitions feel verbose, that's the lesson: the State pattern *is* verbose for small machines, and the payoff is the verbosity scales linearly when the hand-rolled version scales quadratically. Trust the boilerplate.
