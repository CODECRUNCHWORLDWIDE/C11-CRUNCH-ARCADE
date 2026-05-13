# Week 1 Homework

Six practice problems that revisit the week's topics. The full set should take about **6 hours** in total. Work in your Week 1 Git repository so each problem produces at least one commit you can point to later.

Each problem includes:

- A short **problem statement**.
- **Acceptance criteria** so you know when you're done.
- A **hint** if you get stuck.
- An **estimated time**.

---

## Problem 1 — Measure your real frame rate

**Problem statement.** Take `exercise-02-moving-circle.py` and extend it to **render the current fps on screen** using `pygame.font`. The number should update at most twice per second so it isn't a strobing eye-stab. Also render the last frame's elapsed milliseconds.

**Acceptance criteria.**

- A file `homework/p1_fps_overlay.py` exists and runs.
- The window shows the moving circle plus an overlay in the top-left like `fps: 60.0   frame: 4.2 ms`.
- The overlay is rendered in a system font (Pygame's default font is fine — `pygame.font.SysFont(None, 24)`).
- The number is updated every 0.5 seconds, not every frame.
- Code is committed.

**Hint.** `pygame.font.init()` is called by `pygame.init()` for you. `font.render(text, True, colour)` returns a `Surface` you blit with `screen.blit(surf, (10, 10))`. Use a small accumulator: add `dt` each frame, when it crosses 0.5 s recompute and reset.

**Estimated time.** 45 minutes.

---

## Problem 2 — The "speed slider"

**Problem statement.** Take `exercise-03-keyboard-input.py` and bind the keys `1` through `5` to five different player speeds: 100, 200, 300, 500, and 800 px/s. While the player holds the number, the speed switches; on release, it stays at the last selected speed. Print to the terminal whenever the speed changes.

**Acceptance criteria.**

- A file `homework/p2_speed_slider.py` exists.
- The circle's speed switches when the player presses 1–5.
- Movement still uses delta time — the circle should travel an honest 100 px in 1 second at the lowest setting.
- The console prints `[speed] 100 px/s` (etc.) on change.
- Code is committed.

**Hint.** Use `pygame.KEYDOWN` and a `dict` mapping `pygame.K_1`..`pygame.K_5` to the speed values. This is one-shot per press, so `KEYDOWN` is right; do NOT use `get_pressed` here.

**Estimated time.** 30 minutes.

---

## Problem 3 — Two circles, one window

**Problem statement.** Two independent circles in one window. Circle A moves at 200 px/s, bouncing horizontally only (you can ignore vertical bouncing). Circle B uses WASD with the rules from Exercise 3. Different colours so you can tell them apart.

**Acceptance criteria.**

- A file `homework/p3_two_circles.py` exists.
- Two circles visible at the same time, never interfering with each other's state.
- Each circle's position is its own `Vector2`, not a shared global.
- The bouncing circle correctly reverses x-velocity at both edges.
- Code is committed.

**Hint.** You're not required to write a class yet, but if you find yourself copying `pos`, `vel`, `radius` for each circle you're a few keystrokes away from a `Ball` dataclass. Go ahead and write one — it's good practice for next week.

**Estimated time.** 1 hour.

---

## Problem 4 — Frame-budget report

**Problem statement.** Write a 250–400 word note at `notes/frame-budget.md` answering:

1. What is the frame budget at 30 fps? At 60 fps? At 120 fps? At 144 fps? Show the math.
2. Open `htop` / Activity Monitor / Task Manager while running your moving-circle program. What does it show your process consuming, in CPU and memory? Is that what you expected?
3. From the per-frame `ms` printout in Exercise 2, what was your average frame time? Where in the loop (input / update / render / present) do you think it was spent? You don't have to be exactly right — articulate your guess.
4. Name two things that would push you toward the 16.6 ms ceiling. Two that would push you over it. (Examples from the lecture or your own.)

**Acceptance criteria.**

- File at `notes/frame-budget.md`, 250–400 words, four numbered sections.
- Each section addresses the question in its own paragraph.
- Math is shown for question 1 (`1/30 = 33.3 ms`, etc.).
- File is committed.

**Hint.** This is reflective writing, not a test. Be honest about what you don't know yet. Future-you reading this after Week 6 will thank you.

**Estimated time.** 45 minutes.

---

## Problem 5 — Compare Pygame, Godot, Unity loops in code

**Problem statement.** Write `notes/loop-comparison.md` showing the **same logical behaviour** (move a sprite right at 200 px/s) in three engines:

1. Pygame (your real working code).
2. Godot 4 GDScript (pseudo-code is fine; you don't have to install Godot yet).
3. Unity C# (also pseudo-code; we don't teach Unity but this is one comparison).

For each, highlight where `delta` enters the math. End with a one-paragraph reflection: which one would you reach for tomorrow, and why?

**Acceptance criteria.**

- File at `notes/loop-comparison.md`, three short code blocks (10 lines each), each with a one-paragraph explanation.
- Each code block clearly shows the `delta` parameter being multiplied by speed.
- Final paragraph (50–100 words) defends a preference.
- File is committed.

**Hint.** Godot docs: <https://docs.godotengine.org/en/stable/getting_started/step_by_step/scripting_first_script.html>. Unity reference: <https://docs.unity3d.com/Manual/ExecutionOrder.html>. Borrow the syntax; you don't have to *run* them.

**Estimated time.** 1 hour.

---

## Problem 6 — Reflection essay

**Problem statement.** Write a 300–400 word reflection at `notes/week-01-reflection.md` answering:

1. What surprised you most about how the game loop works?
2. If you had to teach Lecture 1 in your own words to a friend in 2 minutes, what would you say?
3. What's the first game you'd want to clone for Week 2's brick-breaker exercise — and which existing game from your childhood does the bounce most remind you of?
4. What's one thing you'd want to learn next that this week didn't cover?

**Acceptance criteria.**

- File at `notes/week-01-reflection.md`, 300–400 words.
- Each numbered question addressed in its own paragraph.
- File is committed.

**Hint.** Be honest. Nobody is grading this. The two minutes of writing here saves you 30 minutes of self-doubt in week 6.

**Estimated time.** 30 minutes.

---

## Time budget recap

| Problem | Estimated time |
|--------:|---------------:|
| 1 | 45 min |
| 2 | 30 min |
| 3 | 1 h 0 min |
| 4 | 45 min |
| 5 | 1 h 0 min |
| 6 | 30 min |
| **Total** | **~4 h 30 min** |

That's under the 6-hour weekly budget — the rest is for fixing the bugs you'll create. You will create them. That is the work.

When you've finished all six, push your repo and open the [mini-project](./mini-project/README.md).
