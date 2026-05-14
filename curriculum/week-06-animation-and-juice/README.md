# Week 6 — Animation and Juice

Last week you wired the bones. A four-state player whose behaviour is structured by code shape, not by accident. It walks, it jumps, it takes a hit, it recovers. It is *correct*. It also looks like a rectangle sliding on a rectangle. Show it to a non-programmer friend and watch the polite face they make.

This week we paint the muscles. Sprite-sheet animation. Tweens. Easing curves. Screen shake. Particles on landing. A red flash on hit. A little upward squash before the jump and a thump when you land. Footstep dust puffs. A subtle camera lean. The transitions you wired last week become the moments where the *art* happens. The `enter()` of `JumpState` starts a clip, the `exit()` stops it. The `enter()` of `HurtState` triggers a hit-flash. The `enter()` of `LandState` (the one-frame land-squash you're about to add) fires a dust puff and a 3-pixel screen shake. The architecture is from Week 5; the *behaviour you can feel* is from this week.

The word for all of that is **juice**, and it has a clear definition: any feedback the game gives you that confirms the action you just took, beyond the mechanical outcome. The mechanical outcome of "press jump" is `vy = -650`. The juice is the squash-and-stretch sprite, the dust puff at your feet, the woosh sound, the trail behind your head, the camera lean into the apex, and the thump-plus-shake on landing. None of that changes the physics. All of it changes how the game *feels* to the player. Two games can ship with identical code and one will be loved and the other will not, and the difference is juice.

We do not invent the vocabulary. **Steve Swink's *Game Feel* (2009)** is the canonical text, and his three-pillar definition — *real-time control*, *simulated physical space*, *polish* — is the spine of the week. **Jan Willem Nijman's *The Art of Screenshake* GDC talk (2013, 30 min)** is the canonical demo: he ships the same Vlambeer game twice in thirty minutes, once without juice and once with every juice trick stacked, and the difference is staggering. **Martin Jonasson and Petri Purho's *Juice it or lose it* talk (2012)** is the eight-minute companion piece every game-feel lecture cribs from. All three are free; all three are in `resources.md`; you will watch all three this week.

By Sunday you ship a **juice pass on your Week-5 character**: animations driven by sprite sheets and bound to states, tweened squash-and-stretch, screen shake on impact, particle dust puffs, sound cues fired on transitions, and a "before/after" comparison video. The video is the deliverable. Anyone can claim "I added juice." A 25-second side-by-side comparison is the difference between a claim and an artefact.

There is still no Godot. The Pygame foundation now has a *feel* layer on top of it, and when we re-implement this player in Godot 4 in Week 9, you will already know what good feels like.

## Learning objectives

By the end of this week, you will be able to:

- **Define** "juice" using Swink's three pillars (real-time control, simulated physical space, polish) and identify which pillar a given polish feature serves.
- **Implement** sprite-sheet animation in Pygame: a `SpriteSheet` loader, an `Animation` class with `frames`, `fps`, and `loop`, and a `play()`/`update(dt)` lifecycle that returns the current frame.
- **Bind** animation playback to FSM transitions: `enter()` calls `anim.play("run_loop")`; `exit()` stops or fades. This is the Week 5 → Week 6 bridge made explicit.
- **Implement** a `tween()` function from scratch: `lerp`, `ease_in`, `ease_out`, `ease_in_out`, and `ease_out_back` (the overshoot curve). Plot the curves on paper before coding.
- **Apply** squash-and-stretch on jump and land using a scale tween driven by a 200 ms duration.
- **Implement** screen shake with three parameters: `amplitude`, `duration`, `decay`. Fire it on landings, hits, and explosions; tune so it reads as impact, not earthquake.
- **Implement** a particle emitter as a list of dataclass particles with position, velocity, lifetime, and per-frame integration. Spawn on landings, footsteps, and hits.
- **Trigger** sound cues from FSM transitions. The `enter()` of `JumpState` plays "jump"; `exit()` of `RunState` stops "footsteps." No `play_sound("hit")` scattered through the physics code.
- **Compare** a before-juice and after-juice version of the same game and articulate, in writing, which juice tricks contributed the most to the feel — and which were noise.
- **Frame-budget** the juice pass: the animation update is ~0.3 ms, the particle pass is ~0.5 ms, the screen-shake math is essentially free. Juice is cheap; the question is taste, not performance.

## Prerequisites

This week assumes you have completed **Weeks 1, 2, 3, 4, and 5**. Specifically:

- You have a Week 5 mini-project repo with a four-or-five-state player driven by the State pattern (`IdleState`, `RunState`, `JumpState`, `FallState`, optionally `HurtState`). You can run it.
- Each state class has `enter()`, `update()`, and `exit()` methods. The slots exist whether or not their bodies do.
- You understand `dt`-correct integration from Weeks 1 and 2.
- You can load an image in Pygame with `pygame.image.load(...).convert_alpha()`.
- You have at least one `.wav` or `.ogg` sound file lying around. If you don't, **Kenney's *Interface Sounds*** and ***Impact Sounds*** packs are CC0 and 50 MB total; download them now.

If any of those are shaky, do the previous week's mini-project before continuing.

## Topics covered

Lecture 1 — Sprite-sheet animation:

- The single PNG with a grid of frames: why a sheet is the right shape (not 30 PNGs in a folder).
- The `SpriteSheet` loader: a `pygame.Surface` plus `frame_w`, `frame_h`, `cols`, `rows`, and a `frame(i)` method that returns a subsurface.
- The `Animation` class: a list of frame indices, an `fps`, a `loop` flag, an `elapsed_t` counter, and a `current_frame()` method.
- Binding animations to FSM states: `IdleState.enter()` calls `char.anim.play("idle_breathing")`; `exit()` is a `pass`. The architectural bridge from Week 5.
- Frame-rate-independent animation: `elapsed_t` ticks in seconds; current frame is `int(elapsed_t * fps) % len(frames)`. Never tied to render frame count.
- One-shot animations (jump launch, attack, hit-react) vs looping animations (idle, run): the `loop=False` path and the "completed" signal that fires the *next* state transition.
- A small frame-budget tile: 60 fps animation update is ~0.1 ms for one character, ~0.3 ms for a dozen. Animation is *cheap*; the question is which frames to draw.

Lecture 2 — Tweening, easing, and juice:

- The two-line `lerp(a, b, t)` and why it is the most-used function in game programming.
- Easing curves: `ease_in`, `ease_out`, `ease_in_out`, `ease_out_back` (the overshoot). Each is a one-line function applied to `t` before the lerp. Plot them on paper.
- The `tween()` driver: a small class with `start`, `end`, `duration`, `elapsed`, `ease`, and `value()` and `done()`. Six fields, twelve lines. Drives squash, slide, fade, pop.
- Squash-and-stretch on jump and land: a 200 ms scale tween. `enter()` of `JumpState` kicks off `tween_scale(1.0, 0.7, 0.1, ease_out)`; `exit()` reverses.
- Screen shake: `amplitude`, `duration`, `decay`. The camera offset is `(uniform(-amp, amp), uniform(-amp, amp)) * (remaining/duration)`. Fire it on landings, hits, kills.
- Particles: a flat `list[Particle]` integrated like the player. Spawned by FSM `enter()` hooks. Pooling is a Week-11 optimisation; for this week the list is fine up to a thousand particles.
- Sound cues bound to transitions: `enter()` plays one-shots, `exit()` stops loops. No `play_sound` outside the FSM.
- The Nijman *Screenshake* checklist: a list of twenty cheap polish tricks. We don't implement all twenty this week. We implement six and the rest are stretch.
- The "less is more" reminder: every juice trick has a *dose*. Too much screen shake is migraine-inducing. Too many particles is fog. Taste is the work; the code is mechanical.

## Weekly schedule

The schedule below adds up to approximately **34 hours**. Treat it as a target. Juice is the kind of topic that looks simple on the spec and consumes a full Saturday once you start tuning numbers.

| Day       | Focus                                            | Lectures | Exercises | Challenges | Quiz/Read | Homework | Mini-Project | Self-Study | Daily Total |
|-----------|--------------------------------------------------|---------:|----------:|-----------:|----------:|---------:|-------------:|-----------:|------------:|
| Monday    | Lecture 1 + sprite-sheet loader                  |    2h    |    1.5h   |     0h     |    0.5h   |   1h     |     0h       |    0.5h    |     5.5h    |
| Tuesday   | Bind animations to FSM states                    |    1h    |    1.5h   |     0h     |    0.5h   |   1h     |     1h       |    0.5h    |     5.5h    |
| Wednesday | Lecture 2 + lerp/ease/tween                      |    2h    |    1.5h   |     0h     |    0.5h   |   1h     |     1h       |    0h      |     6h      |
| Thursday  | Squash, screen shake, particle emitter           |    0h    |    1h     |     1.5h   |    0.5h   |   1h     |     1.5h     |    0h      |     5.5h    |
| Friday    | Wire the juice pass into the Week-5 character    |    0h    |    0h     |     0.5h   |    0.5h   |   1h     |     2.5h     |    0.5h    |     5h      |
| Saturday  | Sound cues, before/after video, quiz             |    0h    |    0h     |     0h     |    0.5h   |   0.5h   |     2.5h     |    0h      |     3.5h    |
| Sunday    | Polish, README, push                             |    0h    |    0h     |     0h     |    0.5h   |   0h     |     2h       |    0h      |     2.5h    |
| **Total** |                                                  | **5h**   | **5.5h**  | **2h**     | **3.5h**  | **5.5h** | **10.5h**    | **1.5h**   | **33.5h**   |

## How to navigate this week

| File | What's inside |
|------|---------------|
| [README.md](./README.md) | This overview (you are here) |
| [resources.md](./resources.md) | Swink *Game Feel* free chapters, Nijman *Screenshake*, Jonasson/Purho *Juice it or lose it*, Coding Train juice videos, Kenney asset packs |
| [lecture-notes/01-sprite-sheet-animation.md](./lecture-notes/01-sprite-sheet-animation.md) | The `SpriteSheet` loader; the `Animation` class; frame-rate-independent playback; binding animations to FSM `enter`/`exit` |
| [lecture-notes/02-tweening-easing-and-juice.md](./lecture-notes/02-tweening-easing-and-juice.md) | `lerp`, easing curves, the `tween()` driver, squash-and-stretch, screen shake, particles, the Nijman *Screenshake* checklist |
| [exercises/README.md](./exercises/README.md) | Index of short coding drills |
| [exercises/exercise-01-sprite-animation.py](./exercises/exercise-01-sprite-animation.py) | A procedurally-generated 4-frame sprite sheet driving an `Animation` instance; on-screen frame counter |
| [exercises/exercise-02-tween-easing-curves.py](./exercises/exercise-02-tween-easing-curves.py) | Plot five easing curves on screen and drive five tweened squares across the window with each one |
| [exercises/exercise-03-add-juice-to-week5-character.py](./exercises/exercise-03-add-juice-to-week5-character.py) | Take the Week-5 four-state player and add squash-and-stretch, screen shake on landing, dust particles, and a sound-cue stub on every transition |
| [challenges/README.md](./challenges/README.md) | Index of weekly challenges |
| [challenges/challenge-01-before-after-juice-comparison.md](./challenges/challenge-01-before-after-juice-comparison.md) | Record a side-by-side video and write a 200-word teardown of which juice tricks earned their keep |
| [quiz.md](./quiz.md) | 10 multiple-choice questions |
| [homework.md](./homework.md) | Six practice problems for the week |
| [mini-project/README.md](./mini-project/README.md) | A full juice pass on your Week-5 character: animations, screen shake, particles, sound cues, before/after demo |

## Frame budget for this week

A reminder of what 60 fps actually means, in milliseconds. Every C11 lecture returns to this tile. This week's two new rows are animation playback and particles.

```
┌─────────────────────────────────────────────────────────┐
│  FRAME BUDGET — 60 fps target, with juice               │
│                                                         │
│  Input poll:       ~0.2 ms                              │
│  FSM dispatch:     ~0.1 ms                              │
│  Update (sim):     ~1.4 ms                              │
│  Tilemap collide:  ~0.6 ms                              │
│  Animation tick:   ~0.3 ms  (player + 11 NPCs)          │
│  Tween update:     ~0.1 ms  (≤20 active tweens)         │
│  Particles:        ~0.6 ms  (up to 400 alive)           │
│  Screen shake:     ~0.0 ms  (two random.uniform calls)  │
│  Tilemap draw:     ~1.2 ms                              │
│  Entity draw:      ~1.5 ms                              │
│  Camera apply:     ~0.1 ms                              │
│  HUD draw:         ~0.4 ms                              │
│  Audio mix:        ~0.4 ms  (6 SFX channels)            │
│  GPU + present:    ~4.0 ms                              │
│  Headroom:         ~5.7 ms                              │
│  ─────────────────────                                  │
│  Total:           ~16.6 ms / frame                      │
└─────────────────────────────────────────────────────────┘
```

The new rows — **animation tick** and **particles** — are the two cheapest *substantive* costs in the whole frame. Animation playback for a dozen characters is ~0.3 ms. Four hundred alive particles cost ~0.6 ms. Screen shake is essentially free — two `random.uniform()` calls and a draw offset. If your juice pass ever shows up on a profiler, it isn't the juice — it's the work the *art* is doing. The point of the lecture is to make that work explicit, not expensive.

## Stretch goals

If you finish early and want to push further:

- **Read Steve Swink's *Game Feel*, chapter 4 ("Polish")** in full. Swink's three pillars (real-time control, simulated physical space, polish) are the spine of the entire week; chapter 4 is the polish pillar in fifty pages. The book is on Internet Archive for borrow; the publisher's free chapter sampler is linked in `resources.md`.
- **Watch *all* of Daniel Shiffman's *Coding Train* juice videos.** Six episodes, ~90 minutes total. Daniel reads through *Game Feel* on camera and ports the examples to p5.js. You don't need p5.js — the *vocabulary* and the *demos* are what you're after.
- **Implement a `coyote_time` window.** When the player walks off a ledge, allow an 80-100 ms grace period during which `JUMP_PRESSED` still triggers a jump. This is *Celeste*-grade polish and the implementation is six lines in `FallState.enter`.
- **Implement a `jump_buffer` window.** If the player presses jump 80 ms before landing, queue the jump and fire it on land. Also six lines, also *Celeste*-grade.
- **Add a hit-stop frame.** On a successful spike hit (or a successful enemy attack), pause the world for ~50 ms. The pause makes the hit *land*. Used in every fighting game and most action platformers. A boolean on `App` (`hit_stop_t > 0`) gates the update calls.
- **Implement Nijman's "permanent particles" trick.** Every state transition emits one or two small particles that survive for 600 ms. The result is a screen that *always feels alive*. The cost: ~50 alive particles steady-state, well within the budget.
- **Add a chromatic-aberration on impact.** Three colour-shifted draws of the player offset by 1-2 pixels for 80 ms after a hit. Cheap, *very* shippable polish. Reference: the *Hyper Light Drifter* devblog (linked in `resources.md`).

## Voice rules for the week

- We define **juice** by Swink's three pillars and Nijman's checklist, not by feel. "It feels better" is the outcome, not the technique.
- We credit **Steve Swink**, whose *Game Feel* (Morgan Kaufmann, 2009) coined and popularised the vocabulary the rest of game development uses.
- We credit **Jan Willem Nijman** (Vlambeer / *Nuclear Throne*) and his GDC 2013 talk *The Art of Screenshake* — the most-cited 30-minute talk in game-feel literature.
- We credit **Martin Jonasson and Petri Purho** for the *Juice it or lose it* talk (Nordic Game Jam 2012) — the eight-minute companion piece every game-feel lecture cribs from.
- We credit **Kenney** (kenney.nl) for the CC0 sprite and sound packs we use. Always cite the source, even though Kenney's licence does not require attribution. It is *correct* to.
- We prefer **bind-presentation-to-state** over scattered effect calls. `play_sound("jump")` lives in `JumpState.enter`. Always. If you find a `play_sound` call outside an FSM hook, refactor.
- We prefer **before-and-after side-by-side video** as the artefact, not the claim. "I added juice" is a sentence. A twenty-five-second comparison clip is an argument.
- We **respect the dose**. Every juice trick has a knob; the knob has a *taste* setting that is rarely the maximum. Screen shake at amplitude 24 is a migraine. At amplitude 4 it is the feel of a fist landing. The work this week is tuning, not coding.

## Up next

Continue to [Week 7 — Save and load](../week-07/) once you've pushed your juiced Week-5 character. The reflection essay you write for Week 6 is the design diary for the rest of the course; the squash-tween code you write this week is the boilerplate every future project copies in.

---

*If you find errors in this material, please open an issue or send a PR. Future learners will thank you.*
