# Lecture 3 — Authoring Loops, Formats, and the Godot Bridge

> **Duration:** ~2 hours of reading plus hands-on Audacity work.
> **Outcome:** You can author a seamless music loop in Audacity, pick the right file format per clip with reasoning, and read Godot 4.x's `AudioServer` documentation as the bridge to Week 9.

If you only remember one thing from this lecture, remember this:

> **A clip loops cleanly in your DAW preview only because the DAW respects the loop region. A game engine does not. The engine concatenates the end of the file to the start of the next loop iteration, bit-perfectly. Any DC offset, trailing silence, or non-matching waveform at the seam becomes an audible click. The fix is to cut at zero-crossings and (when needed) cross-fade the seam. Five minutes in Audacity, every loop in your game.**

This lecture has two halves. The first is content authoring: how to make a loop that does not click, which file format to pick for which clip, and what licence reading discipline keeps your asset list shippable. The second is the Godot 4.x bridge: what every Pygame technique from Lectures 1 and 2 looks like in Godot's `AudioServer` model. By the end you can save a game-ready OGG, justify the choice over WAV and MP3, and skim the Godot AudioServer docs without getting lost in the API.

---

## 1. The looping point problem

A music track is a sequence of audio samples — say, 44100 stereo samples per second over 30 seconds = 1,323,000 samples. A *seamless loop* means: when sample 1,322,999 plays and the next sample is sample 0 (the start of the file restarts), the listener cannot hear the seam.

In a DAW preview, the loop region is *inside* the editor, and the editor cross-fades or otherwise smooths the seam. In a game engine — Pygame's `pygame.mixer.music.play(-1)` and Godot's `AudioStreamPlayer.stream.loop = true` — the seam is *bit-perfect concatenation*. The end of the file meets the start of the file with no smoothing, no fade, no help.

Three things can go wrong at the seam:

1. **Waveform discontinuity.** The last sample's amplitude is +5000; the first sample's amplitude is -3000. The instantaneous jump from +5000 to -3000 is a transient with high-frequency energy — a *click*.
2. **DC offset.** The whole file is shifted off the zero-line (the average sample value is not zero, but say +200). Every loop, the seam plays the DC step *and* the start-of-file transient. The DC offset usually comes from an asymmetric recording or a microphone with a non-zero bias.
3. **Trailing silence or fade.** The file has 100 ms of silence at the end (intended for fade-out in a standalone listening context). Every loop iteration plays this silence, breaking the musical rhythm.

The fixes are all editorial:

- **Cut at zero-crossings.** Find a sample where the waveform crosses zero, and cut both end and start to land on a zero-crossing. Audacity's `Z` shortcut snaps the cursor to the nearest zero-crossing.
- **Cut to a beat boundary.** If the track is 120 BPM, a beat is 60/120 = 0.5 seconds = 22050 samples at 44.1 kHz. The loop length should be a whole number of beats. Round to the nearest beat.
- **Cross-fade the seam.** If the end and start cannot be matched (e.g., the track has a unique outro), render a 50-100 ms cross-fade where the tail of the file overlaps the head. Audacity's `Effect → Cross Fade Tracks` does this in three menu clicks.
- **Remove DC offset.** Audacity's `Effect → Normalize` with "Remove DC offset" checked. One menu click.

---

## 2. Step-by-step in Audacity

The Audacity workflow for a 30-second loop:

**Step 1 — Open the source.** `File → Open`. Pick the OGG, WAV, or MP3 source (Audacity supports all three for read).

**Step 2 — Identify the loop region.** Listen to the whole file. Find the moment where the music "comes back to the beginning" — usually the end of a 4-bar or 8-bar phrase. Click that moment to place the cursor.

**Step 3 — Snap to a zero-crossing.** Press `Z`. The cursor moves to the nearest zero-crossing. Audacity shows the exact sample number in the bottom-left status bar.

**Step 4 — Trim before this point.** Select from the cursor to the end of the file (`Shift+End`). Delete (`Delete` or `Edit → Delete`).

**Step 5 — Snap the start to a zero-crossing.** Click at sample 0. Press `Z`. If sample 0 is already a zero-crossing, nothing moves. Otherwise the cursor snaps to the nearest zero-crossing, and you trim everything before it.

**Step 6 — Remove DC offset.** `Effect → Normalize`. Check "Remove DC offset." Set "Normalize peak amplitude to: -1.0 dB." Click OK.

**Step 7 — Test the loop in Audacity.** Place the cursor at the end of the file, press `Shift+J` to select from cursor to end (about 100 ms), and Audacity will preview the loop seam by playing the tail and wrapping to the start. Listen with headphones. If you hear a click, return to step 3 with a different cut point.

**Step 8 — (Optional) Cross-fade the seam.** If the cut point is fundamentally not loop-friendly (e.g., a sustained note at the end and silence at the start), render a 50 ms cross-fade. `Effect → Cross Fade Tracks` after duplicating the track and aligning copies.

**Step 9 — Export as OGG.** `File → Export → Export as OGG`. Quality 5 (~128 kbps) is fine for game music; quality 7 (~192 kbps) for music-heavy games; quality 3 (~96 kbps) for atmospheric loops. Filename matches the in-game asset key (`combat-layer.ogg`, `explore-layer.ogg`).

**Step 10 — Test in Pygame.** Load with `pygame.mixer.music.load(...)`, play with `pygame.mixer.music.play(-1)`. Listen for 30 seconds spanning the loop seam. Confirm no click.

This is the whole authoring loop. It takes ~5-10 minutes per track once you have done it twice. Challenge 1 walks you through it end-to-end on a free OpenGameArt track.

---

## 3. OGG vs WAV vs MP3

The three formats Pygame's audio stack accepts have different costs and use cases.

### 3.1 WAV (Waveform Audio File Format)

- **Compression:** none. Uncompressed PCM samples on disk.
- **File size:** 10.6 MB/minute at 44.1 kHz / 16-bit stereo.
- **Decode cost:** zero. The file is already samples.
- **Loop fidelity:** perfect. The samples on disk are the samples played; no codec artefact at the seam.
- **Use case:** short SFX (≤ 2 s). The size cost is negligible at short durations (a 250 ms SFX is ~44 KB).

WAV is the safe default for short clips. The zero-decode-cost means a `Sound("hit.wav").play()` call has no surprise CPU spike. The loop fidelity matters less for short SFX (which usually do not loop), but the *absence* of codec artefacts is one less thing to debug.

### 3.2 OGG Vorbis

- **Compression:** lossy, patent-free, ~5-10x smaller than WAV.
- **File size:** ~1 MB/minute at quality 5.
- **Decode cost:** moderate (~1-2 ms per minute of audio during the streaming pull).
- **Loop fidelity:** good when authored correctly. The Vorbis codec adds a small priming delay (~50 ms of decoder warm-up) — `pygame.mixer.music` handles this transparently for loops.
- **Use case:** all music. Authored loops play seamlessly when the file is cut on zero-crossings.

OGG is the default for any clip longer than ~5 seconds, and especially any clip that loops. The size reduction is meaningful — a 3-minute song is ~30 MB as WAV and ~3 MB as OGG. The decode cost is paid asynchronously by the streaming subsystem and never blocks the game loop.

### 3.3 MP3

- **Compression:** lossy, patent-encumbered (mostly expired by 2017, but still legally complicated in some jurisdictions), ~5-10x smaller than WAV.
- **File size:** ~1 MB/minute at 128 kbps.
- **Decode cost:** moderate.
- **Loop fidelity:** *bad*. MP3 has a non-zero *priming delay* (samples added at the start of the file as decoder warm-up) and a non-zero *end-of-file padding* (samples added at the end). Every loop iteration replays both. The seam *cannot* be sample-accurate.
- **Use case:** background music *that does not loop*. Avoid for loops entirely.

The loop-fidelity issue is the killer. A track that loops cleanly as OGG will click at the seam as MP3. The fix is "use OGG." We do not relitigate this.

### 3.4 The format decision table

| Clip length | Use case | Format | Reasoning |
|-------------|----------|--------|-----------|
| < 2 s | SFX (one-shot) | WAV | Tiny on disk, zero decode cost |
| < 2 s | SFX (looping ambient) | WAV | Loops sample-accurate |
| 2-30 s | Dialogue (one-shot) | OGG | Decode cost paid once per line |
| 2-30 s | Sting / jingle | OGG | Size matters as count grows |
| > 30 s | Music (looping) | OGG | Streamable + loop-clean if authored |
| > 30 s | Music (one-shot) | OGG | Same as looping; do not bother with MP3 |
| Any | Anything that needs to loop | NOT MP3 | Priming delay breaks the seam |

The rule of thumb: **OGG for music, WAV for SFX, MP3 for nothing.** This is the only formatting rule the mini-project enforces.

---

## 4. Licence reading: CC0, CC-BY, CC-BY-SA, CC-BY-NC

Free assets come with licences. The licence determines what you can do with the asset and what you owe the creator. Mis-reading a licence is the second-most-common asset-pipeline failure (the first is "forgot to credit").

### 4.1 CC0 — public domain dedication

- **You can:** do anything. Use commercially, modify, redistribute. No credit required.
- **You should:** credit anyway. It is the right thing to do.
- **Where you find it:** Kenney's audio packs are CC0. Many Freesound clips are CC0 (filter on "Creative Commons 0").

CC0 is the safest licence. If you only used CC0 assets, your `CREDITS.md` is optional — but you still write one.

### 4.2 CC-BY — attribution required

- **You can:** use commercially, modify, redistribute.
- **You must:** include a credit line with the creator's name, the asset name, the URL, and the licence name. Standard attribution string:

```
"Forest Ambient Loop" by JohnDoe (https://freesound.org/people/JohnDoe/sounds/12345/)
licensed under CC-BY 3.0 (https://creativecommons.org/licenses/by/3.0/).
```

- **Where you find it:** majority of Freesound clips, much of OpenGameArt, Kevin MacLeod's Incompetech music.

CC-BY is shippable. The credit goes in `CREDITS.md`, with a copy in the game's about screen if you have one. Failing to credit is a licence violation; nobody will sue an indie, but the asset community is small and reputations carry.

### 4.3 CC-BY-SA — attribution + share-alike

- **You can:** use, modify, redistribute.
- **You must:** credit (as CC-BY) *and* license your derivative work under CC-BY-SA.

The share-alike requirement is *incompatible with most commercial game licences*. If you ship a CC-BY-SA asset in a commercial game, your game must also be CC-BY-SA, which means the *whole game's source* must be released. For a portfolio project this is fine; for a commercial release this is a no-go.

The discipline: avoid CC-BY-SA for commercial-track assets. Use CC-BY or CC0 instead.

### 4.4 CC-BY-NC — non-commercial

- **You can:** use for personal, educational, non-commercial purposes only.
- **You cannot:** ship in a commercial game.

The NC variant is also a no-go for commercial games. The fact that your portfolio project is non-commercial does *not* matter — Steam pages count as commercial display, and the asset cannot live there. Avoid CC-BY-NC.

### 4.5 The licence audit

Every time you add an asset to the project, paste these four lines into your asset spreadsheet:

```
Filename:    explore-layer.ogg
Source:      https://opengameart.org/content/calm-loop-ambient-60bpm
Creator:     JaneDoe
Licence:     CC-BY 3.0
Credit:      "Calm Loop Ambient" by JaneDoe, https://opengameart.org/content/...,
             licensed under CC-BY 3.0 (https://creativecommons.org/licenses/by/3.0/).
```

Five minutes per asset. Compounds over the course of a project into a one-screen `CREDITS.md` that is correct.

---

## 5. The Godot 4.x AudioServer bridge

Week 9 moves to Godot. Most of this week's Pygame discipline ports directly. The differences are vocabulary, not concept.

### 5.1 The mapping

| This week's Pygame concept | Godot 4.x equivalent |
|----------------------------|----------------------|
| `pygame.mixer.pre_init(...)` | Project settings → Audio → Driver. Default is fine. |
| `pygame.mixer.Sound` | `AudioStreamWAV`, `AudioStreamOggVorbis` resource |
| `pygame.mixer.music` | Same — load an `AudioStreamOggVorbis` into an `AudioStreamPlayer` |
| `pygame.mixer.Channel` | Implicit. Godot allocates a player per `AudioStreamPlayer` node. |
| Our `Bus` class | `AudioServer.bus_count`, `AudioServer.add_bus(idx)`, `set_bus_volume_db(idx, db)` |
| Our `AudioMixer.master` | The Master bus (index 0, always present) |
| Our `play_sfx` | `node.bus = "SFX"; node.play()` |
| Our duck | `AudioEffectCompressor` on the music bus with sidechain |
| Our spatial attenuation | `AudioStreamPlayer2D` with `max_distance` + `attenuation` |
| Our stereo pan | `AudioStreamPlayer2D` does this automatically from listener |
| Our `apply_settings` | Iterate `AudioServer.bus_count`, call `set_bus_volume_db` |

### 5.2 The big differences

**Difference A — `volume_db` not `volume`.** Godot's API takes volume in decibels (`set_bus_volume_db`), where 0 dB is unity (no change), negative is quieter, and -80 dB is "essentially silent." Our Pygame work uses linear `[0.0, 1.0]`. The conversion is `db = 20 * log10(linear)`. A linear 0.5 is -6 dB; a linear 0.1 is -20 dB.

**Difference B — Buses are configured in the editor, not in code.** In Godot you open the Audio bus panel, click "Add Bus," type a name, set its parent in the dropdown. The same three-bus tree we built in 50 lines of Python is three clicks per bus in Godot. The `AudioServer` API in code lets you *change* volumes at runtime; the editor configures the topology.

**Difference C — `AudioStreamPlayer2D` does spatial automatically.** Our `play_spatial_sfx` function disappears. You attach an `AudioStreamPlayer2D` to a game object, set its `max_distance`, `attenuation`, and `panning_strength`, and Godot computes the volume and pan based on the position of the active `AudioListener2D` (or the `Camera2D` if no listener is set). Our 30 lines of distance math reduce to one node and three editor properties.

**Difference D — Effects are nodes on buses.** Reverb, chorus, EQ, compressor, limiter — all are `AudioEffect*` resources added to a bus in the editor. Sidechain ducking is `AudioEffectCompressor` with the sidechain bus property set to "Voice." This replaces our hand-written `update_duck` function entirely. We will use this in Week 9.

**Difference E — Music looping is a property of the stream.** Our `pygame.mixer.music.play(-1)` becomes `stream.loop = true` on the `AudioStreamOggVorbis` resource, set once at import. The engine handles the loop.

### 5.3 What ports unchanged

- The **mental model** of buses as a tree of named multipliers.
- The **decision rule** for OGG vs WAV (Godot supports both; the trade-offs are identical).
- The **loop-authoring discipline** in Audacity. Audacity is upstream of any engine.
- The **licence audit** of CC-BY / CC0 assets in `CREDITS.md`.
- The **mixing reference table** of typical per-clip volumes by category.

The week's work is *transferable* in the strongest sense. You will spend a few hours in Week 9 learning Godot's editor UI for audio; the underlying knowledge is already in place.

---

## 6. The audio-asset budget for a small game

A practical reference for how much audio a small game should ship. These are *typical* numbers for a C11 mini-project or short Crunch Arcade title.

| Category | Count | Format | Size per | Subtotal |
|----------|-------|--------|----------|----------|
| Music (background) | 4-6 tracks | OGG q5 | ~3 MB / 3 min | ~15 MB |
| Music (combat layer) | 1-2 tracks | OGG q5 | ~3 MB / 3 min | ~5 MB |
| Music (stings, intros) | 4-6 short | OGG q3 | ~200 KB / 10 s | ~1 MB |
| SFX (one-shot) | 30-60 | WAV | ~40 KB / 250 ms | ~2 MB |
| SFX (ambient loops) | 4-8 | WAV | ~250 KB / 2 s | ~2 MB |
| Dialogue | 30-100 lines | OGG q5 | ~80 KB / 5 s | ~5 MB |
| UI sounds | 5-10 | WAV | ~20 KB / 100 ms | ~0.2 MB |
| **Total** | | | | **~30 MB** |

For comparison: a 1080p PNG screenshot is ~3 MB. A short Twitter video is ~30 MB. The whole audio of a small indie game is one screenshot's worth of network bandwidth. Audio is *cheap* — never compress an asset to the point of audible degradation to save bytes.

---

## 7. A worked loop-authoring session

Concrete walkthrough for the mini-project's explore-layer track.

**Source.** Download `60bpm-ambient-loop.ogg` from OpenGameArt (CC-BY 3.0). 90 seconds, 60 BPM.

**Goal.** Trim to exactly 32 bars (= 32 beats / 60 bpm × 60 s/min ÷ 60 bpm? let us recompute: 32 bars at 4 beats per bar at 60 bpm = 128 beats = 128 seconds. Too long. Let us aim for 16 bars = 64 seconds, or 8 bars = 32 seconds. Pick 8 bars.) Trim to 32 seconds.

**Step 1.** `File → Open → 60bpm-ambient-loop.ogg`.

**Step 2.** Audacity shows a stereo waveform. Look at the BPM in the file (often in the metadata; if not, use Audacity's *Effect → Beat Finder* on a chunk).

**Step 3.** Place the cursor at the 32-second mark. Press `Z` to snap to zero-crossing. Audacity reports the exact sample number, e.g., 1,411,200.

**Step 4.** `Select → Region → Cursor to End`. Then `Edit → Delete`.

**Step 5.** Place the cursor at sample 0. Press `Z`. If the file does not start at a zero-crossing, trim the leading samples.

**Step 6.** `Effect → Normalize` with "Remove DC offset" checked and "Normalize peak amplitude" to -1.0 dB.

**Step 7.** Preview the loop. `Transport → Loop Play On/Off`. Audacity will loop the entire selection, but the seam is now bit-perfect concatenation. Listen for 30 seconds. If you hear a click, the cut point was not on a zero-crossing — return to step 3.

**Step 8.** `File → Export → Export as OGG`. Quality 5. Filename `explore-layer.ogg`. Project asset path `assets/audio/explore-layer.ogg`.

**Step 9.** In Pygame: `pygame.mixer.music.load("assets/audio/explore-layer.ogg")` then `pygame.mixer.music.play(-1)`. Listen for 60 seconds. Confirm two passes through the loop are seamless.

**Step 10.** Add the credit to `CREDITS.md`:

```
"60bpm Ambient Loop" by JaneDoe (https://opengameart.org/content/60bpm-ambient-loop)
licensed under CC-BY 3.0 (https://creativecommons.org/licenses/by/3.0/).
Edited in Audacity for the C11 mini-project (trimmed to 32 s, DC removed, normalised).
```

The credit names the edit. Some CC-BY licences require disclosing modifications; this practice satisfies the requirement and is unambiguous.

---

## 8. The "loop click" diagnostic flowchart

When you hear a click at the loop seam, walk this tree:

```
Click at the seam?
│
├─ Is the click a single short pop (< 5 ms)?
│   │
│   ├─ YES → Cut point is not at a zero-crossing.
│   │        Re-cut with Z-snap.
│   │
│   └─ NO  → Continue.
│
├─ Is there audible silence around the seam (>= 50 ms)?
│   │
│   ├─ YES → Trailing silence in the file.
│   │        Trim with selection-and-delete; re-export.
│   │
│   └─ NO  → Continue.
│
├─ Does the click happen on every loop iteration at the same place?
│   │
│   ├─ YES → DC offset.
│   │        Effect → Normalize with "Remove DC offset" checked.
│   │
│   └─ NO  → Continue.
│
├─ Is the file MP3?
│   │
│   ├─ YES → MP3 priming delay. Convert to OGG.
│   │
│   └─ NO  → Continue.
│
└─ Cross-fade the seam.
    Effect → Cross Fade Tracks with a 50-100 ms overlap.
```

Four diagnostics, four fixes. Most loop-click problems are one of the first two; the rest are rare.

---

## 9. What we built across all three lectures

A full audio stack:

- **Lecture 1.** Mixer initialisation, `Sound` vs `music`, channels, `endevent` wiring.
- **Lecture 2.** Three-bus mixer, ducking, layered music, spatial attenuation.
- **Lecture 3.** Loop authoring, format selection, licence audit, Godot bridge.

This is the same feature set every shipping indie game uses. The Pygame implementation is ~250 lines; the Godot implementation is ~50 lines plus editor configuration. The mini-project assembles every piece into a tiny arcade game that runs at 60 fps with three buses, ducked dialogue, layered combat music, spatial SFX, and a settings panel that writes to a JSON file using last week's atomic-write pipeline.

By Sunday you have it. The next week — Godot — rewrites the engine layer; the *audio thinking* you do this week carries forward unchanged.

---

## References

- **Audacity manual — Edit menu (zero-crossings).** The Z-shortcut, the cut/copy/paste tools. <https://manual.audacityteam.org/man/edit_menu.html>
- **Audacity manual — Effect menu (cross-fade).** Cross Fade Tracks for the seam. <https://manual.audacityteam.org/man/effect_menu.html>
- **Audacity manual — Exporting audio.** Export-as-OGG quality settings. <https://manual.audacityteam.org/man/exporting_audio_files.html>
- **Wikipedia — *Vorbis*.** The OGG Vorbis codec spec at a high level. <https://en.wikipedia.org/wiki/Vorbis>
- **Godot — *AudioServer* class reference.** Buses, effects, runtime API. <https://docs.godotengine.org/en/stable/classes/class_audioserver.html>
- **Godot — *Audio buses* tutorial.** The editor-driven bus tree. <https://docs.godotengine.org/en/stable/tutorials/audio/audio_buses.html>
- **Godot — *AudioStreamPlayer2D*.** Spatial SFX as one node. <https://docs.godotengine.org/en/stable/classes/class_audiostreamplayer2d.html>
- **Freesound.** Community SFX library, CC0 and CC-BY filters. <https://freesound.org/>
- **OpenGameArt.** Community game-asset library. <https://opengameart.org/>

---

*This concludes Week 8's lecture series. Proceed to the exercises.*
