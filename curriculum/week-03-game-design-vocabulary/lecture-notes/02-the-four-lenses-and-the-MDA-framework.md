# Lecture 2 — The Four Lenses and the MDA Framework

> **Duration:** ~2 hours of reading.
> **Outcome:** You can name Doug Church's four lenses (Intention, Perceivable Consequence, Story, Goals), explain the MDA framework (Mechanics, Dynamics, Aesthetics) by Hunicke, LeBlanc, and Zubek, and apply both to a game you already know — your Week 2 brick-breaker.

If you only remember one thing from this lecture, remember this:

> **The designer ships Mechanics. The player feels Aesthetics. Dynamics is the bridge.** When a feature "doesn't feel right," the bug is usually in the bridge — the gap between the rule you wrote and the experience the player had.

---

## 1. Why a "framework" at all?

Last lecture we talked about *game feel* — the moment-to-moment sensation of pressing a button and watching the world respond. Feel is local. It lives inside a single interaction.

This lecture zooms out. We want vocabulary for talking about the *whole game* — why some games feel like a coherent design and others feel like a pile of mechanics. Designers have been trying to formalise this since the 1990s, and two attempts have stuck:

1. **Doug Church's *Formal Abstract Design Tools* (1999).** A short essay that proposed four "lenses" — Intention, Perceivable Consequence, Story, Goals — as the start of a shared vocabulary. Re-read every five years by anyone who designs games.
2. **Hunicke, LeBlanc, and Zubek's *MDA framework* (2004).** Three abstraction layers — Mechanics, Dynamics, Aesthetics — that map the gap between the designer's code and the player's experience.

Neither framework is complete. Both are useful. The third thing you need is your own taste, built over years of playing and shipping. The frameworks accelerate that taste; they don't replace it.

---

## 2. Doug Church's four lenses

In 1999, Doug Church (then at Looking Glass Studios, behind *Thief* and *System Shock 2*) wrote an essay titled *Formal Abstract Design Tools*. He argued that game designers spoke in vague terms — "good level design," "fun gameplay" — and that the field needed shared, abstract, formal tools the way architects have *space*, *axis*, and *threshold*. He proposed four.

### 2.1 Intention

> **Intention** is the player's ability to formulate a plan and act on it.

A game supports Intention when the player can look at the world, decide what they want to do, and then *do it*. The decision is theirs. The world responds.

Brick-breaker example: when the ball is approaching the paddle, the player decides *where they want the ball to go next* and positions the paddle to bounce it that way. The paddle English from last week — "centre hit goes straight, edge hit curves" — is the mechanism that gives the player Intention. Without paddle English, the player has no plan to make; the ball bounces deterministically.

Counter-example: a slot machine has no Intention. The player decides nothing. They pull a lever and watch.

### 2.2 Perceivable Consequence

> **Perceivable Consequence** means the player can see the result of their actions, immediately and clearly.

This is *adjacent to but distinct from* game feel. Game feel asks "does the button press feel responsive?" Perceivable Consequence asks "after the action completes, can the player tell what changed?"

Brick-breaker example: when the ball hits a brick, the brick disappears, the score ticks up, a sound plays. Three perceivable consequences. The player knows exactly what happened.

Counter-example: a brick that takes two hits but looks identical after the first hit. The player has no way to know whether their last action mattered. *Damaged-brick coloring* is the fix; we'll do it as a stretch goal in this week's mini-project.

### 2.3 Story

> **Story** is the narrative thread that runs through the play experience, whether authored or emergent.

Church wasn't talking only about *narrative* in the cutscene sense. He was talking about the *throughline* that ties one moment to the next. A speedrunner's story is "I optimised this jump for six months." A casual player's story is "I just barely cleared that wave." Both are stories.

Brick-breaker example: a basic brick-breaker has thin Story. *Arkanoid* (1986) added power-ups and bosses to thicken it. We won't add narrative this week, but the frame is worth holding: every game has a Story dimension, even one without dialogue.

### 2.4 Goals

> **Goals** are the things the player is trying to achieve, at every scale — micro-goal (bounce this ball), meso-goal (clear this row), macro-goal (clear all bricks).

A well-designed game has nested goals: a short-term goal that takes 5 seconds, a medium one that takes a minute, a long one that takes 20 minutes. They reinforce each other.

Brick-breaker example: micro-goal = land the ball on the paddle. Meso-goal = clear the row of bricks closest to the paddle. Macro-goal = clear the whole wall. If you only have one of those, the game is monotonous (all-micro) or unmotivating (all-macro).

### 2.5 Applying the four lenses to your brick-breaker

Hold each lens up to your Week 2 mini-project. Score it out of 5.

| Lens | What you check | Typical week-2 score |
|------|----------------|---------------------:|
| Intention | Can the player decide where to send the ball? | 3 (paddle English works, but no other tools) |
| Perceivable Consequence | Does every hit have a visible/audible response? | 2 (brick vanishes, score increments — no juice yet) |
| Story | Is there a throughline that ties one round to the next? | 1 (no progression, no levels) |
| Goals | Are there nested short/medium/long goals? | 3 (clear-row → clear-wall is two scales; lives gives a soft loss state) |

This is what the four lenses are for: a structured way to look at a thing you already have and see what's *missing* rather than what's wrong. The numbers don't matter; the *act of evaluating* matters.

---

## 3. The MDA framework

Five years after Church's essay, three researchers at Northwestern and a Game Developers Conference workshop proposed a different cut at the same problem.

**Hunicke, LeBlanc, and Zubek (2004) — *MDA: A Formal Approach to Game Design and Game Research*.** Three layers. Read in different directions depending on whether you're the designer or the player.

### 3.1 The three layers

- **M — Mechanics.** The rules. The code. The numbers in the configuration file. *Mechanics* are what you ship. A brick has 24 px of height, takes one hit, scores 10 points. Those are mechanics.
- **D — Dynamics.** What happens at runtime when players play. Mechanics interact; players make choices; patterns emerge. *Dynamics* are not in any one rule — they emerge from the rules in interaction.
- **A — Aesthetics.** The emotional response. *Aesthetics* are what the player feels. Tension, delight, frustration, surprise.

### 3.2 The two directions

Here is the part that makes MDA worth memorising.

> The **designer** sees the game in the order M → D → A. They write rules; the rules produce dynamics in playtest; the dynamics produce an aesthetic experience. The designer's job is to imagine A from a starting M.
>
> The **player** sees the game in the order A → D → M. They feel an experience; if they reflect, they notice the dynamics that produced it; only the most curious player ever asks about the mechanics underneath.

These are different orderings of the same thing. The trap is to assume your players see what you see. They don't. **They see Aesthetics first.** If the Aesthetic doesn't land, the rules can be perfect and the game will still fail.

### 3.3 The eight aesthetics (Hunicke et al.)

The MDA paper proposed a (deliberately incomplete) list of eight aesthetic flavours that games tend to deliver:

| # | Aesthetic | Plain English | Example game |
|---|-----------|---------------|--------------|
| 1 | **Sensation** | Pleasure of the senses | *Bejeweled* |
| 2 | **Fantasy** | Make-believe | *World of Warcraft* |
| 3 | **Narrative** | Drama | *The Walking Dead* |
| 4 | **Challenge** | Obstacle course | *Super Hexagon* |
| 5 | **Fellowship** | Social framework | *Animal Crossing* |
| 6 | **Discovery** | Uncharted territory | *No Man's Sky* |
| 7 | **Expression** | Self-discovery | *The Sims* |
| 8 | **Submission** | Pastime | *Solitaire* |

A game can target multiple aesthetics. Most games target two or three. **Brick-breaker is primarily Sensation (the satisfying smash) and Challenge (don't lose the ball).** Knowing that, you can prioritise the juice that *reinforces* Sensation and Challenge — i.e., impact effects on hit and ball-fall — and de-prioritise anything that doesn't (a long cutscene, an inventory).

### 3.4 The MDA worked example

Here is a brick-breaker design decision worked through the framework.

**Decision:** "Should we add a power-up brick that, when destroyed, gives the player a wider paddle for 10 seconds?"

| Layer | What the decision adds |
|-------|------------------------|
| **M (Mechanics)** | A new brick type; a `power_up_active` boolean on the paddle; a 10-second timer; a wider paddle hitbox. ~40 lines of code. |
| **D (Dynamics)** | Players now have a *strategic choice*: do I aim for the power-up brick first, or do I clear the lower rows first? The dynamic "risk vs reward" emerges. |
| **A (Aesthetics)** | Sensation (the wider paddle feels powerful), Challenge (the power-up is harder to reach), Goals (a new micro-goal appears). |

Notice how reading the framework top-to-bottom is the *designer's* reading: I add this mechanic, here is the dynamic it will produce, here is the aesthetic that lands.

Now read it bottom-to-top from a *player's* perspective: I felt powerful for ten seconds (A); I realised I'd been making a risk-reward tradeoff (D); I wondered what the underlying rule was (M). Most players never reach M. That's fine.

---

## 4. Where the frameworks help, and where they don't

Both frameworks are *vocabulary*, not algorithms. They will not tell you what to build. They will tell you how to *talk* about what you built. That's why they survive.

**They help when:**

- You're stuck in "this doesn't feel right" and need to name *which part* doesn't feel right. (Use the four lenses to localise: is it Intention? Perceivable Consequence?)
- You're playtesting and a tester says something vague. (Translate it to MDA: are they reporting an Aesthetic issue? A Dynamic? A Mechanic?)
- You're writing a postmortem and need shared terms. (Cite Church or MDA and your readers will know what you mean.)
- You're critiquing another designer's game. (The vocabulary keeps the critique constructive — "I think your Perceivable Consequence is weak on hit" beats "your game feels off.")

**They don't help when:**

- You're trying to figure out what to make in the first place. (Use prototypes, not frameworks. Build the thing, then evaluate.)
- You're stuck on a specific bug. (Frameworks don't fix bugs. Code fixes bugs.)
- You're designing a kind of game the framework's authors didn't anticipate. (MDA was written about competitive multiplayer arcade games; it bends a bit for purely meditative or social games.)

A framework is a flashlight. It lights up some corners of the room; the rest are still dark. You still need to walk around.

---

## 5. A taxonomy of "this feels off"

When a tester says "it feels off," translate it through the frameworks before responding. Here is a starter list.

| Tester says | Likely framework problem | Likely fix |
|-------------|--------------------------|------------|
| "I don't know what to do." | Weak **Goals** (Church). | Add a visible objective, a counter, a clear win-state. |
| "I pressed the button and nothing happened." | Weak **Perceivable Consequence** (Church). | Add immediate audio + visual feedback on input. |
| "I'm just bouncing the ball forever." | Weak **Story** / weak **Dynamics**. | Add progression — speed-up over time, level transitions. |
| "It's hard but in a way I don't enjoy." | Misaligned **Aesthetics** (MDA — Challenge instead of Sensation, or vice versa). | Decide which aesthetic you're targeting; tune challenge to it. |
| "The controls are sluggish." | **Game feel** (Swink) — input response. | Reduce input latency; check that input is read every frame. |
| "I don't know if I'm winning." | Weak **Perceivable Consequence** at the macro scale. | A scoreboard. A progress bar. Something that says "you are 40% there." |

Note that several of these map to *multiple* frameworks. That's fine. The frameworks overlap. They are vocabularies, not orthogonal axes.

---

## 6. A note on what these frameworks don't tell you

Both Church and the MDA authors were writing in the early 2000s, primarily about *competitive* and *single-player traditional* games. The vocabulary works less well for:

- **Mobile and casual games.** Where session length is 90 seconds and the goal-structure is "checkpoint → checkpoint → ad."
- **Walking simulators and narrative games.** Where Mechanics are deliberately thin and the Aesthetic is almost pure Narrative.
- **Live-service multiplayer.** Where the Dynamics layer is dominated by the *other players*, not the designer's mechanics.
- **Idle / incremental games.** Where the loop deliberately runs without the player and the Aesthetic is something like *anticipation*.

When you read modern design writing (Mark Brown's *Game Maker's Toolkit*, Tom Francis's blog, GDC talks from 2018+), you will see Church and MDA cited *as the foundation* and then extended. Read the foundation first. Then read the extensions.

---

## 7. Worked critique — your brick-breaker through both frameworks

Open your Week 2 brick-breaker. Play it for one minute. Then write — actually write, not just think — answers to these eight prompts.

**Church:**

1. Where does the player exercise *Intention*?
2. Is every action accompanied by *Perceivable Consequence* — visual, audio, or both?
3. What's the *Story* arc within a single play session?
4. What are the player's *Goals* at the micro, meso, and macro scales?

**MDA:**

5. List the three or four most important *Mechanics*.
6. What *Dynamics* emerge from those mechanics in actual play? (Tip: list things that happen that you didn't explicitly code.)
7. Which of the eight *Aesthetics* is your game primarily delivering?
8. Are there mechanics that don't serve the targeted aesthetic? (If yes, consider cutting them.)

Eight prompts. Twenty minutes of writing. By the end you have a vocabulary you can use to talk about your own game without sounding like a beginner. **That's the whole point of this lecture.** The frameworks are not for theory; they are for conversation.

---

## 8. Recap: what to take away

- **Doug Church (1999) — four lenses**: Intention, Perceivable Consequence, Story, Goals.
- **Hunicke, LeBlanc, Zubek (2004) — MDA**: Mechanics, Dynamics, Aesthetics; designer reads M→D→A, player reads A→D→M.
- The **eight aesthetics**: Sensation, Fantasy, Narrative, Challenge, Fellowship, Discovery, Expression, Submission. Most games target 2-3.
- **Frameworks are vocabulary, not recipes.** They help you talk about games; they don't tell you what to build.
- **The bridge between rules and feel is Dynamics.** When something "feels off," check the dynamic, not the rule.
- The mini-project this week asks you to *apply* this vocabulary to your own game by adding three feel touches and writing a 200-word reflection that uses these terms correctly.

The next lecture (Week 4) drops back into code: tilemaps, levels, camera follow. But you will use this lecture's vocabulary every time someone asks "why did you do it that way?" for the rest of the course.

---

*Lecture written for C11 · Crunch Arcade. Cite Doug Church (1999, *Formal Abstract Design Tools*) and Hunicke/LeBlanc/Zubek (2004, *MDA: A Formal Approach to Game Design and Game Research*) when reproducing these definitions.*
