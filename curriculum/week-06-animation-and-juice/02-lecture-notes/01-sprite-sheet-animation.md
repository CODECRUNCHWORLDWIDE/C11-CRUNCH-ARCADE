# Lecture 1 — Sprite-Sheet Animation

> **Duration:** ~2 hours of reading + hands-on.
> **Outcome:** You can load a sprite sheet, define an `Animation` clip, advance it frame-rate-independently, and bind playback to your Week-5 FSM by calling `anim.play("run_loop")` in `RunState.enter` and `anim.stop()` in `RunState.exit`.

If you only remember one thing from this lecture, remember this:

> **A sprite sheet is one PNG. An animation is a list of frame indices plus an `fps`. The FSM's `enter()` hook calls `play(clip)`; `exit()` calls `stop()`. The whole bridge from Week 5 to Week 6 fits in twelve lines of code.**

The lecture builds toward that twelve-line bridge. We will first explain the *shape* of a sprite sheet — why one PNG and not thirty — then write the `SpriteSheet` and `Animation` classes from scratch, then wire them into your Week-5 player. By the end you can read every published Pygame platformer's animation code without looking anything up.

---

## 1. The single PNG is the right shape

A character's idle animation is four frames. The run cycle is six. The jump launch is one frame, the airborne pose is one, the landing-squash is one. The hit-react is two. Total: a dozen-ish frames for a small character.

The wrong way: thirty PNG files in `art/character/idle/`, `art/character/run/`, etc. Each file is a separate disk read, a separate decode, a separate `pygame.image.load()` call. The cache fragments. The filenames drift. The numbering breaks when someone adds a frame and re-numbers everything.

The right way: **one PNG with a grid of frames**. Sixty-four-pixel-wide cells, sixty-four-pixel-tall cells, eight columns and four rows. Thirty-two cells, twelve of them used, the rest empty (or filled with the next character). Disk reads: one. Decodes: one. `pygame.image.load()` calls: one. The grid is the *index*; the animation clip says "frames 0-3 are idle, 8-13 are run." The numbering is per-clip, not per-character.

Kenney's *Platformer Characters* pack ships sprite sheets in exactly this shape. Look at one. The PNG is 384×256 pixels. The cells are 64×64. The character struts across the top row in eight frames; jumps in two; takes a hit in two; falls in one. You bind clips to those indices. The artist edits one file. The code reads one file.

This is the same architectural rhyme as Week 4 (one tilemap CSV, not a directory of per-tile images) and Week 5 (one transition table, not a function of nested `if`s). Concentrate the data; thin out the code that touches it.

---

## 2. The `SpriteSheet` class

A `SpriteSheet` wraps a `pygame.Surface` and exposes a `frame(i)` method that returns the i-th cell as a subsurface. Twelve lines.

```python
from dataclasses import dataclass
import pygame


@dataclass
class SpriteSheet:
    surface: pygame.Surface
    frame_w: int
    frame_h: int

    @property
    def cols(self) -> int:
        return self.surface.get_width() // self.frame_w

    @property
    def rows(self) -> int:
        return self.surface.get_height() // self.frame_h

    def frame(self, index: int) -> pygame.Surface:
        col = index % self.cols
        row = index // self.cols
        rect = pygame.Rect(col * self.frame_w, row * self.frame_h,
                           self.frame_w, self.frame_h)
        return self.surface.subsurface(rect)
```

Three things to notice.

1. **`subsurface()` does not copy pixels.** It returns a *view* into the parent surface. Allocations: zero per frame. This is why a sprite sheet beats thirty PNGs on memory and load time both.
2. **Frames are addressed by a single integer.** Row-major: index 0 is top-left, index `cols` is the start of row 2. The artist doesn't care about row/col; the code converts.
3. **`frame_w` and `frame_h` are *cell* dimensions**, not character dimensions. If the artist draws a 32×32 character in a 64×64 cell with 16-pixel padding on every side, the cell is 64×64 and the cell-padding is the *art*, not the code. Cell-padding is the artist's discipline; cell size is the engineer's.

For sheets where some cells are pixel-art and others are blank, the blank cells are just transparent pixels. The `frame(i)` view is the same; the surface happens to be fully transparent. No special case in code.

---

## 3. Loading a sheet from disk

```python
def load_sheet(path: str, frame_w: int, frame_h: int) -> SpriteSheet:
    surface = pygame.image.load(path).convert_alpha()
    return SpriteSheet(surface=surface, frame_w=frame_w, frame_h=frame_h)
```

Two pitfalls beginners hit, both worth a one-line fix:

- **`convert_alpha()` is mandatory.** Without it, every blit composites slowly against a fully-opaque RGB pixel and your frame rate drops 30%. Always call `.convert_alpha()` (or `.convert()` for opaque sheets) right after `load`. The conversion matches the surface to the display's pixel format. The cost is one allocation at load time; the benefit is fast blits forever.
- **The display must exist before `convert_alpha()`.** Call `pygame.display.set_mode((W, H))` *before* `load_sheet`. Otherwise Pygame doesn't know the destination format and `convert_alpha` either errors or silently no-ops. Symptom: the sheet loads, but blits are 3x slower than the same code on the same machine an hour later. Always init display first, load assets second.

---

## 4. The `Animation` class

An animation is a list of frame *indices* into a sprite sheet, plus an `fps` and a `loop` flag. The class holds the elapsed time and reports the current frame.

```python
from dataclasses import dataclass, field


@dataclass
class Animation:
    sheet: SpriteSheet
    frames: list[int]   # indices into the sheet
    fps: float = 12.0   # frames per second of *animation*, not render
    loop: bool = True
    elapsed_t: float = 0.0
    finished: bool = False

    def reset(self) -> None:
        self.elapsed_t = 0.0
        self.finished = False

    def update(self, dt: float) -> None:
        if self.finished:
            return
        self.elapsed_t += dt
        if not self.loop:
            total = len(self.frames) / self.fps
            if self.elapsed_t >= total:
                self.elapsed_t = total
                self.finished = True

    def current_frame(self) -> pygame.Surface:
        i = int(self.elapsed_t * self.fps)
        if self.loop:
            i %= len(self.frames)
        else:
            i = min(i, len(self.frames) - 1)
        return self.sheet.frame(self.frames[i])
```

The class has six fields and three methods. Read each:

- **`fps`** is the animation's playback rate, not the render rate. An animation at 12 fps plays one frame every ~83 ms. The render loop runs at 60 fps, so each animation frame is drawn ~5 times before it advances. This is normal and correct — animation rate and render rate are different things and the lecture's whole point is that the two are *decoupled*.
- **`elapsed_t`** ticks in seconds, accumulating `dt` every frame. The current frame index is `int(elapsed_t * fps)`. For a 12 fps animation, that's a new frame every 83 ms regardless of whether the render frame rate is 60, 144, or 30 fps. **Frame-rate-independent animation in two lines.**
- **`loop=True`** wraps with `%`. Idle, run, breathing — all looping. **`loop=False`** clamps to the last frame and sets `self.finished = True`. Jump-launch, hit-react, attack-swing — all one-shot. The `finished` flag is what the FSM watches to decide *the next state*.

That's the entire animation engine. Twenty-five lines of code, frame-rate-independent, supports looping and one-shot, indexes into a single sheet.

---

## 5. Frame-rate independence: why `elapsed_t * fps` and not `frame_count + 1`

A beginner's first cut at animation looks like this:

```python
def update(self):
    self.frame_count += 1
    if self.frame_count >= 6:
        self.frame_count = 0
```

Run it at 60 fps and the animation advances one render frame at a time — 60 sprite frames per second. Six-frame loop = ten cycles per second. The character is a blur.

Run it at 30 fps (a slow laptop, an unplugged monitor cable, vsync misconfigured) and the animation advances at 30 sprite frames per second — five cycles per second. The character now looks like a slow-motion zombie.

Run it at 144 fps (a gaming monitor, vsync off) and 24 cycles per second. The character is a strobe light.

**The render rate and the animation rate are not the same thing.** Tie animation to render and your art is wrong on every machine that isn't yours.

The fix is the `dt`-correct integration we used for physics in Week 1. `elapsed_t += dt`, current frame is `int(elapsed_t * fps)`. The render rate falls out entirely. A 12 fps animation plays at 12 fps whether the monitor renders at 30, 60, or 144 fps.

This is the same lesson as Week 1's `dt`-correct movement, applied to animation. The principle scales: any per-second rate (animation fps, particle emission rate, healing tick rate, tween progress) is `rate * dt` accumulated, not `rate += 1` per render frame.

---

## 6. The animation library: one dict per character

A character has a *library* of animation clips. Idle, run, jump-launch, jump-airborne, fall, land, hurt, attack. The library is a `dict[str, Animation]`. The character holds one `current: Animation` reference, and `play(name)` swaps it.

```python
@dataclass
class Animator:
    library: dict[str, Animation]
    current: Animation | None = None
    current_name: str = ""

    def play(self, name: str, restart: bool = False) -> None:
        clip = self.library.get(name)
        if clip is None:
            print(f"[anim] missing clip: {name}")
            return
        if clip is self.current and not restart:
            return  # already playing; don't reset
        self.current = clip
        self.current_name = name
        clip.reset()

    def stop(self) -> None:
        self.current = None
        self.current_name = ""

    def update(self, dt: float) -> None:
        if self.current is not None:
            self.current.update(dt)

    def current_frame(self) -> pygame.Surface | None:
        if self.current is None:
            return None
        return self.current.current_frame()
```

Three things to notice.

1. **`play(name)` is idempotent when the clip is already playing.** Calling `anim.play("run_loop")` every frame from `RunState.update` is fine — the second call early-outs. This matters because the State pattern's `update` runs every frame and you don't want to reset the animation on every call.
2. **The `restart` flag is for one-shots.** When the player jumps twice in quick succession, you want each jump to *restart* the jump-launch clip rather than continue from the middle. `anim.play("jump_launch", restart=True)` does that.
3. **`stop()` clears `current`.** Drawing then returns `None`; the caller draws a fallback (the character's default pose, or the last frame, or nothing). For this week we always have a `current`; for next week's add-ons (a brief "no animation" beat between states), `stop()` matters.

---

## 7. Binding animations to FSM states (the bridge to Week 5)

Open your Week-5 player. Find `RunState.enter`. It looks like this:

```python
class RunState(State):
    name = "RunState"

    def enter(self, char):
        pass

    def update(self, char, dt):
        # ... transitions ...
        pass

    def exit(self, char):
        pass
```

Add three lines:

```python
class RunState(State):
    name = "RunState"

    def enter(self, char):
        char.anim.play("run_loop")
        char.sfx.play("footsteps_loop", loop=True, volume=0.3)

    def update(self, char, dt):
        # ... transitions unchanged ...
        pass

    def exit(self, char):
        char.sfx.stop("footsteps_loop")
```

That's the bridge. Reading `RunState` tells you both:

- **What the character *does* while running** (`update`): the transition rules.
- **What the character *looks like and sounds like* while running** (`enter` / `exit`): the animation clip and the looping SFX.

The Week 5 lecture promised this exact shape. Now we light it up.

Other states follow the same pattern:

```python
class IdleState(State):
    def enter(self, char):
        char.anim.play("idle_breathing")

    def exit(self, char):
        pass  # idle has no audio override


class JumpState(AirborneState):
    def enter(self, char):
        char.vy = -JUMP_VEL
        char.grounded = False
        char.anim.play("jump_launch", restart=True)
        char.sfx.play_one_shot("jump")

    def exit(self, char):
        pass


class FallState(AirborneState):
    def enter(self, char):
        char.anim.play("fall_airborne")

    def exit(self, char):
        pass


class HurtState(State):
    def enter(self, char):
        char.anim.play("hurt_react", restart=True)
        char.sfx.play_one_shot("hit")
        char.invincible = True

    def exit(self, char):
        char.invincible = False
```

Five classes. Each one has the same shape: `enter` plays an animation and optionally an SFX; `update` decides transitions; `exit` stops anything `enter` started. The character's *presentation* now lives next to its *behaviour*, exactly where Lecture 2 of Week 5 said it should.

If you remember nothing else from this lecture, remember the shape: **`enter() = play(); exit() = stop()`**. Everything else this week is dressing.

---

## 8. One-shot animations and the "finished" signal

A jump-launch is a one-shot — three frames, plays once, *then* the character is in their airborne pose. The transition out of "jump-launch animation" into "airborne pose" is *not* an FSM state transition. The character is in `JumpState` through both. The animation library is what changes.

The clean shape: `jump_launch` is `loop=False`. When it finishes, `JumpState.update` notices and plays the next clip:

```python
class JumpState(AirborneState):
    def enter(self, char):
        char.vy = -JUMP_VEL
        char.grounded = False
        char.anim.play("jump_launch", restart=True)
        char.sfx.play_one_shot("jump")

    def update(self, char, dt):
        self.update_airborne(char, dt)
        # When the launch clip finishes, swap to the airborne loop.
        if char.anim.current_name == "jump_launch" and char.anim.current.finished:
            char.anim.play("jump_airborne")
        # The FSM transition is unchanged: apex -> FallState.
        if char.vy >= 0:
            char.change_state(FallState())
```

Three things to notice.

1. **Animation transitions are *inside* an FSM state.** A state can play multiple clips over its lifetime. Idle → run → jump is one FSM transition each; jump-launch → jump-airborne is *one* FSM state (JumpState) with two animation clips.
2. **The `finished` flag is the signal.** No timer in the FSM. The animation's own clock owns the timing. Move the `fps` from 12 to 24 and the launch-to-airborne handoff happens twice as fast, no FSM changes.
3. **One-shot SFX, not loop.** `play_one_shot("jump")` fires the sound once when the state is entered. Looping SFX (footsteps) call `play("footsteps_loop", loop=True)` and `stop` on exit. The pattern in Lecture 2 makes the distinction explicit.

---

## 9. Direction: the horizontal flip

A 2D platformer character runs both left and right. The artist draws one direction (usually right-facing) and the engine flips horizontally for the other direction.

```python
def draw_character(screen, char):
    frame = char.anim.current_frame()
    if frame is None:
        return
    if char.facing == -1:  # facing left
        frame = pygame.transform.flip(frame, True, False)
    screen.blit(frame, (int(char.x), int(char.y)))
```

Two things to notice.

1. **`facing` is a separate field from `vx`.** When the player runs right and then stops, they keep facing right during the idle. `facing` only flips when the player moves the *opposite* direction. Updating: `if char.move_input != 0: char.facing = sign(char.move_input)`.
2. **`pygame.transform.flip()` is fast** but it does allocate a new surface. For a single character it's fine. For ten characters with run animations, you cache the flipped sheet at load time (a second `SpriteSheet` flipped horizontally) and pick the right sheet per-frame. We do that in the mini-project; the exercise uses the per-frame flip for clarity.

---

## 10. Padding, anchors, and offsets

A character's *art* is usually smaller than its *cell*. The 32×32 character sits in a 64×64 cell, padded with 16 pixels of transparency on every side. Reasons:

- The animator wants room for **squash-and-stretch** without clipping. A 64-pixel cell can hold a 48-pixel-tall stretched character.
- The animator wants room for **anticipation poses** — a wind-up before an attack that extends the silhouette horizontally.
- The animator wants room for **effects on the sprite** — a brief lightning aura, a recoil offset.

The cost: when you blit the cell at `(x, y)`, the character is *not* at `(x, y)`. It's at `(x + pad_x, y + pad_y)`. For collision, that matters. For drawing alone, it does not.

The fix: the character's `x`, `y` is the *collision rect's top-left*, not the cell's top-left. Drawing offsets by the padding:

```python
draw_x = int(char.x) - pad_x
draw_y = int(char.y) - pad_y
screen.blit(frame, (draw_x, draw_y))
```

Where `pad_x = (cell_w - collision_w) // 2` and `pad_y = cell_h - collision_h` (the character's feet are usually at the bottom of the cell; pad_y is the height of the head-room).

For this week's exercise we keep the cell size *equal to* the collision size — the character has no padding — so the question doesn't come up. For the mini-project, when you load a real Kenney sheet, the padding is the first thing to get right. The HUD's "the character draws above the floor" bug is always a padding-offset bug. Now you know.

---

## 11. The animation library lives in code (this week)

For this week we define the animation library inline:

```python
def make_character_animations(sheet: SpriteSheet) -> dict[str, Animation]:
    return {
        "idle_breathing":  Animation(sheet, frames=[0, 1, 2, 3], fps=6.0,
                                     loop=True),
        "run_loop":        Animation(sheet, frames=[8, 9, 10, 11, 12, 13],
                                     fps=12.0, loop=True),
        "jump_launch":     Animation(sheet, frames=[16, 17, 18], fps=18.0,
                                     loop=False),
        "jump_airborne":   Animation(sheet, frames=[19], fps=1.0, loop=True),
        "fall_airborne":   Animation(sheet, frames=[20], fps=1.0, loop=True),
        "land_squash":     Animation(sheet, frames=[21, 22], fps=18.0,
                                     loop=False),
        "hurt_react":      Animation(sheet, frames=[24, 25], fps=10.0,
                                     loop=False),
    }
```

Seven clips. The dictionary is hand-written. The frame indices are hand-picked. The `fps` is hand-tuned.

The natural next step (Week 7+) is to move this into a JSON or TOML file edited by the artist:

```json
{
  "idle_breathing": {"frames": [0, 1, 2, 3], "fps": 6, "loop": true},
  "run_loop": {"frames": [8, 9, 10, 11, 12, 13], "fps": 12, "loop": true}
}
```

The same rhyme as Week 4 (levels in CSV, not Python) and Week 5 (transitions in a dict — or, for a real project, a JSON file). Concentrate the data; thin out the code. For this week, inline is fine; the *architectural commitment* is what matters.

---

## 12. Frame budget: animation is cheap

A frame-budget tile so you know the cost.

```
┌─────────────────────────────────────────────────────────┐
│  ANIMATION FRAME BUDGET — 60 fps, 12 animated entities  │
│                                                         │
│  Per-character anim.update():    ~0.005 ms              │
│  Per-character current_frame():  ~0.002 ms (subsurface) │
│  Per-character flip (if needed): ~0.020 ms (allocates)  │
│  Per-character blit:             ~0.040 ms              │
│                                                         │
│  Total for 12 characters:        ~0.8 ms / frame        │
│  Out of a 16.6 ms frame:         4.8% of budget         │
└─────────────────────────────────────────────────────────┘
```

Animation is one of the *cheapest* substantive costs in a frame. If your profiler shows animation taking more than 1 ms for a player + a handful of enemies, you almost certainly have a *blit* problem (no `convert_alpha`, or transform.flip in a hot loop without caching), not an animation-system problem.

The lecture's point is to make the cost *explicit* — and *unsurprising*. Juice is not a frame-rate-killer. It is a taste decision.

---

## 13. What you should write after this lecture

Before you open Lecture 2 or the exercises, do this on paper:

1. **List the clips your Week-5 character needs.** Idle, run, jump-launch, jump-airborne, fall-airborne, land-squash (one-shot), hurt-react, (later) attack-swing.
2. **For each clip, write three numbers**: `fps`, `loop`, and the approximate number of frames. The numbers are a budget for the artist.
3. **Pick a Kenney sheet** (or download one now). Open it in your image viewer. Count the cells. Map the cells to your clip list. (Two clips might share frames — `fall_airborne` and `jump_airborne` are often the same single frame.)
4. **Sketch the FSM-to-animation binding** as a table:

   | State        | `enter()` plays               | `exit()` stops          |
   |--------------|-------------------------------|--------------------------|
   | IdleState    | `idle_breathing` (loop)       | -                        |
   | RunState     | `run_loop` (loop)             | (footsteps loop)         |
   | JumpState    | `jump_launch` (one-shot)      | -                        |
   | FallState    | `fall_airborne` (loop, 1 fr)  | -                        |
   | HurtState    | `hurt_react` (one-shot)       | -                        |

5. **Now open the exercise.** You'll find the code mirrors the table. If the table is right, the code is right.

The table is the design artefact. The code is the implementation. The two should match; if they drift, the table is the source of truth.

---

## What you should take away

- A sprite sheet is one PNG. An animation is a list of frame indices, an `fps`, and a `loop` flag.
- `subsurface()` does not copy. `convert_alpha()` is mandatory and must be called after `set_mode`.
- Animations advance with `elapsed_t * fps`, not `frame_count + 1`. Frame-rate-independent in two lines.
- A character has an `Animator` with a `library: dict[str, Animation]`. `play(name)` is idempotent; `play(name, restart=True)` resets.
- The FSM `enter()` hook calls `anim.play(clip)`. The `exit()` hook calls `anim.stop()` or, more commonly, stops *only the loops* (`sfx.stop("footsteps")`).
- One-shot animations end and the `finished` flag tells the *containing FSM state* to play the next clip — without changing FSM state.
- The horizontal flip is one `pygame.transform.flip()` call, gated on `char.facing`.
- Animation is cheap. ~0.8 ms for twelve characters. Worry about taste, not budget.

Continue to [Lecture 2 — Tweening, easing, and juice](./02-tweening-easing-and-juice.md).
