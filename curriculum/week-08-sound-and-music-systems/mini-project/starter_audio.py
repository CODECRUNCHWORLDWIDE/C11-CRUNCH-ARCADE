"""starter_audio.py - mini-project audio module scaffold.

Drop this file into your mini-project repo as ``audio.py``. It ships
with:

- The Bus dataclass (complete; copied from Exercise 2).
- The AudioMixer facade (complete with ducking; copied from Exercise 2).
- The LayerCrossfade dataclass (complete; copied from Exercise 4).
- A SoundCache for loading sounds once at startup.
- The AudioSettings dataclass and atomic-write helpers (complete).
- A spatial helper trio: distance_attenuation, horizontal_pan,
  play_spatial.

TODO items are clearly marked. Search for "TODO" to find them.

Module-level constants (channel reservations, duck timing) live at
the top. Adjust as your project demands.
"""

from __future__ import annotations

import json
import math
import os
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional

import pygame

# ----- Audio configuration ------------------------------------------------

SAMPLE_RATE_HZ: int = 44100
BIT_DEPTH_SIZE: int = -16
CHANNELS: int = 2
BUFFER_SAMPLES: int = 512
NUM_CHANNELS: int = 16

# Channel reservations.
DIALOGUE_CHANNEL_INDEX: int = 0
LAYER_EXPLORE_CHANNEL: int = NUM_CHANNELS - 2
LAYER_COMBAT_CHANNEL: int = NUM_CHANNELS - 1

# Ducking.
DUCK_TARGET_MUSIC_VOLUME: float = 0.30
DUCK_RESTORE_MUSIC_VOLUME: float = 1.00
DUCK_FADE_MS: int = 300

# Layered music crossfade.
CROSSFADE_MS: int = 1500

# Spatial.
MIN_DISTANCE: float = 60.0
MAX_DISTANCE: float = 420.0
PAN_DISTANCE: float = 350.0

# Custom events.
DIALOGUE_END_EVENT: int = pygame.USEREVENT + 1

# Settings.
SETTINGS_SCHEMA_VERSION: int = 1


# ----- The Bus tree and AudioMixer ---------------------------------------


@dataclass
class Bus:
    """A named volume multiplier with optional parent."""

    name: str
    volume: float = 1.0
    muted: bool = False
    parent: Optional["Bus"] = None
    children: list["Bus"] = field(default_factory=list)

    def attach(self, child: "Bus") -> "Bus":
        child.parent = self
        self.children.append(child)
        return child

    def effective_volume(self) -> float:
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


@dataclass
class DuckState:
    active: bool = False
    t_remaining_ms: int = 0
    from_vol: float = 1.0
    to_vol: float = 1.0
    ref_count: int = 0


class AudioMixer:
    """Owns the bus tree and routes plays through it."""

    def __init__(self) -> None:
        self.master: Bus = Bus("master", volume=0.80)
        self.music: Bus = self.master.attach(Bus("music", volume=0.60))
        self.sfx: Bus = self.master.attach(Bus("sfx", volume=1.00))
        self.voice: Bus = self.master.attach(Bus("voice", volume=1.00))
        self.duck: DuckState = DuckState()

    def play_sfx(self, sound: pygame.mixer.Sound) -> Optional[pygame.mixer.Channel]:
        sound.set_volume(self.sfx.effective_volume())
        return sound.play()

    def play_voice(self, sound: pygame.mixer.Sound) -> Optional[pygame.mixer.Channel]:
        sound.set_volume(self.voice.effective_volume())
        ch: pygame.mixer.Channel = pygame.mixer.Channel(DIALOGUE_CHANNEL_INDEX)
        ch.set_endevent(DIALOGUE_END_EVENT)
        ch.play(sound)
        self.begin_duck()
        return ch

    def begin_duck(self) -> None:
        self.duck.ref_count += 1
        if self.duck.ref_count == 1:
            self.duck.active = True
            self.duck.from_vol = self.music.volume
            self.duck.to_vol = DUCK_TARGET_MUSIC_VOLUME
            self.duck.t_remaining_ms = DUCK_FADE_MS

    def end_duck(self) -> None:
        if self.duck.ref_count > 0:
            self.duck.ref_count -= 1
        if self.duck.ref_count == 0:
            self.duck.active = True
            self.duck.from_vol = self.music.volume
            self.duck.to_vol = DUCK_RESTORE_MUSIC_VOLUME
            self.duck.t_remaining_ms = DUCK_FADE_MS

    def update_duck(self, dt_ms: int) -> None:
        if not self.duck.active:
            return
        self.duck.t_remaining_ms -= dt_ms
        if self.duck.t_remaining_ms <= 0:
            self.music.set_volume(self.duck.to_vol)
            self.duck.active = False
            return
        progress: float = 1.0 - (self.duck.t_remaining_ms / DUCK_FADE_MS)
        v: float = self.duck.from_vol + (self.duck.to_vol - self.duck.from_vol) * progress
        self.music.set_volume(v)


# ----- The SoundCache -----------------------------------------------------


class SoundCache:
    """Load every sound once at startup; return handles thereafter."""

    def __init__(self) -> None:
        self._sounds: dict[str, pygame.mixer.Sound] = {}

    def load(self, key: str, path: str) -> pygame.mixer.Sound:
        if key in self._sounds:
            return self._sounds[key]
        try:
            sound: pygame.mixer.Sound = pygame.mixer.Sound(path)
            self._sounds[key] = sound
            return sound
        except (pygame.error, FileNotFoundError) as e:
            print(f"failed to load sound {key} from {path}: {e}")
            raise

    def get(self, key: str) -> pygame.mixer.Sound:
        return self._sounds[key]

    def has(self, key: str) -> bool:
        return key in self._sounds


# ----- LayerCrossfade -----------------------------------------------------


@dataclass
class LayerCrossfade:
    """Animation state for the two-stem crossfade."""

    target_explore: float = 1.0
    target_combat: float = 0.0
    from_explore: float = 1.0
    from_combat: float = 0.0
    t_remaining_ms: int = 0
    fade_total_ms: int = CROSSFADE_MS

    def request_combat(self, current_explore: float, current_combat: float) -> None:
        self.from_explore = current_explore
        self.from_combat = current_combat
        self.target_explore = 0.0
        self.target_combat = 1.0
        self.t_remaining_ms = self.fade_total_ms

    def request_explore(self, current_explore: float, current_combat: float) -> None:
        self.from_explore = current_explore
        self.from_combat = current_combat
        self.target_explore = 1.0
        self.target_combat = 0.0
        self.t_remaining_ms = self.fade_total_ms

    def current_levels(self) -> tuple[float, float]:
        if self.t_remaining_ms <= 0:
            return self.target_explore, self.target_combat
        progress: float = 1.0 - (self.t_remaining_ms / self.fade_total_ms)
        e: float = self.from_explore + (self.target_explore - self.from_explore) * progress
        c: float = self.from_combat + (self.target_combat - self.from_combat) * progress
        return e, c

    def advance(self, dt_ms: int) -> None:
        if self.t_remaining_ms > 0:
            self.t_remaining_ms -= dt_ms
            if self.t_remaining_ms < 0:
                self.t_remaining_ms = 0


# ----- Spatial helpers ----------------------------------------------------


def distance_attenuation(
    listener_x: float, listener_y: float,
    source_x: float, source_y: float,
    min_distance: float = MIN_DISTANCE,
    max_distance: float = MAX_DISTANCE,
) -> float:
    dx: float = source_x - listener_x
    dy: float = source_y - listener_y
    d: float = math.sqrt(dx * dx + dy * dy)
    if d <= min_distance:
        return 1.0
    if d >= max_distance:
        return 0.0
    return 1.0 - (d - min_distance) / (max_distance - min_distance)


def horizontal_pan(
    listener_x: float, source_x: float, pan_distance: float = PAN_DISTANCE,
) -> tuple[float, float]:
    dx: float = source_x - listener_x
    p: float = max(-1.0, min(1.0, dx / pan_distance))
    left: float = (1.0 - p) * 0.5
    right: float = (1.0 + p) * 0.5
    return left, right


def play_spatial(
    mixer: AudioMixer,
    sound: pygame.mixer.Sound,
    listener_x: float, listener_y: float,
    source_x: float, source_y: float,
) -> Optional[pygame.mixer.Channel]:
    bus_v: float = mixer.sfx.effective_volume()
    att: float = distance_attenuation(listener_x, listener_y, source_x, source_y)
    if att <= 0.0:
        return None
    left, right = horizontal_pan(listener_x, source_x)
    sound.set_volume(bus_v * att)
    ch: Optional[pygame.mixer.Channel] = sound.play()
    if ch is not None:
        ch.set_volume(left, right)
    return ch


# ----- AudioSettings ------------------------------------------------------


@dataclass
class AudioSettings:
    """The on-disk shape of the player's audio preferences."""

    schema_version: int = SETTINGS_SCHEMA_VERSION
    master_volume: float = 0.80
    music_volume: float = 0.60
    sfx_volume: float = 1.00
    voice_volume: float = 1.00
    music_muted: bool = False
    sfx_muted: bool = False
    voice_muted: bool = False


def audiosettings_to_dict(s: AudioSettings) -> dict:
    return asdict(s)


def audiosettings_from_dict(d: dict) -> AudioSettings:
    """Build AudioSettings from a dict, tolerating missing fields."""
    defaults = AudioSettings()
    return AudioSettings(
        schema_version=int(d.get("schema_version", defaults.schema_version)),
        master_volume=float(d.get("master_volume", defaults.master_volume)),
        music_volume=float(d.get("music_volume", defaults.music_volume)),
        sfx_volume=float(d.get("sfx_volume", defaults.sfx_volume)),
        voice_volume=float(d.get("voice_volume", defaults.voice_volume)),
        music_muted=bool(d.get("music_muted", defaults.music_muted)),
        sfx_muted=bool(d.get("sfx_muted", defaults.sfx_muted)),
        voice_muted=bool(d.get("voice_muted", defaults.voice_muted)),
    )


def apply_settings(mixer: AudioMixer, s: AudioSettings) -> None:
    """Bulk-apply an AudioSettings instance to a live AudioMixer."""
    mixer.master.set_volume(s.master_volume)
    mixer.music.set_volume(s.music_volume)
    mixer.sfx.set_volume(s.sfx_volume)
    mixer.voice.set_volume(s.voice_volume)
    mixer.music.set_muted(s.music_muted)
    mixer.sfx.set_muted(s.sfx_muted)
    mixer.voice.set_muted(s.voice_muted)


# ----- Atomic-write settings persistence ---------------------------------


def save_audio_settings(settings: AudioSettings, path: Path) -> None:
    """Atomic-write settings to disk, rotating any existing file to .bak.

    Pattern from Week 7 Lecture 3 section 4: write to .tmp, fsync,
    rename to canonical. Survives a crash mid-write.
    """
    tmp_path: Path = path.with_suffix(path.suffix + ".tmp")
    bak_path: Path = path.with_suffix(path.suffix + ".bak")
    payload: str = json.dumps(
        audiosettings_to_dict(settings), indent=2, sort_keys=True
    )
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(payload)
        f.flush()
        try:
            os.fsync(f.fileno())
        except OSError:
            # fsync may fail on some filesystems; safe to continue.
            pass
    # Rotate the existing primary to .bak before replacing.
    if path.exists():
        try:
            os.replace(path, bak_path)
        except OSError:
            pass
    os.replace(tmp_path, path)


def load_audio_settings(path: Path) -> AudioSettings:
    """Load settings from disk, falling back to .bak on failure.

    Returns dataclass defaults if neither file exists.
    """
    bak_path: Path = path.with_suffix(path.suffix + ".bak")
    for candidate in (path, bak_path):
        if not candidate.exists():
            continue
        try:
            with open(candidate, "r", encoding="utf-8") as f:
                d: dict = json.load(f)
            return audiosettings_from_dict(d)
        except (OSError, json.JSONDecodeError) as e:
            print(f"failed to load {candidate}: {e}; trying next fallback")
            continue
    return AudioSettings()


# ----- Mixer initialisation ----------------------------------------------


def init_audio() -> bool:
    """Run pre_init + init + set_num_channels. Return True on success."""
    pygame.mixer.pre_init(
        frequency=SAMPLE_RATE_HZ,
        size=BIT_DEPTH_SIZE,
        channels=CHANNELS,
        buffer=BUFFER_SAMPLES,
    )
    try:
        pygame.init()
    except pygame.error as e:
        print(f"pygame.init() failed: {e}")
        return False
    try:
        pygame.mixer.set_num_channels(NUM_CHANNELS)
    except pygame.error as e:
        print(f"set_num_channels failed: {e}")
        return False
    return True


# ----- TODO: starter helpers for the mini-project ------------------------

# TODO 1: write a helper that takes an AudioMixer and the two layer
# Sounds and starts both stems looping in sync.
#
# def start_layered_music(
#     mixer: AudioMixer,
#     explore_sound: pygame.mixer.Sound,
#     combat_sound: pygame.mixer.Sound,
#     state: LayerCrossfade,
# ) -> None:
#     # 1. Reserve channels LAYER_EXPLORE_CHANNEL and LAYER_COMBAT_CHANNEL.
#     # 2. Set explore_sound.set_volume(mixer.music.effective_volume() *
#     #    state.target_explore).
#     # 3. Same for combat_sound.
#     # 4. Call play(loops=-1) on both channels on the SAME frame.
#     pass


# TODO 2: write a helper that advances the layer crossfade by one frame
# and applies the resulting per-channel volumes.
#
# def update_layered_music(
#     mixer: AudioMixer,
#     state: LayerCrossfade,
#     dt_ms: int,
# ) -> None:
#     # 1. Call state.advance(dt_ms).
#     # 2. Read state.current_levels() into (e, c).
#     # 3. Multiply each by mixer.music.effective_volume().
#     # 4. Apply to pygame.mixer.Channel(LAYER_EXPLORE_CHANNEL) and
#     #    pygame.mixer.Channel(LAYER_COMBAT_CHANNEL) via set_volume.
#     pass


# TODO 3: write a helper that detects whether the player has just
# crossed into or out of the combat zone, and calls the appropriate
# request_combat / request_explore.
#
# def on_combat_zone_transition(
#     was_in_zone: bool,
#     is_in_zone: bool,
#     state: LayerCrossfade,
# ) -> None:
#     if was_in_zone == is_in_zone:
#         return
#     e_now, c_now = state.current_levels()
#     if is_in_zone:
#         state.request_combat(e_now, c_now)
#     else:
#         state.request_explore(e_now, c_now)
