# Mini-Project — Crunch Dot

> Build a tiny single-screen game called **Crunch Dot**: a player circle the user moves with WASD, on a screen with two AI dots that bounce around. The player must collect score-pickups while avoiding the bouncers. No collisions need to be precise this week — it's a prototype to practise the game loop, delta time, and clean input handling. Polish is encouraged but not required.

This is the only mini-project in C11 where the spec is "movement and a counter, that's it." The point is to build **the spine** every other game in this course will hang from — a clean main loop, delta time everywhere, input that reads correctly. Get this scaffold right and the rest of the term is sprite art and mechanics.

**Estimated time:** 10 hours (split across Wednesday, Thursday, Friday, Saturday, Sunday).

---

## What you will build

A single-window Pygame game called `crunch_dot` that:

1. Boots to a 960×540 window titled "Crunch Dot — C11 Week 1".
2. Shows a player circle (Coin Pink, 16-px radius) starting in the centre.
3. Reads WASD to move the player at 280 px/s, with diagonals normalised and edges clamped (Exercise 3, basically).
4. Has two **bouncer dots** (Power-Up Cyan, 12-px radius) that bounce around at 200 px/s on randomised initial velocities, reflecting off all four edges (Challenge 1, basically).
5. Spawns a **pickup dot** (white, 8-px radius) at a random position on screen. When the player's circle overlaps the pickup, the pickup despawns, the player's score increments by 1, and a new pickup spawns at a new random position.
6. Displays the current score in the top-left corner using `pygame.font`.
7. Displays the current fps in the top-right corner.
8. Quits cleanly on X / Cmd-Q / Escape.

By the end you have a public GitHub repo of ~200 lines of code that demonstrates every concept this week: game loop, delta time, WASD input, multiple moving entities, simple distance-based collision, on-screen text. You will refer back to this as a template in Weeks 2–6.

---

## Rules

- **You may** use any of your exercise / homework / challenge code as starting material — copying yourself is fine, this is what those drills were for.
- **You may NOT** copy a "Pygame template" from someone else's repo. Type your own scaffold; it's how the loop becomes muscle memory.
- **You may NOT** add sound, animation, or sprite art this week. Those are upcoming weeks' lessons. Resist scope creep.
- You **must** use a virtual environment.
- Python 3.11+, Pygame 2.5+.

---

## Acceptance criteria

- [ ] A new public GitHub repo named `c11-week-01-crunch-dot-<yourhandle>`.
- [ ] The repo's root contains: `crunch_dot.py` (or `crunch_dot/__main__.py` if you went modular), `requirements.txt` or `pyproject.toml`, `.gitignore`, `README.md`.
- [ ] `python -m py_compile crunch_dot.py` succeeds with no output.
- [ ] `python crunch_dot.py` opens a 960×540 window.
- [ ] WASD moves the player at 280 px/s with diagonals normalised.
- [ ] Two bouncer dots are visibly moving and visibly bouncing off all four edges.
- [ ] A white pickup dot is visible somewhere; when the player overlaps it, the pickup relocates to a new random spot and the score increments.
- [ ] The score is displayed in the top-left, the fps in the top-right.
- [ ] Closing the window does not throw a stack trace; the terminal returns to a prompt cleanly.
- [ ] `.gitignore` excludes `__pycache__/`, `.venv/`, `.DS_Store`.
- [ ] Your `README.md` includes:
  - One paragraph describing the game.
  - The exact commands to set it up from a fresh clone.
  - A list of the controls.
  - One short section titled "Things I learned building this."
  - One short section titled "Known issues / things I'd improve."

---

## Suggested order of operations

You'll find it easier if you build incrementally rather than trying to write the whole thing at once. Each phase ends with a commit.

### Phase 1 — Boot a window (~30 min)

1. `mkdir crunch-dot && cd crunch-dot`
2. Create and activate a venv: `python -m venv .venv && source .venv/bin/activate`.
3. `pip install pygame`. `pip freeze > requirements.txt`.
4. Write `.gitignore` (`__pycache__/`, `.venv/`, `.DS_Store`).
5. Create `crunch_dot.py` with the minimum-viable Pygame loop from Lecture 1 §3, but at 960×540 with the right title.
6. `git init`, commit: `Bootable window`.

### Phase 2 — Add the player (~1.5 h)

1. Refactor your loop so the game state lives in variables at the top of `main()`: `player_pos: pygame.Vector2`.
2. Add a `read_input(keys) -> Vector2` function that returns a normalised direction vector based on WASD.
3. In your update step, move the player. In your render step, draw a Coin-Pink circle at the player position.
4. Clamp the player to the window edges.
5. Run it. The player should move at 280 px/s, diagonals normalised, can't leave the screen.
6. Commit: `Player WASD movement`.

### Phase 3 — Add the bouncers (~2 h)

1. Define a `Bouncer` class (or `dataclass`) with `pos: Vector2`, `vel: Vector2`, `radius: int`, and an `update(dt)` method.
2. In `update(dt)`, move the bouncer by `vel * dt`, then check each edge. If past an edge, snap-back-and-flip (see Challenge 1).
3. Create two bouncers with `random.uniform(-200, 200)` velocity components — re-roll if the magnitude is under ~100 so neither bouncer starts stationary.
4. Update and draw both. They should both visibly bounce.
5. Commit: `Bouncer dots that bounce`.

### Phase 4 — Add the pickup (~1.5 h)

1. Define a `Pickup` with `pos: Vector2` and a `respawn(screen_size)` method that picks a random `pos` inside a margin.
2. Spawn one pickup at start.
3. In the update step, check distance from player to pickup. If less than `player_radius + pickup_radius`, the player is touching the pickup. Increment the score and call `respawn`.

   **Distance check.** Cheaper version (no sqrt):

   ```python
   delta = player_pos - pickup.pos
   if delta.length_squared() < (player_radius + pickup_radius) ** 2:
       score += 1
       pickup.respawn(screen_size)
   ```

4. Draw the pickup. Run. Walk into it. Watch the score climb.
5. Commit: `Pickups and scoring`.

### Phase 5 — Add the HUD (~1 h)

1. Create a font once at startup: `font = pygame.font.SysFont(None, 28)`.
2. Each frame, render the score and fps with `font.render(text, True, colour)`.
3. Blit each rendered surface at `(10, 10)` and somewhere near the top-right.
4. Update the fps text only twice per second so it isn't strobing — keep a `text_refresh_accumulator` and a cached surface.
5. Commit: `Score and fps HUD`.

### Phase 6 — Polish & ship (~2.5 h)

- Tune speeds and radii until it *feels* right. 280 px/s might be too fast for your screen — playtest. If your roommate plays it for 30 seconds, that's a playtest, even informal.
- Tweak the colours to match your taste while keeping Coin Pink for the player. Brand consistency.
- Add a one-line title bar in the window: include the score in the title, e.g. `pygame.display.set_caption(f"Crunch Dot — score {score}")`. Nice and lo-fi.
- Write your README. Include a `gif/` folder with a short capture of gameplay if you can — OBS or `ffmpeg` will make one. Not required, but a portfolio repo with a GIF is worth a hundred without one.
- Push to GitHub. Submit the repo URL on the course tracker.
- Commit: `Polish & README`.

---

## Rubric

| Criterion | Weight | What "great" looks like |
|----------|-------:|-------------------------|
| Runs | 25% | `python crunch_dot.py` runs on a fresh clone in <30 seconds setup |
| Loop hygiene | 20% | input → update → render order is clear; `dt` is in seconds; clamped |
| Code clarity | 15% | Functions or classes are short, each has one job, no dead code |
| Game state | 15% | Player, bouncers, pickup, score all coexist cleanly without globals everywhere |
| README quality | 10% | Someone unfamiliar can clone and play in <5 minutes |
| "Things I learned" | 10% | At least 3 specific, non-trivial learnings (not "I learned Pygame") |
| Commit history | 5% | Multiple commits with meaningful messages (not just "wip") |

---

## Stretch (if you finish early)

- **Movement smoothing.** Instead of jumping the player at full velocity instantly, accelerate over ~0.1 s and decelerate the same way when released. This is one of the cheapest game-feel improvements ever and you'll use it for the rest of your life.
- **A "danger" cooldown.** When the player overlaps a bouncer, flash the screen red for 0.2 seconds and decrement the score by 1 (clamped to 0). No game-over screen — that's Week 5. Just a feel test.
- **A second pickup type** worth 3 points, but only one of them is on screen at a time, and it moves slowly. Add a second `Pickup` subclass with `vel` and an update method.
- **A timer.** Display elapsed time in the centre top. Resets on Esc. This is the closest you can get to a "score attack" loop in 200 lines.

These are stretch. Do **not** lose the main spec chasing them.

---

## What this prepares you for

- **Week 2** (Collisions & physics-lite) wires the bouncers and the player together into something like brick-breaker. The `Bouncer` class you write here is the prototype of `Ball`.
- **Week 5** (State machines) takes your player from "always-movable circle" to "idle / moving / hurt" states. Today's `read_input` becomes one branch of an FSM.
- **Week 8** (Hello, Godot 4) re-implements Crunch Dot in Godot. You'll see in real time how the loop maps over. The exercise is roughly: "same game, 1/3 the code, plus signals."

---

## Resources

- Your own [Lecture 1](../lecture-notes/01-the-game-loop-and-why-it-exists.md) and [Lecture 2](../lecture-notes/02-delta-time-and-the-fixed-timestep.md).
- The week's [exercises](../exercises/) — copy from them, that's why they exist.
- [Pygame docs](https://www.pygame.org/docs/) — keep the `display`, `event`, `key`, and `draw` pages open in tabs.
- [Game Programming Patterns — Game Loop](https://gameprogrammingpatterns.com/game-loop.html) for theory.
- [Kenney.nl](https://kenney.nl/) if you decide to swap circles for sprites (don't, this week — but bookmark it).

---

## Submission

When done:

1. Push your repo to GitHub with a public URL.
2. Make sure `README.md` includes the setup commands and the controls.
3. Make sure `python -m py_compile crunch_dot.py` is clean on a freshly cloned copy.
4. Capture a 5-second GIF if you can. Add it to the repo. Tweet, post, or share. You built a tiny working game; show it.

You shipped a prototype. **You did not ship a game** — a game has audio, levels, art, and a UX flow. We will get there. For now: well done, the spine works.
