# Exercises — Solutions and Walk-Throughs

Every exercise this week ships with a working, commented file. The "solution" is therefore not a fresh implementation — it is a *walk-through* of the file in the order a student should read it, plus the answers to the "Things to try" prompts at the bottom of each exercise.

The intended reading order is the exercise number order (1 through 7, with the Python playground being a side-quest you can do any time). Each section below corresponds to one exercise file.

---

## Exercise 1 — Identity and tint (`exercise-01-identity-and-tint.gdshader`)

### Walk-through

Lines 50-58 are the *identity shader*: declare `shader_type canvas_item;` and write a single-line `fragment()` body that samples the texture and writes to `COLOR`. Run this first. The sprite should render exactly as it would with no material assigned. If it does not, your texture import settings have a colour-space mismatch (set the texture's *Compress > Mode* to *Lossless* and *Detect 3D* off).

Lines 60-72 add the tint uniform and a TIME-driven pulse. The `source_color` hint linearises the colour-picker input from sRGB. Multiply `base * tint` and you have a tinted sprite. Multiply `tinted.rgb *= pulse` and the colour pulses at `pulse_hz` Hz.

The `pulse_hz > 0.0 ? expr : 1.0` ternary is the GLSL ternary. It is equivalent to GDScript's `expr if cond else 1.0`. Branches inside a fragment shader are inexpensive on modern GPUs; the compiler often turns them into predicated execution rather than a real branch.

### Answers to "Things to try"

1. Replacing the fragment body with `COLOR = base;` gives identity. Verified.
2. `COLOR = vec4(UV, 0.0, 1.0);` produces the red-green gradient. UV.x in red, UV.y in green. This is the *single most useful debug visualisation in 2D shader work*; you will use it again.
3. The 0.5 + 0.5 * sin(TIME) trick maps sin's -1..+1 range into 0..1. The sprite pulses every TAU seconds (~6.28 seconds for one full cycle).
4. The stripes pattern is the canonical "scan-line" effect's basis. Frequency 10 gives 10 stripes; frequency 100 gives 100. We use a finer version in the mini-project's optional CRT pass.
5. The 4 Hz red pulse is the classic "low health" overlay. Stack it on the screen-wave for an "emergency state" feel.

---

## Exercise 2 — Hit-flash (`exercise-02-hit-flash.gdshader` + `exercise-02-hit-flash-driver.gd`)

### Walk-through — the shader

The shader is five lines of math. `mix(a, b, t)` is the GLSL built-in for linear interpolation; it returns `a * (1 - t) + b * t`. When `t == 0`, you get `a`; when `t == 1`, you get `b`. The hit-flash mixes the sprite's rgb toward `flash_color` by the `flash` uniform.

Alpha is preserved by a separate `mixed_alpha` calculation. The `flash_opacity_boost` knob is an optional feature: when set to 1.0, even transparent regions of the sprite light up during the flash. Useful for sprites with semi-transparent halos (a ghost, a flame); useless for opaque sprites.

### Walk-through — the driver

The driver demonstrates four patterns worth memorising:

1. **Material duplication in `_ready()`**. Without this, every sprite sharing the shader flashes when one is hit. With it, each sprite has its own uniform bag. The duplicate is shallow; the shader is still shared (and compiled once).
2. **Tween creation and cancellation**. `create_tween()` returns a fresh Tween rooted in the scene tree; `kill()` cancels an in-flight tween. The pattern of "kill the existing tween, start a new one" is universal in time-bounded effect code.
3. **`tween_method(callable, from, to, duration)`**. The tween calls `callable(value)` every frame with the interpolated value. The callable can be any method on the node. We use `_set_flash`, a private wrapper that writes the uniform.
4. **Defensive checks in `_ready()`**. Warn if the input action is missing; warn if the material is not a `ShaderMaterial`. These warnings save students an hour of "why doesn't it work" debugging on first run.

### Answers to "Things to try"

1. Red flash: `flash_color = vec3(1.0, 0.2, 0.2)`. The slight green-blue tint (0.2 each) avoids the over-saturated "pure red" look that reads as cheap.
2. Cold flash: `vec3(0.4, 0.8, 1.0)`. Reads as "took ice damage" or "frozen by an enemy spell."
3. The "double tap to flash green" Easter egg at the bottom of the driver shows the pattern: check timestamps, dispatch differently based on the gap. Useful for revealing developer-only features.

---

## Exercise 3 — Dissolve (`exercise-03-dissolve.gdshader`)

### Walk-through

The dissolve shader has two phases per fragment: the *discard test* and the *edge tint*. The discard test is the binary part: `if (noise < threshold) discard;`. The fragment contributes nothing to the framebuffer.

The edge tint is the soft part. Fragments that survive the discard but are *close to* the threshold (within `edge_width` of it) are tinted toward `edge_color`. This gives the "burning edge" appearance that turns a binary dissolve into a stylised effect. The math is `smoothstep(threshold, threshold + edge_width, noise)`, which returns 0 at `noise == threshold` (full edge tint) and 1 at `noise == threshold + edge_width` (no tint).

### Generating the noise texture

A noise texture is required input. The exercise expects a 256x256 grayscale PNG named `noise_256.png`. Here is a Python script that generates one with the standard library only:

```python
"""generate_noise.py

Generates a 256x256 grayscale noise PNG using only the standard library.
"""
import struct
import zlib
import random

WIDTH: int = 256
HEIGHT: int = 256


def _make_png(width: int, height: int, raw_rgba: bytes) -> bytes:
    """Build a minimal PNG from raw rgba bytes."""

    def chunk(tag: bytes, data: bytes) -> bytes:
        crc: int = zlib.crc32(tag + data)
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", crc)
        )

    sig: bytes = b"\x89PNG\r\n\x1a\n"
    ihdr: bytes = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    # Add a filter byte (0) at the start of each scanline.
    raw_with_filter = b""
    for y in range(height):
        raw_with_filter += b"\x00" + raw_rgba[y * width * 4:(y + 1) * width * 4]
    idat: bytes = zlib.compress(raw_with_filter, 9)
    return sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")


def main() -> int:
    random.seed(42)
    pixels: bytearray = bytearray()
    for _ in range(WIDTH * HEIGHT):
        v: int = random.randint(0, 255)
        pixels.extend([v, v, v, 255])  # rgba
    png: bytes = _make_png(WIDTH, HEIGHT, bytes(pixels))
    with open("noise_256.png", "wb") as f:
        f.write(png)
    print("wrote noise_256.png ({} bytes)".format(len(png)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

The generator uses `random.randint` for pure white noise. For more interesting patterns (Perlin, Worley), use Godot's built-in `FastNoiseLite` resource — set it to *Perlin* mode and call `get_image()` to bake to a texture.

### Answers to "Things to try"

1. `edge_width = 0`: hard binary cut. Looks pixelated, reads as "the wizard cast a quick-snap spell."
2. `edge_width = 0.2`, `edge_color = vec4(1.0, 0.2, 0.0, 1.0)`: thick orange band. Reads as actual fire.
3. `noise_scale = 8.0`: fine-grained dispersion. Looks like sand.
4. `noise_scale = 0.5` with low-frequency noise: chunky region-by-region dissolve. Looks like the sprite is being eaten by a slow corrosive blob.
5. Tween 0->1 over 800 ms: the canonical death-dissolve duration. Players read 600-1000 ms as "the moment of death"; anything faster reads as a glitch; anything slower reads as drama.
6. Tween 1->0: the materialisation. Pair with a sound cue and a colour flash for "the boss has arrived."

---

## Exercise 4 — Outline (`exercise-04-outline.gdshader`)

### Walk-through

The outline shader is a *neighbour-sampling* shader. Every fragment, after deciding it is itself transparent, asks: "are any of my four (or eight) neighbours opaque?" If yes, output the outline colour; if no, discard.

The trick is the step size: `TEXTURE_PIXEL_SIZE * outline_width`. `TEXTURE_PIXEL_SIZE` is `(1/texture_width, 1/texture_height)` in UV space — the size of one texel. Multiplying by `outline_width` (in texels) gives the UV offset for the desired thickness.

A subtle bug to watch for: if the sprite's texture is cropped tight to its visible content, the alpha-1 region is on the edge of the texture, and the alpha-0 neighbours sample outside the texture. With `repeat_disable`, out-of-bounds samples return transparent, which is what we want. With `repeat_enable`, they wrap around to the opposite edge, and the outline appears on the wrong side. *Always* use `repeat_disable` on sprite textures used with this shader.

### Answers to "Things to try"

1. `outline_width = 2.0`: two-texel outline. Visible at any zoom.
2. `eight_tap = true`, `outline_width = 1.5`: rounder corners. Doubles the sample count per fragment but is still cheap on any modern GPU.
3. Red pulsing outline: the classic "selected unit" affordance in RTS games. Use `pulse_hz = 2.0` for slow, `pulse_hz = 6.0` for "the unit is about to die."
4. Chaining: stack the outline shader after the hit-flash shader as two TextureRects in a post-process pipeline. The hit-flash makes the sprite go white; the outline gives it a coloured border. The combined feedback reads as "selected and just hit."

---

## Exercise 5 — Screen wave (`exercise-05-screen-wave.gdshader`)

### Walk-through

This is the first *post-process* shader. It samples `screen_texture` (auto-bound via `hint_screen_texture`) at a distorted `SCREEN_UV`. The distortion is `sin(UV.y * frequency + TIME * speed)` in the x axis, optionally with a `cos` companion in the y axis.

The clamping at the end (`uv = clamp(uv, vec2(0.0), vec2(1.0));`) prevents UV wrap-around when amplitude is high. Without it, edges sampling outside 0..1 either wrap (visible seam) or get black (depending on the sampler's wrap mode). Clamping pulls them to the edge texel, which is usually invisible.

### Scene setup recap (matches Lecture 3 section 2.1)

```text
- RootNode (Node2D or Control)
  - SubViewportContainer (stretch=true, anchor full rect)
    - SubViewport (size 1920x1080)
      - Camera2D
      - your-game-nodes ...
  - TextureRect (anchor full rect, material=ShaderMaterial pointing here)
```

The `SubViewportContainer` is critical: it sizes the SubViewport to its own rect. If you forget it, the SubViewport defaults to a 512x512 render target and looks pixelated when shown full-screen.

### Answers to "Things to try"

1. Amplitude 0 = identity. Useful baseline.
2. `wave_amplitude = 0.02, wave_frequency = 5.0`: underwater. Pair with a blue tint and you have a swimming level.
3. `wave_amplitude = 0.005, wave_frequency = 80.0, wave_speed = 12.0`: heat haze above hot metal. Subtle but visible.
4. Hit-shock: ramp amplitude to 0.03 in 50 ms, decay to 0 in 250 ms. Total perceived event is 300 ms.
5. `vertical_factor = 1.0, wave_frequency = 8.0`: 2D ripple. The screen sloshes. Use sparingly; nauseating in excess.
6. Stacking: the standard polish stack is wave -> colour grade -> vignette, in that order. The wave operates on the rendered scene; the grade operates on the warped scene; the vignette operates on the graded result.

---

## Exercise 6 — Palette swap (`exercise-06-palette-swap.gdshader`)

### Walk-through

The palette-swap shader is two texture samples per fragment: one for the source (we use only its red channel as the index) and one for the palette (looked up at `(source.r, palette_row)`). The result is the palette colour at that index, blended with the source by `swap_amount`.

The art workflow is the load-bearing part. To use this shader you need a source sprite whose pixels are coloured by *palette index*, not by final colour. In a typical 16-colour palette:

- region 0 (eyes whites): red value = 0/16 = 0.0
- region 1 (skin): red value = 1/16 = 0.0625
- region 2 (hair): red value = 2/16 = 0.125
- ...
- region 15 (outline): red value = 15/16 = 0.9375

In GIMP or Krita, paint each region with one of these exact values. The green and blue channels can be anything (the shader ignores them); convention is to set them to the red value too, so the source sprite renders as a recognisable grayscale.

### Generating palettes in Python

```python
"""generate_palettes.py

Generates a set of 16x1 palette PNGs using only the standard library.
"""
import struct
import zlib

WIDTH: int = 16
HEIGHT: int = 1


def make_png(rgba_pixels: list[tuple[int, int, int, int]]) -> bytes:
    """Build a 16x1 PNG."""

    def chunk(tag: bytes, data: bytes) -> bytes:
        crc: int = zlib.crc32(tag + data)
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", crc)

    raw: bytearray = bytearray()
    raw.append(0)  # filter byte for the single scanline
    for r, g, b, a in rgba_pixels:
        raw.extend([r, g, b, a])
    sig: bytes = b"\x89PNG\r\n\x1a\n"
    ihdr: bytes = struct.pack(">IIBBBBB", WIDTH, HEIGHT, 8, 6, 0, 0, 0)
    idat: bytes = zlib.compress(bytes(raw), 9)
    return sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")


# Default palette: a perceptual ramp from black to white.
DEFAULT: list[tuple[int, int, int, int]] = [
    (int(255 * i / 15), int(255 * i / 15), int(255 * i / 15), 255)
    for i in range(16)
]

# Fire palette: black -> deep red -> orange -> yellow -> white.
FIRE: list[tuple[int, int, int, int]] = [
    (0, 0, 0, 255),
    (32, 0, 0, 255),
    (64, 8, 0, 255),
    (96, 16, 0, 255),
    (128, 32, 0, 255),
    (160, 48, 0, 255),
    (192, 64, 0, 255),
    (224, 96, 0, 255),
    (255, 128, 0, 255),
    (255, 160, 32, 255),
    (255, 192, 64, 255),
    (255, 224, 96, 255),
    (255, 240, 128, 255),
    (255, 248, 160, 255),
    (255, 252, 200, 255),
    (255, 255, 240, 255),
]

# Ice palette: dark blue -> cyan -> white.
ICE: list[tuple[int, int, int, int]] = [
    (0, 0, 32, 255),
    (0, 0, 64, 255),
    (0, 16, 96, 255),
    (0, 32, 128, 255),
    (0, 48, 160, 255),
    (16, 64, 192, 255),
    (32, 96, 224, 255),
    (48, 128, 240, 255),
    (64, 160, 248, 255),
    (96, 192, 252, 255),
    (128, 216, 252, 255),
    (160, 232, 252, 255),
    (192, 240, 252, 255),
    (224, 248, 252, 255),
    (240, 252, 254, 255),
    (255, 255, 255, 255),
]


def main() -> int:
    for name, palette in [("default", DEFAULT), ("fire", FIRE), ("ice", ICE)]:
        png_bytes = make_png(palette)
        filename: str = "palette_{}.png".format(name)
        with open(filename, "wb") as f:
            f.write(png_bytes)
        print("wrote {} ({} bytes)".format(filename, len(png_bytes)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Three palettes. ~3 KB total. Drop them in your Godot project; assign to the `palette` uniform; swap at runtime.

### Answers to "Things to try"

1. Three palettes, key-press swap: build a simple `_input` handler in a script attached to the sprite. On key 1, set palette to default; on key 2, fire; on key 3, ice. The character changes outfit.
2. 16x4 palette, animated row: tween `palette_row` from 0 to 1 over 1 second. The character cycles through four outfits — a "level-up flash."
3. `swap_amount = 0.5`: 50/50 blend. Useful as a transition frame between two palettes.
4. Combined with hit-flash: palette defines the base; hit-flash overrides briefly. The visual reads as "the character is normal, then a flash, then normal again with the same palette."
5. Wider palette: 32 colours. Authoring is harder (more discrete red values to remember); colour fidelity is better.

---

## Exercise 7 — Particles (`exercise-07-particles.gd`)

### Walk-through

The script configures a `GPUParticles2D` and its `ParticleProcessMaterial` entirely from code. In production you would typically build the process material once in the inspector, save it as a `.tres` resource, and reference it; doing it in code is verbose but makes the configuration legible in one place.

Key configuration:

- `amount = 32` — the maximum live particles. With `one_shot = true` and `explosiveness = 1.0`, all 32 emit at t=0 of the cycle.
- `lifetime = 0.4` — each particle lives 400 ms.
- `emission_shape = EMISSION_SHAPE_SPHERE`, `emission_sphere_radius = 4.0` — particles emit from anywhere in a small sphere.
- `spread = 180.0`, `flatness = 1.0` — full circle in the xy plane. `flatness` constrains the 3D-direction sphere to the 2D plane.
- `gravity = Vector3(0, 400, 0)` — pulls particles downward. *Vector3 even in 2D*; the z-component is ignored.
- `damping_min/max = 80..200` — linear damping slows particles toward a stop. Cinematic.

The colour gradient defines the per-particle colour over its normalised life (0=birth, 1=death). The four stops are bright yellow at birth, orange in the middle, dark partially-transparent red near the end, and fully transparent at the end. The result is a candle-flame-like trail.

### Answers to "Things to try"

1. `BURST_COUNT = 8`: popcorn (too few). 200: fog (too many). 32 is the sweet spot for "a hit happened."
2. `LIFETIME_S = 0.15`: snappy. 1.2: dreamy / magical. Lifetime is the duration the player perceives the feedback for.
3. Fire variant: gradient orange -> black. Magic variant: cyan -> white. Both are one-line edits in `_make_colour_gradient()`.
4. Zero gravity: particles drift forever along initial direction. Reads as "space" or "underwater."
5. Three-layer composite: yellow sparks + grey smoke + a single big white-flash particle. Each layer is its own `GPUParticles2D`; trigger all three together. The composite reads as a much bigger event than any one layer.
6. Triggering from gameplay: replace the `_input` handler with a signal-handler that fires on `damaged` or `hit`. The particles are the visible reward for gameplay events, not a manual toggle.

---

## UV playground (`uv-playground.py`)

### Walk-through

The Python script is a CPU-side renderer of fragment-shader-style functions. Each effect is a one-line body that takes a UV tuple and returns an rgb tuple. The renderer loops over every pixel of a 256x256 grid, calls the effect function, and writes the result.

The six built-in effects map directly to GLSL one-liners:

| Python                                        | GLSL equivalent                                |
|-----------------------------------------------|------------------------------------------------|
| `(u, v, 0.0)`                                 | `COLOR = vec4(UV, 0.0, 1.0);`                  |
| `((u-0.5)*0.5+0.5, (v-0.5)*0.5+0.5, 0.0)`    | `COLOR = vec4((UV-0.5)*0.5+0.5, 0.0, 1.0);`   |
| `sqrt(du*du+dv*dv)*sqrt(2)`                   | `COLOR = vec4(vec3(length(UV-0.5)*sqrt(2.0)), 1.0);` |
| `0.5 + 0.5 * cos(angle + ...)`                | `cos(atan(UV.y-0.5, UV.x-0.5) + ...)`          |
| `0.5 + 0.5 * sin(v*freq*TAU + t*speed)`      | `sin(UV.y*freq + TIME*speed)`                  |
| `1.0 if frac(u*freq) < 0.5 else 0.0`          | `step(0.5, fract(UV.x*freq))`                  |

After running the playground a few times, the GLSL forms feel less alien. That is the entire point of the exercise.

### Answers to "Things to try"

1. A seventh effect: try `(0.5 + 0.5*sin(u*10.0 + t), 0.5 + 0.5*sin(v*10.0 + t*1.3), 0.5)`. Mesmerising 2D wave grid.
2. Change `WINDOW_SIZE` to 128 (faster) or 512 (slower; runs at 1 fps). 256 is the speed compromise.
3. Profile: wrap the inner loop in `time.perf_counter()` calls and report the per-frame fragment count. On a 2018 laptop, ~50,000 fragments per second is typical. A GPU does 100 *million* per second. The factor-of-2000 speed gap is why we write shaders on the GPU.
