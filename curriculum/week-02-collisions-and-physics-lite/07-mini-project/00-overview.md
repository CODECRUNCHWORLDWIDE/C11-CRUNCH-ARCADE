# Mini-Project — Brick Breaker (or Pong — your call)

> Build a small, complete Pygame game that lives on a single screen and uses every collision-and-physics idea from this week. The default pick is **Brick Breaker** — paddle, ball, brick wall, score, lives. If you prefer the constraints of a two-player local game, swap it for **Pong** — two paddles, one ball, two scores, first-to-eleven. Pick one. Ship one.

The point of this mini-project is to put a complete, playable thing in your repo by Sunday night. We have spent two weeks teaching primitives — main loops, delta time, vectors, AABBs, gravity, reflection. This week the primitives become a *game*: a thing with a start state, a win condition, a loss condition, and a number that goes up.

It is not a juicy game. It is not a polished game. It is a **prototype with all the parts**: rules, scoring, an end state. We'll add the polish in Week 3.

**Estimated time:** 10 hours (split across Wednesday → Sunday).

---

## What you will build

### Option A — Brick Breaker (default)

A single-window Pygame game called `brick_breaker` that:

1. Boots to a 960×600 window titled "Brick Breaker — C11 Week 2".
2. Shows a Coin-Pink paddle at the bottom the player drives with LEFT/RIGHT at ~480 px/s.
3. Shows a wall of bricks at the top — at least **3 rows × 10 columns** of Power-Up-Cyan bricks, each 80×24 with 4-px gaps.
4. Shows a 12-px Coin-Pink ball that starts pinned above the paddle.
5. Pressing SPACE launches the ball at roughly `(0, -360)` px/s plus a small random `vel.x`.
6. Ball bounces off the side walls and ceiling (restitution = 1.0).
7. Ball bounces off the paddle with "paddle English" — where on the paddle the ball lands biases its outgoing `vel.x`.
8. Ball overlapping a brick destroys the brick (one per frame max) and reflects on the smaller-overlap axis.
9. **Score** displayed top-left, increments by 10 per brick.
10. **Lives** displayed top-right, starts at 3, decrements when the ball falls past the bottom. On life loss, re-pin the ball to the paddle.
11. When all bricks cleared, show "YOU CLEARED THE WALL — press R to play again." When lives reach 0, show "GAME OVER — press R to restart."
12. R restarts the game. ESC quits.
13. Quits cleanly.

### Option B — Pong

A single-window Pygame game called `pong` that:

1. Boots to a 960×600 window titled "Pong — C11 Week 2".
2. Two paddles 12×96 each, Coin-Pink on the left, Power-Up-Cyan on the right.
3. Left paddle controlled with W/S; right paddle with UP/DOWN. Both at 480 px/s.
4. A 14×14 white ball that starts at the centre and launches in a random direction on SPACE.
5. Ball bounces off the top and bottom walls (restitution = 1.0).
6. Ball bounces off the paddles with the same paddle-English trick as Brick Breaker.
7. **Scores** displayed top-centre as `LEFT — RIGHT`, starting `0 — 0`.
8. When the ball passes a paddle, the opposite side scores and the ball re-centres.
9. First to 11 wins. Show "PLAYER 1 WINS — press R to play again." (or "PLAYER 2 WINS").
10. R restarts. ESC quits.
11. Quits cleanly.

Whichever you pick, the **collision spine** is the same: paddle-vs-ball, ball-vs-wall, ball-vs-something-it-destroys (a brick, or in Pong's case, the screen edge that triggers a score).

---

## Rules

- **You may** copy from your exercises, challenge, and homework — that's why those drills exist.
- **You may NOT** copy a "Pygame Breakout" tutorial from someone else's repo. Type your own. The chassis becomes muscle memory.
- **You may NOT** add sound, sprite art, or particle effects this week. Those are Week 3 / Week 6 lessons. Resist scope creep.
- You **must** use a virtual environment.
- Python 3.11+, Pygame 2.5+.
- `pygame.Rect` and `pygame.Vector2` are encouraged. Hand-rolled vector math is fine if you want it.

---

## Acceptance criteria

- [ ] A new public GitHub repo named `c11-week-02-brick-breaker-<yourhandle>` (or `c11-week-02-pong-<yourhandle>`).
- [ ] The repo's root contains: the main `.py` file, `requirements.txt` (or `pyproject.toml`), `.gitignore`, `README.md`.
- [ ] `python -m py_compile <main>.py` succeeds with no output.
- [ ] `python <main>.py` opens the window and the game is immediately playable.
- [ ] All ten functional requirements from the chosen option are met.
- [ ] Movement uses delta time. `dt` is clamped to `1/30` or sub-stepped when needed.
- [ ] The ball does not visibly tunnel through walls, bricks, or paddles at normal play speed.
- [ ] Closing the window does not throw a stack trace; the terminal returns to a prompt cleanly.
- [ ] `.gitignore` excludes `__pycache__/`, `.venv/`, `.DS_Store`.
- [ ] Your `README.md` includes:
  - One paragraph describing the game.
  - The exact commands to set it up from a fresh clone.
  - A list of the controls.
  - One short section titled "Things I learned building this."
  - One short section titled "Known issues / things I'd improve."

---

## Suggested order of operations (Brick Breaker variant)

Build incrementally rather than trying to write the whole thing at once. Each phase ends with a commit.

### Phase 1 — Boot + paddle (~45 min)

1. `mkdir brick-breaker && cd brick-breaker`
2. `python -m venv .venv && source .venv/bin/activate && pip install pygame && pip freeze > requirements.txt`
3. `.gitignore`: `__pycache__/`, `.venv/`, `.DS_Store`.
4. Minimum-viable Pygame loop. 960×600 window, dark-blue background, title set.
5. Add the paddle: a `Rect`, LEFT/RIGHT movement at 480 px/s, clamped to the window.
6. Commit: `Bootable window + paddle`.

### Phase 2 — Ball that bounces off walls (~1.5 h)

1. Add the ball: `Vector2` position, `Vector2` velocity, derived `Rect` for collision queries.
2. The ball starts pinned above the paddle (its `pos.y = paddle.top - 12`, its `pos.x` follows the paddle).
3. SPACE launches the ball with `vel = Vector2(random.uniform(-100, 100), -360)`.
4. After launch, integrate position from velocity each frame.
5. Wall collisions: snap-back-and-flip on left, right, top edges. Don't add a bottom wall — the ball falling past the bottom triggers a life-loss in a later phase.
6. Commit: `Ball launches and bounces off walls`.

### Phase 3 — Paddle collision with English (~1.5 h)

1. Ball-vs-paddle collision: `Rect.colliderect`. On hit, snap the ball above the paddle and reflect `vel.y` (always send upward — `vel.y = -abs(vel.y)`).
2. Apply paddle English: bias `vel.x` based on hit position. Centre = unchanged, edges = ±240.
3. Cap `vel.length()` to 700 px/s so the ball doesn't run away after many paddle hits.
4. Playtest: can you keep the ball alive for 30 seconds?
5. Commit: `Paddle collision with English`.

### Phase 4 — The brick wall (~2 h)

1. Build a list of `Rect`s for the bricks: 3 rows × 10 cols, 80×24 each, 4-px gaps, starting at `y = 60`.
2. Render each frame.
3. Ball-vs-brick collisions: iterate bricks, on first hit, remove the brick, reflect on smaller-overlap axis, `break`.
4. Commit: `Brick wall — destroy on hit`.

### Phase 5 — Score, lives, win/lose (~2 h)

1. Add a `score` integer. Increment by 10 per brick destroyed.
2. Add a `lives` integer starting at 3. When the ball's `pos.y > WINDOW_HEIGHT`, decrement lives and re-pin the ball.
3. Render score top-left, lives top-right, using `pygame.font.SysFont(None, 28)`.
4. When all bricks gone: enter a "you cleared the wall" state. Show the text. R restarts.
5. When lives reach 0: enter a "game over" state. Show the text. R restarts.
6. Commit: `Score, lives, win/lose states`.

### Phase 6 — Polish & ship (~2 h)

- Tune speeds and sizes. Playtest. If someone takes 30 seconds to clear a row, the bricks are too easy. If they lose a life in the first 5 seconds, the paddle is too narrow or the ball too fast.
- Set the window title to include the score: `pygame.display.set_caption(f"Brick Breaker — score {score} lives {lives}")`.
- Add a small "press SPACE to launch" hint when the ball is pinned.
- Write your README. Include a `gif/` folder with a short capture of gameplay if you can. Not required, but a portfolio repo with a GIF is worth a hundred without.
- Push to GitHub. Submit the repo URL on the course tracker.
- Commit: `Polish & README`.

---

## Rubric

| Criterion | Weight | What "great" looks like |
|----------|-------:|-------------------------|
| Runs | 20% | `python <main>.py` runs on a fresh clone in <30 seconds setup |
| Collisions | 25% | Ball cleanly bounces off paddle, walls, bricks. No tunneling at normal speed. No "stuck in wall" glitches. |
| Game-state flow | 15% | Title or first-launch, playing, win, lose, restart — all clean transitions |
| Code clarity | 15% | Functions or classes are short, each has one job, no dead code |
| README quality | 10% | Someone unfamiliar can clone and play in <5 minutes |
| "Things I learned" | 10% | At least 3 specific, non-trivial learnings (not "I learned collision") |
| Commit history | 5% | Multiple commits with meaningful messages (not just "wip") |

---

## Stretch (if you finish early)

These are *stretch*. Do **not** lose the main spec chasing them.

- **Variable-strength bricks.** Some bricks need two hits. Display a different colour for damaged bricks. Score 20 instead of 10.
- **A power-up brick.** 1 in 10 bricks, when destroyed, spawns a falling power-up the player catches. Options: extra life, double-wide paddle for 10 seconds, slow-mo ball.
- **Multiple balls (stretch+).** When the player catches a multi-ball power-up, the ball splits into two. Track a list of `Ball` instances and the same collision loop handles all of them.
- **Brick layouts from a file.** A `levels/01.txt` with `X` for "brick here" and `.` for "no brick", 10 columns × N rows. Load it at startup. This is a tiny preview of Week 4's tilemap.
- **A "started" overlay.** Title screen with the game name, press SPACE to start. Reset to title on game-over.

---

## What this prepares you for

- **Week 3** (Game design vocabulary) takes your brick-breaker and adds three "feel" touches — screen shake, particle burst, sound cue. Same code, more polish.
- **Week 4** (Tilemaps) reads the brick layout from a file and lets you design 10 levels in 10 minutes.
- **Week 5** (State machines) makes the title→playing→pause→game-over transitions explicit instead of a tangle of booleans.
- **Week 11** (Playtesting) puts your game in front of 5 people and asks them what's confusing. Several will be confused by your brick-breaker. That's data.

---

## Resources

- Your own [Lecture 1](../02-lecture-notes/01-aabb-collision-and-rectangles.md) and [Lecture 2](../02-lecture-notes/02-velocity-gravity-and-the-bouncing-ball.md).
- The week's [exercises](../03-exercises/) — copy from them.
- The week's [challenge](../04-challenges/challenge-01-brick-breaker.md) — *especially* the hints.
- [Pygame docs](https://www.pygame.org/docs/) — keep `Rect`, `Vector2`, `key`, `draw` open.
- The original [Atari Breakout](https://en.wikipedia.org/wiki/Breakout_(video_game)) Wikipedia page for context. Worth ten minutes.

---

## Submission

When done:

1. Push your repo to GitHub with a public URL.
2. Make sure `README.md` includes the setup commands and the controls.
3. Make sure `python -m py_compile <main>.py` is clean on a freshly cloned copy.
4. Capture a 5–10 second GIF if you can. Add it to the repo. Tweet, post, or share.

You shipped a **prototype with rules and a score**. That's a small but meaningful step from last week's moving-circle prototype. **You did not ship a game** — a game has audio, juice, level design, and a UX flow. We will get there. For now: well done, the bones of an arcade title work.
