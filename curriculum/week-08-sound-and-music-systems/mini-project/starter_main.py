"""starter_main.py - mini-project game scaffold.

Drop this file into your mini-project repo as ``main.py``. It ships
with a runnable Pygame loop, a Coin-Pink player on a single screen,
two NPC markers, a combat zone, and three enemy markers. The audio
subsystem (init, bus tree, mixer) is wired through ``audio.py``
(use ``starter_audio.py`` from this folder).

Search for "TODO" to find the gaps you need to fill:

- TODO 1: load real audio assets and synthesise placeholder fallbacks.
- TODO 2: wire NPC dialogue with ducking.
- TODO 3: wire combat-zone crossfade.
- TODO 4: wire spatial attack SFX.
- TODO 5: build the settings panel (Esc).

The file as shipped compiles cleanly and runs as a silent demo so
you can see the layout before adding audio. Add audio one TODO at
a time.
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pygame

# Import the audio module you copied from ``starter_audio.py``.
import audio as audio_module


# ----- Window configuration -----------------------------------------------

WINDOW_W: int = 960
WINDOW_H: int = 540
TARGET_FPS: int = 60
WINDOW_TITLE: str = "C11 Week 8 - Mini-project - Audio game"

BG_COLOUR: tuple[int, int, int] = (24, 24, 32)
TEXT_COLOUR: tuple[int, int, int] = (240, 240, 240)
DIM_COLOUR: tuple[int, int, int] = (140, 140, 150)
PLAYER_COLOUR: tuple[int, int, int] = (236, 72, 153)
NPC_A_COLOUR: tuple[int, int, int] = (96, 165, 250)
NPC_B_COLOUR: tuple[int, int, int] = (132, 204, 22)
COMBAT_ZONE_FILL: tuple[int, int, int] = (50, 24, 32)
COMBAT_ZONE_BORDER: tuple[int, int, int] = (220, 80, 80)
ENEMY_COLOUR: tuple[int, int, int] = (250, 204, 21)
FLASH_GREEN: tuple[int, int, int] = (132, 204, 22)


# ----- World layout -------------------------------------------------------

PLAYER_SIZE: int = 22
PLAYER_SPEED: float = 220.0
NPC_INTERACT_RADIUS: float = 80.0


@dataclass
class NPC:
    name: str
    x: float
    y: float
    colour: tuple[int, int, int]
    dialogue_key: str


@dataclass
class Enemy:
    x: float
    y: float


# Two NPCs and a combat zone with three enemies.
NPCS: list[NPC] = [
    NPC("Alphard", 180.0, 200.0, NPC_A_COLOUR, "dialogue_a"),
    NPC("Beren",   180.0, 380.0, NPC_B_COLOUR, "dialogue_b"),
]

COMBAT_ZONE: pygame.Rect = pygame.Rect(540, 120, 380, 340)

ENEMIES: list[Enemy] = [
    Enemy(610.0, 200.0),
    Enemy(810.0, 280.0),
    Enemy(680.0, 400.0),
]


# ----- Asset path config --------------------------------------------------

ASSETS_DIR: Path = Path("assets") / "audio"

# TODO 1: replace these with paths to real CC0/CC-BY assets you source.
# The defaults point at filenames that may or may not exist in your
# assets/audio folder. The game will fall back to silence for missing
# clips; the demo will be quieter but still runnable.
ASSET_PATHS: dict[str, str] = {
    "footstep":      str(ASSETS_DIR / "footstep.wav"),
    "attack":        str(ASSETS_DIR / "attack.wav"),
    "pickup":        str(ASSETS_DIR / "pickup.wav"),
    "dialogue_a":    str(ASSETS_DIR / "dialogue-a.ogg"),
    "dialogue_b":    str(ASSETS_DIR / "dialogue-b.ogg"),
    "explore_layer": str(ASSETS_DIR / "explore-layer.ogg"),
    "combat_layer":  str(ASSETS_DIR / "combat-layer.ogg"),
}


SETTINGS_PATH: Path = Path("audio_settings.json")
FOOTSTEP_INTERVAL_MS: int = 280
FLASH_FRAMES: int = 30


# ----- Helpers ------------------------------------------------------------


def distance(ax: float, ay: float, bx: float, by: float) -> float:
    dx: float = ax - bx
    dy: float = ay - by
    return math.sqrt(dx * dx + dy * dy)


def nearest_enemy(player_x: float, player_y: float) -> Enemy:
    return min(ENEMIES, key=lambda e: distance(player_x, player_y, e.x, e.y))


def load_assets_or_warn(cache: audio_module.SoundCache) -> dict[str, bool]:
    """Attempt to load every asset. Returns a key -> success dict."""
    status: dict[str, bool] = {}
    for key, path in ASSET_PATHS.items():
        if not Path(path).exists():
            print(f"asset missing: {path} (will fall back to silence)")
            status[key] = False
            continue
        try:
            cache.load(key, path)
            status[key] = True
        except (pygame.error, FileNotFoundError) as e:
            print(f"failed to load {key}: {e}")
            status[key] = False
    return status


# ----- Main loop ----------------------------------------------------------


def main() -> int:
    if not audio_module.init_audio():
        print("audio init failed; continuing without audio")

    screen: pygame.Surface = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    pygame.display.set_caption(WINDOW_TITLE)
    clock: pygame.time.Clock = pygame.time.Clock()
    font_lg: pygame.font.Font = pygame.font.SysFont(None, 26)
    font_sm: pygame.font.Font = pygame.font.SysFont(None, 20)

    mixer: audio_module.AudioMixer = audio_module.AudioMixer()
    cache: audio_module.SoundCache = audio_module.SoundCache()
    asset_status: dict[str, bool] = load_assets_or_warn(cache)

    # Apply persisted settings.
    settings: audio_module.AudioSettings = audio_module.load_audio_settings(SETTINGS_PATH)
    audio_module.apply_settings(mixer, settings)

    crossfade: audio_module.LayerCrossfade = audio_module.LayerCrossfade()

    player_x: float = 320.0
    player_y: float = WINDOW_H / 2.0
    is_in_combat_zone: bool = False
    was_in_combat_zone: bool = False
    footstep_timer_ms: int = 0
    flash_text: str = ""
    flash_t: int = 0

    # TODO 3: if both layered-music assets loaded, start them looping
    # in sync. The starter implements the silent fallback.
    music_started: bool = False
    if asset_status.get("explore_layer") and asset_status.get("combat_layer"):
        try:
            explore_sound: pygame.mixer.Sound = cache.get("explore_layer")
            combat_sound: pygame.mixer.Sound = cache.get("combat_layer")
            ch_explore: pygame.mixer.Channel = pygame.mixer.Channel(audio_module.LAYER_EXPLORE_CHANNEL)
            ch_combat: pygame.mixer.Channel = pygame.mixer.Channel(audio_module.LAYER_COMBAT_CHANNEL)
            music_eff: float = mixer.music.effective_volume()
            explore_sound.set_volume(music_eff * crossfade.target_explore)
            combat_sound.set_volume(music_eff * crossfade.target_combat)
            ch_explore.play(explore_sound, loops=-1)
            ch_combat.play(combat_sound, loops=-1)
            music_started = True
        except (pygame.error, KeyError) as e:
            print(f"could not start layered music: {e}")

    running: bool = True
    while running:
        dt_ms: int = clock.tick(TARGET_FPS)
        dt_s: float = dt_ms / 1000.0

        # ---- Events -----------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == audio_module.DIALOGUE_END_EVENT:
                mixer.end_duck()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # TODO 5: open the settings panel here. For the
                    # starter, Esc quits.
                    running = False
                elif event.key == pygame.K_e:
                    # TODO 2: play the nearest NPC's dialogue if in range.
                    for npc in NPCS:
                        if distance(player_x, player_y, npc.x, npc.y) <= NPC_INTERACT_RADIUS:
                            if asset_status.get(npc.dialogue_key):
                                mixer.play_voice(cache.get(npc.dialogue_key))
                                flash_text = f"{npc.name}: dialogue (music ducked)"
                                flash_t = FLASH_FRAMES
                            else:
                                flash_text = f"{npc.name}: (no audio loaded)"
                                flash_t = FLASH_FRAMES
                            break
                elif event.key == pygame.K_SPACE:
                    # TODO 4: fire spatial attack at nearest enemy if in combat zone.
                    if is_in_combat_zone and asset_status.get("attack"):
                        e_target: Enemy = nearest_enemy(player_x, player_y)
                        audio_module.play_spatial(
                            mixer, cache.get("attack"),
                            player_x, player_y, e_target.x, e_target.y,
                        )
                        flash_text = f"attack -> ({e_target.x:.0f}, {e_target.y:.0f})"
                        flash_t = FLASH_FRAMES
                    elif is_in_combat_zone:
                        flash_text = "attack (no audio loaded)"
                        flash_t = FLASH_FRAMES

        # ---- Movement ---------------------------------------------------
        keys = pygame.key.get_pressed()
        vx: float = 0.0
        vy: float = 0.0
        if keys[pygame.K_a]:
            vx -= 1.0
        if keys[pygame.K_d]:
            vx += 1.0
        if keys[pygame.K_w]:
            vy -= 1.0
        if keys[pygame.K_s]:
            vy += 1.0
        norm: float = math.sqrt(vx * vx + vy * vy)
        if norm > 0.0:
            vx /= norm
            vy /= norm
        player_x += vx * PLAYER_SPEED * dt_s
        player_y += vy * PLAYER_SPEED * dt_s
        half: float = PLAYER_SIZE / 2.0
        if player_x < half:
            player_x = half
        if player_x > WINDOW_W - half:
            player_x = WINDOW_W - half
        if player_y < half:
            player_y = half
        if player_y > WINDOW_H - half:
            player_y = WINDOW_H - half

        # Footsteps every FOOTSTEP_INTERVAL_MS while moving.
        is_moving: bool = norm > 0.0
        if is_moving:
            footstep_timer_ms += dt_ms
            if footstep_timer_ms >= FOOTSTEP_INTERVAL_MS:
                footstep_timer_ms = 0
                if asset_status.get("footstep"):
                    mixer.play_sfx(cache.get("footstep"))
        else:
            footstep_timer_ms = 0

        # ---- Combat zone transition ------------------------------------
        was_in_combat_zone = is_in_combat_zone
        is_in_combat_zone = COMBAT_ZONE.collidepoint(player_x, player_y)
        if was_in_combat_zone != is_in_combat_zone and music_started:
            e_now, c_now = crossfade.current_levels()
            if is_in_combat_zone:
                crossfade.request_combat(e_now, c_now)
                flash_text = "entered combat zone (music crossfade)"
                flash_t = FLASH_FRAMES
            else:
                crossfade.request_explore(e_now, c_now)
                flash_text = "exited combat zone (music crossfade)"
                flash_t = FLASH_FRAMES

        # ---- Per-frame audio updates -----------------------------------
        mixer.update_duck(dt_ms)
        crossfade.advance(dt_ms)
        if music_started:
            e_lvl, c_lvl = crossfade.current_levels()
            mv: float = mixer.music.effective_volume()
            pygame.mixer.Channel(audio_module.LAYER_EXPLORE_CHANNEL).set_volume(mv * e_lvl)
            pygame.mixer.Channel(audio_module.LAYER_COMBAT_CHANNEL).set_volume(mv * c_lvl)

        if flash_t > 0:
            flash_t -= 1

        # ---- Render -----------------------------------------------------
        screen.fill(BG_COLOUR)

        # Combat zone (drawn first so it sits under the actors).
        pygame.draw.rect(screen, COMBAT_ZONE_FILL, COMBAT_ZONE)
        pygame.draw.rect(screen, COMBAT_ZONE_BORDER, COMBAT_ZONE, width=2)
        zone_label: pygame.Surface = font_sm.render(
            "COMBAT ZONE", True, COMBAT_ZONE_BORDER
        )
        screen.blit(zone_label, (COMBAT_ZONE.x + 12, COMBAT_ZONE.y + 8))

        # Enemies.
        for en in ENEMIES:
            erect: pygame.Rect = pygame.Rect(int(en.x - 12), int(en.y - 12), 24, 24)
            pygame.draw.rect(screen, ENEMY_COLOUR, erect, border_radius=3)

        # NPCs.
        for npc in NPCS:
            nrect: pygame.Rect = pygame.Rect(int(npc.x - 16), int(npc.y - 16), 32, 32)
            pygame.draw.rect(screen, npc.colour, nrect, border_radius=5)
            lbl: pygame.Surface = font_sm.render(npc.name, True, TEXT_COLOUR)
            screen.blit(lbl, lbl.get_rect(midtop=(int(npc.x), int(npc.y) + 20)))
            # Interact ring when in range.
            if distance(player_x, player_y, npc.x, npc.y) <= NPC_INTERACT_RADIUS:
                pygame.draw.circle(
                    screen, FLASH_GREEN,
                    (int(npc.x), int(npc.y)),
                    int(NPC_INTERACT_RADIUS), 1,
                )

        # Player.
        prect: pygame.Rect = pygame.Rect(
            int(player_x - PLAYER_SIZE / 2), int(player_y - PLAYER_SIZE / 2),
            PLAYER_SIZE, PLAYER_SIZE,
        )
        pygame.draw.rect(screen, PLAYER_COLOUR, prect, border_radius=4)

        # HUD.
        zone_text: str = "combat" if is_in_combat_zone else "explore"
        e_lvl_now, c_lvl_now = crossfade.current_levels()
        hud_lines: list[tuple[str, tuple[int, int, int]]] = [
            (f"zone: {zone_text}    music explore: {e_lvl_now:.2f}    "
             f"combat: {c_lvl_now:.2f}",
             TEXT_COLOUR),
            (f"master: {mixer.master.volume:.2f}    music: {mixer.music.volume:.2f}    "
             f"sfx: {mixer.sfx.volume:.2f}    voice: {mixer.voice.volume:.2f}",
             TEXT_COLOUR),
            (f"duck active: {mixer.duck.active}    "
             f"music started: {music_started}    fps: {clock.get_fps():.0f}",
             DIM_COLOUR),
            ("[WASD] move   [E] talk to NPC   [SPACE] attack in zone   [ESC] save+quit",
             DIM_COLOUR),
        ]
        y: int = 8
        for text, colour_each in hud_lines:
            surf: pygame.Surface = font_sm.render(text, True, colour_each)
            screen.blit(surf, (12, y))
            y += 22

        if flash_t > 0:
            flash_surf: pygame.Surface = font_lg.render(flash_text, True, FLASH_GREEN)
            screen.blit(flash_surf, (12, WINDOW_H - 36))

        pygame.display.flip()

    # ---- Persist settings on quit ---------------------------------------
    # Reconstruct the current settings from the live mixer.
    out_settings: audio_module.AudioSettings = audio_module.AudioSettings(
        master_volume=mixer.master.volume,
        music_volume=mixer.music.volume,
        sfx_volume=mixer.sfx.volume,
        voice_volume=mixer.voice.volume,
        music_muted=mixer.music.muted,
        sfx_muted=mixer.sfx.muted,
        voice_muted=mixer.voice.muted,
    )
    audio_module.save_audio_settings(out_settings, SETTINGS_PATH)
    print(f"settings persisted to {SETTINGS_PATH}")

    pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
