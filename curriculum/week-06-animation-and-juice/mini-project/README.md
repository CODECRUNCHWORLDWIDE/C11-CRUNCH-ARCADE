# Mini-Project — A Full Juice Pass on Your Week-5 Character

> Take your Week-5 four-state player (or the Exercise-2 starter, if your mini-project hasn't shipped yet) and add a full juice pass: sprite-sheet animations bound to FSM states, squash-and-stretch on jump and land, screen shake on landings and hits, dust and impact particles, hit-flash on damage, and real sound cues on every transition. Record a 30-second before-and-after side-by-side video. Write a 300-word reflection. Push to GitHub.

This is the artefact this week was building toward. By Sunday you have a small, juiced character whose *feel* matches the structural correctness from Week 5. The before/after video is the deliverable that turns "I added juice" into a portfolio piece.

The mechanic is intentionally the same as Week 5 — walk, jump, fall, take damage, recover — because the work this week is the *presentation layer*, not new mechanics. Week 7 adds save state; Week 8 starts Godot. But it all starts with this: state-bound polish.

**Estimated time:** 10.5 hours (split across Wednesday → Sunday).

---

## What you will build

A new repo (or a `juice-pass/` subfolder of your portfolio repo), with:

1. **An engine** — Python codebase, ~700-900 lines, that loads your Week-5 character plus a tilemap (your Week-4 level loader is fine) and renders it with a full juice pass.
2. **Sprite-sheet animations** for at least five clips: `idle_breathing`, `run_loop`, `jump_launch`, `fall_airborne`, `hurt_react`. The sheet may be a real Kenney *Platformer Characters* sheet (recommended) or a hand-drawn 8-frame placeholder.
3. **Animation library binding** — `IdleState.enter` plays `idle_breathing`; `RunState.enter` plays `run_loop` (looping) and the `footsteps_loop` SFX; etc. The five-class binding from Lecture 1 §7.
4. **Squash-and-stretch tween** on jump-launch (~120 ms scale tween, `ease_out`) and on land-recovery (~180 ms, `ease_out_back` with overshoot). The art deforms; the hitbox doesn't.
5. **Screen shake** with the three-tier dose system: ~2 px for footsteps (optional; can be 0), ~4 px for landings, ~8 px for hits. Tune by feel.
6. **Particle system** spawning dust on landings (8-12 particles) and footsteps (2-3 particles), and Coin-Pink "blood" particles on spike hits (12-14 particles).
7. **Hit-flash** — the player sprite tinted white (or Coin-Pink-deep `#9D174D`) for 80 ms after a damage event.
8. **Real SFX** — at least five sounds (jump, land, hit, footstep, ambient), all from Kenney's *Impact Sounds* + *Interface Sounds* packs (CC0). The `SFX` stub from Exercise 3 becomes a real `pygame.mixer`-backed class.
9. **A pause overlay** carried over from Week 5's state stack. Pausing should *also* freeze all the juice systems (the shake, the particles, the tweens). Verify on test.
10. **A 25-40 second side-by-side before/after video** at `demo.mp4` showing your Week-5 character (left) and your Week-6 juiced character (right) running the same input sequence.
11. **A 300-word `REFLECTION.md`** using this week's vocabulary correctly.

You will NOT add:

- New mechanics beyond what was in Week 5. (Week 7+.)
- Multiple enemies with their own juice. (Week 11 capstone.)
- A save system. (Week 7.)
- Online multiplayer. (Not in this course.)
- More than six juice tricks from Nijman's checklist. (Stretch only — see below.)

---

## Rules

- **You may** copy from this week's exercises freely — that's why they exist. The `SpriteSheet`, `Animation`, `Animator`, `Tween`, `ScreenShake`, and `ParticleField` classes from Exercises 1, 2, and 3 are the starting point.
- **You may** reuse your Week-4 tilemap loader and camera and your Week-5 FSM verbatim. Those are solved problems; don't re-solve them.
- **You may NOT** put any `play_sound("hit")` calls outside an FSM `enter()` or `exit()` hook. If you find one — even in the physics code — refactor. The discipline of bind-presentation-to-state is the whole week.
- **You may NOT** apply the squash-and-stretch scale to the collision rectangle. The hitbox stays at `PLAYER_W x PLAYER_H` regardless of `scale_y`. Art deforms; hitbox doesn't.
- **You may NOT** crank screen-shake amplitude past 16 px (and ideally not past 10 px). Past 16, screen-readability degrades; past 24, the player feels motion-sick.
- **You must** credit Kenney for the asset packs in `README.md` and in `CREDITS.md`. Kenney's CC0 licence does not require attribution; it is the *right thing* to do regardless.
- **You must** commit the before/after video (or link to it). This is the design artefact; without it the juice pass has no reviewer.
- **Python 3.11+, Pygame 2.5+.**
- **Use a virtual environment.**

---

## Acceptance criteria

- [ ] A repo (or subfolder) called `c11-week-06-juice-pass-<yourhandle>`.
- [ ] `python -m py_compile main.py` succeeds with no output.
- [ ] `python main.py` opens a window with a Coin-Pink player on a tilemap, animating cleanly.
- [ ] The player has **at least five animation clips** loaded into an `Animator`: `idle_breathing`, `run_loop`, `jump_launch`, `fall_airborne`, `hurt_react`. Bound by class-name (`IdleState.enter` calls `anim.play("idle_breathing")`).
- [ ] **Squash-and-stretch** fires on jump-launch (scale-tween ~`1.0 → 1.18 → 1.0` with `ease_out`) and on land-recovery (`~0.7 → 1.0` with `ease_out_back`).
- [ ] **Screen shake** fires on at least three events: landings (~4 px), hits (~8 px), and (optionally) enemy kills if you have them. The amplitude is bounded; no shake exceeds 16 px.
- [ ] **Dust particles** spawn on landings (8-12 count) and footsteps (2-3 count, at a regular ~280 ms cadence while in `RunState`).
- [ ] **Impact particles** spawn on hits (12-14 count, Coin-Pink colour).
- [ ] **Hit-flash** — the player sprite tints white (or Coin-Pink-deep) for ~80 ms on every damage event.
- [ ] **Real SFX** — at least five `.wav` or `.ogg` files in a `sfx/` folder, loaded into a `pygame.mixer.Sound`-backed `SFX` class. Sounds are credited by name in `CREDITS.md`.
- [ ] **Pause overlay** (carried from Week 5) freezes ALL juice systems: tweens stop advancing, particles stop integrating, screen shake holds its offset.
- [ ] **HUD** shows the current state's class name, the current animation clip name, the active screen-shake amplitude, the live particle count, and FPS. The HUD updates within one frame of any FSM transition.
- [ ] **`demo.mp4`** — 25-40 seconds, side-by-side composition, Week-5 vs Week-6 versions of the same character running the same input sequence. Both halves are labelled.
- [ ] **`REFLECTION.md`** — 300 words at the repo root that:
  - Names the SIX juice tricks you implemented and ranks them by perceived impact (1 = biggest, 6 = smallest).
  - Names the ONE trick that, after tuning, you considered cutting and why you kept it (or did cut it).
  - Cites both lecture notes by name (Lecture 1 *Sprite-sheet animation*, Lecture 2 *Tweening, easing, and juice*).
  - Cites Swink's *Game Feel* or Nijman's *Screenshake* by name.
  - States ONE thing you would do differently next time.
- [ ] **`CREDITS.md`** — credits for Kenney, any other asset creators, and the lecture authors (Swink, Nijman).
- [ ] **`README.md`** includes:
  - A controls section.
  - A "Juice tricks implemented" section listing the six tricks and their tuning values.
  - The side-by-side video inlined (or linked).
  - The asset credits inlined or linked.

---

## Suggested order of operations

Build incrementally rather than trying to write the whole thing at once. Each phase ends with a commit.

### Phase 1 — Scaffold the repo (~30 min)

1. Tag your Week-5 mini-project repo: `git tag week-05-final`. You'll want a clean comparison point.
2. Create the new repo. Copy your Week-5 `main.py`, `levels/`, and `state_machine.py`.
3. Copy `exercise-01-sprite-animation.py`'s `SpriteSheet`, `Animation`, and `Animator` classes into a new `animation.py` file.
4. Copy `exercise-02-tween-easing-curves.py`'s `lerp` and easing curves and `Tween` class into `tweening.py`.
5. Copy `exercise-03-add-juice-to-week5-character.py`'s `ScreenShake`, `ParticleField`, and `SFX` (stub) classes into `juice.py`.
6. Run the unchanged Week-5 player on top of these new modules. Confirm nothing is broken.
7. Commit: `Scaffold juice modules; Week-5 player unchanged.`

### Phase 2 — Download and integrate a sprite sheet (~1.5 h)

1. Download Kenney's *Platformer Characters 1* pack (or *2*; either works) from kenney.nl/assets. CC0, ~10 MB.
2. Pick one character. Identify the cells for idle (1-4 frames), run (4-8 frames), jump (1-2 frames), fall (1 frame), hurt (1-2 frames).
3. Load the sheet in your `main.py` startup: `sheet = SpriteSheet(pygame.image.load("kenney_chars.png").convert_alpha(), frame_w=64, frame_h=64)` (or whatever your sheet's cell size is).
4. Build the `Animator` with the five clips, indexed into the sheet.
5. Draw the character's current frame instead of the coloured rectangle. The character should now ANIMATE just by virtue of `anim.update(dt)` and `anim.current_frame()`.
6. The FSM transitions don't drive the animation yet — that's the next phase. The character idle-loops in every state.
7. Commit: `Sprite sheet loaded; character animates the idle loop in every state.`

### Phase 3 — Bind animations to FSM transitions (~1 h)

1. In `IdleState.enter`, call `char.anim.play("idle_breathing")`.
2. In `RunState.enter`, call `char.anim.play("run_loop")`.
3. In `JumpState.enter`, call `char.anim.play("jump_launch", restart=True)`.
4. In `FallState.enter`, call `char.anim.play("fall_airborne")`.
5. In `HurtState.enter`, call `char.anim.play("hurt_react", restart=True)`.
6. Run the player. Walk: the run cycle plays. Jump: the launch frames play once, then the airborne pose holds. Land: idle resumes. Hit a spike: hurt-react plays.
7. Commit: `Bind animation clips to FSM enter() hooks.`

### Phase 4 — Squash-and-stretch tween (~1 h)

1. Add a `scale_y_tween: Optional[Tween]` field on `Character`.
2. In `JumpState.enter`, kick off a `Tween(start=1.0, end=1.18, duration=0.12, ease=ease_out)`.
3. In `IdleState.enter` and `RunState.enter`, if `char.arrived_airborne` was set by the airborne states, fire the land squash: `Tween(start=0.65, end=1.0, duration=0.20, ease=ease_out_back)`.
4. In the character draw call, scale the frame by `(1.0, scale_y_tween.value())` before blitting. The hitbox stays the same.
5. Run. Jump. Feel the launch stretch. Land. Feel the squash-and-recover.
6. Commit: `Add squash-and-stretch tween on launch and land.`

### Phase 5 — Screen shake and particles (~1.5 h)

1. In `_apply_land_juice` (the helper from Exercise 3), kick `world.shake.kick(amp=4.0, dur=0.10)` and emit `world.particles.emit_dust(...)`.
2. In `HurtState.enter`, kick `shake.kick(amp=8.0, dur=0.18)` and emit `particles.emit_hit(...)`.
3. In `RunState.update`, advance a footstep timer; every ~280 ms, emit 2-3 dust particles at the feet.
4. Run. Jump and land. Feel the thud + dust. Walk into a spike. Feel the hit + impact particles.
5. Commit: `Add screen shake and particle emitters on land, hit, footstep.`

### Phase 6 — Real SFX (~1.5 h)

1. Download Kenney's *Impact Sounds* and *Interface Sounds* packs from kenney.nl/assets. CC0, ~50 MB combined.
2. Pick five `.wav` files: `jump.wav`, `land.wav`, `hit.wav`, `footstep.wav`, `hurt.wav`. Copy them into `sfx/`.
3. Replace the `SFX` stub in `juice.py` with a `pygame.mixer.Sound`-backed version. Load all five sounds at startup.
4. The call sites in `JumpState.enter`, `RunState.enter`, etc., are unchanged.
5. Tune per-sound volume: footsteps at 0.3, jump at 0.6, land at 0.7, hit at 1.0, hurt at 0.8. Tuning is the work.
6. Commit: `Add real SFX from Kenney's Impact + Interface packs.`

### Phase 7 — Hit-flash and pause integration (~1 h)

1. Add a `hit_flash_t: float = 0.0` field on `Character`. In `HurtState.enter`, set it to 0.08 (80 ms).
2. Every frame, decrement `hit_flash_t`. If `> 0`, draw the player tinted (white or Coin-Pink-deep) instead of Coin-Pink.
3. In your `PauseState` (from Week 5), make sure `world.shake.update`, `world.particles.update`, and `char.scale_y_tween.update` ALL stop being called while paused. The simplest fix: gate the whole `world.update(dt)` and `char.update(dt)` block on `not paused`.
4. Test: pause mid-air, mid-shake, mid-particle-burst. Everything should *freeze*.
5. Commit: `Add hit-flash; pause freezes all juice systems.`

### Phase 8 — Record the demo + write reflection (~1.5 h)

1. Stage canonical start position and document the input sequence (see [Challenge 1](../challenges/challenge-01-before-after-juice-comparison.md) for the recipe).
2. Run your Week-5 version (your `git tag week-05-final`). Record a 25-second take.
3. Run your Week-6 juiced version. Record the same input sequence.
4. Composite side-by-side in DaVinci Resolve (or any free editor). Label both halves. Export as `demo.mp4`.
5. Write `REFLECTION.md`. 300 words. Cite both lectures and either Swink or Nijman. Name the ranked tricks.
6. Final commit: `Add demo video and reflection.`
7. Push. Verify the repo URL works on a fresh clone.

---

## Rubric

| Criterion | Weight | What "great" looks like |
|----------|-------:|-------------------------|
| Sprite-sheet animations bound to FSM `enter()` | 20% | All five clips load from one sheet; each state's `enter` plays the right one. No `play_sound` or `anim.play` outside an FSM hook. |
| Squash-and-stretch on jump/land | 15% | Visible, tuned, `ease_out_back` overshoot on land-recovery. Hitbox does not deform with art. |
| Screen shake (three doses) | 10% | Lands, hits, and at least one other event shake at distinct amplitudes. None exceeds 16 px. |
| Particles (dust + hit) | 10% | Dust on land and footstep; impact particles on hit; counts and colours readable. |
| Real SFX from Kenney (5+) | 10% | Five sounds loaded; volumes tuned per sound; loops stop in `exit()`. |
| Hit-flash + pause integration | 10% | Hit-flash visible for ~80 ms; pause freezes shake, particles, tweens. |
| Before/after side-by-side video | 15% | 25-40 s, labelled, same input sequence, side-by-side composition. |
| Reflection (vocabulary + ranking) | 8% | Cites both lectures; cites Swink or Nijman; ranks the six tricks honestly. |
| Commit history | 2% | One commit per phase; meaningful messages. |

---

## Stretch (if you finish early)

These are *stretch*. Do **not** lose the main spec chasing them.

- **Variable jump height.** Releasing SPACE while `vy < 0` cuts `vy *= 0.5`. The single biggest *Celeste*-grade feel feature in any platformer. Eight lines of code.
- **Coyote time.** A 100 ms grace window after the player walks off a ledge during which `JUMP_PRESSED` still triggers a jump. The fix for "I clearly pressed jump and the game ignored me."
- **Jump buffer.** A 100 ms window before landing during which an early jump-press is queued and fired the instant the player lands. The fix for "I clearly pressed jump and the game ignored me, part 2."
- **Hit-stop.** On hit (or spike contact), pause the world for 50-80 ms before the knockback fires. Makes hits *land*. A boolean on `App` gates the update calls.
- **Chromatic aberration on hit.** Three RGB-offset draws of the player for ~80 ms after damage. The *Hyper Light Drifter* trick. Cheap, *very* shippable.
- **Permanent particles.** Every FSM transition emits one or two tiny ambient particles that survive ~600 ms. The result: the screen *always feels alive*.
- **Random pitch variation on SFX.** Every `play_one_shot` plays at `pitch * uniform(0.95, 1.05)`. Same sound, but it stops feeling robotic. Pygame's `pygame.mixer.Sound` doesn't natively support pitch shift; preload three pitch-shifted variants per sound and pick one at random. Five lines.
- **Camera lean.** The camera offsets ~6-10 px in the direction of fast horizontal motion. Subtle, free, *always* a positive.
- **A second enemy with its own juice.** Bring in your Week-5 challenge enemy and give it a squash-on-hit and a death particle burst. Reuse, not duplication.

---

## What this prepares you for

- **Week 7** (Save & load) serialises the player. The juice fields (`scale_y_tween`, `hit_flash_t`) raise the *serialisation* question: do you save the in-flight squash, or do you snap to neutral on load? The mini-project this week is what makes that question expressible.
- **Week 9** (Pygame → Godot port). Godot has `AnimationPlayer` and `AnimationTree` nodes, `Tween` nodes, and a built-in shake-by-noise. The six tricks you wrote by hand map to five Godot nodes plus one `AudioStreamPlayer`. The port is mostly translation.
- **Week 10** (Audio). The SFX stub becomes a real audio bus with `master/sfx/music` channels, volume sliders, and ducking. The five sounds you loaded this week are the test cases.
- **Week 11** (Playtesting). When a tester says "the jump feels weak," your first move will be to open `manifest.json`, find the `SQUASH_LAUNCH_TO` knob, and dial it from 1.18 to 1.25. The tuning surface is the playtesting surface.

---

## Resources

- This week's [Lecture 1](../lecture-notes/01-sprite-sheet-animation.md) and [Lecture 2](../lecture-notes/02-tweening-easing-and-juice.md).
- The week's [exercises](../exercises/) — copy from them.
- The week's [challenge](../challenges/challenge-01-before-after-juice-comparison.md) — the side-by-side video is the deliverable.
- Steve Swink — *Game Feel*: <https://archive.org/details/gamefeelgamedesi0000swin>
- Jan Willem Nijman — *The Art of Screenshake*: <https://www.youtube.com/watch?v=AJdEqssNZ-U>
- Jonasson + Purho — *Juice it or lose it*: <https://www.youtube.com/watch?v=Fy0aCDmgnxg>
- Kenney — CC0 sprite/sound packs: <https://kenney.nl/assets>

---

## Submission

When done:

1. Push your repo to GitHub with a public URL.
2. Make sure `README.md` links to `demo.mp4` (or has it inlined) and credits Kenney.
3. Make sure `python -m py_compile main.py` is clean on a freshly cloned copy.
4. Make sure the before/after video shows the *diff*, not just the after.
5. Submit the repo URL on the course tracker.

You painted the muscles on top of the Week-5 bones. The character now *feels*. Next week we make it remember — save state, JSON, versioning. The week after, we cross the bridge to Godot.
