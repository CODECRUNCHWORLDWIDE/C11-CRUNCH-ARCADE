# Week 8 — Sound and Music Systems

Last week you wrote a save system that survives a crash. The disk is now a reliable subsystem. This week we turn to the speakers — the subsystem the player notices the most and the developer almost always notices last. By Sunday you ship a tiny arcade game with a *real* audio stack: three mixer buses, ducked dialogue, layered combat music, spatial SFX, and a settings panel that persists per-bus volume to disk using last week's atomic-write pattern.

Sound is the most undervalued discipline in indie game development. A muted clip of the game looks fine; the same clip with audio added gains a full league of perceived production value. The mid-tier indies who ship without an audio engineer almost always have a *mixing* problem — every SFX is the same volume, music drowns out dialogue, gunshots clip, the menu beep is twice as loud as the player's footsteps. None of this is a content problem. It is a *bus structure* problem, and a bus structure is fifty lines of code.

Pygame's `pygame.mixer` and Godot 4.x's `AudioServer` solve the same problem with very different vocabularies. Pygame gives you `Channel` objects, a `music` streaming singleton, and per-`Sound` volumes. Godot gives you a *graph* of `AudioServer` buses with `AudioEffect`s, three flavours of `AudioStreamPlayer`, and editor-driven routing. Both are correct. Both will ship a game. This week covers Pygame in depth — every mini-project ships with it — and reads Godot's audio stack as the *bridge* to Week 9, when C11 moves to Godot for the rest of the semester.

We start from the *Pygame mixer documentation*, Godot's *AudioServer* reference, two free CC-licensed asset sources (*Freesound*, *OpenGameArt*), and the *Audacity manual* — five free sources, all linked in `resources.md`. By Sunday you ship a tiny arcade game with **three buses (master / music / sfx), one ducked dialogue line, two-layer combat music with seamless looping, attenuated spatial SFX, and a settings panel that writes per-bus volume to a JSON file using last week's atomic-write pipeline**. The game itself is intentionally small — a player on a single screen who walks past two NPC speakers and into a "combat zone." The *audio system* is the artefact.

There is still no Godot in the exercises. The Godot material is in Lecture 3 and one read-only `.gd` reference file, so you can spot the equivalents when Week 9 lands. Every Pygame technique in this week's exercises ports to Godot with a one-line API change and the same mental model.

## Learning objectives

By the end of this week, you will be able to:

- **Explain** the three numbers that define every audio engine: sample rate (Hz), channel count (mono / stereo), and bit depth (8 / 16 / 24 / float). For a Pygame game you will pick 44100 Hz, 2-channel stereo, 16-bit signed, and you will know *why* for each number.
- **Initialise** `pygame.mixer` with explicit parameters before `pygame.init()`, allocate eight playback channels, and route SFX to channels and music to the dedicated `pygame.mixer.music` streaming module.
- **Distinguish** SFX from music as a *technical* distinction (decode-on-play vs stream-from-disk), not a content one. Know when to use `pygame.mixer.Sound` and when to use `pygame.mixer.music.load`.
- **Implement** a three-bus mixer in Pygame using channel groups and per-group volume multipliers. Master bus on top, music and SFX as children. Every `play()` call is multiplied through the chain.
- **Implement** dynamic music layering: two stems (e.g. "explore" and "combat") play in sync, and a `fade` between them transitions without a click or a beat drop.
- **Implement** *ducking* — temporarily lower the music bus by ~12 dB whenever a dialogue line is playing, then restore the level when the line ends. Trigger is event-driven, not polled.
- **Implement** distance attenuation: a 2D SFX at world position `(sx, sy)` is played at a volume scaled by the inverse of its distance to the listener (capped at min and max distances). The same code in Godot is `AudioStreamPlayer2D` plus `max_distance` and `attenuation`.
- **Compare** OGG Vorbis and WAV on size, decode cost, and loop fidelity. Pick OGG for music and WAV for short SFX; know the one edge case where the reverse is correct.
- **Author** a seamless music loop in Audacity (free): identify a zero-crossing pair, trim to a whole-beat boundary, cross-fade the loop seam if needed, and export as 44.1 kHz / 16-bit stereo OGG. Test in Pygame with `pygame.mixer.music.play(-1)`.
- **Source** assets from Freesound and OpenGameArt under CC0 / CC-BY licences, track attribution in a `CREDITS.md`, and recognise the licence mismatches that make a clip un-shippable.
- **Frame-budget** the audio mix — a stereo 44.1 kHz mix with eight SFX channels and one music stream costs ~0.4 ms per frame on a modern laptop and is sound-card-blocked, not CPU-bound.

## Prerequisites

This week assumes you have completed **Weeks 1-7**. Specifically:

- You have a Week-7 save system. The settings panel this week persists per-bus volume using the same atomic-write pattern.
- You are comfortable with Pygame's event loop and FSM-style state from Week 5.
- You know what a *decibel* is at the level of "a 6 dB drop is half the loudness in linear terms." (If not, skim the *dB Glossary* link in `resources.md`; one paragraph is enough.)
- You can install one third-party package with `pip install pygame` inside a virtual environment.
- You have a working pair of headphones. Laptop speakers will mask the bugs this week is supposed to teach you to hear.

If any of those are shaky, do the previous week's mini-project before continuing.

## Topics covered

Lecture 1 — Audio engine fundamentals and `pygame.mixer`:

- The three numbers: sample rate, channel count, bit depth. Why 44100 / 2 / 16 is the default and what each parameter costs if you change it.
- The mixer's *internal pipeline*: samples come in from each `Sound` object, are scaled by per-sound volume, summed per-frame, clipped to the output range, and written to the sound-card buffer.
- `pygame.mixer.pre_init` — the one function you call *before* `pygame.init()` to set sample rate, channels, and buffer size.
- `pygame.mixer.Sound` (decoded entirely into RAM, cheap to play, paid for at load) vs `pygame.mixer.music` (streamed from disk, expensive to seek, the only sensible option for a 3-minute track).
- `pygame.mixer.Channel` objects: eight by default; `Sound.play(loops, maxtime, fade_ms)` returns one; explicit channels let you stop, queue, fade out, and route.
- Why every short SFX is a `Sound` and every long track is `music`. The size threshold is roughly 1 MB of decoded audio per channel — above that, stream.

Lecture 2 — Mixing, buses, and dynamic music:

- The *bus* abstraction: a tree of named groups, each with a volume, whose output flows up to the master. Every SFX is on some bus; the bus volume scales every member sound.
- A minimal three-bus design: master, music, sfx. Optional fourth bus: voice / dialogue, separate from sfx so ducking can target it.
- Implementing buses in Pygame from scratch: a `Bus` class with a name, a volume, a parent, and a list of attached `Sound`s. Every `play()` is wrapped in a function that computes the *effective volume* by walking up the parent chain.
- *Ducking*: the technique where a high-priority bus (dialogue) automatically lowers a lower-priority bus (music) while the high-priority bus is playing. Implementation: an event fires on dialogue start that fades music down to ~30%; another event on dialogue end fades it back. The fade is the discipline; an abrupt cut sounds amateur.
- *Layered music*: two or more stems play in *exact* sync; crossfades between layers achieve "the music intensifies when combat starts." Pygame ships two playback paths (`music` and `Sound`); the layered-music exercise uses two `Sound` channels with synchronised `play()` calls.
- *Spatial attenuation*: in 2D, distance from the listener controls volume on a linear or inverse curve, capped at a min and max range. Optional stereo panning by horizontal offset. Godot's `AudioStreamPlayer2D` does this for free; in Pygame you compute the multiplier and apply it via `channel.set_volume(left, right)`.
- The "master volume" trap: if your settings menu only exposes master volume, the player cannot mute the music while keeping SFX. Ship at least three sliders.

Lecture 3 — Authoring loops, picking formats, and the Godot bridge:

- The *looping point problem*: a track that loops cleanly in DAW preview almost never loops cleanly in-engine, because game engines do not respect the DAW's loop region. The loop is *bit-perfect concatenation* of end-to-start; any DC offset, fade, or trailing silence becomes a click.
- The *zero-crossing* discipline: cut at a sample where the waveform crosses zero in both stems. Audacity's `Z` shortcut snaps the cursor to the nearest zero-crossing.
- The *beat boundary* discipline: the loop length is a whole number of beats at the track's BPM. A 120 BPM track at 44100 Hz has one beat every 22050 samples — round to the nearest one.
- The *cross-fade-the-seam* technique for tracks whose end and start cannot be matched: render a 50-100 ms cross-fade where the tail of the track overlaps the head of the next loop iteration. Audacity does this in three menu clicks.
- OGG Vorbis vs WAV vs MP3: OGG is patent-free, ~5-10x smaller than WAV, decoded with `pygame.mixer.music` natively. WAV is uncompressed, the safe choice for short SFX. MP3 has a non-zero priming delay that breaks loops — avoid for music.
- File-size budget for a typical small game: ~10 MB total audio. A 3-minute OGG music track is ~3 MB; a 200 ms WAV SFX is ~40 KB. You have room for ~10 music tracks and ~50 SFX before audio is a notable fraction of the install.
- The Godot 4.x bridge: `AudioServer.set_bus_volume_db(idx, db)` is `bus.volume = ...`. `AudioStreamPlayer2D` is the spatial-SFX class. `AudioEffectChorus`, `AudioEffectReverb`, and friends are inserted as nodes on a bus; Pygame has no built-in equivalent and you would script them manually. Most of this week's discipline ports verbatim.

## Weekly schedule

The schedule below adds up to approximately **33 hours**. Treat it as a target. Audio is deceptively quick to play a single clip and deceptively slow to mix five clips into something a player would describe as "good."

| Day       | Focus                                          | Lectures | Exercises | Challenges | Quiz/Read | Homework | Mini-Project | Self-Study | Daily Total |
|-----------|------------------------------------------------|---------:|----------:|-----------:|----------:|---------:|-------------:|-----------:|------------:|
| Monday    | Lecture 1 + mixer init + first `Sound.play`    |    2h    |    1.5h   |     0h     |    0.5h   |   1h     |     0h       |    0.5h    |     5.5h    |
| Tuesday   | Lecture 2 + three-bus mixer exercise           |    2h    |    1.5h   |     0h     |    0.5h   |   1h     |     0.5h     |    0h      |     5.5h    |
| Wednesday | Lecture 3 + Audacity loop authoring            |    2h    |    1.5h   |     0.5h   |    0.5h   |   1h     |     1h       |    0h      |     6.5h    |
| Thursday  | Spatial attenuation + ducking exercise         |    0h    |    1.5h   |     1h     |    0.5h   |   1h     |     1.5h     |    0h      |     5.5h    |
| Friday    | Wire mixer + music + ducking into a tiny game  |    0h    |    0h     |     0.5h   |    0.5h   |   1h     |     2h       |    0.5h    |     4.5h    |
| Saturday  | Asset sourcing, attribution, settings UI       |    0h    |    0h     |     0h     |    0.5h   |   0.5h   |     2.5h     |    0h      |     3.5h    |
| Sunday    | Polish, README, demo capture, push             |    0h    |    0h     |     0h     |    0.5h   |   0h     |     1.5h     |    0h      |     2h      |
| **Total** |                                                | **6h**   | **6h**    | **2h**     | **3.5h**  | **5.5h** | **9h**       | **1h**     | **33h**     |

## How to navigate this week

| File | What is inside |
|------|----------------|
| [README.md](./README.md) | This overview (you are here) |
| [resources.md](./resources.md) | Pygame mixer docs, Godot AudioServer docs, Freesound, OpenGameArt, Audacity manual, dB primer |
| [lecture-notes/01-audio-engine-fundamentals-and-pygame-mixer.md](./lecture-notes/01-audio-engine-fundamentals-and-pygame-mixer.md) | Sample rate, channels, bit depth; the mixer pipeline; `pre_init`; `Sound` vs `music`; channels |
| [lecture-notes/02-mixing-buses-and-dynamic-music.md](./lecture-notes/02-mixing-buses-and-dynamic-music.md) | The three-bus design; ducking; layered music; spatial attenuation; the master-volume trap |
| [lecture-notes/03-authoring-loops-formats-and-the-godot-bridge.md](./lecture-notes/03-authoring-loops-formats-and-the-godot-bridge.md) | The loop-point problem; zero-crossings; cross-fade authoring; OGG vs WAV vs MP3; Godot AudioServer |
| [exercises/exercise-01-mixer-init-and-sfx.py](./exercises/exercise-01-mixer-init-and-sfx.py) | Initialise the mixer correctly and play eight SFX on demand. Generate test tones in code |
| [exercises/exercise-02-three-bus-mixer-with-ducking.py](./exercises/exercise-02-three-bus-mixer-with-ducking.py) | A `Bus` class, three buses (master / music / sfx / voice), and a duck event that fades music when voice plays |
| [exercises/exercise-03-spatial-attenuation-and-panning.py](./exercises/exercise-03-spatial-attenuation-and-panning.py) | A listener and three SFX emitters in 2D space; distance attenuation and left-right panning |
| [exercises/exercise-04-layered-music-crossfade.py](./exercises/exercise-04-layered-music-crossfade.py) | Two stems playing in sync; a Tab key crossfades between explore and combat layers |
| [exercises/SOLUTIONS.md](./exercises/SOLUTIONS.md) | Solution discussion and the "common bugs" list for each exercise |
| [challenges/challenge-01-author-a-seamless-loop-in-audacity.md](./challenges/challenge-01-author-a-seamless-loop-in-audacity.md) | A hands-on Audacity walkthrough: take a free 30-second loop and make it seamless |
| [challenges/challenge-02-design-a-mixer-for-a-fighting-game.md](./challenges/challenge-02-design-a-mixer-for-a-fighting-game.md) | A paper-design exercise: bus tree, ducking rules, and category budgets for a six-bus fighting-game mixer |
| [quiz.md](./quiz.md) | Ten multiple-choice questions |
| [homework.md](./homework.md) | Six practice problems for the week |
| [mini-project/README.md](./mini-project/README.md) | A tiny arcade game with three buses, ducked dialogue, layered combat music, spatial SFX, and a persistent settings panel |
| [mini-project/starter_main.py](./mini-project/starter_main.py) | Scaffold for the mini-project: a window, a player, and a stubbed audio module to fill in |
| [mini-project/starter_audio.py](./mini-project/starter_audio.py) | The audio module stub — `init_audio`, the `Bus` tree, and the volume helpers, ready for you to wire |

## Frame budget for this week

A reminder of what 60 fps means in milliseconds. The audio mixer runs every frame, but it is *not* CPU-bound — the sound card pulls samples on its own clock, and your Python code only feeds the queue.

```
┌─────────────────────────────────────────────────────────┐
│  FRAME BUDGET — 60 fps target, with three-bus audio     │
│                                                         │
│  Input poll:       ~0.2 ms                              │
│  FSM dispatch:     ~0.1 ms                              │
│  Update (sim):     ~1.4 ms                              │
│  Animation tick:   ~0.3 ms                              │
│  Particles:        ~0.6 ms                              │
│  Render (entity):  ~1.5 ms                              │
│  HUD draw:         ~0.4 ms                              │
│  Audio dispatch:   ~0.4 ms  (Sound.play, bus volumes)   │
│  Save system:      ~0.0 ms                              │
│  GPU + present:    ~4.0 ms                              │
│  Headroom:         ~7.7 ms                              │
│  ─────────────────────                                  │
│  Total:           ~16.6 ms / frame                      │
└─────────────────────────────────────────────────────────┘
```

The 0.4 ms "Audio dispatch" budget covers our per-frame work: checking the duck state, advancing crossfades, recomputing the listener-to-emitter distance for spatial SFX, and (rarely) calling `Sound.play`. The actual mixing happens on the sound card's clock outside of Python entirely. If you ever see audio dispatch exceed 1 ms on a profiler, you are probably loading a `Sound` from disk inside the game loop. Load all sounds at startup; reference them by handle thereafter.

## Stretch goals

If you finish early and want to push further:

- **Read every page of the *pygame.mixer* documentation** end-to-end. It is shorter than you expect (~30 minutes) and you will learn about three methods — `Channel.queue`, `Sound.set_volume(left, right)`, and `pygame.mixer.fadeout` — that solve real problems we do not have time to demo in lecture.
- **Implement a fourth bus for UI sounds** (menu hover, button click, modal open) and route the Kenney `interface-sounds` pack through it. UI sounds typically sit on a separate bus so they remain audible even when SFX and music are muted (the player must still hear the menu).
- **Build a "test tone" debug mode**. Press F12 to sweep a 1 kHz sine through left → centre → right at full volume; press F11 for pink noise. This is how every audio engineer sanity-checks a new mix.
- **Watch Marshall McGee's *Sound Design for Games* talks on YouTube** (free, ~30 min each). McGee's series on *Hades* and *Subnautica* are studies in mixing discipline at production scale.
- **Read Godot's *Audio buses* tutorial** in full (linked in `resources.md`). Build the same three-bus tree in the Godot editor as a *visual* reference even if you do not yet know GDScript. You will land in Week 9 with the audio mental model already in place.
- **Wire a sidechain compressor into Audacity** and use it on a music stem to manually duck under a dialogue clip. Compare your authored-in-Audacity result to your engine-driven duck. The engine-driven version wins on flexibility; the authored version wins on quality.
- **Use a free spectrogram view in Audacity** to verify that your music's seamless loop has no visible discontinuity at the seam. The spectrogram makes invisible audio defects visible.

## Voice rules for the week

- We define **mixing** as "deciding the relative volume of every sound that plays at the same time." It is not mastering. It is not sound design. The whole job is *the relative levels*, and the whole job has to be done.
- We credit **Pygame's `pygame.mixer` module documentation** as the canonical free reference for everything in this week's exercises. We link the exact URL once and refer to "the mixer docs" thereafter.
- We credit **Godot's *AudioServer* and *Audio buses* documentation** as the bridge to Week 9. We do not write Godot code this week; we read its docs so the API looks familiar when we arrive.
- We credit **Freesound** and **OpenGameArt** as the two free, CC-licensed sources for every clip we use. Every clip used in any exercise or the mini-project must have a credit line in `CREDITS.md`. CC-BY clips require the credit line; CC0 clips do not, but we write one anyway.
- We credit the **Audacity team** for shipping a free, open-source audio editor that handles every loop-authoring task in this week. The Audacity manual link is in `resources.md`.
- We **prefer OGG Vorbis for music** and **WAV for short SFX**. We avoid MP3 for any clip that needs to loop seamlessly. The reasoning is in Lecture 3 §3; do not relitigate it.
- We **never** load a `Sound` inside a game loop. Load once at startup; play many times. The load cost is ~5 ms; the play cost is microseconds.
- We **respect the player's ears**. A player who turns down the music slider expects the music to actually get quieter. A player who mutes a bus expects silence on that bus, not a "quieter version." Sliders and mutes are contracts, and breaking them is the kind of mid-tier indie failure this course exists to prevent.

## Up next

Continue to [Week 9 — Transitioning to Godot 4.x](../week-09/) once you have pushed your audio mini-project. Week 9 takes everything from Weeks 1-8 and re-implements the key pieces in Godot. The mixer-bus discipline you wrote this week becomes one editor screen plus three lines of GDScript; the *thinking* is the artefact and ports cleanly.

---

*If you find errors in this material, please open an issue or send a PR. Future learners will thank you.*
