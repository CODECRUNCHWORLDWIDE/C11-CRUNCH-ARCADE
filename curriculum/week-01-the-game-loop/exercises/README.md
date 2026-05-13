# Week 1 — Exercises

Short, focused drills. Each one should take 20–40 minutes. Do them in order; later ones build on earlier ones.

## Index

1. **[Exercise 1 — Blank Window](exercise-01-blank-window.py)** — open a Pygame window, fill it with a colour, close it cleanly. The first 17 lines that every game starts with. (~25 min)
2. **[Exercise 2 — Moving Circle](exercise-02-moving-circle.py)** — a circle that crosses the screen using delta time. Run it on a friend's machine too — it should look the same. (~30 min)
3. **[Exercise 3 — Keyboard Input](exercise-03-keyboard-input.py)** — move the circle with WASD, normalise the diagonal, clamp to the screen edges. (~35 min)

## How to work the exercises

- Read the prompt at the top of each file. Skim, don't memorise.
- **Type the code yourself.** Do not copy-paste from the lecture notes. Muscle memory is the entire point of these drills.
- Run it. See the output. Read the error if it crashed.
- If you get stuck for more than 10 minutes, scroll to the `HINT` block at the bottom of the file. It is commented out for a reason — peeking early stunts the learning.
- Only check the official solution after you've made it run. There are no solutions checked in; solutions live in forks and Gists from other learners. Search GitHub for `c11-week-01 site:github.com` after you've finished to compare.

## Before you start

```bash
python -m venv .venv
source .venv/bin/activate    # or: .venv\Scripts\activate on Windows
pip install pygame
```

Confirm Pygame works with `python -c "import pygame; print(pygame.version.ver)"`. You should see `2.5.x` or newer. If you see `1.9.x`, you're on an ancient install — upgrade.
