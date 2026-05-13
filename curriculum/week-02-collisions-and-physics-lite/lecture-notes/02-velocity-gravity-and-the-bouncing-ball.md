# Lecture 2 — Velocity, Gravity, and the Bouncing Ball

> **Duration:** ~2 hours of reading + hands-on.
> **Outcome:** You can integrate position from velocity and velocity from acceleration with Euler's method, add gravity, reflect velocity on collision with a restitution coefficient less than 1, and detect when a ball has "come to rest" without it forever-twitching from floating-point noise.

If you only remember one thing from this lecture, remember this:

> **Position, velocity, and acceleration are three vectors that live together.** Update position from velocity. Update velocity from acceleration. Multiply each step by `dt`. That is essentially every 2D physics simulation ever shipped — the rest is choosing what to put into `acceleration` and what to do when bodies meet.

---

## 1. Three vectors, one update

You already know position from Week 1. We added velocity to it once — `x += SPEED_PX_PER_S * dt` was velocity times time. Now we make it explicit and we add the third member of the family: acceleration.

```python
pos = pygame.Vector2(400, 100)     # pixels
vel = pygame.Vector2(  0,   0)     # pixels per second
acc = pygame.Vector2(  0, 800)     # pixels per second squared  (gravity)
```

The update, every frame:

```python
vel += acc * dt
pos += vel * dt
```

That's it. Two lines. The first one says "velocity gains a little more downward every frame, because acceleration is pulling it down." The second says "position moves by velocity-times-time, because that's what velocity means."

### The units

A unit check is the fastest bug-finder in physics:

- `pos`: pixels.
- `vel`: pixels per second.
- `acc`: pixels per second² (pixels per second per second).
- `dt`: seconds.

`vel * dt` has units `(px/s) * s = px`. Adds cleanly to `pos`. Good.
`acc * dt` has units `(px/s²) * s = px/s`. Adds cleanly to `vel`. Good.

If you ever see yourself adding `acc * dt` to `pos`, stop. Your units are wrong. The number you'd be adding is in `px/s`, not `px`. That bug is invisible visually (the ball still moves) but produces wildly wrong physics. Track units in your head every time you write a physics line.

### Why this is called Euler integration

In calculus terms, position is the integral of velocity over time, and velocity is the integral of acceleration. We're computing those integrals by **forward Euler's method**: take a tiny step in time, multiply by the current rate, add. The accuracy depends on how small the step is and how smooth the function is.

For our game, `dt` is around `1/60` of a second, the functions are *very* smooth (gravity is literally constant), and "accuracy" means "the ball looks right" — not "the ball lands at the predicted point 100 seconds from now." Euler is fine for this. The whole indie 2D world ships with forward Euler. AAA physics engines move to **Verlet** or **semi-implicit Euler** for better stability under stiff forces (springs, ropes, large masses). Out of scope this term.

> The shorthand to remember is: **"Euler is wrong but fine for games."** Newton, Euler, Verlet, Runge-Kutta — they're all integrators, and they trade simplicity for accuracy. Pick the simplest one that doesn't visibly misbehave. For us that's Euler.

---

## 2. Semi-implicit Euler, the one-line upgrade

There's a tiny tweak to forward Euler that's strictly better for games. It's called **semi-implicit Euler** (sometimes "symplectic Euler"), and it's just a reordering:

```python
# Forward Euler (the version above):
vel_new = vel + acc * dt
pos_new = pos + vel * dt    # uses old vel!

# Semi-implicit Euler:
vel += acc * dt             # update velocity FIRST
pos += vel * dt             # use the NEW velocity
```

The difference is whether you use the old or the new velocity when updating position. Semi-implicit uses the new one. It's one line of difference and it produces noticeably better behaviour for gravity, springs, and orbits — energy doesn't drift over time the way it does with forward Euler.

The exercises and the brick-breaker both use **semi-implicit Euler**. It's no more code. It's better. Use it.

---

## 3. Gravity, the simplest force

Gravity in our game is a constant downward acceleration. On Earth it's `9.8 m/s²`. In our pixel-world it's whatever value makes a ball *feel* like it's falling under gravity, which is almost never the real-world value scaled.

```python
GRAVITY = pygame.Vector2(0, 800)   # 800 px/s² downward
```

`800 px/s²` is a number we picked because it feels good in an 800-px-tall window. If you tune your game in a smaller window, drop it. If you tune in a larger window or for slower play, raise it. Game-feel beats physical accuracy. (Mario's gravity, famously, is *much* higher than Earth's when scaled to its character heights. That's why Mario feels snappy; real-gravity Mario would feel floaty.)

In the loop:

```python
vel += GRAVITY * dt
pos += vel * dt
```

The ball accelerates downward forever. After two seconds it's moving at `800 * 2 = 1600` px/s downward — about two screens per second. Without a floor it falls off the screen and is gone.

To keep it in play, we add a floor and a bounce.

---

## 4. Reflecting velocity on bounce

When the ball hits the floor — defined as `pos.y + radius > FLOOR_Y` — we want it to bounce. Reflection of a velocity component across an axis is one of the prettiest pieces of code you'll write:

```python
vel.y = -vel.y
```

That's the reflection. The ball was moving down; now it's moving up at the same speed. Snap the position back to the floor first (Lecture 1 §6) and the bounce looks clean.

```python
if pos.y + radius > FLOOR_Y:
    pos.y = FLOOR_Y - radius
    vel.y = -vel.y
```

Run this. The ball bounces back to exactly the same height it fell from. Forever. Real balls don't do this. Real balls lose energy on every bounce. That's restitution.

### Restitution — the energy-loss coefficient

A rubber ball returns about 70% of its kinetic energy on each bounce. A bowling ball returns less. A super-ball returns more. The factor that captures "how much velocity comes back" is the **coefficient of restitution** (often called `e`):

```python
RESTITUTION = 0.7
# on bounce:
vel.y = -vel.y * RESTITUTION
```

Now each bounce returns 70% of the previous velocity. After ten bounces the ball is barely moving. After twenty it's a blur of micro-bounces. After a few seconds it should be still.

If you set `RESTITUTION = 1.0` the ball never loses energy. If you set it to `0.0` the ball sticks to the floor. The range you want is usually `0.5` to `0.9`. **Pong's paddles are `1.0`** because Pong cares about pace, not realism. **A pinball plunger is around `0.8`**. **A platformer's "land softly" floor is around `0.0`** — full stop.

---

## 5. The won't-settle bug

Here's a subtlety nobody warns you about.

Drop the ball. It bounces. After ten bounces the velocity is `0.7^10 * initial_velocity` — small but not zero. Each frame the floor pushes it back up with a tiny negative-velocity nudge. The ball is now visually still — pixel-perfect on the floor — but its `vel.y` is jittering between, say, `+2` and `-1.4` every frame. The ball is **vibrating** on the floor. Some of those vibrations show as a 1-pixel jitter.

Worse: every frame you're still running the collision-detected-snap-back-and-reflect code path. Your "the ball is at rest" branch never fires because the ball is never *quite* at rest.

The fix is a **velocity threshold**. If after the bounce the velocity is small enough, snap it to zero:

```python
REST_THRESHOLD = 30.0   # px/s. Below this we call it "at rest."

if pos.y + radius > FLOOR_Y:
    pos.y = FLOOR_Y - radius
    vel.y = -vel.y * RESTITUTION
    if abs(vel.y) < REST_THRESHOLD:
        vel.y = 0.0
```

Four lines. The ball now settles cleanly. The "rest threshold" depends on the game's units — `30 px/s` for our 800x600 window is reasonable. Tune it.

This bug has shipped in real games. Pinball clones, breakout games, ragdoll demos. It's not glamorous and it doesn't have a glamorous fix. It just needs to be known.

---

## 6. The bouncing ball, complete

```python
import pygame

WIDTH, HEIGHT = 800, 600

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

pos = pygame.Vector2(WIDTH / 2, 100)
vel = pygame.Vector2(0, 0)
acc = pygame.Vector2(0, 800)        # gravity

RADIUS = 16
RESTITUTION = 0.75
REST_THRESHOLD = 30.0

dt = 0.0
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Semi-implicit Euler
    vel += acc * dt
    pos += vel * dt

    # Floor
    if pos.y + RADIUS > HEIGHT:
        pos.y = HEIGHT - RADIUS
        vel.y = -vel.y * RESTITUTION
        if abs(vel.y) < REST_THRESHOLD:
            vel.y = 0.0

    # Walls (just in case)
    if pos.x - RADIUS < 0:
        pos.x = RADIUS
        vel.x = -vel.x * RESTITUTION
    if pos.x + RADIUS > WIDTH:
        pos.x = WIDTH - RADIUS
        vel.x = -vel.x * RESTITUTION

    screen.fill((20, 20, 30))
    pygame.draw.circle(screen, (219, 39, 119), (int(pos.x), int(pos.y)), RADIUS)
    pygame.draw.line(screen, (6, 182, 212), (0, HEIGHT - 1), (WIDTH, HEIGHT - 1), 2)
    pygame.display.flip()

    dt = min(clock.tick(60) / 1000.0, 1.0 / 30.0)

pygame.quit()
```

Forty lines. Drop the ball, watch it settle. Change `RESTITUTION` to `0.95` and it bounces for what feels like forever. Change to `0.3` and it's down in two thumps. Change `GRAVITY` to `1600` and it falls twice as fast. Change to `400` and it floats. Each of those changes is a knob in your game-feel toolbox; in Week 3 we'll talk about which knob to turn when a tester says "it feels off."

---

## 7. Adding horizontal motion

A ball that only falls is dull. Real balls — paddle balls, pinballs, anti-grav balls in space — have horizontal velocity too. The math doesn't change. Add a starting `vel.x`:

```python
vel = pygame.Vector2(220, 0)   # 220 px/s rightward, starts not falling
```

The ball moves diagonally, gravity acts vertically. When it hits a wall, reflect `vel.x`. When it hits the floor, reflect `vel.y`. **The walls and floor act independently** — same restitution coefficient, different axis.

If you want a ball that bounces around a *closed box* — like a screensaver — turn gravity off:

```python
acc = pygame.Vector2(0, 0)
```

…and now you have your Week 1 bouncing ball, but with `vel` as a vector instead of two `x_speed`/`y_speed` scalars. The same code handles both cases. That's the point of the velocity vector.

---

## 8. Drag and friction (optional but useful)

Real moving objects slow down. Air resists motion (drag) and surfaces resist sliding (friction). A simple model that's "good enough for games":

```python
DRAG = 0.99   # multiply velocity by this each frame
# inside the loop:
vel *= DRAG
```

This is **per-frame** drag, which is technically frame-rate-dependent. The frame-rate-correct version uses an exponential decay scaled by `dt`:

```python
# Frame-rate-independent drag
import math
DRAG_RATE = 0.5      # higher = more drag
vel *= math.exp(-DRAG_RATE * dt)
```

The exponential form means "the velocity halves every `1/DRAG_RATE` seconds, regardless of frame rate." It's slightly more expensive (one `exp` per frame per body) but it's the version you should use when correctness matters. We won't use it in this week's mini-project, but you should know it exists.

**Ground friction** is the same trick, applied only on the X axis and only when the ball is touching the ground:

```python
if on_ground:
    vel.x *= math.exp(-FRICTION_RATE * dt)
```

---

## 9. A taste of the fixed timestep for physics

Last week we mentioned the fixed timestep. This week we have a stronger reason to actually do it: **physics integration accuracy depends on `dt`**. Bigger `dt`, worse integration. Variable `dt` (which we have right now) means the simulation's behaviour subtly changes when the frame rate changes — gravity that feels right at 60 fps may feel wrong at 30 or 144.

The fix is to **decouple the simulation step from the render step**, exactly like we sketched last week:

```python
SIM_STEP = 1.0 / 120.0
accumulator = 0.0

while running:
    # input
    # ...

    # accumulate real time
    accumulator += dt
    # advance physics in fixed-size steps
    while accumulator >= SIM_STEP:
        update_physics(SIM_STEP)
        accumulator -= SIM_STEP

    # render at whatever rate the loop wants
    render()
    dt = clock.tick(60) / 1000.0
```

Now `update_physics` always sees `SIM_STEP` as its `dt`. The simulation is deterministic across machines.

**We won't implement this in this week's mini-project.** A brick-breaker with a single ball and ten bricks survives just fine on a clamped variable timestep. We'll do the fixed timestep properly in Week 4 alongside the tilemap, where the consequences of a bad integration step are bigger (a platformer character ghosting through a wall is a worse bug than a brick-breaker ball that bounces 5% differently on a slow machine).

For now: know the pattern. Reuse the framework when your mini-project needs it.

---

## 10. The forces you'll meet in this course

Gravity is one force. Games use a small zoo of others, all expressible as accelerations or as direct velocity changes:

| Force | What it does | Where it shows up |
|-------|--------------|-------------------|
| Gravity | Constant downward `(0, +g)` | Platformers, falling objects |
| Drag | Velocity multiplied by `< 1` each step | Top-down vehicles, projectiles in fluid |
| Friction | Drag on the ground axis only when grounded | Platformers, top-down RPGs |
| Impulse | Instant change to velocity, no `dt` | Jumping, getting hit |
| Spring | Force proportional to displacement | Camera follow, juicy UI bounces (Week 6) |
| Magnetic / homing | Acceleration toward a target | Homing missiles, pickups that fly to player |

Today we use gravity and a touch of drag. By Week 6 you'll be combining all six in the same scene. The recipe is always the same: each frame, accumulate accelerations into a single `acc`, then `vel += acc * dt; pos += vel * dt`. **One integrator, many forces.** That's the model.

---

## 11. What to remember

- **`vel += acc * dt; pos += vel * dt`.** Update velocity first. That's semi-implicit Euler.
- **Units check.** Position in px, velocity in px/s, acceleration in px/s². `dt` in s. Always.
- **Gravity is just a constant acceleration.** Tune it to game-feel, not Earth.
- **Reflection on bounce:** `vel.y = -vel.y`. With restitution: `vel.y = -vel.y * E`. With snap: position first, velocity next.
- **The won't-settle bug** wants a velocity threshold below which you snap to zero.
- **Drag and friction** are velocity multipliers; use `math.exp(-rate * dt)` for the frame-rate-correct form.
- **Fixed timestep is the long-term answer for physics.** Preview now, implement in Week 4.

You now have everything you need for the second exercise — a bouncing ball under gravity — and most of what you need for the brick-breaker. The pattern from here is: every "physics-y" thing in 2D is an acceleration, a velocity, a position, and a collision response.

---

*Next: open [`exercises/exercise-01-two-rects-collide.py`](../exercises/exercise-01-two-rects-collide.py) and make two boxes know they touched.*
