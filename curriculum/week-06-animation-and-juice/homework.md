# Week 6 Homework

Six practice problems that revisit the week's topics. The full set should take about **5-6 hours** in total. Work in your Week 6 Git repository so each problem produces at least one commit you can point to later.

The work this week is *tuning*. Most of these problems are short to type and long to dial in. By Sunday your Week-5 character will be unrecognisable in the best possible way — same physics, same controls, completely different *feel*.

Each problem includes:

- A short **problem statement**.
- **Acceptance criteria** so you know when you're done.
- A **hint** if you get stuck.
- An **estimated time**.

---

## Problem 1 — Plot a sixth easing curve

**Problem statement.** Open `exercise-02-tween-easing-curves.py`. Add a sixth easing curve: `ease_in_back` (anticipation — the curve dips *below* 0 before rising to 1, mirror image of `ease_out_back`). Plot it as a sixth panel and drive a sixth tweened square with it. The point is to make the lecture's "ease_in / ease_out are mirror images, ease_out_back / ease_in_back are mirror images" observation concrete in your hands.

**Acceptance criteria.**

- A file `homework/p1_ease_in_back.py` runs and shows six panels and six squares.
- The new `ease_in_back(t)` function returns values that dip below 0 in the first half of `t` and reach 1.0 at `t=1`.
- The plot of `ease_in_back` clearly shows the dip below the y=0 grid line.
- The sixth square *retreats slightly* before launching toward the target — visible anticipation.
- A `homework/p1_note.md` (50-75 words) describes one effect in a real game where you've seen `ease_in_back` used. (Most common: a slingshot windup; a boss attack telegraph; a doorway that pulls back before opening.)

**Hint.** Penner's `ease_in_back` is `t * t * ((s + 1) * t - s)` where `s = 1.70158`. The negative middle term is what causes the dip below 0. Plot the curve carefully — your panel will need to allow a small negative y-range; expand the plot's vertical bounds from `[0, 1]` to `[-0.2, 1.0]`.

**Estimated time.** 35 minutes.

---

## Problem 2 — Tune the squash-and-stretch knobs

**Problem statement.** Take `exercise-03-add-juice-to-week5-character.py`. Tune the six squash-and-stretch knobs (`SQUASH_LAUNCH_FROM/TO/DUR`, `SQUASH_LAND_FROM/TO/DUR`) for two distinct *feel personalities*: a "Celeste" feel (snappy, ~10% squash, ~120 ms recovery) and a "Hollow Knight" feel (heavy, ~30% squash, ~250 ms recovery with deeper overshoot). Commit both as `p2_celeste.py` and `p2_hollow_knight.py`. Record a 10-second clip of each.

**Acceptance criteria.**

- A file `homework/p2_celeste.py` runs with snappy squash values clearly distinct from defaults.
- A file `homework/p2_hollow_knight.py` runs with heavy squash values.
- Both files differ ONLY in their `SQUASH_*` constants. Everything else is identical.
- Two clips at `homework/p2_celeste.mp4` and `homework/p2_hollow_knight.mp4`, 8-12 seconds each, show the player jumping and landing repeatedly.
- A `homework/p2_tuning.md` (75-125 words) names the exact knob values chosen for each feel and explains why one would NOT use Hollow Knight values in a fast-twitch precision platformer.

**Hint.** Celeste values to try: `LAUNCH_FROM=1.0 / TO=1.10 / DUR=0.08`; `LAND_FROM=0.85 / TO=1.0 / DUR=0.12`. Hollow Knight values: `LAUNCH_FROM=1.0 / TO=1.25 / DUR=0.18`; `LAND_FROM=0.65 / TO=1.0 / DUR=0.28`. These are starting points; the real values come from playing for sixty seconds each and adjusting.

**Estimated time.** 50 minutes.

---

## Problem 3 — Three screen-shake doses

**Problem statement.** In `exercise-03-add-juice-to-week5-character.py`, add three new key bindings: `1` triggers `world.shake.kick(amp=2.0, dur=0.06)` ("footstep tier"), `2` triggers `kick(amp=8.0, dur=0.18)` ("hit tier"), `3` triggers `kick(amp=18.0, dur=0.30)` ("explosion tier"). Use them to feel the three doses without firing any other juice. Then write a short reflection on the "amplitude that feels present but not loud" for each tier.

**Acceptance criteria.**

- A file `homework/p3_shake_tiers.py` runs and the three keys trigger three shakes of distinct intensities.
- The HUD shows which tier was last fired (e.g. `last shake: explosion`).
- A `homework/p3_dose.md` (75-100 words) reports the amplitude that *you* settled on as "present but not loud" for each tier, and notes whether the canonical values from Nijman's tuning table (Lecture 2 §5) are too aggressive, too subtle, or about right for your taste.

**Hint.** Test the tiers with the character standing still — no other juice firing. Then test them in motion. The amplitude that feels right at rest often feels too small in motion (because the moving character masks the shake). This is why playtesting is the second half of tuning.

**Estimated time.** 35 minutes.

---

## Problem 4 — Implement variable jump height

**Problem statement.** Take `exercise-03-add-juice-to-week5-character.py` and add **variable jump height**: if the player releases the jump key while `vy < 0` (still ascending), cut the upward velocity in half. This is the single biggest "game feel" payoff for a platformer and a *Celeste*/*Hollow Knight*-grade feature. Eight lines of code, infinite payoff.

**Acceptance criteria.**

- A file `homework/p4_variable_jump.py` runs and a *short tap* of SPACE produces a *short jump*; a *held* SPACE produces the full jump.
- The cut-off is bound to `JUMP_KEYUP` in the event loop, not to a per-frame key-state read. (Why? Because key-state is sticky; the *release edge* is what we want.)
- The implementation lives where it should: in `JumpState`'s logic, not in the input handler.
- A `homework/p4_variable_jump_note.md` (50-100 words) describes which Pygame event you used (`KEYUP`) and why this trick belongs in *Celeste*'s feel-feature canon. Cite Lecture 2 §8, item 17.

**Hint.** Wire a new field on `Character`: `jump_released_this_frame: bool`. Set it in the event loop when `KEYUP` fires for SPACE. In `JumpState.update`, check `if char.jump_released_this_frame and char.vy < 0: char.vy *= 0.5`. Reset the field every frame. That's the whole feature.

**Estimated time.** 45 minutes.

---

## Problem 5 — Real SFX with Kenney's Impact Sounds pack

**Problem statement.** Download Kenney's *Impact Sounds* pack (CC0, ~5 MB, linked in `resources.md`). Replace the `SFX` stub in `exercise-03-add-juice-to-week5-character.py` with a real `pygame.mixer`-backed version that plays the appropriate `.wav` on each transition. Map at least four sounds: jump, land, hit, footstep. Confirm the call sites are unchanged — only the `SFX` class is new.

**Acceptance criteria.**

- A folder `homework/p5_real_sfx/` exists with the `.py` file and a `sfx/` subfolder containing at least four `.wav` or `.ogg` files (Kenney CC0).
- A `homework/p5_real_sfx/CREDITS.md` credits Kenney (kenney.nl) by name.
- The `SFX` class plays real sounds; the `.play_one_shot`, `.play(loop=True)`, and `.stop` methods all work.
- Every existing call site in `JumpState.enter`, `RunState.enter`, etc., is *unchanged*. Only the `SFX` class differs.
- A `homework/p5_sfx_note.md` (50-100 words) names the four sounds you picked and notes whether you applied per-call volume tuning (e.g. footsteps at 0.3, hits at 1.0). Sounds at full volume often feel too loud; tune.

**Hint.** `pygame.mixer.Sound(path)` loads a `.wav`. `snd.set_volume(0.3)` sets the volume. `snd.play()` plays it. `snd.play(loops=-1)` loops it; the return is a `Channel` you can call `.stop()` on. The stub in Exercise 3 shows the four method signatures you need to fill in.

**Estimated time.** 50 minutes.

---

## Problem 6 — Reflection essay

**Problem statement.** Write a 350-450 word reflection at `notes/week-06-reflection.md` answering:

1. Before this week, your character was correct but lifeless. After this week, it has a feel. Describe one *specific* juice trick that, in your hands, made the biggest perceived difference. Be specific: name the trick, name the tuning value you ended up at, name the moment in your test sequence where it stood out.
2. Lecture 2 §10 argues that the *dose* is the work, not the code. Did you experience that crossover in your own writing this week? Pick one trick where you initially used the canonical default value and later changed it — say what you changed it to and why.
3. Steve Swink's *Game Feel* defines feel as three pillars (Lecture 2 §9). For each pillar, name one technique from C11 Weeks 1-6 that contributes to it. (Week 1's `dt`-correct integration → pillar 1; Week 2's mass-and-friction physics → pillar 2; etc.)
4. Jan Willem Nijman's *Screenshake* talk enumerates twenty cheap tricks; the week implements six. Of the remaining fourteen (Lecture 2 §8), which TWO would you add next, and why? Don't pick the easy ones; pick the ones that would change *your* mini-project the most.

**Acceptance criteria.**

- A file `notes/week-06-reflection.md`, 350-450 words.
- Each numbered question addressed in its own paragraph.
- At least one specific technique mentioned by name (e.g., "the `ease_out_back` overshoot on the land-recovery tween" rather than "the squash thing").
- At least one citation of Lecture 1 or Lecture 2 by section number.
- At least one citation of Swink's *Game Feel* or Nijman's *Screenshake* by name.
- File is committed.

**Hint.** Reflection essays read flat when they're abstract. Write about specific moments: "When I lowered SQUASH_LAND_FROM from 0.65 to 0.78, the character stopped feeling cartoonish and started feeling *grounded*. The diff was tiny in numbers and enormous in feel. I'd watched Nijman's talk twice and only after that tuning pass did I understand what 'dose-response curve' really means."

**Estimated time.** 30 minutes.

---

## Time budget recap

| Problem | Estimated time |
|--------:|---------------:|
| 1 | 35 min |
| 2 | 50 min |
| 3 | 35 min |
| 4 | 45 min |
| 5 | 50 min |
| 6 | 30 min |
| **Total** | **~4 h 5 min** |

That's about an hour and a half under the 5-6 hour weekly budget — the rest is for the tuning that *every problem* this week absorbs more time than the spec admits. Juice tuning is open-ended; the spec says "Celeste values" but settling on YOUR Celeste values is sixty minutes of playing.

When you've finished all six, push your repo and open the [mini-project](./mini-project/README.md).
