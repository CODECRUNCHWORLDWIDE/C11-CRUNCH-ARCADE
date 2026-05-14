# Week 6 — Exercises

Short, focused drills. Each one should take 40–60 minutes. Do them in order; the third one assembles the first two on top of your Week-5 character. The point this week is *binding presentation to state*: animations, tweens, shake, and particles all hang off the FSM `enter()` and `exit()` hooks you wrote last week.

## Index

1. **[Exercise 1 — Sprite animation](exercise-01-sprite-animation.py)** — build a `SpriteSheet` loader and an `Animation` class from scratch. A procedurally-generated 4x3 sheet drives three clips (idle loop, run loop, jump-launch one-shot). The HUD shows the current clip, frame index, elapsed time, and whether the clip is `finished`. (~45-55 min)
2. **[Exercise 2 — Tween easing curves](exercise-02-tween-easing-curves.py)** — implement `lerp` and five easing curves (`linear`, `ease_in`, `ease_out`, `ease_in_out`, `ease_out_back`); plot each one across the top of the window; drive five tweened squares with each one. Press R to restart. (~40-50 min)
3. **[Exercise 3 — Add juice to Week-5 character](exercise-03-add-juice-to-week5-character.py)** — take the Week-5 four-state-plus-hurt player and add squash-and-stretch on jump and land, screen shake on landing and hit, dust particle bursts from the feet, a red-flash hit indicator, and stub sound cues fired from each FSM transition. The character is the same Coin-Pink rectangle; the diff is the feel. (~55-70 min — the code is short; the tuning is the work)

## How to work the exercises

- Read the prompt at the top of each file. Skim, don't memorise.
- **Type the code yourself.** Do not copy-paste from the lecture notes. Muscle memory is the entire point of these drills.
- Run it. See the output. Read the error if it crashed.
- If you get stuck for more than 20 minutes, scroll to the `HINT` block at the bottom of the file. It is commented out for a reason — peeking early stunts the learning.
- Verify each `.py` compiles with `python -m py_compile exercise-XX-name.py` before declaring it done.
- None of the exercises this week require external asset downloads. Exercise 1 generates a procedural sheet in code; Exercise 3 uses a coloured rectangle with juice on it (no sprite art). The mini-project is where you swap in real Kenney assets.

## Before you start

Week 5's venv is fine. If you wiped it:

```bash
python -m venv .venv
source .venv/bin/activate    # or: .venv\Scripts\activate on Windows
pip install pygame
```

Confirm Pygame works with `python -c "import pygame; print(pygame.version.ver)"`. You want `2.5.x` or newer.

## What you'll have at the end

- **Exercise 1:** a `SpriteSheet` + `Animation` + `Animator` triad that loads any grid-of-frames PNG, supports looping and one-shot clips, and is frame-rate-independent. You'll keep this exact code into the mini-project.
- **Exercise 2:** a `Tween` class and the five easing curves. The class drives every value-over-time effect in your future code: squash, fade, slide, shake-decay, score-pop.
- **Exercise 3:** a juice-pass template — `ScreenShake`, `ParticleField`, `SFX` stub, and the binding pattern of "`enter()` fires the polish, `exit()` stops the loops." You'll lift this *directly* into the mini-project on top of your Week-5 state machine.

By the end of Wednesday you have all three pieces. Thursday and Friday glue them into the mini-project — a Week-5 character with a real Kenney sprite sheet, real `.wav` SFX, and a before/after comparison video.

## A note on style

The exercises this week are *shorter than Week 5's* in code, *longer in tuning*. Juice is the kind of work that is mechanical to write and personal to dial in. If your land-squash feels too floaty after the first run, the fix is not "more code." The fix is `SQUASH_LAND_DUR = 0.20` becomes `0.15`. Tune by feel; the file's `# JUICE` knobs are the tuning surface.

If at any point you find yourself wanting to add a sixth easing curve, or a particle emitter that can do bursts AND streams, or a screen-shake with Perlin-noise smoothing — *don't*, this week. Those are the stretch goals for the mini-project. The exercises drill the *baseline*; the project earns the polish.
