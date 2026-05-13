# Challenge 1 — Bouncing Ball

**Time estimate:** ~90 minutes.

## Problem statement

Take the moving circle from Exercise 2 and give it a 2D velocity. When the circle reaches the edge of the window, it must **bounce** — reflect its velocity component along that axis so it travels back into the play area at the same speed.

This is the canonical first physics-like behaviour in any game. It looks trivial on paper. It is not, because there are at least three subtle bugs you can write that all *almost* work. Catching them is the point.

## Acceptance criteria

- [ ] A single Python file `bouncing_ball.py` you can run with `python bouncing_ball.py`.
- [ ] One 16-px Coin-Pink circle bounces around an 800x600 window.
- [ ] Initial velocity is roughly `(220, 180)` px/s — a deliberate non-axis-aligned vector so you see real diagonal bounces, not a boring zigzag.
- [ ] When the circle hits the left or right edge, its **x**-velocity reverses sign and its position is **corrected** so the circle is fully back inside the play area before next frame's render.
- [ ] When the circle hits the top or bottom edge, its **y**-velocity reverses sign and its position is corrected the same way.
- [ ] The circle never visibly clips outside the window. Not even by 1 pixel for one frame.
- [ ] Movement uses delta time. The same `bouncing_ball.py`, run on a friend's machine with a different refresh rate, looks the same.
- [ ] The window closes cleanly on X / Cmd-Q / Escape.
- [ ] You commit the file to your Week 1 GitHub repo with a one-paragraph `README.md` explaining what you built and what was harder than you expected.

## Stretch (any of these for extra polish)

- **Sound on bounce.** Pick a short free SFX from <https://freesound.org/> (CC0 or CC-BY; credit the author). Play it on each bounce using `pygame.mixer.Sound.play()`. Mute it with the M key.
- **Multiple balls.** Spawn three balls with different starting positions and velocities. They do *not* need to collide with each other this week — only with the walls. (That's the Week 2 problem.)
- **Variable restitution.** Add an "energy loss" coefficient between 0.8 and 1.0. On every bounce, multiply the velocity by it. Watch the ball asymptote to rest. This is more interesting than it sounds and is half of every breakout/pinball mechanic.
- **Trail.** Don't fully fill the background each frame. Fill with `(20, 20, 30, 30)` on a `pygame.SRCALPHA` surface, blit it over the previous frame, and you'll get a tail effect. It is roughly five lines and looks great.

## Hints

<details>
<summary>How to reflect velocity</summary>

Reflecting a velocity component across an axis is exactly `v = -v`. If the circle hits the right edge, do `vel.x = -vel.x`. If it hits the bottom, do `vel.y = -vel.y`.

```python
if pos.x + radius >= WINDOW_WIDTH:
    vel.x = -abs(vel.x)   # see the "absorbing" hint below
```

</details>

<details>
<summary>The "stuck on the wall" bug — and the fix</summary>

The naive bounce code is:

```python
if pos.x + radius > WINDOW_WIDTH:
    vel.x = -vel.x
```

This *almost* works. Imagine a high-velocity frame where the circle ends up at `pos.x = WINDOW_WIDTH + 5`. You flip `vel.x` from positive to negative. Next frame the circle moves a few pixels left. But on a hiccup, the position correction might still leave it overshooting, and on the frame after you flip `vel.x` *again* — back to positive — and the circle gets stuck wiggling against the wall.

Two fixes, use both:

1. **Snap the position back inside the box** after flipping the velocity:

   ```python
   if pos.x + radius > WINDOW_WIDTH:
       pos.x = WINDOW_WIDTH - radius
       vel.x = -abs(vel.x)
   if pos.x - radius < 0:
       pos.x = radius
       vel.x = abs(vel.x)
   ```

2. **Use `abs` not negation.** `vel.x = -abs(vel.x)` guarantees the velocity points *inward*. `vel.x = -vel.x` can re-flip an already-reflected velocity if you re-enter the if-block. Belts and braces.

This pattern — "if you overshot the constraint, project back to the constraint and flip the relevant velocity component" — is the foundation of all 2D collision response. Every solid-wall collision in the game industry is a fancier version of this.

</details>

<details>
<summary>Don't forget delta time</summary>

```python
pos += vel * dt
```

Velocity is in pixels per second. `dt` is in seconds. Result is in pixels. Standard kinematics.

If you write `pos += vel` (no `dt`), the ball moves N pixels per frame. We covered why that's a bug in Lecture 2. If you write `pos.x += vel.x * dt; pos.y += vel.y * dt` instead of using `Vector2`, that's fine too — just verbose.

</details>

<details>
<summary>Tunneling at large dt</summary>

If `dt` spikes (alt-tab, breakpoint, debugger), the ball could "tunnel" past the wall — its previous position was inside, its new position is *way* past the wall, and the snap-back behaves strangely.

We **clamp** `dt` exactly because of this:

```python
dt = min(clock.tick(60) / 1000, 1/30)
```

A truly robust solution uses a fixed timestep (Lecture 2 §5). For a single bouncing ball at 220 px/s on an 800-px window, the clamp is enough. Bigger physics needs fixed-step. We'll do that in Week 2.

</details>

## Frame budget for this challenge

A bouncing ball at 220 px/s on a single screen is *cheap*. You will have something like:

```text
┌─────────────────────────────────────────────────────────┐
│  FRAME BUDGET — Bouncing Ball at 60 fps                 │
│                                                         │
│  Input poll:       ~0.1 ms                              │
│  Update (pos+vel): ~0.05 ms                             │
│  Edge collision:   ~0.05 ms                             │
│  Render:           ~0.4 ms                              │
│  GPU + present:    ~4.0 ms                              │
│  Headroom:         ~12.0 ms                             │
│  ─────────────────────                                  │
│  Total:           ~16.6 ms / frame                      │
└─────────────────────────────────────────────────────────┘
```

You're nowhere near saturating the budget. **This is intentional.** Get used to the feeling of "I have a 12 ms headroom; I can afford something." That headroom is what lets you add three balls, particles, a trail, a sound system, all without dropping a frame. Optimise later. Build now.

## Submission

Commit `bouncing_ball.py` and `README.md` to your Week 1 GitHub repo under `challenges/challenge-01/`. In the README, list each stretch goal you attempted and link to anything (sound credit, GIF, etc.).

## Why this matters

The bouncing-ball problem is the smallest non-trivial physics simulation. Every brick-breaker, pinball table, Pong clone, and Arkanoid started from this. Next week we add a paddle and bricks; the bounce logic you write today is the bounce logic that ships. **Get the snap-back-and-flip pattern right now** and Week 2's collisions feel like a small extension instead of a redesign.

Also: when your mini-project asks for a player-controlled circle that bounces, you'll have already solved half of it.
