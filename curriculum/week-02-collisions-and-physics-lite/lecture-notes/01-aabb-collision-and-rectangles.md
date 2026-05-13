# Lecture 1 — AABB Collision and Rectangles

> **Duration:** ~2 hours of reading + hands-on.
> **Outcome:** You can write the four-comparison AABB overlap test from memory, explain when it lies (tunneling), and resolve a collision by pushing the moving body out of the wall along the axis of least penetration.

If you only remember one thing from this lecture, remember this:

> **An overlap test is four comparisons. A collision *response* is everything else.** Detecting that two boxes touch is small. Deciding what to do about it — and not breaking the simulation while you do it — is the work.

---

## 1. Why AABBs are the workhorse

There are dozens of ways to ask "do two shapes touch?" in two dimensions. Polygon vs polygon. Circle vs line. Capsule vs capsule. Each one has its own math and its own corner cases. The industry agreed decades ago that for most 2D games most of the time, the answer is:

> Approximate every collidable thing as a **rectangle**, with sides parallel to the X and Y axes. Then the question "do they touch?" is four `if` statements.

That rectangle is called an **axis-aligned bounding box** — AABB. "Axis-aligned" because its sides don't tilt; they're parallel to the screen's X and Y axes. "Bounding" because it bounds (encloses) the actual sprite, which is usually a more complex shape underneath.

```
    AABB                            actual sprite
    ┌──────────────┐                    ▲
    │              │                   ▲▲▲
    │     ▲        │                  ▲▲▲▲▲
    │    ▲▲▲       │      vs         ▲▲ x ▲▲
    │   ▲▲▲▲▲      │                ▲▲▲▲▲▲▲▲▲
    │  ▲▲ x ▲▲     │
    └──────────────┘
```

The cost is precision: a sprite-shaped enemy in an AABB has dead space in the corners, and a bullet that grazes one of those corners "hits" the enemy even though it visually missed. The benefit is speed and simplicity. For a brick-breaker, a Mario clone, or a top-down shooter, AABBs are correct enough that no player will ever complain.

When AABBs aren't enough, you graduate to circles (cheap), circle-vs-AABB (also cheap, with a little extra work), or one of the heavier polygon tests. We'll meet circles in §4. For everything else, this term is AABB.

---

## 2. The four-comparison overlap test

Two AABBs overlap if and only if **they overlap on the X-axis AND they overlap on the Y-axis.** That's the entire trick.

Two intervals `[a_min, a_max]` and `[b_min, b_max]` on a number line overlap when:

```
a_min < b_max  AND  b_min < a_max
```

If `a_min >= b_max`, A is entirely to the right of B. If `b_min >= a_max`, A is entirely to the left of B. Either way they don't touch. Otherwise they do.

In 2D you do this test twice — once for X, once for Y — and require both to be true:

```python
def aabb_overlap(a_left, a_top, a_right, a_bottom,
                 b_left, b_top, b_right, b_bottom):
    return (
        a_left   < b_right  and
        b_left   < a_right  and
        a_top    < b_bottom and
        b_top    < a_bottom
    )
```

That's it. Four comparisons. Two `and`s. One Boolean. Memorise it. You will write some variant of this function in every 2D engine you ever touch.

### A diagram

```
    ┌──────────┐
    │     A    │
    │     ┌──────────┐
    │     │   ║  B   │
    └─────│───╝      │
          │          │
          └──────────┘

  A overlaps B on X:  A.left < B.right AND B.left < A.right    ✓
  A overlaps B on Y:  A.top  < B.bottom AND B.top  < A.bottom  ✓
  → They collide.
```

### The `<` vs `<=` debate

Two reasonable people, one writing for Pygame and one writing for Unity, will disagree about whether the test should use `<` or `<=`. Pygame's `Rect.colliderect` uses strict `<`. That means **two rectangles that share *exactly* an edge — pixel-perfect touching, no overlap — do NOT collide.**

```python
a = pygame.Rect(0,  0, 10, 10)   # spans x=0..10
b = pygame.Rect(10, 0, 10, 10)   # spans x=10..20
a.colliderect(b)  # False — they share x=10 but don't overlap
```

This sounds like a gotcha. In practice it's the right call: if two boxes are exactly touching, no resolution is needed, so reporting "no collision" lets you move on. It also means that **`x=10` belongs to `b`, not `a`** — Pygame rectangles are half-open intervals `[x, x + width)` on the right and bottom. The pixel at `right` is **not** inside the rect. The pixel at `right - 1` is.

This is the kind of detail you only notice when a bug demands it. Now you know.

---

## 3. Pygame's `Rect`

You can write your own AABB type. Don't, this term. Pygame ships a `Rect` that does everything we need.

### Construction

```python
import pygame
r = pygame.Rect(left, top, width, height)
r = pygame.Rect((left, top), (width, height))    # also valid
```

Pygame's screen coordinates: `(0, 0)` is the **top-left**, `x` grows right, `y` grows **down**. This trips up everyone whose physics intuition is "y up" from school. You can either get used to it (recommended) or you can flip the sign at the boundary (more code, more bugs). Get used to it.

### Mutating

```python
r.x = 100         # set left
r.y = 200         # set top
r.move_ip(5, 3)   # in-place move by (5, 3)
r2 = r.move(5, 3) # returns a new Rect, doesn't modify r
```

Pygame's habit of having both in-place (`move_ip`) and not-in-place (`move`) versions of every method is one to know up front. The `_ip` suffix means "in place" — it mutates the receiver and returns `None`. Forget the `_ip` and you get a new rect but the old one is unchanged.

### Anchor points

A `Rect` carries thirteen anchor properties: `.left`, `.top`, `.right`, `.bottom`, `.centerx`, `.centery`, `.topleft`, `.topright`, `.bottomleft`, `.bottomright`, `.midtop`, `.midleft`, `.center`, etc. Most are setters too:

```python
ball.center = (player.centerx, player.top - 16)  # move ball just above the player
```

Setting `.center` translates the whole rect; setting `.left` shifts the rect left-edge to that value. This is one of the most beautiful APIs in Pygame and worth ten minutes of your life clicking through the [docs](https://www.pygame.org/docs/ref/rect.html).

### `.colliderect(other)`

```python
if paddle.colliderect(ball_rect):
    bounce()
```

The four-comparison overlap test, with the strict-`<` semantics from §2. This is the single most-called collision function in Pygame projects.

### `.collidelist(rects)` and `.collidelistall(rects)`

```python
hit_index = ball_rect.collidelist(brick_rects)   # -1 if none, else the first hit
hit_indices = ball_rect.collidelistall(brick_rects)
```

You'll use `collidelist` for the brick-breaker mini-project. It's an O(n) loop in C under the hood, much faster than a Python loop calling `colliderect` n times. For a brick-breaker with 50 bricks, no measurable cost.

### `.collidepoint(x, y)`

```python
if button_rect.collidepoint(mouse_pos):
    click()
```

For mouse clicks on rectangles. We'll use this in Week 5 when we build a pause menu.

### `Rect.inflate(dx, dy)` — the hitbox trick

```python
hitbox = enemy_rect.inflate(-8, -8)  # shrink by 4 px each side
```

Inflate by **negative** numbers to shrink the hitbox. Every shooter uses this: the *visible* sprite is the full rect, but the *hitbox* is a smaller inflated rect, so the player can dodge a bullet by 4 pixels and the game says "you ducked." This is the easiest game-feel improvement in the world. Remember it.

---

## 4. Circles need a different test

A circle isn't a rectangle. Its bounding rectangle exists — and `colliderect` against it returns false hits in the corners.

```
    ┌──────────┐         ●●●           ●●●
    │   ●●●    │          ●             ●
    │  ●   ●   │       ●     ●       ●     ●
    │ ●     ●  │       ●     ●       ●     ●
    │  ●   ●   │          ●             ●
    │   ●●●    │         ●●●           ●●●
    └──────────┘

    AABB of circle      Two circles that  Two circles that
                        do NOT overlap     DO overlap
                        but their AABBs do (AABB also yes)
```

The right test for **circle vs circle** is the distance test: two circles overlap when the distance between their centres is less than the sum of their radii.

```python
def circles_overlap(a_pos, a_radius, b_pos, b_radius):
    delta = a_pos - b_pos
    distance = delta.length()
    return distance < (a_radius + b_radius)
```

And the right way to write it in a hot loop is **without the `sqrt`**:

```python
def circles_overlap(a_pos, a_radius, b_pos, b_radius):
    delta = a_pos - b_pos
    distance_sq = delta.length_squared()
    radii_sum = a_radius + b_radius
    return distance_sq < radii_sum * radii_sum
```

`length_squared` skips the square root. If you only need the comparison, you don't need the actual distance, and `sqrt` is expensive enough at scale to matter. Get in the habit now.

### Circle vs AABB

The most common case in 2D gameplay is **a circle (the ball) hitting a rectangle (the paddle or brick)**. The standard algorithm is:

1. Take the rectangle.
2. **Clamp** the circle's centre to the rectangle, getting the closest point on the rectangle to the circle.
3. Measure the distance from that clamped point to the circle's centre.
4. If that distance is less than the circle's radius, they overlap.

```python
def circle_aabb_overlap(circle_pos, radius, rect):
    closest_x = max(rect.left, min(circle_pos.x, rect.right))
    closest_y = max(rect.top,  min(circle_pos.y, rect.bottom))
    dx = circle_pos.x - closest_x
    dy = circle_pos.y - closest_y
    return (dx * dx + dy * dy) < (radius * radius)
```

This is the test the brick-breaker mini-project actually wants. It's still cheap — four `min`/`max` calls, two subtractions, two multiplies. We'll write it again, with diagrams, in Lecture 2 alongside the bounce response.

---

## 5. The tunneling problem

Now the bug.

You have a ball at `pos = (100, 100)` moving at `vel = (2000, 0)` pixels per second. The frame's `dt` is `0.02` (a 50 fps frame). The new position is:

```
pos.x = 100 + 2000 * 0.02 = 140
```

That's fine. Now consider a thin wall — a `Rect(120, 80, 4, 40)`. The wall is at x = 120..124. The ball *was* at x = 100 (left of the wall). The ball *is now* at x = 140 (right of the wall). The ball **moved through the wall in one frame and we never sampled a position inside it.** Our overlap test, asked "is the ball overlapping the wall *right now*?", says "no, the ball is at x=140 and the wall ends at x=124."

The ball **tunnelled** through the wall. The player sees the ball pass through. The collision never fires. The bounce never happens. The bug is real and ships in real games every year.

```
   Frame N-1                           Frame N
   ─────────────                       ─────────────

        ●                                          ●
       │ ▌                                        │ ▌
       │ ▌  wall                                  │ ▌
       │ ▌                                        │ ▌

   ball at x=100                       ball at x=140
   wall at x=120..124                  wall at x=120..124
   overlap? NO                         overlap? NO
                                       ← but it CROSSED the wall →
```

### Why it happens

Our simulation is **discrete**. We sample positions once per frame. Between frames, the ball doesn't exist — its position is not defined. If the path between frame N-1 and frame N crosses an obstacle, but neither endpoint is inside the obstacle, no point-test catches it.

This is the central problem of game collision. The fix has names.

### Fix 1: clamp `dt`

If `dt` is bounded, then movement per frame is bounded, and if your fastest object moves less than your thinnest wall per frame, you can't tunnel. This is the `dt = min(dt_raw, 1/30)` we put in last week.

For a ball at 2000 px/s and a clamp of `1/30` s, max movement per frame is `66` pixels. Walls thinner than 66 pixels: still tunnels. So clamping alone isn't enough for fast objects or thin walls.

### Fix 2: cap velocity

Make sure no object moves faster than, say, half the thinnest obstacle's width per frame. For brick-breaker with 60-pixel-wide bricks and 60 fps, that's a velocity cap of `1800` px/s. Tractable. Restrictive but tractable.

### Fix 3: sub-step the simulation

If `vel * dt` would cross more than half a wall-width, split the frame into N substeps and run the simulation N times with `dt / N`. This is the simplest robust fix:

```python
MAX_STEP = 8.0   # max pixels per substep
distance = (vel * dt).length()
steps = max(1, int(distance // MAX_STEP) + 1)
sub_dt = dt / steps
for _ in range(steps):
    pos += vel * sub_dt
    check_collisions()
```

It's not the fastest. It is the simplest. Use it this week.

### Fix 4 (the real answer): swept tests

Compute the **line segment** the ball would travel along this frame, and check whether *that segment* intersects the wall. If it does, find the point on the segment where contact first happens, snap the ball there, and resolve from that point.

This is **swept AABB** and we'll meet it in Week 4 when we have a tilemap. For now: know the name, know it exists. Don't implement it until you need it.

---

## 6. Resolving a collision after detection

You detected a collision. Now what? Two questions:

1. **Where do I put the body?** Not where it overshot — back to where it just barely doesn't overlap.
2. **What does it do next?** Bounce? Stop? Slide? Trigger a sound?

The simplest response is **push out along the axis of least penetration and reflect velocity**.

### Step 1 — compute the overlap on each axis

```python
overlap_x = min(a.right, b.right) - max(a.left, b.left)
overlap_y = min(a.bottom, b.bottom) - max(a.top, b.top)
```

If both are positive, the rectangles overlap by these amounts on each axis. (If either is non-positive, they don't actually overlap and you shouldn't be in this code path.)

### Step 2 — push along the smaller axis

Whichever overlap is smaller is the axis you came in along. Push the moving body out on that axis.

```python
if overlap_x < overlap_y:
    # came in from the side
    if a.centerx < b.centerx:
        a.right = b.left      # push left
    else:
        a.left  = b.right     # push right
    vel.x = -vel.x            # bounce horizontally
else:
    # came in from top or bottom
    if a.centery < b.centery:
        a.bottom = b.top      # push up
    else:
        a.top    = b.bottom   # push down
    vel.y = -vel.y            # bounce vertically
```

This is the canonical 2D collision response. It's not physically perfect — at a corner it picks one axis when in reality both got hit at the same instant — but it's good enough for ten thousand shipped games, and it's the algorithm the Week 2 mini-project wants.

### Step 3 — apply restitution (Lecture 2)

If you want energy loss, multiply the reflected component by a restitution coefficient less than 1. We cover this in Lecture 2. For now, the reflection above is "perfectly elastic" — full energy back.

---

## 7. A complete code example

```python
import pygame

WIDTH, HEIGHT = 800, 600

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

ball = pygame.Rect(100, 100, 20, 20)
ball_vel = pygame.Vector2(220, 180)

wall = pygame.Rect(380, 200, 40, 200)

dt = 0.0
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    ball.x += int(ball_vel.x * dt)
    ball.y += int(ball_vel.y * dt)

    if ball.colliderect(wall):
        overlap_x = min(ball.right, wall.right) - max(ball.left, wall.left)
        overlap_y = min(ball.bottom, wall.bottom) - max(ball.top, wall.top)
        if overlap_x < overlap_y:
            if ball.centerx < wall.centerx:
                ball.right = wall.left
            else:
                ball.left = wall.right
            ball_vel.x = -ball_vel.x
        else:
            if ball.centery < wall.centery:
                ball.bottom = wall.top
            else:
                ball.top = wall.bottom
            ball_vel.y = -ball_vel.y

    if ball.left < 0 or ball.right > WIDTH:
        ball_vel.x = -ball_vel.x
    if ball.top < 0 or ball.bottom > HEIGHT:
        ball_vel.y = -ball_vel.y

    screen.fill((20, 20, 30))
    pygame.draw.rect(screen, (219, 39, 119), ball)
    pygame.draw.rect(screen, (6, 182, 212), wall)
    pygame.display.flip()
    dt = min(clock.tick(60) / 1000.0, 1.0 / 30.0)

pygame.quit()
```

A ball bounces around a window, off a wall in the middle. Forty lines, every concept from this lecture.

You'll notice we cast `vel * dt` to `int` before adding to the rect. `pygame.Rect` stores ints, not floats, and the fractional pixels accumulate as a position error. **In production we'd store position as a `Vector2` of floats, and rebuild the rect each frame** from the float position — exactly like we did last week with `int(x)` for drawing. We'll do that the right way in Exercise 1 and Lecture 2.

---

## 8. Common mistakes (the greatest hits)

In two terms of teaching this material:

- **`<=` instead of `<`.** Edge-sharing rects "collide" forever, the ball jitters along a paddle that it's not actually inside. Use strict `<`, match Pygame.
- **Resolving along both axes at once.** You push out on X, then on Y, and end up further from the wall than necessary, or worse, inside an adjacent wall. **Push on one axis only — the smaller overlap.**
- **Reflecting velocity before snapping position.** Velocity flips, but the rect is still inside the wall, so next frame it's still detected as colliding, you flip again, and the ball oscillates inside the wall forever. **Snap position first, then flip velocity.**
- **Forgetting the half-open interval.** Pygame rects are `[left, right)`. The pixel at `right` is *not* in the rect. Off-by-one bugs come from this.
- **Storing position as int.** Velocity is in pixels per second. `vel.x * dt` at 200 px/s and 60 fps is `3.33` pixels. Truncate to int, lose the `.33`, and over 100 frames you've drifted by 33 pixels. Floats for position, ints only at draw time.
- **Tunneling.** Bullet at 3000 px/s, wall 10 px thick. Bullet vanishes. Clamp dt, cap velocity, or sub-step. Or accept the bug if your game doesn't need fast bullets.

---

## 9. A taste of the Separating Axis Theorem

For rectangles that aren't axis-aligned — say, a rotated paddle in a top-down brawler — the four-comparison test doesn't work. The general answer is the **Separating Axis Theorem** (SAT):

> Two convex shapes don't overlap if and only if there exists an axis on which their projections don't overlap.

For two AABBs the only axes that matter are X and Y, which is why our test is two interval-overlap checks. For two rotated rectangles, the candidate axes are the four edge normals of the two rectangles — eight checks instead of four. For arbitrary convex polygons, it's every edge normal of both shapes.

You don't need SAT this term. You should know the name, because every collision article online will assume you've heard of it, and because the moment you ship a game with rotated hitboxes you'll need it. Add it to your "things to study later" list and move on.

---

## 10. What to remember

- **Overlap test:** four comparisons. `a.left < b.right AND b.left < a.right AND a.top < b.bottom AND b.top < a.bottom`.
- **Pygame `Rect` uses strict `<`.** Touching-but-not-overlapping rects don't collide. This is correct.
- **`colliderect`, `collidelist`, `collidepoint`, `inflate`** are your daily tools.
- **Circles use the distance test**, with `length_squared` to skip the `sqrt`.
- **Circle vs AABB:** clamp the circle's centre to the rectangle, measure distance to the clamped point.
- **Tunneling is real.** Clamp `dt`, cap velocity, or sub-step. Swept tests are the eventual fix; not this week.
- **Resolve on the shorter overlap axis.** Snap position back, *then* flip velocity. Order matters.
- **Hitboxes ≠ sprites.** Inflate by a negative number to shrink the hitbox. Every shipped game does this.

You now have everything you need for the exercises. The pattern from this point forward is: every gameplay event in 2D Pygame is "did rect A overlap rect B, and if so what now?" That's collisions.

---

*Next: [Lecture 2 — Velocity, Gravity, and the Bouncing Ball](./02-velocity-gravity-and-the-bouncing-ball.md).*
