# Week 3 — Game Design Vocabulary

You shipped a brick-breaker last week. Run it now. Watch the ball hit a brick: the brick disappears, the ball reverses, the score ticks up. It *works*. It is correct. It is also a little dead — the impact has no weight, the hit has no thud, nothing on screen says *something just happened* louder than the score in the corner.

This week we put names to that gap. The gap between "the code does the right thing" and "the player feels the right thing" is what designers call **game feel**, and it has been studied for two decades by people much smarter than us. Steve Swink wrote a whole book about it. Doug Church wrote a 1999 essay that the entire industry still cites. Robin Hunicke, Marc LeBlanc, and Robert Zubek formalised a way to talk about games as Mechanics, Dynamics, and Aesthetics. By the end of this week, you will be able to look at any 2D game and say, in vocabulary the industry agrees on, *why* it feels the way it feels.

We do not write a new game this week. We add **three feel touches** to the brick-breaker we already have — screen shake on brick destruction, a tiny particle burst at the impact point, and a sound cue — and we record a before/after video of the same gameplay. The code change is small. The perceptual change is large. The point of this week is to feel that gap in your own hands.

There is still no Godot. There is still no level editor. We are extending the brick-breaker chassis we already trust into something that does not just compute correctly but *communicates*.

## Learning objectives

By the end of this week, you will be able to:

- **Define** game feel in Steve Swink's terms — real-time control of a virtual character or object, with predictable response, in a simulated space — and identify the three pillars (input response, simulated space, polish).
- **List** Doug Church's four lenses (Intention, Perceivable Consequence, Story, Goals) and apply at least two to a game you already know.
- **Distinguish** Mechanics (the rules), Dynamics (what emerges when players play), and Aesthetics (what the player feels), per Hunicke, LeBlanc, and Zubek's MDA framework.
- **Identify** at least five common "juice" techniques — screen shake, particle bursts, hit-stop, squash-and-stretch, sound cues, screen flash, camera zoom — and explain when each one is appropriate.
- **Implement** screen shake, a particle burst, and a sound cue in Pygame, each with the magnitude tied to the strength of the triggering event (a small brick = a small shake; a power-up = a big shake).
- **Record** a before/after juice-comparison video of your own game and explain in 200 words what changed and why it feels different.
- **Critique** another student's game using the vocabulary in this week's lectures, without resorting to "it feels good" or "it feels bad."

## Prerequisites

This week assumes you have completed **Week 1** (the game loop and delta time) and **Week 2** (collisions and physics-lite). Specifically:

- You have a Week 2 brick-breaker (or Pong) repo you can keep extending. **If you skipped the Week 2 mini-project, do it first.** You cannot juice a game you do not have.
- You can write a Pygame main loop from memory and use `pygame.Vector2` and `Rect` without checking the docs every line.
- You read `pygame.key.get_pressed()` for held input and `KEYDOWN` for one-shot events.

If any of those are shaky, do the Week 2 mini-project before continuing.

## Topics covered

Lecture 1 — What makes a game feel good:

- Steve Swink's definition of **game feel** and why "feel" is not vibes but a measurable response curve.
- The three pillars: **input response**, **simulated space**, and **polish** (the layer that sells the other two).
- A short tour of named juice techniques: screen shake, hit-stop, particles, squash-and-stretch, audio anticipation, camera nudge, screen flash.
- Juice as a *signal-to-noise* problem: each effect must carry information, not decoration.
- How to playtest for feel without leading the witness.

Lecture 2 — The Four Lenses and the MDA framework:

- Doug Church's 1999 essay *Formal Abstract Design Tools*, the **four lenses** (Intention, Perceivable Consequence, Story, Goals), and why this vocabulary survived two decades.
- The **MDA framework** (Mechanics, Dynamics, Aesthetics) by Hunicke, LeBlanc, and Zubek — three lenses at three abstraction levels.
- Designer-side vs player-side: the designer ships M, the player experiences A; D is the bridge.
- A worked example: applying the four lenses and MDA to your Week 2 brick-breaker.
- A short note on what these frameworks *do not* tell you (and why no single framework is enough).

## Weekly schedule

The schedule below adds up to approximately **35 hours**. Treat it as a target. Lecture-heavy weeks like this one feel light on the keyboard — the *thinking* time replaces the typing time. That is normal. Vocabulary takes longer than syntax.

| Day       | Focus                                         | Lectures | Exercises | Challenges | Quiz/Read | Homework | Mini-Project | Self-Study | Daily Total |
|-----------|-----------------------------------------------|---------:|----------:|-----------:|----------:|---------:|-------------:|-----------:|------------:|
| Monday    | Game feel essay, the three pillars            |    2h    |    1h     |     0h     |    0.5h   |   1h     |     0h       |    1h      |     5.5h    |
| Tuesday   | Four lenses + MDA, applied to brick-breaker   |    2h    |    1h     |     0h     |    0.5h   |   1.5h   |     0h       |    0.5h    |     5.5h    |
| Wednesday | First feel touch: screen shake                |    0h    |    1.5h   |     1h     |    0.5h   |   1h     |     1h       |    0h      |     5h      |
| Thursday  | Second + third feel touches: particles, audio |    0h    |    1.5h   |     2h     |    0.5h   |   1.5h   |     1.5h     |    0h      |     7h      |
| Friday    | Tuning the feel — playtest with one human     |    0h    |    0h     |     0h     |    0.5h   |   1h     |     2.5h     |    0.5h    |     4.5h    |
| Saturday  | Before/after recording, quiz                  |    0h    |    0h     |     0h     |    0.5h   |   0h     |     2.5h     |    0h      |     3h      |
| Sunday    | Review, write up, push                        |    0h    |    0h     |     0h     |    0.5h   |   0h     |     2h       |    0h      |     2.5h    |
| **Total** |                                               | **4h**   | **5h**    | **3h**     | **3.5h**  | **6h**   | **9.5h**     | **2h**     | **33h**     |

## How to navigate this week

| File | What's inside |
|------|---------------|
| [README.md](./00-overview.md) | This overview (you are here) |
| [resources.md](./01-resources.md) | Swink's *Game Feel*, Nystrom's *Game Programming Patterns*, Church's four-lenses essay |
| [lecture-notes/01-what-makes-a-game-feel-good.md](./02-lecture-notes/01-what-makes-a-game-feel-good.md) | Game feel defined, juice as measurable signal |
| [lecture-notes/02-the-four-lenses-and-the-MDA-framework.md](./02-lecture-notes/02-the-four-lenses-and-the-MDA-framework.md) | Church's four lenses, Hunicke/LeBlanc/Zubek MDA, applied |
| [exercises/README.md](./03-exercises/00-overview.md) | Index of short coding drills |
| [exercises/exercise-01-add-three-juice-touches.py](./03-exercises/exercise-01-add-three-juice-touches.py) | A square that gets shake, particles, and a sound cue on click |
| [exercises/exercise-02-screenshake-and-particles.py](./03-exercises/exercise-02-screenshake-and-particles.py) | Screen-shake offset, particle list with decay, both event-driven |
| [exercises/exercise-03-tune-the-feel.py](./03-exercises/exercise-03-tune-the-feel.py) | Runtime sliders for shake magnitude, particle count, decay — playtest your own values |
| [challenges/README.md](./04-challenges/00-overview.md) | Index of weekly challenges |
| [challenges/challenge-01-juice-comparison-video.md](./04-challenges/challenge-01-juice-comparison-video.md) | Record a 30-second before/after video of your brick-breaker |
| [quiz.md](./05-quiz.md) | 10 multiple-choice questions |
| [homework.md](./06-homework.md) | Six practice problems for the week |
| [mini-project/README.md](./07-mini-project/00-overview.md) | Take your Week 2 brick-breaker, add three feel touches, record the comparison video |

## Frame budget for this week

A reminder of what 60 fps actually means, in milliseconds. Every C11 lecture returns to this tile.

```
┌─────────────────────────────────────────────────────────┐
│  FRAME BUDGET — 60 fps target, with juice               │
│                                                         │
│  Input poll:       ~0.2 ms                              │
│  Update (sim):     ~2.0 ms                              │
│  Collision:        ~1.5 ms                              │
│  Particles:        ~1.0 ms                              │
│  Render:           ~6.0 ms                              │
│  Screen-shake:     ~0.1 ms                              │
│  Audio mix:        ~0.3 ms                              │
│  GPU + present:    ~4.0 ms                              │
│  Headroom:         ~1.5 ms                              │
│  ─────────────────────                                  │
│  Total:           ~16.6 ms / frame                      │
└─────────────────────────────────────────────────────────┘
```

This week, **Particles** and **Audio mix** earn their rows for the first time. A few dozen particles cost almost nothing; a few thousand cost real frame time. Audio is cheap unless you trigger ten clones of the same sample in one frame. Get the budgets in your head now; Week 6 (Animation & juice) will spend them more aggressively.

## Stretch goals

If you finish early and want to push further:

- Read all of Steve Swink's *Game Feel* (the book — chapter excerpts are free online, and the Gamasutra essays it's based on are free in full). Notice that the book's structure mirrors this week's structure: define the term, list the techniques, measure them.
- Watch Jan Willem Nijman's GDC talk *The Art of Screenshake* end-to-end. It is the single most-watched game-feel talk on YouTube for a reason.
- Read Mark Brown's *Game Maker's Toolkit* essay/video on *The Genius of Doom (2016)'s Combat*. Notice how every term in this week's lectures appears in the analysis without being named.
- Pick a published indie game you love and write a 400-word analysis using ONLY this week's vocabulary. No "it feels good." No "polish." Use specific names.
- Implement **hit-stop** in your brick-breaker: on brick destruction, freeze the simulation for 50ms. Notice the disproportionate weight that one tiny pause adds.

## Voice rules for the week

- We do not say a game "feels good" or "feels bad" without naming what we mean. "The hit lacks weight" is more useful than "this feels bad."
- We credit Steve Swink, Doug Church, Robin Hunicke. We did not invent this vocabulary. Citing the lineage is part of being indie.
- We trust playtest data over our own taste. "Three of five testers smiled when the bricks exploded" beats "I think the particles are good."
- **Juice is information, not decoration.** Every effect must answer a player question — what happened, how big was it, was it good. If it doesn't, cut it.

## Up next

Continue to [Week 4 — Tilemaps and Levels](../week-04/) once you've pushed your juiced brick-breaker and the before/after video to GitHub.

---

*If you find errors in this material, please open an issue or send a PR. Future learners will thank you.*
