# Challenge 1 — Port a Shadertoy Effect to Godot

> **Estimated time:** 90-120 minutes.
> **Difficulty:** medium.
> **Deliverable:** one ported `.gdshader` file, one screen-capture (or screenshot) showing it running in Godot, and a 200-word reflection on what changed in the port.

## The challenge

[Shadertoy](https://www.shadertoy.com/) is the largest free public library of small, self-contained shader programs in the world. Most are MIT-licensed; many are CC0; a few are author-owned with attribution required. Browse the [popular results page](https://www.shadertoy.com/results?query=&sort=popular) and pick one shader that meets all four of:

- Uses only the `mainImage` entry point (no extra buffers, no compute, no textures other than the built-in `iChannel` noise). About 70% of beginner Shadertoy shaders qualify.
- Is fewer than ~60 lines of code. The port grows when there are more lines.
- Renders something visually distinctive — a flame, a kaleidoscope, a moving pattern, a procedural cityscape — not a static gradient.
- Has a permissive licence (MIT, CC0, or the author's "feel free to use" comment). Default to assuming "all rights reserved" if no licence is stated; pick a different shader.

Port it to a Godot 4 `canvas_item` shader and apply it to either a full-screen TextureRect (for environment/scene effects) or a single Sprite2D (for character effects).

## The port mechanics

Shadertoy's signature is:

```glsl
void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 uv = fragCoord / iResolution.xy;
    // ... your effect ...
    fragColor = vec4(rgb, 1.0);
}
```

Godot's `canvas_item` signature is:

```glsl
void fragment() {
    // UV is already 0..1
    vec2 uv = UV;
    // ... your effect ...
    COLOR = vec4(rgb, 1.0);
}
```

### The five renamings

Apply these mechanically. They cover ~90% of typical ports:

| Shadertoy                       | Godot canvas_item                |
|---------------------------------|----------------------------------|
| `mainImage(out vec4 fragColor, in vec2 fragCoord)` | `fragment()`           |
| `iResolution.xy`                | `1.0 / SCREEN_PIXEL_SIZE`        |
| `iTime`                         | `TIME`                           |
| `iMouse.xy / iResolution.xy`    | `MOUSE_UV` (or pass as uniform)  |
| `fragColor = ...`               | `COLOR = ...`                    |
| `fragCoord.xy / iResolution.xy` | `UV` (for a sprite) or `SCREEN_UV` (for a full-screen quad) |

### The Y-axis flip

Shadertoy uses Y-up (origin at bottom-left). Godot canvas_item uses Y-down (origin at top-left). For most effects this is invisible (sines are symmetric); for any effect that uses UV.y asymmetrically, flip:

```glsl
uv.y = 1.0 - uv.y;
```

at the top of `fragment()`. Pick whichever orientation makes the effect look "right side up" relative to the world.

### The aspect-ratio fix

Shadertoy effects often assume a square viewport. On a 16:9 screen, circles drawn with `length(uv - 0.5)` come out as ellipses. The fix:

```glsl
vec2 aspect = vec2(1.0 / SCREEN_PIXEL_SIZE) / max(1.0/SCREEN_PIXEL_SIZE.x, 1.0/SCREEN_PIXEL_SIZE.y);
vec2 uv_aspected = (uv - 0.5) * aspect + 0.5;
```

Use `uv_aspected` for the math; use the unmodified `uv` for the texture sample.

### Texture samples

If the Shadertoy uses `iChannel0` as a generic noise input, replace with a uniform `sampler2D` in your Godot port and assign a noise PNG. Godot's `FastNoiseLite` resource generates one with two lines of script.

If the Shadertoy uses `iChannel0` as audio, drop that line — we are not piping audio into shaders this week. Replace with a uniform float and animate via tween.

## The deliverable

Submit three files in your Week 10 challenge folder:

1. **`challenge-01-port.gdshader`** — your ported shader. Include the original source URL in a leading comment and a note on what licence the original is under. Cite the Shadertoy author by username at minimum.
2. **`challenge-01-screenshot.png`** — a screen capture of your port running in Godot. The screen-capture must include enough context to confirm it is Godot (the editor's title bar, or a Godot-specific UI element). A 1280x720 capture is fine.
3. **`challenge-01-reflection.md`** — a 150-200 word reflection answering:
   - What did the port require beyond the mechanical renamings?
   - Where did the visuals diverge from the original, and why?
   - What did you learn about GLSL or Godot's shader dialect from doing this?

## Grading rubric

- 40% — the port compiles and renders without errors.
- 30% — the visual output matches the source (allowing for axis-flip and aspect differences).
- 20% — the reflection is thoughtful and specific. Generic "I learned a lot" answers score zero.
- 10% — the attribution is correct and the licence is verified.

## Suggested shaders to start from

If the popular page is overwhelming, these five are known to port cleanly:

- **[Plasma](https://www.shadertoy.com/view/XsVSDz)** — animated colour swirl, ~15 lines, MIT.
- **[Simple flame](https://www.shadertoy.com/view/MdX3zr)** — vertical fire, ~30 lines, requires a 1D noise channel.
- **[Kaleidoscope](https://www.shadertoy.com/view/wsSGRc)** — polar-symmetric pattern, ~25 lines.
- **[Glow](https://www.shadertoy.com/view/ldjGzV)** — soft circular glow you can attach to a sprite, ~10 lines.
- **[Voronoi pattern](https://www.shadertoy.com/view/Md2GDw)** — cellular pattern, ~40 lines, Inigo Quilez's reference implementation.

URLs may rot; if a link 404s, browse the popular page and pick something with similar characteristics.

## A note on attribution

Even when a shader is MIT or CC0, attribution is the cultural norm. Include in your `.gdshader` header:

```glsl
// Ported from:
//   "Title" by @username
//   https://www.shadertoy.com/view/XXXXXX
//   Original licence: MIT
// Port to Godot canvas_item: <your name>, week 10, C11-CRUNCH-ARCADE
```

That is enough. No formal bibliography is required at this level. Shader authors who notice their work in your project will appreciate the citation; the next student who reads your file will know where to look for the source.

## Stretch goals

If you finish the basic port quickly and want to push further:

1. **Add two uniforms to the shader** that did not exist in the Shadertoy original. For example: `pulse_hz` to animate an intensity; `tint_color` to tint the output. Wire them up in the inspector.
2. **Layer the ported effect on top of a Week-9 mini-project sprite**. The ported shader runs on a TextureRect overlay; the gameplay underneath is unchanged.
3. **Compare GPU usage**. Open the Godot editor's *Debugger > Monitors > Render* tab. Note the `frame_time_gpu` reading with and without your shader active. Most ports cost between 0.05 ms and 0.5 ms on integrated hardware.
4. **Write a "fastpath" version** that drops one expensive operation (a long loop, a complex `pow`) and visually compares to the original. The smallest shipped shader is often a 70%-fidelity version of the artist's original.

The point of the stretch goals is to internalise that shaders are *tunable*. Every uniform you add, every operation you replace, every loop bound you reduce is a knob the artist or the platform can turn. Production shaders ship with dozens of knobs; learning to add them is part of the craft.
