# Week 2 Homework

Six practice problems that revisit the week's topics. The full set should take about **6 hours** in total. Work in your Week 2 Git repository so each problem produces at least one commit you can point to later.

Each problem includes:

- A short **problem statement**.
- **Acceptance criteria** so you know when you're done.
- A **hint** if you get stuck.
- An **estimated time**.

---

## Problem 1 — Circle vs AABB collision

**Problem statement.** Extend `exercise-01-two-rects-collide.py`'s pattern to test a **circle** (the player) against a **rectangle** (the static target). Implement the clamp-and-distance algorithm from Lecture 1 §4 by hand. The static rectangle should turn red when the circle's edge enters it — not when the circle's *bounding rectangle* enters it.

**Acceptance criteria.**

- A file `homework/p1_circle_vs_aabb.py` exists and runs.
- The player is a 24-px-radius Coin-Pink circle controlled with WASD at 280 px/s.
- The static target is a 120x80 Power-Up-Cyan rectangle.
- The static rectangle turns red **only** when the circle's perimeter actually enters it — corner-grazes that miss the circle are correctly reported as no-hit.
- Code is committed.

**Hint.** Clamp the circle's centre into the rectangle (`max(rect.left, min(circle.x, rect.right))` for X, ditto Y). Then `distance_sq < radius_sq`. Lecture 1 §4 has the formula.

**Estimated time.** 45 minutes.

---

## Problem 2 — The corner case

**Problem statement.** Take your Problem 1 solution. Walk the circle into the **corner** of the rectangle very slowly. Compare to: walk the circle into the middle of the **top edge** very slowly. Both should report hit at the moment the perimeter crosses the rectangle.

Then change your code to use a naive AABB-vs-AABB test (the circle's bounding rect vs the rectangle). Walk the circle past the **corner** of the rectangle without actually touching it. The naive AABB will report a false hit; the circle-vs-AABB will not. Write a 200–300 word note in `homework/p2_corner_case.md` explaining what you saw and why.

**Acceptance criteria.**

- A file `homework/p2_corner_case.md` exists, 200–300 words.
- Describes the false-positive case in the corner.
- Explains why AABB-vs-AABB lies there (dead corner space) and why circle-vs-AABB tells the truth.
- File is committed.

**Hint.** Add a key (T) that toggles between the two tests in your Problem 1 code. Then write the comparison live.

**Estimated time.** 30 minutes.

---

## Problem 3 — Gravity-tuner sandbox

**Problem statement.** Take `exercise-02-bouncing-ball-gravity.py` and turn `GRAVITY_PX_PER_S2` and `RESTITUTION` into runtime-tunable parameters. Add an overlay listing both values; pressing `Q`/`A` raises/lowers gravity by 100, `W`/`S` raises/lowers restitution by 0.05. Print to the terminal on change.

**Acceptance criteria.**

- A file `homework/p3_gravity_tuner.py` exists.
- Q raises gravity by 100; A lowers by 100. Floor: 0. Ceiling: 4000.
- W raises restitution by 0.05; S lowers by 0.05. Floor: 0.0. Ceiling: 1.5 (yes, above 1 — try it).
- On change, print `[gravity] 1200`, `[restitution] 0.85`, etc.
- The HUD shows current values.
- Code is committed.

**Hint.** Use `pygame.KEYDOWN` for one-shot adjustments. Cap values with `max` / `min`. Cache the rendered HUD text and only re-render when a value changes — beginners blit a font surface every frame and it's an easy 1-2 ms saved.

**Estimated time.** 45 minutes.

---

## Problem 4 — Two balls, no walls

**Problem statement.** Two balls share an 800x600 window. Both bounce off the four walls (Week 1's challenge, basically). NEW: when the **two balls themselves** collide, both reflect off each other using the same circle-vs-circle test from Lecture 1 §4 and a velocity swap along the contact normal.

**Acceptance criteria.**

- A file `homework/p4_two_balls.py` exists.
- Two 18-px balls visible at all times.
- When they overlap, both reflect — the resulting motion looks like real billiard balls (not pacman-style pass-through, not stuck-together).
- Movement is delta-time correct.
- Code is committed.

**Hint.** The "two balls bounce off each other" velocity swap is more subtle than wall reflection. The simplest acceptable version, for equal masses:

```python
delta = b.pos - a.pos
distance_sq = delta.length_squared()
radii_sum = a.radius + b.radius
if distance_sq < radii_sum * radii_sum and distance_sq > 1e-9:
    normal = delta.normalize()
    # Velocity components along the contact normal.
    va = a.vel.dot(normal)
    vb = b.vel.dot(normal)
    if va - vb > 0:
        # They're moving apart already, ignore. Avoids re-collision.
        pass
    else:
        # Swap the normal-aligned components (equal-mass elastic collision).
        a.vel += (vb - va) * normal
        b.vel += (va - vb) * normal
        # Also separate them so they don't overlap next frame.
        overlap = radii_sum - distance_sq ** 0.5
        a.pos -= normal * (overlap / 2)
        b.pos += normal * (overlap / 2)
```

If that confuses you, do the easy version first: both reflect their *own* velocity (each ball treats the other like a wall). It's wrong but it's visible. Then upgrade to the swap above.

**Estimated time.** 1 hour 30 minutes.

---

## Problem 5 — Tunneling demo

**Problem statement.** Write `homework/p5_tunneling_demo.py` that intentionally produces a tunneling bug, then offer two keyboard toggles to "fix" it. The setup: one ball moving at 4000 px/s horizontally, a thin vertical wall 4 px wide in the middle of the screen.

- With **no fix**, the ball passes through the wall about half the time.
- Toggle `1` enables the dt-clamp + velocity-cap fix (Lecture 1 §5, Fix 1 and 2). The ball stops tunneling but its top speed is capped.
- Toggle `2` enables the sub-step fix (Lecture 1 §5, Fix 3). The ball runs at full speed and never tunnels.

**Acceptance criteria.**

- A file `homework/p5_tunneling_demo.py` exists.
- Pressing `0` disables all fixes. Pressing `1` enables Fix-1+2. Pressing `2` enables Fix-3.
- A counter on screen shows how many times the ball has crossed the wall WITHOUT bouncing (i.e. tunnelled).
- With Fix 0 the counter rises; with Fix 1 or 2 it stays at 0.
- Code is committed.

**Hint.** Detect tunneling: keep `last_x` between frames. If `(last_x - WALL_X) * (pos.x - WALL_X) < 0` and the ball didn't bounce this frame, you tunnelled. Increment the counter.

For the sub-step fix:

```python
steps = max(1, int(abs(vel.x * dt) // 2) + 1)
sub_dt = dt / steps
for _ in range(steps):
    pos.x += vel.x * sub_dt
    check_wall_collision()
```

**Estimated time.** 1 hour.

---

## Problem 6 — Reflection essay

**Problem statement.** Write a 350–450 word reflection at `notes/week-02-reflection.md` answering:

1. Which was harder — Lecture 1's collisions or Lecture 2's physics? Why?
2. The brick-breaker challenge has a specific bug pattern around modifying a list while iterating it. Have you hit this before in non-game code? What surprised you?
3. Describe a specific moment during the exercises or challenge where you saw a bug clearly because the lecture had named it. (e.g. "I saw the ball jitter on the floor and thought 'oh — the won't-settle bug'.")
4. What's one thing you'd want to learn next that this week didn't cover? (Swept tests? Multi-body collision response? Particle systems?)

**Acceptance criteria.**

- A file `notes/week-02-reflection.md`, 350–450 words.
- Each numbered question addressed in its own paragraph.
- At least one specific bug mentioned by name.
- File is committed.

**Hint.** Naming bugs is half the work. Future-you reading this in Week 8 will thank present-you.

**Estimated time.** 30 minutes.

---

## Time budget recap

| Problem | Estimated time |
|--------:|---------------:|
| 1 | 45 min |
| 2 | 30 min |
| 3 | 45 min |
| 4 | 1 h 30 min |
| 5 | 1 h 0 min |
| 6 | 30 min |
| **Total** | **~5 h 0 min** |

That's just under the 6-hour weekly budget — the rest is for fixing the bugs you'll create. You will create them. That is the work.

When you've finished all six, push your repo and open the [mini-project](./07-mini-project/00-overview.md).
