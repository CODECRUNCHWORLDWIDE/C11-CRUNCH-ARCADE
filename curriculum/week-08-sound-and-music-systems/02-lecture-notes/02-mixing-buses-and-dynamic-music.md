# Lecture 2 — Mixing, Buses, and Dynamic Music

> **Duration:** ~2 hours of reading plus hands-on.
> **Outcome:** You can build a three-bus mixer from scratch in Pygame, implement event-driven ducking, crossfade between two music layers in exact sync, and apply distance attenuation to a 2D spatial SFX.

If you only remember one thing from this lecture, remember this:

> **A bus is a multiplier with a name. Every SFX you play is multiplied by its bus volume, which is multiplied by the bus's parent's volume, all the way up to the master. Three numbers per play call gives you a mixing console. The whole bus tree is fifty lines of code.**

The naive Pygame audio call — `sound.set_volume(0.5); sound.play()` — gives the player no way to mute the music while keeping SFX. A real game must split *categories* of audio (music, SFX, voice, UI) into independent volume groups. The standard pattern is a *bus tree*: a parent-child hierarchy of named groups where each group has its own volume multiplier and the effective playback volume is the product of the chain from the leaf to the root.

This lecture builds the tree, demonstrates *ducking* (the technique where dialogue automatically lowers music), implements *layered music* (two stems playing in sync, crossfading on game state), and adds *spatial attenuation* (the volume falls off with distance from the listener). Each is a small body of code; together they are the audio backbone of every shippable indie game.

---

## 1. The bus tree

A bus is a node in a tree. Each bus has:

- A **name** (string).
- A **volume** (float in `[0.0, 1.0]`; the multiplier).
- A **parent** (another bus, or `None` for the root).
- An optional **mute** flag (boolean; same as volume = 0 but more explicit).

A bus can also be *active* or *muted*. Muting a bus silences every descendant; the children are unaffected internally — they still have their own volumes — but when you ask for the *effective volume* (the product up the chain), the mute short-circuits to zero.

The minimal tree:

```
master  (top)
├── music
├── sfx
└── voice
```

A larger tree:

```
master
├── music
│   ├── ambient
│   └── combat
├── sfx
│   ├── footsteps
│   ├── impact
│   └── pickup
├── voice
└── ui
```

The depth-of-tree decision is a design call. Two levels (master + leaves) is enough for most small games. Three levels (master + category + sub-category) is useful when, for example, you want a single "footsteps" slider that affects every footstep sound regardless of surface type.

### 1.1 Implementing `Bus` in Python

```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Bus:
    """A named volume multiplier with optional parent.

    Effective volume is the product of self.volume up the parent chain.
    Mute short-circuits to 0 anywhere on the chain.
    """

    name: str
    volume: float = 1.0
    muted: bool = False
    parent: Optional[Bus] = None
    children: list[Bus] = field(default_factory=list)

    def attach(self, child: Bus) -> Bus:
        """Add a child bus and set its parent to self."""
        child.parent = self
        self.children.append(child)
        return child

    def effective_volume(self) -> float:
        """Walk up the chain, multiplying volumes. Mute zeros out."""
        if self.muted:
            return 0.0
        v: float = self.volume
        p: Optional[Bus] = self.parent
        while p is not None:
            if p.muted:
                return 0.0
            v *= p.volume
            p = p.parent
        return max(0.0, min(1.0, v))

    def set_volume(self, value: float) -> None:
        self.volume = max(0.0, min(1.0, value))

    def set_muted(self, value: bool) -> None:
        self.muted = value
```

The class is intentionally tiny. The whole abstraction is `effective_volume()`. Five fields, four methods, twenty lines. Test it:

```python
master = Bus("master", volume=0.8)
music = master.attach(Bus("music", volume=0.6))
sfx = master.attach(Bus("sfx", volume=1.0))

print(music.effective_volume())  # 0.48
print(sfx.effective_volume())    # 0.80

master.set_muted(True)
print(music.effective_volume())  # 0.0
print(sfx.effective_volume())    # 0.0
```

### 1.2 The `AudioMixer` facade

The `Bus` class on its own does not play sounds. We add a small facade that owns the bus tree and routes `play()` calls through it:

```python
@dataclass
class AudioMixer:
    """Owns the bus tree and routes Sound.play() through it."""

    master: Bus = field(default_factory=lambda: Bus("master", volume=0.8))
    music: Bus = field(init=False)
    sfx: Bus = field(init=False)
    voice: Bus = field(init=False)

    def __post_init__(self) -> None:
        self.music = self.master.attach(Bus("music", volume=0.6))
        self.sfx = self.master.attach(Bus("sfx", volume=1.0))
        self.voice = self.master.attach(Bus("voice", volume=1.0))

    def play_sfx(self, sound: "pygame.mixer.Sound", volume: float = 1.0) -> None:
        """Play a Sound on the sfx bus with an optional per-call multiplier."""
        eff: float = self.sfx.effective_volume() * volume
        sound.set_volume(eff)
        sound.play()

    def play_voice(self, sound: "pygame.mixer.Sound", volume: float = 1.0) -> Optional["pygame.mixer.Channel"]:
        """Play a Sound on the voice bus. Returns the Channel for endevent wiring."""
        eff: float = self.voice.effective_volume() * volume
        sound.set_volume(eff)
        return sound.play()

    def set_music_volume(self, value: float) -> None:
        """Setting the music bus volume reflects immediately on the streamed music."""
        self.music.set_volume(value)
        import pygame
        pygame.mixer.music.set_volume(self.music.effective_volume())
```

Notes:

- `play_sfx` looks up the effective volume *at play time*, not at load time. If the player changes the SFX slider, the next SFX uses the new volume; in-flight SFX keep their old volume. That is fine for short clips.
- `set_music_volume` calls `pygame.mixer.music.set_volume(...)` immediately because the streaming music has its own playback state — there is no per-play volume call to wrap.
- The facade does not own the `Sound` objects. The `SoundCache` from Lecture 1 §4 does. The mixer is concerned with *levels*, not with *what is loaded*.

---

## 2. Ducking

*Ducking* is the audio-engineering term for "automatically lower the music when something else is playing." In speech radio it lowers the background bed when the host talks; in dance music a sidechain compressor lowers the bass when the kick drum hits; in game audio it lowers the music when an NPC speaks.

The mechanism is simple: on dialogue start, fade the music bus down to ~30% (-10 dB ish). On dialogue end, fade it back to 100%. The fade — not the abrupt cut — is the production quality marker.

### 2.1 The implementation

```python
DUCK_TARGET_VOLUME: float = 0.30
DUCK_RESTORE_VOLUME: float = 1.00
DUCK_FADE_MS: int = 300


@dataclass
class DuckState:
    """Tracks the current duck animation."""

    active: bool = False
    t_remaining_ms: int = 0
    from_vol: float = 1.0
    to_vol: float = 1.0


class AudioMixer:
    # ... fields from §1.2 ...

    duck: DuckState = field(default_factory=DuckState)

    def begin_duck(self) -> None:
        """Start fading the music bus down."""
        self.duck.active = True
        self.duck.from_vol = self.music.volume
        self.duck.to_vol = DUCK_TARGET_VOLUME
        self.duck.t_remaining_ms = DUCK_FADE_MS

    def end_duck(self) -> None:
        """Start fading the music bus back up."""
        self.duck.active = True
        self.duck.from_vol = self.music.volume
        self.duck.to_vol = DUCK_RESTORE_VOLUME
        self.duck.t_remaining_ms = DUCK_FADE_MS

    def update_duck(self, dt_ms: int) -> None:
        """Call once per frame from the game loop. Advances the duck fade."""
        if not self.duck.active:
            return
        self.duck.t_remaining_ms -= dt_ms
        if self.duck.t_remaining_ms <= 0:
            self.set_music_volume(self.duck.to_vol)
            self.duck.active = False
            return
        # Linear ramp. The ear hears log-volume, but over 300 ms a linear
        # ramp is indistinguishable from log to anyone but an audio engineer.
        progress: float = 1.0 - (self.duck.t_remaining_ms / DUCK_FADE_MS)
        v: float = self.duck.from_vol + (self.duck.to_vol - self.duck.from_vol) * progress
        self.set_music_volume(v)
```

### 2.2 Wiring it to the dialogue clip

Use the `endevent` from Lecture 1 §7:

```python
DIALOGUE_END_EVENT: int = pygame.USEREVENT + 1

dialogue_channel: pygame.mixer.Channel = pygame.mixer.Channel(0)
dialogue_channel.set_endevent(DIALOGUE_END_EVENT)


def play_dialogue(mixer: AudioMixer, clip: pygame.mixer.Sound) -> None:
    """Play a dialogue clip and duck the music."""
    mixer.begin_duck()
    eff: float = mixer.voice.effective_volume()
    clip.set_volume(eff)
    dialogue_channel.play(clip)


# In the event loop:
for event in pygame.event.get():
    if event.type == DIALOGUE_END_EVENT:
        mixer.end_duck()

# In the per-frame update:
mixer.update_duck(dt_ms)
```

Three things to notice.

- The duck is *event-driven on start* (the duck fires when `play_dialogue` is called) and *event-driven on end* (the duck fires when the `DIALOGUE_END_EVENT` is posted by pygame when the channel finishes).
- The duck *fade* happens in `update_duck`, which runs every frame. The fade is the time-based animation that the event-driven start/end events kick off.
- The duck applies to the *music bus*, not to individual music sounds. This is why we built the bus structure first.

### 2.3 The duck-during-duck edge case

What if the player triggers a second dialogue line while the first is still playing? The naive `begin_duck` call captures `from_vol = self.music.volume`, which is currently `0.3` (mid-duck). The duck then "starts again" from 0.3 toward 0.3 — visually a no-op. The fix is to *track an outstanding duck count*: a counter that increments on dialogue start and decrements on dialogue end. Only when the counter returns to zero do we begin the restore.

```python
@dataclass
class DuckState:
    active: bool = False
    t_remaining_ms: int = 0
    from_vol: float = 1.0
    to_vol: float = 1.0
    ref_count: int = 0


def begin_duck(self) -> None:
    self.duck.ref_count += 1
    if self.duck.ref_count == 1:
        self.duck.active = True
        self.duck.from_vol = self.music.volume
        self.duck.to_vol = DUCK_TARGET_VOLUME
        self.duck.t_remaining_ms = DUCK_FADE_MS


def end_duck(self) -> None:
    if self.duck.ref_count > 0:
        self.duck.ref_count -= 1
    if self.duck.ref_count == 0:
        self.duck.active = True
        self.duck.from_vol = self.music.volume
        self.duck.to_vol = DUCK_RESTORE_VOLUME
        self.duck.t_remaining_ms = DUCK_FADE_MS
```

This is the same pattern as a semaphore. The ref count is the number of "duck reasons" currently active; the music restores only when none are.

---

## 3. Layered music

Layered music — also called *adaptive music* or *vertical layering* — is the technique where two or more stems play in *exact* sync, and you crossfade between them to convey game-state changes. The classic example: an "explore" layer plays in safe areas, a "combat" layer fades in when enemies appear, both layers play together during boss fights at different mix levels.

The discipline is hard for one reason: the two stems must be *bit-perfectly aligned* in time. If the explore layer starts at frame 0 and the combat layer starts at frame 6 (a 100 ms delay), they will be out of phase for the entire song and sound terrible. The fix is to *play both at the same `play()` call frame* and to keep both playing forever — only the *volumes* change as the state changes. You never stop one and start another; you fade volumes.

### 3.1 The implementation in Pygame

Pygame's `mixer.music` is a singleton — there can only be one streaming track. For two layers we use two `Sound` objects loaded into RAM and play them on dedicated channels:

```python
explore_layer: pygame.mixer.Sound = pygame.mixer.Sound("assets/audio/explore.ogg")
combat_layer: pygame.mixer.Sound = pygame.mixer.Sound("assets/audio/combat.ogg")

LAYER_EXPLORE_CHANNEL: int = 14   # reserve high channel indices
LAYER_COMBAT_CHANNEL: int = 15

ch_explore: pygame.mixer.Channel = pygame.mixer.Channel(LAYER_EXPLORE_CHANNEL)
ch_combat: pygame.mixer.Channel = pygame.mixer.Channel(LAYER_COMBAT_CHANNEL)


def start_layered_music(mixer: AudioMixer) -> None:
    """Start both layers in sync. Combat layer silent at first."""
    explore_layer.set_volume(mixer.music.effective_volume() * 1.0)
    combat_layer.set_volume(mixer.music.effective_volume() * 0.0)
    ch_explore.play(explore_layer, loops=-1)
    ch_combat.play(combat_layer, loops=-1)
```

Both channels start playing on the same frame. Both loop forever. Both are at the same nominal length (this matters — they must be the same number of samples or they will drift). The combat layer is silent; the explore layer is full.

### 3.2 The crossfade

Crossfading between layers is a per-frame volume animation, the same shape as the duck:

```python
@dataclass
class LayerCrossfade:
    target_explore: float = 1.0
    target_combat: float = 0.0
    fade_ms: int = 1500
    t_remaining_ms: int = 0
    from_explore: float = 1.0
    from_combat: float = 0.0


def request_combat_music(state: LayerCrossfade) -> None:
    state.from_explore = ch_explore.get_volume()
    state.from_combat = ch_combat.get_volume()
    state.target_explore = 0.0
    state.target_combat = 1.0
    state.t_remaining_ms = state.fade_ms


def request_explore_music(state: LayerCrossfade) -> None:
    state.from_explore = ch_explore.get_volume()
    state.from_combat = ch_combat.get_volume()
    state.target_explore = 1.0
    state.target_combat = 0.0
    state.t_remaining_ms = state.fade_ms


def update_layered_music(state: LayerCrossfade, mixer: AudioMixer, dt_ms: int) -> None:
    if state.t_remaining_ms <= 0:
        return
    state.t_remaining_ms -= dt_ms
    if state.t_remaining_ms <= 0:
        ch_explore.set_volume(state.target_explore * mixer.music.effective_volume())
        ch_combat.set_volume(state.target_combat * mixer.music.effective_volume())
        return
    progress: float = 1.0 - (state.t_remaining_ms / state.fade_ms)
    e: float = state.from_explore + (state.target_explore - state.from_explore) * progress
    c: float = state.from_combat + (state.target_combat - state.from_combat) * progress
    mv: float = mixer.music.effective_volume()
    ch_explore.set_volume(e * mv)
    ch_combat.set_volume(c * mv)
```

Three observations.

- A 1500 ms (1.5 s) crossfade is the right number for music-state transitions. Faster feels abrupt; slower feels muddy.
- The crossfade volumes are *multiplied* by `mixer.music.effective_volume()`. The bus chain still applies. If the player has lowered the music slider to 0.3, both layers are quieter throughout — the crossfade only adjusts their *relative* balance.
- We use *linear* crossfades, not *equal-power* crossfades. Linear is correct when the two stems are *correlated* (the same music piece, layered) — at the 50% point both layers play at 0.5, summing to 1.0, which is what you want. Equal-power (`sin/cos` curves) is correct when the two stems are *uncorrelated* (one ends, a different one begins).

### 3.3 The loop-length discipline

For layered music to stay in sync, both stems must be the *same exact length in samples*. A 30.000 second explore layer paired with a 30.013 second combat layer drifts ~0.4 ms per loop, which accumulates to a perceptible offset after a minute. The author's discipline (Lecture 3 §1) is to trim both stems to the *same* sample count in Audacity before exporting.

If you cannot control the source, you can re-record both stems in Audacity at the same BPM and length. The mini-project ships two stems guaranteed to be the same length.

---

## 4. Spatial attenuation in 2D

A 2D game's "spatial audio" is volume that scales with distance and pan that scales with horizontal offset. The math is straightforward; the trick is choosing the curve.

### 4.1 Distance attenuation

```python
import math


def distance_attenuation(
    listener_x: float, listener_y: float,
    source_x: float, source_y: float,
    min_distance: float = 50.0,
    max_distance: float = 400.0,
) -> float:
    """Return a volume scalar in [0, 1] based on distance.

    Within min_distance: full volume (1.0).
    Between min and max: linear ramp.
    Beyond max_distance: silent (0.0).
    """
    dx: float = source_x - listener_x
    dy: float = source_y - listener_y
    d: float = math.sqrt(dx * dx + dy * dy)
    if d <= min_distance:
        return 1.0
    if d >= max_distance:
        return 0.0
    return 1.0 - (d - min_distance) / (max_distance - min_distance)
```

The *linear* attenuation curve is the simplest and the right default. Inverse-square (`1 / d^2`) is physically correct but sounds wrong for game audio — sounds drop off too quickly and the listener feels deaf two screens away. Linear with min/max clamping gives the player intuitive control.

The `min_distance` parameter is the "everything inside this radius is at full volume" zone — a fixed margin so a sound centred on the player does not suddenly snap from 1.0 to 0.99 when the player moves one pixel.

### 4.2 Stereo panning

```python
def horizontal_pan(
    listener_x: float, source_x: float, pan_distance: float = 300.0,
) -> tuple[float, float]:
    """Return (left, right) volumes in [0, 1] based on horizontal offset.

    Source directly above listener: (0.5, 0.5).
    Source to the right: shifts toward (0.1, 0.9).
    """
    dx: float = source_x - listener_x
    # Normalise to [-1, +1] over pan_distance.
    p: float = max(-1.0, min(1.0, dx / pan_distance))
    # Linear pan law: at +1 all right, at -1 all left, at 0 centre.
    left: float = (1.0 - p) * 0.5
    right: float = (1.0 + p) * 0.5
    return left, right
```

The pan_distance of 300 pixels means "objects 300 pixels left or right are hard-panned to one side." The curve is linear; an equal-power pan (`cos(p) / sin(p)`) is more correct for uncorrelated sources but linear is fine for game SFX.

### 4.3 Wiring it together

```python
def play_spatial_sfx(
    mixer: AudioMixer,
    sound: pygame.mixer.Sound,
    listener_x: float, listener_y: float,
    source_x: float, source_y: float,
) -> None:
    """Play a Sound with distance attenuation and stereo pan."""
    bus_v: float = mixer.sfx.effective_volume()
    att: float = distance_attenuation(listener_x, listener_y, source_x, source_y)
    if att <= 0.0:
        return  # too far; do not bother allocating a channel
    left, right = horizontal_pan(listener_x, source_x)
    # The Sound's volume is the bus chain times the distance attenuation.
    # The Channel's volume is the pan (which is also two-channel).
    sound.set_volume(bus_v * att)
    ch: Optional[pygame.mixer.Channel] = sound.play()
    if ch is not None:
        ch.set_volume(left, right)
```

This is the spatial-SFX call. Three multiplications (bus, attenuation, pan) compose into one playback volume. The pan is the only piece that ends up on the `Channel` rather than the `Sound`, because the two-arg `Channel.set_volume(left, right)` is how Pygame expresses stereo balance.

---

## 5. The master-volume trap

The trap: your settings menu has one slider labelled "Volume" and it controls the master bus. The player wants to mute the music while keeping SFX. They cannot. They write a one-star review.

The fix: ship at least *three* sliders.

- **Master** — overall level. Affects everything.
- **Music** — music bus only.
- **SFX** — SFX bus only.

A typical game ships four:

- Master / Music / SFX / Voice.

Some ship more (footsteps separate from impact SFX, UI sounds separate from everything else). For a small game four is plenty. For a small game with no dialogue, three is plenty. The threshold question: *can the player mute every category they care about independently?* If yes, you have enough sliders.

### 5.1 The settings model

```python
@dataclass
class AudioSettings:
    """The on-disk shape of the player's audio preferences."""

    master_volume: float = 0.8
    music_volume: float = 0.6
    sfx_volume: float = 1.0
    voice_volume: float = 1.0
    music_muted: bool = False
    sfx_muted: bool = False
    voice_muted: bool = False


def apply_settings(mixer: AudioMixer, s: AudioSettings) -> None:
    mixer.master.set_volume(s.master_volume)
    mixer.music.set_volume(s.music_volume)
    mixer.sfx.set_volume(s.sfx_volume)
    mixer.voice.set_volume(s.voice_volume)
    mixer.music.set_muted(s.music_muted)
    mixer.sfx.set_muted(s.sfx_muted)
    mixer.voice.set_muted(s.voice_muted)
    import pygame
    pygame.mixer.music.set_volume(mixer.music.effective_volume())
```

`AudioSettings` is a dataclass; the same `to_dict` / `from_dict` discipline from Week 7 applies. The settings file is `audio_settings.json` and is written with the atomic-write pattern from Week 7 Lecture 3. The mini-project does exactly this — the settings panel from Week 7 gains three new sliders this week.

---

## 6. The bus-chain effective-volume cost

You may worry that walking the bus chain on every `play()` is wasteful. It is not:

- A typical chain is 2-3 levels deep.
- The `effective_volume` call is 3-5 multiplications and 1-2 conditional branches.
- A 60 fps game plays at most ~20 SFX per frame.
- 20 × 5 multiplications × 60 fps = ~6000 multiplications per second.

This is roughly *0.00001%* of a typical Python interpreter's throughput. The pattern is not a performance concern. If your profiler shows the bus traversal on the hot path, you have miscounted by three orders of magnitude — look elsewhere.

For a paranoid optimisation, cache the effective volumes after every `set_volume` or `set_muted` mutation. The mini-project does not bother.

---

## 7. The full mixer architecture

Putting Lecture 1 and Lecture 2 together, the audio module of a small game looks like this:

```
audio.py
├── init_audio()              # pre_init, init, set_num_channels
├── class SoundCache          # load each .wav/.ogg once
├── class Bus                 # name, volume, parent, children, effective_volume
├── class AudioMixer          # owns master / music / sfx / voice buses
│   ├── play_sfx              # routes through sfx bus
│   ├── play_voice            # routes through voice bus, returns Channel
│   ├── set_music_volume      # also updates mixer.music streaming
│   ├── begin_duck / end_duck / update_duck
│   └── apply_settings        # bulk-apply an AudioSettings dataclass
├── class LayerCrossfade      # vertical layering state
│   ├── request_combat_music
│   ├── request_explore_music
│   └── update_layered_music
└── play_spatial_sfx          # distance + pan, builds on play_sfx
```

About 250 lines of Python. Every line is replayable; nothing here is "magic." The same 250 lines port to Godot as ~30 lines of GDScript plus a one-screen editor configuration.

---

## 8. What to mix at what level

A practical mixing reference. These are starting points, not laws.

| Sound category | Bus | Typical Sound volume | Typical bus volume | Effective |
|----------------|-----|----------------------|--------------------|-----------|
| UI button click | sfx | 0.5 | 1.0 | 0.4 (with 0.8 master) |
| Footstep | sfx | 0.4 | 1.0 | 0.32 |
| Pickup jingle | sfx | 0.7 | 1.0 | 0.56 |
| Hit impact | sfx | 0.8 | 1.0 | 0.64 |
| Explosion | sfx | 1.0 | 1.0 | 0.80 |
| Ambient drone | music | 0.6 | 0.6 | 0.29 |
| Music stem | music | 0.8 | 0.6 | 0.38 |
| Boss music | music | 1.0 | 0.6 | 0.48 |
| Dialogue line | voice | 0.9 | 1.0 | 0.72 |

Observation: the master bus at 0.8 leaves ~20% of headroom for transient peaks. The music bus at 0.6 lets SFX cut through. Dialogue at the voice bus 1.0 means dialogue is the loudest thing on the screen when it plays, which is correct — dialogue is information, and the duck of the music makes it the focal point.

---

## 9. The "every clip the same volume" anti-pattern

A common new-developer failure: every SFX plays at `sound.set_volume(1.0)`. Every clip is the same loudness. The mix sounds flat and the player cannot tell which sounds matter.

The fix is *per-clip pre-mixing*. When you import a clip, listen to it on the bus you intend to play it on, and dial the `sound.set_volume()` so it sits at a level appropriate to its *importance*:

- *Background* sounds (ambient, distant) should sit at 0.3-0.5.
- *Feedback* sounds (footsteps, button clicks, ambient pickups) at 0.5-0.7.
- *Important* sounds (hits, pickups the player will hear) at 0.7-0.9.
- *Critical* sounds (death, level-up, "you found the key") at 0.9-1.0.

This is a content-side mixing pass; you do it once per clip on import. The mini-project's `assets/audio/credits.md` ships with the recommended per-clip volume for every clip in the asset list.

---

## 10. What we built and what comes next

By the end of this lecture you should have:

- A `Bus` class with effective-volume traversal.
- An `AudioMixer` facade with `play_sfx`, `play_voice`, ducking, and bulk settings application.
- A layered-music crossfade state machine.
- A `play_spatial_sfx` helper with distance attenuation and stereo pan.
- A four-slider mental model (master, music, SFX, voice) for the settings UI.

You do not yet have:

- Loop-clean assets authored in Audacity (Lecture 3).
- A decision rule for OGG vs WAV vs MP3 (Lecture 3).
- The Godot 4.x AudioServer mapping (Lecture 3).
- A persistent audio settings file written through last week's atomic-write pipeline (mini-project).

Lecture 3 covers the content side: authoring loops in Audacity, picking the right file format per clip, and reading Godot's `AudioServer` documentation so the bridge to Week 9 is open.

---

## References

- **Pygame — `pygame.mixer.Sound.set_volume`.** Two-argument form takes stereo `(left, right)`. <https://www.pygame.org/docs/ref/mixer.html#pygame.mixer.Sound.set_volume>
- **Pygame — `pygame.mixer.Channel.set_volume`.** Same two-arg form on the Channel; what we use for pan. <https://www.pygame.org/docs/ref/mixer.html#pygame.mixer.Channel.set_volume>
- **Pygame — `pygame.mixer.Channel.set_endevent`.** The event-driven hook for ducking. <https://www.pygame.org/docs/ref/mixer.html#pygame.mixer.Channel.set_endevent>
- **Wikipedia — *Sidechain compression*.** The audio-engineering background to ducking. <https://en.wikipedia.org/wiki/Dynamic_range_compression#Side-chaining>
- **Godot — *Audio buses* tutorial.** The same three-bus structure expressed in the Godot editor. <https://docs.godotengine.org/en/stable/tutorials/audio/audio_buses.html>

---

*Continue to [Lecture 3 — Authoring Loops, Formats, and the Godot Bridge](./03-authoring-loops-formats-and-the-godot-bridge.md).*
