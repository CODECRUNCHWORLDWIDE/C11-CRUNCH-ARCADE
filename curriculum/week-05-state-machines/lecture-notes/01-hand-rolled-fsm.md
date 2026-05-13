# Lecture 1 — The Hand-Rolled Finite State Machine

> **Duration:** ~2 hours of reading + hands-on.
> **Outcome:** You can identify a "missing FSM" in a character function, name the four parts of an FSM, and refactor a 60-line tangle of nested `if`s into a 30-line state machine with explicit transitions, an `Enum` of states, and a transition table.

If you only remember one thing from this lecture, remember this:

> **A character that does different things at different times is a state machine.** It doesn't matter whether you call it that. The choice is whether you write it as *one*, with explicit states and explicit transitions, or whether you write it as *implicitly* — a junk drawer of boolean flags (`is_jumping`, `is_attacking`, `is_hurt`) whose combinations encode the real states by accident. The first version is six fewer bugs and twenty fewer lines.

---

## 1. The smell

Open your Week 4 platformer `main.py`. Find the player update function. It probably looks something like this:

```python
def update_player(player, dt, keys, world):
    # Horizontal movement
    vx = 0.0
    if keys[pygame.K_LEFT]:
        vx = -SPEED
    if keys[pygame.K_RIGHT]:
        vx = SPEED

    # Jump
    if keys[pygame.K_SPACE] and player.grounded and not player.is_jumping:
        player.vy = -JUMP_VEL
        player.is_jumping = True
        player.grounded = False

    # Gravity
    player.vy += GRAVITY * dt
    if player.vy > TERMINAL_V:
        player.vy = TERMINAL_V

    # Move and collide (omitted)
    # ...

    # Reset is_jumping if grounded
    if player.grounded and player.vy >= 0:
        player.is_jumping = False
```

It works. You shipped it. Now you want to add a `hurt` state. Easy enough:

```python
    if player.is_hurt:
        # Can't move while hurt
        vx = 0
        player.hurt_timer -= dt
        if player.hurt_timer <= 0:
            player.is_hurt = False
```

Now you want a `dash`. And a `wall_slide`. And to disable jump while attacking. Forty-five minutes later your `update_player` is a hundred and twenty lines of `if not is_hurt and not is_dashing and grounded and ...`. Worse: the *order* of the `if`s now matters. Reordering them silently changes the behaviour. The "double-jump after spike" bug appears, you fix it with another `if`, and a week later it comes back in a slightly different form.

This is the **missing-FSM** smell. The character has many mutually-exclusive behaviour modes. You are encoding them with boolean flags whose combinations are meaningful by accident. The fix is to admit that the character has *states*, name them, and only allow one at a time.

> A practical rule: **if you have two or more boolean flags whose combinations the code branches on, you have a state machine in disguise.** Pull it out into the daylight.

---

## 2. What is an FSM?

A **finite state machine** is four things. Memorise the list — it comes up in interview questions and in this week's quiz.

1. **A finite set of states** — the named modes the system can be in. For a platformer player: `idle`, `run`, `jump`, `fall`, `hurt`. Five is plenty; ten is reasonable; thirty is the point where you reach for hierarchical machines or behaviour trees.
2. **A current state** — exactly one, at all times. Not "mostly idle, kind of jumping." One.
3. **An alphabet of events** — the triggers that may cause a transition. `JUMP_PRESSED`, `LANDED`, `HIT_BY_SPIKE`, `MOVE_INPUT`, `STOP_INPUT`. These are *not* the same as states. Beginners conflate them.
4. **A transition function** — a mapping from `(current_state, event)` to a new state. Some events do nothing in some states (no transition). Some events trigger a transition with a side effect (play a sound, reset a timer). The transition function is the *whole behaviour* of the machine, compressed.

That's it. Five lines of definition. Let's write one.

---

## 3. The minimal FSM, in twenty lines of Python

We'll model a four-state player: `idle`, `run`, `jump`, `fall`. (We'll add `hurt` later; the lecture builds up.) States are an `Enum`. Events are also an `Enum`. The transition table is a `dict`.

```python
from enum import Enum, auto

class State(Enum):
    IDLE = auto()
    RUN  = auto()
    JUMP = auto()
    FALL = auto()

class Event(Enum):
    MOVE_PRESSED   = auto()
    MOVE_RELEASED  = auto()
    JUMP_PRESSED   = auto()
    LANDED         = auto()
    FELL_OFF_EDGE  = auto()

# (from_state, event) -> to_state
TRANSITIONS: dict[tuple[State, Event], State] = {
    (State.IDLE, Event.MOVE_PRESSED): State.RUN,
    (State.IDLE, Event.JUMP_PRESSED): State.JUMP,
    (State.IDLE, Event.FELL_OFF_EDGE): State.FALL,
    (State.RUN, Event.MOVE_RELEASED): State.IDLE,
    (State.RUN, Event.JUMP_PRESSED): State.JUMP,
    (State.RUN, Event.FELL_OFF_EDGE): State.FALL,
    (State.JUMP, Event.LANDED): State.IDLE,
    (State.JUMP, Event.FELL_OFF_EDGE): State.FALL,  # apex passed
    (State.FALL, Event.LANDED): State.IDLE,
}
```

That's the whole machine. Nine transitions. Six are obvious. Three deserve a comment:

- `(IDLE, FELL_OFF_EDGE) -> FALL`: if you walk off a ledge from idle without jumping, you fall. The event is generated by your physics code when `not grounded and was_grounded_last_frame`.
- `(JUMP, FELL_OFF_EDGE) -> FALL`: the upward arc of the jump ends. The event fires when `vy >= 0 and state == JUMP`. Conceptually, the jump *is over*; gravity now owns you.
- `(RUN, MOVE_RELEASED) -> IDLE`: the player let go of the arrow keys. Simple, but easy to forget — and a `RUN` state that never returns to `IDLE` is the classic beginner FSM bug.

The transitions you *don't* have are also load-bearing. `(JUMP, JUMP_PRESSED) -> ???` is missing on purpose — you can't double-jump. The event arrives in `JUMP`, the transition table looks up `(JUMP, JUMP_PRESSED)`, finds nothing, and the event is dropped. The double-jump-after-spike bug from the introduction is *structurally impossible* in this design. You didn't add a guard; the guard is the *absence* of an entry in the table.

---

## 4. The four phases of an update

A frame, for an FSM-driven character, has four phases. Run them in this order, every frame, without exception.

```python
def update_character(char, dt, raw_input, world):
    # PHASE 1 — Gather events.
    events = collect_events(char, raw_input, world)

    # PHASE 2 — Decide transitions.
    for event in events:
        key = (char.state, event)
        if key in TRANSITIONS:
            char.state = TRANSITIONS[key]
        # else: the event is illegal in this state; we drop it.

    # PHASE 3 — Run current-state behaviour.
    run_state_behaviour(char, dt, raw_input, world)

    # PHASE 4 — Render (in your draw pass, not here).
```

The phases must be in this order. Common bug: running behaviour *before* deciding transitions means the player runs one frame of stale behaviour. Common bug 2: transitioning in the middle of behaviour means one transition can fire two state changes in a frame, which is rarely what you want.

The four phases are the algorithm. Internalise them. Every FSM update you ever write will look like this.

---

## 5. Where each piece of code lives

In the nested-if version, the question "where do I add the dash?" has no good answer. You add seven `if`s, scattered through the function, hoping you got the precedence right. In the FSM version, the answer is mechanical:

| Question | Answer |
|---------|--------|
| What states does dash interact with? | Add `DASH` to the `State` enum. |
| What event fires the dash? | Add `DASH_PRESSED` to the `Event` enum. |
| Which states allow entering dash? | Add `(IDLE, DASH_PRESSED) -> DASH` and `(RUN, DASH_PRESSED) -> DASH` to `TRANSITIONS`. |
| What does the dash do while active? | A `run_dash(char, dt)` function called from the dispatcher when `char.state == DASH`. |
| What ends the dash? | Add `DASH_TIMER_DONE` to `Event`, fire it from `run_dash` when `dash_timer <= 0`, add `(DASH, DASH_TIMER_DONE) -> IDLE` to `TRANSITIONS`. |

Five questions. Five answers. Five edits, all in known places. Compare to "add seven `if`s and pray."

This is the structural payoff. Every new state is a known shape. You don't have to re-read the whole function to add one.

---

## 6. The transition table is data, not code

Look at the `TRANSITIONS` dict again:

```python
TRANSITIONS: dict[tuple[State, Event], State] = {
    (State.IDLE, Event.MOVE_PRESSED): State.RUN,
    # ...
}
```

That is a Python dict, but it might as well be a CSV. You could move it into a file:

```csv
from,event,to
IDLE,MOVE_PRESSED,RUN
IDLE,JUMP_PRESSED,JUMP
RUN,MOVE_RELEASED,IDLE
...
```

…and load it at startup. The loader is six lines. The point isn't to *actually* do this for a four-state player — that's over-engineering — but to *notice* that you could. The transitions are *data*. The behaviour functions are *code*. The separation makes the diagram (the data) something a designer can edit without touching the engine, exactly like the levels-vs-engine split from Week 4. The same architectural rhyme appears at a different scale.

For the mini-project this week we keep the table inline in Python. For a real shipped game with thirty enemies and a hundred player states, you move it into a JSON file. The choice is when, not whether.

---

## 7. Illegal transitions: log loudly, never silently no-op

The minimal version drops illegal events:

```python
for event in events:
    key = (char.state, event)
    if key in TRANSITIONS:
        char.state = TRANSITIONS[key]
    # else: silent drop
```

That is wrong in production. An illegal transition usually means a bug somewhere else: physics fired `LANDED` when the player wasn't airborne; combat fired `HIT_BY_SPIKE` while the player was in `HURT` (a redundant hit); UI fired `PAUSE_PRESSED` during a transition. Silent drops hide these bugs for *months*.

The correct version logs:

```python
for event in events:
    key = (char.state, event)
    if key in TRANSITIONS:
        new_state = TRANSITIONS[key]
        char.transition(new_state, event)  # see below for side effects
    else:
        # Optional but recommended: a debug log so you notice illegal events.
        if DEBUG_FSM:
            print(f"[fsm] illegal: {char.state.name} got {event.name}; ignored")
```

A flag, not always on. Flip it during development; turn it off for ship. The cost is half a millisecond per noisy frame, the benefit is "every illegal-transition bug surfaces by the second test run."

---

## 8. Side effects on transition: where they live

A transition is rarely just "change the state field." It usually has side effects:

- `(IDLE -> RUN)` — start playing the run-cycle sound; start the dust-puff particle emitter.
- `(JUMP -> FALL)` — *no* sound (the jump sound already played); the animation switches to fall.
- `(RUN -> IDLE)` — stop the run sound; stop the dust puff.
- `(any -> HURT)` — play hit sound; flash the sprite red; freeze input for `HURT_DURATION`.

Where do you put those? Two choices in a hand-rolled FSM. (The State pattern in Lecture 2 has a third, cleaner choice.)

**Choice A — Side-effect lookup table.** Another dict, parallel to the transitions:

```python
ON_ENTER: dict[State, Callable[[Character], None]] = {
    State.IDLE: lambda c: stop_run_sound(c),
    State.RUN:  lambda c: (play_run_sound(c), start_dust(c)),
    State.JUMP: lambda c: (play_jump_sound(c), set_vy(c, -JUMP_VEL)),
    State.FALL: lambda c: None,  # nothing to do
    State.HURT: lambda c: (play_hit_sound(c), flash_red(c), set_invincible(c, 0.5)),
}
```

Call `ON_ENTER[new_state](char)` after every transition. Symmetric `ON_EXIT` if a state needs cleanup.

**Choice B — Inline in a `transition()` method.**

```python
def transition(self, new_state: State, by_event: Event):
    self._exit(self.state)
    self.state = new_state
    self._enter(new_state, by_event)

def _enter(self, state: State, by_event: Event):
    if state == State.JUMP:
        self.vy = -JUMP_VEL
        play_jump_sound(self)
    elif state == State.HURT:
        play_hit_sound(self)
        flash_red(self)
        self.invincible_t = 0.5
    # ...
```

Choice A is *data-driven* and scales to dozens of states without ballooning the dispatcher. Choice B is *easier to read* for four-state machines because the side effects sit next to their state names. We use B in this lecture's exercises and A in the mini-project. Both ship.

---

## 9. Worked example: the four-state player

Let's put the whole thing together. A character with `IDLE`, `RUN`, `JUMP`, `FALL`. The transitions, the events, the per-state behaviour, the dispatcher. Inline, runnable, copy-paste-ready.

```python
from enum import Enum, auto
from dataclasses import dataclass

GRAVITY = 1800.0
JUMP_VEL = 650.0
RUN_SPEED = 240.0
TERMINAL_V = 1200.0

class State(Enum):
    IDLE = auto()
    RUN  = auto()
    JUMP = auto()
    FALL = auto()

class Event(Enum):
    MOVE_PRESSED   = auto()
    MOVE_RELEASED  = auto()
    JUMP_PRESSED   = auto()
    LANDED         = auto()
    FELL_OFF_EDGE  = auto()

TRANSITIONS = {
    (State.IDLE, Event.MOVE_PRESSED):  State.RUN,
    (State.IDLE, Event.JUMP_PRESSED):  State.JUMP,
    (State.IDLE, Event.FELL_OFF_EDGE): State.FALL,
    (State.RUN,  Event.MOVE_RELEASED): State.IDLE,
    (State.RUN,  Event.JUMP_PRESSED):  State.JUMP,
    (State.RUN,  Event.FELL_OFF_EDGE): State.FALL,
    (State.JUMP, Event.LANDED):        State.IDLE,
    (State.JUMP, Event.FELL_OFF_EDGE): State.FALL,
    (State.FALL, Event.LANDED):        State.IDLE,
}

@dataclass
class Character:
    x: float = 0.0
    y: float = 0.0
    vx: float = 0.0
    vy: float = 0.0
    state: State = State.IDLE
    grounded: bool = True
    was_grounded: bool = True
    move_input: int = 0   # -1, 0, +1
    last_move_input: int = 0

def collect_events(c: Character, raw_input: dict, world) -> list[Event]:
    events: list[Event] = []
    if c.move_input != 0 and c.last_move_input == 0:
        events.append(Event.MOVE_PRESSED)
    if c.move_input == 0 and c.last_move_input != 0:
        events.append(Event.MOVE_RELEASED)
    if raw_input.get("jump_pressed_this_frame", False):
        events.append(Event.JUMP_PRESSED)
    if c.grounded and not c.was_grounded:
        events.append(Event.LANDED)
    if not c.grounded and c.was_grounded:
        events.append(Event.FELL_OFF_EDGE)
    if c.state == State.JUMP and c.vy >= 0:
        events.append(Event.FELL_OFF_EDGE)  # apex
    return events

def transition(c: Character, new_state: State):
    if new_state == State.JUMP:
        c.vy = -JUMP_VEL
        c.grounded = False
    c.state = new_state

def run_state(c: Character, dt: float):
    # Horizontal control is allowed in IDLE, RUN, JUMP, FALL alike.
    c.vx = c.move_input * RUN_SPEED
    if c.state in (State.JUMP, State.FALL):
        c.vy += GRAVITY * dt
        if c.vy > TERMINAL_V:
            c.vy = TERMINAL_V
    # IDLE and RUN: vy stays whatever the collision step set it to.
```

Three things to notice:

1. **`collect_events` is the only place that reads inputs and physics state to generate events.** No state-behaviour function reads inputs to fire transitions. The separation is deliberate.
2. **`run_state` is short.** It applies the input-driven `vx` and integrates gravity for airborne states. That's it. The states do almost the same thing because *the difference between IDLE and RUN is what the animation looks like*, not what the physics does. We'll feel this distinction more in Week 6.
3. **`transition()` handles entry side effects** (the upward velocity for JUMP). No state-behaviour function sets `vy = -JUMP_VEL`. Setting jump velocity outside the transition would be a state-leak bug.

The full runnable version lives in **exercise-01**.

---

## 10. The "RUN versus IDLE is just animation" insight

Look at `run_state` above. The physics is identical for `IDLE` and `RUN`: `c.vx = c.move_input * RUN_SPEED`. The only behavioural difference is that, in `IDLE`, `move_input` is zero (by definition — if it weren't, you'd be in `RUN`). So why have two states at all?

Two reasons.

**Reason 1: animation.** In `IDLE`, you play `idle_breathing.png`. In `RUN`, you play `run_cycle.png`. The same physics produces different art, and the art is bound to the state. Week 6 will make this binding explicit; for now, hold the thought.

**Reason 2: transitions from each are different.** `IDLE -> JUMP` may be allowed; `IDLE -> DASH` may not be (you have to be running to dash). `RUN -> JUMP` is allowed; `RUN -> SLIDE` is allowed. The state name is the *category* the transitions are written against. Without the distinction, you'd write `if move_input != 0 and dash_pressed: dash()` — a nested conditional rather than a clean transition.

The general principle: **states exist to make transitions writable.** If two states have the same physics *and* the same allowed transitions *and* the same animation, you have one state. Otherwise you have two.

---

## 11. The "no two states active" rule

Exactly one state, at all times. Not "running while jumping." Not "idle while hurt." One.

The most common beginner FSM bug is reaching for "and" — "the player is jumping *and* dashing." Resist. If you need both behaviours, you have:

- **A new combined state**, e.g. `JUMP_DASH`. (Fine for two combinations; combinatorial blow-up for ten.)
- **Two parallel state machines** on the same character, e.g. a `MovementFSM` (idle/run/jump) and a `WeaponFSM` (sheathed/swinging/cooldown). The two machines run side-by-side and never interfere. This is the **Component pattern** answer; Nystrom covers it in chapter 9.
- **An HFSM** (hierarchical FSM): an `airborne` superstate contains a sub-FSM with `jump` and `fall`. The player can be in "airborne, currently jumping" — one composite state — without breaking the one-state-at-a-time rule. Lecture 2 builds this.

Reach for parallel machines first; reach for HFSMs second. Reach for "a new combined state" only if there are two or three. If you find yourself enumerating ten combined states, your design has decayed into a permutation table — back up and use parallel machines.

---

## 12. The three classic bugs (preview)

The State pattern in Lecture 2 makes each of these structurally hard to write. The hand-rolled FSM does not — you have to be disciplined. Know them:

- **Forgotten exit-action.** You enter `RUN`, the dust-puff emitter starts. You leave `RUN`, the emitter keeps running because you forgot to stop it on exit. The dust now puffs while the player is jumping. Fix: pair every `on_enter` with an `on_exit`.
- **Illegal transition silently succeeds.** You forget to check `key in TRANSITIONS` and call `TRANSITIONS[key]` unguarded. Python raises `KeyError` and the frame crashes — *or* you wrote a fallback that returns the current state, and the event vanishes into silence. Fix: log loudly on illegal transitions; never fall back silently.
- **State leak.** A field set in one state ("I'm holding a charged shot for 1.2 s") is not cleared on exit. The next state sees the stale value and acts on it. Fix: think of every per-state field as needing an explicit `enter` initialiser and an explicit `exit` clearer.

You'll meet all three this week. Forewarned is forearmed.

---

## 13. When the hand-rolled FSM is enough — and when it isn't

Below five states with a flat transition table, the hand-rolled version in this lecture is the right tool. It is shorter than the State pattern, equally clear, and a junior engineer can read it without prior exposure.

Above five states, the dispatcher's `if/elif/elif` ladder gets long, the transition table gets dense, and the per-state behaviour functions live far from their state names. That's the moment the **State pattern** earns its keep. Lecture 2 builds that version with the same player, one class per state, polymorphic dispatch, and lifecycle hooks that pair `enter()` with `exit()` *by construction*.

The two versions ship the same game. Picking the right one is a question of project scale, not correctness.

---

## 14. What you should write after this lecture

Before you open Lecture 2 or the exercises, do this on paper:

1. **List the states of your Week 4 player.** Write each on a sticky note or a line. You'll probably find five: `idle`, `walk`, `jump`, `fall`, `land` (the brief 1-frame post-landing state). Possibly `hurt` if you've already added damage.
2. **List the events.** Walk through every input and every physics-derived state change: arrow key down/up, jump key down, hit by spike, became grounded, fell off ledge.
3. **Draw the transitions as arrows.** Each arrow goes from one state to another, labelled with the event that causes it. Boxes are states; arrows are transitions.
4. **Notice which arrows are missing.** Are `(IDLE -> ATTACK)` and `(RUN -> ATTACK)` both present? Why? If `(JUMP -> ATTACK)` isn't, is that intentional?
5. **Now open the exercise.** You'll find the code mirrors the diagram you drew. If the diagram is right, the code is right.

The diagram is the design artefact. The code is the implementation. The two should match; if they drift, the diagram is the source of truth and the code is what's wrong.

---

## What you should take away

- A character that does different things at different times is an FSM. Make it explicit.
- An FSM is four things: states, current state, events, transition function. Memorise.
- The transition table is data. The behaviour functions are code. The separation pays for itself.
- A four-phase frame: gather events, decide transitions, run state behaviour, render.
- The three classic bugs: forgotten exit, silent illegal transition, state leak. Watch for each.
- Below five states the hand-rolled version wins. Above five, reach for the State pattern (Lecture 2).

Continue to [Lecture 2 — State transitions and substates](./02-state-transitions-and-substates.md).
