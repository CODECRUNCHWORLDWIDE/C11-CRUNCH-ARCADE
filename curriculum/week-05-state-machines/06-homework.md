# Week 5 Homework

Six practice problems that revisit the week's topics. The full set should take about **5–6 hours** in total. Work in your Week 5 Git repository so each problem produces at least one commit you can point to later.

The work this week is *re-shape the code you already wrote*. By Sunday your Week 4 platformer player should be unrecognisable in the best possible way — same physics, same controls, completely different code shape underneath.

Each problem includes:

- A short **problem statement**.
- **Acceptance criteria** so you know when you're done.
- A **hint** if you get stuck.
- An **estimated time**.

---

## Problem 1 — Draw the diagram for the player you already have

**Problem statement.** Before you change any code, open `exercise-02-character-with-states.py`. On paper (or in any free state-chart drawing tool such as the XState visualiser), draw the full state diagram for the five states (`idle`, `run`, `jump`, `fall`, `hurt`). Boxes are states. Arrows are transitions. Label each arrow with its triggering event or condition. Then take a photo (or export PNG) and commit it.

**Acceptance criteria.**

- A file `homework/p1_diagram/diagram.png` (or `diagram.svg`) exists and shows all five states.
- Every transition from Exercise 2 is represented as a labelled arrow. There should be at least eight.
- Transitions that are "from any state" (e.g. `take_hit -> HURT`) are drawn as a shared arrow into `HURT` from a meta-box labelled "any non-hurt state."
- A `homework/p1_diagram/NOTES.md` (50-75 words) names one transition you got wrong on the first draft and what you missed.

**Hint.** The transitions you forget are usually the *leaving* ones. `HURT -> ???` is easy to forget because in code it's a timer-driven transition (when `self.timer <= 0`) rather than an explicit event. Make the timer arrow visible: label it `timer_done`.

**Estimated time.** 25 minutes.

---

## Problem 2 — Add a fifth state to the hand-rolled FSM

**Problem statement.** Take `exercise-01-fsm-from-nested-ifs.py` (the hand-rolled FSM) and add a `CROUCH` state. While crouching: `vx` is halved; jumping is disabled; pressing DOWN keeps you crouching, releasing DOWN returns you to idle. The point of this problem is to feel the *mechanical* nature of adding a state to a hand-rolled FSM: edit five places, all named.

**Acceptance criteria.**

- A file `homework/p2_hand_rolled_crouch.py` runs and the player can crouch by holding DOWN (or `S`).
- The `State` enum has a `CROUCH` entry.
- The `Event` enum has `CROUCH_PRESSED` and `CROUCH_RELEASED` entries.
- The `TRANSITIONS` dict has `(IDLE, CROUCH_PRESSED) -> CROUCH`, `(RUN, CROUCH_PRESSED) -> CROUCH`, and `(CROUCH, CROUCH_RELEASED) -> IDLE`.
- The `run_state` function has a branch that halves `vx` when `state == CROUCH`.
- The HUD prints `state: crouch` while crouching.
- A `homework/p2_crouch_note.md` (50-100 words) lists the five places you edited and confirms no other places had to change.

**Hint.** The transition `(JUMP, CROUCH_PRESSED) -> ???` is deliberately missing. You can't crouch in mid-air. That absence is the guard. (You could add `(JUMP, CROUCH_PRESSED) -> JUMP_CROUCH` for a "fast-fall" mechanic — pure stretch.)

**Estimated time.** 45 minutes.

---

## Problem 3 — Add the same fifth state to the State-pattern player

**Problem statement.** Take `exercise-02-character-with-states.py` and add a `CrouchState` class. Same behaviour as Problem 2. Confirm by side-by-side comparison that the State-pattern version is *shorter to add* than the hand-rolled one once the new state has its own behaviour.

**Acceptance criteria.**

- A file `homework/p3_state_pattern_crouch.py` runs and the player can crouch.
- A new class `CrouchState(State)` exists with `enter`, `update`, `exit`. `enter` may set `char.crouch_speed_mult = 0.5`; `exit` clears it.
- `IdleState.update` and `RunState.update` have a new transition: `if char.crouch_input: char.change_state(CrouchState())`.
- The HUD shows `state: CrouchState` while crouching.
- A `homework/p3_crouch_compare.md` (75-125 words) compares the lines-of-code count for Problem 2 vs Problem 3. The State-pattern version is likely *slightly more code* for a single state (the class boilerplate). Note that. Then note: how would adding a *second* crouch-variant (e.g. `CrouchSlide`) compare? Which version scales better?

**Hint.** The `crouch_speed_mult` field on `char` is the canonical "this state lowers a multiplier, other states read it" pattern. Set in `enter`; reset to `1.0` in `exit`. Asymmetric `enter`/`exit` like this is the classic "forgot to clear in exit" bug — write both at the same time.

**Estimated time.** 35 minutes.

---

## Problem 4 — Hierarchy: an `AirborneState` parent for jump + fall

**Problem statement.** Take Problem 3's code and factor out a parent `AirborneState` class. `JumpState` and `FallState` both inherit from it. The parent owns the shared `update_airborne` method (gravity, horizontal control in mid-air). `JumpState` and `FallState` only override the transition decisions.

**Acceptance criteria.**

- A file `homework/p4_airborne_parent.py` runs and behaves identically to Problem 3.
- A class `AirborneState(State)` exists with `update_airborne(self, char, dt)`.
- `JumpState(AirborneState)` and `FallState(AirborneState)` both call `self.update_airborne(char, dt)` from their `update`.
- The `JumpState.update` is at most 5 lines (after the parent call). Same for `FallState`.
- A `homework/p4_airborne_note.md` (50-100 words) describes one place in the parent where the abstraction *almost* failed — i.e., a piece of behaviour you nearly factored up but didn't because it differs between jump and fall. (One candidate: the apex-detection that flips jump to fall.)

**Hint.** Don't promote the apex check. `JumpState` is the only state that has an apex transition; `FallState` doesn't. Keep that in each subclass. The parent owns "what airborne *means*" (gravity, horizontal control); each child owns "what makes this airborne state different."

**Estimated time.** 35 minutes.

---

## Problem 5 — Wire a pause stack into your Week-4 platformer

**Problem statement.** Take your Week-4 platformer mini-project (or, if that's not handy, Exercise 3's stack). Add a true pause overlay using the state stack from Exercise 3. ESC pauses; ESC again resumes; the player's position, velocity, and FSM state are *exactly preserved* across the pause.

**Acceptance criteria.**

- A file (or git branch) `homework/p5_pause_stack/` exists with a runnable platformer that pauses.
- ESC pushes a `PauseState` onto the stack. The dt-driven physics and the player's FSM both stop advancing while pause is on top.
- The pause overlay dims the screen and shows "PAUSED — ESC to resume" (Coin-Pink text).
- ESC during pause pops the pause; gameplay resumes seamlessly. The player's `vx`, `vy`, FSM state, and position are unchanged.
- The level-select / gameplay split from Week 4 can also be expressed as states on the stack (stretch). At minimum, the pause-over-gameplay pair must work.
- A `homework/p5_pause_note.md` (75-150 words) explains why pause is implemented as a *push* and not as a *transition to PauseState*. Reference Lecture 2 §5 by section.

**Hint.** The "only the top state updates; every state draws" rule is the whole trick. Make sure your main loop respects it. The most common bug: the gameplay's `update(dt)` keeps running while pause is on top because you forgot to wrap it in `if stack[-1] is gameplay_state`. Re-read Exercise 3.

**Estimated time.** 1 hour 20 minutes.

---

## Problem 6 — Reflection essay

**Problem statement.** Write a 350-450 word reflection at `notes/week-05-reflection.md` answering:

1. Before this week, your character logic was a tangle of boolean flags. After this week, it's a state machine. Describe one *specific* bug from your Week-4 platformer that the state-machine refactor either *fixed* or made *structurally impossible*. Be specific: name the states involved, name the bug.
2. Lecture 1 §13 argues the hand-rolled FSM wins below five states; Lecture 2 §1 argues the State pattern wins above five. Did you experience that crossover in your own writing this week? At what state-count did each version start to feel like the wrong shape?
3. Bob Nystrom's *Game Programming Patterns* chapter on State (linked in `resources.md`) is the canonical free explanation of this pattern for game programmers. If you read it: what was the one paragraph that changed how you thought about character code? If you didn't, what *kept* you from reading it — and will you read it next week?
4. What's one state you'd add to your mini-project player if you had another five hours? Why that one first?

**Acceptance criteria.**

- A file `notes/week-05-reflection.md`, 350-450 words.
- Each numbered question addressed in its own paragraph.
- At least one specific technique mentioned by name (e.g., "the `enter`/`exit` lifecycle pair" rather than "the state pattern thing").
- At least one citation of Lecture 1 or Lecture 2 by section number.
- File is committed.

**Hint.** Reflection essays read flat when they're abstract. Write about specific moments: "I had a bug where the player could shoot during the hurt animation. I 'fixed' it three times with `if not is_hurt:` and it kept coming back. Once I added `HurtState`, the shoot input was *only* read in states that allowed shooting, and the bug never returned. The FSM didn't *fix* the bug; it *deleted the category of bug*." beats "I learned about state machines."

**Estimated time.** 30 minutes.

---

## Time budget recap

| Problem | Estimated time |
|--------:|---------------:|
| 1 | 25 min |
| 2 | 45 min |
| 3 | 35 min |
| 4 | 35 min |
| 5 | 1 h 20 min |
| 6 | 30 min |
| **Total** | **~4 h 50 min** |

That's about an hour under the 6-hour weekly budget — the rest is for the bugs your refactor will produce. Refactoring a four-week-old codebase to a new shape always uncovers latent issues; budget the debugging time.

When you've finished all six, push your repo and open the [mini-project](./07-mini-project/00-overview.md).
