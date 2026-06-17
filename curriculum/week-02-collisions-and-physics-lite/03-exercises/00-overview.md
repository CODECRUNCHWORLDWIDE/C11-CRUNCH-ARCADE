# Week 2 — Exercises

Short, focused drills. Each one should take 30–45 minutes. Do them in order; later ones build on earlier ones.

## Index

1. **[Exercise 1 — Two Rects Collide](./exercise-01-two-rects-collide.py)** — drag a Coin-Pink rectangle around with WASD. When it touches a Power-Up-Cyan rectangle, the second one turns red. Implement the test by hand, then verify with `Rect.colliderect`. (~35 min)
2. **[Exercise 2 — Bouncing Ball, Gravity Edition](./exercise-02-bouncing-ball-gravity.py)** — a ball that falls under gravity and bounces, with a restitution coefficient you can tune and a rest-threshold so it actually settles. (~40 min)
3. **[Exercise 3 — Platformer Floor](./exercise-03-platformer-floor.py)** — a controllable square that walks left/right with arrow keys, jumps with space, and lands on a static floor. The smallest possible platformer. (~45 min)

## How to work the exercises

- Read the prompt at the top of each file. Skim, don't memorise.
- **Type the code yourself.** Do not copy-paste from the lecture notes. Muscle memory is the entire point of these drills.
- Run it. See the output. Read the error if it crashed.
- If you get stuck for more than 10 minutes, scroll to the `HINT` block at the bottom of the file. It is commented out for a reason — peeking early stunts the learning.
- Verify each `.py` compiles with `python -m py_compile exercise-XX-name.py` before declaring it done. A clean compile is the minimum bar.

## Before you start

Last week's venv is fine. If you wiped it:

```bash
python -m venv .venv
source .venv/bin/activate    # or: .venv\Scripts\activate on Windows
pip install pygame
```

Confirm Pygame works with `python -c "import pygame; print(pygame.version.ver)"`. You want `2.5.x` or newer.
