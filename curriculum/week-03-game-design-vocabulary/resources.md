# Week 3 — Resources

Every resource on this page is **free** and **publicly accessible** unless explicitly noted as "excerpts free." No paywalled books, no proprietary PDFs. If a link breaks, please open an issue.

## Required reading (work it into your week)

- **Steve Swink — *Game Feel* (Gamasutra essay version)** — the original Gamasutra essays that became the book. Free in full:
  <https://www.gamedeveloper.com/design/game-feel-the-secret-ingredient>
- **Steve Swink — *Game Feel* (book, excerpts free)** — the canonical book; chapter excerpts and the introduction are available free on the publisher's site and the author's blog. Read the introduction and chapter 1 at minimum:
  <https://www.game-feel.com/>
- **Doug Church — *Formal Abstract Design Tools* (1999)** — the four-lenses essay. Free, full text on Gamasutra/Game Developer:
  <https://www.gamedeveloper.com/design/formal-abstract-design-tools>
- **Hunicke, LeBlanc, Zubek — *MDA: A Formal Approach to Game Design and Game Research* (2004)** — the MDA paper, free PDF:
  <https://users.cs.northwestern.edu/~hunicke/MDA.pdf>

## Robert Nystrom — *Game Programming Patterns* (free online, full book)

Bob Nystrom's book is one of the best free resources in this whole course. Every chapter is online in full at <https://gameprogrammingpatterns.com/>. The chapters relevant this week:

- **Game Loop** (you already wrote one; re-read the chapter now that the loop is muscle memory):
  <https://gameprogrammingpatterns.com/game-loop.html>
- **Update Method** (the spine of every game object's tick):
  <https://gameprogrammingpatterns.com/update-method.html>
- **Observer** (a clean way to fire "brick destroyed" events without coupling the brick to the particle system):
  <https://gameprogrammingpatterns.com/observer.html>
- **Object Pool** (you'll re-read this in Week 6; particles want a pool):
  <https://gameprogrammingpatterns.com/object-pool.html>

## Talks and videos (free, on YouTube)

- **Jan Willem Nijman — *The Art of Screenshake*** (GDC, 2013). Twenty-three minutes. The most-watched single source on juice. Watch it twice:
  <https://www.youtube.com/watch?v=AJdEqssNZ-U>
- **Vlambeer — *The Hidden Subtleties of Easy-To-Approach Games*** (GDC, 2014). Rami Ismail on game feel from the other Vlambeer half:
  <https://www.youtube.com/watch?v=AKlBP6tJZ7o>
- **Mark Brown — *Game Maker's Toolkit*** — the whole channel is a master class in design vocabulary. Specifically the **Secrets of Game Feel** episode:
  <https://www.youtube.com/watch?v=216_5nu4aVQ>
- **Daniel Floyd, Game Maker's Toolkit, and other essayists in the *juice it or lose it* lineage** — start with this GMTK playlist:
  <https://www.youtube.com/@GMTK>

## The classic essays — game design vocabulary

- **Doug Church — *Formal Abstract Design Tools*** (already linked above).
- **Raph Koster — *A Theory of Fun for Game Design*** (the book is not free, but the author's blog has every chapter idea in essay form for free):
  <https://www.raphkoster.com/games/essays/>
- **Anna Anthropy — *A Game Design Vocabulary*** (excerpts free on the publisher's preview):
  <http://www.auntiepixelante.com/>
- **Tom Francis — design talks** (the Gunpoint / Heat Signature designer, very good on building feel from the inside out):
  <https://www.pentadact.com/>

## Game Programming Patterns — specific chapters worth your week

(Repeating because they're free and they're load-bearing.)

- **Game Loop:** <https://gameprogrammingpatterns.com/game-loop.html>
- **Update Method:** <https://gameprogrammingpatterns.com/update-method.html>
- **Observer (events / signals):** <https://gameprogrammingpatterns.com/observer.html>
- **Object Pool (particle pre-allocation):** <https://gameprogrammingpatterns.com/object-pool.html>
- **State (Week 5 preview):** <https://gameprogrammingpatterns.com/state.html>

## Free assets (audio, sprite, palette)

- **Freesound.org** — short SFX. Search "impact", "thud", "coin", "bounce". Filter by CC0 or CC-BY and credit the author:
  <https://freesound.org/>
- **Kenney.nl — Sounds packs** (CC0, the gold standard for free game audio):
  <https://kenney.nl/assets/category:Audio>
- **JSFXR / SFXR (Bfxr web tool)** — generate retro 8-bit SFX in your browser, export as `.wav`. Twenty years old and still the indie standard:
  <https://sfxr.me/>
- **ChipTone (SFB Games)** — similar in spirit to SFXR, more parameters:
  <https://sfbgames.itch.io/chiptone>

## Official Pygame docs (you'll bounce here this week)

- **`pygame.mixer`** (you finally need it): <https://www.pygame.org/docs/ref/mixer.html>
- **`pygame.mixer.Sound`** (load, play, set volume): <https://www.pygame.org/docs/ref/mixer.html#pygame.mixer.Sound>
- **`pygame.draw.circle`** (for particles): <https://www.pygame.org/docs/ref/draw.html>
- **`pygame.Surface` with `SRCALPHA`** (for alpha-blended particles): <https://www.pygame.org/docs/ref/surface.html>

## Glossary cheat sheet

Keep this open in a tab.

| Term | Plain English |
|------|---------------|
| **Game feel** | Real-time control of a virtual character or object, with predictable response, in a simulated space (Swink, 2009). |
| **Juice** | The thin layer of audio-visual polish that confirms player actions and amplifies events. Information, not decoration. |
| **Screen shake** | A short, decaying camera offset applied on impact. Magnitude proportional to event strength. |
| **Hit-stop** | A 1-3 frame freeze of the simulation on impact. Adds disproportionate weight to a hit. |
| **Particle burst** | A short-lived spawn of small drawables that decay and disappear. Carries the impact's location and energy. |
| **Squash and stretch** | Animation principle (Disney, 1937) — a body deforms briefly on acceleration or impact to communicate force. |
| **MDA** | Mechanics, Dynamics, Aesthetics. The designer ships Mechanics; the player feels Aesthetics; Dynamics is the bridge. |
| **Four lenses (Church)** | Intention, Perceivable Consequence, Story, Goals. A 1999 vocabulary for talking about game design without resorting to taste. |
| **Polish (Swink)** | The third pillar of game feel — the visual/audio layer that sells the underlying simulation. Not optional. Not a vibe. |

---

*If a link 404s, please [open an issue](https://github.com/CODECRUNCHWORLDWIDE) so we can replace it.*
