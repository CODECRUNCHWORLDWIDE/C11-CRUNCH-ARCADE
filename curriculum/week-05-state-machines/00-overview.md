# Week 5 — State Machines for Characters

Open your Week 4 platformer prototype and look at the `update_player` function. Be honest with yourself. How many `if grounded and vy == 0 and not pressing_left and not pressing_right and not hurt:` lines does it have? How many places do you set `is_jumping = True`? How many *different* places do you set `is_jumping = False`? When the player ducks and gets hit at the same frame, what happens? You don't know, do you. The function works *most of the time*, and the bug log on your desk has a sticky note that reads "sometimes player can double-jump after touching the spike."

That's not a bug. That's a missing abstraction.

A character that can be in one of several mutually-exclusive **behaviour modes** — idle, running, jumping, falling, hurt — is a **finite state machine**. Once you say the words out loud, the whole code shape changes. There is exactly one state at a time. There are explicit transitions between states. Each state owns its own input handling, its own physics, its own animation. The double-jump-after-spike bug disappears not because you fixed it, but because the state machine never *allowed* it: in the `hurt` state, the jump input is ignored. You didn't add an `if`, you removed a dozen.

This week we build that vocabulary, twice. First as a **hand-rolled FSM** in plain Python — a string variable, a giant `if/elif`, and a dictionary of allowed transitions. Then as the **State pattern** from Bob Nystrom's *Game Programming Patterns* — one class per state, polymorphic dispatch, scales to a dozen states without becoming spaghetti. Both compile. Both ship. The first one is what you'll write in a game jam at 2 a.m. The second is what you'll re-factor into when the jam game becomes a real project.

By end-of-week you ship a **player character with at least four states** (`idle`, `run`, `jump`, `fall`, plus `hurt` recommended), clean transitions, and a tiny demo where the player runs across a Week-4-style tilemap, jumps gaps, takes a hit from a spike, and recovers. The transitions are *explicit*. There is no `if grounded and vy < -1 and not pressed_space_last_frame and ...`. There is `if event == Event.JUMP_PRESSED and state == State.IDLE: transition_to(State.JUMP)`. Six words instead of fifteen. And the code is right.

There is still no Godot. We are sharpening the Pygame foundation. Godot's `AnimationStateMachine` and its built-in state-machine nodes will feel obvious in Week 9 because you wrote one yourself in Week 5.

## Learning objectives

By the end of this week, you will be able to:

- **Explain** what a finite state machine is, why it matters for character code, and identify a "missing FSM" in a function full of nested `if`s.
- **Implement** a hand-rolled FSM with a string state variable, an `enum` of states, a transition table, and an `update()` dispatcher.
- **Implement** the State pattern (a.k.a. polymorphic FSM) with one class per state, `enter()` / `update(dt)` / `exit()` lifecycle hooks, and a `change_state()` method on the owning character.
- **Distinguish** between *states* (idle, run, jump) and *events* (jump-pressed, land-detected, hit-detected) — the two are not the same and beginners conflate them.
- **Design** a state diagram on paper for a four-to-six-state character, then translate the diagram into code without drift.
- **Reason** about *substates* and *hierarchical FSMs*: when a single state grows enough behaviour to deserve its own little machine inside.
- **Implement** a **state stack** (a pushdown automaton) and explain why pause menus, dialog boxes, and "stunned" overlays are stack-shaped, not transition-shaped.
- **Avoid** the three classic FSM bugs: forgotten exit-actions, illegal transitions silently succeeding, and state-leak where one state mutates fields that another state then misinterprets.
- **Ship** a four-state player character built on the State pattern, running on top of last week's tilemap.

## Prerequisites

This week assumes you have completed **Weeks 1, 2, 3, and 4**. Specifically:

- You have a Week 4 platformer prototype repo and you can run it. The player walks, jumps, collides with tiles, and the camera follows.
- You can write a Pygame main loop from memory, use `pygame.Vector2`, and `dt`-correct movement.
- You wrote AABB-vs-grid collision in Week 4 and you understand the horizontal-then-vertical pass.
- You are comfortable with Python `enum`, `dataclasses`, and basic OOP (you can subclass a base class and override a method).

If any of those are shaky, do the previous week's mini-project before continuing.

## Topics covered

Lecture 1 — Hand-rolled FSM:

- The "nested ifs" smell: how a character update function rots from 30 lines to 300 over four weeks of feature creep.
- The FSM definition: a finite set of states, a single current state, an alphabet of events, a transition function.
- Modelling the character as `Enum` of states + dict of allowed transitions. Twenty lines.
- The four phases of an `update(dt)` call: process events, decide transitions, run current-state behaviour, render.
- Why the transition table is data, not code (and why illegal transitions should *log loudly*, not silently no-op).
- Worked example: `idle` → `run` → `jump` → `fall` → `idle`. Five states, six transitions, one Python file.

Lecture 2 — State transitions and substates:

- The State pattern (Nystrom, *Game Programming Patterns*, ch. State): one class per state.
- The `enter()` / `update(dt)` / `exit()` lifecycle. What goes in each.
- Hierarchical state machines: an `airborne` superstate with `jump` and `fall` substates underneath.
- The state stack (pushdown automaton): pausing, dialog overlays, "stunned" wrappers that resume the previous state.
- Animation events tied to state transitions: `play("run_loop")` in `enter()`, `stop` in `exit()`. This is the bridge to Week 6.
- The three classic FSM bugs (forgotten exit-actions, illegal transitions silently succeeding, state-leak) and how the State pattern makes each one structurally hard to write.

## Weekly schedule

The schedule below adds up to approximately **35 hours**. Treat it as a target. State machines are the kind of topic that looks abstract on paper and clicks the moment you write the second `update()` and realise the first one has shrunk.

| Day       | Focus                                            | Lectures | Exercises | Challenges | Quiz/Read | Homework | Mini-Project | Self-Study | Daily Total |
|-----------|--------------------------------------------------|---------:|----------:|-----------:|----------:|---------:|-------------:|-----------:|------------:|
| Monday    | Lecture 1 + the nested-ifs refactor              |    2h    |    1.5h   |     0h     |    0.5h   |   1h     |     0h       |    0.5h    |     5.5h    |
| Tuesday   | Hand-rolled FSM for a four-state character       |    1h    |    1.5h   |     0h     |    0.5h   |   1h     |     1h       |    0.5h    |     5.5h    |
| Wednesday | Lecture 2 + State pattern + lifecycle hooks      |    2h    |    1.5h   |     0h     |    0.5h   |   1h     |     1h       |    0h      |     6h      |
| Thursday  | Substates and the state stack                    |    0h    |    1h     |     2h     |    0.5h   |   1.5h   |     1.5h     |    0h      |     6.5h    |
| Friday    | Wire the State pattern into the Week-4 player    |    0h    |    0h     |     0h     |    0.5h   |   1h     |     2.5h     |    0.5h    |     4.5h    |
| Saturday  | Hurt state, animation-event hooks, quiz          |    0h    |    0h     |     0h     |    0.5h   |   0h     |     2.5h     |    0h      |     3h      |
| Sunday    | Polish, README, push                             |    0h    |    0h     |     0h     |    0.5h   |   0h     |     2h       |    0h      |     2.5h    |
| **Total** |                                                  | **5h**   | **5.5h**  | **2h**     | **3.5h**  | **5.5h** | **10.5h**    | **1.5h**   | **33.5h**   |

## How to navigate this week

| File | What's inside |
|------|---------------|
| [README.md](./00-overview.md) | This overview (you are here) |
| [resources.md](./01-resources.md) | Nystrom's State chapter, Valve's animation talks, the AI Game Programming Wisdom FSM essays |
| [lecture-notes/01-hand-rolled-fsm.md](./02-lecture-notes/01-hand-rolled-fsm.md) | What an FSM *is*; the `Enum`+dict version; the four-phase update; explicit transitions |
| [lecture-notes/02-state-transitions-and-substates.md](./02-lecture-notes/02-state-transitions-and-substates.md) | The State pattern; lifecycle hooks; substates; the state stack; animation-event hooks |
| [exercises/README.md](./03-exercises/00-overview.md) | Index of short coding drills |
| [exercises/exercise-01-fsm-from-nested-ifs.py](./03-exercises/exercise-01-fsm-from-nested-ifs.py) | Take a 60-line tangle of nested ifs and refactor it into a 5-state hand-rolled FSM |
| [exercises/exercise-02-character-with-states.py](./03-exercises/exercise-02-character-with-states.py) | Build a four-state character (`idle`/`run`/`jump`/`fall`) using one class per state |
| [exercises/exercise-03-state-stack.py](./03-exercises/exercise-03-state-stack.py) | A pushdown automaton: pause the gameplay state, push a "paused" overlay, resume cleanly |
| [challenges/README.md](./04-challenges/00-overview.md) | Index of weekly challenges |
| [challenges/challenge-01-enemy-ai-fsm.md](./04-challenges/challenge-01-enemy-ai-fsm.md) | A patrolling enemy with `patrol`/`chase`/`attack`/`return` states |
| [quiz.md](./05-quiz.md) | 10 multiple-choice questions |
| [homework.md](./06-homework.md) | Six practice problems for the week |
| [mini-project/README.md](./07-mini-project/00-overview.md) | A player character with at least four states and clean transitions |

## Frame budget for this week

A reminder of what 60 fps actually means, in milliseconds. Every C11 lecture returns to this tile.

```
┌─────────────────────────────────────────────────────────┐
│  FRAME BUDGET — 60 fps target, with a state machine     │
│                                                         │
│  Input poll:       ~0.2 ms                              │
│  FSM event-drain:  ~0.1 ms  (10-20 events / frame)      │
│  FSM dispatch:     ~0.1 ms  (one current_state.update)  │
│  Update (sim):     ~1.4 ms                              │
│  Tilemap collide:  ~0.6 ms                              │
│  Particles:        ~0.5 ms                              │
│  Tilemap draw:     ~1.2 ms                              │
│  Entity draw:      ~1.5 ms                              │
│  Camera apply:     ~0.1 ms                              │
│  HUD draw:         ~0.4 ms                              │
│  Audio mix:        ~0.3 ms                              │
│  GPU + present:    ~4.0 ms                              │
│  Headroom:         ~6.2 ms                              │
│  ─────────────────────                                  │
│  Total:           ~16.6 ms / frame                      │
└─────────────────────────────────────────────────────────┘
```

The two new rows — **FSM event-drain** and **FSM dispatch** — are the cheapest in the whole frame. A four-state machine costs about 0.2 ms per frame *combined*. If your FSM ever shows up on a profiler, it isn't the FSM — it's the work the states are doing. The point of the machine is to make that work explicit, not expensive.

## Stretch goals

If you finish early and want to push further:

- **Read Nystrom's State chapter** end-to-end: <https://gameprogrammingpatterns.com/state.html>. It is forty minutes of reading and it permanently changes how you write character code. Don't skim — Bob's worked example is the one we crib in Lecture 2.
- **Draw your state diagram on paper** before you write the code. Boxes are states. Arrows are transitions. Label each arrow with the event that causes it. If you can't draw it, you can't code it.
- **Add a `wall_slide` state** to your mini-project player. The state activates when the player is airborne, against a wall, and pressing toward the wall. It modifies gravity (slower fall) and unlocks a wall-jump. This is exactly the kind of feature that is a nightmare in nested-ifs and clean in a State pattern.
- **Add an "animation event" to one transition.** When `idle` → `run` fires, log "play(run_loop)". When `run` → `idle` fires, log "stop". You won't have sprites until Week 6, but the *hook* belongs in Week 5. Wire it now; light it up next week.
- **Read Robert Green's *AI Game Programming Wisdom 1*, chapter "The Basics of Finite-State Machines."** It's the canonical industry primer. The book is paywalled but the chapter has been excerpted across the web; a careful search finds it.
- **Watch Valve's *Animation Bootcamp* talks** (free on GDC Vault and YouTube). The way Valve binds animation states to gameplay states is the bridge Week 5 → Week 6.

## Voice rules for the week

- We separate **state** (a noun: idle, run, jump) from **events** (a verb: jump-pressed, hit-detected). Beginners conflate them. We don't.
- We credit **Bob Nystrom**, whose *Game Programming Patterns* chapter on **State** is the canonical free explanation of this pattern for game programmers. He wrote it for free. Cite the source.
- We credit **Robert Green** and the *AI Game Programming Wisdom* series, which formalised the FSM-for-games vocabulary the rest of the industry now uses.
- We prefer **explicit transitions over implicit state-derived ones.** `transition_to(JUMP)` beats `is_jumping = True; vy = -JUMP_VEL; play_sound("jump")` every time. The first reads as a noun-phrase. The second reads as "and another thing."
- We prefer the **State pattern** over the hand-rolled FSM *once the state count exceeds five.* Below five states, the `if/elif` ladder is clearer and shorter. Above five, the State pattern wins by a mile. The lecture covers both because both ship.

## Up next

Continue to [Week 6 — Animation and juice](../week-06/) once you've pushed your four-state player character. The transitions you wire this week become the animation event hooks next week — `enter()` plays a clip, `exit()` stops it. You're laying the bones now; Week 6 paints the muscles.

---

*If you find errors in this material, please open an issue or send a PR. Future learners will thank you.*
