# Lecture 2 — Tweening, Easing, and Juice

> **Duration:** ~2 hours of reading + hands-on.
> **Outcome:** You can write `lerp` and four easing curves from memory; you can build a `Tween` class that drives squash-and-stretch on jump and land; you can implement screen shake with three parameters; you can spawn a particle emitter from an FSM `enter()` hook; and you can articulate what "juice" means using Swink's three pillars without reaching for "it feels better."

If you only remember one thing from this lecture, remember this:

> **Juice is the polish pillar of Swink's *game feel*. The implementation is mechanical: `lerp`, easing curves, a `Tween` driver, screen shake, particles, sound cues bound to FSM transitions. The work is *tuning*. The code is a hundred lines. The taste is the lifetime.**

The lecture walks the full stack: the two-line `lerp`, the four easing curves you'll use the most, the `Tween` class, squash-and-stretch on jump, screen shake on landing, a particle emitter on impact, sound cues bound to `enter()`. Then we step back and look at Nijman's *Screenshake* checklist — twenty cheap tricks, six of which we implement — and Swink's three pillars one more time.

By the end you have the *recipe book* for juicing any future Pygame project. The mini-project is where you cook.

---

## 1. `lerp` — the two-line function that runs the world

```python
def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t
```

Two lines. `t=0` returns `a`. `t=1` returns `b`. `t=0.5` returns the midpoint. `t` outside `[0, 1]` extrapolates.

`lerp` is the single most-called function in game programming. The camera lerps toward the player. The volume lerps from 0 to 1 on a fade-in. The colour lerps from white to red during the hit flash. The character's scale lerps from `(1.0, 1.0)` to `(0.7, 1.3)` for a jump squash. The same two-line function drives all of it.

A 2D version that takes tuples:

```python
def lerp2(a: tuple[float, float], b: tuple[float, float],
          t: float) -> tuple[float, float]:
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
```

Or, with `pygame.Vector2`:

```python
def lerp_vec(a: pygame.Vector2, b: pygame.Vector2, t: float) -> pygame.Vector2:
    return a + (b - a) * t
```

All three are the same function in different clothes. Lerp does not know what it's lerping. It is *the* abstraction over "smoothly transition between two values."

A 60-fps render loop calling `lerp(camera, player, 0.15)` every frame produces a soft camera-follow that looks human-handheld instead of robot-rigid. Try `t=1.0` and the camera snaps to the player every frame — the rigid robot. Try `t=0.05` and the camera lags noticeably. The taste setting is between. The lerp itself is two lines; the *value of `t`* is the work.

---

## 2. Easing curves: `t` to `t'`

`lerp(a, b, t)` is linear: equal-sized steps. Real motion isn't linear. A jumping character accelerates upward fast, then decelerates as gravity wins. A falling object accelerates downward. A door swings open *faster at first and slower at the end* — overshoot, settle. Linear motion looks robotic; eased motion looks alive.

Easing is one function applied to `t` *before* the lerp. Five curves cover 90% of game work; each one is a one-line function.

```python
def linear(t: float) -> float:
    return t

def ease_in(t: float) -> float:
    return t * t  # quadratic ease-in

def ease_out(t: float) -> float:
    return 1.0 - (1.0 - t) * (1.0 - t)  # quadratic ease-out

def ease_in_out(t: float) -> float:
    if t < 0.5:
        return 2.0 * t * t
    return 1.0 - 2.0 * (1.0 - t) * (1.0 - t)

def ease_out_back(t: float, overshoot: float = 1.70158) -> float:
    """Overshoot-and-settle. The 1.70158 constant is Penner's."""
    s = overshoot
    t = t - 1.0
    return t * t * ((s + 1.0) * t + s) + 1.0
```

Each curve's *shape* matters:

- **`linear`** — robot. Use for nothing aesthetic; use for things that *should* feel mechanical (a progress bar, a level loader).
- **`ease_in`** — slow start, fast end. Anticipation. Used for *gathering energy*: a charged attack windup, a button being held down before release.
- **`ease_out`** — fast start, slow end. Settling. Used for *follow-through*: a camera arriving at a target, a UI panel sliding in.
- **`ease_in_out`** — slow start, fast middle, slow end. The "S-curve." Used for transitions where both ends should feel gentle: a level-fade, a portrait swap.
- **`ease_out_back`** — overshoot past 1.0, then settle back to 1.0. The "pop." Used for *attention* and *delight*: a "+100 SCORE" pop-up appearing, a button being pressed, a coin landing in a counter.

Plot the five curves on paper before you write code. The exercise asks you to plot them on screen.

For the canonical full catalogue, read **Robert Penner's 2001 paper** (linked in `resources.md`). Penner's PDF is the source every easing library is descended from. The five above cover this week's needs; the other thirty are stylistic variations.

---

## 3. The `Tween` class: animating a value over time

A `Tween` wraps `lerp` + an easing curve + a duration. Six fields:

```python
from dataclasses import dataclass
from typing import Callable


@dataclass
class Tween:
    start: float
    end: float
    duration: float
    elapsed: float = 0.0
    ease: Callable[[float], float] = linear
    on_complete: Callable[[], None] | None = None

    def update(self, dt: float) -> bool:
        """Returns True while the tween is still running."""
        if self.elapsed >= self.duration:
            return False
        self.elapsed = min(self.elapsed + dt, self.duration)
        if self.elapsed >= self.duration and self.on_complete is not None:
            self.on_complete()
        return True

    def value(self) -> float:
        t = 0.0 if self.duration <= 0 else self.elapsed / self.duration
        t = max(0.0, min(1.0, t))
        return lerp(self.start, self.end, self.ease(t))

    def done(self) -> bool:
        return self.elapsed >= self.duration
```

Twelve substantive lines. Used like this:

```python
squash_tween = Tween(start=1.0, end=0.7, duration=0.1, ease=ease_out)
# ... per frame ...
squash_tween.update(dt)
scale_y = squash_tween.value()
```

The `on_complete` hook lets a tween chain itself: when squash-down finishes, fire stretch-up; when stretch-up finishes, fire return-to-normal. Three tweens, automatic chaining, no FSM. (You *can* drive the chain with the FSM. Both ship.)

---

## 4. Squash-and-stretch on jump and land

The single most-used juice trick. The character squashes vertically just before the jump (anticipation) and stretches vertically during the jump (follow-through). On landing, the character squashes again (impact) and bounces back to normal (settle).

The implementation is a single `scale_y` field on `Character`, driven by a tween, applied at draw time.

```python
class JumpState(AirborneState):
    def enter(self, char):
        char.vy = -JUMP_VEL
        char.grounded = False
        char.anim.play("jump_launch", restart=True)
        char.sfx.play_one_shot("jump")
        # Squash-and-stretch on launch.
        char.scale_tween = Tween(start=1.0, end=1.25, duration=0.12,
                                 ease=ease_out)


class FallState(AirborneState):
    def enter(self, char):
        char.anim.play("fall_airborne")
        # No tween; the airborne pose is the static value.
        char.scale_y = 1.0


# In a hypothetical LandState — or, simpler, the IdleState's enter
# when arriving from an airborne state:

class IdleState(State):
    def enter(self, char):
        char.anim.play("idle_breathing")
        if char.prev_state_was_airborne:
            char.scale_tween = Tween(start=0.7, end=1.0, duration=0.18,
                                     ease=ease_out_back)
```

Three things to notice:

1. **The tween lives on the character, not the state.** Why? Because the squash *outlasts* the state transition. Land happens in one frame; the squash-and-recover animation runs for 180 ms — three FSM transitions might happen in that window, but the squash should complete regardless.
2. **`ease_out_back` is the overshoot.** The character squashes to 0.7 vertical scale, then *bounces past* 1.0 to ~1.04, and settles back to 1.0. The overshoot is the *life*. Without it, the squash recovers linearly and feels rubbery. With it, the squash recovers with a tiny *pop* and feels springy.
3. **`scale_y` is applied at draw time.** Not in the physics. Not on the collision rect. Just on the visual frame. `pygame.transform.scale_by(frame, (1.0, scale_y))` and blit. The hitbox does not deform; the art does.

Tuning: a 120 ms squash with `ease_out` and a 180 ms recovery with `ease_out_back` is the canonical *Celeste*-style feel. Halve the durations and the character feels twitchier. Double them and the character feels gummy. Tune by feel.

---

## 5. Screen shake: three parameters, two random calls

Screen shake is the single most-cited juice trick in Nijman's *Screenshake* talk, and it is the *cheapest* juice trick in the whole budget.

```python
from dataclasses import dataclass
import random


@dataclass
class ScreenShake:
    amplitude: float = 0.0
    duration: float = 0.0
    elapsed: float = 0.0

    def kick(self, amp: float, dur: float) -> None:
        # If a stronger kick fires while a weaker one is active, take the
        # stronger. Don't add — kicks aren't additive; they're "this is the
        # current intensity."
        if amp >= self.amplitude * self.remaining_fraction():
            self.amplitude = amp
            self.duration = dur
            self.elapsed = 0.0

    def remaining_fraction(self) -> float:
        if self.duration <= 0:
            return 0.0
        return max(0.0, 1.0 - self.elapsed / self.duration)

    def update(self, dt: float) -> None:
        self.elapsed += dt
        if self.elapsed >= self.duration:
            self.amplitude = 0.0
            self.duration = 0.0
            self.elapsed = 0.0

    def offset(self) -> tuple[float, float]:
        if self.amplitude <= 0:
            return (0.0, 0.0)
        amp = self.amplitude * self.remaining_fraction()
        return (random.uniform(-amp, amp), random.uniform(-amp, amp))
```

Three parameters, four methods, ~25 lines. Use like this:

```python
# In LandState.enter or wherever the impact happens:
char.world.shake.kick(amp=4.0, dur=0.10)

# Once per frame, before drawing:
shake_dx, shake_dy = world.shake.offset()
camera_x = round(target_camera_x + shake_dx)
camera_y = round(target_camera_y + shake_dy)
```

Tuning is everything. Nijman's defaults from the talk:

| Event              | Amplitude | Duration |
|--------------------|----------:|---------:|
| Footstep           |     0     |    0     |
| Soft landing       |   2 px    |   60 ms  |
| Hard landing       |   4 px    |  100 ms  |
| Hit (player)       |   6 px    |  150 ms  |
| Hit (heavy enemy)  |  10 px    |  200 ms  |
| Explosion (small)  |  14 px    |  250 ms  |
| Explosion (boss)   |  24 px    |  400 ms  |

24 px is the *maximum*; the talk explicitly warns against going higher. Players notice screen shake at amplitude 2; players are *annoyed* by screen shake at amplitude 16+; players *can't read the screen* at amplitude 24+. The dose matters more than the formula.

Two other tuning notes:

- **`round()` the camera offset.** Floating-point camera positions cause sub-pixel jitter that looks like a *vibrating* shake, not an *impact* shake. Round to the nearest pixel.
- **Decay matters more than amplitude.** A 6-pixel shake that decays linearly over 150 ms feels less impactful than a 4-pixel shake that decays as `(1 - t/duration)^2` (quadratic). The implementation above uses linear decay because it's simpler; the exercise lets you swap to quadratic and feel the difference.

---

## 6. Particle emitter: a flat list, integrated like the player

A particle is a short-lived sprite with position, velocity, lifetime, and per-frame integration. Burst-spawned on impact, footsteps, hits. The shape:

```python
from dataclasses import dataclass


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    lifetime: float       # seconds remaining
    max_lifetime: float
    radius: float = 2.0
    color: tuple[int, int, int] = (200, 200, 220)
    gravity: float = 600.0

    def alive(self) -> bool:
        return self.lifetime > 0

    def update(self, dt: float) -> None:
        self.lifetime -= dt
        self.vy += self.gravity * dt
        self.x += self.vx * dt
        self.y += self.vy * dt


class ParticleField:
    def __init__(self) -> None:
        self.particles: list[Particle] = []

    def emit_dust(self, x: float, y: float, count: int = 6) -> None:
        for _ in range(count):
            self.particles.append(Particle(
                x=x + random.uniform(-3, 3),
                y=y,
                vx=random.uniform(-60, 60),
                vy=random.uniform(-120, -40),
                lifetime=random.uniform(0.25, 0.45),
                max_lifetime=0.45,
                radius=random.uniform(1.5, 3.0),
                color=(180, 170, 160),
                gravity=400.0,
            ))

    def emit_blood(self, x: float, y: float, count: int = 12) -> None:
        for _ in range(count):
            self.particles.append(Particle(
                x=x, y=y,
                vx=random.uniform(-220, 220),
                vy=random.uniform(-320, -80),
                lifetime=random.uniform(0.35, 0.7),
                max_lifetime=0.7,
                radius=random.uniform(2.0, 3.5),
                color=(219, 39, 119),  # Coin Pink for the C11 visual identity
                gravity=900.0,
            ))

    def update(self, dt: float) -> None:
        # Tick all; reap dead.
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.alive()]

    def draw(self, screen, camera_offset: tuple[float, float] = (0, 0)) -> None:
        ox, oy = camera_offset
        for p in self.particles:
            # Fade out as lifetime decreases.
            alpha_frac = max(0.0, p.lifetime / p.max_lifetime)
            r = max(0.5, p.radius * (0.4 + 0.6 * alpha_frac))
            pygame.draw.circle(
                screen, p.color,
                (int(p.x + ox), int(p.y + oy)),
                int(r))
```

The class is a *flat list*. Append on emit; filter on update. Up to ~500 alive particles, the flat list is well under 0.5 ms per frame. Above that, you want **object pooling** (Nystrom, chapter "Object Pool" — linked in `resources.md`) to avoid the allocation churn. Pooling is a Week 11 optimisation.

Three tuning notes:

- **Particles are spawned by `enter()` hooks**, not by physics. `LandState.enter` or `IdleState.enter` (when arriving from airborne) calls `world.particles.emit_dust(char.x + PLAYER_W/2, char.y + PLAYER_H, count=8)`. The presentation lives where the state begins.
- **Colour matters.** Dust particles for footsteps are subtle (tan, low-alpha). Impact particles for a kill are saturated (Coin Pink for our C11 visual). The *colour* tells the player what *kind* of event just happened, even faster than the shape does.
- **Gravity per-particle, not global.** Some particles fall (dust, debris). Some float upward (smoke, sparks). Some have zero gravity (magic dust). Per-particle `gravity` is a cheap field that unlocks every effect.

---

## 7. Sound cues bound to FSM transitions

Audio juice is the same shape as visual juice: bound to the FSM's `enter()` and `exit()`. The pattern:

```python
class JumpState(AirborneState):
    def enter(self, char):
        char.vy = -JUMP_VEL
        char.grounded = False
        char.anim.play("jump_launch", restart=True)
        char.sfx.play_one_shot("jump")    # <- here

class RunState(State):
    def enter(self, char):
        char.anim.play("run_loop")
        char.sfx.play("footsteps_loop", loop=True, volume=0.3)   # <- here

    def exit(self, char):
        char.sfx.stop("footsteps_loop")   # <- here

class HurtState(State):
    def enter(self, char):
        char.anim.play("hurt_react", restart=True)
        char.sfx.play_one_shot("hit")     # <- here
        char.invincible = True

    def exit(self, char):
        char.invincible = False
```

One-shots (`play_one_shot`) fire and forget; the SFX system handles overlap. Loops (`play(name, loop=True)`) must be matched with a `stop` in `exit`. Forgetting the `stop` is the canonical "footsteps that keep playing while the player is jumping" bug — Lecture 1 of Week 5 named it the *forgotten exit-action* and predicted this exact case.

A minimal `SFX` shim sits on the character:

```python
class SFX:
    def __init__(self, library: dict[str, pygame.mixer.Sound]) -> None:
        self.library = library
        self.loops: dict[str, pygame.mixer.Channel] = {}

    def play_one_shot(self, name: str, volume: float = 1.0) -> None:
        snd = self.library.get(name)
        if snd is None:
            print(f"[sfx] missing one-shot: {name}")
            return
        snd.set_volume(volume)
        snd.play()

    def play(self, name: str, loop: bool, volume: float = 1.0) -> None:
        snd = self.library.get(name)
        if snd is None:
            print(f"[sfx] missing loop: {name}")
            return
        if name in self.loops and self.loops[name].get_busy():
            return  # already playing
        snd.set_volume(volume)
        ch = snd.play(loops=-1 if loop else 0)
        if loop:
            self.loops[name] = ch

    def stop(self, name: str) -> None:
        ch = self.loops.pop(name, None)
        if ch is not None:
            ch.stop()
```

The full audio mixing lecture is Week 10. For this week, "play this on transition" is enough.

If you don't have sound files handy, **stub out the SFX with `print` statements**. The architectural commitment is what matters this week:

```python
class SFX:
    def play_one_shot(self, name: str, volume: float = 1.0) -> None:
        print(f"  [sfx] {name}")

    def play(self, name: str, loop: bool, volume: float = 1.0) -> None:
        print(f"  [sfx] {name} (loop)")

    def stop(self, name: str) -> None:
        print(f"  [sfx] {name} stop")
```

Same hook points, no asset dependency. The exercises use the stub. The mini-project uses real sounds (Kenney's *Impact Sounds* pack is 50 MB, CC0, linked in `resources.md`).

---

## 8. The Nijman *Screenshake* checklist

Jan Willem Nijman's 2013 GDC Europe talk *The Art of Screenshake* enumerates twenty cheap juice tricks. We don't implement all twenty this week. We implement six. The rest are stretch.

Implement (this week):

1. **Sprite-sheet animation** with FSM-bound clips. (Lecture 1.)
2. **Squash-and-stretch** on jump and land via scale tween. (This lecture, §4.)
3. **Screen shake** on landings, hits, and explosions. (§5.)
4. **Particle bursts** on landings (dust) and hits (impact). (§6.)
5. **Sound cues** bound to FSM `enter()`. (§7.)
6. **Hit-flash** — the player sprite tinted red for one frame after damage. (Trivially implemented; one boolean and a conditional `tint` blit.)

Defer to stretch goals:

7. **Hit-stop** — pause the world for 50-80 ms on a successful hit. Five lines of code; a boolean on `App`.
8. **Coyote time** — 80 ms grace window after walking off a ledge during which jump still works.
9. **Jump buffer** — 80 ms window before landing during which an early jump-press is queued.
10. **Chromatic aberration** — three colour-shifted draws of the player offset by 1-2 pixels for 80 ms after a hit.
11. **Speed lines** — particles emitted *behind* a fast-moving character.
12. **Trail / ghost** — the previous N frames of the character drawn faded behind the current frame.
13. **Random pitch variation on SFX** — every `play_one_shot` plays at `pitch * uniform(0.95, 1.05)`. The same sound becomes *alive* instead of *robotic*.
14. **Random volume variation** — same trick on volume.
15. **Knockback on hit** for the *hitter* as well as the hit-ee.
16. **Camera lean** — the camera offsets slightly in the direction of fast motion, creating a *speed lean*.
17. **Variable jump height** — releasing jump early cuts the upward velocity (`vy *= 0.5` if vy < 0 and jump released). The single biggest "game feel" payoff for a platformer.
18. **Permanent particles** — every state transition emits one or two small particles for ambient life.
19. **UI-bumps on score change** — the score-counter pops with `ease_out_back` when it changes.
20. **Death pause** — when the player dies, the world pauses for 300 ms before the respawn animation.

Six this week. Twelve more this month if you're working through the stretch goals. All twenty in a year, if you build games on the side. The lecture is the *map*; the practice is the *territory*.

Watch Nijman's full talk. It's thirty minutes. He demos every one of these on a stage with a Vlambeer prototype.

---

## 9. Swink's three pillars (revisited)

Steve Swink's *Game Feel* (Morgan Kaufmann, 2009) defines game feel as the intersection of three pillars:

1. **Real-time control.** The player's inputs map to character actions within ~50 ms with no perceived lag. The *response* feel.
2. **Simulated physical space.** The character has mass, momentum, friction. The character feels *embodied*. Gravity matters; inertia matters. The *physical* feel.
3. **Polish.** The feedback the game gives the player beyond the mechanical outcome. Animations, sounds, particles, screen shake, squash-and-stretch. The *juice* feel.

The first two are mostly Weeks 1-5 territory. This week's pillar is the third. But notice: polish *requires* the first two to work. Squash-and-stretch on a character that doesn't respond to input within 50 ms is *icing on a brick*. A particle burst on a hit that doesn't register as a hit is *decoration on a misfire*. Juice is the third pillar; the first two are the foundation.

This is why we did Weeks 1-5 before Week 6. By the time you add juice, the game already *plays well*. The juice makes a good-playing game *feel* good. It does not rescue a bad-playing one.

---

## 10. Tuning: the dose-response curve

Every juice trick has a knob. The knob has a *taste* setting that is rarely the maximum. The discipline is to tune until the player *notices the effect when present and doesn't notice it when absent* — and stop there.

A simple methodology:

1. **Add the trick at its canonical default** (footstep shake = 0, jump squash = 1.0 → 0.7 over 120 ms, hit particles = 12, etc.).
2. **Play for sixty seconds.** Don't analyse; play.
3. **Crank the knob to 200% of default.** Play for sixty seconds. Note your reaction.
4. **Crank the knob to 50% of default.** Play for sixty seconds. Note your reaction.
5. **Pick the setting that feels *present but not loud*.** Default is usually right. If you're cranking past 150% you've usually got a different problem (lack of contrast, lack of audio, lack of animation).
6. **Have a friend play.** Their face is the dose-response curve. If they wince at the shake, lower it. If they don't notice the squash, raise it.

The mini-project this week is *all tuning*. The code is short; the play is long.

---

## 11. The "before/after" video is the deliverable

You can't ship juice via a code commit. The artefact is the *before-and-after side-by-side video*. The Week 5 mini-project was the "before"; this week's mini-project is the "after." Record both sitting next to each other. The diff is the lecture's whole point.

Format:

- 25-40 seconds.
- Same player input on both sides. Side-by-side or stacked.
- Label "Week 5: bones" / "Week 6: juice."
- Walk, jump, take a spike hit. Show every juice trick at least once.

Tools: any screen recorder (OBS Studio is free, cross-platform, three minutes to set up). Edit in any video editor that supports side-by-side composition (DaVinci Resolve is free; the simpler version: record both runs separately and stack them in any web video tool).

The video is your portfolio piece. It is also Saturday's deliverable. Don't leave it for Sunday morning.

---

## 12. The three classic juice bugs

Three patterns to know.

**Bug 1: too much.** Every knob at maximum. The screen shakes on every footstep; particles fill the screen; the character flashes every frame. The player can't see the game. The fix: dose. Cut every knob by 50% and re-test.

**Bug 2: too uniform.** The same shake, the same particle burst, the same SFX for every action. The player stops noticing. The fix: differentiate. A footstep is a soft thud and three dust particles; a hard land is a thud-plus-shake and six dust particles plus a 100 ms screen shake; a hit is a heavy thump, blood particles, a flash, and a 150 ms shake. Different doses for different events.

**Bug 3: lag.** The juice fires late. The hit lands, then 80 ms later the particles appear, then the screen shakes for 200 ms. The cause: code ordering. The juice must fire *in the same frame* as the event. The fix: bind to the FSM `enter()` hook, which runs *during* the transition, not after.

Watch for all three this week. The mini-project rubric calls each one out.

---

## 13. What you should write after this lecture

Before you open the exercises, do this on paper:

1. **List the juice tricks you'll implement** for your Week-5 character. Use the six-of-twenty list from §8 as your baseline.
2. **For each trick, write its dose.** Amplitude / duration / count / colour. Don't tune in code; tune in your head first.
3. **List the FSM `enter()` and `exit()` hooks** you'll edit. Each trick fires from a specific hook. Write the binding.
4. **List the SFX cues.** Six maximum for this week. Jump, land-soft, land-hard, hit, footsteps-loop, hurt.
5. **Now open the exercises.** They build the pieces; the mini-project assembles them.

---

## What you should take away

- `lerp(a, b, t)` is the two-line function that runs the world. Memorise it.
- Five easing curves cover 90% of game work: `linear`, `ease_in`, `ease_out`, `ease_in_out`, `ease_out_back`.
- A `Tween` is `lerp` + easing + a duration. Twelve lines.
- Squash-and-stretch is a scale tween bound to `enter()`. The hitbox doesn't deform; the art does.
- Screen shake is three parameters and two `random.uniform()` calls. Tune the dose, not the formula.
- Particles are a flat list, integrated like the player, spawned by `enter()` hooks. Up to ~500 alive is free.
- Sound cues live in `enter()` (one-shots) and pair with `exit()` (loop stops). Never outside the FSM.
- Nijman's *Screenshake* checklist has twenty tricks; we implement six. The other fourteen are stretch.
- Swink's three pillars: real-time control, simulated physical space, polish. This week is the polish pillar; the others were Weeks 1-5.
- The dose is the work. Code is mechanical. Taste is craft. Tune by feel, with a friend at the controls.
- The artefact is a *before/after side-by-side video*, not a commit message. Record both. The diff is the lecture.

Continue to [the exercises](../exercises/) and pick up exercise-01.
