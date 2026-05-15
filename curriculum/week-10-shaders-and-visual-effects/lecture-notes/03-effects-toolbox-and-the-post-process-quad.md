# Lecture 3 — The Effects Toolbox and the Post-Process Quad

> **Duration:** ~2 hours of reading plus hands-on.
> **Outcome:** You can write six 2D effects from memory, set up a `SubViewport` post-process pipeline, configure a `GPUParticles2D` with a `ParticleProcessMaterial`, and stack three effects on a single scene without them interfering with each other.

If you only remember one thing from this lecture, remember this:

> **The polish tripod is screen-shake, hit-flash, and freeze-frame. Add those three to any game and players will tell you it "feels better" without being able to say why. None of them is a shader; only the hit-flash needs one. But the visual *grammar* the tripod establishes — feedback that is loud, brief, and aligned to gameplay events — is the same grammar that makes the dissolve, the wave, and the outline feel earned.**

The lecture begins with the polish tripod, opens into the post-process viewport quad pattern that hosts most of our screen-space effects, walks through the dissolve, outline, wave, palette swap, and LUT colour grade, and ends with `GPUParticles2D` plus `ParticleProcessMaterial`. We close with a discussion of when to stack effects and when to fold them into a single shader.

We lean heavily on *The Book of Shaders* chapters 5-7 and Inigo Quilez's distance-function articles in this lecture. Both are linked in `resources.md`.

---

## 1. The polish tripod: screen-shake, hit-flash, freeze-frame

Three techniques, applied together, transform a flat-feeling game into one that punches.

### 1.1 Screen-shake

A *screen-shake* is camera-translation by a random offset that decays to zero. It is the cheapest piece of polish in all of game development. The implementation is six lines in GDScript:

```gdscript
extends Camera2D

var shake_strength: float = 0.0
const SHAKE_DECAY: float = 5.0  # Strength multiplier per second.

func add_shake(amount: float) -> void:
    shake_strength = max(shake_strength, amount)

func _process(delta: float) -> void:
    shake_strength = max(0.0, shake_strength - SHAKE_DECAY * delta)
    offset = Vector2(randf_range(-1, 1), randf_range(-1, 1)) * shake_strength
```

Call `add_shake(8.0)` when something explodes. The camera jiggles for ~1.6 seconds and decays smoothly to zero. That is the entire feature.

Three details worth knowing:

- Use `max(shake_strength, amount)` not `shake_strength += amount`. Otherwise stacked shakes spiral into nausea.
- Decay should be roughly *linear* in time, not exponential. Exponential decay feels too soft.
- For diegetic shakes (an earthquake the player walks into) use a sinusoidal pattern (`shake_strength * sin(TIME * 30.0)`) instead of pure noise. The pattern reads as continuous; the random noise reads as event-driven.

The mini-project's `screen_shake.gd` is the full implementation, with separate strength budgets for explosions, hits, and the dissolve transition.

### 1.2 Hit-flash

Covered in Lecture 2. Drives a `ShaderMaterial`'s `flash` uniform via a tween from 1.0 to 0.0 over 120 milliseconds. The shader mixes the sprite's albedo toward white by the flash amount. Total cost: one uniform, two shader lines, one tween.

### 1.3 Freeze-frame

A *freeze-frame* (or *hit-stop*) is a deliberate pause of game time at the moment a hit lands. The player's swing animation freezes mid-motion for 50-100 milliseconds, the world stops moving, then everything resumes. The pause makes the hit *feel weighty*; the eye reads the freeze as the moment of impact.

```gdscript
func hit_stop(duration_ms: float) -> void:
    Engine.time_scale = 0.05  # Effectively paused; small non-zero value preserves animation continuity.
    await get_tree().create_timer(duration_ms / 1000.0).timeout
    Engine.time_scale = 1.0
```

Use 60-100 ms for medium hits; 30 ms for small hits; 150 ms for boss attacks landing on the player. Calibrate per game. Vlambeer's *Nuclear Throne* used hit-stop pervasively; Smash Bros. uses it on every hit; *Hollow Knight* uses it sparingly to emphasise boss damage.

The three together: when the player takes damage, you call `add_shake(6.0)`, you set the sprite's `flash` uniform to 1.0 with a 120 ms tween, and you call `hit_stop(80.0)`. Three lines of code, ten seconds of typing, an order of magnitude of perceived game-feel.

---

## 2. The post-process viewport quad pattern

The polish tripod handles per-sprite and per-frame feedback. For *screen-wide* effects — colour grading, CRT, vignette, screen waves, chromatic aberration — we need a different architecture. The pattern, ubiquitous since the PS3 era, is the *post-process viewport quad*.

### 2.1 The architecture

```text
                            +---------------------+
                            |     SubViewport     |
                            |  (renders the game) |
                            +---------+-----------+
                                      |
                                      | viewport_texture
                                      v
                            +---------+-----------+
                            |    TextureRect      |
                            |  (full-screen quad) |
                            |                     |
                            |   ShaderMaterial    |
                            |   (post-process)    |
                            +---------+-----------+
                                      |
                                      | rendered output
                                      v
                                +-----+------+
                                |   SCREEN   |
                                +------------+
```

You construct it once in the scene tree:

```text
- RootNode
  - SubViewportContainer (stretch=true)
    - SubViewport (size=1920x1080)
      - [your game's root node — Camera2D, Player, Enemies, UI]
  - TextureRect (anchor full rect, material=ShaderMaterial)
```

The `SubViewport` renders the game off-screen to its own texture. The `TextureRect`'s shader samples that texture and outputs the post-processed result. Anything drawn into the `SubViewport` becomes the input to the post-process shader.

### 2.2 The post-process shader skeleton

```glsl
shader_type canvas_item;

uniform sampler2D screen_texture : hint_screen_texture, filter_linear, repeat_disable;

void fragment() {
    // SCREEN_UV is the fragment's screen position, 0..1 across the viewport.
    vec4 c = texture(screen_texture, SCREEN_UV);

    // ... apply your effect here, modifying c ...

    COLOR = c;
}
```

The `hint_screen_texture` hint is Godot 4's way of saying "auto-bind the current viewport's texture to this sampler." Older Godot versions used a different mechanism; for Godot 4.2+ this is the right way.

### 2.3 The screen wave

The classic underwater / heat-haze effect:

```glsl
shader_type canvas_item;

uniform sampler2D screen_texture : hint_screen_texture, filter_linear, repeat_disable;
uniform float wave_frequency : hint_range(1.0, 100.0) = 30.0;
uniform float wave_speed : hint_range(0.0, 20.0) = 5.0;
uniform float wave_amplitude : hint_range(0.0, 0.05) = 0.005;

void fragment() {
    // Distort the sample UV by a sine wave in screen-y, animated in TIME.
    // The result reads as horizontal shimmer.
    vec2 distorted_uv = SCREEN_UV;
    distorted_uv.x += sin(SCREEN_UV.y * wave_frequency + TIME * wave_speed) * wave_amplitude;

    COLOR = texture(screen_texture, distorted_uv);
}
```

Three uniforms tune the effect. The math is one line. The result is the underwater feel from every game with an underwater level since 2003.

### 2.4 The vignette

A subtle darkening at the corners makes the centre of the screen feel "warmer":

```glsl
shader_type canvas_item;

uniform sampler2D screen_texture : hint_screen_texture, filter_linear, repeat_disable;
uniform float vignette_strength : hint_range(0.0, 1.0) = 0.5;
uniform float vignette_softness : hint_range(0.0, 1.0) = 0.5;

void fragment() {
    vec4 c = texture(screen_texture, SCREEN_UV);

    // Distance from the centre of the screen, 0 at centre, ~0.71 at corners.
    float d = distance(SCREEN_UV, vec2(0.5));

    // Smoothstep gives a soft falloff. The two parameters tune where it starts and ends.
    float v = 1.0 - smoothstep(vignette_softness * 0.5, 0.71, d) * vignette_strength;

    COLOR = vec4(c.rgb * v, c.a);
}
```

`smoothstep(edge0, edge1, x)` returns 0 below `edge0`, 1 above `edge1`, and a Hermite-interpolated value in between. It is the most useful built-in for soft falloffs.

---

## 3. The dissolve effect

A dissolve is a transition that makes a sprite (or the whole screen) "burn away" in a randomised pattern. The implementation is one noise texture and one threshold uniform:

```glsl
shader_type canvas_item;

uniform sampler2D dissolve_noise : repeat_enable, filter_linear, hint_default_white;
uniform float threshold : hint_range(0.0, 1.0) = 0.0;
uniform vec4 edge_color : source_color = vec4(1.0, 0.6, 0.0, 1.0);
uniform float edge_width : hint_range(0.0, 0.2) = 0.05;

void fragment() {
    vec4 base = texture(TEXTURE, UV);
    float noise = texture(dissolve_noise, UV).r;

    // Discard fragments where noise is below the threshold.
    // The threshold sweeps from 0 to 1 to make the sprite vanish.
    if (noise < threshold) {
        discard;
    }

    // Within edge_width of the threshold, tint toward edge_color.
    // This is the "burning edge" effect that sells the dissolve.
    float edge = smoothstep(threshold, threshold + edge_width, noise);
    COLOR = mix(vec4(edge_color.rgb, base.a), base, edge);
}
```

The driver in GDScript is a tween:

```gdscript
var tween: Tween = create_tween()
tween.tween_method(
    func(v: float) -> void:
        material.set_shader_parameter("threshold", v),
    0.0, 1.0, 1.0  # 0 to 1 over 1 second
)
```

The noise texture is generated once in Python (see Exercise 3's SOLUTIONS walk-through) and imported as a 256x256 grayscale PNG. The same texture works for a thousand sprites.

A *reverse* dissolve — appearing rather than vanishing — runs the tween from 1.0 to 0.0. Use it for "the boss materialises" feedback.

---

## 4. The outline

A one-pixel outline detects the alpha boundary by sampling four neighbours:

```glsl
shader_type canvas_item;

uniform vec4 outline_color : source_color = vec4(1.0, 1.0, 1.0, 1.0);
uniform float outline_width : hint_range(0.0, 4.0) = 1.0;

void fragment() {
    vec4 base = texture(TEXTURE, UV);

    // If this fragment is already opaque, just draw the sprite normally.
    if (base.a > 0.5) {
        COLOR = base;
        return;
    }

    // Otherwise, check the four cardinal neighbours.
    // If any has alpha > 0, we are on the outline boundary.
    vec2 step = TEXTURE_PIXEL_SIZE * outline_width;
    float a_right = texture(TEXTURE, UV + vec2(step.x, 0.0)).a;
    float a_left  = texture(TEXTURE, UV - vec2(step.x, 0.0)).a;
    float a_down  = texture(TEXTURE, UV + vec2(0.0, step.y)).a;
    float a_up    = texture(TEXTURE, UV - vec2(0.0, step.y)).a;

    float neighbour_alpha = max(max(a_right, a_left), max(a_down, a_up));

    if (neighbour_alpha > 0.5) {
        COLOR = outline_color;
    } else {
        discard;
    }
}
```

Five samples per fragment. Cheap. Works on any sprite with an alpha channel. For thicker outlines, increase `outline_width`; for diagonal coverage too, add four more samples at the corners.

A note on sprite atlases: this technique only works if the sprite has *transparent border pixels* in its texture. If the sprite is cropped tight to its visible content, the neighbours of the edge fragments sample outside the texture and the wrap mode determines behaviour. Set `repeat_disable` on the texture to ensure the wrap returns transparent.

---

## 5. The palette swap

A palette swap uses each fragment's red channel as a 1-D coordinate into a small palette texture. Same character, ten outfits, one shader:

```glsl
shader_type canvas_item;

// A small (e.g. 16x1) palette texture. Each x position is one palette colour.
uniform sampler2D palette : filter_nearest, repeat_disable, hint_default_white;

void fragment() {
    // Sample the sprite's albedo. We use only the red channel.
    vec4 base = texture(TEXTURE, UV);

    // Use base.r as a horizontal coordinate into the palette.
    // The y coordinate is fixed at 0.5 (the middle of the single palette row).
    vec3 swapped = texture(palette, vec2(base.r, 0.5)).rgb;

    // Preserve the original alpha.
    COLOR = vec4(swapped, base.a);
}
```

The source sprite is drawn in *indexed* style: each visible region is filled with a uniform red value that indexes the palette. Region 1 might be `r=0.0` (eyes), region 2 might be `r=0.1` (skin), region 3 might be `r=0.2` (shirt), etc. Swapping the palette texture re-colours the sprite without retouching it.

This is the technique behind every fighting-game character's alt costumes, Mega Man's weapon-tinted sprite, and Pokémon's shiny variants. Cost: one extra texture sample per fragment.

---

## 6. The LUT colour grade

A colour LUT (look-up table) maps every input rgb colour to a graded output rgb colour. The lookup is a 3D function: `(r, g, b) -> (r', g', b')`. The storage is a *2D* texture laid out as a strip of 2D slices through the 3D cube — the canonical layout is 16x16x16 packed into a 256x16 texture.

```glsl
shader_type canvas_item;

uniform sampler2D screen_texture : hint_screen_texture, filter_linear, repeat_disable;
uniform sampler2D lut : filter_linear, repeat_disable, hint_default_white;
uniform float lut_size : hint_range(2.0, 64.0) = 16.0;

vec3 sample_lut(vec3 color, sampler2D lut_tex, float size) {
    // Quantise the blue channel into a slice index.
    float blue_idx = color.b * (size - 1.0);
    float slice_a = floor(blue_idx);
    float slice_b = ceil(blue_idx);
    float frac = blue_idx - slice_a;

    // Sample the two adjacent blue-slices and interpolate.
    vec2 uv_a = vec2((slice_a + color.r) / size, color.g);
    vec2 uv_b = vec2((slice_b + color.r) / size, color.g);
    vec3 a = texture(lut_tex, uv_a).rgb;
    vec3 b = texture(lut_tex, uv_b).rgb;
    return mix(a, b, frac);
}

void fragment() {
    vec3 c = texture(screen_texture, SCREEN_UV).rgb;
    COLOR = vec4(sample_lut(c, lut, lut_size), 1.0);
}
```

The math is the slice-and-interpolate trick that turns a 256x16 2D texture into a working 16x16x16 3D LUT. Cost: two texture samples per fragment.

Generating a LUT is its own art. Challenge 2 walks you through making one in Python: start with the identity LUT, apply per-channel curves, then save as a PNG. The output is a 256x16 strip; load it in Godot, assign it to the `lut` uniform, and the entire screen is graded.

---

## 7. GPUParticles2D and ParticleProcessMaterial

Particles are the third leg of visual juice. A modest fountain of 200 sparks at the moment of impact reads as "lots of stuff happening" even when nothing else changed. Godot offers two flavours:

- **`GPUParticles2D`** — simulated on the GPU. Fast even with thousands of particles. The default and almost always the right choice.
- **`CPUParticles2D`** — simulated on the CPU. Slower but works in HTML5 export and on hardware without compute shaders. Use only when the platform forces it.

A `GPUParticles2D` node has these key properties:

- **`amount`** — maximum live particles at any time. 100-500 is typical for hit feedback; 2000+ is a fog or rain system.
- **`lifetime`** — seconds each particle lives.
- **`one_shot`** — emit once and stop, or emit continuously.
- **`emitting`** — toggle to start/stop emission.
- **`process_material`** — a `ParticleProcessMaterial` that defines initial velocity, gravity, scale-over-life, colour-over-life, and emission shape.
- **`texture`** — the sprite each particle is drawn as.

A `ParticleProcessMaterial` exposes (from the inspector):

- **Emission shape**: `Point`, `Sphere`, `Box`, `Points`, `Directed Points`.
- **Initial velocity** + variation.
- **Gravity** as a `Vector2`.
- **Damping** to slow particles over time.
- **Scale over life** as a curve.
- **Color over life** as a gradient (the `GradientTexture1D` resource).
- **Animation** if the texture is a sprite sheet.

Exercise 7 configures a hit-spark system from code:

```gdscript
var sparks: GPUParticles2D = $GPUParticles2D
sparks.amount = 32
sparks.lifetime = 0.4
sparks.one_shot = true
sparks.emitting = true

var mat: ParticleProcessMaterial = sparks.process_material as ParticleProcessMaterial
mat.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_SPHERE
mat.emission_sphere_radius = 4.0
mat.initial_velocity_min = 80.0
mat.initial_velocity_max = 200.0
mat.gravity = Vector3(0.0, 400.0, 0.0)  # Yes, Vector3 even in 2D.
mat.scale_min = 0.5
mat.scale_max = 1.5
```

A note on the gravity field: even in `GPUParticles2D`, the gravity field is a `Vector3`. The z-component is ignored for 2D, but you must provide it. The trap catches every student once.

For a custom process shader (rather than the `ParticleProcessMaterial` template), use `shader_type particles;` in a `.gdshader` file. We do not cover custom particle shaders this week — the canned `ParticleProcessMaterial` handles 90% of indie-game needs.

---

## 8. Stacking effects vs folding them

Two ways to apply multiple effects.

**Stacking**: each effect is its own `TextureRect` and `ShaderMaterial`. The first reads from the SubViewport; the second reads from the first's output; and so on. Each pass is its own complete texture-sample-and-resample cycle.

```text
SubViewport
   |
   v
TextureRect #1 (colour grade) ---> rendered to its own viewport
   |
   v
TextureRect #2 (screen wave)  ---> rendered to its own viewport
   |
   v
TextureRect #3 (vignette)
   |
   v
SCREEN
```

Stacking is debuggable: you can disable any pass independently. The cost is N full-screen texture-sample passes for N effects.

**Folding**: a single shader that does all the effects inline. One pass, one set of texture samples, but you cannot disable any of them without re-editing the shader.

```glsl
void fragment() {
    // Colour-graded, wave-distorted, vignetted, all in one.
    vec2 wave_uv = SCREEN_UV + vec2(sin(SCREEN_UV.y * 30.0 + TIME * 5.0) * 0.005, 0.0);
    vec3 c = texture(screen_texture, wave_uv).rgb;
    c = sample_lut(c, lut, 16.0);  // hypothetical helper
    float v = 1.0 - smoothstep(0.3, 0.71, distance(SCREEN_UV, vec2(0.5))) * 0.5;
    COLOR = vec4(c * v, 1.0);
}
```

For the mini-project, we **stack**. Debuggability matters more than performance on a school project. For a shipped game, fold the late-game stable effects into one shader and stack the experimental ones.

---

## 9. The worked example: polish-pass on Week 9's cursor demo

The mini-project takes Week 9's two-cursor LAN demo and adds:

1. **Hit-flash** on each cursor when it crosses the other cursor's recent path. Trigger via `material.set_shader_parameter("flash", 1.0)` and a tween over 120 ms.
2. **Screen-shake** when two cursors touch. Trigger via `camera.add_shake(8.0)`.
3. **Dissolve transition** when a player disconnects. Trigger via the dissolve shader's `threshold` tween from 0 to 1 over 800 ms.

The total addition is one `screen_shake.gd` (60 lines), one combined `post_process.gdshader` (30 lines), and roughly 15 lines of glue in the existing scene script to fire the effects. The Week 9 game is otherwise unchanged.

That ratio — 100 lines of polish on top of 1000 lines of gameplay — is the production ratio. The polish takes a fraction of the time; it accounts for a disproportionate share of player perception.

---

## 10. Closing summary

The toolbox you now own:

- **Polish tripod**: shake, flash, freeze-frame. None is a shader (only the flash uses one). All three are short. Apply them together.
- **Post-process viewport quad**: SubViewport renders the game; full-screen TextureRect runs the post-process shader; sample with `SCREEN_UV` and `hint_screen_texture`.
- **Six effects**: identity, hit-flash, dissolve, outline, screen wave, palette swap, LUT colour grade. Each is one to twenty lines of GLSL.
- **Particles**: `GPUParticles2D` + `ParticleProcessMaterial`. Configure emission shape, lifetime, velocity, gravity, scale-over-life, colour-over-life. Trigger via `emitting = true`.

The next week is physics: we put your now-polished prototypes onto `RigidBody2D` and learn impulses, forces, joints, and the difference between `_process` and `_physics_process`. The dissolve will come back as the entry transition; the screen-shake will come back as the collision feedback. Polish skills compound.

For homework after this lecture, take any prior week's mini-project that has *zero* visual polish, add the tripod (shake, flash, freeze-frame), and write a short reflection on whether it feels like a different game. It usually does.

---

## References cited in this lecture

- *The Book of Shaders*, chapter 5 *Algorithmic drawing*: <https://thebookofshaders.com/05/>
- *The Book of Shaders*, chapter 6 *Shapes*: <https://thebookofshaders.com/06/>
- *The Book of Shaders*, chapter 7 *Matrices*: <https://thebookofshaders.com/07/>
- Inigo Quilez, *2D distance functions*: <https://iquilezles.org/articles/distfunctions2d/>
- Godot 4 docs, *GPUParticles2D*: <https://docs.godotengine.org/en/stable/classes/class_gpuparticles2d.html>
- Godot 4 docs, *ParticleProcessMaterial*: <https://docs.godotengine.org/en/stable/classes/class_particleprocessmaterial.html>
- Vlambeer, *The art of screen-shake* (Jan Willem Nijman, GDC 2013): YouTube talk, often cited as the canonical reference for the polish tripod.
- GLSL 4.60 specification, section 8.3 (common functions, including `mix`, `smoothstep`, `step`, `clamp`): <https://registry.khronos.org/OpenGL/specs/gl/GLSLangSpec.4.60.pdf>
