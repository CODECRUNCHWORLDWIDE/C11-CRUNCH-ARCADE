# Mini-Project — A Player Character with Clean States and Transitions

> Build a player character driven by a State pattern FSM with **at least four states** (`idle`, `run`, `jump`, `fall`, with `hurt` strongly recommended), clean transitions, an `enter` / `update` / `exit` lifecycle, and the character running on top of your Week-4 tilemap. Record a 30-second video showing the character moving through every state. Write a 250-word reflection. Push to GitHub.

This is the artefact this week was building toward. By Sunday you have a small, playable character whose behaviour is *structured* — the code shape matches the mental model, and adding a new state next month will cost you twenty lines and a class definition, not three hundred lines and a re-read of the whole file.

The mechanic is intentionally simple — walk, jump, fall, take damage from spikes, recover — because the work this week is the *character architecture*, not new mechanics. Week 6 adds animation; Week 7 adds save state. But it all starts with this: states as classes.

**Estimated time:** 10.5 hours (split across Wednesday → Sunday).

---

## What you will build

A new repo (or a `state-machine-player/` subfolder of your portfolio repo), with:

1. **An engine** — Python codebase, ~500-700 lines, that loads a Week-4 tilemap and drives a character whose behaviour is defined by the State pattern.
2. **At least four states** for the player: `IdleState`, `RunState`, `JumpState`, `FallState`. A fifth — `HurtState` — is strongly recommended and is what graduates this from "I implemented the State pattern" to "I shipped a character."
3. **An `AirborneState` parent** for `JumpState` and `FallState`. This is the *hierarchical FSM* from Lecture 2 §4 in its simplest form.
4. **An explicit state diagram** committed to the repo as `docs/diagram.png` (or `.svg`, or even ASCII `.txt`). The diagram is the source of truth; the code follows.
5. **A pause overlay** built on the state stack from Exercise 3. ESC pauses; ESC again resumes. The player's FSM state survives the pause.
6. **At least one spike block** in the level. Walking into a spike triggers `HurtState` via `Character.take_hit()`.
7. **A HUD** that displays the current state's class name, the player's `vx`/`vy`, and the FPS.
8. **A 30-second comparison video** showing the player passing through every state.
9. **A 250-word reflection** in `REFLECTION.md` using this week's vocabulary correctly.

You will NOT add:

- New mechanics beyond walk + jump + fall + hurt. (Week 6+.)
- Animation. (Week 6.)
- Multiple enemies. (Week 11 capstone; or do the optional challenge.)
- A save system. (Week 7.)
- Online multiplayer. (Not in this course.)

---

## Rules

- **You may** copy from this week's exercises freely — that's why they exist. The `State` base class and the four core state classes from Exercise 2 are intended as your starting point.
- **You may** reuse your Week-4 tilemap loader, camera, and AABB-vs-grid collision verbatim. Those are solved problems; don't re-solve them.
- **You may NOT** keep a `is_jumping: bool` or `is_falling: bool` field on `Character`. The State pattern *replaces* those flags. If you find one in your code after Wednesday, delete it.
- **You may NOT** scatter `vy = -JUMP_VEL` outside of `JumpState.enter`. Side effects of *becoming a jumper* live in *the entry hook of the jump state*. This is the discipline the lecture exists to instill.
- **You may NOT** write a transition table at the top of the file. The State pattern's whole point is that transitions are decided inside each state's `update`. If you have a `TRANSITIONS: dict` you've drifted back to the hand-rolled FSM.
- **You must** commit the state diagram. This is the design artefact; without it the code has no reviewer.
- **Python 3.11+, Pygame 2.5+.**
- **Use a virtual environment.**

---

## Acceptance criteria

- [ ] A repo (or subfolder) called `c11-week-05-state-machine-<yourhandle>`.
- [ ] `python -m py_compile main.py` succeeds with no output.
- [ ] `python main.py` opens a window with a Coin-Pink player on a tilemap from Week 4.
- [ ] The player has **at least four states**, each its own class: `IdleState`, `RunState`, `JumpState`, `FallState`. (Five with `HurtState` is the recommended target.)
- [ ] Each state class has explicit `enter`, `update`, and `exit` methods. Empty bodies are written as `pass` rather than left implicit.
- [ ] The player can walk left/right, jump, fall, and (if implementing `HurtState`) take damage from at least one spike block in the level.
- [ ] The HUD shows the current state's class name (`state: IdleState` etc.) and updates within one frame of any transition.
- [ ] Every transition prints a log line to the console: `[fsm] IdleState -> RunState`.
- [ ] Pressing ESC pauses (pushes a `PauseState` on the game-state stack). Pressing ESC again resumes. The player's FSM state, `vx`, `vy`, and position are preserved across the pause.
- [ ] A spike block exists; walking into it triggers `HurtState` (if you implemented it). The hurt state lasts ~500 ms and the player flashes red during it.
- [ ] A `JumpState` and `FallState` both inherit from a shared `AirborneState` parent. The shared physics (gravity, airborne horizontal control) lives in the parent.
- [ ] The camera follows the player smoothly (lerp or dead-zone — your call from Week 4), clamped to level bounds. Reuse your Week-4 camera.
- [ ] A `docs/diagram.png` (or `.svg`, or `.txt`) shows the state diagram. Every transition in the code is an arrow in the diagram.
- [ ] A 25-40 second video at `demo.mp4` (or linked from `README.md`) shows the player passing through every state, including a pause and a spike hit.
- [ ] A 250-word `REFLECTION.md` at the repo root that:
  - Describes one bug from Week 4 that the state-machine refactor either fixed or made structurally impossible.
  - Names which states you implemented and which (if any) you deliberately deferred to later weeks.
  - Cites both lecture notes by name.
  - States ONE thing you would do differently next time.
- [ ] Updated `README.md` includes:
  - A controls section.
  - A "How to add a new state" section (in three steps: subclass `State`, define `enter`/`update`/`exit`, add the transition `change_state(NewState())` from whatever existing state should reach it).
  - The state diagram inlined or linked.
  - Credits for any tile assets used.

---

## Suggested order of operations

Build incrementally rather than trying to write the whole thing at once. Each phase ends with a commit.

### Phase 1 — Tag the "before" and copy the scaffolding (~30 min)

1. Tag your Week-4 platformer repo: `git tag week-04-final`. You'll want a clean comparison point.
2. Create the new repo. Copy your Week-4 `main.py`, `levels/`, and asset folder.
3. Copy `exercise-02-character-with-states.py` into a new file `state_machine.py` in the same directory.
4. Commit: `Initial skeleton; Week-4 platformer + State-pattern starter.`

### Phase 2 — Replace the player update with the State pattern (~2 h)

1. Open `main.py` and find the player update function. Delete the `is_jumping` / `is_grounded` / `is_falling` boolean cluster.
2. Replace the `Character` dataclass with the State-pattern `Character` from Exercise 2 (the one whose `update(dt)` delegates to `self.state.update(self, dt)`).
3. Import the four state classes from `state_machine.py`. Wire them up so `Character.__init__` starts in `IdleState`.
4. Hook the player's input — `move_input`, `jump_pressed_this_frame` — into the same fields the State pattern reads.
5. Run. Walk around. Jump. The behaviour should be *identical* to Week 4. The code shape is what changed.
6. Commit: `Replace boolean-flag player with State pattern.`

### Phase 3 — Bind the FSM into the tilemap collision (~1.5 h)

1. Your Week-4 AABB-vs-grid collision sets `grounded = True` when a downward collision resolves. That signal is what the State pattern reads. Make sure `Character.grounded` is correctly set every frame *before* `Character.update(dt)` is called.
2. Confirm: walking off a ledge transitions `RunState -> FallState`. Landing transitions `FallState -> IdleState`.
3. The "fell off ledge" case: if `not grounded and was_grounded`, you want `IdleState` and `RunState` to transition to `FallState`. The `if not char.grounded: char.change_state(FallState())` lines from Exercise 2 should already handle it — verify.
4. Commit: `Wire FSM into Week-4 collision; ledge and landing work.`

### Phase 4 — Add `HurtState` and the spike (~2 h)

1. Add at least one spike tile to one of your CSV levels. Use a new tile-integer (e.g. `7`).
2. In your level loader, build a `spikes` list of `pygame.Rect`s alongside the collision grid.
3. In the per-frame update, after collision is resolved, loop the spikes and call `char.take_hit(spike_centre_x)` on collision.
4. Implement `HurtState` if you haven't (copy from Exercise 2). Test: walk into a spike. The player flashes red, gets knocked back, is briefly invincible.
5. Confirm: while in `HurtState`, jump input is ignored (no transition to `JumpState`). This is the structural payoff — you didn't add a `if not is_hurt:` guard; the hurt state simply doesn't *have* a `change_state(JumpState())` in its update.
6. Commit: `Add HurtState and spike interaction.`

### Phase 5 — Add the pause stack (~1.5 h)

1. Lift the `App` + state-stack pattern from Exercise 3 into your main loop.
2. Wrap your existing gameplay into a `GameplayState`. The State-pattern player FSM is *inside* `GameplayState` — two FSMs running at different scales: the outer game-flow stack, the inner player FSM.
3. Add `PauseState`. ESC during gameplay pushes pause; ESC during pause pops it.
4. Confirm: pause freezes everything. The player's `vy` is preserved across the pause; on resume, mid-air physics continue from where they left off.
5. Commit: `Add pause overlay via state stack.`

### Phase 6 — Diagram + HUD + cleanup (~1 h)

1. Draw the state diagram. Photo or SVG. Commit to `docs/diagram.png`.
2. Make sure the HUD shows the state's class name and updates within one frame of transitions.
3. Sweep the code for stray `is_*` flags. There should be none on `Character` (other than the cross-state ones like `invincible`).
4. Run the linter / py_compile. Fix any warnings.
5. Commit: `Add state diagram; HUD shows state; cleanup.`

### Phase 7 — Record the demo + write the reflection (~1.5 h)

1. Screen-record a 25-40 second pass through every state: idle → run → jump → fall → idle → hurt → recover, plus a pause and resume.
2. Export as `demo.mp4`. Commit (or upload externally and link).
3. Write `REFLECTION.md`. 250 words. Cite both lectures. Name the bug the refactor killed.
4. Final commit: `Add demo video and reflection.`
5. Push. Verify the repo URL works on a fresh clone.

---

## Rubric

| Criterion | Weight | What "great" looks like |
|----------|-------:|-------------------------|
| Four (or more) distinct states implemented as classes | 25% | Each in its own class; no boolean flags on `Character` that duplicate the FSM. |
| State pattern correctness (enter/update/exit) | 15% | Every class has all three methods explicitly. `enter` does setup; `exit` undoes it. |
| Hierarchical FSM (AirborneState parent) | 10% | `JumpState` and `FallState` share their physics via inheritance, not copy-paste. |
| Pause stack | 10% | Pause is a push; gameplay state is preserved. ESC resumes cleanly. |
| State diagram | 10% | Diagram exists, is committed, and matches the code. |
| Spike + HurtState | 10% | The spike triggers HurtState; jump input is ignored during hurt. |
| Demo video | 10% | 25-40 seconds, every state visible, ≤ 50 MB. |
| Reflection (vocabulary correctness) | 8% | Cites both lectures; names states; uses week's terms correctly. |
| Commit history | 2% | One commit per phase; meaningful messages. |

---

## Stretch (if you finish early)

These are *stretch*. Do **not** lose the main spec chasing them.

- **A `wall_slide` state.** Subclass `AirborneState`. Trigger when the player is airborne, against a wall, and pressing toward it. Modify gravity (slower fall) and unlock a wall-jump. The full HFSM workout.
- **A `dash` state.** A burst of horizontal speed for 200 ms. Transitions from `IdleState` or `RunState` on a `Z` press. Exits to `IdleState` on timer-done. This is the exact pattern *Celeste*'s Madeline uses.
- **A `coyote_time` window.** After the player leaves the ground without jumping (transitions `IdleState`/`RunState` -> `FallState`), allow a 80-100 ms grace period during which the jump input still works. This is a *parameter on `FallState`*, not a new state — set `self.coyote_t = 0.08` in `FallState.enter`, decrement in `update`, and allow `change_state(JumpState())` while `self.coyote_t > 0`.
- **Animation event hooks (no art).** In `RunState.enter` and `RunState.exit`, print `[anim] play(run_loop)` and `[anim] stop`. Same for every other state. You won't see anything on screen, but the *hooks are wired*. Week 6 lights them up.
- **Apply the FSM to an enemy.** This is essentially the [Challenge 1](../04-challenges/challenge-01-enemy-ai-fsm.md) — `patrol`, `chase`, `attack`, `return`. Add one enemy to the mini-project. Each enemy is its own `Character` instance, each in its own state. The pattern is the same.
- **State-leak audit.** Walk through every `Character` field and ask: "which state writes this? which state reads this?" If the answer for any field is "more than two states write it," it's a candidate state-leak risk. Refactor: move the field to the state that owns it, or document it on `Character` with a comment explaining its lifecycle.

---

## What this prepares you for

- **Week 6** (Animation & juice) adds sprite-sheet animation. Your `enter` and `exit` hooks become `play_animation("run_loop")` and `stop_animation()`. The architecture you wired this week makes Week 6 mostly *visual* work.
- **Week 7** (Save & load) serialises the player. You'll need to think about *which state to load into* — `IdleState` is the safe default, but if the player saved in mid-air, do you load into `FallState`? The state-machine design is what makes that question even *expressible*.
- **Week 9** (Pygame → Godot port). Godot has a built-in `AnimationStateMachine` node and a more general state-machine pattern. The four classes you wrote map to four `Node` states in Godot. The port is mostly translation, not redesign.
- **Week 11** (Playtesting). When a tester says "the player gets stuck in a weird state after taking damage on a ladder," your first move will be to look at the diagram, find the missing transition, and add it. The diagram is the debugging surface.

---

## Resources

- This week's [Lecture 1](../02-lecture-notes/01-hand-rolled-fsm.md) and [Lecture 2](../02-lecture-notes/02-state-transitions-and-substates.md).
- The week's [exercises](../03-exercises/) — copy from them.
- The week's [challenge](../04-challenges/challenge-01-enemy-ai-fsm.md) — the enemy FSM is the natural stretch after the player.
- Bob Nystrom — *Game Programming Patterns*, chapter "State": <https://gameprogrammingpatterns.com/state.html>
- Kenney — free sprite/tile packs at <https://kenney.nl/assets>

---

## Submission

When done:

1. Push your repo to GitHub with a public URL.
2. Make sure `README.md` links to `demo.mp4` and credits any assets.
3. Make sure `docs/diagram.png` shows the state diagram.
4. Make sure `python -m py_compile main.py` is clean on a freshly cloned copy.
5. Submit the repo URL on the course tracker.

You replaced a tangle of booleans with a state machine. That is the architectural shift this whole phase has been pushing toward at character-scale. Next week we paint the muscles — sprite-sheet animation, tweening, juice — on top of the bones you wired this week.
