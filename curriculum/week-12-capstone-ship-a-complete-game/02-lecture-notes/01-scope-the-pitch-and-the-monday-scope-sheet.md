# Lecture 1 — Scope, the pitch, and the Monday scope sheet

The single most consequential decision of the capstone week is made on Monday morning, before any code is written. It is not a technical decision. It is a *scope* decision. The students who finish this week are not the ones with the most ambitious concept; they are the ones whose Monday concept was small enough that the Sunday build is recognisably the same project. This lecture is about how to make that decision well, how to write it down so you do not drift, and how to defend the decision against the predictable Wednesday-afternoon temptation to add one more thing.

This lecture is editorial in tone because scope is where the editorial voice earns its keep. There is no library function to call. There is no engine API to learn. There is only judgement, and the judgement is the muscle this lecture trains.

## The one-sentence pitch

A pitch is a *single sentence* that a stranger can read in three seconds and understand the entire game from. It has three parts: a *who* (or the implied second person), a *verb*, and a *constraint*. The constraint is the part that makes the game interesting; without it, the verb is a tech demo and the game is a toy.

Examples of pitches:

- *You are a frog. You cross a road. Cars get faster.*
- *You are a paddle. You hit a ball. If you miss, you lose.*
- *You are a ship in a vector field. You shoot rocks. Rocks split into smaller rocks.*
- *You are a snake. You eat dots. You cannot turn into yourself.*
- *You are a wizard on a 4x4 grid. You cast one of four spells per turn. The dungeon has five rooms.*

What those five share is a *who*, a *verb*, and a *constraint that makes the verb interesting*. The constraint is doing the heavy lifting. The frog without "cars get faster" is a frog crossing an empty road, which is a walking simulator. The paddle without "if you miss you lose" is a paddle hitting a ball, which is a screensaver. The constraint is the design.

Examples of *non-pitches* — these are theme statements, not pitches, and theme statements do not ship in a week:

- *A deep narrative roguelike about loss and redemption in a procedurally generated city.* No verb. No constraint. The player does not know what they do every five seconds.
- *A puzzle game where every level teaches you something new.* The constraint ("every level teaches something new") is impossible to scope; what is "something new" in level 47?
- *An atmospheric exploration game.* No verb. No constraint. "Atmospheric" is a *quality*, not a *mechanic*.
- *A multiplayer survival crafting MMO with bosses.* Four games in one sentence; pick one.

The difference is concrete and learnable. A pitch *says what the player does*. A theme statement *says how the player feels*. Both are valid creative directions; one of them ships in a week and one does not.

The discipline this Monday: write *twenty* pitches in the first hour. Quantity is the goal. Most will be bad. Some will be derivative. A few will be genuinely good. Pick the one that excites you *and* whose constraint feels achievable. If two pitches feel equally exciting, pick the one whose constraint is *less* ambitious — the smaller of two scoped games ships sooner and is the larger compounding investment in the toolbox.

## The verb test

A useful filter on the twenty pitches is the *verb test*. Read the pitch aloud. Ask: "What does the player do every five seconds?" If the answer is a single concrete action — *cross a road, hit a ball, shoot a rock, eat a dot, cast a spell* — the pitch passes. If the answer is a *story* — *explore, discover, learn, feel* — the pitch fails the verb test. The verb test is a five-second filter that rejects 80% of week-12-unsuitable pitches.

A pitch can pass the verb test and still be a bad fit for the capstone week. The verb test is necessary, not sufficient. The sufficient filter is the Monday scope sheet, below.

## The Monday scope sheet

The scope sheet is a *one-page document* that you write on Monday and keep open on your second monitor for the rest of the week. It is the contract you make with yourself. The fields are:

1. **Pitch.** The one-sentence pitch, copy-pasted.
2. **Verb.** The single verb the player does every five seconds. *Crosses, hits, shoots, eats, casts.*
3. **Goal.** The win condition. *Reach the other side. Score 11. Survive 60 seconds. Eat 100 dots. Clear all five rooms.*
4. **Obstacle.** The thing standing between the player and the goal. *Cars. The opponent paddle. Asteroids. Your own tail. Dungeon enemies.*
5. **Loop length.** How long a full run lasts. *60 seconds. 3 minutes. 5 minutes.* If the answer is "indefinite" or "as long as the player wants", you have an arcade game (good) or a sandbox (bad fit for the week).
6. **Screen count.** How many distinct screens the player sees. *Title. Playing. Game over.* That is three; that is the target. Five is the maximum. Seven is a rewrite.
7. **Subsystems used.** Which of Weeks 1-11 the capstone uses. *W1 (loop), W2 (collisions), W3 (verb-goal vocab), W6 (juice), W8 (audio), W11 (save).* That is six. Six is plenty. Listing all eleven is a yellow flag; the game is too big.
8. **Subsystems intentionally not used.** This field is more important than #7. *W4 (no tilemap; single-screen game). W9 (single-player only). W10 (no shaders; pixel art aesthetic is shader-free).* The list of things you are *not* doing is the list of features that cannot creep in on Wednesday.
9. **Asset list.** Every asset the game needs. *Player sprite, enemy sprite, projectile sprite, background tile (1), background music (1), three SFX (jump, hit, gameover), one font.* If the asset list is longer than 15 entries, the scope is too big.
10. **Cuts log.** Initially empty; populated through the week as you cut features. Each entry is one line: *Cut <feature> on <day> because <reason>*. By Sunday the cuts log is two pages long. Without the cuts log, the two pages of features got added on Wednesday and the build is broken on Saturday.

The mini-project folder of this week ships a `scope_sheet_template.md` that has these fields blank. You fill it in Monday. You do not modify it on Tuesday except to append to the cuts log. The scope sheet is the *contract*, and the cuts log is the *paper trail*.

## The Tuesday playable prototype gate

By Tuesday end-of-day, the project must satisfy the *playable prototype gate*. The gate has three conditions:

1. **The verb works.** When the player presses the input, the verb happens. The paddle moves. The ship rotates and accelerates. The frog hops. The visual is ugly placeholder squares; the input is real.
2. **The goal works.** A code path exists that, when the player meets the goal condition, transitions to a "you won" state. The state's visual is one line of text. The transition is real.
3. **The obstacle works.** A code path exists that, when the obstacle's condition is met (the car hits the frog, the asteroid hits the ship, the tail hits the head), transitions to a "you lost" state. The state's visual is one line of text. The transition is real.

The Tuesday gate is *not* about polish. It is not about art. It is not about audio. It is about whether the *core loop* — verb, goal, obstacle — is real and exercised by the play of the game. If at Tuesday lunch you have a beautiful title screen but no playable verb, the project is in trouble.

The cure for a missed Tuesday gate is *rescoping*, not pushing through. Drop a feature; drop the title screen for now; drop the second mechanic. The verb-goal-obstacle triangle is the spine of the build, and a build without a spine cannot be polished on Friday because there is no body to wrap polish around. Wednesday's art pass and Thursday's juice pass *assume* the Tuesday gate has been cleared. If it has not, polish becomes a way to avoid the real problem and Saturday's QA pass is a catastrophe.

The Tuesday gate is borrowed directly from the indie game development literature. Pirate Software's "How I shipped my game" talks, the GMTK channel's design videos, and the Mark Brown jam retrospectives all converge on the same advice: ship the playable prototype within 20% of the project budget. For a one-week capstone, 20% is Tuesday end-of-day. The numbers are not arbitrary; they are empirical, observed across thousands of shipped indie games.

## What to cut, and how to decide

Cutting is a learnt skill. The mistake most students make on a first capstone week is treating every feature in the Monday brainstorm as a commitment. It is not. The Monday brainstorm is a *menu*. The Monday scope sheet is what you ordered. The cuts log is what you sent back.

A useful cutting heuristic is the *rule of three* — every game has *exactly three* "delight" features and zero more. A delight feature is something the player will remember after the game is over: the screen-shake on hit (one), the way the music swells on the boss room (two), the easter egg in the title screen (three). Anything beyond three either is not a delight feature (it is mechanical baseline) or competes with the three you already have. Identify your three delight features in the Monday scope sheet under a special line; protect them; cut anything that does not serve them.

Another useful heuristic is the *if I had to cut one feature, which would I cut?* question, asked every Wednesday morning. If the answer is "easy, I would cut feature X", cut feature X now. The capstone is not improved by holding a feature whose removal you have already decided is the easy call.

A third heuristic is the *playtest the obstacle, not the system* rule. A capstone game whose obstacle is dynamic and reactive (cars get faster, asteroids respawn, the snake grows) is more interesting than one with a static obstacle (a single fixed enemy). If you have to cut, cut the *static* part — the title screen background animation, the second enemy type, the credits scroll's typewriter effect. Keep the dynamic obstacle. The obstacle is what makes the verb interesting; it is the last thing to cut.

## The Wednesday temptation

Wednesday afternoon is the hardest day of the week. Tuesday's gate is cleared, the build is playable, the *core* feels right, and the brain naturally wants to *add*. New enemy! New power-up! New level! New mode! Each addition feels small in isolation. Each addition is, in fact, small in isolation. The problem is that the *integration cost* of each addition is non-linear: a second enemy type doubles the test matrix; a third triples it; the screen-shake's interaction with the dissolve transition becomes a bug; the audio mixer's ducking starts pumping wrong; Sunday's build does not run on a friend's machine.

The discipline is: on Wednesday, you *spend* the day on art, audio, and the eleven-week subsystems integration. You do *not* spend the day adding new mechanics. The cuts log on Wednesday afternoon should grow by at least three entries. If it does not grow, you are not cutting hard enough.

A useful Wednesday-afternoon ritual: at 3 pm, set a 15-minute timer. In those 15 minutes, ask yourself: *what is the smallest change I could make today that would most increase the shipped quality of the game?* Almost never is the answer "add a new mechanic". The answer is usually "fix the screen-shake amplitude", "polish the death animation", "tighten the audio mix", "add the credits roll", "test on a friend's laptop". The 15-minute ritual is the antidote to the Wednesday temptation.

## The "would I play this for ninety seconds" test

A useful final filter on the Monday scope is the *ninety-second test*. Read the pitch aloud. Imagine yourself as a stranger discovering the game on itch.io. The page is okay. The screenshots are okay. The trailer is fine. Would you play the game for ninety seconds? The honest answer to that question is the ceiling on how much *anyone else* will play it. If the answer is "no, I would not play for ninety seconds", the pitch needs to change. If the answer is "yes, easily", scope it down anyway — the answer is usually overoptimistic.

A capstone game that holds a stranger's attention for ninety seconds has succeeded. A capstone game that holds a stranger's attention for ten minutes has *exceeded* the brief; very few one-week builds reach that bar, and the ones that do are usually scoped tighter, not larger, than the average week-12 build. Tightness is the path to delight; size is the path to mediocrity.

## A worked example of the scope sheet

To make the format concrete, here is the scope sheet for a hypothetical capstone built by an instructor over the course of one weekend. The game is *Frog Cross*, a small Frogger-likes-but-different prototype.

```text
PITCH: You are a frog. You cross a four-lane highway. Each crossing the cars get 10% faster.

VERB: Hop (one tile per input, four directions).

GOAL: Reach the top edge of the screen.

OBSTACLE: Cars in four lanes, each at a different base speed. Each successful crossing
          increments a global speed multiplier by 1.1x. Run ends when a car hits the frog.

LOOP LENGTH: 30-90 seconds per run, depending on player skill.

SCREEN COUNT: 3. Title, Playing, Game Over (with high score).

SUBSYSTEMS USED:
  W1  — Game loop. Per-frame car movement; per-frame collision check.
  W2  — Collisions. AABB-vs-AABB frog vs car.
  W3  — Vocab. Verb-goal-obstacle clearly named here.
  W5  — State machine. Title -> Playing -> GameOver -> Title.
  W6  — Juice. Frog hop squash. Car explosion. Screen shake on death.
  W7  — Save. High score in user://frogcross/high.json.
  W8  — Audio. Hop SFX, car SFX, gameover sting, ambient road loop.
  W10 — Shaders. Hit-flash on the frog; dissolve transition between states.
  W11 — Save (production). Atomic write of the high-score file. SHA-256 integrity.

SUBSYSTEMS INTENTIONALLY NOT USED:
  W4  — Tilemap. Single-screen game; no level data file needed.
  W9  — Multiplayer. Single-player only.

ASSET LIST:
  - Frog sprite (1, 4 directions; CC0 from OpenGameArt)
  - Car sprite (3 variants; CC0 from OpenGameArt)
  - Road tile (1, repeating; drawn by me, 12 minutes)
  - Background music (1 loop, CC-BY from Freesound, 90 seconds)
  - SFX: hop, splat, gameover, level-up (4, CC0 from Freesound)
  - Font: Press Start 2P (free Google Font)

DELIGHT FEATURES (3):
  1. The frog squash-on-hop is exaggerated; it sells the hop.
  2. The screen-shake amplitude scales with the speed multiplier; the late game feels frantic.
  3. The death animation has a 200 ms hit-pause and then a high-score-beats-old screen flash.

CUTS LOG (begin empty; append through the week):
  Mon  — Cut the river level (W4 tilemap; not needed for the road-only scope).
  Mon  — Cut the power-ups (would require a second mechanic; out of scope).
  Tue  — Cut the multiplayer mode (W9; single-player ships sooner).
  Wed  — Cut the second enemy type (truck); one car-type at three speeds is enough.
  Wed  — Cut the boss frog (out of scope; not in the pitch).
  Thu  — Cut the second background music track; one loop is fine.
  Fri  — Cut the day-night cycle; nothing in the pitch promised it.
  Sat  — Cut the achievements; itch.io has no API; not in pitch.

POST-SCRIPT ON SUNDAY:
  Shipped. itch.io URL: https://example.itch.io/frog-cross. 8 cuts. 38 hours. Worked.
```

That is the scope sheet for *Frog Cross*. It is one page. It fits in a single text file. It is the contract that, on Wednesday at 4 pm when you want to add a power-up, you read again and decide not to.

The version of the scope sheet in `mini-project/scope_sheet_template.md` has the fields blank. Open it Monday at 9 am. Close it Monday at 5 pm. Reopen it on Wednesday at 3 pm. Reopen it on Sunday at 8 pm to write the post-script. That is the rhythm.

## Picking a starting point

A frequent Monday question is *do I start from scratch or do I extend a prior week's project?* The answer is: *start from whichever produces a working playable prototype by Tuesday end-of-day*.

Starting points that have produced reliable wins in prior cohorts:

- **From scratch with a small pitch.** Pong. Snake. Asteroids. Frogger. Tetris (without the rotation system; just the falling blocks). One-screen arena shooter with one enemy type. The advantage is total control. The risk is that the basic engine setup eats Monday morning.
- **From your Week 6 mini-project.** Most Week 6 builds already have a playable loop with juice. Add a death state, a title screen, a high-score table; you have a shipped game.
- **From your Week 7 or Week 11 mini-project.** A save system on a one-screen prototype is already 60% of a shipped game. Add a title screen and a death state.
- **From your Week 10 mini-project.** A shader-polished prototype is the most visually mature starting point. Add a death state and a credits screen.

Starting points that have *not* produced reliable wins:

- **From your Week 4 mini-project.** Tilemap-heavy games are tempting because the editor work is fun, but the *content* requirement (designing enough levels for a complete game) eats the week. If you start from Week 4, scope to *one* level.
- **From your Week 9 mini-project.** Multiplayer is a force multiplier on every other bug. Capstones with multiplayer at the centre are routinely 50% behind schedule by Wednesday. If you absolutely must, keep it local two-player on a shared keyboard.
- **From scratch with no pitch.** You spend Monday brainstorming and Tuesday writing engine plumbing. Pick a pitch first.

The capstone is graded on *whether the game ships*, not *how ambitious the starting point was*. A Pong with screen-shake that ships on Saturday night beats an unreleased JRPG every time.

## Summary, end of lecture

Twelve weeks of work has produced a toolbox of subsystems and a learnt design vocabulary. The capstone is the integration test. Scope is the variable that determines whether the integration test passes. The Monday scope sheet is the contract; the Tuesday playable gate is the proof; the cuts log is the paper trail; the ninety-second test is the final filter. The students who ship are the ones who internalise that scope is the design — not the obstacle to the design.

Tomorrow's lecture covers the export pipeline — getting the build off your machine and into a folder a stranger can download. The day after, the itch.io page and the 30-second trailer. By Friday the shipping pipeline is end-to-end and the rest of the week is execution.
