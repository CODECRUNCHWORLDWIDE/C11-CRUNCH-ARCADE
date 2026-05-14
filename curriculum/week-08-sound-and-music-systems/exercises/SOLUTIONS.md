# Exercises — Solutions and Common Bugs

The four exercise files in this folder ship with their bodies *filled in*. They are not blanks; they are reference implementations you read, run, and modify. This document is the *teardown* — what each exercise is teaching, what people commonly get wrong when they try to write it themselves, and which lines deserve a second look.

Open each `.py` file alongside the matching section here. Do not skip ahead to the "Common bugs" sub-section until you have run the file at least once with headphones on.

---

## Exercise 1 — Mixer init and SFX (`exercise-01-mixer-init-and-sfx.py`)

### What this exercise teaches

- The `pygame.mixer.pre_init(...)` call placed *before* `pygame.init()`. The order is non-negotiable; reversing it leaves the mixer at whatever the platform default happens to be.
- The four parameters to `pre_init` — frequency, size, channels, buffer — and the conventional values for each on a 2D Pygame game.
- `pygame.mixer.set_num_channels(N)` as a separate call after `pygame.init()`. The default 8 channels is too few for a typical action game; 16 is the standard.
- Synthesising audio from `numpy` arrays via `pygame.sndarray.make_sound`. This is the technique used to ship test tones without external assets — useful for unit tests, CI pipelines, and "minimal repro" bug reports.
- The clipping behaviour when you stack eight loud sounds simultaneously. The audible crackle is the auditory signal that your mix is summing past 1.0; the fix is the bus structure from Exercise 2.

### What "done" looks like

The eight coloured swatches appear across the bottom of the window. Pressing `1` plays a clean C4 (~261 Hz) sine. Pressing `2` plays D4. The HUD shows current channel utilisation. Pressing `SPACE` plays all eight tones at once; you hear a slightly clippy chord. The 5 ms attack and 25 ms release envelopes mean none of the tones click at the start or end.

### Common bugs

**Bug A — `pre_init` after `pygame.init`.**
Symptom: the parameters you pass to `pre_init` are silently ignored; the mixer runs at platform-default 22050 Hz or 48000 Hz instead of your requested 44100 Hz.
Cause: `pygame.init()` lazily initialises the mixer with default parameters; `pre_init` only matters if it is called before init.
Fix: the very first lines of `main()` are `pygame.mixer.pre_init(...)` then `pygame.init()`. Memorise the order.

**Bug B — `numpy not installed`.**
Symptom: `ModuleNotFoundError: No module named 'numpy'` on the import line.
Cause: numpy is in the lecture's recommended `pip install` list but is genuinely optional for the rest of the week.
Fix: `pip install numpy`. Or skip Exercise 1 and run Exercises 2-4 with the synthesised audio variations.

**Bug C — Tones click at the start.**
Symptom: every tone has a perceptible "tk" at attack.
Cause: the synthesised envelope has zero attack samples or `attack_n` is set to a sub-millisecond value.
Fix: 5 ms (`SAMPLE_RATE_HZ * 0.005`) is the floor for clean attack. Some headphones reveal sub-5 ms clicks; bump to 10 ms if you hear them.

**Bug D — Pressing `SPACE` silences eight channels.**
Symptom: nothing plays at all on space.
Cause: a previous run already used eight channels and you allocated only 8 (`NUM_CHANNELS = 8`).
Fix: `NUM_CHANNELS = 16` is the exercise default. If you lowered it for testing, restore it.

### Things to notice in the code

- Line ~85 (`synthesise_tone`): the wave is generated as a `numpy` float array, scaled to int16, then duplicated into stereo. The `np.column_stack` call is the mono-to-stereo step.
- Line ~155 (the order of `pre_init` / `init` / `set_num_channels`): this is the *only* correct order. Reversing any pair will silently change behaviour.
- Line ~205 (the busy-channel count in the HUD): a simple `sum(1 for i in range(N) if Channel(i).get_busy())` loop. Useful debug tool you will reuse for the rest of the week.

### Variations worth trying

1. Drop `SAMPLE_RATE_HZ` to 22050 and listen for the loss of high-frequency detail. The eight tones are still in the audible range but the harmonics above 11 kHz are gone.
2. Set `NUM_CHANNELS` to 4. Press `SPACE` to play eight tones; only four play, and pressing `1-8` after the chord shows the eviction behaviour.
3. Change `BUFFER_SAMPLES` to 128. The latency drops to ~3 ms. On a low-spec laptop you may hear audio breakup; this is the latency/CPU trade-off in action.

---

## Exercise 2 — Three-bus mixer with ducking (`exercise-02-three-bus-mixer-with-ducking.py`)

### What this exercise teaches

- The `Bus` dataclass with parent / child links and `effective_volume()` walking up the chain.
- The `AudioMixer` facade owning a three-deep tree (master → music / sfx / voice).
- Event-driven ducking via `Channel.set_endevent(DIALOGUE_END_EVENT)` and a `pygame.USEREVENT` constant.
- The linear duck fade animated per-frame in `update_duck(dt_ms)`.
- The ref-count pattern for the duck-during-duck edge case.

### What "done" looks like

Press `SPACE` to start a looping pad as music. Press `D` to play the 1.5 s dialogue clip. The music slider visually drops from ~0.36 effective to ~0.18 over 300 ms, holds through the dialogue, and rises back over 300 ms when the dialogue ends. Press `D` twice in quick succession; the ref-count goes to 2; the music stays ducked until both dialogues finish.

### Common bugs

**Bug A — The duck never releases.**
Symptom: the music stays at 30% even after the dialogue ends.
Cause: the `DIALOGUE_END_EVENT` is not being posted, or the event-handler is matching the wrong constant.
Fix: confirm `Channel.set_endevent(DIALOGUE_END_EVENT)` was called on the same channel that plays the sound. The exercise uses `pygame.mixer.Channel(0)` explicitly so the channel identity is unambiguous.

**Bug B — Trigger D twice; music stays ducked forever.**
Symptom: the second dialogue's endevent fires, but the duck does not release.
Cause: missing ref-count. The second `begin_duck` captures `from_vol = 0.3` (already ducked), the second `end_duck` sees the count drop to 1 but does not check `== 0`, so the restore is never queued.
Fix: the ref-count semantics from Lecture 2 §2.3. Only restore when the count returns to zero.

**Bug C — Music starts at 0 instead of 0.6.**
Symptom: pressing `SPACE` plays the pad silently.
Cause: `music_loop.set_volume(mixer.music.effective_volume())` is computed *before* `music_channel.play(...)` but the bus chain returns 0 because the master is muted or the music bus is muted.
Fix: print `mixer.music.effective_volume()` immediately before the play call. Confirm it is non-zero. If it is, the issue is elsewhere; if it is zero, you have a muted ancestor in the chain.

**Bug D — Duck fade is not visible (snap to value).**
Symptom: the music slider jumps instantly to 30% instead of fading.
Cause: `update_duck` is not being called, or `dt_ms` is being passed as zero (an integer-division accident).
Fix: confirm `clock.tick(TARGET_FPS)` returns milliseconds (it does) and that the return value is passed to `update_duck`. The `int` from `clock.tick` is in ms; do not divide by 1000.

### Things to notice in the code

- Line ~95 (`Bus.effective_volume`): the while-loop walks the parent chain. It does not recurse — a recursion would be cleaner but the iterative form is faster for the depth-2 or depth-3 trees we use.
- Line ~155 (the duck ref-count): `ref_count` is a plain `int`. The pattern is *not* a semaphore implementation — it is the same idea expressed in twelve lines for a single-threaded game loop.
- Line ~180 (`_reapply_music_volume`): re-pushing the music volume to `pygame.mixer.music.set_volume(...)` is necessary because the streaming subsystem owns its own playback state. Setting `self.music.volume` only updates the bus chain; the streaming module needs its own call.

### Variations worth trying

1. Lower `DUCK_TARGET_MUSIC_VOLUME` to `0.10`. The dialogue becomes much more prominent. Too low and the music feels like it disappears; 0.30 is a sane default.
2. Change `DUCK_FADE_MS` to `1000`. The fade is now slow enough to be visibly animated; the music feels syrupy. 300 ms is the sweet spot.
3. Add a fourth bus `ui` and route a click sound through it. Confirm the UI bus is independent of `sfx` — you can mute the SFX bus and still hear the UI click.

---

## Exercise 3 — Spatial attenuation and panning (`exercise-03-spatial-attenuation-and-panning.py`)

### What this exercise teaches

- The `distance_attenuation` function — linear from `min_distance` to `max_distance`, clamped at the ends.
- The `horizontal_pan` function — `(left, right)` volumes from `pan_distance`-normalised horizontal offset.
- The split between `Sound.set_volume(scalar)` (the bus multiplier) and `Channel.set_volume(left, right)` (the pan).
- The early-out: if attenuation is zero, do not bother allocating a channel.

### What "done" looks like

Three coloured emitter squares are placed across the field, each with a faint ring at `min_distance` (60 px) and `max_distance` (420 px). The cross-hair listener moves with WASD. Pressing `1`, `2`, or `3` fires the matching emitter; you hear it panned and attenuated based on your current position. The live HUD updates the `(att, L, R)` values continuously as you move.

### Common bugs

**Bug A — All sounds come from the centre, no pan.**
Symptom: you can hear distance attenuation but the stereo balance never changes.
Cause: forgot the `Channel.set_volume(left, right)` call after `Sound.set_volume(scalar)`. The `Sound`'s `set_volume` is mono (or takes one scalar); the pan only lives on the `Channel`.
Fix: capture the return of `Sound.play()` as a `Channel`, then call `channel.set_volume(left, right)`. The exercise's `play_spatial` function does this in lines 130-140.

**Bug B — Sounds remain audible at full volume beyond `max_distance`.**
Symptom: distance has no effect.
Cause: `Sound.set_volume(bus_volume * att)` was passed `bus_volume * 1.0` because `att` was computed with the wrong distance.
Fix: print `att` to the HUD (the exercise already does this). Confirm it falls to 0 as you walk past 420 px from the emitter.

**Bug C — Headphones reveal nothing — laptop speakers sum to mono.**
Symptom: you cannot hear the pan.
Cause: laptop speakers are spaced so closely that you cannot hear stereo separation, and many laptops downmix to mono in some modes.
Fix: use headphones. This is the bug the prerequisites section warned about. The pan code is correct; your output device is the problem.

**Bug D — The early-out fires too aggressively.**
Symptom: emitters at the edge of the field never play even when you are close to the emitter's `min_distance`.
Cause: `MAX_DISTANCE` is set lower than the emitter-to-listener distance. The screen is 900 wide; if `MAX_DISTANCE` is 300 you cannot hear an emitter at one corner from the opposite corner.
Fix: 420 px max distance with a 900 px window is the exercise default. For larger windows, scale `MAX_DISTANCE` proportionally.

### Things to notice in the code

- Line ~75 (`distance_attenuation`): the linear curve is intentional. Inverse-square is physically correct but sounds wrong in 2D games — sounds drop off too quickly.
- Line ~92 (`horizontal_pan`): the pan is *only* horizontal. We do not pan vertically because human ears process front-back direction with HRTFs (head-related transfer functions), which are too complex for this scope.
- Line ~110 (`play_spatial`): the early-out `if att <= 0.0: return` is not just an optimisation — it also prevents a `Channel` from being allocated for an inaudible sound. In a busy scene this saves channels for sounds that will actually be heard.

### Variations worth trying

1. Add a vertical pan: place two virtual stereo speakers at `(listener_x, listener_y - 100)` and `(listener_x, listener_y + 100)` and use the *vertical* distance to weight a "front mix" and "rear mix." Pygame has no native rear channel, so you would fold rear into the centre at reduced volume. This is the simplest model of binaural pan and is a stretch goal.
2. Change the distance curve to inverse-square: `att = (min_distance ** 2) / (d ** 2)` clamped at `[0, 1]`. Compare against the linear curve. Most ears prefer linear for game audio.
3. Add a "Doppler" effect: pitch-shift the emitter's tone by the velocity component along the listener-source line. This requires playing the sound through `pygame.sndarray` resampled — a significant exercise on its own.

---

## Exercise 4 — Layered music crossfade (`exercise-04-layered-music-crossfade.py`)

### What this exercise teaches

- Two stems on dedicated, reserved channels (`NUM_CHANNELS - 2` and `NUM_CHANNELS - 1`) so general SFX cannot evict them.
- Both stems started on the same `play()` call so they stay in sync.
- The `LayerCrossfade` dataclass holding the animation state.
- The `request_combat` / `request_explore` API that re-targets the fade without restarting playback.
- Synthesising stems whose duration is a whole number of modulation cycles, so the loop seam is sample-clean.

### What "done" looks like

Press `SPACE` to start both stems looping. The explore stem is at full bus volume; the combat stem is at 0. Press `TAB` to crossfade. Over 1.5 seconds, the explore stem fades down and the combat stem fades up. The two bars in the UI animate the fade. Press `TAB` again to swap back. The stems never go out of sync because both have been playing continuously since `SPACE`.

### Common bugs

**Bug A — Stems drift out of sync over time.**
Symptom: after one minute, the combat layer's beat lags the explore layer's beat.
Cause: the two stems are different lengths in samples. The `synthesise_loop` function rounds the duration to a whole modulation cycle; if both stems use the same `modulation_hz`, the lengths *will* match. If they differ, they drift.
Fix: print `explore_sound.get_length()` and `combat_sound.get_length()` (the exercise does so in the HUD). They must be equal. If they are not, adjust `modulation_hz` so the cycles divide evenly.

**Bug B — Pressing `TAB` does nothing.**
Symptom: the state toggles but the music does not change.
Cause: `update_layered_music` is not being called, or `dt_ms` is being passed as seconds.
Fix: confirm `crossfade.advance(dt_ms)` is in the update block. The `dt_ms` value comes from `clock.tick(TARGET_FPS)`, which returns milliseconds.

**Bug C — Loud click at the loop point.**
Symptom: every 4 seconds (the loop length) you hear a click.
Cause: the synthesised stem does not end on a zero-crossing.
Fix: the exercise applies a 20 ms fade in/out via `attack_n` and `release_n`. If you removed them or set them to zero, the loop click returns. Restore the envelope.

**Bug D — Combat layer plays at full volume the moment `SPACE` is pressed.**
Symptom: both stems are audible right after starting, even though the state is EXPLORE.
Cause: `combat_sound.set_volume(...)` was set to a non-zero value at start.
Fix: `combat_sound.set_volume(music_bus_volume * crossfade.target_combat)` — and `target_combat` is initialised to `0.0`. The first frame should multiply `0.0`, not `1.0`. The exercise gets this right; if you copied incorrectly, double-check the start-up volume assignments.

### Things to notice in the code

- Line ~105 (`synthesise_loop`): the duration is rounded *up* to a whole number of modulation cycles. This is the discipline that makes the loop seamless without authoring in Audacity.
- Line ~145 (`LayerCrossfade.current_levels`): linear interpolation. For two correlated stems (the same music with different orchestration), linear is correct. For two unrelated stems an equal-power crossfade would be correct.
- Line ~210 (`start_music`): both `play()` calls happen on the same Python statement (one after the other within microseconds). The two stems are sample-aligned to within ~1 ms — well below perception.

### Variations worth trying

1. Add a third layer (e.g. "boss") with a still-higher intensity. Crossfade between three states by tracking two crossfade ramps.
2. Change the crossfade to equal-power: `e = cos(t * pi/2)`, `c = sin(t * pi/2)`. Compare against the linear default. You will hear no difference for correlated stems and a slight "dip in the middle" disappear for uncorrelated stems.
3. Crossfade between two *different* music pieces (e.g. menu music and gameplay music). Equal-power is correct here; linear will show a perceptible mid-fade dip.

---

## How to extend these exercises into your own week

The exercises are *infrastructure*. The mini-project assembles them into a real game audio module:

- The `pre_init` boilerplate from Exercise 1 → the `init_audio()` function of the mini-project's `audio.py`.
- The `Bus` class and `AudioMixer` facade from Exercise 2 → the mini-project's bus tree.
- The duck pattern from Exercise 2 → the dialogue subsystem of the mini-project.
- The `distance_attenuation` and `horizontal_pan` from Exercise 3 → the spatial SFX in the combat zone.
- The `LayerCrossfade` from Exercise 4 → the combat-layer fade-in in the mini-project.

Read the mini-project README before you write any audio code outside these exercises. It tells you the exact file shape and acceptance criteria. The exercises are the parts; the mini-project is the assembly.

---

*If you find errors in these solutions or the exercises themselves, please open an issue.*
