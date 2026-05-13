# Mini-Project — Juice Your Brick Breaker

> Take your Week 2 brick-breaker (or Pong) and add three "feel" touches: screen shake, a particle burst, and a sound cue. Record a 30-second before/after video. Write a 200-word reflection that uses this week's vocabulary correctly. Ship the whole thing to GitHub.

The point of this mini-project is to feel — in your own hands, on your own game — the gap between *the simulation is correct* and *the player feels the right thing*. The code change is small. The perceptual change is large. The work this week is mostly noticing the difference, naming it, and tuning until the names match the feel.

You will NOT write a new game this week. You will extend the brick-breaker you already shipped. If you skipped the Week 2 mini-project, do it first — there is nothing to juice without a game underneath.

**Estimated time:** 9.5 hours (split across Wednesday → Sunday).

---

## What you will build

You start from your Week 2 brick-breaker (or Pong). You will add:

1. **A `ScreenShake` system** that triggers on impactful events. Shake magnitude scales with event strength.
2. **A particle system** — a list of short-lived drawables that spawn at impact points and decay over 200–700 ms.
3. **Three sound effects** — one for paddle hit, one for brick destruction, one for ball loss. Pygame mixer, low-latency configured.
4. **A `pre-juice` Git tag** on the commit immediately *before* you start adding juice. This is what you'll record the "before" footage against in the comparison video.
5. **A 30-second side-by-side comparison video** (`.mp4` or `.webm`, in the repo or linked from `README.md`).
6. **A 200-word reflection** in `REFLECTION.md` using Lecture 1 and Lecture 2 vocabulary.

You will NOT add:

- New mechanics (no new brick types, no power-ups, no new control scheme).
- New levels (the brick layout stays the same).
- Story or progression (this is a juice week, not a content week).

If you find yourself "improving the game" beyond juice, you've drifted. Roll back. Add only the three feel touches and the artefacts that document them.

---

## Rules

- **You may** copy from this week's exercises freely — that's why they exist.
- **You may NOT** rewrite the game's core loop or collision code. The simulation is correct; you're adding to it, not replacing it.
- **You may NOT** add sprite art or animations this week. Those are Week 6 lessons. Use shapes and colours.
- You **must** use a virtual environment.
- Python 3.11+, Pygame 2.5+.
- All audio assets must be CC0 or CC-BY (credit the author in `README.md`). Suggested sources: [Freesound.org](https://freesound.org/), [Kenney.nl](https://kenney.nl/assets/category:Audio), [SFXR](https://sfxr.me/).

---

## Acceptance criteria

- [ ] Your existing Week 2 brick-breaker repo (or a clean fork called `c11-week-03-brick-breaker-<yourhandle>`) is updated.
- [ ] A Git tag `pre-juice` exists, pointing to the last commit before juice was added.
- [ ] `python -m py_compile <main>.py` succeeds with no output.
- [ ] `python <main>.py` opens the window and the game is immediately playable.
- [ ] **Screen shake** fires on every brick destruction. Magnitude scales: a single-hit brick gets a small shake (~6 px, ~200 ms), a tougher brick (if any) gets bigger.
- [ ] **Screen shake** fires on ball loss (when the ball falls past the bottom). Magnitude ~14 px, ~350 ms.
- [ ] **Particle burst** fires at the brick's centre on destruction — at least 12 particles, lifetime ~400 ms, in the brick's colour or Coin Pink.
- [ ] **Particle burst** fires at the ball's last position on ball loss — at least 20 particles, lifetime ~600 ms.
- [ ] **Three audio cues** play at the appropriate moments: paddle hit, brick destruction, ball loss. Each at a sensible volume (0.4–1.0 range). All loaded once at startup, played from cached `Sound` objects.
- [ ] `pygame.mixer.pre_init(buffer=512)` is called BEFORE `pygame.init()`. (We do not ship a 90 ms audio delay.)
- [ ] The HUD (score, lives) DOES NOT shake. World content (paddle, ball, bricks, particles) DOES shake.
- [ ] A 25–40 second comparison video lives at `comparison.mp4` or `comparison.webm` in the repo root (or is linked from `README.md`).
- [ ] A 200-word `REFLECTION.md` at the repo root that:
  - Names the three juice techniques you added.
  - Uses at least 2 vocabulary items from Lecture 1 (game feel, polish, juice as information, signal-to-noise, etc.).
  - Uses at least 2 vocabulary items from Lecture 2 (a Church lens OR an MDA layer, named correctly).
  - Cites Steve Swink at least once.
  - Names ONE thing you would tune differently if you had another five hours.
- [ ] Updated `README.md` includes:
  - A link or embed for the comparison video.
  - Credits for any audio you used (author, source URL, license).
  - A controls section.
  - A "Things I learned juicing this" section, 3+ specific bullets.

---

## Suggested order of operations

Build incrementally rather than trying to write the whole thing at once. Each phase ends with a commit.

### Phase 1 — Tag the "before" (~10 min)

1. Open your Week 2 brick-breaker repo. `git status` should be clean.
2. If you've made changes since Week 2, commit them now: `Final state of week-02 brick-breaker`.
3. Create the tag: `git tag pre-juice && git push --tags`.
4. (Optional but recommended) record your "before" footage now, before you change anything. 30 seconds of normal play.

### Phase 2 — Screen shake (~1 h)

1. Add the `ScreenShake` class from Lecture 1 §6 to your main file (or a new `juice.py`).
2. Instantiate one `shake = ScreenShake()` at startup.
3. Call `shake.update(dt)` once per frame in the update phase.
4. Wherever you `screen.blit` or draw the world, apply `shake.offset()` as the offset. Apply it to the paddle, ball, and bricks. **Do not** apply it to the HUD.
5. Call `shake.trigger(6.0, duration=0.2)` from your brick-destruction handler.
6. Call `shake.trigger(14.0, duration=0.35)` from your ball-loss handler.
7. Run, play, tune. Commit: `Add screen-shake on brick destroy and ball loss`.

### Phase 3 — Particle burst (~1.5 h)

1. Add the `Particle` dataclass and `spawn_burst(...)` from Lecture 1 §7.
2. Maintain a `particles: list[Particle] = []` in your game state.
3. In the per-frame update phase, after the simulation: `for p in particles: p.update(dt)` then `particles = [p for p in particles if p.alive]`.
4. In the render phase, after drawing the world: `for p in particles: p.draw(screen, shake.offset())`.
5. In your brick-destruction handler: `particles.extend(spawn_burst(brick.center, count=12, lifetime=0.4))`.
6. In your ball-loss handler: `particles.extend(spawn_burst(ball.pos, count=24, lifetime=0.7, speed=320))`.
7. Run, play, tune. Commit: `Add particle bursts on brick destroy and ball loss`.

### Phase 4 — Audio cues (~1.5 h)

1. Acquire three short `.wav` or `.ogg` files (paddle, brick, loss). SFXR generates all three in <10 minutes.
2. Add `pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)` *before* `pygame.init()`.
3. Load each as a `Sound` at startup. Set volumes: paddle ~0.5, brick ~0.7, loss ~1.0.
4. Call `paddle_sound.play()` from your paddle-hit handler, etc.
5. Pitch variation (recommended): for the brick sound, vary `set_volume(random.uniform(0.5, 0.9))` per play to keep the sound from going robotic.
6. Run, play, tune. Commit: `Add three audio cues`.

### Phase 5 — Tune (~2 h)

1. Play for a full minute. Notice what's *too much* and what's *not enough*.
2. Common adjustments:
   - Paddle-hit shake is usually too loud — turn it down to ~3 px or 0 px.
   - Brick destruction lifetime is usually slightly short — push to 500 ms.
   - Ball-loss shake is usually right at first try — if it isn't, you're probably over-tuning.
3. Bring in one playtester. Watch them play (don't narrate). Note 3 things you'd change.
4. Apply your changes. Re-test.
5. Commit: `Tune juice values from playtest feedback`.

### Phase 6 — Record the comparison video (~1.5 h)

See [challenge-01-juice-comparison-video.md](../challenges/challenge-01-juice-comparison-video.md) for the full spec. The short version:

1. Check out the `pre-juice` tag. Record 30 seconds of normal play. Save as `before.mp4`.
2. Check out `main` (juiced version). Record 30 seconds of as-similar-as-possible play. Save as `after.mp4`.
3. Stack horizontally with ffmpeg or OBS. Save as `comparison.mp4`.
4. Add labels "before" and "after."
5. Commit the video file (or link to it from `README.md`).

### Phase 7 — Reflection + README (~1 h)

1. Write `REFLECTION.md`. 200 words, vocabulary used correctly.
2. Update `README.md` with the video link, audio credits, controls, and the "Things I learned juicing this" section.
3. Final commit: `Write reflection and update README`.
4. Push everything. Make sure the public repo URL works on a fresh clone.

---

## Rubric

| Criterion | Weight | What "great" looks like |
|----------|-------:|-------------------------|
| All three juice techniques implemented | 25% | Shake, particles, audio all fire on the right events with sensible magnitudes |
| Tuning quality | 20% | A first-time viewer can tell which events are big vs small from the feel alone; no effect is so loud it obscures gameplay |
| Comparison video | 20% | Side-by-side; same gameplay; clear labels; ≤ 50 MB; ≤ 40 s |
| Reflection (vocabulary correctness) | 15% | Swink cited; at least 2 Lecture 1 + 2 Lecture 2 terms used correctly |
| README quality | 10% | Audio credits present; controls listed; "things I learned" has 3+ specific bullets |
| `pre-juice` tag exists | 5% | Just yes/no |
| Commit history | 5% | Multiple commits with meaningful messages, one per phase |

---

## Stretch (if you finish early)

These are *stretch*. Do **not** lose the main spec chasing them.

- **Hit-stop.** Add a 30–50 ms simulation freeze on brick destruction. Cheap, hugely impactful. The single best stretch goal this week.
- **Variable shake direction.** Side-wall hits shake horizontally, top-wall hits shake vertically (see Homework Problem 3).
- **Brick-colour-tinted particles.** When a brick is destroyed, spawn particles in *its* colour, not a fixed Coin Pink. Communicates which brick was destroyed at a glance.
- **A second "before/after" video at different tuning levels.** Show "minimum juice that still reads" vs "what you shipped" vs "too much." Three columns instead of two.
- **A pitch-shifted brick sound that rises with the streak count.** Five bricks in a row each play at +5% pitch each. Resets after 1.5 seconds of no hit. This is the Bejeweled trick.

---

## What this prepares you for

- **Week 4** (Tilemaps & levels) reads brick/wall layouts from a file. You'll juice the wall-pop on level completion.
- **Week 5** (State machines) makes the title → playing → game-over flow explicit. Each transition gets its own juice signature.
- **Week 6** (Animation & juice) adds sprite-sheet animation, tweening, and squash-and-stretch — the deep dive into the same techniques you sampled here.
- **Week 11** (Playtesting) puts your fully-juiced game in front of five testers. Several will say "it feels great" without naming why. You will have the vocabulary; they will not. Translate for them.

---

## Resources

- This week's [Lecture 1](../lecture-notes/01-what-makes-a-game-feel-good.md) and [Lecture 2](../lecture-notes/02-the-four-lenses-and-the-MDA-framework.md).
- The week's [exercises](../exercises/) — copy from them.
- The week's [challenge](../challenges/challenge-01-juice-comparison-video.md) — the recording recipe is there.
- Steve Swink — *Game Feel* essays: <https://www.gamedeveloper.com/design/game-feel-the-secret-ingredient>
- Robert Nystrom — *Game Programming Patterns* (free): <https://gameprogrammingpatterns.com/>
- Jan Willem Nijman — *The Art of Screenshake* (GDC video): <https://www.youtube.com/watch?v=AJdEqssNZ-U>

---

## Submission

When done:

1. Push your repo to GitHub with a public URL.
2. Make sure `README.md` links to the comparison video and credits all audio.
3. Make sure the `pre-juice` tag is pushed (`git push --tags`).
4. Make sure `python -m py_compile <main>.py` is clean on a freshly cloned copy.
5. Submit the repo URL on the course tracker.

You took a correct prototype and made it *land*. That is the work this whole phase has been building toward. Next week we add levels — the thing that turns a juiced prototype into something the player can actually progress through.
