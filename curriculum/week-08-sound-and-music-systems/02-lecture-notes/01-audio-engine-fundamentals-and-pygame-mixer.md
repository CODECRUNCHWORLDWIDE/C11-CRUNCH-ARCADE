# Lecture 1 — Audio Engine Fundamentals and `pygame.mixer`

> **Duration:** ~2 hours of reading plus hands-on.
> **Outcome:** You can initialise `pygame.mixer` with explicit parameters, explain what each parameter costs, allocate channels deliberately, and play an SFX from RAM and a music track from disk without confusing the two.

If you only remember one thing from this lecture, remember this:

> **`pygame.mixer.Sound` is RAM-resident audio you can fire-and-forget; `pygame.mixer.music` is a streaming singleton for the one long track that is playing right now. Confuse the two and you either run out of memory on a five-minute song or spend a frame seeking the disk for a footstep. The whole rest of the audio system is built on this one distinction.**

The lecture begins with the three numbers that define every audio engine — sample rate, channel count, bit depth — then explains what each costs if you change it. We then look at the mixer's internal pipeline, the explicit `pre_init` call you must make before `pygame.init()`, the eight default playback channels, and the two playback paths (`Sound` and `music`). By the end you can read the `pygame.mixer` documentation page and recognise every type.

---

## 1. Sound is samples

A computer plays audio by writing a sequence of integers to a sound card. The integers are amplitude values; the sound card converts them to a voltage that drives a speaker cone. That is the whole stack from the OS's point of view.

The integers come from three numbers that the OS, the engine, and the sound card all have to agree on:

- **Sample rate (Hz).** How many integers per second. Consumer audio is 44100 Hz or 48000 Hz. CD audio is 44100; modern OSes natively run at 48000. Above 48000 (96 kHz, 192 kHz) is professional-mastering territory and is wasted on a game.
- **Channels.** 1 (mono), 2 (stereo), or more (5.1, 7.1). For a 2D game, stereo is the right answer; mono throws away half the spatial information; 5.1 is for AAA games with calibrated home-theatre setups.
- **Bit depth.** 8 (CD-error rare; toy quality), 16 (CD quality; the consumer default), 24 (studio mastering), 32-bit float (DAW intermediate format). For a game you ship 16-bit signed; the mixer can compute internally at higher precision.

The Pygame default is **44100 Hz / 2 channels / 16-bit signed**. You will rarely change it. When you do, you change it because:

- You are targeting a constrained platform (a small embedded device) and need to reduce memory or CPU. Drop to 22050 Hz, mono, 8-bit. Your game will sound terrible. The trade is real.
- You are matching a specific asset set authored at 48000 Hz. Match the asset rate; mismatched rates cost a real-time resample and can introduce subtle pitch shifts.
- Everything else: stay at 44100 / 2 / 16. Do not invent reasons to deviate.

### 1.1 Why 44100 Hz?

The Nyquist-Shannon sampling theorem says you can faithfully represent any frequency up to *half* the sample rate. Human hearing tops out around 20 kHz; doubling that and rounding gives 44.1 kHz (the leftover 200 Hz is a margin for the anti-aliasing filter). 22050 Hz can represent up to 11025 Hz — fine for speech, audibly poor for music. 48000 Hz is no perceptual improvement over 44100 for most listeners; it is the chosen rate for video because it divides evenly into common video frame rates.

### 1.2 Why stereo?

A mono mix gives every sound the same apparent direction. A stereo mix lets you pan a footstep to the left when the enemy is on the left, and that single cue makes a 2D game feel inhabitable. The cost of stereo over mono is 2x the bytes on disk and 2x the bytes in RAM; on every modern platform that cost is irrelevant.

### 1.3 Why 16-bit?

A 16-bit signed integer can represent ~96 dB of dynamic range — louder than any consumer playback environment can faithfully reproduce. 8-bit gives ~48 dB and the quiet sounds will be drowned by quantisation noise. 24-bit gives ~144 dB but you cannot hear the difference at consumer-grade listening levels, and the 50% size increase is wasted.

The summary number: **44100 Hz x 2 channels x 16 bits = 176400 bytes/sec, or 10.6 MB/min.** A 3-minute song decoded into RAM is ~32 MB. Compressed as OGG Vorbis at quality 5, the same song fits in ~3 MB on disk and *streams* from disk while playing. This is exactly why music is streamed and SFX are not.

---

## 2. The mixer's internal pipeline

When you call `Sound.play()`, here is what happens inside `pygame.mixer`:

```
┌────────────────────────────────────────────────────────────┐
│  MIXER PIPELINE  (per ~10 ms output frame)                 │
│                                                            │
│  Active channels:    Ch0  Ch1  Ch2  ...  Ch7  music        │
│         │             │    │    │         │    │           │
│         │  sample reader for each channel                  │
│         │             │    │    │         │    │           │
│         │  per-Sound volume scale (set_volume)             │
│         │             │    │    │         │    │           │
│         │  per-channel volume scale (Channel.set_volume)   │
│         │             │    │    │         │    │           │
│         └──────────► [ + ] sum into stereo accumulator     │
│                       │                                    │
│                  master clip (saturate at ±32767)          │
│                       │                                    │
│                  write to sound-card buffer                │
│                       │                                    │
│                       ▼                                    │
│                  speakers                                  │
└────────────────────────────────────────────────────────────┘
```

Three observations.

**Observation A — Volume is applied twice.** Once on the `Sound` object (`Sound.set_volume(v)`) and once on the `Channel` object (`Channel.set_volume(left, right)`). Both are scalar multipliers in the range `[0.0, 1.0]`. The effective output volume is `sound_volume * channel_volume`. We use this in Lecture 2 to implement the bus tree: every bus is *just* a third multiplier that we wrap around the play call.

**Observation B — Mixing is a sum, not an average.** Two sounds at volume 1.0 played at the same time will add to 2.0 in the accumulator, which clips at 1.0 (saturates at ±32767 in the integer representation). This is *clipping* — a harsh distortion you can hear as a crackle. The fix is not to play every sound at full volume. The bus structure from Lecture 2 enforces this discipline.

**Observation C — The pipeline runs on the sound card's clock, not yours.** Your Python code can call `play()` at frame 1 and the actual sample writes to the card happen 2-5 ms later (typical buffer latency). The mixer absorbs the asynchrony. For a 60 fps game that ~5 ms latency is well below the threshold of perception (~30 ms). For a 144 fps competitive shooter you would shrink the buffer; for a 2D arcade game, the default is fine.

---

## 3. `pygame.mixer.pre_init` — the one function before `pygame.init()`

Here is the entire mixer-initialisation discipline in Pygame:

```python
import pygame

# This MUST run before pygame.init(). Pygame's init() will lazily
# initialise the mixer with default parameters if you have not
# called pre_init first. The defaults are usually fine; pre_init
# lets you override them deliberately.
pygame.mixer.pre_init(
    frequency=44100,    # Hz. 22050, 44100, 48000.
    size=-16,           # bit depth. Negative means signed.
    channels=2,         # 1 mono, 2 stereo.
    buffer=512,         # samples per output frame. Smaller is lower latency.
)

pygame.init()  # mixer initialised here

# After init, allocate playback channels. The default is 8.
pygame.mixer.set_num_channels(16)
```

Four notes.

**Note A — The `-16` is not a typo.** Pygame's `size` parameter encodes both bit depth and sign: positive means unsigned, negative means signed. 16-bit signed (`-16`) is the consumer default. 8-bit unsigned (`8`) is the 8-bit gameboy aesthetic if you want it.

**Note B — Buffer size is the latency/CPU trade.** A 512-sample buffer at 44100 Hz is ~12 ms of latency. A 256-sample buffer is ~6 ms but the CPU has to fill the buffer twice as often. For a 2D game, 512 is fine. For a rhythm game where audio-input precision is the whole experience, you would drop to 256 or 128 and accept the higher mixing overhead.

**Note C — Allocating channels is a separate call.** `pygame.mixer.set_num_channels(N)` after init. The default of 8 means *eight simultaneous Sounds*; the 9th `play()` call evicts the oldest. For a game with rich SFX (collision, footsteps, ambient, multiple enemies) bump this to 16 or 32. The cost is negligible.

**Note D — Initialising the mixer can fail.** On a headless server (no sound card), `pygame.mixer.init()` will raise. The defensive pattern is:

```python
try:
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    pygame.mixer.set_num_channels(16)
except pygame.error as e:
    print(f"audio unavailable: {e}")
    # Continue without audio. Substitute a silent stub for the audio API.
```

The mini-project ships a silent stub so the game runs on a CI box with no sound card.

---

## 4. `pygame.mixer.Sound` — RAM-resident clips

A `Sound` object holds an entire audio clip decoded in RAM. Construction reads the file from disk, decodes it, and allocates a contiguous buffer of samples.

```python
footstep: pygame.mixer.Sound = pygame.mixer.Sound("assets/audio/footstep.wav")
print(footstep.get_length())   # 0.25 seconds
print(footstep.get_num_channels())  # how many channels are currently playing

footstep.play()                # fire and forget
footstep.set_volume(0.6)       # scalar [0.0, 1.0]
footstep.play(loops=3)         # play 4 times total (initial + 3 loops)
footstep.play(maxtime=200)     # stop after 200 ms regardless of length
footstep.play(fade_ms=100)     # fade in over 100 ms
```

Five disciplines.

**Discipline A — Load all sounds at startup, never inside the game loop.** The disk read and decode for a 250 ms WAV takes ~5 ms. At 60 fps you have ~16 ms per frame. A `pygame.mixer.Sound("file.wav")` call inside `update()` is a frame drop. Build an asset cache:

```python
class SoundCache:
    """Loads every sound once and returns the same handle on lookup."""

    def __init__(self) -> None:
        self._sounds: dict[str, pygame.mixer.Sound] = {}

    def load(self, key: str, path: str) -> pygame.mixer.Sound:
        if key not in self._sounds:
            self._sounds[key] = pygame.mixer.Sound(path)
        return self._sounds[key]

    def get(self, key: str) -> pygame.mixer.Sound:
        return self._sounds[key]
```

**Discipline B — Sound size is your memory budget.** A 250 ms stereo 16-bit clip at 44100 Hz is ~44 KB in RAM. A one-second clip is ~176 KB. Fifty short SFX is ~5-10 MB. This is fine on a modern PC; on a tight memory budget (mobile, embedded) you would lower the bit depth or sample rate for SFX to 22050 / mono.

**Discipline C — `play()` returns a `Channel`.** If you want to control the playback after firing, capture it:

```python
ch: pygame.mixer.Channel | None = footstep.play()
if ch is not None:
    ch.set_volume(0.3, 0.7)   # pan slightly right
    ch.fadeout(500)           # fade out over 500 ms
```

`play()` returns `None` if no channel was available — i.e. all channels are busy and the system did not evict one. In practice this rarely happens with 16+ allocated channels.

**Discipline D — Volume composes.** The effective playback volume is `sound.get_volume() * channel.get_volume()`. The bus structure from Lecture 2 adds a *third* multiplier on top (the bus chain). All three are linear scalars in `[0.0, 1.0]`. Multiply them; clamp the result.

**Discipline E — `play(loops=-1)` loops forever.** Useful for ambient drone loops. The standard `pygame.mixer.music.play(-1)` form is the same convention for streaming music.

---

## 5. `pygame.mixer.music` — the streaming singleton

Music is *one* track at a time, streamed from disk. The whole API is a module, not a class — there is exactly one music stream at any moment, and the module-level functions manipulate it.

```python
pygame.mixer.music.load("assets/audio/main-theme.ogg")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(loops=-1)   # loop forever
pygame.mixer.music.fadeout(2000)    # fade out over 2 seconds
pygame.mixer.music.stop()
pygame.mixer.music.queue("assets/audio/boss-theme.ogg")
```

Three disciplines.

**Discipline A — `music` is for *streaming*, not RAM.** The `load` call opens the file and seeks to the start; the actual decode happens as the sound card pulls samples. A 3-minute OGG track stays on disk; ~32 KB of decoded samples sit in a small ring buffer in RAM. Memory cost is constant in the song length.

**Discipline B — There is one music stream.** `load` overwrites the previous track. If you want two tracks playing simultaneously (layered music — Lecture 2 §3), neither can use `music` — you have to load both as `Sound` objects and play them on dedicated channels. The mini-project does exactly this for combat-layer crossfade.

**Discipline C — `play(loops=-1)` loops forever, like `Sound.play`.** But the streaming loop has one extra gotcha: the loop point is the *start of the file*. There is no in-file loop region. Every loop iteration restarts from sample 0. The seamless-loop authoring discipline (Lecture 3 §1) makes this constraint workable.

### 5.1 The `Sound` vs `music` decision

| Use `Sound` for | Use `music` for |
|-----------------|-----------------|
| Short clips (<2 s) | Long tracks (>30 s) |
| Sounds played many times (footsteps, hits, pickups) | The one background track currently playing |
| Sounds played simultaneously (stacked SFX) | A single foreground track |
| WAV format usually | OGG format usually |
| Loaded once, played thousands of times | Loaded once, played once or looped |

The 1 MB rule of thumb: if a clip's *decoded* size is over ~1 MB, stream it (use `music` or load as a `Sound` only if you can afford the RAM). Below 1 MB, `Sound` is cheaper.

---

## 6. Channels — the explicit handles

`pygame.mixer` allocates a fixed pool of *channels*. Each channel can play one `Sound` at a time. The default pool size is 8. You can request a specific channel by index or let the mixer pick.

```python
# Request a specific channel
ch5: pygame.mixer.Channel = pygame.mixer.Channel(5)
ch5.play(footstep)

# Reserve channels for specific purposes
pygame.mixer.set_reserved(2)   # channels 0 and 1 reserved
# Channel 0: dialogue. Channel 1: footsteps (so they never collide
# with a stack of impact SFX competing for channels 2-7).
```

Three notes.

**Note A — Reserved channels are not pickable by `Sound.play()` without explicit `Channel(N).play(sound)`.** This lets you guarantee that dialogue never gets evicted by a flood of impact SFX. The mini-project reserves channel 0 for dialogue and channel 1 for music-layer crossfade.

**Note B — `Channel.queue(sound)` plays the queued sound after the current one finishes.** Useful for sequencing dialogue lines without the polling logic to detect end-of-clip.

**Note C — `Channel.fadeout(ms)` fades the current sound to silence over `ms` milliseconds and stops it.** The hard-cut equivalent is `Channel.stop()`. Always fade. Hard cuts sound amateur.

---

## 7. The `endevent` mechanism

When a `Channel` finishes its current sound, it can post a `pygame.event` so other code can react. This is how the duck system from Lecture 2 detects "dialogue line ended."

```python
DIALOGUE_END_EVENT: int = pygame.USEREVENT + 1

dialogue_ch: pygame.mixer.Channel = pygame.mixer.Channel(0)
dialogue_ch.set_endevent(DIALOGUE_END_EVENT)
dialogue_ch.play(dialogue_clip)

# Elsewhere in the event loop:
for event in pygame.event.get():
    if event.type == DIALOGUE_END_EVENT:
        # Restore music volume from the duck.
        audio.restore_music_after_duck()
```

This is *the* event-driven pattern for audio. The alternative — polling `channel.get_busy()` every frame — works but is fragile and harder to compose.

---

## 8. A worked first program

Put the discipline together. Initialise the mixer, allocate channels, load a single SFX, and play it on a key press.

```python
"""hello-audio.py — the smallest correct Pygame audio program."""

import sys

import pygame


def main() -> int:
    # Init mixer BEFORE pygame.init().
    pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
    pygame.init()
    pygame.mixer.set_num_channels(16)

    screen: pygame.Surface = pygame.display.set_mode((400, 200))
    pygame.display.set_caption("hello audio")
    clock: pygame.time.Clock = pygame.time.Clock()

    # Load the sound ONCE, here, not in the loop.
    try:
        beep: pygame.mixer.Sound = pygame.mixer.Sound("beep.wav")
    except (pygame.error, FileNotFoundError):
        print("no beep.wav — generate one with Exercise 1 first.")
        return 1
    beep.set_volume(0.6)

    running: bool = True
    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    beep.play()
        screen.fill((24, 24, 32))
        pygame.display.flip()

    pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

Three things to notice.

- The `pre_init` block is the *first* thing in `main()`. Before the window. Before the display surface. Before any other Pygame call.
- The `Sound("beep.wav")` is loaded *once*, before the loop. Inside the loop we only call `beep.play()`, which is a constant-time operation.
- The `try`/`except` block degrades gracefully when the asset is missing. Production audio code is full of these — a missing clip should not crash the game.

---

## 9. The "twelve sounds in one frame" stress test

What happens when you stack a lot of SFX? Try this:

```python
# In your event loop, on space-bar:
for _ in range(12):
    beep.play()
```

If you have allocated 16 channels, all 12 play simultaneously. The output is loud and clippy. If you have only 8 channels, the first 8 play and the remaining 4 fail silently (`play()` returns `None`).

There are two takeaways. First, the clipping is *the bus structure's job to prevent* — Lecture 2 introduces a master-bus volume of ~0.6 that keeps the per-frame peak comfortably below clipping. Second, the silent failure is *the channel pool's job to prevent* — allocate enough channels for the peak scenario you actually need (16-32 is typical for an action game).

The "stack 12 sounds" stress test is your sanity check at the end of each audio session. If it clips, lower the master. If it drops, allocate more channels.

---

## 10. What we built and what comes next

By the end of this lecture you should have:

- The three numbers (sample rate, channels, bit depth) memorised with their conventional values.
- The `pre_init` + `init` + `set_num_channels` boilerplate typed into a `hello-audio.py`.
- The `Sound` vs `music` decision flow internalised.
- Channels, the eight-default pool, and `Channel.set_endevent` understood.
- A first `Sound.play()` call running on space-bar.

You do not yet have:

- A bus structure (Lecture 2).
- Ducking (Lecture 2).
- Layered music (Lecture 2).
- Spatial attenuation (Lecture 2).
- Loop authoring in Audacity (Lecture 3).
- OGG vs WAV decision discipline (Lecture 3).
- The Godot 4.x bridge (Lecture 3).

Lecture 2 will compose this lecture's primitives into the *three-bus mixer* that every shippable indie game uses. Lecture 3 will then teach the *content* side — how to author loops that do not click, which file format to pick for which clip, and what the same code looks like in Godot's editor-driven AudioServer model.

---

## References

- **Pygame — `pygame.mixer` documentation.** The canonical reference. Read the module page once end-to-end. <https://www.pygame.org/docs/ref/mixer.html>
- **Pygame — `pygame.mixer.music` documentation.** The streaming sub-module. <https://www.pygame.org/docs/ref/music.html>
- **Wikipedia — *Sampling (signal processing)*.** Nyquist-Shannon at a level suitable for game programmers. <https://en.wikipedia.org/wiki/Sampling_(signal_processing)>
- **Wikipedia — *Audio bit depth*.** Why 16-bit is the consumer default. <https://en.wikipedia.org/wiki/Audio_bit_depth>
- **Wikipedia — *Decibel*.** The dB primer. The single takeaway: -6 dB is half the linear amplitude. <https://en.wikipedia.org/wiki/Decibel>

---

*Continue to [Lecture 2 — Mixing, Buses, and Dynamic Music](./02-mixing-buses-and-dynamic-music.md).*
