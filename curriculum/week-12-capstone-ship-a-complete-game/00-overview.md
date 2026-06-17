# Week 12 — Capstone: Ship a Complete Arcade Game

Eleven weeks ago you opened a blank Godot project and an editor full of nodes whose names meant nothing yet. You wrote a `_process(delta)` function, made a sprite move, and were told that the rectangle on screen was a game loop. You believed it on faith. Now, twelve weeks later, the rectangle moves because a fixed-timestep integration in Week 1 told it to; it stops at walls because the collision math in Week 2 said so; it has hit-feedback because the screen-shake shader in Week 10 multiplies UV offsets by a sine of time; it remembers the player's name across sessions because the atomic-write loader in Week 11 promoted `save.tmp` to `save.latest` under SHA-256 verification on Sunday at 22:14 last week. The toolbox is real. The toolbox is yours. This week you assemble the toolbox into a single shipped game and put it on the public internet under your name.

The deliverable is not a prototype. It is a *complete* arcade game — by which we mean a game with a title screen, an end screen, a settings panel, a high-score table, one playable level (or one playable run, for roguelikes), a credits roll, an audio mix, and a downloadable build on a public storefront. The storefront is **itch.io**. The build is **HTML5 + Windows + macOS + Linux**, exported from Godot 4.x. The marketing surface is one **screenshot strip**, one **30-second trailer**, and one **page of copy** written in the second person. The page costs zero dollars to publish. The store takes zero dollars in revenue share unless you choose to sell the game (free is default and recommended for a first ship). The whole pipeline — engine, store, asset sources — is free to use this week and free to use for the rest of your career as an indie developer.

The single most consequential decision of the week is **scope**. The students who finish this week are not the ones with the most ambitious concepts; they are the ones whose Monday scope statement was small enough that Saturday's "polish pass" was actually polish, not a rewrite. The mini-project README enforces this with a hard upper bound: *one screen, one mechanic, three minutes of playtime, two days of art budget.* The students who shipped a 90-second Pong-with-screen-shake and uploaded it to itch.io by Saturday night will be ahead of the students who began a JRPG on Monday and have a title screen by Sunday. Be the first kind of student. Lecture 1 makes the case in detail.

The single most cited free reference this week is the **Godot 4 export documentation** at [docs.godotengine.org/en/stable/tutorials/export/exporting_projects.html](https://docs.godotengine.org/en/stable/tutorials/export/exporting_projects.html) — the canonical, engine-maintained guide to taking your project from a `.godot` folder to a `.exe`, a `.dmg`, a `.x86_64` Linux binary, and an `index.html` web export. The HTML5-specific page at [docs.godotengine.org/en/stable/tutorials/export/exporting_for_web.html](https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_web.html) is the one you will read three times this week because the web target is the path of least friction to a shipped game. The **itch.io developer docs** at [itch.io/docs/creators/getting-started](https://itch.io/docs/creators/getting-started) cover the upload, the page customisation, the pricing model (free or pay-what-you-want at zero revenue share), and the per-platform binary upload. The **OpenGameArt** library at [opengameart.org](https://opengameart.org) and the **Freesound** archive at [freesound.org](https://freesound.org) are the two free-asset sources you draw from when your own art bandwidth runs out — CC0 and CC-BY pixel art, sound effects, music, and palettes, all attributable and all free. Five free references, all linked in `resources.md`, all cited in the lectures.

This week is the wrap-up of the track. The sidebar in `resources.md` walks all twelve weeks in order and reminds you which subsystem came from where. Treat that sidebar as a personal index — when a capstone-week problem looks unfamiliar, it almost always maps to a prior week, and the prior week's mini-project has the solved version sitting in a folder on your disk. Twelve weeks of mini-projects is now twelve solved reference implementations. The capstone is the integration test for all of them.

## Learning objectives

By the end of this week, you will be able to:

- **Scope** a one-week arcade game so that Monday's design statement and Sunday's shipped build are recognisably the same project. The discipline is to write the *one-sentence pitch* on Monday morning, the *Monday scope sheet* by Monday evening, and then *refuse* every Wednesday-afternoon idea that does not fit the pitch. The graveyard of indie games is paved with mid-week feature creep; the discipline is a learnt habit and this week is where you learn it. The mini-project enforces it with a written scope-cut log.
- **Assemble** a complete game out of the subsystems built in Weeks 1-11. The game loop comes from Week 1. The collision detection comes from Week 2. The design vocabulary (verb, goal, obstacle, reward) comes from Week 3. The tilemap-or-grid comes from Week 4. The state machine that drives title-screen → playing → game-over → title-screen comes from Week 5. The juice (squash-and-stretch, particle bursts, screen-shake) comes from Week 6. The save-the-high-score code comes from Week 7. The audio mix (one-shots, ducking, background music) comes from Week 8. The optional two-player local mode comes from Week 9 (or the optional one-player-against-a-friend-on-the-network mode if you are ambitious). The shader-driven hit flash and the menu-transition shader come from Week 10. The atomic-write and SHA-256 verification on the high-score file come from Week 11. The capstone is *which* of those subsystems your specific game needs and *which* it does not — a Pong clone needs Week 2 and Week 6 and Week 8 and Week 11; it does not need Week 4 or Week 9. The integration is the skill.
- **Export** a Godot 4 project to four platforms using the official export-template workflow. You will install the export templates from the *Editor → Manage Export Templates* dialog, configure four presets in *Project → Export* (HTML5, Windows Desktop, macOS, Linux/X11), and produce four shipped binaries. The Windows binary will be a single `.exe` plus a `.pck`. The macOS binary will be a `.app` bundle (unsigned, with a documented gatekeeper-bypass instruction for the page). The Linux binary will be an `.x86_64` ELF. The HTML5 binary will be a folder containing `index.html`, a `.wasm`, a `.js`, and a `.pck`, ready to upload as a zip to itch.io. You will know which targets need code-signing later (macOS, Windows) and why you skip that step in week 12 (signing costs money; signing is for the *commercial* release).
- **Publish** an itch.io page that does not look like a Sunday-night cram session. The page has a 240-pixel-tall banner image, a 32-pixel-square thumbnail, three to five screenshots, an embedded 30-second trailer (uploaded to YouTube or Vimeo first; itch.io accepts the embed code), three paragraphs of copy in the second person ("you play the part of..."), a controls section, a credits section that names every free-asset source you used, and a download button per platform. You will set the price to **Free** (or **Name your own price** with a zero minimum). You will set the visibility to **Public**. You will share the URL with the cohort. The page is the artefact future employers will look at.
- **Record** a 30-second trailer that is *not* a screen capture of you playing the entire level. The trailer is six 5-second beats: hook → mechanic intro → first conflict → escalation → climax → title card with URL. You will use free tools — OBS for capture, Shotcut or DaVinci Resolve free edition for editing, a Freesound CC0 sting for audio. The trailer is uploaded to YouTube as Unlisted (so the itch.io embed works without making it Public on YouTube's algorithm). The discipline is the same as scoping: a 30-second trailer beats a 3-minute trailer because the 30-second trailer gets watched all the way through.
- **Source** every asset from a CC0 or CC-BY library, and **attribute** every asset in a credits section. OpenGameArt and Freesound are the two libraries this week. Both list the licence on every asset's page. You will keep a `CREDITS.md` file in the project repo that names every asset by URL, lists the author, lists the licence, and (for CC-BY assets) acknowledges the author by their preferred name. The credits file is mirrored into the in-game credits screen and into the itch.io page's footer. Attribution is a contract; CC-BY is not "free as in nothing required" — it is "free as in attribution required." The students who blow off attribution this week are the students who get a polite-but-firm DMCA email next year.
- **Survey** the *future* paid storefronts at the conceptual level. **Steam Direct** charges a one-time $100 per app, refundable if the app meets a small lifetime revenue floor, and the Steam revenue share is 30% reducing to 25% then 20% at sales tiers. The Steam release adds 30% revenue and 95% of the audience compared to itch.io alone, but it adds a Steamworks integration cost (Steam Cloud, Steam achievements, the storefront's Build Pipeline) that is a multi-week effort on top of a finished game. **App Store Connect** for iOS and the **Google Play Console** for Android each charge $99/year and $25 lifetime respectively, plus a 15-30% revenue share, plus a per-platform native-build pipeline; both are wildly out of scope for week 12. The point of the survey is not to ship to those stores this week; it is to know what the migration path *from* a free itch.io ship *to* a paid commercial ship will look like when you decide to take it.
- **Track-wrap** by re-walking the twelve weeks and naming, for each week, the *one subsystem* that ended up in the capstone build. The wrap is an explicit ritual — there is a sidebar in `resources.md` and a section in `homework.md` that asks you to write the twelve-line index. Students who complete the index in their own words will retrieve the toolbox faster on every future project. Students who skip it will eventually relearn Week 4's tilemap from scratch because they forgot they had a working implementation in a folder on their disk.
- **Cite** the five free references — *Godot export docs*, *Godot HTML5 export*, *itch.io developer docs*, *OpenGameArt*, *Freesound* — and explain what each one was for in your specific shipped build. The citations go in `CREDITS.md` and in the itch.io page's footer.

## Prerequisites

This week assumes you have completed **Weeks 1-11**. Specifically:

- You have a working Godot 4.x install (4.2 or newer recommended; 4.3 is the version the export-docs lectures pin against). You have the Godot binary on your PATH or shortcutted to your dock so you can launch it without thinking about it.
- You have a working installation of **OBS Studio** (free, [obsproject.com](https://obsproject.com)) for screen capture. The cohort lab has it pre-installed; if you are on your own machine, install it Monday morning.
- You have a free **itch.io account**. Create one at [itch.io/register](https://itch.io/register) by Monday end-of-day. The upload pipeline requires an account; the account is free; the account-creation step takes 90 seconds.
- You have a free **YouTube account** (or Vimeo) where you can upload the 30-second trailer as Unlisted. Vimeo's free tier has a weekly upload cap; YouTube's free tier does not. We recommend YouTube unless you have a specific reason to prefer Vimeo.
- You have **at least one mini-project from Weeks 1-11** that you are willing to evolve into the capstone. The Week 6 (juice), Week 7 (save), Week 8 (audio), or Week 10 (shader-polish) builds are the most common starting points because they already have a playable loop. You are not required to start from a prior week; starting from a blank project is acceptable if your scope is small.
- You are comfortable enough with GDScript to read and modify all eleven prior weeks' mini-projects, and you can locate any subsystem in those projects within thirty seconds. Twelve weeks of code is now sitting on your disk; the capstone leans on that fact.
- You have read this README, the `resources.md` sidebar walk-through of Weeks 1-12, and the mini-project README before Monday lunch. The mini-project README is the longest single document of the week; it is the spec.

If any of those are shaky, fix them first. The capstone week does not have slack to debug an export-templates install on Friday.

## Topics covered

Lecture 1 — Scope, the pitch, and the Monday scope sheet:

- The one-sentence pitch. *"You are a frog. You cross a road. Cars get faster."* That is a pitch. *"You play a deep narrative roguelike about loss and redemption in a procedurally generated city."* That is not a pitch — it is a *theme statement*, and theme statements do not ship in a week. We will write twenty pitches together on Monday morning and then we will pick one.
- The Monday scope sheet. A one-page document with: the pitch (one sentence), the verb (the player's action), the goal (the win condition), the obstacle (the loss condition), the loop length (in seconds), the screen count (one is best, three is acceptable, five is too many), and the asset list. Every Monday scope sheet that omits the asset list ends with a Friday-night frantic search for a sprite of a frog. We will do the list on Monday.
- The cuts log. Every time you decide *not* to add a feature this week, you write the feature on the cuts log with a one-sentence reason. By Sunday the cuts log is two pages long and the build still works. Without the cuts log, the same two pages of features got added on Wednesday afternoon and the build is broken on Saturday morning.
- The Tuesday "playable prototype" gate. By Tuesday end-of-day, the project must be a playable prototype — ugly art, no audio, no polish, but the verb works, the goal works, the obstacle works. If Tuesday end-of-day is not playable, the project is rescoped, not pushed. The week's calendar does not survive a Wednesday-morning "still not playable" state.

Lecture 2 — Export, build, and the four targets:

- Installing export templates. *Editor → Manage Export Templates → Download and Install*. The dialog downloads ~1.5 GB of platform-specific runtimes. Do this Monday. Do it once. Do it before you need it.
- The export-presets file (`export_presets.cfg`). Godot writes it for you when you add a preset. Commit it to git. Without it, the next time you open the project on another machine you redo every preset by hand.
- The HTML5 target. Web is the path of least friction — no installer, no gatekeeper, no antivirus warning. The downside is that mobile Safari is sometimes finicky, that the wasm payload is 20-30 MB unstripped, and that audio playback on iOS Safari requires a user-gesture before the first `AudioContext.resume()`. We use HTML5 as the *primary* shipped target and the desktop targets as fall-backs.
- The Windows target. Single `.exe` plus `.pck`. Unsigned. Windows SmartScreen will warn the user on first launch; we add a one-line note to the itch.io page explaining why and how to bypass.
- The macOS target. A `.app` bundle, unsigned, in a zip. On Apple Silicon and Intel both, Gatekeeper will refuse to open an unsigned `.app` from the Internet. The bypass is `xattr -dr com.apple.quarantine MyGame.app` from Terminal, or *right-click → Open* in Finder. We add the instruction to the page.
- The Linux/X11 target. An `.x86_64` ELF, executable bit set. On most distributions, double-click works; on others, the user runs `chmod +x MyGame.x86_64 && ./MyGame.x86_64` from a terminal. Add the note.
- The future paid targets. Steam Direct ($100 one-time) is the next storefront most students will graduate to. iOS and Android are further out and require platform-specific build pipelines (Xcode for iOS, Android Studio for Android). We do not ship to either this week; we know they exist.

Lecture 3 — The itch.io page, the trailer, and the credits:

- The itch.io page anatomy. Banner (920x480 recommended), thumbnail (315x250), three to five screenshots, an embedded 30-second trailer, three paragraphs of copy, controls, credits. The page is the artefact that gets read; the binary is what gets downloaded. We spend Friday on the page itself.
- Pricing on itch.io. *Free* (the default and the recommendation for a first ship) or *Pay what you want, minimum $0* (which lets supporters tip but does not gate the download). itch.io's revenue share on paid sales is *adjustable by the creator* at 0-30%, with a default of 10%. Free downloads cost the creator nothing. We ship Free this week.
- The 30-second trailer. Six 5-second beats. Hook (the verb in action), mechanic intro (what the player does), first conflict (the obstacle appears), escalation (more obstacles, faster), climax (a peak moment), title card (the game's name and the itch.io URL). The audio is one Freesound CC0 sting (or a CC-BY track with attribution in the description), not a copyrighted soundtrack. The trailer is uploaded as YouTube *Unlisted*, the embed code is pasted into the itch.io page.
- Credits and attribution. Every CC-BY asset *must* name the author. Every CC0 asset *should* still be acknowledged — it is courtesy. The credits file in the repo is the source of truth; the in-game credits screen and the itch.io credits section are mirrors. We will write the credits file Friday afternoon and we will not skip it.
- The post-ship checklist. After upload: test the download from a fresh browser (incognito mode). Test the HTML5 build in three browsers (Chrome, Firefox, Safari). Click your own download button and verify the binary launches. Update the page if anything is broken. Tweet the URL or post it to the cohort Discord with a one-sentence pitch.

## Weekly schedule

The schedule below adds up to approximately **38 hours** — the heaviest week of the track. The capstone is the integration test for everything; expect it to feel longer than a normal week. Treat the schedule as a target. The Sunday "ship" deadline is the only firm one.

| Day       | Focus                                                | Lectures | Exercises | Challenges | Quiz/Read | Homework | Mini-Project | Self-Study | Daily Total |
|-----------|------------------------------------------------------|---------:|----------:|-----------:|----------:|---------:|-------------:|-----------:|------------:|
| Monday    | Lecture 1 + the Monday scope sheet + asset list      |    2h    |    1.5h   |     0h     |    0.5h   |   1h     |     1h       |    0.5h    |     6.5h    |
| Tuesday   | Playable prototype gate. Verb + goal + obstacle live.|    0h    |    1h     |     0h     |    0.5h   |   1h     |     4h       |    0h      |     6.5h    |
| Wednesday | Art pass + audio pass. Subsystems wired in.          |    0h    |    1h     |     0.5h   |    0.5h   |   1h     |     3.5h     |    0.5h    |     7h      |
| Thursday  | Lecture 2 + four-platform export. Polish.            |    2h    |    1h     |     0.5h   |    0.5h   |   0.5h   |     2.5h     |    0h      |     7h      |
| Friday    | Lecture 3 + itch.io page + 30s trailer.              |    2h    |    1h     |     1h     |    0.5h   |   0.5h   |     2h       |    0.5h    |     7.5h    |
| Saturday  | Mini-project — final QA pass + upload to itch.io.    |    0h    |    0h     |     0h     |    0h     |   0h     |     4h       |    0.5h    |     4.5h    |
| Sunday    | Mini-project recording + final exam + write-up + retrospective. |    0h    |    0h     |     0h     |    1h     |   0.5h   |     1.5h     |    0h      |     3h      |
| **Total** |                                                      | **6h**   | **5.5h**  | **2h**     | **3.5h**  | **4.5h** | **18.5h**    | **2h**     | **42h**     |

An overshoot is expected this week. Plan for it; do not panic over it. The mini-project alone is the single biggest line item of the entire track.

## Files in this folder

| File / Folder                                              | What it is                                                                               |
|------------------------------------------------------------|------------------------------------------------------------------------------------------|
| `README.md`                                                | This file. The week's contract.                                                          |
| `resources.md`                                             | Annotated reading list. Godot export docs, itch.io developer docs, OpenGameArt, Freesound. Plus the W1-W12 sidebar wrap-up. |
| `lecture-notes/01-scope-the-pitch-and-the-monday-scope-sheet.md` | Scope, the one-sentence pitch, the asset list, the cuts log, the Tuesday playable gate. |
| `lecture-notes/02-export-build-and-the-four-targets.md`    | Installing export templates, HTML5 + Windows + macOS + Linux presets, the future paid targets. |
| `lecture-notes/03-the-itch-page-the-trailer-and-the-credits.md` | Page anatomy, pricing, the 30-second trailer, CC0/CC-BY attribution, the post-ship checklist. |
| `exercises/exercise-01-pitch-and-scope-sheet.py`           | Validate a Monday scope sheet against a small schema. Reject malformed sheets.           |
| `exercises/exercise-02-asset-license-audit.py`             | Parse a `CREDITS.md`, check every asset has a licence and (if CC-BY) an author.          |
| `exercises/exercise-03-itch-page-validator.py`             | Validate a `page.md` against the itch.io page checklist. Banner, thumb, screenshots, trailer, controls, credits. |
| `exercises/exercise-04-export-config-check.py`             | Parse a Godot `export_presets.cfg` and verify all four targets are present.              |
| `exercises/exercise-05-credit-line-generator.gd`           | A small GDScript helper that loads `CREDITS.md` at runtime and renders the in-game credits roll. |
| `exercises/SOLUTIONS.md`                                   | Walk-through of every exercise.                                                          |
| `challenges/challenge-01-trailer-storyboard.md`            | Stretch: storyboard a 30-second trailer for a hypothetical game in six 5-second beats.   |
| `challenges/challenge-02-steam-direct-migration-plan.md`   | Stretch: write a one-page migration plan from a shipped itch.io build to a Steam Direct release. |
| `quiz.md`                                                  | The final exam — 30 questions covering Weeks 1-12.                                       |
| `homework.md`                                              | The week's structured homework. Three problems plus the W1-W12 retrospective.            |
| `mini-project/README.md`                                   | The capstone spec — full game design + scope advice + itch.io upload checklist.          |
| `mini-project/scope_sheet_template.md`                     | The blank Monday scope sheet template you fill in.                                       |
| `mini-project/credits_template.md`                         | The blank `CREDITS.md` template you fill in.                                             |
| `mini-project/itch_page_template.md`                       | The blank `page.md` template you fill in then paste into the itch.io editor.             |
| `mini-project/post_ship_checklist.md`                      | The post-upload QA checklist.                                                            |

## How to run any Python file in this folder

```bash
python3 -m venv venv
source venv/bin/activate
pip install pyyaml
cd exercises
python3 exercise-01-pitch-and-scope-sheet.py
```

Every `.py` file in this folder is independently executable. None imports another exercise. Each prints a small report of what it did and a final `OK` line on success. Only `exercise-02-asset-license-audit.py` and `exercise-03-itch-page-validator.py` need `pyyaml`; the others are pure standard library.

## How to run the GDScript exercise

1. Open Godot 4.2+ (or newer).
2. Create a new 2D scene with a `Node` root.
3. Attach `exercises/exercise-05-credit-line-generator.gd` to the root node.
4. Place a sample `CREDITS.md` in the project root.
5. Run the scene. Watch the *Output* tab for the rendered credits roll.

## Grading

| Component                       | Weight |
|---------------------------------|-------:|
| Final exam (30 questions)       |   10%  |
| Homework (3 problems + retro)   |   15%  |
| Exercises (5 files)             |   15%  |
| Challenges (2 files)            |   10%  |
| Mini-project (shipped on itch.io) |   50%  |
| **Total**                       | **100%** |

A pass is 70%. The mini-project is the single largest weight of any week in the track. A live, public itch.io page with a downloadable build, a 30-second trailer, three or more screenshots, and a credits section with all assets attributed is the deliverable that counts. A private link or a "still in progress" page does not pass the mini-project component.

## Common pitfalls

A short list of capstone-week pitfalls. None is fatal; all are easy to fix if recognised early.

- **The Monday scope was too big.** By Tuesday lunch you have a title screen and no playable loop. Rescope down to a single-screen, single-mechanic build immediately. Pong with screen-shake ships; a JRPG does not.
- **The HTML5 export shows a black screen.** The export template is missing or the browser blocked the audio context. Open the browser console; the error is almost always there. Re-run *Editor → Manage Export Templates → Download and Install* if the template is missing.
- **The macOS build refuses to open.** Gatekeeper quarantined the unsigned `.app`. Add the `xattr -dr com.apple.quarantine MyGame.app` instruction to the itch.io page; the user runs it once and the binary launches. Or use the right-click → Open workaround.
- **The Windows build triggers SmartScreen.** Unsigned binaries do. Add a one-line note to the itch.io page; users click *More info → Run anyway*. The alternative is code-signing, which costs $250-400/year and is out of scope for week 12.
- **The itch.io upload is rejected for being too big.** The free tier has a 1 GB per-file limit. A typical Godot project is 30-200 MB. If you are over 1 GB, you have committed asset source files (PSDs, RAW audio) into the export; strip them.
- **The 30-second trailer is 90 seconds long.** Cut it. The 30-second cut gets watched all the way through; the 90-second cut does not. Six 5-second beats. Cut anything that does not fit.
- **A CC-BY asset has no attribution.** The author can DMCA the itch.io page and itch.io will take it down. Audit `CREDITS.md` against the actual assets in the build before you upload. The exercise script in this folder does it for you.
- **The capstone build does not run on a friend's machine.** You shipped a dev build by accident. Re-export from the *release* preset (debug = off, runtime debug print = off). Test in an incognito window on a different machine if you can.
- **The save file from a prior week's playthrough overwrites the high-score table on first launch.** You forgot to namespace the save path. Use `user://capstone/save.latest`, not `user://save.latest`. The Week 11 `SaveManager` accepts a per-game prefix; pass one.
- **You skipped the cuts log and lost track of why you cut a feature.** Next time, write it down. The cuts log is the single most valuable artefact from a capstone week for *future* projects; reread it on the next project's Monday.

When in doubt, the rescue trick from Lecture 1 applies: cut a feature. The shipped game with one cut feature is shipped; the unshipped game with one extra feature is not.

## A note on the next week

There is no next week. This is week twelve of twelve. The track is complete.

What comes after this is your decision. Some students extend the capstone for another four weeks and submit it to a game jam — Ludum Dare (April, August, December), Global Game Jam (January-February), and js13kGames (August-September) are the three best free public jams to enter as a first-time-shipping indie. Other students start a Week 13 of their own design — a procedurally generated level pack for the capstone, a Steam Direct port, a mobile port, a multiplayer expansion. The toolbox is yours. The next twelve weeks are not on a schedule any longer.

Save your capstone repo. Pin it on your GitHub profile. Link it from your portfolio. The single most valuable artefact of this track is not the cohort certificate; it is a public, downloadable, playable arcade game with your name on the itch.io page and a working credits roll. That artefact is the bar a future employer or collaborator will measure against. You cleared it this week.

## Track wrap-up: Weeks 1-12 at a glance

| Week | Topic                                | The one subsystem you keep                                       |
|-----:|--------------------------------------|------------------------------------------------------------------|
|   1  | The game loop                        | A `_process(delta)` body that takes `delta` seriously.           |
|   2  | Collisions and physics-lite          | An AABB-vs-AABB sweep test that survives high speeds.            |
|   3  | Game design vocabulary               | The verb-goal-obstacle-reward decomposition of any prototype.    |
|   4  | Tilemaps and levels                  | A grid-backed tilemap reader plus an LDtk import path.           |
|   5  | State machines                       | The `State` interface and the `StateMachine` autoload.           |
|   6  | Animation and juice                  | Squash-and-stretch, screen-shake, hit-pause, particle burst.     |
|   7  | Save and load systems                | A `user://`-rooted JSON loader with a default schema.            |
|   8  | Sound and music systems              | A two-bus audio mixer with ducking and one-shots.                |
|   9  | Multiplayer fundamentals             | A `MultiplayerSpawner` plus a `MultiplayerSynchronizer` pair.    |
|  10  | Shaders and visual effects           | Hit-flash, dissolve transition, screen-shake post-process.       |
|  11  | Save systems and serialization       | Temp-file-plus-rename, SHA-256 integrity, version migration.     |
|  12  | Capstone: ship a complete game       | The shipped build with your name on the itch.io page.            |

Twelve subsystems. Twelve mini-projects. One shipped game. That is the contract for the track and it is the contract you fulfilled this week.
