# Week 3 — Exercises

Short, focused drills. Each one should take 30–45 minutes. Do them in order; later ones build on earlier ones. The point this week is *feel*, not new mechanics — you'll keep using your Week 2 brick-breaker pattern with small additions.

## Index

1. **[Exercise 1 — Add Three Juice Touches](./exercise-01-add-three-juice-touches.py)** — a single Coin-Pink square that grows screen shake, particles, and a sound cue when you click it. The smallest possible "juice on demand" sandbox. (~35 min)
2. **[Exercise 2 — Screenshake and Particles](./exercise-02-screenshake-and-particles.py)** — a bouncing ball that triggers shake and a particle burst on every wall hit. Decay handled cleanly. (~40 min)
3. **[Exercise 3 — Tune the Feel](./exercise-03-tune-the-feel.py)** — runtime sliders for shake magnitude, particle count, particle decay. Playtest your own values. (~45 min)

## How to work the exercises

- Read the prompt at the top of each file. Skim, don't memorise.
- **Type the code yourself.** Do not copy-paste from the lecture notes. Muscle memory is the entire point of these drills.
- Run it. See the output. Read the error if it crashed.
- If you get stuck for more than 10 minutes, scroll to the `HINT` block at the bottom of the file. It is commented out for a reason — peeking early stunts the learning.
- Verify each `.py` compiles with `python -m py_compile exercise-XX-name.py` before declaring it done.
- For Exercise 1, you'll need a short `.wav` file. The exercise tells you where to get one (or how to skip it gracefully).

## Before you start

Week 2's venv is fine. If you wiped it:

```bash
python -m venv .venv
source .venv/bin/activate    # or: .venv\Scripts\activate on Windows
pip install pygame
```

Confirm Pygame works with `python -c "import pygame; print(pygame.version.ver)"`. You want `2.5.x` or newer.
