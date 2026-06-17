# Week 3 Homework

Six practice problems that revisit the week's topics. The full set should take about **6 hours** in total. Work in your Week 3 Git repository so each problem produces at least one commit you can point to later.

The work this week is half-coding, half-writing. Get used to producing prose alongside code; design documentation is part of the job, and this is the week we practise it.

Each problem includes:

- A short **problem statement**.
- **Acceptance criteria** so you know when you're done.
- A **hint** if you get stuck.
- An **estimated time**.

---

## Problem 1 — Apply the four lenses to a published game

**Problem statement.** Pick any published 2D game you have played for at least 5 hours. Suggested candidates: *Celeste*, *Hollow Knight*, *Dead Cells*, *Stardew Valley*, *Spelunky*, *Vampire Survivors*. Write a 400–600 word analysis at `homework/p1_four_lenses.md` that scores the game on each of Doug Church's four lenses (Intention, Perceivable Consequence, Story, Goals) out of 5, with one supporting paragraph per lens.

**Acceptance criteria.**

- A file `homework/p1_four_lenses.md` exists, 400–600 words.
- Each of the four lenses gets its own header and one supporting paragraph.
- Each lens has a numeric score `n/5` with at least one *specific* example from the game justifying the score (not "the controls feel great" — name a specific input mechanic).
- File is committed.

**Hint.** Don't pick the same game you're building. The point is to evaluate someone else's design with the new vocabulary. If you're stuck on which game to pick, default to *Celeste* — it's the most-analysed-with-vocabulary indie of the last decade and you can cross-check your own analysis against Mark Brown's *Game Maker's Toolkit* video.

**Estimated time.** 50 minutes.

---

## Problem 2 — MDA your brick-breaker

**Problem statement.** Write `homework/p2_mda_brick_breaker.md` (200–350 words) applying the MDA framework to YOUR Week 2 brick-breaker. List 4–6 Mechanics. Describe 2–3 Dynamics that emerge from those mechanics. Name 1–2 Aesthetics (from the eight in Lecture 2 §3.3) that you believe the game delivers.

**Acceptance criteria.**

- A file `homework/p2_mda_brick_breaker.md` exists, 200–350 words.
- A bulleted list of 4–6 Mechanics, each one named in 1–2 words and described in 1 sentence.
- A bulleted list of 2–3 Dynamics that emerged in playtest (yours or a friend's). At least one Dynamic should be something you *did not explicitly design* — emergent.
- A short paragraph naming the primary Aesthetic and explaining why.
- File is committed.

**Hint.** Dynamics are the trickiest. Examples: "after losing the ball twice, the player starts hugging the centre with the paddle" (a behavioural dynamic, emerging from the mechanic of lives + paddle-English). "The player aims for the corner brick first because it's hardest to reach later" (a strategic dynamic).

**Estimated time.** 35 minutes.

---

## Problem 3 — Extend the screen-shake to vary by direction

**Problem statement.** Take `exercise-02-screenshake-and-particles.py` and modify the `ScreenShake.offset()` method so the shake is biased *along* the impact direction rather than isotropic (random in x and y). A horizontal wall hit should produce a vertical shake. A vertical wall hit should produce a horizontal shake.

This is a one-axis shake. It tends to read as more deliberate than a random-2D shake, and it makes the impact direction visible.

**Acceptance criteria.**

- A file `homework/p3_directional_shake.py` exists and runs.
- `ScreenShake.trigger()` takes an optional `axis: pygame.Vector2 | None` argument. When `None`, the shake is isotropic (the default behaviour). When given, the shake offset lies on that axis only.
- The bouncing ball passes `axis=` matching the wall's tangent direction. A side-wall hit produces vertical shake; a top/bottom hit produces horizontal shake.
- The HUD shows "axis: (x, y)" so you can see what's happening.
- Code is committed.

**Hint.** Inside `offset()`, if `self.axis is not None`, return `(int(self.axis.x * d), int(self.axis.y * d))` where `d = random.uniform(-current, current)`. Store the axis when `trigger()` is called.

**Estimated time.** 45 minutes.

---

## Problem 4 — Two flavours of "hit-stop"

**Problem statement.** Add hit-stop to `exercise-02-screenshake-and-particles.py` and save as `homework/p4_hitstop.py`. On any wall hit, freeze the *simulation* (ball update, particle update) for `HITSTOP_MS` milliseconds. Rendering continues — the screen does not freeze, just the simulation.

Then add a key toggle:

- `1` = no hit-stop.
- `2` = 30 ms hit-stop on every hit.
- `3` = 30 ms hit-stop on slow hits, 80 ms on fast (impact_speed > 600 px/s) hits.

Play with each mode for one minute. Write a 100–150 word note `homework/p4_hitstop.md` describing what you observed.

**Acceptance criteria.**

- A file `homework/p4_hitstop.py` exists and runs.
- A file `homework/p4_hitstop.md` (100–150 words) describes the perceptual difference between the three modes.
- Pressing 1, 2, 3 switches modes live.
- Both files committed.

**Hint.** Hit-stop is a single state variable:

```python
hitstop_left = 0.0  # seconds remaining

# On hit:
hitstop_left = max(hitstop_left, HITSTOP_DURATION)

# Each frame:
if hitstop_left > 0:
    hitstop_left = max(0, hitstop_left - dt)
else:
    ball.update(dt)
    for p in particles: p.update(dt)
```

Rendering happens unconditionally. The particles you draw during the freeze are last frame's positions — which is exactly the "frozen moment of impact" feeling you want.

**Estimated time.** 1 hour.

---

## Problem 5 — Audio: pitch variation as juice

**Problem statement.** Take any short `.wav` (from SFXR/JSFXR, Freesound, or Kenney). In `homework/p5_pitch_variation.py`, build a single Pygame window with three buttons:

1. "monotone" — plays the same sample 20 times in a row at constant pitch.
2. "varied" — plays the same sample 20 times in a row with pitch randomly varied by ±15%.
3. "stop" — interrupts whichever is playing.

Use `pygame.mixer.Sound`. Pygame doesn't have built-in pitch shifting, so you'll either need to:

- Pre-render 5–10 pitch-shifted copies of the sample (use Audacity or ffmpeg) and pick one at random per play; OR
- Use `pygame.sndarray` to read the sample, resample it with `numpy`, and play the new array.

Either approach is acceptable. The simpler is the pre-render.

**Acceptance criteria.**

- A file `homework/p5_pitch_variation.py` exists and runs.
- Three on-screen buttons (or three keys: M, V, X) for monotone / varied / stop.
- "monotone" plays a single sample 20 times in 4 seconds.
- "varied" plays the same sample 20 times in 4 seconds, with audibly varied pitch each time.
- A `homework/p5_audio_note.md` (50–100 words) describes the perceptual difference.
- Code and note both committed.

**Hint.** The "20 in 4 seconds" cadence (5/sec) is what makes the difference audible. At slower cadences both modes feel fine; at this cadence the monotone mode reads as "robotic" and the varied mode reads as "alive."

If you go the pre-render route: in Audacity, open your sample, `Effect > Change Pitch` by -10%, save as `hit_-10.wav`. Repeat for -5%, 0%, +5%, +10%. Five files. Pick one at random in code.

**Estimated time.** 1 hour 15 minutes.

---

## Problem 6 — Reflection essay

**Problem statement.** Write a 350–450 word reflection at `notes/week-03-reflection.md` answering:

1. Which framework — Steve Swink's three pillars, Doug Church's four lenses, or MDA — felt most useful when applied to your own brick-breaker? Why?
2. The lecture claims "juice is information, not decoration." Did you experience that as obvious, or did you have to convince yourself? Describe one specific moment in the exercises or the mini-project where you felt the claim land (or fail to land).
3. Steve Swink writes that game feel is "the secret ingredient." Now that you have a vocabulary for it, do you agree that it's secret — or has it just been under-named?
4. What's one thing you'd add to your brick-breaker's juice if you had another five hours? Why that thing first?

**Acceptance criteria.**

- A file `notes/week-03-reflection.md`, 350–450 words.
- Each numbered question addressed in its own paragraph.
- At least one specific technique mentioned by name (e.g., "hit-stop on brick destruction" rather than "more polish").
- File is committed.

**Hint.** Reflection essays read flat when they're abstract. Write about specific moments: "When I cranked particle_lifetime to 0.05 the game stopped 'speaking' and I noticed how much information that channel had been carrying" beats "I learned that particles matter."

**Estimated time.** 30 minutes.

---

## Time budget recap

| Problem | Estimated time |
|--------:|---------------:|
| 1 | 50 min |
| 2 | 35 min |
| 3 | 45 min |
| 4 | 1 h 0 min |
| 5 | 1 h 15 min |
| 6 | 30 min |
| **Total** | **~4 h 55 min** |

That's about an hour under the 6-hour weekly budget — the rest is for fixing the bugs your audio code will produce. Pygame mixer is unforgiving in ways that the rest of the API isn't; budget some debugging time.

When you've finished all six, push your repo and open the [mini-project](./07-mini-project/00-overview.md).
