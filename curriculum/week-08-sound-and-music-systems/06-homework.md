# Week 8 Homework

Six practice problems that revisit the week's topics. The full set should take about **5-6 hours** in total. Work in your Week 8 Git repository so each problem produces at least one commit you can point to later.

The work this week splits between *the mixer* (problems 1-3) and *the content side* (problems 4-6). The mini-project assembles the whole stack; these homework problems are the parts.

Each problem includes:

- A short **problem statement**.
- **Acceptance criteria** so you know when you are done.
- A **hint** if you get stuck.
- An **estimated time**.

---

## Problem 1 — Audit your Week-6 player for audio events

**Problem statement.** Take the `Player` class from your Week-6 mini-project. Open `main.py` (or wherever the class lives). Walk every state transition on the player's FSM and identify every moment that *should* fire a sound event. Save the annotated list as `homework/p1_audio_events.md`. For each event, write four columns: the event name, the FSM state-pair that triggers it (e.g. `IdleState -> RunState`), the *bus* that the sound should route through (master, music, sfx, voice), and a sentence describing the intended sound (e.g. "soft footfall, ~150 ms WAV, looping while in RunState").

**Acceptance criteria.**

- A file `homework/p1_audio_events.md` exists.
- At least eight distinct audio events are named.
- Each event has a bus assignment.
- The list distinguishes "fire-on-transition" events (jump, land, attack) from "looping-while-in-state" events (footsteps, ambient drone).
- At least one event uses the `voice` bus (e.g. a hurt grunt or a death cry).

**Hint.** Footsteps loop while in RunState; they do not fire on transition into RunState. Jump fires on `Grounded -> JumpState` transition. Land fires on `JumpState -> Grounded` *if* the fall velocity was non-trivial. Damage events fire on hp-decrement, independent of FSM state. Death is its own event.

**Estimated time.** 30 minutes.

---

## Problem 2 — Round-trip an `AudioSettings` dataclass through atomic write

**Problem statement.** Write `homework/p2_audio_settings_roundtrip.py` that:

1. Defines the `AudioSettings` dataclass from Lecture 2 §5.1 with at least four float fields (master / music / sfx / voice volumes) and three bool fields (music / sfx / voice muted).
2. Constructs an `AudioSettings` with non-default values.
3. Writes it to `audio_settings.json` using the atomic-write pattern from Week 7 Lecture 3 §4 — write to `.tmp`, `os.fsync`, `os.replace`.
4. Reads it back from disk.
5. Asserts the loaded `AudioSettings` equals the original field-by-field.
6. Prints `PASS` or fails loudly with the first mismatched field.

The point: Week 8's settings persistence reuses Week 7's atomic-write discipline. The two weeks compose.

**Acceptance criteria.**

- A file `homework/p2_audio_settings_roundtrip.py` exists and runs.
- The atomic-write pattern is implemented (you can see the `.tmp` file appear and disappear by inserting a `print` before the `os.replace` call).
- The script prints `PASS` after a clean round-trip.
- `python -m py_compile homework/p2_audio_settings_roundtrip.py` succeeds.
- All function signatures have type hints.

**Hint.** Reuse the `gamestate_to_dict` / `gamestate_from_dict` pair shape from Week 7 Lecture 1. For an `AudioSettings`, the body is literally `asdict(settings)` for to-dict, and a hand-written `from_dict` with defaults for each field (so missing keys do not crash). The atomic-write boilerplate is a four-line helper.

**Estimated time.** 50 minutes.

---

## Problem 3 — Wire ducking through your Week-6 player

**Problem statement.** Take your Week-6 mini-project (or a copy in `homework/p3_ducked_player/`). Wire the `AudioMixer` and ducking pattern from Exercise 2 into your player's existing audio. When the player picks up an item, play a "pickup jingle" through the `voice` bus that ducks the music. Use the `USEREVENT + 1` event for the duck-release.

**Acceptance criteria.**

- A `homework/p3_ducked_player/` folder contains a runnable Pygame project.
- `main.py` imports `AudioMixer` (you may inline the class from Exercise 2 or import it from a file at the project root).
- The `play_voice` call routes through the voice bus.
- The duck fade is visible — if you log the music bus volume per frame, you see it descend over 300 ms and rise back over 300 ms.
- A short demo video (~10 seconds, `demo.mp4` in the folder) captures the picking-up-and-ducking flow.
- `python -m py_compile main.py` succeeds.

**Hint.** Reuse the `AudioMixer` class from Exercise 2 verbatim. The only new thing is calling `mixer.play_voice(pickup_jingle)` when your existing pickup logic fires. The endevent wiring is already in `play_voice`.

**Estimated time.** 75 minutes.

---

## Problem 4 — Source one CC-BY asset and write the credit

**Problem statement.** Visit Freesound or OpenGameArt. Find one SFX clip you would use in a portfolio game (suggested: a coin-pickup chime, a sword swing, or a magical sparkle). Filter by licence — pick CC-BY 3.0 or 4.0. Download. Save in `homework/p4_attribution/sfx.<ext>`.

Write `homework/p4_attribution/CREDITS.md` with the canonical four-part attribution string:

```
"<Asset Title>" by <Creator Name> (<Asset URL>)
licensed under CC-BY <version> (<licence URL>).
```

Then write a 50-100-word note in `homework/p4_attribution/note.md` answering:

- Why you picked CC-BY 3.0/4.0 over CC-BY-SA 3.0/4.0 for a hypothetical commercial game.
- One way you would *credit visibly* in the game's UI (e.g. a credits screen, a hover tooltip, a README link).

**Acceptance criteria.**

- A `homework/p4_attribution/` folder exists with `sfx.<ext>`, `CREDITS.md`, and `note.md`.
- The credit string is the canonical four-part form.
- The licence URL points to the official Creative Commons page for the licence version (not a third party).
- `note.md` cites Lecture 3 §4 by name.

**Hint.** A CC-BY licence URL is one of `https://creativecommons.org/licenses/by/3.0/` or `https://creativecommons.org/licenses/by/4.0/`. Use the exact version that the asset is licensed under; the two versions are not interchangeable.

**Estimated time.** 40 minutes.

---

## Problem 5 — Implement a settings menu with three sliders

**Problem statement.** Build `homework/p5_settings_menu/main.py` — a small Pygame settings panel with three sliders: master, music, sfx. Each slider is a horizontal bar with a draggable knob. Below the sliders, three mute checkboxes (one per bus). Below those, a "Test SFX" button that plays a short tone routed through the SFX bus, and a "Test Music" button that toggles the music loop.

The settings panel reads from and writes to `audio_settings.json` using the atomic-write pattern from problem 2. Closing the window persists the current settings.

**Acceptance criteria.**

- A `homework/p5_settings_menu/main.py` exists and runs.
- The three sliders accept mouse-drag input. Dragging a slider updates the bus volume in real time — confirm by holding the Test SFX button while dragging the SFX slider.
- The three mute checkboxes toggle on click and immediately silence the bus.
- On window close, the settings persist to disk via atomic write.
- On startup, the panel reads the previous settings (or applies defaults if no file exists).
- `python -m py_compile main.py` succeeds.

**Hint.** A slider is a `pygame.Rect` for the track, another `pygame.Rect` for the knob, and a "is the knob being dragged?" boolean. On `MOUSEBUTTONDOWN` over the knob, start drag. On `MOUSEMOTION` while dragging, update the knob's `x`. On `MOUSEBUTTONUP`, stop drag. The volume is `(knob.x - track.left) / track.width`.

**Estimated time.** 90 minutes.

---

## Problem 6 — Benchmark Sound load time vs play time

**Problem statement.** Write `homework/p6_load_vs_play.py` that:

1. Loads ten short SFX files (you may synthesise them in code via Exercise 1's technique, or use Kenney's `interface-sounds` pack).
2. Measures the wall-clock time to *load* each sound (the `pygame.mixer.Sound(path)` call).
3. Measures the wall-clock time to *play* each sound (the `Sound.play()` call returning a Channel).
4. Reports both medians using `statistics.median` over 100 trials.
5. Prints a table: format, load_ms, play_us.

Use `time.perf_counter()` for both measurements.

**Acceptance criteria.**

- A file `homework/p6_load_vs_play.py` exists and runs.
- The output table shows ten rows (one per sound).
- The "load" column is in *milliseconds* (typically 1-20 ms per file).
- The "play" column is in *microseconds* (typically 50-500 us).
- The script prints a note at the bottom observing whether the play-time ratio is *consistent* with the lecture's claim that "Sound.play is microseconds while Sound() construction is milliseconds."
- `python -m py_compile homework/p6_load_vs_play.py` succeeds.

**Hint.** Use `time.perf_counter()` not `time.time()`. The play-time is so short that 100 trials are necessary to get a stable median; the load-time is large enough that you might only load each file *once* and time that single load. Re-loading a file via `pygame.mixer.Sound(path)` is what triggers the disk read and decode — keep the cache cold for the load measurement.

**Estimated time.** 50 minutes.

---

## What you should have at the end of homework

A `homework/` folder containing:

- `p1_audio_events.md` — your Week-6 player annotated by audio event.
- `p2_audio_settings_roundtrip.py` — atomic-write round-trip for `AudioSettings`.
- `p3_ducked_player/` — Week-6 player with pickup-jingle-ducks-music.
- `p4_attribution/` — one CC-BY asset, the credit string, and the note.
- `p5_settings_menu/main.py` — a working settings panel with sliders.
- `p6_load_vs_play.py` — the load-vs-play microbenchmark.

Each problem produces one or two commits. By Sunday this folder is a portfolio-worthy demonstration that you understand every layer of game audio — event design, ducking, asset licensing, settings persistence, and mixer performance — in code you wrote, on numbers you measured.

The mini-project then assembles the parts.

---

*If you are short on time, prioritise problems 2 (atomic-write round-trip), 3 (ducking wired through real code), and 5 (settings menu). These three are the engineering core. Problems 1, 4, and 6 are valuable but slightly more peripheral.*
