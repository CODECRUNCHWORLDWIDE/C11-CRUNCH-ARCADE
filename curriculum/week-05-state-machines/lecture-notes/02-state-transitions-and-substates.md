# Lecture 2 — State Transitions and Substates

> **Duration:** ~2 hours of reading + hands-on.
> **Outcome:** You can implement the State pattern with one class per state and `enter()` / `update(dt)` / `exit()` lifecycle hooks; you can describe a hierarchical FSM in words and code one with an `airborne` superstate; you can implement a state stack (pushdown automaton) for pause menus and dialog overlays; and you can spot the three classic FSM bugs and explain why the State pattern makes each one structurally hard to write.

If you only remember one thing from this lecture, remember this:

> **One class per state. Three methods: `enter`, `update`, `exit`.** The hand-rolled FSM in Lecture 1 is the right tool for four states. The State pattern in this lecture is the right tool for ten. The shift is not "more complex" — it is "the per-state code now lives next to the state name." That single rearrangement removes most state-leak bugs by construction, and it scales to thirty states without becoming a flat `if/elif` wall.

---

## 1. From transition table to polymorphism

The hand-rolled FSM stores behaviour in three places: a transition `dict`, an `enter` lookup, and a per-state `run_state` `if/elif`. For four states this is fine. For ten, the `run_state` function becomes a hundred-line ladder and the transition `dict` becomes a wall of fifty tuples. Each addition touches three files; the relationship between "the `RUN` state" and "the code that runs in it" is held only by a string name in three places.

The State pattern's move is mechanical and devastating: **make each state a class.** The class holds its own behaviour. The character holds a reference to the *current* state. Switching states is replacing the reference.

```python
class State:
    def enter(self, char): ...
    def update(self, char, dt): ...
    def exit(self, char): ...

class IdleState(State):
    def enter(self, char):
        char.vx = 0

    def update(self, char, dt):
        if char.move_input != 0:
            char.change_state(RunState())
        elif char.jump_pressed:
            char.change_state(JumpState())

    def exit(self, char):
        pass

class Character:
    def __init__(self):
        self.state: State = IdleState()
        self.state.enter(self)

    def change_state(self, new_state: State):
        self.state.exit(self)
        self.state = new_state
        self.state.enter(self)

    def update(self, dt):
        self.state.update(self, dt)
```

Twenty lines. That's the whole pattern. Notice what changed:

- The `(from, event) -> to` dict is *gone*. Transitions are decided inside `update()` by the *current state itself*. `IdleState.update` knows the rules for leaving idle; `RunState.update` knows the rules for leaving run. The rules sit next to the state that owns them.
- `enter` and `exit` are *paired by construction*. The class has both methods. The class author either fills them in or explicitly writes `pass`. The "forgotten exit-action" bug from Lecture 1 §12 is structurally harder to write because the slot is *visible* in the class. You can still leave it empty; you can't accidentally forget it exists.
- State leak is *structurally constrained*: per-state data lives on the state instance, not on the character. When the state object goes away, so does its data. (We'll qualify this in §6 — sometimes the data has to live on the character. But the *default* is the state instance, and that default is correct.)

---

## 2. The three lifecycle hooks: what goes in each

Each state class has three methods that fire at three different times.

**`enter(self, char)`** — runs *once*, when the state becomes current. This is where you:

- Set per-state initial values (`char.attack_timer = 0`, `self.dust_emitter.start()`).
- Play one-shot sounds (`play_sound("jump")`).
- Start animations (`char.anim.play("run_loop")` — Week 6).
- Initialise any fields that the state's `update` will then advance.

**`update(self, char, dt)`** — runs *every frame* the state is current. This is where you:

- Read inputs and advance physics: `char.vx = char.move_input * RUN_SPEED`.
- Decide transitions: `if char.grounded: char.change_state(IdleState())`.
- Tick timers: `self.attack_timer -= dt; if self.attack_timer <= 0: ...`.

**`exit(self, char)`** — runs *once*, when the state stops being current. This is where you:

- Stop per-state effects (`self.dust_emitter.stop()`).
- Clear flags on `char` that the next state shouldn't inherit.
- Stop any animation overrides (`char.anim.stop_layer("attack")`).

The three together form a **lifecycle**. The class author thinks of the state as having a *birth*, a *life*, and a *death*. Every per-state effect either lives entirely inside the state instance (no clean-up needed; garbage collection handles it) or has explicit `enter`/`exit` setup/teardown. There is no third option.

> **Rule of thumb:** if your `enter` adds something to `char` (a particle emitter, a flag, an animation override), your `exit` removes it. Always. Asymmetric `enter`/`exit` is the State pattern's version of `malloc` without `free`.

---

## 3. The State pattern player: `idle`, `run`, `jump`, `fall`

Let's build the full four-state player in the State pattern. (The full runnable version is **exercise-02**.) Just the skeleton here:

```python
GRAVITY = 1800.0
JUMP_VEL = 650.0
RUN_SPEED = 240.0
TERMINAL_V = 1200.0


class State:
    name = "abstract"
    def enter(self, char): pass
    def update(self, char, dt): pass
    def exit(self, char): pass


class IdleState(State):
    name = "idle"

    def enter(self, char):
        char.vx = 0.0

    def update(self, char, dt):
        char.vx = char.move_input * RUN_SPEED
        if char.move_input != 0:
            char.change_state(RunState())
        if char.jump_pressed and char.grounded:
            char.change_state(JumpState())
        if not char.grounded:
            char.change_state(FallState())


class RunState(State):
    name = "run"

    def enter(self, char):
        pass  # animation hook lives here in Week 6

    def update(self, char, dt):
        char.vx = char.move_input * RUN_SPEED
        if char.move_input == 0:
            char.change_state(IdleState())
        if char.jump_pressed and char.grounded:
            char.change_state(JumpState())
        if not char.grounded:
            char.change_state(FallState())

    def exit(self, char):
        pass


class JumpState(State):
    name = "jump"

    def enter(self, char):
        char.vy = -JUMP_VEL
        char.grounded = False

    def update(self, char, dt):
        # Horizontal control is preserved in the air.
        char.vx = char.move_input * RUN_SPEED
        # Gravity.
        char.vy += GRAVITY * dt
        if char.vy > TERMINAL_V:
            char.vy = TERMINAL_V
        # Apex reached -> fall.
        if char.vy >= 0:
            char.change_state(FallState())


class FallState(State):
    name = "fall"

    def update(self, char, dt):
        char.vx = char.move_input * RUN_SPEED
        char.vy += GRAVITY * dt
        if char.vy > TERMINAL_V:
            char.vy = TERMINAL_V
        if char.grounded:
            char.change_state(IdleState())
```

Six things to notice.

1. **Each `update` is self-contained.** Reading `JumpState.update` tells you everything the player does while jumping. You don't need to grep for `state == "jump"` across the file.
2. **Transitions are owned by the source state.** `IdleState` knows the conditions for leaving idle; nobody else does. This is the inversion: in the hand-rolled FSM, the central `TRANSITIONS` dict owns the transitions. In the State pattern, the source state owns them. Each shape has advantages; for ten states the State pattern wins, because the central dict gets unreadable.
3. **`JumpState.enter` sets `char.vy = -JUMP_VEL`.** That is the *side effect of entering Jump*. It does not live in the input handler. It does not live in physics. It lives where the player becomes a jumper. State-leak resistance.
4. **`FallState.update` is identical to `JumpState.update` minus the apex check.** A code smell. Lecture §4 below introduces hierarchical FSMs to factor out the shared `airborne` behaviour.
5. **No `exit` here does anything yet.** That's because none of our states yet *add* anything to `char`. When we add `HurtState`, its `enter` will set `char.invincible_t = 0.5` and its `exit` will clear `char.invincible_t = 0`. The asymmetry will be visible immediately.
6. **The `name` class attribute is for HUD/debugging.** The mini-project HUD prints `state: jump` so you can see the FSM working without animations. Cheap, essential.

---

## 4. Hierarchical FSMs: an `airborne` superstate

`JumpState.update` and `FallState.update` share most of their code. That's the structural smell that says "these are two substates of one parent state." Promote the shared logic to a parent class.

```python
class AirborneState(State):
    """Shared behaviour for any state where the character is not grounded."""
    name = "airborne"

    def update_airborne(self, char, dt):
        char.vx = char.move_input * RUN_SPEED
        char.vy += GRAVITY * dt
        if char.vy > TERMINAL_V:
            char.vy = TERMINAL_V


class JumpState(AirborneState):
    name = "jump"

    def enter(self, char):
        char.vy = -JUMP_VEL
        char.grounded = False

    def update(self, char, dt):
        self.update_airborne(char, dt)
        if char.vy >= 0:
            char.change_state(FallState())


class FallState(AirborneState):
    name = "fall"

    def update(self, char, dt):
        self.update_airborne(char, dt)
        if char.grounded:
            char.change_state(IdleState())
```

The `JumpState` and `FallState` `update` bodies are now two lines each. The shared physics lives in `AirborneState.update_airborne`. Add a `WallSlideState(AirborneState)` next month and it inherits the same shared physics for free, with its own override for slower gravity:

```python
class WallSlideState(AirborneState):
    name = "wall_slide"
    SLIDE_GRAVITY = 400.0  # gentler than the airborne 1800

    def update(self, char, dt):
        char.vx = 0  # pinned to the wall horizontally
        char.vy += self.SLIDE_GRAVITY * dt
        if not char.touching_wall:
            char.change_state(FallState())
        if char.jump_pressed:
            char.change_state(WallJumpState())
```

This is **hierarchical FSM** territory and Statecharts (Harel 1987) made it formal. The Python implementation is plain inheritance. The mental model is: the parent state owns the "what is true for all airborne states"; each child overrides what is specific. You can read the parent and know the shared invariant; you can read each child and know its differentiator. The pattern scales smoothly to twenty states because the parents do the heavy lifting and the children are short.

> A practical rule: **promote shared code to a parent state class the moment two states share more than five lines.** Below five, the duplication is cheaper than the abstraction. Above five, the parent earns its keep.

---

## 5. The state stack (pushdown automaton)

So far we've replaced the current state with a new state. Transitions are *moves*, not *additions*. That model breaks for one common pattern: **pausing**. When the player hits ESC during gameplay, you don't want to *transition* to a `PauseState` that has its own physics — you want to *suspend* the current state, overlay a pause menu, and *resume* the suspended state when the player unpauses. The pause is a *stack push*; the unpause is a *stack pop*.

A **pushdown automaton** is an FSM with a stack of states instead of one current state. The top of the stack is "the active state." Push adds a new state on top; pop removes the top and reveals the one beneath.

```python
class Character:
    def __init__(self):
        self.state_stack: list[State] = [IdleState()]
        self.state_stack[-1].enter(self)

    @property
    def state(self) -> State:
        return self.state_stack[-1]

    def push_state(self, new_state: State):
        # Don't exit the current state — it's only suspended.
        self.state_stack.append(new_state)
        new_state.enter(self)

    def pop_state(self):
        top = self.state_stack.pop()
        top.exit(self)
        # The new top resumes — no enter() call; it never left.

    def change_state(self, new_state: State):
        # Replace the top of the stack.
        top = self.state_stack.pop()
        top.exit(self)
        self.state_stack.append(new_state)
        new_state.enter(self)

    def update(self, dt):
        self.state.update(self, dt)
```

Three operations: `push`, `pop`, `change`. The first two are the stack-only operations; the third is the classic FSM transition. A game uses both at the same time:

- **Push:** pause menu, dialog box, "stunned" overlay, cutscene.
- **Change:** the bread-and-butter FSM transition (`idle` -> `run`).

This is why the State pattern wins long-term: layering a pushdown automaton on top of it is *six lines*. Adding a pause menu to a hand-rolled FSM with a flat transition table requires re-thinking the table.

The full runnable version of the state stack is **exercise-03**. The exercise pauses gameplay and overlays a "PAUSED — press ESC to resume" screen.

---

## 6. Per-state data: instance versus character

A subtle but important question: where do timers and per-state counters *live*?

**On the state instance** (most often correct):

```python
class AttackState(State):
    def enter(self, char):
        self.timer = 0.4  # 400 ms attack swing
        char.swing_active = True

    def update(self, char, dt):
        self.timer -= dt
        if self.timer <= 0:
            char.change_state(IdleState())

    def exit(self, char):
        char.swing_active = False
```

`self.timer` lives on the *instance* of `AttackState`. When the character leaves attack, the instance is replaced by `IdleState()`, and `self.timer` is garbage-collected with it. Clean.

**On the character** (sometimes necessary):

```python
class Character:
    def __init__(self):
        # ...
        self.hurt_invincible_until: float = 0.0  # world time

class HurtState(State):
    def enter(self, char):
        char.hurt_invincible_until = char.now + 0.5
```

`hurt_invincible_until` has to live on `char` because *other states* read it. `IdleState.update` checks "am I still invincible from the recent hit?" The value must survive the transition out of `HurtState`.

The rule is mechanical: **if the value matters only while the state is current, it lives on the state instance. If other states read it after the transition, it lives on the character.** When in doubt, put it on the instance — that is the State pattern's structural advantage, and moving a field up to the character when you discover other states need it is an easy refactor.

---

## 7. Animation events tied to transitions (the bridge to Week 6)

The State pattern makes Week 6 trivial. Animation is a per-state phenomenon: `idle` plays the breathing loop; `run` plays the run cycle; `jump` plays the jump-launch one-shot. The `enter()` hook is where you start the clip; the `exit()` hook is where you stop or fade it.

```python
class RunState(State):
    name = "run"

    def enter(self, char):
        char.anim.play("run_loop", loop=True)
        char.sfx.play("footsteps", loop=True, volume=0.3)

    def exit(self, char):
        char.anim.stop()
        char.sfx.stop("footsteps")
```

Reading the class tells you both the physics rules (`update`) and the audio/visual rules (`enter` and `exit`). The behaviour of running and the *presentation* of running live in the same place. This is the **bind-presentation-to-state** principle that Valve's animation talks (linked in `resources.md`) hammer at length.

For Week 5 we don't have sprite art yet. Don't worry — the *hook* belongs in Week 5. We wire `char.anim.play("run_loop")` as a no-op printf in `RunState.enter` this week. Week 6 wires it to an actual `SpriteSheet` and your screen lights up. Two weeks of work, but the *architectural* commitment is Week 5's.

---

## 8. The three classic bugs, revisited

Lecture 1 §12 named the three classic FSM bugs. The State pattern makes each one structurally harder to write. Here's how.

**Bug 1: forgotten exit-action.**

Hand-rolled FSM: you have an `ON_ENTER` dict but you forget to also write an `ON_EXIT`. The dust-puff emitter started in `IDLE -> RUN` keeps running through every subsequent state because there's no symmetric off-switch.

State pattern: the slot for `exit` is *visible* in the class. You either fill it in or write `def exit(self, char): pass` explicitly. The signal that you have to think about cleanup is *the class definition itself*. You can still forget; the pattern makes forgetting harder.

**Bug 2: illegal transition silently succeeds.**

Hand-rolled FSM: you call `TRANSITIONS[key]` unguarded, hit `KeyError`, write a fallback `try/except` that swallows the error. The bug vanishes from the logs and from your mind.

State pattern: a transition is `char.change_state(SomeState())`. There is no transition table to look up in. The state's `update` decides "should I transition?" If the conditions are met, it calls `change_state`. There is no key to miss, no fallback to write. The bug class is structurally absent.

(There's a different illegal-transition risk: `JumpState.update` reads `char.jump_pressed` and tries to *double-jump*. That's not an FSM bug — it's a missing condition. Guard it explicitly: `if char.jump_pressed and char.grounded`. The State pattern doesn't save you from missing conditions; it saves you from misrouted ones.)

**Bug 3: state leak.**

Hand-rolled FSM: `char.attack_timer` is set in the attack handler; the next state doesn't know to clear it; the timer keeps ticking; suddenly the player can attack again "even though they're in hurt." The leak is between the handler that set the field and the handler that should have cleared it.

State pattern: per-state data lives on the state *instance*. When `AttackState` is replaced, its `self.timer` is gone. The leak surface is much smaller. The only fields that can leak are the ones you put on `char` (e.g. `char.hurt_invincible_until` from §6), and those are the explicitly-shared ones, where leakage is the *point*.

> Every pattern is a trade. The State pattern's cost is *more files / more class definitions*. Its payoff is the three bug classes above being structurally rarer. For four-state characters, the trade is borderline. For ten-state characters with substates, the trade is a no-brainer.

---

## 9. When the State pattern is *too much*

The State pattern wins for character AI, player controllers, and any object whose behaviour has more than four mutually-exclusive modes. It is *not* the right tool for:

- **Simple boolean toggles.** `door.is_open: bool` is fine. Don't write `OpenDoorState` / `ClosedDoorState`. The classes are overhead with no payoff.
- **Pure data records.** A `Bullet` that flies in a straight line and explodes on impact has one state. It doesn't need a state machine.
- **Top-level game flow** (menu / playing / paused / game-over). This *is* a state machine, but the state-stack version from §5 is the right shape. Don't write four classes for four screens — write a stack and push/pop.
- **Anything with more than fifteen states.** At fifteen states the State pattern starts feeling like a hundred class definitions. You want a **behaviour tree** (covered in Week 11 stretch or your own reading) or **GOAP** (Jeff Orkin's *F.E.A.R.* talk in `resources.md`). FSMs scale to about fifteen; behaviour trees scale to hundreds.

The week's pattern is the State pattern. It is the right answer for *this* week's player character (four states with substate ambitions). It will be right for next month's enemy AI. It will *not* be right when you have a hundred-state ranger that decides when to climb a rope versus eat a meal versus call for help — that's a different course.

---

## 10. The diagram-to-code workflow (the discipline)

A four-state machine is small enough to hold in your head. A ten-state machine is not. The discipline that scales is: **draw the diagram first, code it second.**

1. **Sketch on paper** (or in a free tool like the XState statechart visualiser, linked in `resources.md`). Boxes are states. Arrows are transitions. Label each arrow with its triggering event.
2. **List the entry side effects per state.** Next to each box, jot one or two notes: "play jump sound; set vy = -650." These become the `enter` body.
3. **List the exit side effects per state.** Next to each box, jot the things the state *adds* to the character (emitter, flag, override). Each becomes a line in `exit`.
4. **List the loop body per state.** What happens every frame inside the state.
5. **Now open your editor.** Type out the classes in the order of the diagram, top to bottom. Each class is roughly: `class FooState: name; enter(); update(); exit()`.
6. **Compile and run.** If the diagram is right and the typing is faithful, the player works on the first run. Most of the bugs in this lecture are *diagram bugs* — a missing arrow, a state with no entry. The diagram is the source of truth.

The diagram is the design artefact. Photograph it; commit the photo to the repo. When you come back in two months and add a state, you start by editing the diagram, then by editing the code. The two stay in lockstep.

---

## 11. The complete picture: an annotated state machine

Putting it all together, a player character at the end of this week has the following shape:

```
                MOVE_PRESSED
   +---------+ <--------- +---------+
   |  IDLE   | ---------> |   RUN   |
   +---------+ MOVE_REL.  +---------+
       |  ^                  |  ^
       |  | LANDED   JUMP_P. |  | LANDED
       v  |                  v  |
   +---------+ FELL_OFF_  +---------+
   |  FALL   | <--------- |  JUMP   |
   +---------+            +---------+
       |
       | HIT_BY_SPIKE        (HIT_BY_SPIKE from any state)
       v
   +---------+
   |  HURT   | --(timer_done)--> IDLE (or FALL if airborne)
   +---------+
```

Five states. Eight or nine transitions. Two of the transitions can fire from *any* state — the `HIT_BY_SPIKE` arrow into `HURT`. That's modelled in code with:

```python
class Character:
    def take_hit(self, source):
        if isinstance(self.state, HurtState):
            return  # already hurt; can't be hurt twice
        self.change_state(HurtState(source))
```

A *method on the character*, not a transition entry. Methods like `take_hit` are how you express "this can happen anywhere" without polluting every state's `update`. Use them sparingly — too many cross-cutting methods are a smell — but for the obvious case of "damage from external sources," it's right.

The `HurtState` *itself* is then trivially:

```python
class HurtState(State):
    name = "hurt"

    def __init__(self, source):
        self.source = source
        self.timer = 0.5  # 500 ms invulnerability + stagger

    def enter(self, char):
        char.invincible = True
        # Knockback away from the hit source.
        knockback_dir = -1 if self.source.x < char.x else +1
        char.vx = knockback_dir * 200.0
        char.vy = -300.0  # small upward pop

    def update(self, char, dt):
        # Decay knockback over time.
        char.vx *= 0.92
        char.vy += GRAVITY * dt
        self.timer -= dt
        if self.timer <= 0:
            if char.grounded:
                char.change_state(IdleState())
            else:
                char.change_state(FallState())

    def exit(self, char):
        char.invincible = False
```

Read the class. The whole "what does hurt do?" question is answered in twenty lines. No grep across the codebase. No `if is_hurt:` scattered through `update_player`. The class *is* the answer.

That is the architectural payoff of the State pattern. Find it in your own mini-project this week and you will keep reaching for it for the rest of the course.

---

## What you should take away

- The State pattern: one class per state, three methods (`enter`, `update`, `exit`).
- The class structure pairs `enter` and `exit` *by construction* — the slot is visible whether you fill it or not.
- Transitions are decided inside the source state's `update`. No central transition table.
- Hierarchical FSMs are plain inheritance in Python: an `AirborneState` parent for `JumpState`, `FallState`, `WallSlideState`.
- State stacks (pushdown automata) handle pausing and overlays in six extra lines.
- Per-state data lives on the state instance by default; only fields that other states read should live on the character.
- The diagram-to-code workflow keeps the design and the implementation in sync.
- The State pattern wins above five states; below five, the hand-rolled FSM from Lecture 1 is shorter and equally clear.

Continue to [the exercises](../exercises/) and pick up exercise-01.
