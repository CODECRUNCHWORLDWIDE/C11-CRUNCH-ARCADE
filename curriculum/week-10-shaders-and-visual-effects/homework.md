# Week 10 Homework — Shaders and Visual Effects

> **Estimated time:** 4-5 hours.
> **Submit by:** Sunday 23:59 (your local time).
> **Deliverable:** a folder `week-10-homework/` containing the files described under each problem.

The homework consists of three problems plus a short write-up. Each problem produces one or two files. The total page-count of code you write is small (~150 lines of GDScript and shader code, ~80 lines of Python); the time goes into testing and tuning.

The write-up at the end (`homework-reflection.md`, 300-400 words) is graded. It is the part of the assignment that confirms you understood *why* the code does what it does.

---

## Problem 1 — Directional hit-flash

> **Estimated time:** 60 minutes.
> **Files to submit:** `hw1-directional-flash.gdshader`, `hw1-driver.gd`.

Extend the hit-flash shader from Exercise 2 to support *directional* damage feedback. When the player takes damage from the right, the flash leans toward red; from the left, toward blue; from above, toward yellow; from below, toward green. The directional bias is driven by a single `vec2` uniform `damage_direction` whose components are in -1..+1.

### Requirements

- The shader must declare exactly three uniforms in addition to `flash`: `damage_direction` (vec2), `directional_red` (vec3, default red), and `directional_blue` (vec3, default blue). (You may add more.)
- The fragment shader must compute a tint colour as a blend of the four directional colours weighted by `damage_direction`. For instance, when `damage_direction == vec2(1.0, 0.0)` the tint is fully red; when `vec2(0.0, 1.0)` it is fully green (south); when `vec2(0.5, 0.5)` it is a 50/50 red-green blend.
- The GDScript driver must:
  - Accept a Vector2 argument to `flash_from(direction: Vector2)`.
  - Set the `damage_direction` uniform.
  - Tween `flash` from 1.0 to 0.0 over 150 ms.
  - Cancel any in-flight flash before starting a new one (multi-hit safe).
- The driver must be testable: pressing the WASD keys triggers a flash from the corresponding direction.

### Grading rubric

- 20% — the shader compiles and renders without errors.
- 30% — the directional tint reads correctly: pressing D flashes red, A flashes blue, W flashes yellow, S flashes green.
- 20% — the driver cancels in-flight flashes.
- 20% — the duration and easing feel right (subjective; tune until a tester says "yeah that feels like getting hit from that direction").
- 10% — comments and code style match the week's conventions.

### Implementation hint

The cleanest way to blend four colours by a vec2 in [-1, 1]^2 is to map the vec2 into the four corners of a unit square, weight each corner by bilinear interpolation, and sum:

```glsl
vec3 directional_tint(vec2 dir) {
    // Map -1..1 -> 0..1 for bilinear weights.
    vec2 t = dir * 0.5 + 0.5;
    vec3 br = mix(directional_red, vec3(1.0, 1.0, 0.0), t.y);  // E, with NE pulling toward yellow
    vec3 bl = mix(directional_blue, vec3(0.0, 1.0, 0.0), t.y); // W, with SW pulling toward green
    return mix(bl, br, t.x);
}
```

That is the math. Wire it into your `fragment()` and the `flash` uniform.

---

## Problem 2 — Generated dissolve noise

> **Estimated time:** 60-90 minutes.
> **Files to submit:** `hw2-generate-noise.py`, `hw2-noise-output.png`.

Write a Python script (standard library only — no Pillow, no numpy) that generates a 256x256 grayscale "Perlin-ish" noise texture suitable for the dissolve shader from Exercise 3. The result must:

- Be saved as `hw2-noise-output.png` (an 8-bit RGBA PNG; convert your grayscale value to `(v, v, v, 255)`).
- Have visibly *clumped* low-frequency features rather than pure white noise. The dissolve produced by this texture should burn away in irregular blobs, not in a fine dither.
- Compile with `python3 -m py_compile hw2-generate-noise.py`.
- Include type hints on every helper function and every parameter.

### Recommended algorithm: value noise

A simple "value noise" with two octaves gives the right look:

1. Generate a coarse 16x16 grid of random values.
2. Bilinearly interpolate to 256x256.
3. Generate a finer 64x64 grid of random values, scaled to 25% amplitude.
4. Bilinearly interpolate to 256x256 and add.
5. Renormalise to 0..255.

This is two octaves of value noise. It is not true Perlin (which uses gradient noise) but is visually close for the dissolve use-case.

### PNG writing

You may copy the `make_png` helper from `SOLUTIONS.md` (the noise-generator there is white-noise; you need to upgrade to value noise).

### Grading rubric

- 25% — script compiles with `python3 -m py_compile`.
- 25% — type hints present on every helper function and parameter.
- 25% — the output PNG, when applied to the dissolve shader, produces visibly clumped dissolution (not fine-grained dither).
- 25% — the algorithm is value noise (or better) with at least two octaves. Pure white noise from `random.randint` does not pass.

### Implementation hint

The bilinear-interpolation helper is the core sub-routine:

```python
def bilinear(grid: list[list[float]], x: float, y: float) -> float:
    """Bilinearly sample `grid` at fractional coords (x, y).
    Assumes grid is a list of lists of floats with consistent width."""
    h: int = len(grid)
    w: int = len(grid[0])
    # Wrap around for tileable noise.
    x = x % w
    y = y % h
    x0: int = int(x)
    y0: int = int(y)
    x1: int = (x0 + 1) % w
    y1: int = (y0 + 1) % h
    fx: float = x - x0
    fy: float = y - y0
    a: float = grid[y0][x0] * (1.0 - fx) + grid[y0][x1] * fx
    b: float = grid[y1][x0] * (1.0 - fx) + grid[y1][x1] * fx
    return a * (1.0 - fy) + b * fy
```

Use this to upsample your coarse grids to 256x256.

---

## Problem 3 — Compound effect on a prior week's sprite

> **Estimated time:** 90 minutes.
> **Files to submit:** `hw3-compound.tscn` (the Godot scene file), `hw3-compound-screenshot.png`.

Take any sprite from any prior week's mini-project (Week 4 platformer's player, Week 7 puzzle game's tile, Week 9's cursor — your choice) and apply *all three* of the following to it simultaneously:

1. A hit-flash that fires every 2 seconds.
2. A subtle pulsing outline (e.g. `pulse_hz = 1.0`, light yellow).
3. A slow palette-swap cycle (e.g. tween `palette_row` 0->1->0 over 6 seconds).

The combined effect should read as "this is a special, alive, interactable object." It is the visual grammar for an objective marker, a glowing pickup, a magical entity.

### Requirements

- All three effects must be active simultaneously.
- The scene must run without errors (no shader compile errors, no GDScript exceptions).
- The screenshot must show the scene at a moment when all three effects are visibly active.
- The sprite must be recognisably *the same sprite* as in its source week (no swapping in a different sprite).

### Grading rubric

- 30% — all three effects compile and run without error.
- 30% — all three are visibly active in the screenshot.
- 20% — the combined effect is tuned: not so loud that it nauseates, not so subtle that an effect is invisible.
- 20% — the GDScript glue is clean: each effect's driver is in its own function or its own script, and effects can be enabled/disabled independently.

### Implementation hint

The simplest architecture is to chain the shaders as three separate `ShaderMaterial`s in a `MeshInstance2D`-style stack. Since Godot does not directly support stacking materials on a single Sprite2D, you instead use *three layers*:

```text
- ParentNode
  - Sprite2D (the actual sprite, with the palette-swap shader)
  - Sprite2D (a clone, same texture, with the outline shader, drawn behind)
  - Sprite2D (another clone, with the hit-flash shader, drawn on top)
```

This is the "z-stack" pattern for combining per-sprite shaders. The downside is three draws per visible sprite; the upside is that each effect remains debuggable.

A more advanced approach is to fold all three into one `.gdshader`. We do not require this; do it as a stretch goal if you finish early.

---

## Reflection (300-400 words)

> **File to submit:** `homework-reflection.md`.

Answer all three of:

**1. Which of the three problems was hardest, and why?** Be specific. "The shader was hard" is not an answer; "the bilinear interpolation in the noise generator had an off-by-one when I wrapped at the texture edge, and I lost 30 minutes to it" is.

**2. Pick one shader concept from this week (UV coordinates, uniforms, mix, smoothstep, discard, screen-space sampling, particles) and explain how you would teach it to a friend in three sentences.** The goal is to test that you can *transmit* the idea, not just use it.

**3. Take one of your three submissions and describe one production-grade improvement you would make if this were a real game.** A production-grade improvement is something a senior engineer would do: handle a platform difference (mobile vs desktop), add a fallback path, optimise a hot loop, document a non-obvious trick, add a setting in the options menu. "I would tune the colour" is not production-grade; "I would expose the flash colour as a per-character resource so the artist can adjust without touching code" is.

### Grading rubric

- 30% — answer to (1) is specific (cites a concrete bug or decision).
- 30% — answer to (2) is genuinely pedagogical and would help a beginner.
- 30% — answer to (3) demonstrates engineering judgement, not just artistic.
- 10% — the writing is clean (no typos, no vague filler).

---

## Submission

Bundle your homework folder as `week-10-homework/` with the following structure:

```text
week-10-homework/
  hw1-directional-flash.gdshader
  hw1-driver.gd
  hw2-generate-noise.py
  hw2-noise-output.png
  hw3-compound.tscn
  hw3-compound-screenshot.png
  homework-reflection.md
```

Submit by Sunday 23:59 (your local time). If you cannot submit on time, message the instructor *before* the deadline with a one-line reason; we extend cheerfully when the request is honest and the bug is interesting.

## A note on what to expect

The shader part of game programming is the area students tend to either *love* or *fear*. The fear comes from the unfamiliar mental model: parallel evaluation, no I/O, no print statements. The love comes from the speed of iteration: change one number, save, see the result. Both reactions are normal. By the end of this homework, the fear should be smaller.

If you find yourself stuck on a problem for more than 45 minutes, the right move is to write down what you were trying, what happened, and what you expected — then ask for help with that artefact. Shader bugs are almost never "I have no idea why this is broken;" they are almost always "I expected X and got Y," which is a question someone can answer in two minutes.
