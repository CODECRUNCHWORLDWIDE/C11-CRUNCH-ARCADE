# Lecture 2 — The Godot 4 Shader System: ShaderMaterial, Uniforms, Canvas Item

> **Duration:** ~2 hours of reading plus hands-on.
> **Outcome:** You can distinguish `CanvasItemMaterial` from `ShaderMaterial`, declare a uniform with the correct hint, set a uniform from GDScript, and wire a tween that drives a hit-flash uniform from 1.0 down to 0.0 over 120 milliseconds.

If you only remember one thing from this lecture, remember this:

> **A shader is a text file. A material is a Godot resource that pairs a shader text file with a set of uniform values. A node references a material. Changing the uniform values changes the rendered output. The shader text never changes at runtime; the uniform values change every frame.**

The split between *shader* (the code) and *material* (the bag of parameters) is the load-bearing distinction this lecture teaches. Once it lands, every other Godot-shader feature falls out cleanly.

---

## 1. The two material types in Godot 4

When you click on a `Sprite2D` and open the *Material* property in the inspector, Godot offers two relevant options: `CanvasItemMaterial` and `ShaderMaterial`. (It also offers `ParticleProcessMaterial`, but that is for particles, which we cover in Lecture 3.)

### 1.1 `CanvasItemMaterial`

A `CanvasItemMaterial` is a *fixed-feature* material. It exposes a small set of properties through the inspector:

- **Blend mode**: `Mix`, `Add`, `Sub`, `Mul`, `Premultiplied Alpha`.
- **Light mode**: `Normal`, `Unshaded`, `Light Only`.
- **Particles anim**: parameters for sprite-sheet particle animation.

That is the entire surface area. No custom code; what you see in the inspector is what you get. The advantage is that it is fast to use, fast to compose, and impossible to write a bug into. The disadvantage is that it cannot do *any* effect this week's lectures cover — no tint by uniform, no dissolve, no wave, no outline.

Use `CanvasItemMaterial` when:
- You want additive blending on a sprite for a glow effect.
- You want to disable lighting (unshaded) so a sprite ignores 2D lights.
- You want one of the four built-in blend modes and nothing else.

### 1.2 `ShaderMaterial`

A `ShaderMaterial` is a *custom-program* material. It pairs:

- One **Shader** resource — a `.gdshader` text file you wrote.
- A set of **uniform values** — one entry per `uniform` declaration in the shader. The inspector auto-populates this list when you assign a shader.

The advantage is unlimited expressiveness. The disadvantage is that every shader is a tiny program you are responsible for; the compiler will reject syntactically invalid code; the GPU will silently render wrongness if your math is wrong.

Every exercise this week uses a `ShaderMaterial`. Use it when you need anything beyond the four canned `CanvasItemMaterial` options.

### 1.3 The decision tree

```text
Do you need fragment-shader behaviour beyond a blend mode?
        |
        +-- No --> Use CanvasItemMaterial. Pick the blend mode in the inspector.
        |
        +-- Yes --> Use ShaderMaterial. Write a .gdshader file.
                    |
                    +-- Is the effect a per-sprite tint, flash, or dissolve?
                    |       --> Attach the ShaderMaterial to the sprite directly.
                    |
                    +-- Is the effect a screen-wide post-process (CRT, vignette, wave)?
                            --> Render the game to a SubViewport. Attach the ShaderMaterial
                                to a full-screen TextureRect that samples the viewport.
```

---

## 2. The anatomy of a `.gdshader` file

Every shader file follows the same skeleton:

```glsl
shader_type canvas_item;
render_mode blend_mix;

// Uniforms — parameters you set from GDScript.
uniform float strength : hint_range(0.0, 1.0) = 0.0;
uniform vec4 tint_color : source_color = vec4(1.0);

// Optional helper functions.
float ramp(float x) {
    return smoothstep(0.0, 1.0, x);
}

// The fragment function. Required.
void fragment() {
    vec4 base = texture(TEXTURE, UV);
    COLOR = vec4(mix(base.rgb, tint_color.rgb, ramp(strength)), base.a);
}
```

Line by line:

- **`shader_type canvas_item;`** — declares what *kind* of shader this is. Valid values for Godot 4 are `canvas_item` (2D), `spatial` (3D), `particles` (process material), `sky`, and `fog`. We use only `canvas_item` this week.
- **`render_mode`** — comma-separated list of mode flags that change how the GPU configures the blend stage. `blend_mix` (default), `blend_add`, `blend_sub`, `blend_mul`, `blend_premul_alpha`, `unshaded`, `light_only`, `skip_vertex_transform`. Most exercises this week leave this at the default.
- **`uniform`** — declares an externally-controllable parameter. The `: hint_range(...)` and `: source_color` are *hints* that tell the editor how to display the uniform. The `= 0.0` is an optional default.
- **Helper function** — any pure function on shader types. Helpers cannot recurse but can call each other.
- **`void fragment()`** — the per-fragment function. You write to `COLOR` (and optionally call `discard`).

There may also be `void vertex()` (per-vertex, optional) and `void light()` (per-light, only relevant when using Godot's 2D lighting). We do not write either this week.

---

## 3. Uniform types and hints, exhaustively

The eight uniform types you will use:

| Type        | Example                                              | GDScript setter                                              |
|-------------|------------------------------------------------------|--------------------------------------------------------------|
| `float`     | `uniform float t = 0.0;`                             | `material.set_shader_parameter("t", 0.5)`                    |
| `int`       | `uniform int n = 0;`                                 | `material.set_shader_parameter("n", 4)`                      |
| `bool`      | `uniform bool enabled = false;`                      | `material.set_shader_parameter("enabled", true)`             |
| `vec2`      | `uniform vec2 offset = vec2(0.0);`                   | `material.set_shader_parameter("offset", Vector2(0.1, 0.0))` |
| `vec3`      | `uniform vec3 tint;`                                 | `material.set_shader_parameter("tint", Vector3(1, 0.5, 0))`  |
| `vec4`      | `uniform vec4 col : source_color = vec4(1.0);`       | `material.set_shader_parameter("col", Color(1, 1, 1, 1))`    |
| `sampler2D` | `uniform sampler2D noise_tex;`                       | `material.set_shader_parameter("noise_tex", noise_texture)`  |
| `mat4`      | `uniform mat4 transform;`                            | `material.set_shader_parameter("transform", t.to_mat4())`    |

Hints worth memorising:

- **`hint_range(min, max)`** — the editor shows a slider between the two values. Without it, a `float` shows as a text field. With it, the artist on your team can drag.
- **`hint_range(min, max, step)`** — quantised slider. Useful for integer-quantised UI where the type is still `float`.
- **`source_color`** (on `vec3` or `vec4`) — declares that the input is a colour in sRGB. Godot does the linearisation for you when reading. *Always* use this on colour uniforms; otherwise the shader operates on gamma-encoded values and the math is wrong.
- **`hint_default_white`** / **`hint_default_black`** / **`hint_default_transparent`** (on `sampler2D`) — fall back to a 1x1 texture of the named colour if the artist has not assigned one. Stops the editor from crashing when you preview an unfinished scene.
- **`hint_screen_texture`** (on `sampler2D`) — auto-binds the screen's rendered content to this sampler. Used in post-process shaders to read what the rest of the scene drew.
- **`filter_nearest`** / **`filter_linear`** / **`repeat_enable`** / **`repeat_disable`** — sampler hints that control how the GPU filters and wraps the texture.

A real-world example combining several:

```glsl
uniform sampler2D dissolve_noise : repeat_enable, filter_linear, hint_default_white;
uniform float threshold : hint_range(0.0, 1.0) = 0.0;
uniform vec4 edge_color : source_color = vec4(1.0, 0.6, 0.0, 1.0);
uniform float edge_width : hint_range(0.0, 0.2) = 0.05;
```

That is the full uniform block for the dissolve shader in Exercise 3. Four uniforms, each with a hint suited to its role. The editor renders the dissolve threshold as a slider; the colour as a colour picker; the texture as an asset slot with a sensible default.

---

## 4. Setting uniforms from GDScript

The contract is:

```gdscript
# Once, at setup. Store a reference to the material to avoid the get-property
# tax every frame.
@onready var material: ShaderMaterial = $Sprite2D.material as ShaderMaterial

# Every frame (or every event), update the uniform.
material.set_shader_parameter("flash", 0.7)
```

Three rules:

1. **Get the material once.** `node.material` returns the resource the node references; if multiple nodes share the same `ShaderMaterial` resource, changes to it affect all of them. To get a per-instance copy, *duplicate* the material first (`material = material.duplicate()`). The duplicate cost is small but non-zero; do it once at `_ready()`.
2. **Set parameters by string.** Godot does no compile-time check that "flash" is a real uniform name; misspell it and the call silently fails. A test in `_ready()` that pokes every uniform and verifies the shader compiled is a small defensive measure (Exercise 2 includes one).
3. **Set what changed.** Setting a uniform every frame to the same value is wasteful but cheap. Setting it every frame to a tweened value is correct.

---

## 5. The tween pattern for time-bounded effects

A hit-flash, a screen-shake, a dissolve transition — all three are *time-bounded* effects. They start, animate for a fixed window, and end. The idiomatic Godot 4 implementation uses the `Tween` object:

```gdscript
extends Sprite2D

const FLASH_MS: float = 120.0  # 0.12 seconds total duration

func on_hit() -> void:
    # Cancel any in-flight flash tween.
    var existing_tween: Tween = get_tree().get_meta("flash_tween") as Tween
    if existing_tween:
        existing_tween.kill()

    # Snap the uniform to 1.0 (fully white).
    material.set_shader_parameter("flash", 1.0)

    # Tween it back to 0.0 over FLASH_MS.
    var tween: Tween = create_tween()
    tween.tween_method(_set_flash, 1.0, 0.0, FLASH_MS / 1000.0)
    get_tree().set_meta("flash_tween", tween)

func _set_flash(value: float) -> void:
    material.set_shader_parameter("flash", value)
```

Three things to note:

- `create_tween()` returns a fresh `Tween` rooted in the scene tree. It runs each frame on its own schedule.
- `tween_method(callable, from, to, duration)` interpolates by calling `callable(value)` every frame.
- We store the tween in the scene tree's meta so we can cancel it if a second hit lands inside the window. Without the cancel, the second hit's tween fights the first one and the flash flickers.

The exercise file `exercise-02-hit-flash-driver.gd` builds this out with input handling, multi-sprite support, and a configurable duration.

---

## 6. The `canvas_item` built-in inputs, exhaustively

For reference, the full list of `canvas_item` fragment-shader built-ins in Godot 4.x:

| Built-in              | Type        | Direction | Description                                                |
|-----------------------|-------------|-----------|------------------------------------------------------------|
| `FRAGCOORD`           | `vec4`      | in        | Fragment's pixel coordinate. `FRAGCOORD.xy` is integer + 0.5. |
| `UV`                  | `vec2`      | in        | Texture coordinate, 0..1 across the sprite.                |
| `SCREEN_UV`           | `vec2`      | in        | Fragment's screen position, 0..1 across the viewport.       |
| `SCREEN_PIXEL_SIZE`   | `vec2`      | in        | `(1.0/width, 1.0/height)` of the viewport.                  |
| `TEXTURE_PIXEL_SIZE`  | `vec2`      | in        | `(1.0/width, 1.0/height)` of the sprite's albedo texture.   |
| `TEXTURE`             | `sampler2D` | in        | The sprite's albedo. Sample with `texture(TEXTURE, UV)`.    |
| `NORMAL_TEXTURE`      | `sampler2D` | in        | The sprite's normal map (optional).                         |
| `SPECULAR_SHININESS_TEXTURE` | `sampler2D` | in | The sprite's specular map (optional).                       |
| `SPECULAR_SHININESS`  | `vec4`      | in        | The sprite's specular colour and shininess.                 |
| `POINT_COORD`         | `vec2`      | in        | Coordinate within a `POINT` primitive (used by particles).  |
| `MODULATE`            | `vec4`      | in        | The node's modulate colour.                                 |
| `TIME`                | `float`     | in        | Engine time in seconds.                                     |
| `PI`                  | `float`     | constant  | `3.14159265358979323846`.                                   |
| `TAU`                 | `float`     | constant  | `6.28318530717958647692` (i.e. 2*PI).                       |
| `E`                   | `float`     | constant  | `2.71828182845904523536`.                                   |
| `COLOR`               | `vec4`      | in+out    | The fragment's final colour. Read it for the modulate, write it for the output. |
| `NORMAL`              | `vec3`      | in+out    | The fragment's surface normal (for 2D lighting).            |
| `NORMAL_MAP`          | `vec3`      | out       | The fragment's normal-map output.                           |
| `NORMAL_MAP_DEPTH`    | `float`     | out       | The depth-scale of the normal map.                          |
| `LIGHT_VERTEX`        | `vec3`      | out       | Offset applied for light position calculation.              |

You will write code that touches `UV`, `COLOR`, `TIME`, `TEXTURE`, `SCREEN_UV`, `SCREEN_PIXEL_SIZE`, and `TEXTURE_PIXEL_SIZE`. The rest you can look up in the canvas-item shader reference.

---

## 7. The `texture` and `textureLod` built-in functions

Sampling a texture is the most expensive operation in a typical fragment shader. Understand it.

```glsl
vec4 c = texture(TEXTURE, UV);
```

`texture` takes a `sampler2D` and a `vec2` UV. It returns a `vec4` rgba colour interpolated from the texture's texels using whatever filter the sampler is set up with (linear is the default; nearest if you set `filter_nearest`).

```glsl
vec4 c = textureLod(TEXTURE, UV, 0.0);
```

`textureLod` adds an explicit mipmap level (LOD = level-of-detail). Pass 0.0 to sample the base mip; pass higher numbers to sample lower-resolution mips. Useful when you know exactly what blur level you want.

```glsl
vec4 c = texture(TEXTURE, UV + vec2(TEXTURE_PIXEL_SIZE.x, 0.0));
```

Sample one texel to the right. The outline shader does this four times per fragment.

A sample costs roughly the same as 10-20 arithmetic operations on modern GPUs; do not sample inside a long loop unless the loop body is the texture sample.

---

## 8. The first real shader: hit-flash

We have built up enough vocabulary to write the first real shader. Hit-flash:

```glsl
shader_type canvas_item;

// Driven by GDScript via material.set_shader_parameter("flash", value).
// 0.0 = no flash, 1.0 = fully white.
uniform float flash : hint_range(0.0, 1.0) = 0.0;

// Optional override colour. Default white.
uniform vec3 flash_color : source_color = vec3(1.0, 1.0, 1.0);

void fragment() {
    // Sample the sprite's base albedo.
    vec4 base = texture(TEXTURE, UV);

    // Mix the rgb toward flash_color by the flash amount.
    // Alpha is preserved so transparent pixels stay transparent.
    COLOR.rgb = mix(base.rgb, flash_color, flash);
    COLOR.a = base.a;
}
```

Five real lines. The GDScript driver in Exercise 2 wires the `flash` uniform to a tween that fires when the player takes damage. The result: every time you get hit, the sprite flashes white for 120 milliseconds.

Run it. Tune the duration. Try `flash_color = vec3(1.0, 0.2, 0.2)` for a red flash, or `vec3(0.2, 1.0, 0.2)` for green, or `vec3(1.0, 1.0, 1.0)` for the canonical white.

This is the moment in the week the abstract becomes concrete. Every shader from here is a variation of the same five-line pattern.

---

## 9. A note on shared materials and `duplicate()`

The default behaviour in Godot is that two `Sprite2D` nodes sharing the same scene resource share *the same `ShaderMaterial`*. Setting a uniform on the material affects both sprites.

This is sometimes what you want (a screen-wide setting, a global tint) and sometimes not (per-enemy hit-flash). The fix:

```gdscript
func _ready() -> void:
    # Make this node's material independent from any other node's.
    if material is ShaderMaterial:
        material = material.duplicate() as ShaderMaterial
```

The duplicate is shallow but sufficient: the shader resource is still shared (so the program is compiled once), but the uniform values are now this instance's own.

A common bug is forgetting this duplicate. Symptom: every enemy in the scene flashes white when any one of them is hit. Cure: the four lines above in `_ready()`.

---

## 10. Closing summary

A `ShaderMaterial` is the marriage of a `.gdshader` text file and a bag of uniform values. The shader is the program; the material is the parameter set. The GDScript driver writes uniforms; the GPU runs the program; the fragment shader writes `COLOR`.

Tomorrow we move into the effects toolbox proper: dissolve, outline, wave, palette swap, LUT colour grading, and the post-process viewport quad. By the end of Lecture 3 you have seen every pattern in the mini-project.

For homework after this lecture, port the hit-flash shader to a green-flash version and a damage-direction version (where the flash colour leans toward red if the hit came from the right, blue if from the left). The math is one extra uniform and one extra `mix`.

---

## References cited in this lecture

- Godot 4 docs, *ShaderMaterial*: <https://docs.godotengine.org/en/stable/classes/class_shadermaterial.html>
- Godot 4 docs, *Shading language*: <https://docs.godotengine.org/en/stable/tutorials/shaders/shader_reference/shading_language.html>
- Godot 4 docs, *Canvas item shaders*: <https://docs.godotengine.org/en/stable/tutorials/shaders/shader_reference/canvas_item_shader.html>
- Godot 4 docs, *Tween*: <https://docs.godotengine.org/en/stable/classes/class_tween.html>
- *The Book of Shaders*, chapter 3 *Uniforms*: <https://thebookofshaders.com/03/>
- GLSL 4.60 specification, section 8.13 (texture lookup functions): <https://registry.khronos.org/OpenGL/specs/gl/GLSLangSpec.4.60.pdf>
