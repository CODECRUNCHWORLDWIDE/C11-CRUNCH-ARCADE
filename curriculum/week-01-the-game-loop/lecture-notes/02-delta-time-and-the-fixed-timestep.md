# Lecture 2 — Delta Time and the Fixed Timestep

> **Duration:** ~2 hours of reading + hands-on.
> **Outcome:** You can move a sprite at the same speed on a 60 Hz monitor and a 144 Hz monitor, explain why "N pixels per frame" is a bug, and articulate the fixed-timestep pattern (even though we won't fully implement it until Week 2).

If you only remember one thing from this lecture, remember this:

> **Frame rate is not the same as simulation rate.** They are two different numbers, and if you treat them as one, your game runs faster on better hardware. This is the most-shipped bug in indie gamedev. Do not ship it.

---

## 1. The naive bug

You've just written your first Pygame loop. You have a circle. You decide to move it right. The obvious code:

```python
x = 100
# inside the loop, every frame:
x += 5
pygame.draw.circle(screen, (255, 0, 200), (x, y), 10)
```

Every frame, the circle moves 5 pixels right. At 60 fps that's `5 × 60 = 300` pixels per second. Across an 800-pixel-wide screen, the circle takes about 2.6 seconds to cross. Looks fine on your laptop. You commit, push, and post a GIF.

A friend with a 144 Hz monitor downloads your demo. **Their circle crosses the screen in 1.1 seconds.** Same code. Same Python. Same Pygame. The circle moves more than twice as fast on their machine.

What happened? On their monitor running at 144 Hz, Pygame's `clock.tick(60)` may not be capping you to 60 if VSync is doing its thing differently, or `tick` is being called incorrectly, or — most commonly — you wrote `tick(0)` or no tick at all, and the loop is running as fast as the CPU allows.

But even if `tick(60)` does its job and you genuinely run at 60 fps on both machines: imagine the same code on a *slower* machine that can only achieve 30 fps. Now the loop runs 30 times a second instead of 60. The circle moves `5 × 30 = 150` pixels per second. **Half speed.** Same code; the game world ticks at half the rate.

This is the bug. The fix has a name.

---

## 2. Delta time — the fix

The fix is to **scale movement by elapsed real time**, not by frames.

Instead of "move 5 pixels per frame," you say "move 300 pixels per second." Then each frame you check how many seconds have actually passed since the last frame — call that `dt` (for delta time) — and you move the player by `300 × dt`.

```python
SPEED = 300  # pixels per second
# inside the loop, every frame:
x += SPEED * dt
```

On a 60 fps machine, `dt` is about `1/60 ≈ 0.0167` seconds. Movement per frame: `300 × 0.0167 ≈ 5` pixels. Same as before.

On a 30 fps machine, `dt` is about `1/30 ≈ 0.0333` seconds. Movement per frame: `300 × 0.0333 ≈ 10` pixels. **Twice as much per frame**, but the loop runs half as often, so the net result is the same 300 pixels per second.

On a 144 fps machine, `dt` is about `1/144 ≈ 0.0069` seconds. Movement per frame: `300 × 0.0069 ≈ 2.08` pixels. Less per frame, more frames. Net: still 300 px/s.

That is the entire idea of delta time. It is one multiplication. It is the difference between a game and a bug-shaped prototype.

### Getting `dt` from Pygame

```python
clock = pygame.time.Clock()
dt = 0.0
while running:
    # ... input, update (using dt), render ...
    dt = clock.tick(60) / 1000
```

`clock.tick(fps)` returns the number of **milliseconds** since the previous call. Divide by 1000 to get seconds. That's your `dt` for the next frame.

> **Pitfall.** The first frame, you have no previous `dt`. Default to `0.0` or to a sensible `1/60`. If you use `0.0`, on frame 1 nothing moves — which is usually fine. If you use `1/60`, on frame 1 the world moves as if 16 ms passed — which is approximately correct.

### Units, units, units

Use **seconds** everywhere in your update code. Speed in pixels per second. Acceleration in pixels per second squared. Time in seconds. If anyone in the code uses milliseconds, convert at the boundary (just after `clock.tick`) and forget about ms inside your update logic. Mixing units silently is how you get circles that move at light-speed by accident.

---

## 3. The frame budget

You have a budget per frame. At 60 fps, that budget is `1 / 60 = 16.6` milliseconds. Every system you add to your game eats into it.

```
┌─────────────────────────────────────────────────────────┐
│  FRAME BUDGET — 60 fps target                           │
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

If you blow the budget — your loop takes 25 ms — your effective fps drops to 40 and the game feels sluggish. `clock.tick(60)` will return immediately instead of sleeping, but it cannot make time go backwards.

At 60 fps, 16.6 ms feels like a lot until you start adding things:

- 50 sprites each updating their own physics: ~1 ms.
- A particle system with 500 particles: ~2 ms.
- Per-pixel collision against a tilemap: easily 5 ms if done badly.
- An audio decode you forgot to cache: ~3 ms.

These add up faster than you think. Junior devs will tell you they "optimised early and it didn't help." That's because the *render* and *present* steps usually dominate small games. Until you've measured, you're guessing.

**Measure with `time.perf_counter()`.** Wrap suspect blocks:

```python
import time
start = time.perf_counter()
do_the_suspicious_thing()
elapsed_ms = (time.perf_counter() - start) * 1000
print(f"thing took {elapsed_ms:.2f} ms")
```

This is one of those weeks where the discipline matters more than the result. Get used to the question "where did this frame's milliseconds go?" Coming weeks will push you to actually answer it.

---

## 4. Game-loop hygiene — clamping delta time

There is a second bug nobody tells you about. Imagine the player tabs out of your game for 10 seconds. Your loop is paused (the OS deprioritises background processes). When they tab back in, `clock.tick(60)` returns **10,000 milliseconds**. `dt` is 10 seconds.

Your update code does `x += SPEED * dt`. Now `x` jumps by `300 × 10 = 3000` pixels. The player teleports off screen. The ball you were tracking has tunnelled through every wall. The score has incremented by a hundred. Welcome to game-state corruption from a long frame.

The fix is a **delta-time clamp**:

```python
MAX_DT = 1 / 30  # don't let dt exceed ~33ms
dt = min(clock.tick(60) / 1000, MAX_DT)
```

If a frame takes longer than 33 ms, we pretend it only took 33 ms. The simulation slows down (from the player's perspective time has stretched) but it doesn't catastrophically warp. Most games clamp at somewhere between `1/30` and `1/15`.

This is also why every shipped game with a "Pause" menu *actually* sets a paused flag instead of just letting `dt` run wild. The right behaviour for pause is to **skip the update step entirely**, not to feed the update a giant `dt`.

```python
if not paused:
    update(dt)
```

Tiny thing. Saves you a class of weird bugs.

---

## 5. The fixed timestep — a preview

Delta-time-scaled movement works fine for things that move in a straight line. It starts to break for things that *bounce*, *collide*, or *integrate* — anything with physics.

The problem is that physics simulation does not scale linearly with `dt`. If gravity adds `9.8 * dt` to your y-velocity, and `dt` is twice as big this frame because of a hiccup, you can tunnel through a thin floor: your previous-frame position was above the floor, your new-frame position is below it, and you never checked the in-between. The collision check sees you below the floor and thinks "they've always been below the floor."

The solution is the **fixed timestep**. You decouple the simulation rate from the render rate. The simulation always advances in fixed-size steps — say, 1/120 of a second — no matter how slowly or quickly the render is happening. If the render took 20 ms (so `dt = 0.02`), you run the simulation two and a half steps (or two steps and accumulate the remainder for next frame).

The pseudocode looks like this:

```python
SIM_STEP = 1 / 120  # 120 simulation steps per second
accumulator = 0.0

while running:
    # input
    handle_input()

    # accumulate real time
    accumulator += dt

    # advance simulation in fixed steps
    while accumulator >= SIM_STEP:
        update_physics(SIM_STEP)
        accumulator -= SIM_STEP

    # render at whatever rate the screen wants
    render()

    dt = clock.tick(60) / 1000
```

The simulation always sees `SIM_STEP` as its `dt`. Always. Even if the render is running at 30 fps or 144 fps. This is **the** pattern for any game that does its own physics. It's what Box2D does internally. It's what every Mario clone does. It's what every Souls-like does for its hitboxes.

We won't fully implement this in Week 1. We do **non-physics movement** this week (a circle gliding around), where simple `pos += speed * dt` works fine. We come back to fixed timestep in Week 2 when we add collisions.

For now you just need to know:

1. Render rate ≠ simulation rate.
2. Variable timestep is fine for kinematic motion.
3. Fixed timestep is the right answer for physics.
4. Glenn Fiedler's [Fix Your Timestep!](https://gafferongames.com/post/fix_your_timestep/) essay is the canonical reference and it is on your resources list.

---

## 6. Putting it together — a moving circle, the right way

A complete program from the top. Type this. Don't paste.

```python
import pygame

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
running = True

# Game state
x, y = 100.0, 300.0           # floats — see note below
speed_px_per_s = 200          # pixels per second

dt = 0.0
MAX_DT = 1 / 30

while running:
    # 1. Input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 2. Update
    x += speed_px_per_s * dt
    if x > 800:
        x = 0   # wrap to the left edge

    # 3. Render
    screen.fill((20, 20, 30))
    pygame.draw.circle(screen, (219, 39, 119), (int(x), int(y)), 16)
    pygame.display.flip()

    dt = min(clock.tick(60) / 1000, MAX_DT)

pygame.quit()
```

A circle slides right at 200 px/s and wraps to the left edge when it leaves the screen. Run it on every machine you can find. It looks the same on all of them. That is the whole point.

### Note: use floats for position

You'll see we declared `x, y = 100.0, 300.0` — floats, not ints. Why? Because at 200 px/s and 60 fps, each frame's increment is `200 × (1/60) ≈ 3.33` pixels. If `x` is an `int`, you can't add 3.33 to it without losing the fractional part. Over a thousand frames the error accumulates.

Store positions as floats. Convert to `int` only at the moment you pass them to `pygame.draw`. The drawing functions accept floats but will truncate to integer pixel positions — that's fine, the integer pixel is "where to draw," but your *logical position* is the float.

If you want sub-pixel smoothness for the visual itself, you need anti-aliased drawing (`pygame.draw.aacircle` does not exist; `pygame.gfxdraw.aacircle` does — different module). We'll touch on this in Week 6 (animation & juice).

---

## 7. The Pygame `Vector2` — use it

Manually tracking `x` and `y` works for one object. Once you have two, you'll wish for vector math. Pygame ships `pygame.Vector2`:

```python
pos = pygame.Vector2(100, 300)
vel = pygame.Vector2(200, 0)   # 200 px/s rightward

# inside the loop:
pos += vel * dt
```

That's the same physics as `x += speed * dt` and `y += 0 * dt`, but reads cleanly. `Vector2` supports `.length()`, `.normalize()`, `.rotate(degrees)`, dot product, addition, scaling — everything you'd want. Use it. It's `import pygame; v = pygame.Vector2(0, 0)` — no extra install.

This week's exercises use both styles so you see them. Past this week you'll use `Vector2` for everything.

---

## 8. Reading input — two ways

Keyboard input in Pygame works in two distinct modes, and you need to know which to use when.

### Event-based (one-shot)

```python
for event in pygame.event.get():
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_SPACE:
            fire_bullet()
```

Use `KEYDOWN` / `KEYUP` events for actions that should happen **once per press**: firing a bullet, opening a menu, jumping. The event fires on the frame the key was pressed; nothing more.

### State-based (held)

```python
keys = pygame.key.get_pressed()
if keys[pygame.K_d]:
    pos.x += speed * dt
```

Use `pygame.key.get_pressed()` for actions that should happen **every frame while the key is held**: movement, charging a weapon. It returns a sequence indexed by key constant — `keys[pygame.K_d]` is `True` while D is down, `False` otherwise.

**Most beginner WASD bugs come from using `KEYDOWN` for movement.** With `KEYDOWN`, the player moves one pixel when they press the key, then nothing happens until they release and press again. Use `get_pressed` for movement; use `KEYDOWN` for jumps and shots.

---

## 9. Normalising diagonal movement

A small gotcha. If your update is:

```python
if keys[pygame.K_d]:
    vel.x = speed
if keys[pygame.K_s]:
    vel.y = speed
```

…then pressing D and S together produces a vector with magnitude `sqrt(speed² + speed²) ≈ 1.41 × speed`. The player moves **faster on diagonals**. Every action game has solved this for forty years; you solve it by **normalising** the direction:

```python
direction = pygame.Vector2(0, 0)
if keys[pygame.K_d]: direction.x += 1
if keys[pygame.K_a]: direction.x -= 1
if keys[pygame.K_s]: direction.y += 1
if keys[pygame.K_w]: direction.y -= 1

if direction.length_squared() > 0:
    direction = direction.normalize()

pos += direction * speed * dt
```

`length_squared()` is faster than `length()` — same comparison, no `sqrt`. The `> 0` guard is there because `normalize()` on a zero vector raises. Get used to this idiom. It will appear in every game you write.

---

## 10. What to remember

- **`pos += speed * dt`.** Not `pos += SPEED_PER_FRAME`. Ever.
- **Get `dt` from `clock.tick()`.** Convert ms → s once. Keep seconds in your update logic.
- **Clamp `dt`.** `dt = min(dt_raw, 1/30)` or similar.
- **Use floats for position.** Cast to `int` only for drawing.
- **Pick the right input style.** `get_pressed` for held; `KEYDOWN` for taps.
- **Normalise diagonals.** Or admit you're shipping diagonal-speedrun-by-accident.
- **Render and simulation are different rates.** Today we couple them. After Week 2 we won't.

You now have everything you need to do the exercises. The pattern from this point forward is: input → update (with `dt`) → render → tick. Forever.

---

*Next: open [`exercises/exercise-01-blank-window.py`](../exercises/exercise-01-blank-window.py) and get a window on the screen.*
