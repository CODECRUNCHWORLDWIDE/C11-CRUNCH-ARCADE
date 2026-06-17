# Week 8 — Resources

Every resource on this page is **free** and **publicly accessible**. No paywalled books, no proprietary PDFs. If a link breaks, please open an issue.

## Required reading and watching (work it into your week)

- **Pygame — *pygame.mixer* documentation (free).** The canonical reference for everything in this week's exercises. Read the top of the page once for the module overview, then `Sound`, `Channel`, and the `music` sub-page in detail. The whole reference is short — ~30 minutes — and is the single most useful pre-read for the week:
  <https://www.pygame.org/docs/ref/mixer.html>
- **Pygame — *pygame.mixer.music* sub-page (free).** The streaming-music API. Distinct from `pygame.mixer.Sound` and worth reading separately. The `play`, `queue`, `set_volume`, `fadeout`, and the volume-vs-position semantics are the four things you will use most:
  <https://www.pygame.org/docs/ref/music.html>
- **Godot — *AudioServer* class reference (free).** The Godot 4.x audio engine's central singleton. Read once to recognise the API names you will meet in Week 9. The bus index conventions and `set_bus_volume_db` / `set_bus_effect_enabled` are the load-bearing methods:
  <https://docs.godotengine.org/en/stable/classes/class_audioserver.html>
- **Godot — *Audio buses* tutorial (free).** The editor-driven introduction to the bus tree. Reading this even without GDScript context gives you a visual map of the same abstractions we implement by hand in Pygame:
  <https://docs.godotengine.org/en/stable/tutorials/audio/audio_buses.html>
- **Audacity manual — *Edit menu and zero-crossings* (free).** The Z-shortcut, the cross-fade tool, and the export-as-OGG flow are the three Audacity techniques you will use this week. Bookmark this page:
  <https://manual.audacityteam.org/man/edit_menu.html>

## Pygame audio (free)

- **`pygame.mixer` reference.** Mixer module, `pre_init`, `init`, channel allocation, fadeout, `get_busy`:
  <https://www.pygame.org/docs/ref/mixer.html>
- **`pygame.mixer.Sound` class.** Decoded sounds: `play`, `stop`, `set_volume`, `get_length`. Note the `set_volume(left, right)` two-arg form for stereo panning:
  <https://www.pygame.org/docs/ref/mixer.html#pygame.mixer.Sound>
- **`pygame.mixer.Channel` class.** Channel objects, `queue`, `play`, `fadeout`, `get_endevent`. The `endevent` is how you trigger logic when a clip finishes:
  <https://www.pygame.org/docs/ref/mixer.html#pygame.mixer.Channel>
- **`pygame.mixer.music` streaming.** The dedicated music streaming module: `load`, `play`, `set_volume`, `fadeout`, `queue`. Stream-from-disk, not load-to-memory:
  <https://www.pygame.org/docs/ref/music.html>
- **`pygame.sndarray` reference.** Read or generate audio as `numpy` arrays. Used in Exercise 1 to synthesise test tones without shipping asset files:
  <https://www.pygame.org/docs/ref/sndarray.html>
- **`pygame.event` reference.** `USEREVENT` and custom event types are how the duck system signals "dialogue started" and "dialogue ended" from one part of the codebase to another:
  <https://www.pygame.org/docs/ref/event.html>

## Godot 4.x audio (free; Week 9 bridge)

We mention Godot to set up Week 9. The algorithms in this week's lectures port verbatim. Skim now; revisit in Week 9.

- **Godot — *AudioServer* class reference.** The central singleton. `bus_count`, `set_bus_volume_db`, `get_bus_index(name)`, `add_bus_effect`:
  <https://docs.godotengine.org/en/stable/classes/class_audioserver.html>
- **Godot — *Audio buses* tutorial.** Editor-driven walkthrough. The same three-bus tree we build in Pygame is one panel here:
  <https://docs.godotengine.org/en/stable/tutorials/audio/audio_buses.html>
- **Godot — *AudioStreamPlayer* class.** The non-spatial player. Use for music, UI sounds, dialogue:
  <https://docs.godotengine.org/en/stable/classes/class_audiostreamplayer.html>
- **Godot — *AudioStreamPlayer2D* class.** The 2D spatial player. Distance attenuation, panning, and `max_distance` all built in:
  <https://docs.godotengine.org/en/stable/classes/class_audiostreamplayer2d.html>
- **Godot — *AudioStreamPlayer3D* class.** The 3D spatial player. We mention it for completeness; C11 is 2D and you will not use it this semester:
  <https://docs.godotengine.org/en/stable/classes/class_audiostreamplayer3d.html>
- **Godot — *AudioEffect* class index.** The list of built-in effects (reverb, chorus, compressor, EQ, limiter, panner). Each is one node insert in the editor:
  <https://docs.godotengine.org/en/stable/classes/class_audioeffect.html>
- **Godot — *Sync with audio* tutorial.** How to align gameplay events to the music timeline (e.g. rhythm games). Worth a skim; out of scope for this week's mini-project:
  <https://docs.godotengine.org/en/stable/tutorials/audio/sync_with_audio.html>

## Audio engineering fundamentals (free)

- **Wikipedia — *Sample rate*.** A clean two-page primer. The Nyquist theorem and why 44100 Hz is "good enough" for human hearing:
  <https://en.wikipedia.org/wiki/Sampling_(signal_processing)>
- **Wikipedia — *Bit depth*.** Why 16-bit signed is the consumer audio default and what 24-bit and 32-bit float buy you in professional contexts:
  <https://en.wikipedia.org/wiki/Audio_bit_depth>
- **Wikipedia — *Decibel*.** The dB primer. The single sentence to remember: every -6 dB is half the linear amplitude. Every +20 dB is ten times. Skim the "Field versus power quantities" section once:
  <https://en.wikipedia.org/wiki/Decibel>
- **Wikipedia — *Audio compression (data)*.** The general topic of lossless vs lossy audio compression. OGG Vorbis, MP3, AAC are all lossy; FLAC and ALAC are lossless; WAV is uncompressed:
  <https://en.wikipedia.org/wiki/Audio_compression_(data)>
- **Wikipedia — *Vorbis*.** The OGG Vorbis spec at a high level. Patent-free, open container, supported natively by `pygame.mixer.music`:
  <https://en.wikipedia.org/wiki/Vorbis>
- **Wikipedia — *Sidechain compression*.** The audio-engineering term for what we call "ducking." Reading the dance-music context makes the game-audio use case click:
  <https://en.wikipedia.org/wiki/Dynamic_range_compression#Side-chaining>

## Audacity (the free DAW you will use)

- **Audacity — official site.** Free, open-source, cross-platform. Download once:
  <https://www.audacityteam.org/>
- **Audacity manual — Edit menu.** The `Z` shortcut for snap-to-zero-crossing lives here, along with the cut/copy/paste/cross-fade tools:
  <https://manual.audacityteam.org/man/edit_menu.html>
- **Audacity manual — Effect menu.** The Fade In / Fade Out / Cross Fade Tracks effects. Cross Fade Tracks is the one that authors a seamless loop seam:
  <https://manual.audacityteam.org/man/effect_menu.html>
- **Audacity manual — Exporting audio.** How to export as OGG Vorbis at 44.1 kHz / quality 5 (~128 kbps). The default export settings are wrong for game audio; the manual page has the right ones:
  <https://manual.audacityteam.org/man/exporting_audio_files.html>
- **Audacity manual — Spectrogram view.** Switch the track view to spectrogram to visually confirm a loop seam has no discontinuity. The seam shows as a vertical line if it is wrong; smooth gradient if it is right:
  <https://manual.audacityteam.org/man/spectrogram_view.html>

## Free CC-licensed asset sources

The whole week's audio is free under Creative Commons. Two sources cover ~95% of what an indie needs.

- **Freesound.** Community-uploaded SFX library. Sign up free; download as WAV or OGG. Filter by licence — CC0 means no attribution required, CC-BY 3.0 / 4.0 means a credit line is required. Tag-based search is excellent:
  <https://freesound.org/>
- **OpenGameArt.** Community-uploaded game-assets library — sprites, music loops, SFX packs, fonts. Filter by audio. Many entries are CC0; a few are CC-BY or GPL. Read the licence on the asset page before downloading:
  <https://opengameart.org/>
- **Kenney — audio packs (CC0).** Same Kenney whose sprites you have used since Week 4. The audio packs (interface, impact, RPG) are CC0 and shippable without attribution. Reuse the *Interface Sounds* pack from Week 6:
  <https://kenney.nl/assets/category:Audio>
- **Free Music Archive.** A music-focused free archive. Music for trailers, menus, and overworlds. CC licences vary per track — read the page:
  <https://freemusicarchive.org/>
- **Incompetech (Kevin MacLeod).** CC-BY-licensed royalty-free music. The MacLeod attribution string is standard and worth memorising. Many of the loops are already loop-clean:
  <https://incompetech.com/>

### Creative Commons licences (free reading)

- **Creative Commons — about CC0.** "No rights reserved." You can do anything; attribution is courtesy not requirement:
  <https://creativecommons.org/publicdomain/zero/1.0/>
- **Creative Commons — about CC-BY.** Attribution required. Specifies what an attribution string must include:
  <https://creativecommons.org/licenses/by/4.0/>
- **Creative Commons — about CC-BY-SA.** Attribution plus share-alike. If your game uses a CC-BY-SA asset, *your derivative work* must be CC-BY-SA. This is incompatible with most commercial game licences. We avoid CC-BY-SA for game audio for that reason:
  <https://creativecommons.org/licenses/by-sa/4.0/>
- **Creative Commons — about CC-BY-NC.** Non-commercial. Cannot ship in a commercial game. Avoid:
  <https://creativecommons.org/licenses/by-nc/4.0/>

## Talks and long-form (free)

- **Marshall McGee — *Sound Design for Games* (YouTube channel, free).** McGee's analysis videos on *Hades*, *Subnautica*, *Hollow Knight*, and others are exemplary studies in how shipping games actually mix. Watch in your self-study hours:
  <https://www.youtube.com/@MarshallMcGee>
- **Game Audio Strategy — *Reactive Music* (YouTube, free).** A short series on layered and reactive music systems. The "stems crossfade on intensity" pattern in Exercise 4 comes from here:
  <https://www.youtube.com/results?search_query=reactive+music+game+audio>
- **Akash Thakkar — *How to make game music* (YouTube, free).** A composer's-eye view of writing for games. Useful counterweight to the programmer-centric view of this week:
  <https://www.youtube.com/@AkashThakkarMusic>
- **GDC Vault — free sessions on audio.** Search the GDC Vault for "game audio." Several free sessions on mixing, voice direction, and procedural audio. Look specifically for sessions tagged "Free":
  <https://www.gdcvault.com/>

## Reference projects with public audio (free reading)

- **Celeste — source-available repo.** Celeste's audio implementation in C# / FMOD. Useful as a reference for "what a shipped indie's audio code looks like":
  <https://github.com/NoelFB/Celeste>
- **Mini Mike's Metro Minis — free Pygame game with full audio.** A small open-source Pygame title with a working music system. Browse the audio module to see how the patterns from this week look at production scale:
  <https://github.com/scriptisaboss/MiniMikesMetroMinis>

## Free Python packages we use this week

Install in your virtual environment:

```bash
pip install pygame numpy
```

- **pygame (>= 2.5).** The game engine and its `pygame.mixer` audio subsystem. Free, open-source, LGPL:
  <https://www.pygame.org/>
- **numpy (>= 1.24).** Used in Exercise 1 to synthesise test tones via `pygame.sndarray`. The mini-project does not require numpy at runtime — only the test-tone exercise:
  <https://numpy.org/>

Stdlib only (no install needed):

- `json`, `os`, `pathlib`, `dataclasses`, `math`, `time`, `enum`.

## Asset packs (for the mini-project)

- **Kenney — *Interface Sounds* (CC0).** Already in your repo from Week 6. Reuse the "confirm" and "cancel" beeps for the settings menu. ~150 KB:
  <https://kenney.nl/assets/interface-sounds>
- **Kenney — *Impact Sounds* (CC0).** Crunchy hits and clanks for the combat zone. ~500 KB:
  <https://kenney.nl/assets/impact-sounds>
- **Kenney — *RPG Audio* (CC0).** Inventory pickups, level-up jingles, magic effects. ~3 MB:
  <https://kenney.nl/assets/rpg-audio>
- **Freesound — search "footstep grass loop" (CC0 filter on).** The footstep clip for the mini-project player. Download as OGG; trim to ~250 ms in Audacity:
  <https://freesound.org/search/?q=footstep+grass+loop&f=license%3A%22Creative+Commons+0%22>
- **OpenGameArt — search "loop ambient 60 bpm" (CC-BY filter on).** A loop-clean ambient track for the explore layer of the mini-project. ~3 MB OGG typical:
  <https://opengameart.org/art-search?keys=loop+ambient&field_art_licenses_tid%5B%5D=2>

All Kenney audio packs are CC0 (public domain). Freesound and OpenGameArt clips vary per item — read the licence on each page.

## What you will *not* need this week

- A DAW with multitrack mixing (Reaper, Ableton, Logic). Audacity is enough for loop authoring and the few edits this week demands.
- A commercial sound-library (Soundsnap, Pro Sound Effects). Freesound and OpenGameArt cover everything.
- FMOD or Wwise. Both are powerful middleware engines used by professional studios. Out of scope for this course; the equivalent abstractions are in Pygame's mixer and Godot's AudioServer.
- A USB audio interface or studio monitors. Headphones are mandatory; a quality pair is recommended. Laptop speakers will hide the mixing bugs this week is teaching you to find.

---

*Bookmark this page. Audio resources accumulate; the Freesound and OpenGameArt search filters alone will save you hours by Week 11.*
