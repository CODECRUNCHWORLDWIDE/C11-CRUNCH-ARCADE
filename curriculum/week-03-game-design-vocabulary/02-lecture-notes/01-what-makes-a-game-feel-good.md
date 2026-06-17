# Lecture 1 — What Makes a Game Feel Good

> **Duration:** ~2 hours of reading + hands-on.
> **Outcome:** You can define **game feel** in Steve Swink's terms, list its three pillars, name at least five juice techniques, and explain why each one is information rather than decoration.

If you only remember one thing from this lecture, remember this:

> **Juice is information, not decoration.** Every screen shake, every particle burst, every "thump" of audio answers a question the player asked: *what happened, how big was it, was that good or bad?* A juice effect that doesn't answer a question is noise, and noise costs trust.

---

## 1. What is "game feel"?

If you have played a game that felt *right* and another that felt *off*, you already know game feel. The thing that's harder is naming what differs. Until 2009, the industry mostly didn't have words for it; designers said "it has that thing" and moved on. Then Steve Swink wrote *Game Feel: A Game Designer's Guide to Virtual Sensation* and gave us a definition we can build from.

> **Game feel** (Swink, 2009): *real-time control of virtual objects in a simulated space, with interactions emphasised by polish.*

Unpack that. Three claims:

1. **Real-time control.** The player presses a button and something happens *now*. Not on the next frame. Not after a 200 ms animation. Now.
2. **A simulated space with rules.** The character has a position, a velocity, an acceleration. It collides with walls. It is subject to the world's physics. The world is consistent.
3. **Polish.** The visual and audio layer that sells (1) and (2). A jump with no sound, no squash, and no dust cloud is mechanically a jump and perceptually nothing. A jump with all three is *a jump*.

Notice that Swink's definition doesn't say "it feels good." Feel-good is the *outcome* of getting all three right. The definition gives you the *inputs* — three things you can name and tune.

We're going to spend this lecture on the third pillar, **polish**, because it's the one your Week 2 brick-breaker is missing and the one you'll add in this week's mini-project. But the first two pillars matter just as much, and ignoring them is the single biggest beginner mistake: **a juicy bad game is still a bad game.** Get the controls right first. Then juice them.

---

## 2. Why "feel" is measurable, not vibes

Swink's contribution wasn't the term — designers had been using it for years. His contribution was the claim that **feel can be decomposed and measured.** Every aspect of game feel can be expressed as a response curve, a delay, a magnitude, or a count. You can graph it. You can A/B test it. You can write unit tests against it (sort of — bear with us).

Examples:

- **Input response time.** From key-press to first visible character movement. 0 ms feels instant. 16 ms (one frame) is the floor for "perfect." 50 ms feels sluggish. 200 ms feels broken. You can measure this with a high-speed camera or a test harness.
- **Acceleration curve.** When a character starts moving, does it snap to top speed (Mario in NES Mario) or ramp up over 300 ms (early Sonic)? Both are choices. Neither is wrong. They feel *different*.
- **Bounce restitution.** Last week you set a number between 0 and 1 to control how much energy a ball loses on bounce. That number *is* feel. Tune it from 0.5 to 0.9 and play the game; the ball goes from "dead" to "perky."
- **Screen shake magnitude.** Pixels of camera offset on a hit. 1 px is invisible. 4 px is a flinch. 16 px is a critical hit. Beyond 24 px the player loses the ball, which is bad in a brick-breaker.

This is the headline: **every "vibe" you have ever felt about a game corresponds to a number, somewhere in the code.** You can find that number, change it by 10%, and re-test. That's the craft.

---

## 3. The three pillars in detail

### 3.1 Input response (the spine)

If only one pillar is right, make it this one. The player's brain checks for response within a window of roughly 100 ms. Inside that window, the player feels in control. Outside it, they feel like the game is responding to someone else.

What helps:

- **Read input every frame.** No batching. No "process input every other frame to save CPU." That's a 33 ms response time floor on a 60-fps game.
- **Apply input to velocity, not position.** A keypress changes intent, not place. The simulation then moves the character based on that intent. This sounds pedantic; it makes the difference between a character that *snaps* and one that *responds*.
- **Buffer input by 1-2 frames.** If the player presses Jump 1 frame before they land, the game should still jump. This is *coyote time* and *jump buffering*, and AAA platformers ship with both because beginners hate landing-and-then-falling-because-they-pressed-too-early.
- **Decouple update rate from render rate.** Last week's `dt`-correct movement is the foundation. If you ever feel input lag, profile your render loop; it's probably stealing your input window.

What hurts:

- **A long startup animation.** "Press jump, wait for the wind-up, then jump" is fine for *Dark Souls*. It is wrong for a platformer where the player presses jump 4 times per second.
- **Dead zones bigger than 10%.** On controllers, anything past 10% on the stick should produce *some* movement. Otherwise the player feels like the stick is "unresponsive" when it's actually just being filtered.
- **Modifying input on the next frame.** A common bug: you set `vel.x = 200` in the input phase but the update phase has already run for this frame, so the movement appears 16 ms later than it should. Read input *first* in the frame, then update.

### 3.2 Simulated space (the world)

The character lives somewhere. That somewhere has rules. The rules need to be consistent enough that the player can *predict* what will happen — but textured enough that prediction is sometimes wrong and the player is delighted.

What helps:

- **A clear physical model.** Velocity in px/s. Acceleration in px/s². Gravity is a constant. You can describe the world to a friend in two sentences.
- **Stable collision response.** A ball hitting a wall *always* bounces. A character standing on a floor *never* falls through. The bugs you fixed in Week 2 weren't just bugs — they were violations of the player's trust in the simulation.
- **Restitution coefficients tuned to the game.** A brick-breaker ball with restitution 1.0 is correct; the ball never loses energy on a wall. A bouncing slime with restitution 0.7 is correct; it loses energy. Pick the right value for the role.
- **Friction or no friction, consistently.** A top-down game where the character coasts after release is a different game from one that stops on a dime. Pick one. Don't mix.

What hurts:

- **Invisible walls.** The player can see they should be able to walk somewhere, but they can't. Trust gone.
- **Inconsistent restitution.** The ball bounces high off one brick and low off another for no visible reason. Trust gone.
- **Hidden state.** A character that "remembers" some flag from 30 seconds ago and behaves differently because of it, with no visible cue. Trust gone.

### 3.3 Polish (the seller)

This is the layer this week is about. The simulation is correct; the polish makes the simulation *visible*. Some named techniques:

- **Screen shake.** Decaying camera offset on impact. Magnitude tied to event strength.
- **Particle bursts.** Short-lived drawables spawned at the impact point. Direction tied to the impact normal.
- **Hit-stop.** A 1-3 frame pause of the simulation on a big hit. The whole world freezes for a heartbeat.
- **Squash and stretch.** The character or ball briefly deforms on impact or acceleration. Disney animators figured this out in 1937.
- **Audio cue.** A short sound on every meaningful event. Different pitches for different events.
- **Screen flash.** A brief full-screen colour overlay on a big event (taking damage, scoring, level-up).
- **Camera nudge.** A small, persistent camera offset toward the action — the camera "leans" toward what matters.
- **Tween easing.** Movements don't go in straight lines at constant speed; they accelerate and decelerate. *In-out cubic* is the safest default.

We'll implement the first three in this week's mini-project (screen shake, particle burst, audio cue). The others are Week 6.

---

## 4. Juice as a signal-to-noise problem

Here is the trap that beginners fall into: they add every effect they read about, and the game becomes a slot machine. Every action sprays particles, shakes the screen, plays a sound, and flashes a colour. Within thirty seconds the player's brain learns to *filter all of it out*, and you're back to zero communication — but now your frame budget is 3 ms tighter.

> Juice is a signal. Every signal needs a quiet background to be visible against.

Rules of thumb:

1. **Reserve big effects for big events.** If a normal brick destruction gets 6 px of screen shake, a power-up brick gets 14 px. The *difference* tells the player something. If every brick is 14 px, no brick is special.
2. **Decay matters more than peak.** A 12-px shake that decays over 300 ms reads as "impact." A 4-px shake held for 5 seconds reads as "my game crashed."
3. **One channel per question.** Screen shake = "how hard was the hit?" Particles = "where did the hit happen?" Audio = "what type of hit was it?" If you put all three on the same axis, you're spending three signals on one piece of information.
4. **Tune to the smallest event, then scale up.** Set the minimum effect to barely-noticeable. Set the maximum to "obviously this was important." Everything in between is a linear (or curved) interpolation.

This is also why we say **the simulation is correct first, the juice second.** Juice cannot fix a broken simulation. It can amplify the things the simulation does right, but if the simulation is wrong, the juice just makes the wrongness louder.

---

## 5. Measuring juice — three concrete numbers

These are the numbers we will use for the rest of the week. Memorise them, then ignore them once your taste catches up.

| Effect | Tiny event | Medium event | Big event |
|--------|-----------:|-------------:|----------:|
| **Screen shake magnitude** | 2 px | 6 px | 14 px |
| **Screen shake duration** | 80 ms | 200 ms | 350 ms |
| **Particle count** | 4 | 12 | 30 |
| **Particle lifetime** | 200 ms | 400 ms | 700 ms |
| **Audio volume (0–1)** | 0.4 | 0.7 | 1.0 |
| **Hit-stop duration** | 0 ms | 30 ms | 80 ms |

These numbers come from playtesting our reference brick-breaker plus skimming the source of *Vlambeer's Nuclear Throne* and *Spelunky*. They are not laws. They are the kind of numbers you should be able to *recognise* are reasonable when you see them — and to *change* when your specific game asks for something different.

---

## 6. Screen shake — the canonical implementation

Screen shake is the cheapest, most visible juice technique. Here is a small Pygame implementation. You will paste a variant of this into the mini-project this week.

```python
import random
import pygame

class ScreenShake:
    """A decaying camera-offset effect.

    Call ``trigger(strength)`` on an event. Each frame, call
    ``update(dt)`` once and ``offset()`` to get the (dx, dy) you blit
    the world with.
    """

    def __init__(self) -> None:
        self.magnitude = 0.0
        self.duration_left = 0.0
        self.duration_total = 0.0

    def trigger(self, strength: float, duration: float = 0.2) -> None:
        # Only let bigger shakes override smaller ones. A new event
        # should not shorten an existing big shake.
        if strength > self.magnitude:
            self.magnitude = strength
            self.duration_left = duration
            self.duration_total = duration

    def update(self, dt: float) -> None:
        if self.duration_left > 0.0:
            self.duration_left = max(0.0, self.duration_left - dt)
            if self.duration_left == 0.0:
                self.magnitude = 0.0

    def offset(self) -> tuple[int, int]:
        if self.duration_left <= 0.0:
            return (0, 0)
        # Linear decay: at t=0 full strength, at t=duration zero.
        t = self.duration_left / self.duration_total
        current = self.magnitude * t
        return (
            int(random.uniform(-current, current)),
            int(random.uniform(-current, current)),
        )
```

A few things to notice:

- **Decay is linear** here for simplicity. A more expressive choice is `t * t` (quadratic) so the shake "settles" faster. Try both.
- **The random offset is recomputed every frame.** That's the *shake*. If you returned the same offset every frame you'd get a static displacement, which reads as a glitch, not a hit.
- **We don't shake the input.** The world is rendered with the offset. Player input still applies to the unshaken world. Otherwise the player feels like the controls "lurched" on impact, which is bad.

To apply it: where you normally blit the world at `(0, 0)`, blit it at `screen_shake.offset()`. Done.

---

## 7. Particles — the canonical implementation

A particle is a tiny object with a position, a velocity, and a lifetime that decays each frame.

```python
import math
import random
import pygame
from dataclasses import dataclass, field

@dataclass
class Particle:
    pos: pygame.Vector2
    vel: pygame.Vector2
    lifetime: float
    age: float = 0.0
    radius: float = 3.0
    colour: tuple[int, int, int] = (219, 39, 119)  # Coin Pink

    @property
    def alive(self) -> bool:
        return self.age < self.lifetime

    def update(self, dt: float) -> None:
        self.pos += self.vel * dt
        self.vel *= 0.96  # mild drag
        self.age += dt

    def draw(self, surface: pygame.Surface, offset: tuple[int, int]) -> None:
        # Fade-out: alpha not needed if we shrink instead.
        t = 1.0 - (self.age / self.lifetime)
        r = max(1, int(self.radius * t))
        pygame.draw.circle(
            surface,
            self.colour,
            (int(self.pos.x + offset[0]), int(self.pos.y + offset[1])),
            r,
        )


def spawn_burst(at: pygame.Vector2, count: int, speed: float = 220.0,
                lifetime: float = 0.4) -> list[Particle]:
    particles: list[Particle] = []
    for _ in range(count):
        angle = random.uniform(0, math.tau)
        v = pygame.Vector2(math.cos(angle), math.sin(angle)) * random.uniform(0.3, 1.0) * speed
        particles.append(Particle(pos=pygame.Vector2(at), vel=v, lifetime=lifetime))
    return particles
```

The full burst-on-collision pattern looks like:

```python
particles: list[Particle] = []

# ... inside your collision handler:
particles.extend(spawn_burst(hit_position, count=12))

# ... each frame:
for p in particles:
    p.update(dt)
for p in particles:
    p.draw(screen, screen_shake.offset())
particles = [p for p in particles if p.alive]
```

A few things to notice:

- **We never grow particles unboundedly.** The filter-out-dead step is mandatory. Drop it and your game leaks memory.
- **Mild drag (`vel *= 0.96`)** makes particles "settle" instead of flying off the screen. Without it, particles read as "broken pixels" rather than "debris."
- **Shrinking, not fading**, is cheaper than alpha blending. Pygame can do both; shrinking is one less surface allocation per particle.
- **The colour is Coin Pink**. We always use the brand palette for first-pass effects. Players' eyes track the colour they already know means *the player*.

---

## 8. Audio — the canonical implementation

Pygame's `mixer` is one of the rougher corners of the API. Here is the minimum-viable cue.

```python
import pygame

pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
pygame.mixer.init()

hit_sound = pygame.mixer.Sound("assets/audio/hit.wav")
hit_sound.set_volume(0.7)

# ... inside your collision handler:
hit_sound.play()
```

Things to notice:

- **`pre_init` before `pygame.init()`** with `buffer=512`. The default is `4096`, which produces a 90 ms latency. 512 samples at 44.1 kHz is ~12 ms — perceptible only as "instant." This is the single most-skipped fix in beginner Pygame projects, and it ruins juice for everyone who skips it.
- **`set_volume(0.7)`** for medium events, 1.0 for big, 0.4 for ambient. Match the table in §5.
- **Don't load the sound in the collision handler.** Load it once at startup; cache the `Sound` object. Loading from disk in a hot path is a frame-time crime.
- **Pitch variation costs you nothing.** If you play the same hit sound 50 times in a row at the same pitch, the player's brain starts filtering it. Vary it: `hit_sound.set_volume(random.uniform(0.5, 0.9))`. Better yet, ship 3 hit sounds and pick one at random.

---

## 9. Putting it together — the event-bus pattern

Once you have three effect systems (shake, particles, audio), you do not want to call all three from every collision handler. You want to fire one *event*, and have three listeners respond. This is the **Observer pattern** from Nystrom's *Game Programming Patterns* — read [the chapter](https://gameprogrammingpatterns.com/observer.html) if you haven't.

The simplest event bus is a list of callables:

```python
from typing import Callable

class EventBus:
    def __init__(self) -> None:
        self._listeners: dict[str, list[Callable]] = {}

    def on(self, event: str, fn: Callable) -> None:
        self._listeners.setdefault(event, []).append(fn)

    def emit(self, event: str, **kwargs) -> None:
        for fn in self._listeners.get(event, ()):
            fn(**kwargs)


bus = EventBus()

bus.on("brick_destroyed", lambda pos, **_: screen_shake.trigger(6.0, duration=0.2))
bus.on("brick_destroyed", lambda pos, **_: particles.extend(spawn_burst(pos, count=12)))
bus.on("brick_destroyed", lambda **_: hit_sound.play())

# ... in your collision handler, all you write is:
bus.emit("brick_destroyed", pos=brick_centre)
```

This is overkill for this week's mini-project — three direct calls are fine. But you will want this pattern by Week 6, and the time to learn it is *before* the game has 50 event types. We are flagging it now.

---

## 10. Recap: what to take away

- **Game feel** has a definition: real-time control + simulated space + polish (Swink, 2009).
- **Juice is information, not decoration.** Every effect answers a player question.
- **Three pillars, in order of importance**: input response → simulated space → polish.
- **Five named techniques** worth knowing: screen shake, particle burst, hit-stop, squash-and-stretch, audio cue.
- **Reference magnitudes**: small / medium / big events get distinct numbers; reserve big effects for big events.
- **Implement small, tune by hand, playtest with one human** before you trust your own feel.

The next lecture moves up a level. Instead of "what makes a *hit* feel good?" we ask "what makes a *game* feel like a game?" That's the four-lenses framework and MDA, and it's the vocabulary you'll use in the rest of the course every time you have to defend a design choice.

---

*Lecture written for C11 · Crunch Arcade. Cite Steve Swink (Game Feel, 2009) when you reproduce any of these definitions.*
