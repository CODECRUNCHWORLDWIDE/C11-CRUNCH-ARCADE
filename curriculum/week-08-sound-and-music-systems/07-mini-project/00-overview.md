# Mini-Project — A Tiny Arcade Game with a Real Audio System

> Build a small Pygame arcade game with a single-screen overworld containing two NPC speakers and a combat zone, and a *real* audio system: three buses (master / music / sfx / voice, with voice ducking the music), layered music with a 1.5 s crossfade between explore and combat layers, spatial SFX attenuation in 2D, and a settings panel with three sliders that persists per-bus volume to disk using last week's atomic-write pattern. Record a 20-second demo. Write a 250-word reflection. Push to GitHub.

This is the artefact this week was building toward. By Sunday you have a tiny but complete game whose audio system would not embarrass a small indie studio. The *game* itself is intentionally minuscule — a single screen, a player, two NPCs, one combat zone — because the *audio system* is the substantive code this week.

The mini-project assembles every piece of the week: the mixer initialisation from Lecture 1, the bus tree and ducking from Lecture 2, the layered music and spatial attenuation from Lecture 2, and the loop authoring and licence discipline from Lecture 3. Plus last week's atomic-write pattern for the settings file.

**Estimated time:** 9 hours (split across Wednesday → Sunday).

---

## What you will build

A new repo (or an `audio-game/` subfolder of your portfolio repo), with:

1. **An engine** — Python codebase, ~600-900 lines, that loads a single-screen overworld and renders a Coin-Pink player who can move with WASD.
2. **Two NPC speakers** — fixed positions on the field. Walking up to either NPC and pressing `E` triggers a short dialogue line (a ~2 s OGG clip). The dialogue ducks the music for the line's duration.
3. **A combat zone** — a rectangular region of the field marked visually. When the player enters, the music crossfades from explore-layer to combat-layer over 1.5 s. When the player leaves, it crossfades back. Inside the zone, pressing `Space` fires an attack that plays a spatial SFX at the nearest "enemy marker" (a static target on the field). The SFX attenuates with distance and pans with horizontal offset.
4. **An `audio.py` module** — the audio subsystem from Lectures 1 and 2, refactored from Exercises 1-4 into a single coherent module.
5. **An `AudioSettings` dataclass** — the on-disk shape of the player's audio preferences. At minimum: `master_volume`, `music_volume`, `sfx_volume`, `voice_volume`, and three mute flags.
6. **A settings panel** — opened with `Esc`. Three sliders (master / music / sfx), three mute checkboxes (music / sfx / voice). Saving the panel writes the settings to `audio_settings.json` via the atomic-write pipeline from Week 7.
7. **Layered music** — two synchronised stems (explore + combat) crossfaded by the player's combat-zone entry/exit.
8. **A "saving..." flash** — when settings save, a small badge appears for ~30 frames. Reuses the Week 7 pattern.
9. **A `CREDITS.md`** — lists every audio asset used, the creator, the source URL, and the licence. CC-BY assets get the canonical four-part credit string.
10. **A 20-second demo video** at `demo.mp4` showing: start the game, walk to NPC A, press `E`, hear ducked dialogue; walk to NPC B, hear ducked dialogue; walk into the combat zone, hear the music crossfade; fire an attack, hear the spatial SFX; walk out, hear music crossfade back; open settings, adjust sliders, close.
11. **A 250-word `REFLECTION.md`** using this week's vocabulary correctly.

You will NOT add:

- Enemy AI. The "enemy markers" in the combat zone are *static* — they exist so spatial SFX has a target. Week-11 capstone is where AI lives.
- Sprite-sheet animation. Reuse a single sprite per character; this week is about audio, not animation.
- Inventory or save system for game state. Audio settings persist; *game* state does not in this week's scope.
- Multiple levels. One screen.
- Online multiplayer. (Week 17 stretch.)

---

## Rules

- **You may** copy from this week's exercises freely — that is why they exist. The `Bus` class from Exercise 2, the spatial helpers from Exercise 3, and the `LayerCrossfade` from Exercise 4 are the starting points.
- **You may** reuse your Week-5 FSM and Week-6 juice modules if you have them. The mini-project is the *audio system*, not a rewrite of the engine.
- **You may** use the starter files (`starter_main.py`, `starter_audio.py`) in this folder as a scaffold. They have TODOs marking what to fill in.
- **You may NOT** load any `Sound` inside the game loop. All sounds load once at startup; the loop calls `play()` only.
- **You may NOT** put any `pygame.Surface`, `pygame.mixer.Sound`, or `pygame.font.Font` reference inside the `AudioSettings` save file. Same `to_dict` discipline as Week 7.
- **You may NOT** use MP3 for any clip that loops. OGG only for loops.
- **You may NOT** skip the atomic-write pattern for the settings file. The `os.replace` line is non-negotiable.
- **You may NOT** ship a CC-BY-SA or CC-BY-NC asset in this project. CC0 and CC-BY are the only acceptable licences.
- **You must** ship at least *one* CC-BY asset with the canonical four-part credit in `CREDITS.md`. Sourcing and crediting is part of the artefact.
- **You must** commit the demo video (or link to it).
- **Python 3.11+, Pygame 2.5+, numpy 1.24+** (numpy only required if you synthesise test stems rather than sourcing real assets).
- **Use a virtual environment.**

---

## Acceptance criteria

- [ ] A repo (or subfolder) called `c11-week-08-audio-game-<yourhandle>`.
- [ ] `python -m py_compile main.py audio.py` succeeds with no output.
- [ ] `python main.py` opens a window with a player on a single-screen overworld, two NPC markers, and a combat zone.
- [ ] Player can move with WASD.
- [ ] Walking up to an NPC and pressing `E` plays a dialogue clip on the voice bus that ducks the music. The music returns when the dialogue ends.
- [ ] Walking into the combat zone triggers a 1.5 s crossfade from explore to combat layer. Walking out triggers the reverse crossfade.
- [ ] Pressing `Space` inside the combat zone fires a spatial SFX at the nearest enemy marker. Far emitters are quieter; off-centre emitters pan.
- [ ] **`Esc`** opens a settings panel. The panel has three working sliders (master / music / sfx) and three mute checkboxes.
- [ ] Slider drag updates the bus volume in real time. The mute toggle silences the bus immediately.
- [ ] Closing the settings panel (or the game window) writes `audio_settings.json` via atomic write.
- [ ] On next startup, the previously-saved settings are loaded and applied before any audio plays.
- [ ] **`audio_settings.json`** contains the seven fields (4 floats + 3 bools) and a `schema_version: 1` field.
- [ ] **Atomic write:** check by inspecting the filesystem. After settings save, you see `audio_settings.json` and `audio_settings.json.bak`. There is no `audio_settings.json.tmp` after a successful save (it was renamed away).
- [ ] **At least one** CC-BY-credited asset is in `assets/audio/` and credited in `CREDITS.md` with the canonical four-part string.
- [ ] **`demo.mp4`** — 15-30 seconds, showing the dialogue duck / combat crossfade / spatial attack / settings flow.
- [ ] **`REFLECTION.md`** — 250 words at the repo root that:
  - Names the FOUR major audio features your game ships (three-bus mixer, ducking, layered music, spatial attenuation, settings persistence — pick four).
  - Identifies which Pygame primitive (`Sound`, `music`, `Channel`) you used for each.
  - Names the asset you sourced under CC-BY and where you got it.
  - Cites both Lecture 2 (*Mixing, buses, and dynamic music*) and Lecture 3 (*Authoring loops, formats, and the Godot bridge*) by name.
  - States ONE behaviour of the audio system you would want a play-tester to listen for to find a bug.
- [ ] **`CREDITS.md`** — credits for every audio asset, plus Pygame and (if used) Kenney/Freesound/OpenGameArt as source platforms.
- [ ] **`README.md`** includes:
  - A controls section.
  - A "What this demonstrates" section listing the audio features (three-bus mixer, ducking, layered music, spatial SFX, settings persistence).
  - The demo video inlined (or linked).
  - The asset credits inlined or linked.

---

## Suggested order of operations

Build incrementally rather than trying to write the whole thing at once. Each phase ends with a commit.

### Phase 1 — Scaffold the engine (~45 min)

1. Create the new repo.
2. Copy `starter_main.py` and `starter_audio.py` into the repo as `main.py` and `audio.py`.
3. Confirm the loop runs at 60 fps with the Coin-Pink player movable.
4. Confirm `pygame.mixer.pre_init` + `pygame.init` + `pygame.mixer.set_num_channels` initialise without errors.
5. Commit: `Scaffold the engine with mixer init and a movable player.`

### Phase 2 — Bus tree and a first SFX (~1 hour)

1. In `audio.py`, define the `Bus` class and the `AudioMixer` facade (copy from Exercise 2).
2. Load a single SFX (footstep WAV is fine; Kenney's `interface-sounds` pack has a "tick" you can use).
3. Wire it to fire on player movement: every ~250 ms while moving, play the footstep through the sfx bus.
4. Commit: `Bus tree, AudioMixer, and footstep SFX.`

### Phase 3 — NPC dialogue with ducking (~1.5 hours)

1. Add two NPC markers (static positions, drawn as coloured squares).
2. Detect proximity (`distance < 80 px` and `E` pressed).
3. Load two dialogue clips (you may synthesise them with Exercise 2's `synthesise_dialogue` function or source real ones).
4. Wire `play_voice` with `set_endevent(DIALOGUE_END_EVENT)`.
5. Confirm the music ducks when dialogue plays and restores when it ends.
6. Commit: `NPC dialogue with music ducking.`

### Phase 4 — Layered music with combat-zone crossfade (~1.5 hours)

1. Source or synthesise two stems (`explore-layer.ogg` and `combat-layer.ogg`). Synthesised stems are fine — Exercise 4's `synthesise_loop` produces seamless results.
2. Reserve channels 14 and 15 for the two stems.
3. Define a rectangular `combat_zone` on the field.
4. On enter, call `crossfade.request_combat(...)`. On exit, `request_explore(...)`.
5. Update the crossfade per frame.
6. Commit: `Layered music with combat-zone crossfade.`

### Phase 5 — Spatial attack SFX in the combat zone (~45 min)

1. Place 2-3 "enemy marker" sprites in the combat zone.
2. Pressing `Space` inside the zone fires a spatial SFX from the nearest enemy.
3. Use the `distance_attenuation` and `horizontal_pan` helpers from Exercise 3.
4. Commit: `Spatial attack SFX with attenuation and panning.`

### Phase 6 — Settings panel (~2 hours)

1. Define `AudioSettings` dataclass (master/music/sfx/voice volumes + three mute flags).
2. Implement `apply_settings(mixer, settings)` from Lecture 2 §5.1.
3. Implement atomic-write `save_audio_settings(path, settings)` reusing Week 7 Lecture 3 §4.
4. Implement `load_audio_settings(path)` with `.bak` fallback.
5. Build the panel UI (three horizontal sliders + three checkboxes + a Close button).
6. Wire `Esc` to open the panel; settings persist on close.
7. Commit: `Settings panel with atomic-write persistence.`

### Phase 7 — Polish, demo, reflection (~1.5 hours)

1. Add the "settings saved" flash badge.
2. Add a HUD showing FPS, current music state (`explore` / `combat`), and a "duck active" indicator.
3. Record `demo.mp4`: 20 seconds, with the dialogue duck, combat crossfade, spatial attack, and settings flow visible.
4. Write `REFLECTION.md` (250 words).
5. Write `README.md` and `CREDITS.md`.
6. Commit: `Polish, demo video, reflection.`
7. Push.

---

## Suggested code layout

```
audio-game/
├── main.py                     # game loop, player, NPCs, combat zone
├── audio.py                    # AudioMixer, Bus, ducking, crossfade, spatial
├── settings_panel.py           # the Esc-key panel (optional split)
├── assets/
│   └── audio/
│       ├── footstep.wav        # CC0 or CC-BY
│       ├── pickup.wav          # CC0 or CC-BY
│       ├── attack.wav          # CC0 or CC-BY
│       ├── dialogue-a.ogg      # CC-BY typical
│       ├── dialogue-b.ogg      # CC-BY typical
│       ├── explore-layer.ogg   # CC-BY typical
│       └── combat-layer.ogg    # CC-BY typical
├── audio_settings.json         # created at runtime
├── audio_settings.json.bak     # created at runtime
├── demo.mp4
├── README.md
├── REFLECTION.md
└── CREDITS.md
```

The split between `main.py`, `audio.py`, and `settings_panel.py` is the *minimum* sensible separation. You may collapse `settings_panel.py` into `main.py` if you prefer; do not collapse `audio.py` — that is the artefact.

---

## Grading rubric (self-assessed)

Score your own submission against this rubric before submitting. If any criterion is below "passing," go back and fix it.

| Criterion | Failing | Passing | Strong |
|---|---|---|---|
| **Mixer init** | `pygame.mixer.init` with default params; no `pre_init`. | `pre_init` before `pygame.init`; channels set explicitly. | Plus a defensive try/except for headless CI environments. |
| **Bus tree** | Single global volume. | Three buses (master / music / sfx / voice) with effective-volume traversal. | Plus a fourth bus (e.g. UI) for menu sounds. |
| **Ducking** | None. | Music ducks during dialogue with a 300 ms fade; ref-count handles overlapping triggers. | Plus an asymmetric fade (fast down, slow up) for production quality. |
| **Layered music** | Single track. | Two stems in sync, 1.5 s crossfade on combat-zone entry/exit. | Plus correct seamless loops authored in Audacity (Challenge 1). |
| **Spatial SFX** | All SFX centred at full volume. | Distance attenuation + horizontal pan applied to attack SFX. | Plus an early-out when `att <= 0` to save channels. |
| **Settings persistence** | Sliders work in-session but do not persist. | Atomic-write `audio_settings.json` with `.bak` fallback. | Plus a checksum (reusing Week 7 Lecture 3 §6) on the settings file. |
| **Asset credits** | No `CREDITS.md` or generic "thanks to Freesound." | Canonical four-part CC-BY string for every CC-BY asset; CC0 assets listed. | Plus the modification note for any edited asset. |
| **Reflection** | Generic; cites no lecture or source. | 250 words; cites Lecture 2 and Lecture 3; names the asset and licence. | Plus a concrete audio bug the writer found and fixed during testing. |

---

## Stretch goals

If you finish the core mini-project early and want to push further:

- **Add a fourth bus** for UI sounds (slider drag, button click, panel open/close). Route the Kenney `interface-sounds` pack through it.
- **Author your own loop in Audacity** for the explore layer (Challenge 1). Replace the synthesised stem with a real OGG. The audible quality jump is large.
- **Add a "test SFX" button** to the settings panel — plays a 1 kHz pink-noise burst through the SFX bus so the player can confirm the SFX slider works without entering combat.
- **Implement a fade-out on quit.** When the player closes the window, fade master to 0 over 500 ms before quitting. Better feel than an abrupt cut.
- **Author *two* layered music tracks** so the second stage of the game has a different explore/combat pair. The mini-project has one stage, so this is genuinely stretch.
- **Watch Marshall McGee's *Hades* audio analysis** (linked in `resources.md`) and write a 200-word note on which McGee technique you would adopt for your second project.
- **Read Godot's *Sync with audio* tutorial** and write 100 words on whether the technique is applicable to a rhythm version of your mini-project.

---

## Why this matters

By Sunday you have shipped an audio system that:

- Initialises a 44.1 kHz stereo mixer with explicit channels (Lecture 1).
- Routes sounds through a three-bus tree with effective-volume traversal (Lecture 2 §1).
- Ducks the music under dialogue with a fade and a ref-count (Lecture 2 §2).
- Crossfades two music stems in exact sync with no loop click (Lecture 2 §3, Lecture 3 §1).
- Attenuates and pans spatial SFX by distance from the listener (Lecture 2 §4).
- Persists per-bus volume and mute state to disk with atomic writes and a `.bak` fallback (Lecture 2 §5, reusing Week 7 Lecture 3).
- Credits CC-BY assets in a `CREDITS.md` with the canonical attribution string (Lecture 3 §4).

That feature set is the same one shipped by *Celeste*, *Hollow Knight*, and *Stardew Valley*. Your *game* is a tenth the size; your *audio system* is roughly the same shape. The portability of this week's code is high: the same `audio.py` drops into Week 11's capstone with minor renames and the capstone has the audio system it needs.

Next week — Transitioning to Godot — uses Godot's *AudioServer* and *AudioStreamPlayer2D* for the same feature set. The Pygame implementation you wrote this week is the *thinking*; the Godot rewrite next week is the *clicking*. The thinking ports cleanly.

---

*If you find errors in this material, please open an issue or send a PR. Future learners will thank you.*
