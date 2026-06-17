# Week 2 — Quiz

Ten multiple-choice questions. Take it with your lecture notes closed. Aim for 9/10 before moving to Week 3. Answer key at the bottom — don't peek.

---

**Q1.** Two AABBs overlap if and only if:

- A) They overlap on the X axis OR they overlap on the Y axis.
- B) They overlap on the X axis AND they overlap on the Y axis.
- C) Their centres are within `(radius_a + radius_b)` of each other.
- D) Their edges cross at least once.

---

**Q2.** Pygame's `Rect.colliderect` returns `False` when two rectangles share an edge exactly (e.g. `a.right == b.left` and they otherwise overlap on Y). Why?

- A) It's a Pygame bug; every other engine returns `True` there.
- B) Pygame rectangles are half-open on the right and bottom — pixel `right` is not inside the rect — so an exact edge-share is not an overlap.
- C) Pygame uses circles internally.
- D) It returns `True` actually; the question is wrong.

---

**Q3.** A ball moves at 2000 px/s and your `dt` clamps to `1/30`. What is the maximum distance the ball can travel between frames, and what bug does this enable for a 30-pixel-wide wall?

- A) ~67 pixels; the ball can tunnel through any wall thinner than 67 px.
- B) ~2000 pixels; the ball can never tunnel.
- C) ~2 pixels; tunneling is impossible for fast objects.
- D) ~60 pixels; tunneling only happens at 60 fps.

---

**Q4.** Which Python expression is the cheap "are these two circles overlapping?" test, with no `sqrt`?

- A) `(a_pos - b_pos).length() < a_r + b_r`
- B) `(a_pos - b_pos).length_squared() < (a_r + b_r) ** 2`
- C) `(a_pos - b_pos).length_squared() < a_r ** 2 + b_r ** 2`
- D) `abs(a_pos.x - b_pos.x) < a_r + b_r`

---

**Q5.** You write the bouncing-ball update as:

```python
pos += vel * dt
vel += acc * dt
```

What scheme is this, and what minimal change makes it strictly better for gravity?

- A) Verlet — already correct, no change.
- B) Forward Euler — swap the two lines so velocity is updated first (semi-implicit / symplectic Euler).
- C) Runge-Kutta — divide each step by 4.
- D) Implicit Euler — multiply each step by `dt²`.

---

**Q6.** Your bouncing ball never settles on the floor — it jitters forever between `vel.y = +2` and `vel.y = -1.4`. What is the canonical fix?

- A) Set restitution to exactly 1.0.
- B) Add a rest threshold: after the bounce, if `abs(vel.y) < THRESHOLD`, set `vel.y = 0.0`.
- C) Render at 30 fps instead of 60.
- D) Remove gravity once the ball is on the floor.

---

**Q7.** When resolving an AABB-vs-AABB overlap, the canonical algorithm is:

- A) Push the moving body out along whichever axis has the **smaller** overlap, then reflect the corresponding velocity component.
- B) Push the moving body out along whichever axis has the **larger** overlap, then reflect both velocity components.
- C) Push the moving body to the centre of the other one and reverse both velocity components.
- D) Set the moving body's position to `(0, 0)` and ignore velocity.

---

**Q8.** A platformer character lands on the floor. The right code on contact is:

- A) Reflect `vel.y` with restitution = 1.0 (`vel.y = -vel.y`).
- B) Reflect `vel.y` with restitution = 0.5 (`vel.y = -vel.y * 0.5`).
- C) Snap the player to the floor's top edge and set `vel.y = 0` (restitution = 0).
- D) Multiply `vel.y` by 0.99 and let it asymptote.

---

**Q9.** In the brick-breaker mini-project, when the ball hits the paddle, modern arcade Breakout-style behaviour reflects `vel.y` AND:

- A) Doubles `vel.x`.
- B) Biases `vel.x` based on where on the paddle the ball hit — centre = no change, edges = ±SPIN.
- C) Sets `vel.x` to a constant 300 px/s.
- D) Inverts gravity for the next frame.

---

**Q10.** Why does the lecture say "Euler is wrong but fine for games"?

- A) Euler is mathematically incorrect at every step.
- B) Euler accumulates small numerical errors per step, but at `dt ≈ 1/60` and game-scale velocities those errors are invisible to the player; the simplicity wins.
- C) Pygame's `Clock` returns Euler-incompatible delta times.
- D) Euler only works in 2D, and games are 2D, so it's fine.

---

## Answer key

<details>
<summary>Click to reveal answers</summary>

1. **B** — Two AABBs overlap if and only if their intervals overlap on BOTH X and Y. "Or" would report overlap whenever they're in the same row or column, regardless of distance. (Lecture 1 §2.)
2. **B** — Pygame Rects are half-open: a rect with `x=10, width=20` covers `10..29` inclusive, pixel `30` is not inside. The strict-`<` overlap test matches this. (Lecture 1 §2, §3.)
3. **A** — At 2000 px/s and `dt = 1/30 s`, max movement per frame is `2000/30 ≈ 66.7 px`. The ball can entirely cross a 30-px wall in one frame and never sample a position inside it. (Lecture 1 §5.)
4. **B** — Compare `distance²` to `(radius_sum)²`. No `sqrt`. Answer C is wrong because `(a+b)² ≠ a² + b²`. (Lecture 1 §4.)
5. **B** — Forward Euler. Swap to semi-implicit (velocity-first) for strictly-better energy behaviour with gravity. (Lecture 2 §2.)
6. **B** — The rest-threshold pattern: below some small `|vel.y|` post-bounce, snap to zero. Four-line fix. (Lecture 2 §5.)
7. **A** — Smaller overlap = the axis you came in along. Push out that way and reflect that axis's velocity. Larger overlap = the axis you were already inside on, which would push too far. (Lecture 1 §6.)
8. **C** — Landing is not a bounce. Restitution = 0. Snap-and-zero. (Lecture 2 §4 and Exercise 3.)
9. **B** — The "paddle English" trick: where on the paddle the ball hit determines its outgoing horizontal velocity. Without this, Breakout would not be playable. (Challenge 1.)
10. **B** — Euler is `O(dt²)` accurate per step. At `dt ≈ 16 ms` and game-scale velocities those errors are dominated by player perception and frame quantisation. Pick the simplest integrator that doesn't visibly misbehave. (Lecture 2 §1.)

</details>

---

If you scored under 7, re-read the lecture sections cited in the answers you missed. If you scored 9 or 10, you're ready for the [homework](./06-homework.md).
