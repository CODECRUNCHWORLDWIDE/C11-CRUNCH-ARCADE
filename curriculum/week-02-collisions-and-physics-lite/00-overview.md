# Week 2 — Collisions and Physics-Lite

Last week we got a circle on screen and made it move at the same speed on every monitor. That was the spine. This week we put **two things in the same world** and ask the only question that matters once you have two things: *did they touch?*

Collision detection is where every game-development course earns its keep, because almost every mechanic — a paddle hitting a ball, a bullet hitting a wall, a player landing on a platform, a sword swinging through an enemy — is "did A touch B, and if so, what now?" The math is small. The bookkeeping is sneaky. The bugs are eerie. By Sunday you'll have written a brick-breaker (or Pong, your call) where the ball bounces off the paddle, the bricks, and the walls — and you'll know exactly which line of code rejects each impossible state.

We pair collisions with **physics-lite** because the two are joined at the hip. As soon as the ball moves under gravity, the question "is it on the floor?" becomes a collision check, and the question "did it stop?" becomes a velocity check. We'll do gravity. We'll do bounce. We'll meet the **tunneling problem** (the bug where a fast ball passes *through* a wall in one frame because we only sample positions, not paths) and survive it with the same delta-time clamp we already know plus a couple of new tricks. The full swept-collision deep dive waits for Week 4's tilemap; this week, you get an honest preview.

There is still no Godot. Still no sprite sheets. We are extending the Pygame skeleton we already trust into something that resembles a game in the way a chassis resembles a car.

## Learning objectives

By the end of this week, you will be able to:

- **Define** an axis-aligned bounding box (AABB) and write the four-comparison overlap test from memory.
- **Use** Pygame's `Rect.colliderect()` and explain why it returns `True` for an exact-edge touch and `False` for an off-by-one miss.
- **Distinguish** AABB overlap from a **circle–circle** distance test, and pick the right one for the shape you're checking.
- **Resolve** an overlap: push the moving body back out of the wall along the axis of least penetration, and reflect the relevant velocity component.
- **Identify** the tunneling problem when objects move farther than their own width in one frame, and explain why the discrete sampling we do is the root cause.
- **Apply** Euler integration — `pos += vel * dt; vel += acc * dt` — to a ball under gravity, and articulate why "Euler is wrong but fine for games" is the right shorthand.
- **Reflect** a velocity component on bounce, including a restitution coefficient less than 1 so the ball loses energy on each contact.
- **Diagnose** the "ball that won't settle" bug where floating-point noise keeps a resting body forever twitching, and apply the small-velocity-snap fix.

## Prerequisites

This week assumes you have completed **Week 1**. Specifically:

- You can write a Pygame main loop from memory.
- You use `dt` (seconds) for every movement update.
- You're comfortable with `pygame.Vector2`.
- You read `pygame.key.get_pressed()` for held input and `KEYDOWN` for one-shot input — and you know which is which.

If any of those are shaky, do the Week 1 mini-project first. Week 2 stacks directly on top of it.

## Topics covered

Lecture 1 — AABB collision and rectangles:

- Why **axis-aligned bounding boxes** are the workhorse of 2D collision.
- The four-comparison overlap test (and why it's two `<` and two `>`, never `<=`/`>=` depending on whose engine you read).
- Pygame's `Rect`: construction, anchor points, mutation, and the suite of `collide*` helpers.
- Circle vs circle: distance-squared less than radius-sum-squared. No `sqrt`.
- The **tunneling problem**: a fast ball that "jumps over" a thin wall in one frame because we only sampled the endpoints of its path.
- Resolving collisions after they've happened: shortest-axis push, position correction, velocity reflection.
- A word on the **separating axis theorem** for next year's brain.

Lecture 2 — Velocity, gravity, and the bouncing ball:

- Position, velocity, acceleration — all as 2D vectors with units (px, px/s, px/s²).
- **Euler integration**: the simplest integrator in the world and why every shipped 2D game uses it.
- Gravity as a constant downward acceleration of `(0, +g)`.
- **Reflection** of velocity on impact: flip the appropriate component, multiply by **restitution** to lose energy.
- The "won't settle" bug and its 4-line fix.
- A preview of the **fixed timestep for physics** (Week 4 deep dive).

## Weekly schedule

The schedule below adds up to approximately **36 hours**. Treat it as a target. Some sections click in 20 minutes, others take 3 hours. That is normal. Physics work is non-linear; if you find yourself tweaking gravity for an hour, that is not lost time — that is game-feel work.

| Day       | Focus                                         | Lectures | Exercises | Challenges | Quiz/Read | Homework | Mini-Project | Self-Study | Daily Total |
|-----------|-----------------------------------------------|---------:|----------:|-----------:|----------:|---------:|-------------:|-----------:|------------:|
| Monday    | AABB collision, the four comparisons          |    2h    |    1.5h   |     0h     |    0.5h   |   1h     |     0h       |    0.5h    |     5.5h    |
| Tuesday   | Velocity, gravity, the bouncing ball          |    2h    |    1.5h   |     1h     |    0.5h   |   1h     |     0h       |    0.5h    |     6.5h    |
| Wednesday | Resolving collisions, the platformer floor    |    0h    |    1.5h   |     1h     |    0.5h   |   1.5h   |     1h       |    0h      |     5.5h    |
| Thursday  | Brick-breaker challenge, polish               |    0h    |    1h     |     2h     |    0.5h   |   1h     |     2h       |    0.5h    |     7h      |
| Friday    | Mini-project deep work                        |    0h    |    0h     |     0h     |    0.5h   |   1.5h   |     2.5h     |    0.5h    |     5h      |
| Saturday  | Mini-project polish, quiz                     |    0h    |    0h     |     0h     |    0.5h   |   0h     |     2.5h     |    0h      |     3h      |
| Sunday    | Review, write up, push                        |    0h    |    0h     |     0h     |    0.5h   |   0h     |     2h       |    0h      |     2.5h    |
| **Total** |                                               | **4h**   | **5.5h**  | **4h**     | **3.5h**  | **6h**   | **10h**      | **2h**     | **35h**     |

## How to navigate this week

| File | What's inside |
|------|---------------|
| [README.md](./00-overview.md) | This overview (you are here) |
| [resources.md](./01-resources.md) | Collision references, the Nature of Code, Glenn Fiedler revisited |
| [lecture-notes/01-aabb-collision-and-rectangles.md](./02-lecture-notes/01-aabb-collision-and-rectangles.md) | AABB overlap, `Rect`, circles, tunneling, resolution |
| [lecture-notes/02-velocity-gravity-and-the-bouncing-ball.md](./02-lecture-notes/02-velocity-gravity-and-the-bouncing-ball.md) | Euler integration, gravity, restitution, the "won't settle" bug |
| [exercises/README.md](./03-exercises/00-overview.md) | Index of short coding drills |
| [exercises/exercise-01-two-rects-collide.py](./03-exercises/exercise-01-two-rects-collide.py) | Two rectangles overlap test with `colliderect` and your own implementation |
| [exercises/exercise-02-bouncing-ball-gravity.py](./03-exercises/exercise-02-bouncing-ball-gravity.py) | A ball that falls under gravity and bounces with restitution |
| [exercises/exercise-03-platformer-floor.py](./03-exercises/exercise-03-platformer-floor.py) | A controllable square that lands on a floor — the start of every platformer |
| [challenges/README.md](./04-challenges/00-overview.md) | Index of weekly challenges |
| [challenges/challenge-01-brick-breaker.md](./04-challenges/challenge-01-brick-breaker.md) | A paddle, a ball, ten bricks, and the score that makes it a game |
| [quiz.md](./05-quiz.md) | 10 multiple-choice questions |
| [homework.md](./06-homework.md) | Six practice problems for the week |
| [mini-project/README.md](./07-mini-project/00-overview.md) | Full spec for the brick-breaker (or Pong) mini-project |

## Frame budget for this week

A reminder of what 60 fps actually means, in milliseconds. Every lecture in this course returns to this tile.

```
┌─────────────────────────────────────────────────────────┐
│  FRAME BUDGET — 60 fps target, with collisions          │
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

This week, **Collision** finally earns its row. A handful of bricks and a paddle won't get you anywhere near 1.5 ms — but the brick-breaker mini-project is the first time you'll have more than two moving rectangles in one scene. Get comfortable with the budget now; in Week 4 we'll have a hundred tiles, and that row starts to matter.

## Stretch goals

If you finish early and want to push further:

- Read Glenn Fiedler's [Fix Your Timestep!](https://gafferongames.com/post/fix_your_timestep/) for the second time. Now that you've felt a tunneling bug, the essay reads completely differently.
- Read the [Nature of Code, chapter 2 — Forces](https://natureofcode.com/book/chapter-2-forces/). Daniel Shiffman's intuition for vectors is the one we want you to leave this course with.
- Implement **circle vs AABB** collision (the case the brick-breaker actually needs) by clamping the circle's centre to the rectangle and measuring the resulting distance. Write a one-paragraph note about why this works.
- Add **swept AABB** collision to your platformer floor: instead of "is the player below the floor this frame?", ask "did the player's path *cross* the floor between last frame and this frame?". This is one step toward Week 4's tilemap.
- Profile your brick-breaker with `cProfile`. Find the hottest function in your collision loop. Don't optimise it; just notice it.

## Voice rules for the week

- We still do not say "easy." Physics is not easy. We say "small" or "tractable."
- We name the bug before we name the fix. "Tunneling" is the bug; "swept tests" is the fix. Naming things gives you a hook.
- We credit the people who solved this before us: Newton, Euler, Verlet, Box2D's Erin Catto, Bob Nystrom. Citing the lineage is part of being indie.
- We trust playtest data over our own opinion. "Three of five testers thought the ball felt floaty" beats "I think gravity is right."

## Up next

Continue to [Week 3 — Game Design Vocabulary](../week-03/) once you've pushed your mini-project to GitHub.

---

*If you find errors in this material, please open an issue or send a PR. Future learners will thank you.*
