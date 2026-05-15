# Lecture 3 — The itch.io page, the trailer, and the credits

By the time this lecture is delivered on Friday, the binary side of the capstone is done. The four targets have exported. The zip files are sitting in the `dist/` folder of your project. The only thing standing between you and a shipped game is the *marketing surface* — the itch.io page, the screenshots, the trailer, the credits. The marketing surface is the artefact a stranger sees before they download the binary; it is also the artefact that determines whether they download it at all.

This lecture is editorial because the marketing surface, like the scope decision in Lecture 1, is a judgement-driven discipline that punishes neglect more than it punishes inexperience. A page that looks like a Sunday-night cram session does not pass the capstone, even if the binary behind it is excellent. A page that looks like a deliberate week-long effort passes the capstone even if the binary behind it is small.

The canonical reference is the **itch.io developer documentation** at [itch.io/docs/creators/getting-started](https://itch.io/docs/creators/getting-started). Read it in full before today's lecture; it is shorter than this one and you will refer back to it on Saturday during the upload.

## The anatomy of an itch.io page

An itch.io project page has, in display order, the following parts. Each one is configurable from the page editor at [itch.io/dashboard](https://itch.io/dashboard) → *New project* (or *Edit* on an existing project).

1. **Banner image.** A large image (920x480 recommended) shown at the top of the page. The image is the *first* thing the visitor sees. It should reproduce the *feel* of the game — not necessarily a screenshot, often a stylised composition.
2. **Thumbnail image.** A small image (315x250 recommended) shown on the itch.io browse pages and on your dashboard. The thumbnail is the *only* thing the visitor sees when deciding whether to click into the project page. It is the highest-leverage asset.
3. **Title.** The game's name, plain text. itch.io shows it adjacent to the banner.
4. **Short description (tagline).** A one-line under-the-title summary. *"Cross the road. Cars get faster."* itch.io shows it adjacent to the title on browse pages.
5. **Body copy.** The long-form description. Three to five paragraphs. We will talk in detail.
6. **Embedded video (trailer).** YouTube or Vimeo embed code; itch.io renders it inline. We will talk in detail.
7. **Screenshots.** Three to five static images of the game in action. itch.io renders them as a strip below the trailer.
8. **Download buttons.** One button per uploaded binary. itch.io shows them as a list, with platform icons and file sizes auto-detected.
9. **Tags.** A space-separated list of categorisation tags (*pixel-art*, *arcade*, *frog*, *2d*, *short*). itch.io uses these for browse and search.
10. **Genre and made-with.** Picks from a dropdown. Genre: *Action*, *Adventure*, *Card Game*, *Educational*, etc. Made-with: *Godot*, *Unity*, *Unreal*, *Other*. Pick *Godot*.
11. **Pricing.** *Free*, *Pay-what-you-want* (with optional minimum), or *Fixed price*. We ship *Free* in the capstone.
12. **Visibility.** *Public*, *Restricted* (URL-only, no browse listing), *Draft* (only you can see it). We ship *Public*.

The page editor renders a preview as you edit. Use it. Resist the temptation to publish a half-edited page and "fix it later" — the URL gets indexed by search engines and shared in cohort channels the moment you go public.

## Pricing — why we ship Free

itch.io supports three pricing models. They are all worth knowing about; for the capstone, we recommend *Free*. The reasoning matters.

- **Free.** Zero charge to download. itch.io takes 0% of $0, which is $0. The download is *frictionless* — no email, no payment, no account required on the user side. Maximum reach.
- **Pay-what-you-want.** A suggested price, with a minimum (which can be $0). If the minimum is $0, the user can still download for free; the *Pay* button is offered above the *Take it for free* button. The model is creator-friendly because supporters can tip without gating the download. itch.io's revenue share on PWYW sales is *creator-adjustable* between 0% and 30% (default 10%). The model is the second-best option for a capstone and the model we recommend if you want to leave a tipping option open.
- **Fixed price.** A non-zero price required to download. The model produces revenue but adds friction. For a first shipped game, the revenue is almost always smaller than the lost downloads from gating. Fixed price is the right choice for a *commercial* release with a marketing push behind it; it is a wrong choice for a first capstone.

The capstone rubric grades on *whether the game ships and is downloaded*, not on whether it earns revenue. Free is the rubric-aligned choice. If after the capstone you decide to move to Pay-what-you-want, the page editor lets you change the price at any time with no impact on the URL.

itch.io itself recommends Free for first ships in its *Getting Started* docs and in the community forums; the recommendation is empirically grounded in data from the platform's first decade of operation. The students who shipped for free in past cohorts have a public artefact; the students who priced their first build at $5 have, on average, fewer downloads, no revenue, and a less linkable portfolio.

## Writing the body copy

The body copy is three to five paragraphs of plain English describing the game. It is written in the **second person**. The reader is the player; *you* in the copy is *them*. Examples:

> *You are a frog. Four lanes of traffic between you and the other side. Each crossing the cars get faster. There is no power-up, no respawn, no second chance — only your reflexes and the next gap in the traffic. How many crossings can you make before the road wins?*

That is one paragraph. It does several things at once: it states the pitch (*you are a frog crossing a road*), it states the obstacle (*cars get faster*), it states what the game is *not* (*no power-up, no respawn, no second chance*), and it ends with the *hook question* — the implicit invitation to download and find out.

A second paragraph might describe the controls:

> *Use the arrow keys (or WASD) to hop one tile at a time. Each hop is committed — you cannot cancel mid-air. The death animation is brief; you can be hopping again in two seconds. The game is built for the kind of "one more run" rhythm that arcade games have run on since 1981.*

A third paragraph might describe the build:

> *FrogCross was built in Godot 4.2 for the Code Crunch Worldwide C11 Crunch Arcade capstone in May 2026. Single-player, single-screen, single-mechanic. Five minutes from your first hop to your first high score. The shipped build runs in the browser (HTML5), on Windows, on macOS, and on Linux. No install, no account, no email. Just hop.*

That is three paragraphs. Hundreds of capstone pages have used a similar template. The discipline is to keep the copy short — five paragraphs is the maximum; three is the target. A page with a 20-paragraph description is read by no one. A page with a three-paragraph description is read by everyone who clicked into it.

Things to *not* include in the body copy:

- A development log. The page is not your blog. If you want a devlog, write it as a separate itch.io devlog post linked from the project page.
- A pitch for *future* features. If a feature is not in the shipped build, it does not exist for the player. *"I plan to add multiplayer later"* is a Reddit comment, not a page.
- Inside jokes from your cohort. The page is read by strangers. The strangers are not in on the joke.
- A wall of credits. Credits go in the credits section (below the controls), not in the body copy. Body copy is for the *player*.

## Screenshots — what to capture

A capstone page has three to five screenshots. The screenshots must, taken together, convey the entire game's appeal in less than five seconds of scrolling. The principles:

- **Screenshot one is the hero shot.** The single most appealing moment in the game. For *Frog Cross*, it is the frog mid-hop with two cars converging. For a paddle game, it is the ball trail across the screen. For a top-down shooter, it is a screen-shake-active moment with bullets and particles in flight. The hero shot is the screenshot that, all by itself, sells the game.
- **Screenshot two is the loop.** A representative moment of normal play. Not the hero shot, not the dramatic moment, just *what the player does most of the time*. The frog walking calmly between two lanes. The paddle waiting for the next return. The ship dodging a smaller asteroid.
- **Screenshot three is the consequence.** The death animation, the game-over screen with the high score, the level-clear screen, the boss explosion. Whatever the *out of play* moment is, it is the third screenshot.
- **Screenshots four and five are optional.** Variety, alternate game states, the title screen, the credits roll. Skip them if you do not have three excellent variety shots; three strong screenshots beat five mediocre ones.

The capture method on each platform:

- **HTML5:** Run the local build in Chrome. Press F12, switch to *Device Toolbar* mode if you want a pixel-precise crop, take a screenshot with the *Capture full size screenshot* developer-tools menu.
- **Windows:** Win+Shift+S. Snipping Tool. Save as PNG.
- **macOS:** Cmd+Shift+4, drag a region. Save to Desktop. (Or Cmd+Shift+5 for the screenshot UI with options.)
- **Linux:** GNOME Screenshot, KSnip, Flameshot. All free.

Crop to a 16:9 aspect ratio (1920x1080, 1280x720, or 960x540 are common). Save as PNG. Upload to itch.io.

The itch.io documentation recommends *not* using JPEG for screenshots — pixel art compresses poorly to JPEG and develops visible block artifacts at low quality. PNG is the right choice for sub-megabyte screenshots; the itch.io CDN serves them efficiently regardless.

## The 30-second trailer

The trailer is the single most consequential marketing asset on the page after the thumbnail. The thumbnail decides whether visitors click in; the trailer decides whether they download.

The capstone trailer is **30 seconds**. Not 45. Not 60. Not 90. Thirty. The 30-second cut is the cut that gets watched all the way through. A 90-second trailer is a trailer that gets watched for 25 seconds and abandoned. The data on attention spans across video platforms is unambiguous on this point.

The structure is *six 5-second beats*:

| Beat | Time | Content                                                   |
|-----:|-----:|-----------------------------------------------------------|
|  1   |  0-5 | **Hook.** The verb in action. The most "this is fun" moment of the game. |
|  2   | 5-10 | **Mechanic intro.** What the player does. Stripped-down, clear, single action. |
|  3   |10-15 | **First conflict.** The obstacle appears. Tension introduced. |
|  4   |15-20 | **Escalation.** More obstacles, faster, more chaotic. |
|  5   |20-25 | **Climax.** A peak moment. The screen shakes; the music swells. |
|  6   |25-30 | **Title card.** The game's name and the itch.io URL, plain text, three seconds visible, two seconds fade. |

The six beats are a template, not a law. Variations are fine — some genres prefer a slow-burn opening; some prefer a comedic anti-climax. The discipline is to *plan* the beats before recording, not improvise them in the editor. The exercise `challenge-01-trailer-storyboard.md` in this week's folder walks you through storyboarding a beat-by-beat for a hypothetical game; do that exercise before recording your own.

### The capture pipeline

Recording the trailer involves three tools:

1. **OBS Studio** for the screen capture. [obsproject.com](https://obsproject.com). Configure: 1080p, 60 fps, hardware-accelerated H.264 encoding, ~10 Mbps bitrate. Capture the game's window only (not the whole desktop). Record three to five takes of each beat; you will pick the best in editing.
2. **Shotcut** or **DaVinci Resolve free edition** for the editing. [shotcut.org](https://shotcut.org) or [blackmagicdesign.com/products/davinciresolve](https://blackmagicdesign.com/products/davinciresolve). Both are free. Shotcut is lighter (200 MB install) and sufficient for a 30-second cut. Resolve is heavier (3 GB install) and the industry standard if you want a longer-term investment.
3. **YouTube** for the hosting. Upload the rendered MP4 as *Unlisted*. The video has a URL but is not surfaced in YouTube's algorithm or search; the itch.io page embeds it. We use Unlisted, not Private (Private requires the viewer to be signed in) and not Public (Public puts the video in YouTube's algorithm before the game has any traction).

The audio is *one* track. Either a CC0 sting from Freesound (filter the Freesound search by licence: CC0) or a CC-BY music loop with the author attributed in the YouTube description and in the itch.io page's credits. Do *not* use a copyrighted soundtrack — even a "fair use" clip will trigger YouTube's Content ID and may demonetise or mute the trailer. If the game has a soundtrack, use the soundtrack; if not, use a Freesound CC0 loop.

The render settings:

- Resolution: 1080p (1920x1080). Higher is unnecessary for a 30-second cut; lower looks dated.
- Frame rate: 60 fps (or 30 fps if the source footage is 30 fps).
- Codec: H.264, MP4 container.
- Bitrate: ~10 Mbps.
- Output file size: typically 30-50 MB for a 30-second 1080p MP4.

Upload to YouTube. Set visibility to *Unlisted*. Copy the video URL. Paste into the itch.io page editor's *Add a trailer* field.

### A worked storyboard

To make the format concrete, here is the storyboard for the hypothetical *Frog Cross* trailer:

```text
BEAT 1 (0:00-0:05): HOOK
  - Frog mid-hop, two cars converging. Screen-shake amplitude high.
  - Audio: single high-energy SFX. Sub-bass thump.

BEAT 2 (0:05-0:10): MECHANIC INTRO
  - Calm shot: frog hopping forward, one tile per beat, three hops.
  - Title overlay: "ARROW KEYS. ONE HOP AT A TIME."
  - Audio: hop SFX on each hop. Quiet music kicks in.

BEAT 3 (0:10-0:15): FIRST CONFLICT
  - First car appears. Frog dodges. Camera follows.
  - Audio: car engine pass-by. Music swells slightly.

BEAT 4 (0:15-0:20): ESCALATION
  - Four cars on screen, three lanes occupied. Frog moves between.
  - Audio: layered car engines. Music intensifies.

BEAT 5 (0:20-0:25): CLIMAX
  - Frog reaches the top edge. Screen flashes. High score banner.
  - Audio: triumphant sting. Music peak.

BEAT 6 (0:25-0:30): TITLE CARD
  - Black background. White text:
        FROG CROSS
        play free on itch.io
        https://example.itch.io/frog-cross
  - Audio: music tail-off. Silence at 0:29-0:30.
```

That is the storyboard. The recording captures each beat in OBS. The editing assembles the beats in Shotcut, adds the title card text, and renders to MP4. The MP4 uploads to YouTube as Unlisted. The Unlisted URL goes into the itch.io page. Total time from "start OBS" to "trailer is embedded in itch.io" — about three to four hours on Friday.

## Credits and attribution

Every asset used in the game must be attributed. This is a legal requirement for CC-BY assets and a professional norm for CC0 assets. The credits live in *three* places, all of which must agree:

1. **`CREDITS.md` in the project repo.** The source of truth. Plain text. Lists every asset by URL, the author, the licence, and a one-line description.
2. **The in-game credits screen.** Reachable from the title screen or after game-over. Renders the same content as `CREDITS.md`, scrolled or paginated.
3. **The itch.io page's credits section.** A subsection of the body copy, or a separate paragraph below the controls. Mirrors `CREDITS.md`.

The exercise `exercise-02-asset-license-audit.py` in this week's folder parses a `CREDITS.md` against the assets in the build folder and reports missing attributions. Run it before uploading.

The `CREDITS.md` template (in `mini-project/credits_template.md`) looks like:

```markdown
# Credits

## Code

- All game code by <YOUR NAME>, 2026. Built in Godot 4.2.
- The Code Crunch Worldwide C11 Crunch Arcade curriculum was the framework
  the build was written against.

## Art

- **Frog sprite**, 32x32, 4 directions. CC0. By "PixelArtist123" on OpenGameArt.
  https://opengameart.org/content/cute-frog-sprite
- **Car sprites**, 64x32, 3 variants. CC-BY by "RoadWarriorArt".
  https://opengameart.org/content/road-cars-pack
- **Road tile**, 32x32, repeating. Drawn by <YOUR NAME>. CC0.

## Audio

- **Hop SFX**. CC0 by "FreesoundUser42" on Freesound.
  https://freesound.org/people/FreesoundUser42/sounds/12345/
- **Background music loop**, 90 seconds. CC-BY by "AmbientCreator99" on Freesound.
  https://freesound.org/people/AmbientCreator99/sounds/67890/
- **Death sting**. CC0 by "SoundDesigner007" on Freesound.
  https://freesound.org/people/SoundDesigner007/sounds/24680/

## Fonts

- **Press Start 2P**, a pixel-art font from Google Fonts, Open Font License.
  https://fonts.google.com/specimen/Press+Start+2P

## Tools

- **Godot 4.2.2-stable**. Free, open source. MIT licence.
  https://godotengine.org
- **OBS Studio 30**. Free, open source. GPL.
- **Shotcut 24**. Free, open source. GPL.
- **OpenGameArt** and **Freesound** for the free-asset libraries.

## Special thanks

- The C11 Crunch Arcade Spring 2026 cohort, for the playtests.
- The instructor, for the editorial brutality on scope.
```

That template is mirrored into the in-game credits roll (Lecture 1 of Week 6 introduced the typewriter-effect credits component; Week 12's Exercise 5 wires it up to read from `CREDITS.md` at runtime) and into the itch.io page footer.

## The CC licence taxonomy in practice

Briefly, because it comes up: the licences you will see on OpenGameArt and Freesound are CC0, CC-BY, CC-BY-SA, CC-BY-NC, and CC-BY-ND. The full reference is at [creativecommons.org/share-your-work/cclicenses/](https://creativecommons.org/share-your-work/cclicenses/); the practical implications for a free itch.io capstone are:

- **CC0**: No attribution required. Safe to use. Still polite to acknowledge.
- **CC-BY**: Attribution required. Always include the author's name and a link to the original asset page. Safe to use for free and paid releases.
- **CC-BY-SA**: Attribution required, *and* any derivative must be CC-BY-SA. Reusing a CC-BY-SA sprite in a capstone is fine; commercialising the capstone later requires the entire game's code to be CC-BY-SA, which is contaminating. Avoid CC-BY-SA if you might charge for the game.
- **CC-BY-NC**: Attribution required, *non-commercial only*. **Not safe** for any version of the game you might eventually charge for. Treat as "do not use" if you have any commercial future plans.
- **CC-BY-ND**: Attribution required, *no derivatives*. You can redistribute the asset as-is but cannot modify it. Rare in game-asset libraries.

The exercise `exercise-02-asset-license-audit.py` warns on CC-BY-NC and CC-BY-SA usage and flags missing CC-BY attributions. Treat its output as a Saturday-morning gate before uploading.

## The post-ship checklist

After clicking *Save & view page* on the itch.io editor, the page is public. The post-ship checklist takes 15 minutes and prevents the most common post-publish embarrassments.

1. **Open the page URL in an incognito browser window.** This verifies the page is public and the assets load correctly without your itch.io session.
2. **Click each download button.** Verify the binary downloads at the expected size.
3. **Launch the HTML5 build in three browsers.** Chrome, Firefox, Safari (if available). Some HTML5 builds work in Chrome and fail silently in Safari due to audio context handling differences.
4. **Launch the Windows binary on a Windows machine.** Verify SmartScreen warning is dismissable. Verify the game launches and the title screen renders.
5. **Launch the macOS binary on a Mac.** Verify the Gatekeeper bypass works (right-click → Open). Verify the title screen renders.
6. **Launch the Linux binary on a Linux machine** (or WSL). Verify the executable bit is set and the binary runs.
7. **Re-read the page copy.** Typos, missing punctuation, weird line breaks. Edit them. The page is forever; the typos are forever unless fixed.
8. **Verify the credits.** Every asset attributed. Every CC-BY author named. The credits in `CREDITS.md`, in the in-game roll, and on the page agree.
9. **Test the trailer embed.** Click play on the embedded video. Verify it plays inside the itch.io page (not redirecting to YouTube).
10. **Share the URL.** Post to the cohort Discord. Update your portfolio. Pin the repo on GitHub. The artefact exists; tell the world.

## Summary, end of week, end of track

The capstone is the integration test for twelve weeks of work. The marketing surface is the integration test for the capstone. The shipped page with a downloadable build, three screenshots, a 30-second trailer, and a credits section is the artefact that closes the track.

Sunday's homework is the retrospective — a written walk-through of the twelve weeks, the subsystems retained, the lessons learnt, and the next project's preliminary scope. The retrospective is not a grading exercise. It is a *retrieval* exercise — the closer you write to the work, the more of the work you retain, and the more of the toolbox is available to you on the next project's Monday morning.

Save the capstone repo. Pin it on GitHub. Link it from your portfolio. The itch.io URL is permanent; share it on every job application that mentions games, indie, prototyping, or Godot. The single most valuable artefact of this track is not the cohort certificate; it is a public, downloadable, playable arcade game with your name on the itch.io page and a working credits roll. You shipped that this week. The next twelve weeks are not on a schedule any longer.
