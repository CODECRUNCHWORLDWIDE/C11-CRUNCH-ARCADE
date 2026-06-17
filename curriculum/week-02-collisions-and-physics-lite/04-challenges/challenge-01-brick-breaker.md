# Challenge 1 — Brick-Breaker Prototype

**Time estimate:** ~120 minutes.

## Problem statement

Build the smallest Breakout-style prototype that works. One paddle the player drives with LEFT/RIGHT, one ball that starts attached to the paddle and launches on SPACE, and a 10-brick row at the top of the window. When the ball hits the paddle, it bounces with a velocity that depends on **where** on the paddle it hit (so the player can aim). When the ball hits a brick, the brick disappears and the ball bounces. When the ball hits a wall or ceiling, it bounces with full restitution. When the ball falls past the bottom of the window, the round ends — re-attach the ball to the paddle for a fresh launch.

This is a tractable problem the day after Lecture 1, and it is also exactly the chassis your mini-project will hang on. **Do this challenge before the mini-project** and the mini-project is "decorate this with score, lives, and audio." Skip the challenge and you'll be debugging collisions while you're also debugging UI and scoring.

## Acceptance criteria

- [ ] A single Python file `brick_breaker.py` you can run with `python brick_breaker.py`.
- [ ] A 800x600 window titled "C11 Week 2 - Brick Breaker (Challenge)".
- [ ] A Coin-Pink paddle 96x12 px, centred at `y = 540`, controlled with LEFT/RIGHT arrows at 480 px/s. Cannot leave the window.
- [ ] A 12-px Coin-Pink ball that starts pinned above the paddle's centre.
- [ ] Pressing SPACE launches the ball at roughly `(0, -360)` px/s plus a small horizontal randomisation so successive launches differ.
- [ ] Ten Power-Up-Cyan bricks 68x24 px each, arranged in a single row at `y = 80`, with a 4-px gap between them.
- [ ] **Ball–wall collisions:** snap-back-and-flip on the left, right, and top edges. Restitution = 1.0.
- [ ] **Ball–paddle collision:** when the ball overlaps the paddle, snap the ball above the paddle and reflect `vel.y`. The reflected `vel.x` should be biased by where on the paddle the ball hit — centre = current `vel.x`, edges = ±240 px/s added. (This is the classic "Breakout English.")
- [ ] **Ball–brick collisions:** when the ball overlaps a brick, remove the brick from the world AND reflect the ball on the axis of smaller overlap (Lecture 1 §6). At most one brick per frame may be destroyed — process them in order and break out of the loop on the first hit.
- [ ] When the ball falls below the bottom edge, re-pin it to the paddle. (No "game over" needed for the challenge; the mini-project adds lives.)
- [ ] When all ten bricks are destroyed, print `"You cleared the wall."` to the terminal once.
- [ ] Movement uses delta time. `dt` is clamped to `1/30`.
- [ ] `python -m py_compile brick_breaker.py` succeeds with no output.
- [ ] You commit the file to your Week 2 GitHub repo with a one-paragraph `README.md` explaining what you built and what was harder than you expected.

## Stretch (any of these for extra polish)

- **A second row of bricks.** Three colours, each worth a different score (we won't display the score in the challenge — but you can print it on a brick-destroyed event).
- **Ball-trail.** Don't fully fill the background each frame. Alpha-fill with `(20, 20, 30, 30)` on a `SRCALPHA` surface. ~5 lines, looks great.
- **Sub-step on fast frames.** If `vel * dt > BRICK_HEIGHT / 2`, run two physics sub-steps. This is the only honest fix for tunneling on a slow frame. (Lecture 1 §5.)
- **Sound on bounce.** A short SFX from <https://freesound.org/> (CC0 or CC-BY, credit the author). Use `pygame.mixer.Sound.play()`. Different sound for paddle vs brick vs wall — three SFX total.
- **Variable restitution.** Each brick has a restitution. Cyan = 1.0, magenta = 1.05 (ball speeds up; the classic Breakout difficulty curve). Cap ball speed so the game doesn't explode.

## Hints

<details>
<summary>The "paddle English" formula</summary>

When the ball hits the paddle, you want centre hits to go straight back up and edge hits to fly off sideways. The standard formula:

```python
# Where did the ball hit the paddle?
# -1.0 = far left edge, 0.0 = centre, +1.0 = far right edge.
relative_hit = (ball_pos.x - paddle_rect.centerx) / (paddle_rect.width / 2)
relative_hit = max(-1.0, min(1.0, relative_hit))   # clamp

# Add an angle-bias to the reflected velocity.
SPIN = 240.0
ball_vel.x = ball_vel.x + relative_hit * SPIN
ball_vel.y = -abs(ball_vel.y)   # always go up after paddle hit
```

This is the trick that makes Breakout playable. Without it, the player has no aiming control — the ball just bounces deterministically. With it, the player aims by intercepting the ball off-centre.

Cap the maximum speed of the ball after this so it doesn't accelerate forever (`ball_vel.length()` clamped to, say, 600 px/s).

</details>

<details>
<summary>Why brick destruction needs to break out of the loop</summary>

Naive code:

```python
for brick in bricks:
    if ball_rect.colliderect(brick):
        bricks.remove(brick)
        reflect_ball(ball_rect, brick)
```

Two bugs:

1. **Modifying a list while iterating it** is a Python sin. Use `bricks[:]` to iterate a copy, or rebuild the list, or — easier — break out on the first hit:

```python
for brick in bricks:
    if ball_rect.colliderect(brick):
        bricks.remove(brick)
        reflect_ball(ball_rect, brick)
        break
```

2. **Multi-brick frames.** A fast ball at a brick-row corner can overlap two bricks in one frame. With `break`, only one is destroyed per frame, which is what you want — destroying two and reflecting twice in one frame produces weird kinematic results. Process one, render, re-detect next frame.

</details>

<details>
<summary>Why the ball–brick reflection uses the "smaller overlap" axis</summary>

When the ball overlaps a brick, you need to know whether it came in from the side (reflect X) or from above/below (reflect Y). The cleanest test is the one from Lecture 1 §6:

```python
overlap_x = min(ball_rect.right, brick.right) - max(ball_rect.left, brick.left)
overlap_y = min(ball_rect.bottom, brick.bottom) - max(ball_rect.top, brick.top)
if overlap_x < overlap_y:
    # came in from the side
    ball_vel.x = -ball_vel.x
    if ball_rect.centerx < brick.centerx:
        ball_rect.right = brick.left
    else:
        ball_rect.left = brick.right
else:
    # came in from top or bottom
    ball_vel.y = -ball_vel.y
    if ball_rect.centery < brick.centery:
        ball_rect.bottom = brick.top
    else:
        ball_rect.top = brick.bottom
```

This is "good enough" for a brick wall. It fails at exact corner hits — both axes overlap equally — but those are rare and the error is invisible to players. SAT or swept tests would do better; not for this week.

</details>

<details>
<summary>Don't forget delta time</summary>

```python
ball_pos += ball_vel * dt
paddle_x += paddle_vel * dt
```

If you write `ball_pos += ball_vel`, the ball moves N pixels per frame (Lecture 2 of Week 1, the canonical bug). Use `dt` everywhere movement happens.

</details>

<details>
<summary>The float-position-with-derived-rect pattern</summary>

For the ball, keep two variables: a `Vector2` for the float position and a `Rect` you rebuild each frame for collision queries:

```python
ball_pos = pygame.Vector2(WINDOW_WIDTH / 2, paddle_rect.top - 12)
ball_vel = pygame.Vector2(0.0, 0.0)
BALL_SIZE = 12

# Inside the loop, after updating ball_pos:
ball_rect = pygame.Rect(
    int(ball_pos.x - BALL_SIZE / 2),
    int(ball_pos.y - BALL_SIZE / 2),
    BALL_SIZE,
    BALL_SIZE,
)
```

The Rect is a query view. The Vector2 is the truth. After resolution snaps the rect (e.g. `ball_rect.right = brick.left`), copy back to the Vector2:

```python
ball_pos.x = ball_rect.centerx
ball_pos.y = ball_rect.centery
```

Yes, this is two lines of bookkeeping. It saves you from float-vs-int collision bugs that take hours to find.

</details>

## Frame budget for this challenge

A paddle, a ball, and ten bricks is *cheap*. Expect something like:

```text
┌─────────────────────────────────────────────────────────┐
│  FRAME BUDGET — Brick Breaker at 60 fps                 │
│                                                         │
│  Input poll:       ~0.1 ms                              │
│  Update (pos+vel): ~0.1 ms                              │
│  Collisions (~12): ~0.3 ms                              │
│  Render:           ~0.6 ms                              │
│  GPU + present:    ~4.0 ms                              │
│  Headroom:         ~11.5 ms                             │
│  ─────────────────────                                  │
│  Total:           ~16.6 ms / frame                      │
└─────────────────────────────────────────────────────────┘
```

You have 11 ms of headroom. **This is intentional.** Get used to building with plenty of budget left over; later weeks will eat it.

## Submission

Commit `brick_breaker.py` and `README.md` to your Week 2 GitHub repo under `challenges/challenge-01/`. In the README, list each stretch goal you attempted and link to anything (sound credit, GIF, etc.).

## Why this matters

A paddle and a ball is the simplest **two-bodies-and-a-target** game. Pong, Breakout, Arkanoid, every pinball table — all the same chassis. Once the ball-bounces-cleanly-off-paddle-and-brick code is right, the mini-project is layout, score, lives, audio, polish — none of which are physics work.

Get this right today. Then the mini-project is a feel-and-polish exercise, not a debugging session.
