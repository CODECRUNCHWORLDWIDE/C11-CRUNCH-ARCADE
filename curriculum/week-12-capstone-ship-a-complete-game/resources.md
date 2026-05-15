# Week 12 — Resources

The capstone week has the largest reading list of the track, partly because every prior week's references are still in scope and partly because shipping a game involves more non-engine knowledge than building one (storefronts, licensing, capture tools, marketing copy). The list below is partitioned: the five **primary** references are the ones you must read this week; the next tier are the ones you will reach for as questions arise; the appendix is the **W1-W12 sidebar wrap-up**, which is the single most valuable index in this folder.

All references are free. No paywalls. No "trial" links. The capstone toolchain is end-to-end zero-dollar.

## Primary references — read these this week

### 1. Godot 4 Export — exporting projects (the canonical export reference)

*Engine maintainers; latest stable; web*

[docs.godotengine.org/en/stable/tutorials/export/exporting_projects.html](https://docs.godotengine.org/en/stable/tutorials/export/exporting_projects.html)

The official engine documentation for taking a `.godot` project and producing a shipped binary. Reads in roughly 30 minutes. Covers: installing export templates, the *Project → Export* dialog, the per-platform presets (Windows Desktop, macOS, Linux/X11, HTML5, Android, iOS), debug vs release builds, embedded vs side-car PCK files, encryption, and signing flags. The page is also the entry point to the per-platform deep dives. Read once on Monday, then revisit Thursday when you actually configure the four presets.

### 2. Godot 4 Export — exporting for the web (the HTML5 deep dive)

*Engine maintainers; latest stable; web*

[docs.godotengine.org/en/stable/tutorials/export/exporting_for_web.html](https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_web.html)

The HTML5-specific page. Why it matters: the web target is the path of least friction to a shipped game, and HTML5 has more browser-specific gotchas than any other target. Covers: the wasm payload, the audio-context-must-resume-on-user-gesture rule, the cross-origin isolation requirements for `SharedArrayBuffer`, the headers itch.io will or will not let you set, and the `gzip`/`brotli` pre-compression workflow that gets your 25 MB wasm down to 8 MB on the wire. Read three times this week — once on Monday, once on Thursday before exporting, once on Saturday before uploading.

### 3. itch.io developer docs — getting started

*itch.io; living document; web*

[itch.io/docs/creators/getting-started](https://itch.io/docs/creators/getting-started)

The store's own onboarding documentation. Covers: creating an account, creating a project page, uploading binaries, configuring platform tags, setting the price (Free, Pay-what-you-want, or Fixed), writing the page copy, adding screenshots, embedding a trailer, configuring downloads-per-platform, and (later) using the *butler* command-line tool for automated updates. The pricing page at [itch.io/docs/creators/pricing](https://itch.io/docs/creators/pricing) and the HTML5 hosting page at [itch.io/docs/creators/html5](https://itch.io/docs/creators/html5) are required adjacent reading. Free. No revenue share on free games. 10% default revenue share on paid games (creator-adjustable, 0-30%).

### 4. OpenGameArt — the free 2D/3D asset library

*OpenGameArt community; living archive; web*

[opengameart.org](https://opengameart.org)

The largest free-licensed game-art library on the public web. CC0, CC-BY, CC-BY-SA, GPL, OGA-BY assets — every page lists the licence. Sprites, tilesets, character animations, UI elements, fonts, music tracks. Search by licence to filter to CC0 if you want zero attribution overhead, or CC-BY to access a wider library at the cost of one credits-section entry per asset. Browse Monday, download Wednesday. The art-bandwidth saver of this week: a CC0 pixel-art sprite sheet that takes 0 minutes to make is the same as a homemade sprite sheet that takes 4 hours to make, but the 0-minute option leaves the 4 hours for design and code.

### 5. Freesound — the CC0/CC-BY sound effects and music archive

*Universitat Pompeu Fabra (the Music Technology Group); living archive; web*

[freesound.org](https://freesound.org)

The Freesound archive. Hundreds of thousands of CC0 and CC-BY sound effects and music loops, every one with a licence shown on the file's page. Sign-up is free and only required for downloads (browsing and previewing is anonymous). The site's filtering by licence is identical to OpenGameArt's: filter to CC0 if you want zero credits overhead, CC-BY if you want a broader catalogue. The "Random sounds" feature is a surprisingly good design prompt — sometimes the sting drives the screen-shake, not the other way around.

## Secondary references — useful as questions arise

### Steam Direct — the official storefront onboarding (future, paid)

*Valve; living document; web*

[partner.steamgames.com/steamdirect](https://partner.steamgames.com/steamdirect)

The Steam Direct fee (one-time $100 per app, refundable after $1,000 in lifetime adjusted gross revenue) is the gateway to a Steam release. Steam's revenue share is 30% reducing to 25% at $10M lifetime gross and 20% at $50M, which is a non-issue at the indie scale and a real number at the AA scale. Steamworks integration (Steam Cloud, achievements, the Build Pipeline, Steam Input, Big Picture, the storefront's tagging system) is a multi-week effort on top of a finished game. Out of scope for week 12; on the roadmap if you decide to commercialise the capstone.

### Apple App Store Connect — iOS / macOS distribution (future, paid)

*Apple; living document; web*

[developer.apple.com/app-store-connect/](https://developer.apple.com/app-store-connect/)

The Apple Developer Program is $99/year. The iOS build pipeline requires Xcode on a Mac, an Apple Developer account, code-signing certificates, provisioning profiles, and TestFlight for beta builds. The revenue share is 15% for the first $1M/year (under the small-business programme) or 30% standard. The macOS App Store is the same toolchain. Out of scope for week 12; the canonical migration path *from* a Godot HTML5 + macOS unsigned build *to* an App Store release is documented in the Godot iOS export docs at [docs.godotengine.org/en/stable/tutorials/export/exporting_for_ios.html](https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_ios.html) and the macOS export docs at [docs.godotengine.org/en/stable/tutorials/export/exporting_for_macos.html](https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_macos.html).

### Google Play Console — Android distribution (future, paid)

*Google; living document; web*

[play.google.com/console](https://play.google.com/console)

A one-time $25 lifetime fee. The Android build pipeline runs through the Godot Android export plus a JDK plus the Android SDK plus a signing keystore. The revenue share is 30% standard, 15% for small developers. Out of scope for week 12; on the roadmap if your game's mechanics are touch-friendly. The Godot Android export docs at [docs.godotengine.org/en/stable/tutorials/export/exporting_for_android.html](https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_android.html) are the canonical reference.

### Creative Commons — the licence taxonomy

*Creative Commons; living document; web*

[creativecommons.org/share-your-work/cclicenses/](https://creativecommons.org/share-your-work/cclicenses/)

The canonical reference for the CC licence family. The five you will encounter on OpenGameArt and Freesound are: **CC0** (no rights reserved, no attribution required, you can do anything), **CC-BY** (attribution required, no other restrictions), **CC-BY-SA** (attribution required, derivatives must be released under CC-BY-SA — *contaminating* in the way GPL is, careful in commercial work), **CC-BY-NC** (attribution required, non-commercial only — *not safe* if you ever charge for the game, even on Steam), **CC-BY-ND** (attribution required, no derivatives — usually means you cannot modify the asset, only redistribute it as-is). For week 12 free-release: CC0 is safest, CC-BY is fine with attribution, the rest need a careful read. Memorise the abbreviations.

### OBS Studio — the free screen-capture tool

*OBS Project; open source; web*

[obsproject.com](https://obsproject.com)

The de-facto free screen recorder for the trailer. macOS, Windows, Linux. Captures a window or a region; encodes to MP4 at 60 fps. Configurable bitrate and resolution. The macOS install asks for *Screen Recording* permission in *System Settings → Privacy*; the Linux install on Wayland needs `pipewire-screen-recorder`. Install Monday; record the trailer Friday.

### Shotcut and DaVinci Resolve (free) — video editors for the trailer

*Meltytech (Shotcut) / Blackmagic Design (DaVinci Resolve free); web*

[shotcut.org](https://shotcut.org) — Shotcut: free, open source, lightweight, sufficient for a 30-second trailer with cuts, titles, and an audio track.

[blackmagicdesign.com/products/davinciresolve](https://blackmagicdesign.com/products/davinciresolve) — DaVinci Resolve free edition: free, closed source, heavier (~3 GB install), supports colour grading and the *Fairlight* audio panel. Overkill for the capstone but the industry standard for a reason; if you want to invest in one editor for the long term, this is the one.

Either is fine for the week-12 trailer. Pick the lighter install if disk space is tight.

### YouTube creator help — upload, unlisted, embed

*Google; living document; web*

[support.google.com/youtube/answer/2657964](https://support.google.com/youtube/answer/2657964) (about visibility settings)

The *Unlisted* visibility setting is the right choice for the trailer: the video is accessible to anyone with the URL but is not surfaced in YouTube's recommendation algorithm and is not indexed in YouTube search. The itch.io page can embed the video via the standard YouTube embed code (paste the video URL into itch.io's *Add trailer* field). When the game's commercial release is ready, flip the visibility to *Public*.

### Ludum Dare, Global Game Jam, js13kGames — the three big free jams

*Ludum Dare:* [ldjam.com](https://ldjam.com) — quarterly (Apr/Aug/Dec), 48-72 hours, free entry, themed.

*Global Game Jam:* [globalgamejam.org](https://globalgamejam.org) — annual (Jan/Feb), 48 hours, free entry, themed, in-person and online.

*js13kGames:* [js13kgames.com](https://js13kgames.com) — annual (Aug-Sep), 13 KB JavaScript max, themed, technically the strictest. Goes via the *js13k* category, not Godot, but the discipline is the same.

If you want a "Week 13" of your own design, entering one of these jams with a stripped-down version of the capstone is the most-recommended path. Free, social, peer-reviewed, and you walk away with a second shipped artefact.

## Books and longer-form reading

These are off-track for a one-week capstone but are the canonical longer reads if you are thinking about the *next* shipped project.

- *The Art of Game Design: A Book of Lenses* — Jesse Schell. The 100+ design lenses are a tool you keep on a shelf forever. Not free, but the lens index is widely paraphrased online if you want a free taste before buying.
- *Designer Notes* podcast — Soren Johnson (designer of Civilization IV, Old World). Interview format. Two-hour episodes with shipped-game designers about why they made the choices they made. Free, episodic, deep.
- *Pirate Software's How I Shipped My Game* talks on YouTube — free, sharp, opinionated, indie-scaled. The single best free crash course on the *business* side of shipping that we know of.
- *Game Developers Conference (GDC) Vault* — free talks at [gdcvault.com](https://gdcvault.com). Filter to *Free* in the sidebar. The yearly Indie Megabooth and Day of the Devs talks are particularly relevant to a week-12 student.

## Sidebar — Weeks 1-12 wrap-up walk-through

Twelve weeks of mini-projects is twelve solved subsystems on your disk. The capstone is the integration test for all of them. The walk-through below is the *retrieval index* — when a capstone-week problem feels unfamiliar, this is where you look.

### Week 1 — The game loop

*The one subsystem you keep:* a `_process(delta)` body that takes `delta` seriously.

The mini-project was a frame-rate-independent moving sprite. The trick is to multiply velocities by `delta` so the same code produces the same on-screen motion at 30 fps and 240 fps. In the capstone, every per-frame system — the enemy movement, the projectile physics, the camera lerp, the screen-shake decay — multiplies by `delta`. If a system in the capstone is frame-rate-dependent, the cure is in the Week 1 mini-project.

### Week 2 — Collisions and physics-lite

*The one subsystem you keep:* an AABB-vs-AABB sweep test that survives high speeds.

The mini-project was the swept-AABB-vs-static-AABB collision response. The Week 2 corner-case bug — a fast-moving projectile tunnels through a thin wall on a 60 fps frame — is the bug you debug *fastest* in the capstone if you remember the swept-test fix. The hit-detection on the capstone's enemies, the wall-clamp on the player, the projectile-vs-enemy test all come from Week 2.

### Week 3 — Game design vocabulary

*The one subsystem you keep:* the verb-goal-obstacle-reward decomposition of any prototype.

The mini-project was a written design statement of a prior week's prototype using the four-vocab framework. In the capstone, the Monday scope sheet *is* the verb-goal-obstacle-reward decomposition. If on Tuesday the playable prototype does not have a *verb* (a thing the player does), a *goal* (a state they are trying to reach), an *obstacle* (a thing standing between them and the goal), and a *reward* (a thing they get on reaching the goal), the design is incomplete and the build will not feel like a game. Week 3 is the rubric you run the Monday scope sheet through.

### Week 4 — Tilemaps and levels

*The one subsystem you keep:* a grid-backed tilemap reader plus an LDtk import path.

The mini-project was a static tilemap level loader with a small editor. Not every capstone needs a tilemap — Pong does not, a single-screen arena shooter does not. If yours does (a platformer, a top-down dungeon crawler, a puzzle game with a level grid), the Week 4 implementation is the one you reach for. The capstone's level designer (you, on Wednesday) is a Week 4 user.

### Week 5 — State machines

*The one subsystem you keep:* the `State` interface and the `StateMachine` autoload.

The mini-project was a finite-state machine driving an enemy AI through *idle → patrol → chase → attack → return*. In the capstone, the *game* itself is a state machine: title-screen → playing → paused → game-over → high-score-entry → title-screen. The Week 5 `StateMachine` autoload is the single class that drives the entire flow. If your capstone has a title screen and an end screen — and it should — the orchestration code is Week 5.

### Week 6 — Animation and juice

*The one subsystem you keep:* squash-and-stretch, screen-shake, hit-pause, particle burst.

The mini-project was the *juice toolbox* — four small effects bolted onto a static prototype. In the capstone, every game-feel decision is a Week 6 call: does the player squash on jump (Week 6 yes), does the screen shake on enemy hit (Week 6 yes), does the game pause for 60 milliseconds on critical hit (Week 6 yes), do particles spray on collectible pickup (Week 6 yes). The toolbox is small and the difference it makes is large.

### Week 7 — Save and load systems (first pass)

*The one subsystem you keep:* a `user://`-rooted JSON loader with a default schema.

The mini-project was a first save system — write the player's name and the level number to `user://save.json`, read it back on launch. In the capstone, the high-score table, the settings panel state, and the unlocked-level flags all use this loader. (The Week 11 *production* version is what you actually use in the capstone; Week 7 is the *first pass* that taught you the API.)

### Week 8 — Sound and music systems

*The one subsystem you keep:* a two-bus audio mixer with ducking and one-shots.

The mini-project was a two-bus audio routing setup: a *Music* bus and an *SFX* bus, with ducking so the music dims when an explosion fires. In the capstone, the title-screen music, the in-game music, the end-screen sting, every one-shot SFX flow through the Week 8 mixer. The mixer is also the single hook for the settings panel's *Music Volume* and *SFX Volume* sliders.

### Week 9 — Multiplayer fundamentals

*The one subsystem you keep:* a `MultiplayerSpawner` plus a `MultiplayerSynchronizer` pair.

The mini-project was a two-cursor demo synced over the LAN. Most capstones do not use Week 9 — single-player ships faster and is the right scope for a one-week build. If yours does (a two-player local versus mode, a co-op survival mode, an online versus mode), Week 9 is the implementation. Local two-player on a shared keyboard is the lowest-friction case; do not reach for online multiplayer in the capstone unless your prior week-9 mini-project already shipped working.

### Week 10 — Shaders and visual effects

*The one subsystem you keep:* hit-flash, dissolve transition, screen-shake post-process.

The mini-project was the polish tripod — three fragment shaders bolted onto a Week 9 prototype. In the capstone, the hit-flash shader is on every enemy. The dissolve transition is on every screen change. The screen-shake post-process rides on top of the Week 6 transform-based screen-shake, doubling the felt impact. Three `.gdshader` files; the difference is night and day.

### Week 11 — Save systems and serialization (production)

*The one subsystem you keep:* temp-file-plus-rename, SHA-256 integrity, version migration.

The mini-project was the *production* save system: atomic writes, integrity checks, backup rotation, schema versioning, Pydantic validation on the tools side. In the capstone, this is the loader on the high-score table — because the high-score table is the one save the player will *notice* if it gets corrupted. Use the Week 11 manager, not the Week 7 first pass. Namespace the path with a per-game prefix.

### Week 12 — Capstone

*The one subsystem you keep:* the shipped build with your name on the itch.io page.

Twelve weeks. Twelve subsystems. One shipped game. The capstone is not a new subsystem; it is the integration test that proves you can compose the eleven prior subsystems into something a stranger can download, launch, and play to completion. The artefact is public. The artefact is permanent. The artefact is the one a future employer reads first.
