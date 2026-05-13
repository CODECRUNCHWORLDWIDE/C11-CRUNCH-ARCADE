# Week 5 — Quiz

Ten multiple-choice questions. Take it with your lecture notes closed. Aim for 9/10 before moving to Week 6. Answer key at the bottom — don't peek.

---

**Q1.** Lecture 1 names four parts of a finite state machine. Which set is correct?

- A) States, transitions, animations, sounds.
- B) States, current state, events, transition function.
- C) Inputs, outputs, side effects, return values.
- D) `enter`, `update`, `exit`, `change_state`.

---

**Q2.** A player can be in `idle`, `run`, `jump`, or `fall`. Pressing JUMP while in `fall` should do nothing (no double-jump). In a hand-rolled FSM with a `TRANSITIONS: dict[(State, Event), State]`, how is "do nothing" expressed?

- A) `TRANSITIONS[(State.FALL, Event.JUMP_PRESSED)] = State.FALL`.
- B) The dict has no entry for `(State.FALL, Event.JUMP_PRESSED)`; the event is silently dropped (or logged) and the state does not change.
- C) An explicit `if state == State.FALL and event == JUMP_PRESSED: return`.
- D) Pygame's `pygame.event.set_blocked(pygame.K_SPACE)` while airborne.

---

**Q3.** Lecture 1 §4 prescribes a four-phase update for an FSM-driven character. Which order is correct?

- A) Render → process events → update state behaviour → decide transitions.
- B) Collect events → decide transitions → run current-state behaviour → render.
- C) Update physics → check transitions → render → collect events for next frame.
- D) Decide transitions → collect events → render → run behaviour.

---

**Q4.** A *state* and an *event* are not the same thing. Which pair correctly names one of each?

- A) `IDLE` (state) and `RUN` (state).
- B) `JUMP_PRESSED` (event) and `MOVE_RELEASED` (event).
- C) `RUN` (state) and `JUMP_PRESSED` (event).
- D) `vy = -650` (state) and `grounded = True` (event).

---

**Q5.** Lecture 2 argues the State pattern (one class per state) wins over the hand-rolled FSM once the state count exceeds about five. Why?

- A) Python classes are faster than dict lookups.
- B) Per-state behaviour lives next to the per-state name (one class), the `enter`/`exit` slot is structurally visible, and the central transition table — which gets unreadable at ten+ states — disappears entirely.
- C) The State pattern uses less memory.
- D) The State pattern is required by `pygame.sprite.Sprite`.

---

**Q6.** A `JumpState` sets `char.vy = -JUMP_VEL` somewhere. Where does this assignment belong?

- A) In `JumpState.update`, every frame.
- B) In the input handler, when the SPACE key is pressed.
- C) In `JumpState.enter`. The velocity change is a *one-time side effect of becoming a jumper*; it belongs in the entry hook, not in per-frame update or per-input handler.
- D) In `IdleState.exit`, because that's the state being left.

---

**Q7.** Per Lecture 2 §8, the three classic FSM bugs are:

- A) Off-by-one errors, integer overflow, and floating-point precision.
- B) Forgotten exit-action, illegal transition silently succeeding, and state leak (one state's fields persisting into another state by accident).
- C) Race conditions, deadlocks, and livelocks.
- D) GIL contention, garbage-collection pauses, and import order.

---

**Q8.** A pushdown automaton (state stack) is the right tool for which of the following?

- A) `idle → run → jump → fall`. The transitions are linear; a stack is overkill.
- B) Pause menu overlaid on gameplay. The gameplay state is *suspended* and resumes from the exact frame when the pause is popped — push and pop, not transition.
- C) Replacing the player's `IdleState` with a `RunState` when the player presses an arrow key.
- D) Loading levels from `.csv` files.

---

**Q9.** Hysteresis in enemy AI (Challenge 1) uses a chase-radius of 180 and a lose-radius of 260. Why two different values?

- A) The artist asked for it.
- B) Without the gap (`CHASE_RADIUS = LOSE_RADIUS = 220`), the enemy oscillates between chase and return every frame when the player stands at the boundary. The gap (the hysteresis band) absorbs the noise.
- C) For performance — two distance checks are cheaper than one.
- D) Because Pygame's distance function returns approximate values.

---

**Q10.** Per Lecture 2, where should per-state data (e.g. `AttackState`'s 400 ms swing timer) live by default?

- A) On the `Character` instance, as `char.attack_timer`.
- B) On the `AttackState` instance, as `self.timer`. The data lives only as long as the state is current; when the state is replaced, the data is garbage-collected with it. Only fields that *other states must read* belong on the character.
- C) In a global dict keyed by character ID.
- D) In a pygame.event.Event payload.

---

## Answer key

<details>
<summary>Click to reveal answers</summary>

1. **B** — States, current state, events, transition function. (Lecture 1 §2.) `enter`/`update`/`exit` are part of the State pattern, not the FSM definition.
2. **B** — No entry in the table = no transition. The guard against double-jump is the *absence* of a row, not an `if` check. (Lecture 1 §3 and §6.)
3. **B** — Collect events, decide transitions, run state behaviour, render. The order is load-bearing; reversing collect and decide gives one-frame-stale behaviour. (Lecture 1 §4.)
4. **C** — `RUN` is a state (a noun, a behaviour mode); `JUMP_PRESSED` is an event (a verb, a trigger). Beginners conflate these and the lecture explicitly separates them. (Lecture 1 §2.)
5. **B** — The class definitions colocate state-name, behaviour, and lifecycle slots. The transition table becomes per-state knowledge in each `update`. (Lecture 2 §1 and §2.)
6. **C** — Side effects of *becoming* a state belong in `enter`. Setting `vy` in `update` makes the upward kick re-apply every frame; setting it in the input handler is the state-leak shape. (Lecture 2 §2 and §3, "JumpState.enter" example.)
7. **B** — The three classic bugs from Lecture 2 §8 (and previewed in Lecture 1 §12). The State pattern makes each one structurally harder to write.
8. **B** — Pause is a *push*, not a transition. The underlying state is preserved and resumed on pop. (Lecture 2 §5.)
9. **B** — Hysteresis is the gap between "enter" and "leave" thresholds. Without the gap, the FSM oscillates at the boundary. Same trick a thermostat uses. (Challenge 1 hints + general control theory.)
10. **B** — Per-state data on the state instance by default; only cross-state fields on the character. (Lecture 2 §6.)

</details>

---

If you scored under 7, re-read the lecture sections cited in the answers you missed. If you scored 9 or 10, you're ready for the [homework](./homework.md).
