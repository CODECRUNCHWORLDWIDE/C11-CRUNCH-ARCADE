# Challenge 1 — Enemy AI FSM

**Time estimate:** ~120 minutes (state-diagram sketch, code, tune, write-up).

## Problem statement

Build a single enemy character driven by a four-state FSM: `patrol`, `chase`, `attack`, `return`. The enemy uses the same `State` base class as the player from Exercise 2; the difference is that the enemy's transitions are driven by *observation* of the player (distance, line-of-sight, attack range) rather than by input.

This is the artefact that distinguishes "I have a player state machine" from "I have a *character* state machine." The pattern is reusable. Same shape, different intent — and after this challenge you've felt the reuse in your own hands.

You will produce three artefacts:

1. **One Python file** at `challenges/challenge-01/enemy_fsm.py`, runnable, that draws a 600×400 arena with a player (driven by arrow keys), an enemy (driven by the FSM), and one static obstacle. The HUD shows the enemy's current state.
2. **A state diagram** at `challenges/challenge-01/diagram.png` (or `diagram.txt` if you draw it with ASCII art). Boxes are states; arrows are transitions; each arrow is labelled with the event that triggers it.
3. **A 150-200 word write-up** at `challenges/challenge-01/WRITEUP.md` explaining the design: why these four states, what each transition's condition is, and one bug you hit and fixed during tuning.

## Acceptance criteria

- [ ] A folder `challenges/challenge-01/` exists in your repo.
- [ ] `python -m py_compile challenges/challenge-01/enemy_fsm.py` succeeds with no output.
- [ ] `python challenges/challenge-01/enemy_fsm.py` opens a 600×400 window with a patrolling enemy.
- [ ] The enemy has **four states**: `patrol`, `chase`, `attack`, `return`. Each is its own class subclassing the `State` base from Exercise 2.
- [ ] **Patrol:** the enemy walks back and forth between two patrol points, at constant speed.
- [ ] **Chase:** when the player is within `CHASE_RADIUS` (default 180 px) AND has line-of-sight (no obstacle between the enemy and the player), the enemy transitions to chase and moves toward the player.
- [ ] **Attack:** when the player is within `ATTACK_RADIUS` (default 40 px), the enemy transitions to attack. The attack draws a brief Coin-Pink "swing" indicator for 200 ms and the enemy stops moving during the swing.
- [ ] **Return:** when the player breaks line-of-sight OR moves beyond `LOSE_RADIUS` (default 260 px — note the hysteresis), the enemy transitions to return and walks back toward its nearest patrol point.
- [ ] On reaching the patrol point, the enemy transitions back to `patrol`.
- [ ] Each transition is logged to the console: `[fsm] PatrolState -> ChaseState`.
- [ ] The HUD shows the current state's class name (e.g. `state: ChaseState`).
- [ ] The state diagram exists, is committed, and accurately reflects the implementation (no state-diagram-and-code drift).
- [ ] A `WRITEUP.md` of 150-200 words exists and:
  - Names the four states and what each one *does*.
  - Lists the transitions and what triggers each.
  - Describes the hysteresis pair (`CHASE_RADIUS` < `LOSE_RADIUS`) and why a single radius would cause oscillation.
  - Describes one bug you hit and how you fixed it.
  - Cites Lecture 2 (the State pattern) by name.

## Suggested order of operations

Build incrementally. Each phase ends with a commit.

### Phase 1 — Sketch the diagram (~15 min)

1. Take a piece of paper. Draw four boxes labelled `patrol`, `chase`, `attack`, `return`.
2. Draw arrows. From `patrol` you can reach `chase`. From `chase` you can reach `attack` or `return`. From `attack` you can reach `chase` or `return`. From `return` you can reach `patrol` or `chase` (if the player re-enters the chase radius while the enemy is returning).
3. Label each arrow with its triggering condition: `player_in_chase_radius and LOS`, `dist <= ATTACK_RADIUS`, `swing_timer <= 0`, `dist > LOSE_RADIUS or not LOS`, `reached_patrol_point`.
4. Commit the photo or ASCII diagram: `Add enemy FSM state diagram`.

### Phase 2 — Scaffold the file (~10 min)

1. Copy `exercise-02-character-with-states.py` to `enemy_fsm.py` as a starting point.
2. Strip out the player FSM. Keep the `State` base class, the Pygame loop, and the rendering helpers.
3. Add a `Player` dataclass with arrow-key movement (no FSM needed; the player is the user's input).
4. Add an `Enemy` dataclass with `x`, `y`, `speed`, `state`, `change_state` (copy from `Character` in Exercise 2).
5. Commit: `Scaffold arena, player, enemy stub`.

### Phase 3 — Patrol state (~15 min)

1. Implement `PatrolState`. On `enter`, set the enemy's target to the next patrol point. On `update`, move toward the target; on arrival, swap to the other patrol point.
2. No transitions yet. Run the file; confirm the enemy paces back and forth.
3. Commit: `Add PatrolState; enemy paces between two points`.

### Phase 4 — Chase + LOS (~30 min)

1. Implement a `line_of_sight(a, b, obstacle_rect)` helper. Use a simple segment-vs-rect intersection. Three lines:

   ```python
   def line_of_sight(a, b, obstacle_rect):
       return obstacle_rect.clipline(a, b) == ()
   ```

   (`Rect.clipline` returns the clipped segment, or an empty tuple if there is no intersection. Inverted: an empty tuple means "no intersection," meaning *clear* LOS.)

2. Implement `ChaseState`. On `update`, move toward the player. Transitions: enter `AttackState` if within `ATTACK_RADIUS`; enter `ReturnState` if `dist > LOSE_RADIUS` or LOS is broken.
3. Add the transition out of `PatrolState`: `if dist_to_player < CHASE_RADIUS and LOS: change_state(ChaseState())`.
4. Test: walk near the enemy, watch it chase. Walk behind the obstacle, watch the chase break.
5. Commit: `Add ChaseState with line-of-sight and hysteresis`.

### Phase 5 — Attack + Return (~25 min)

1. Implement `AttackState`. On `enter`, set `self.swing_timer = 0.2`. On `update`, tick the timer; on `timer <= 0`, transition back to `ChaseState` if the player is still nearby, else to `ReturnState`. Draw a small Coin-Pink rectangle next to the enemy during the swing (you'll see it as a brief flash).
2. Implement `ReturnState`. On `enter`, pick the nearest patrol point as the target. On `update`, move toward it; on arrival, transition to `PatrolState`. Also: if the player re-enters the chase radius with LOS, transition straight back to `ChaseState`.
3. Test all four transitions. Walk into attack range. Walk away. Hide behind the obstacle.
4. Commit: `Add AttackState and ReturnState; FSM complete`.

### Phase 6 — Tune and write up (~25 min)

1. Tune the radii. `CHASE_RADIUS` < `LOSE_RADIUS` (the hysteresis pair) prevents oscillation when the player stands exactly on the boundary. Try `CHASE_RADIUS = 180`, `LOSE_RADIUS = 260` and feel the difference vs setting them equal.
2. Tune the enemy speed (faster in chase than in patrol is the convention; the chase feels purposeful).
3. Write `WRITEUP.md`. 150-200 words. Hit every bullet under the acceptance criteria.
4. Commit: `Tune enemy radii; add WRITEUP`.

## Stretch (any of these for extra polish)

- **A "search" state.** When the player breaks LOS, the enemy enters `SearchState` (a brief 1-2 second look-around at the last-known position) before falling back to `ReturnState`. This is what *Metal Gear Solid* enemies do; it makes the AI feel *alive* instead of *robotic*. Adds one state and two transitions.
- **A second enemy.** Spawn two of the same `Enemy` instances. They share the FSM definitions but each has its own state instance. Confirm in the HUD that they can be in different states simultaneously. Reuse, not duplication.
- **A "stunned" overlay.** When the player presses `Z`, fire a "stun" event at the nearest enemy. The enemy *pushes* a `StunnedState` on its own state stack (you'll need to add a stack from Exercise 3 to the `Enemy`). After 1.5 seconds, the stun pops and the previous state resumes. This is the bridge between Lecture 2's state stack and AI.
- **A patrol path** with three or four points instead of two. The enemy picks the next point in a cycle. One extra field on the `PatrolState` and a list on the `Enemy`.

## Hints

<details>
<summary>How do I do line-of-sight in Pygame?</summary>

`pygame.Rect.clipline(start, end)` returns the clipped portion of a segment that lies inside the rect. If the segment doesn't intersect the rect, it returns `()`. So:

```python
def line_of_sight(a: tuple[float, float], b: tuple[float, float],
                  obstacle_rect: pygame.Rect) -> bool:
    return obstacle_rect.clipline(a, b) == ()
```

For multiple obstacles, call this for each in a loop and `all()` the results. For dozens of obstacles, you want a spatial partition (Week 4's tilemap *is* one). For one obstacle, the loop is one call.
</details>

<details>
<summary>What's hysteresis and why does the challenge insist on it?</summary>

Hysteresis is "the threshold for entering a state is *tighter* than the threshold for leaving it." `CHASE_RADIUS = 180`, `LOSE_RADIUS = 260` means the enemy starts chasing when the player is within 180 px and stops chasing only when the player is more than 260 px away. The gap between them is the hysteresis band.

Without hysteresis (`CHASE_RADIUS == LOSE_RADIUS`), the enemy oscillates wildly when the player stands at exactly the boundary: chase, return, chase, return, chase, every frame. The oscillation is visible. The fix is the gap. This is the same trick a thermostat uses to avoid clicking on and off every second when the room is near the set point.
</details>

<details>
<summary>How do I avoid the "enemy gets stuck on the wall" bug?</summary>

You don't, in the challenge spec. The enemy's pathfinding is "move directly toward the target." If a wall is in the way, the enemy gets pinned. That's *fine* for the challenge — pathfinding is Week 11 territory. For now, place the obstacle so the LOS check is the interesting decision, not the movement. (If the enemy gets stuck on the obstacle's corner, drop the obstacle's collision and only use it for LOS. The enemy walks *through* the obstacle, which is silly but acceptable for a 120-minute challenge.)
</details>

<details>
<summary>What if my enemy never transitions out of attack?</summary>

The classic bug: you set `self.swing_timer = 0.2` in `__init__`, then `AttackState.__init__` re-runs every time you do `change_state(AttackState())`, so the timer keeps resetting. Make sure `AttackState`'s timer lives on the *new instance* — Python's `__init__` runs on construction, which is what you want; each `AttackState()` is fresh. But check: are you creating a new instance, or re-using the old one? If you're storing one `AttackState` instance somewhere and reusing it, the timer state leaks across visits. Always construct fresh: `change_state(AttackState())`, not `change_state(self.cached_attack_state)`.
</details>

## What "great" looks like

A friend who has never seen your project sits down. They see the arena, drive the player around, watch the enemy pace. They walk toward the enemy; the HUD flips to `ChaseState` and the enemy turns to follow. They duck behind the obstacle; the HUD flips to `ReturnState` and the enemy walks back to its post. They peek out; the enemy spots them and flips back to chase. They walk into attack range; the HUD flashes `AttackState` and a Coin-Pink swing pulses. After thirty seconds they say "okay, can I add a second enemy?" — and you tell them yes, instantiate another `Enemy()` and pass it the same `State` classes. They paste two lines and there are two enemies on screen, each in their own state. That's the moment the FSM-as-shared-pattern *clicks* — and it's also the moment that turns this challenge into a portfolio piece.
