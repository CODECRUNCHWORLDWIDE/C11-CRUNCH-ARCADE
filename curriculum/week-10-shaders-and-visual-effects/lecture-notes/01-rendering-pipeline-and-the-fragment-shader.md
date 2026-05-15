# Lecture 1 — The Rendering Pipeline and the Fragment Shader

> **Duration:** ~2 hours of reading plus hands-on.
> **Outcome:** You can describe the four stages of the simplified rendering pipeline, state the input and output of the fragment shader in one sentence, write the minimal `canvas_item` shader from memory, and explain why a fragment shader cannot read its neighbour's colour.

If you only remember one thing from this lecture, remember this:

> **A fragment shader is a pure function the GPU runs in parallel, once per fragment, with no shared state. Every visual effect in 2D games is some choice of body for the function signature `(uv, time) -> color`. The whole job of the rest of the week is to choose interesting bodies.**

The lecture begins with a one-page tour of the GPU pipeline, narrows to the fragment shader (the only programmable stage we need this week), explains the GPU's data types and constraints, and ends with the minimal identity shader in Godot's `canvas_item` dialect. By the end you can read every line of Exercise 1.

We lean heavily on *The Book of Shaders* chapters 1-2 throughout. The book's "What is a shader?" page is the canonical answer to that question; the GPU pipeline diagram on the Khronos wiki is the canonical picture. Both are linked in `resources.md`.

---

## 1. What a GPU is, in one paragraph

A CPU is a small number of complex cores (4 to 16, typically) that can do almost anything: branch on arbitrary data, allocate memory, read from disk, sleep. A GPU is a large number of simple cores (hundreds to thousands) that can do one thing well: run the same short program in parallel, over a large array of inputs, with no inter-thread communication. The GPU is, fundamentally, a *parallel function-evaluator* with custom hardware for two things 3D games happen to need a lot: matrix multiplication and texture sampling.

When you draw a triangle, the GPU:

1. Runs the **vertex shader** once per vertex. Three runs for a triangle.
2. Hands the three transformed vertices to the **rasteriser** — a piece of fixed-function hardware that figures out which screen pixels the triangle covers.
3. Emits one **fragment** per covered pixel. A fragment is a candidate colour at a screen position; it is not yet a finished pixel.
4. Runs the **fragment shader** once per fragment. If the triangle covers 1000 pixels, the fragment shader runs 1000 times. In parallel. With no shared state between runs.
5. Writes each fragment's resulting colour into the framebuffer, after a fixed-function **blend** step that combines the fragment with whatever was already there.

That is the entire pipeline relevant to a 2D shader course. There are more stages in modern hardware (tessellation, geometry shaders, compute), but you can ship a polished 2D game knowing only those five steps.

---

## 2. The four stages we care about

The diagram below is the version we will draw on the board on Monday. It is the simplified version; we ignore tessellation, geometry shaders, and compute pipelines entirely.

```text
   +-------------+      +-------------+      +-------------+      +-------------+
   |   VERTEX    |      |             |      |  FRAGMENT   |      |             |
   |   SHADER    | ---> |  RASTERISE  | ---> |   SHADER    | ---> |    BLEND    |
   | (per-vertex)|      |    (fixed)  |      |(per-fragment)|     |   (fixed)   |
   +-------------+      +-------------+      +-------------+      +-------------+
        ^                                            ^                  ^
   per-vertex                                  per-fragment       framebuffer
   attributes:                                 built-ins:         operations:
   - POSITION                                  - UV               - source factor
   - UV                                        - COLOR (in)       - dest factor
   - COLOR                                     - TIME             - blend equation
   - NORMAL (3D)                               - SCREEN_UV
                                               - TEXTURE
```

### 2.1 Vertex processing

The vertex shader is a function whose job is *to put the vertex where it belongs on screen*. In 3D it does perspective projection, view transforms, skinning, lighting setup, and a dozen other tasks. In 2D, in Godot, the default vertex shader translates the sprite's local-space vertex by the node's `Transform2D` and outputs the result in clip space. For 95% of canvas-item shaders you do not write a `vertex()` function at all; the default is what you want.

The vertex shader's *outputs* are:
- A clip-space position (the canonical `vec4` the rasteriser needs).
- Any *varyings*: per-vertex values that get interpolated across the triangle and handed to the fragment shader. `UV` is the most important one; the rasteriser computes the UV at every fragment by barycentric interpolation of the triangle's three corner UVs.

You will write `vertex()` exactly twice in this week's exercises: once to displace a vertex with a wobble (a stretch challenge) and once to skip it entirely. Take the default.

### 2.2 Rasterisation

Once the three vertices of a triangle are in clip space, the GPU's rasteriser hardware figures out which screen pixels are inside the triangle. For each such pixel, it emits a *fragment*: a candidate sample at that pixel's screen position, with interpolated values for every varying (UV, colour, anything the vertex shader passed along).

Rasterisation is fixed-function. You do not write code for it. You cannot customise it. You can only observe its output as the per-fragment built-ins your fragment shader receives.

A *fragment* is not yet a pixel. Several fragments from several triangles can land on the same pixel; the depth-test and blend stages decide which one wins (or how they blend). For 2D games drawing sprites back-to-front, fragments simply blend in draw order.

### 2.3 Fragment processing

The fragment shader is the function you will write the most code in this week. Its signature, in Godot's `canvas_item` shader type, is conceptually:

```text
fragment(in UV, in TIME, in TEXTURE, in COLOR_in) -> COLOR_out
```

In actual code, that becomes:

```glsl
shader_type canvas_item;

void fragment() {
    // UV is in 0..1 across the sprite (or texture).
    // TIME is engine time in seconds.
    // TEXTURE is the sprite's albedo.
    // COLOR comes in as the modulate colour; you write the output back to it.
    COLOR = texture(TEXTURE, UV);
}
```

That is the identity shader. Open Godot, create a sprite, assign a `ShaderMaterial`, paste those lines into the shader editor — the sprite looks exactly the same as before. Every effect we write this week is a one-to-five-line modification of that template.

The fragment shader's job is *to choose the fragment's final colour*. It does not write to the framebuffer directly; the blend stage handles that. The fragment shader can also `discard` a fragment — declare that it should not be written at all — which we will use for the dissolve effect.

### 2.4 Blend

After the fragment shader picks a colour, the blend stage combines it with whatever colour is already in the framebuffer at that pixel. The classic alpha-blend equation is:

```text
final = src.rgb * src.a + dst.rgb * (1 - src.a)
```

In Godot, the blend mode is controlled by the `render_mode` declaration at the top of the shader: `blend_mix` (the default — standard alpha blending), `blend_add` (additive — useful for fire, glows, lasers), `blend_sub` (subtractive — useful for shadows), `blend_mul` (multiplicative — useful for tinted overlays).

The blend stage is fixed-function. You choose its mode; you do not write its code.

---

## 3. The data types

Shader languages are typed. Godot's shader language, like GLSL, has a small fixed type system that you should memorise this week.

| Type        | Description                                  | Example use                               |
|-------------|----------------------------------------------|--------------------------------------------|
| `float`     | 32-bit float.                                | `float t = TIME;`                          |
| `int`       | 32-bit integer.                              | `int i = 0;`                               |
| `bool`      | true / false.                                | `bool hit = false;`                        |
| `vec2`      | Two floats; xy or uv.                        | `vec2 uv = UV;`                            |
| `vec3`      | Three floats; rgb or xyz.                    | `vec3 tint = vec3(1.0, 0.5, 0.0);`         |
| `vec4`      | Four floats; rgba or xyzw.                   | `vec4 colour = vec4(1.0);`                 |
| `mat2`      | 2x2 matrix.                                  | `mat2 rotate2d(float a) { ... }`           |
| `mat4`      | 4x4 matrix.                                  | `mat4 model_to_clip;`                      |
| `sampler2D` | Texture handle.                              | `sampler2D albedo;`                        |

The vector types support *swizzling*: `colour.rgb` is the first three components, `colour.bgr` is the first three reversed, `UV.x` is the first component. Swizzling is one of the most common operations in any shader.

What the language does **not** have:

- **Pointers.** There is no `&` operator.
- **Objects.** No `class`, no method dispatch.
- **Recursion.** A function may not call itself (the compiler enforces it).
- **Dynamic memory.** No `new`, no `malloc`. Every variable is stack-allocated.
- **Strings.** A shader cannot print.
- **System calls.** No I/O, no networking, no file access.

The constraint is intentional. Every fragment runs in parallel on a different shader core; allowing recursion or dynamic allocation would require shared memory the architecture does not have. The constraints are what make the GPU fast.

---

## 4. Why a fragment cannot read its neighbour

This is the most common beginner question and worth a dedicated section.

A fragment shader executes once per fragment. Thousands of fragments execute in parallel. The order in which they execute is not defined; the GPU may schedule them in groups of 32 ("warps" on NVIDIA, "wavefronts" on AMD), and within a group they execute in lockstep, but across groups there is no ordering guarantee.

This means a fragment shader **cannot ask "what colour did the fragment one pixel to my left choose?"** — that fragment may not have executed yet, may be executing right now in a different group, may have finished but not yet committed its colour to the framebuffer.

What you *can* do is sample a *texture*. A texture is an immutable input the shader reads from. If you want a fragment to know about its neighbours, you arrange for the neighbour data to be in a texture the shader can sample. This is exactly how the outline effect works: it samples the sprite's own texture at four neighbour UVs.

A more advanced version of "I want to know about a neighbour" is **rendering to a texture in one pass and sampling it in the next pass**. The first pass writes the data; the second pass, running on the already-written texture, reads any pixel of it. This is the *multi-pass* or *render target* technique and the foundation of the post-process viewport quad pattern we cover in Lecture 3.

---

## 5. UV coordinates, the master tool

The single most important built-in for a 2D shader is `UV`. It is a `vec2` whose components run 0 to 1 across the sprite:

```text
                   UV.x = 0                          UV.x = 1
   UV.y = 0   +---------------------------------+
              |  (0, 0)                  (1, 0) |
              |                                 |
              |                                 |
              |             SPRITE              |
              |                                 |
              |                                 |
              |  (0, 1)                  (1, 1) |
   UV.y = 1   +---------------------------------+
```

(Godot uses Y-down for canvas-item UV, matching texture coordinate conventions in most game engines. Some textbooks use Y-up. Be alert for the difference when porting Shadertoy code.)

Every 2D effect you write this week starts with `UV`. The wave is `sin(UV.y * frequency + TIME)`. The dissolve is a threshold against a noise texture sampled at `UV`. The outline reads `texture(TEXTURE, UV + offset)` four times. The palette swap uses the sampled texture's red channel as a 1-D coordinate into a palette texture.

A useful exercise to do *outside* the GPU is to take the UV coordinate and apply transformations to it in Python or on paper:

- `UV - 0.5` centres the origin.
- `(UV - 0.5) * 2.0` rescales to -1..1.
- `length(UV - 0.5)` is the distance from the centre, 0 at centre, ~0.71 at corners.
- `atan(UV.y - 0.5, UV.x - 0.5)` is the polar angle of the fragment.

Exercise `uv-playground.py` is a Pygame visualiser of exactly these transformations, run on the CPU so you can put `print` statements anywhere. It is a deliberately non-GPU way to internalise the coordinate system.

---

## 6. The minimal `canvas_item` shader, line by line

```glsl
// Line 1: the shader type. Every Godot shader file starts here.
shader_type canvas_item;

// Line 2-3: an empty render_mode line is implicit.
// The default is `blend_mix, unshaded` for canvas items.

// Line 4-9: the fragment function. Every shader needs at least this.
void fragment() {
    // Sample the sprite's albedo texture at the fragment's UV.
    // `texture(sampler, uv)` is the GLSL built-in for sampling.
    // The return type is vec4 (rgba).
    COLOR = texture(TEXTURE, UV);
}
```

That is six meaningful lines. Save it as `identity.gdshader`, assign it to a sprite's `ShaderMaterial`, and the sprite renders unchanged. Now change line 6 to `COLOR = texture(TEXTURE, UV) * vec4(1.0, 0.5, 0.5, 1.0);` and the sprite renders with a pink tint. Change it to `COLOR = vec4(UV, 0.0, 1.0);` and the sprite becomes a red-green gradient revealing its UV layout. Change it to `COLOR = vec4(vec3(0.5 + 0.5 * sin(TIME)), 1.0);` and the sprite pulses between black and white at 1/(2pi) Hz.

You now have a working mental model. The rest is vocabulary.

---

## 7. Built-ins worth memorising

The `canvas_item` shader exposes a long list of built-ins. Memorise these eight; look the rest up in the docs.

| Built-in           | Type      | Read/Write | Meaning                                              |
|--------------------|-----------|------------|------------------------------------------------------|
| `UV`               | `vec2`    | read       | Fragment's texture coordinate, 0..1.                 |
| `COLOR`            | `vec4`    | read+write | In: the sprite's modulate. Out: the fragment's colour. |
| `TIME`             | `float`   | read       | Engine time in seconds since the shader was created. |
| `TEXTURE`          | `sampler2D` | read     | The node's albedo texture.                           |
| `SCREEN_UV`        | `vec2`    | read       | Fragment's screen position, 0..1 across the viewport. |
| `SCREEN_PIXEL_SIZE`| `vec2`    | read       | `(1.0/screen_w, 1.0/screen_h)`. Useful for screen-space sampling. |
| `TEXTURE_PIXEL_SIZE` | `vec2`  | read       | `(1.0/tex_w, 1.0/tex_h)`. Useful for neighbour sampling. |
| `MODULATE`         | `vec4`    | read       | The node's modulate colour, separate from `COLOR`.   |

There are more — `VERTEX`, `POINT_COORD`, `LIGHT_VERTEX`, `NORMAL`, `SPECULAR_SHININESS` — that you do not need this week.

---

## 8. Uniforms, the parameter knob

A *uniform* is a constant input to the shader, set from outside. Uniforms are how you make a shader parameterisable. They are how the GDScript driver tells the shader "the player was just hit, set flash to 1.0 and tween it down."

```glsl
shader_type canvas_item;

// A uniform you set from GDScript.
// hint_range(0.0, 1.0) gives the editor a slider.
uniform float flash : hint_range(0.0, 1.0) = 0.0;

void fragment() {
    vec4 base = texture(TEXTURE, UV);
    COLOR = vec4(mix(base.rgb, vec3(1.0), flash), base.a);
}
```

From GDScript:

```gdscript
$Sprite2D.material.set_shader_parameter("flash", 1.0)
```

The cost of changing a uniform per draw is small (it is a single GPU register update). The cost of *uploading a new texture* is large; treat texture uniforms as set-once.

Hints worth knowing:

- `: hint_range(min, max)` — slider in the editor.
- `: hint_range(min, max, step)` — quantised slider.
- `: hint_color` — colour picker (applies to `vec4` and `vec3`).
- `: hint_default_white` / `hint_default_black` / `hint_default_transparent` — fallback texture if you do not assign one.
- `: source_color` — declares an input colour is in sRGB; Godot does the gamma conversion for you. Use it on colour-picker uniforms.

The full list is in the Godot shading language reference, linked in `resources.md`.

---

## 9. A note on GPU debugging

Shaders are notoriously hard to debug. You cannot `print`. The compiler errors are precise but cryptic. The runtime errors are silent: a wrong colour, a black sprite, a flickering halo.

Two tricks that always work:

1. **Output your intermediate values as colour.** If you compute a `vec2` you think should be a certain UV, write `COLOR = vec4(your_uv, 0.0, 1.0);` and visually inspect the result. Red = x; green = y. This is the closest thing to `print` you have.
2. **Bisect.** If your shader is wrong, comment out half of it and replace the output with `vec4(1.0, 0.0, 1.0, 1.0)` (magenta). Move the comment-line up and down until you find the broken line.

The Godot editor's shader compiler is generally helpful. Errors look like:

```text
SHADER ERROR: 0:7 - assignment to uniform.
```

Line 7 of your shader is trying to write to a `uniform`. Uniforms are read-only inside the shader; the GDScript driver writes them via `set_shader_parameter`.

---

## 10. Closing summary

The fragment shader is a pure function. Its inputs are `UV`, `TIME`, the texture, and any uniforms you declare. Its output is `COLOR`. The GPU runs it in parallel, once per fragment, with no shared state. Every effect this week is a different body for that function.

Tomorrow we move to Godot specifics: how a `ShaderMaterial` differs from a `CanvasItemMaterial`, how to wire uniforms from GDScript, how the post-process viewport quad works. Wednesday and Thursday we walk the toolbox. By Friday you are stacking effects on a sprite and the math feels natural.

For homework this week, write the identity shader from memory. No notes, no docs. If you can write the seven-line file in five minutes, you have understood Lecture 1.

---

## References cited in this lecture

- *The Book of Shaders*, chapters 1 and 2: <https://thebookofshaders.com/01/> and <https://thebookofshaders.com/02/>
- Godot 4 docs, *Introduction to shaders*: <https://docs.godotengine.org/en/stable/tutorials/shaders/introduction_to_shaders.html>
- Godot 4 docs, *Canvas item shaders reference*: <https://docs.godotengine.org/en/stable/tutorials/shaders/shader_reference/canvas_item_shader.html>
- Khronos OpenGL wiki, *Rendering Pipeline Overview*: <https://www.khronos.org/opengl/wiki/Rendering_Pipeline_Overview>
- GLSL 4.60 specification, section 4.1 (basic types): <https://registry.khronos.org/OpenGL/specs/gl/GLSLangSpec.4.60.pdf>
