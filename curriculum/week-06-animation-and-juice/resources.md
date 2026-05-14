# Week 6 — Resources

Every resource on this page is **free** and **publicly accessible** unless explicitly noted as "excerpts free." No paywalled books, no proprietary PDFs. If a link breaks, please open an issue.

## Required reading and watching (work it into your week)

- **Steve Swink — *Game Feel* (2009), free chapter sampler (Morgan Kaufmann/Routledge).** The canonical text on game feel. The publisher hosts a free chapter sampler that covers the three-pillar framework (real-time control, simulated physical space, polish). The full book is paywalled but the sampler is enough for this week's vocabulary. Internet Archive also has the full book available for one-hour digital borrow:
  <https://www.routledge.com/Game-Feel-A-Game-Designers-Guide-to-Virtual-Sensation/Swink/p/book/9780123743282>
  <https://archive.org/details/gamefeelgamedesi0000swin>
- **Jan Willem Nijman — *The Art of Screenshake* (GDC Europe 2013, free, 30 min).** The most-cited 30-minute talk in game-feel literature. Nijman ships the same Vlambeer prototype twice — once without juice and once with twenty juice tricks stacked — and the audience laughs. Watch end-to-end:
  <https://www.youtube.com/watch?v=AJdEqssNZ-U>
- **Martin Jonasson + Petri Purho — *Juice it or lose it* (Nordic Game Jam 2012, free, 8 min).** The eight-minute companion piece every game-feel lecture cribs from. A pong clone, juiced live in front of an audience. Free on YouTube:
  <https://www.youtube.com/watch?v=Fy0aCDmgnxg>

## Steve Swink — *Game Feel* (free chapters + borrow)

The book is paywalled in print; the publisher hosts a free chapter sampler and the Internet Archive hosts a one-hour digital borrow of the full text. Chapters relevant this week:

- **Chapter 1 — "Defining Game Feel."** The three-pillar framework. Read first.
- **Chapter 4 — "Polish."** The chapter that names the techniques we implement: squash and stretch, easing, anticipation, follow-through, screen shake, particles.
- **Chapter 5 — "Metaphor."** Why a jump *feels* like a jump even though it is two floats and a gravity constant. Optional but excellent.
- **Chapter 12 — "Tuning Game Feel."** The dose-response work this week's mini-project lives inside. Optional this week; mandatory before Week 11 playtesting.

Free chapter sampler PDF:
<https://www.routledge.com/Game-Feel-A-Game-Designers-Guide-to-Virtual-Sensation/Swink/p/book/9780123743282>

Internet Archive borrow (free with account):
<https://archive.org/details/gamefeelgamedesi0000swin>

## The juice talks (free, all on YouTube)

These four talks together are about 90 minutes. Watch all four this week. Each one earns its keep.

- **Jan Willem Nijman — *The Art of Screenshake* (GDC Europe 2013, 30 min).** Linked above. The single most-cited talk on this topic.
  <https://www.youtube.com/watch?v=AJdEqssNZ-U>
- **Jonasson + Purho — *Juice it or lose it* (Nordic Game Jam 2012, 8 min).** Linked above. The eight-minute version.
  <https://www.youtube.com/watch?v=Fy0aCDmgnxg>
- **Mark Brown — *Secrets of Game Feel and Juice* (Game Maker's Toolkit, 2017, 11 min).** Brown distils Swink's book into a free video. Watch after Nijman; it is the design counterpart to the implementation talk.
  <https://www.youtube.com/watch?v=216_5nu4aVQ>
- **Masahiro Sakurai — *Hit Stop and Game Feel* (Sakurai on Creating Games, 2022, 5 min).** The *Super Smash Bros.* / *Kirby* director on the single most important impact-juice trick — pausing the game for a few frames on a hit. Five minutes; pure technique.
  <https://www.youtube.com/@sora_sakurai_en>

## The Coding Train juice videos (Daniel Shiffman, free, ~90 min total)

Daniel Shiffman reads *Game Feel* on camera and ports the examples to p5.js. You don't need p5.js — the *vocabulary* and the *demos* translate one-to-one to Pygame.

- **The Coding Train — *Game Feel — Defining Game Feel* (Coding Challenge, ~15 min).** Daniel reads Swink's chapter 1 and then implements a juiced movement controller live. Free:
  <https://www.youtube.com/@TheCodingTrain>
- **The Coding Train — *Easing Functions / Lerp* (~12 min).** Daniel walks through the lerp function and the standard easing curves. The single best free explanation of `ease_out_back` we know:
  <https://www.youtube.com/@TheCodingTrain>
- **The Coding Train — *Particle Systems* (~18 min, two parts).** A flat list of particles, integrated like any other game object. Same shape we use this week:
  <https://www.youtube.com/@TheCodingTrain>
- **The Coding Train — *Screen Shake* (~10 min).** Three parameters: amplitude, duration, decay. Daniel's implementation is two lines longer than ours; either ships:
  <https://www.youtube.com/@TheCodingTrain>
- **The Coding Train — *Sprite Sheets* (~12 min).** A single PNG, a grid of frames, a draw call per frame. Daniel uses p5.js; the algorithm is identical in Pygame:
  <https://www.youtube.com/@TheCodingTrain>

## Easing curves reference

- **Robert Penner — easing equations (the original, 2001).** The PDF that every game engine's easing library is descended from. Public domain, ten pages:
  <http://robertpenner.com/easing/penner_chapter7_tweening.pdf>
- **easings.net — interactive easing-curve gallery.** Hover any curve to see it animate. The single best free reference for "which curve do I want?":
  <https://easings.net/>
- **CSS Tricks — *A look at easing curves* (free).** A short, illustrated essay that complements easings.net with one-paragraph descriptions per curve:
  <https://css-tricks.com/ease-out-in-ease-in-out/>

## Pygame-specific (free)

- **Pygame `Surface.subsurface()`.** Used for `SpriteSheet.frame(i)`. Returns a view into the parent surface — no pixel copy, no extra memory:
  <https://www.pygame.org/docs/ref/surface.html#pygame.Surface.subsurface>
- **Pygame `pygame.transform.scale()` and `pygame.transform.scale_by()`.** Used for squash-and-stretch. `scale_by()` is preferred — it takes a factor pair like `(0.7, 1.2)` and returns a new surface:
  <https://www.pygame.org/docs/ref/transform.html>
- **Pygame `pygame.mixer.Sound`.** Loads a `.wav` or `.ogg` and gives you `play()`, `stop()`, and `set_volume()`. Audio mixing is a Week 10 topic; for now, "play this one-shot on transition" is all you need:
  <https://www.pygame.org/docs/ref/mixer.html>
- **Pygame `pygame.sprite.Group` and `LayeredUpdates`.** Useful for particle systems with large counts (>500). Optional for this week; the flat list pattern is fine up to a thousand:
  <https://www.pygame.org/docs/ref/sprite.html>

## Free art and sound assets

- **Kenney (kenney.nl) — CC0 sprite, tile, and sound packs.** The single most useful free-asset source for this course. For Week 6 specifically:
  - **Platformer Characters 1 / 2** — sprite sheets with idle/run/jump frames ready to go.
  - **Impact Sounds** and **Interface Sounds** — short SFX packs. ~50 MB. CC0.
  - **Sci-Fi Sounds** and **RPG Audio** — longer ambient/effect cues.
  <https://kenney.nl/assets>
- **OpenGameArt.org — CC0 / CC-BY sprite sheets and sound effects.** Less consistent quality than Kenney but a much larger catalogue:
  <https://opengameart.org/>
- **freesound.org — short SFX, mostly CC0 / CC-BY.** For the one-shot sounds we trigger on transitions. Search "footstep dirt" and pick something three-frames long:
  <https://freesound.org/>
- **Itch.io free asset packs.** Many free, well-curated, CC-BY or CC0. Filter by "Asset packs > Free":
  <https://itch.io/game-assets/free>

## Open-source games with public juice code

Reading other people's juice code is the fastest way to internalise the dose-response curves. All four below are MIT/BSD/zlib licensed and have visible juice in code you can grep.

- **Celeste (Maddy Thorson + Noel Berry).** The original 2017 PICO-8 prototype is open source; the released version's Madeline character has been extensively reverse-engineered. The coyote-time, jump-buffering, and dash-tween code is canonical:
  <https://github.com/NoelFB/Celeste>
- **Vlambeer / Nuclear Throne style references.** Vlambeer didn't open-source *Nuclear Throne*, but Jan Willem Nijman's *Screenshake* talk demos the same techniques, and several community ports exist with explicit juice code. Search for "nuclear throne screenshake clone" on GitHub.
- **Pico-8 carts on the BBS.** Many *Celeste*-likes and *Downwell*-likes have visible juice in 50-line LUA files. Free, viewable in the browser:
  <https://www.lexaloffle.com/bbs/?cat=7>
- **Pygame community examples.** Search GitHub for `pygame screenshake` and `pygame easing`; many small repos with 200-line implementations.

## Squash-and-stretch references (animation principles)

The "twelve principles of animation" come from Frank Thomas and Ollie Johnston's *Disney Animation: The Illusion of Life* (1981). Free summaries circulate widely.

- **Alan Becker — *12 Principles of Animation* (YouTube series, free, ~12 episodes).** Each principle in 3-5 minutes with hand-drawn examples. Squash-and-stretch is episode 1. Watch the first six:
  <https://www.youtube.com/@AlanBeckerTutorials>
- **Disney *Illusion of Life* — chapter summaries (free).** The book is paywalled but summaries of the twelve principles are on every animation-school blog. The Wikipedia summary is good enough for this week:
  <https://en.wikipedia.org/wiki/Twelve_basic_principles_of_animation>

## Particle systems

- **Bob Nystrom — *Game Programming Patterns*, chapter "Object Pool."** Particles are the canonical use case for object pooling. For this week we use a flat list; for the optimisation pass in Week 11, we'll pool. Read now; implement later:
  <https://gameprogrammingpatterns.com/object-pool.html>
- **Sebastian Lague — *Particle Systems* (~10 min, Unity but the algorithm is universal).** A clean walk-through of the per-particle integration loop:
  <https://www.youtube.com/@SebastianLague>

## Screen shake references

- **Squirrel Eiserloh — *Improved Perlin Noise for Game Developers* (GDC).** The "smooth" shake (Perlin noise) versus the "uniform random" shake. Eiserloh's talk is the canonical free source. Optional for this week — we use uniform random; Perlin shake is a stretch:
  <https://www.youtube.com/results?search_query=squirrel+eiserloh+noise+gdc>
- **Hyper Light Drifter devblog — chromatic aberration on impact (free).** The team blogged the implementation. One paragraph; tweet-length:
  <https://www.gamedeveloper.com/disciplines/hyper-light-drifter-devblog>

## Hit-stop and frame-pause

- **Masahiro Sakurai — *Hit Stop and Game Feel* (linked above).** Five minutes; the single best free explanation.
- **Game Maker's Toolkit — *The Secret of Mario's Jump* (8 min, free).** Mark Brown on the *Super Mario Bros.* jump. Implicitly covers hit-stop and impact framing:
  <https://www.youtube.com/c/GameMakersToolkit>

## Books and longer-form (free or excerpts free)

- **Steve Swink — *Game Feel* (already linked).** Read it.
- **Jesse Schell — *The Art of Game Design* (excerpts free).** *Lens of Juice* and *Lens of Polish* apply directly. Read them this week:
  <http://www.artofgamedesign.com/>
- **Jeremy Gibson Bond — *Introduction to Game Design, Prototyping, and Development* (excerpts free).** Chapter on "Game Feel" is a careful textbook treatment that complements Swink:
  <https://www.gameprototypingbook.com/>

## Glossary cheat sheet

Keep this open in a tab.

| Term | Plain English |
|------|---------------|
| **Game feel** | The moment-to-moment sensation of playing a game. Swink's three pillars: real-time control, simulated physical space, polish. |
| **Juice** | The polish pillar of game feel. The feedback the game gives you that confirms an action beyond the mechanical outcome. |
| **Sprite sheet** | A single PNG containing a grid of animation frames. Draw one frame at a time. |
| **Animation clip** | A list of frame indices plus an `fps` and a `loop` flag. The thing the FSM `enter()` hook plays. |
| **`lerp(a, b, t)`** | "Linear interpolate": return a value `t` of the way from `a` to `b`. Two-line function. The most-used function in game code. |
| **Tween** | "In-betweening": animate a value from `a` to `b` over a duration using an easing curve. A class with `start`, `end`, `duration`, `elapsed`, `ease`, `value()`. |
| **Easing curve** | A function `f(t) -> t'` applied to the lerp parameter before the lerp. `ease_in` accelerates, `ease_out` decelerates, `ease_out_back` overshoots. |
| **Squash-and-stretch** | The animation principle of deforming a shape on acceleration / deceleration. A 200 ms scale tween in Pygame. |
| **Screen shake** | A camera offset of `(uniform(-amp, amp), uniform(-amp, amp)) * decay(t)`. Three parameters; two random calls per frame. |
| **Particle** | A short-lived sprite with position, velocity, lifetime, and per-frame integration. Spawned in bursts. |
| **Particle emitter** | The thing that spawns particles. Owned by an FSM state's `enter()`. |
| **Hit stop** | A 50-100 ms pause of the world on a successful hit. Makes the hit *land*. |
| **Coyote time** | A 80-100 ms grace window after the player walks off a ledge during which jump still works. *Celeste*-grade. |
| **Jump buffer** | A 80-100 ms window before landing during which an early jump-press is queued. Also *Celeste*-grade. |
| **Chromatic aberration** | A three-pass coloured offset draw used as impact polish. *Hyper Light Drifter*'s signature. |
| **Sound cue** | A one-shot SFX triggered by a state transition (in `enter()`), not by physics or input. |
| **Dose** | Every juice trick has a knob. The taste setting is rarely the maximum. |

---

*If a link 404s, please [open an issue](https://github.com/CODE-CRUNCH-CLUB) so we can replace it.*
