# Week 8 — Quiz

Ten multiple-choice questions. Take it with your lecture notes closed. Aim for 9/10 before moving to Week 9. Answer key at the bottom — do not peek.

---

**Q1.** Lecture 1 §3 names the *one* function you must call before `pygame.init()` to configure the mixer with explicit parameters. That function is:

- A) `pygame.mixer.init(...)`.
- B) `pygame.mixer.pre_init(...)`.
- C) `pygame.mixer.set_format(...)`.
- D) `pygame.mixer.configure(...)`.

---

**Q2.** Lecture 1 §4-5 contrasts `pygame.mixer.Sound` with `pygame.mixer.music`. Which statement is accurate?

- A) `Sound` is for streaming long tracks from disk; `music` is for short clips loaded into RAM.
- B) `Sound` decodes the entire clip into RAM at load; `music` streams from disk and is a singleton (only one music track plays at a time).
- C) `Sound` and `music` are aliases for the same object.
- D) `Sound` is deprecated in Pygame 2.5 and should not be used.

---

**Q3.** Lecture 2 §1 defines a *bus* as:

- A) A named volume multiplier with an optional parent, whose effective volume is the product of the chain from itself to the root.
- B) A FIFO queue of `Sound` objects that play in order.
- C) A subclass of `pygame.mixer.Channel` with additional fields.
- D) A USB hardware device for audio output.

---

**Q4.** Lecture 2 §2 describes *ducking*. The minimal duck implementation lowers the music bus by approximately:

- A) 50 dB during voice playback.
- B) -12 dB (~30% linear) during voice playback, restoring to the previous level when the voice ends.
- C) Zero — ducking does not change the bus volume, only the bus mute flag.
- D) The exact volume the player sets in the settings menu.

---

**Q5.** Lecture 2 §3 implements *layered music* using two `pygame.mixer.Sound` objects on dedicated, reserved channels. The reason both stems are loaded as `Sound` rather than streamed via `pygame.mixer.music` is:

- A) `pygame.mixer.music` is faster for short clips.
- B) `pygame.mixer.music` is a singleton — only one music stream can play at a time. Two layered stems require two playback paths, so both load as `Sound`.
- C) `Sound` objects compress better on disk than `music` files.
- D) `pygame.mixer.music` cannot be looped.

---

**Q6.** Lecture 2 §4 implements 2D spatial attenuation. The exercise's `distance_attenuation` function uses a *linear* curve from `min_distance` to `max_distance`. The reason for linear rather than physically-accurate inverse-square is:

- A) Linear is faster to compute.
- B) Inverse-square sounds wrong for game audio — sounds drop off too quickly, and the listener feels deaf two screens away. Linear with min/max clamping gives the player intuitive control.
- C) Inverse-square is not implementable in Python.
- D) Pygame's `set_volume` only accepts linear values.

---

**Q7.** Lecture 3 §1 names the *looping point problem*. The problem manifests as:

- A) The music file's first sample is brighter than its last sample.
- B) Game engines concatenate the end of the file to its start bit-perfectly, so any waveform discontinuity, DC offset, or trailing silence at the seam becomes an audible click on every loop iteration.
- C) The music file's loop point is encoded in a metadata tag that Pygame ignores.
- D) The music file's BPM changes mid-loop.

---

**Q8.** Lecture 3 §3 picks file formats per clip type. The recommended formats are:

- A) MP3 for everything.
- B) WAV for music, OGG for SFX.
- C) OGG Vorbis for music (streamable + loop-clean if authored), WAV for short SFX (sample-accurate + zero decode cost), never MP3 for anything that needs to loop.
- D) FLAC for everything (lossless).

---

**Q9.** Lecture 3 §4 discusses CC licences. A CC-BY-SA-licensed asset has the *practical* drawback that:

- A) It cannot be edited.
- B) Its "share-alike" clause requires the derivative work (your game) to be licensed under CC-BY-SA, which is incompatible with most commercial game licences. Avoid for commercial-track games.
- C) It requires a non-attribution clause.
- D) It cannot be used outside the European Union.

---

**Q10.** Lecture 3 §5 maps this week's Pygame concepts to Godot 4.x `AudioServer`. The Pygame `play_spatial_sfx` function with manual distance and pan math is replaced in Godot by:

- A) `AudioServer.play_spatial_sfx(...)`.
- B) A node — `AudioStreamPlayer2D` — attached to the game object, with `max_distance` and `attenuation` properties; Godot computes distance and pan from the active `AudioListener2D` or `Camera2D` automatically.
- C) The `AudioEffectReverb` effect on the SFX bus.
- D) `AudioServer.set_listener_position(...)` plus a manual `compute_attenuation(...)` call per frame.

---

## Answer key (do not peek until you have committed answers)

1. **B** — `pygame.mixer.pre_init` before `pygame.init`. The order is non-negotiable; `init` lazily creates a mixer if `pre_init` was not called. Lecture 1 §3.
2. **B** — `Sound` is RAM-resident, `music` is a streaming singleton. The 1 MB rule of thumb: above that, stream. Lecture 1 §4-5.
3. **A** — A bus is a named multiplier with parent. The effective-volume walk is the whole abstraction. Lecture 2 §1.
4. **B** — Duck to ~30% linear (-12 dB) for the duration of the voice, restore on the endevent. Lecture 2 §2.
5. **B** — `pygame.mixer.music` is a singleton. Two stems require two `Sound` objects on dedicated channels. Lecture 2 §3.
6. **B** — Inverse-square is physically correct but sounds wrong in game audio. Linear with clamping is the practical default. Lecture 2 §4.1.
7. **B** — The seam is bit-perfect concatenation; any waveform discontinuity becomes a click. Cut at zero-crossings and (when needed) cross-fade. Lecture 3 §1.
8. **C** — OGG for music, WAV for short SFX, never MP3 for loops. The MP3 priming-delay problem breaks the seam. Lecture 3 §3.
9. **B** — Share-alike forces your derivative work under CC-BY-SA, which most commercial game licences cannot satisfy. Avoid CC-BY-SA for commercial. Lecture 3 §4.3.
10. **B** — `AudioStreamPlayer2D` does spatial automatically. Our 30 lines of distance math reduce to one node and three editor properties. Lecture 3 §5.2.

---

*Score yourself. 9-10 is a pass; 7-8 means re-read the lecture for any question you missed; below 7 means re-read all three lectures before starting the mini-project.*
