# Week 10 — Shaders and Visual Effects

Last week you opened the network socket. Two Pygame clients shared a canvas at 20 Hz over UDP and a Godot port of the same demo collapsed two hundred lines of hand-rolled serialisation into a single `@rpc` annotation. This week we open the part of the engine that runs on the GPU. By Sunday you take a small game from Week 9 (or Week 8 if you prefer audio) and bolt on three visual effects that turn a flat prototype into something that *feels* like a shipped game: a screen-shake, a hit-flash, and a one-shot dissolve transition. All three are built on top of fragment shaders you write yourself, and all three run on a 2015-era integrated GPU.

Shaders are the discipline where a 30-line text file replaces a 30,000-line C++ rendering loop. They are also the discipline whose vocabulary is the most unforgiving for a beginner. "Fragment shader" sounds like a typo for "fragment of a shader" until you learn that a *fragment* is a candidate pixel — a sample at a screen position with a depth — and the *shader* is the tiny program the GPU runs in parallel, once per fragment, to decide that fragment's final colour. We unpack the words this week, the rendering pipeline behind them, and the practical art of using Godot 4.x's shader system to ship effects without writing a single line of C++.

The single best free reading on shaders is Patricio Gonzalez Vivo's *The Book of Shaders* at [thebookofshaders.com](https://thebookofshaders.com/) — a chapter-by-chapter introduction that runs every example live in your browser. Godot 4's own shader docs at [docs.godotengine.org/en/stable/tutorials/shaders/index.html](https://docs.godotengine.org/en/stable/tutorials/shaders/index.html) are the production reference. The *OpenGL Shading Language* (GLSL) specification — Godot's shader language is a curated subset of GLSL — is free at [registry.khronos.org/OpenGL/specs/gl/GLSLangSpec.4.60.pdf](https://registry.khronos.org/OpenGL/specs/gl/GLSLangSpec.4.60.pdf). Three free sources, all linked in `resources.md`, all cited in the lectures.

We start from *The Book of Shaders* chapters 1-7 (everything up through "shapes"), the *Godot 4.x shaders* tutorial tree (the "Introduction", "Your first shader", and "Canvas item shaders" pages), and *Inigo Quilez*'s reference articles at [iquilezles.org/articles](https://iquilezles.org/articles/) for the more advanced effects. By Sunday you ship **eleven hand-written `.gdshader` files, a small Godot scene that demonstrates each one, and a polish-pass on a prior week's mini-project that applies three of them in combination**. The polish pass is the deliverable. The eleven shaders are the toolbox.

This week is the first time we leave CPU code behind for substantial stretches. The fragment shader runs on the GPU, in parallel, with no access to disk, no access to the network, and no ability to "print" anything except a colour. The mental model is that of a pure function: `vec4 fragment(vec2 uv, float time) -> vec4 color`. Every effect in the course — every screen wave, every palette swap, every dissolve — is a different body for that one function signature. Once that lands, the rest is vocabulary.

## Learning objectives

By the end of this week, you will be able to:

- **Name** the four stages of the simplified rendering pipeline relevant to 2D shaders — *vertex processing*, *rasterisation*, *fragment processing*, *blend* — and state what each stage's input and output is. The vertex shader runs once per vertex and outputs a position in clip space; the rasteriser fills in the triangle's interior with *fragments*; the fragment shader runs once per fragment and outputs a colour; the blend stage combines that colour with whatever is already in the framebuffer.
- **Distinguish** a Godot `ShaderMaterial` from a `CanvasItemMaterial`. The latter is a fixed-feature material with checkboxes (light enabled, blend mode); the former runs a `.gdshader` program you wrote. You will use both. The fixed material is for the cases the engine already handles; the shader material is for everything else.
- **Read and write** a Godot canvas-item fragment shader from scratch. You will understand `shader_type canvas_item;`, the built-in inputs (`UV`, `TIME`, `SCREEN_UV`, `TEXTURE`, `COLOR`), the built-in outputs (`COLOR` again, this time on the left of an assignment), and the difference between a *uniform* and a *varying*.
- **Use UV coordinates** confidently. `UV.x` ranges from 0 at the left edge of a textured rectangle to 1 at the right; `UV.y` is 0 at top and 1 at bottom (Godot, not standard GL). Most 2D effects are some function of `UV` and `TIME`. The Book of Shaders chapters 2-5 are the canonical walk-through.
- **Animate** a shader with the built-in `TIME` uniform. A 1 Hz colour cycle is `COLOR.rgb = vec3(0.5 + 0.5 * sin(TIME * TAU))`. The same trick scales to wobbles, pulses, and scrolling patterns.
- **Implement** six 2D effects from the toolbox: a *colour-grade LUT* (look-up table) post-process; a *screen wave / distortion* using `sin(UV.y * frequency + TIME)`; a *one-pixel outline* via four neighbour samples on alpha; a *dissolve transition* via a noise threshold; a *palette swap* via a small LUT texture; and a *hit-flash* tint applied for a short window after a hit.
- **Apply** a post-processing effect via a full-screen *viewport quad*. A `SubViewport` renders the game; a `TextureRect` covering the screen displays that viewport's texture; the `TextureRect`'s `ShaderMaterial` is the post-process pass. This is the architecture every console game from the PS3 era used.
- **Configure** a `GPUParticles2D` node with a `ParticleProcessMaterial`. You will set emission rate, lifetime, initial velocity, gravity, scale-over-life, colour-over-life, and emission shape. You will know when `CPUParticles2D` is the right tool instead (the answer is "almost never on modern hardware, but always when GPU particles will not show in HTML5 export").
- **Profile** a shader at the level of "is it cheap or expensive". A texture sample is cheap; a long loop with branches is expensive; `pow`, `exp`, and `sin` are cheap on modern GPUs but free on no GPU. You can read the Godot profiler's `frame_time_gpu` reading and react to it.
- **Cite** the three free shader references — *The Book of Shaders*, the *Godot 4 shader docs*, and the *GLSL 4.60 specification* — and explain which is for first contact, which is for production, and which is for "the engine did something I do not understand and I need to read the language standard."

## Prerequisites

This week assumes you have completed **Weeks 1-9**. Specifically:

- You have a working Godot 4.x install (4.2 or newer is the tested baseline). The shader editor is in the engine; no external tooling is required.
- You have at least one prior-week mini-project in a state you would be willing to polish. Week 8 (audio) and Week 9 (multiplayer cursor) both work; we use Week 9 in the worked example because the network demo is the most visually plain.
- You are comfortable enough with GDScript to attach a script to a node, read a property, and set a uniform. Week 3 covered the basics.
- You have skim-read *The Book of Shaders* chapter 1 (the "What is a shader?" page) before Monday. Five minutes; sets the vocabulary for the rest of the week.
- A modern GPU helps but is not required. Every shader in this week's exercises was tested on an integrated Intel UHD 630 (a 2018 CPU's iGPU). If your machine renders Godot 4.x's editor at 60 fps, it will run these.

If any of those are shaky, do the previous week's mini-project before continuing.

## Topics covered

Lecture 1 — The rendering pipeline at beginner depth:

- The job of a GPU. A GPU is a wide, parallel, fixed-function-by-default pipeline whose programmable stages — vertex shaders and fragment shaders, in our beginner's slice of it — let you customise *transform* and *colour* respectively. Everything else (clipping, rasterisation, depth test, blend) is fixed-function and runs whether you want it or not.
- The four stages we care about. *Vertex processing* takes one vertex in and produces one transformed vertex; the vertex shader's job is to put the vertex where it belongs in clip space. *Rasterisation* takes the assembled triangle and emits one *fragment* per pixel the triangle covers; this is fixed-function and you cannot customise it. *Fragment processing* takes one fragment in and produces one colour out; the fragment shader is where 95% of your beginner shader code lives. *Blend* combines the fragment's colour with whatever is in the framebuffer; usually `src_alpha * src + (1 - src_alpha) * dst` for transparent sprites.
- The data types. `vec2`, `vec3`, `vec4` are 2/3/4-component vectors of `float`. `mat4` is a 4x4 matrix used for transforms. `sampler2D` is the GPU's handle for a texture you sample with `texture(sampler, uv)`. There are no pointers, no objects, no recursion. Shaders are pure functions in a curated language.
- The mental model: a shader is a *function the GPU runs in parallel, once per fragment, with no shared state*. There is no for-loop over pixels in your code; the GPU is the for-loop. Every fragment shader you write is executed thousands to millions of times per frame, in parallel, with no way for one fragment to know what colour its neighbour picked. Once that lands, the constraints make sense: no random access to other fragments, no "previous frame" without a render target, no breaking out of a draw early.

Lecture 2 — Godot 4 shader system in practice:

- `ShaderMaterial` vs `CanvasItemMaterial`. The latter is the fixed-feature material every `Sprite2D` gets by default: tint, blend mode, light-enabled. The former is a custom program. You convert from one to the other by clicking the dropdown in the inspector and picking "New ShaderMaterial".
- The `.gdshader` file. A text file with a `shader_type` declaration on line 1 (`canvas_item` for 2D, `spatial` for 3D, `particles` for particle process materials), zero or more `uniform` declarations, zero or more functions, and one or more of the three special functions `vertex()`, `fragment()`, `light()`.
- `canvas_item` shader inputs. `UV` is the texture coordinate at the fragment (0..1). `COLOR` is both an input (the sprite's modulate colour) and an output (what the fragment shader writes). `TEXTURE` is the sprite's albedo texture; you sample it with `texture(TEXTURE, UV)`. `TIME` is the engine time in seconds. `SCREEN_UV` is the fragment's screen position normalised to 0..1; needed for screen-space effects.
- Uniforms. A `uniform` is a constant input you set from GDScript with `material.set_shader_parameter("name", value)`. The cost of changing a uniform between draws is small. Use uniforms for every tunable parameter (wave frequency, dissolve threshold, tint colour).
- Hints. `uniform float threshold : hint_range(0.0, 1.0)` tells the editor to show a slider. `uniform sampler2D lut : hint_default_white` tells the engine to use a 1x1 white texture if you do not assign one. Hints make a shader's editor experience a real tool.
- The full-screen post-process pattern. Render the game into a `SubViewport`. Display the viewport's texture in a `TextureRect` that fills the screen. Assign a `ShaderMaterial` to the `TextureRect`. The fragment shader gets the rendered frame as `TEXTURE` and outputs the post-processed colour. This is how you do colour grading, screen-space waves, vignettes, and CRT effects in Godot.

Lecture 3 — Effects toolbox: from one-line shaders to compound effects:

- The minimal fragment shader: `void fragment() { COLOR = texture(TEXTURE, UV); }`. Identity. From here every effect is one or two extra lines.
- *Hit-flash*. Add a uniform `flash` in 0..1 and write `COLOR.rgb = mix(COLOR.rgb, vec3(1.0), flash)`. A short GDScript tween over `flash` from 1 to 0 over 100 ms is the entire "I was hit" feedback.
- *Screen-shake*. Not a shader at all — it is camera translation by a decaying random offset. We cover it here because it is the third leg of the "feel" tripod (shake + flash + freeze-frame).
- *Dissolve*. Sample a noise texture by UV, compare against a threshold uniform, discard fragments below. Animate threshold from 0 to 1 to make a sprite disappear in a randomised pattern.
- *Outline*. Sample the texture's alpha at four neighbour UVs (`UV + vec2(+1/w, 0)`, `UV + vec2(-1/w, 0)`, similar for y). If the current alpha is 0 and any neighbour's alpha is >0, output the outline colour. One-pixel outline in eight lines.
- *Screen wave*. In a post-process shader, sample the viewport at `SCREEN_UV + vec2(sin(SCREEN_UV.y * 30.0 + TIME * 5.0) * 0.005, 0.0)`. Heat-haze, underwater shimmer, hit-shock.
- *Colour grade via LUT*. A small (typically 16x16 or 32x32 strip) texture maps every input colour to a graded output. Two texture samples, one mix. Every modern game uses this for "looks like night," "looks like fire," "looks like the bad ending."
- *Palette swap*. Each pixel's colour indexes a 1-D palette texture. The displayed colour is the palette at that index. Same character, ten outfits, one shader.
- The art of *combining* effects. Stack them as separate `TextureRect`s, each rendering the previous one's output. Or fold them into a single longer fragment shader if they are cheap. We do the first; it is more debuggable.

## Weekly schedule

The schedule below adds up to approximately **33 hours**. Treat it as a target. Shaders are the rare topic where the *first* hour is the hardest; once the mental model lands, you start moving fast.

| Day       | Focus                                          | Lectures | Exercises | Challenges | Quiz/Read | Homework | Mini-Project | Self-Study | Daily Total |
|-----------|------------------------------------------------|---------:|----------:|-----------:|----------:|---------:|-------------:|-----------:|------------:|
| Monday    | Lecture 1 + first identity shader              |    2h    |    1.5h   |     0h     |    0.5h   |   1h     |     0h       |    0.5h    |     5.5h    |
| Tuesday   | Lecture 2 + uniforms + hit-flash               |    2h    |    1.5h   |     0h     |    0.5h   |   1h     |     0.5h     |    0h      |     5.5h    |
| Wednesday | Dissolve, outline, palette swap                |    0h    |    2h     |     0.5h   |    0.5h   |   1h     |     1h       |    0.5h    |     5.5h    |
| Thursday  | Lecture 3 + post-process viewport pattern      |    2h    |    1h     |     0.5h   |    0.5h   |   0.5h   |     1.5h     |    0h      |     6h      |
| Friday    | Particles + Book of Shaders chapters 3-5       |    0h    |    1h     |     1h     |    0.5h   |   0.5h   |     2h       |    0.5h    |     5.5h    |
| Saturday  | Mini-project polish pass — three effects       |    0h    |    0h     |     0h     |    0h     |   0h     |     4.5h     |    0.5h    |     5h      |
| Sunday    | Mini-project recording + quiz + write-up       |    0h    |    0h     |     0h     |    1h     |   0.5h   |     1.5h     |    0h      |     3h      |
| **Total** |                                                | **6h**   | **7h**    | **2h**     | **3.5h**  | **4.5h** | **11h**      | **2h**     | **36h**     |

A modest overshoot is normal in the first half (the rendering pipeline takes time to internalise) and an undershoot is normal in the second half (the toolbox shaders are short).

## Files in this folder

| File / Folder                                     | What it is                                                          |
|---------------------------------------------------|----------------------------------------------------------------------|
| `README.md`                                       | This file. The week's contract.                                      |
| `resources.md`                                    | The annotated reading list. *The Book of Shaders*, Godot docs, GLSL spec, plus Inigo Quilez and Shadertoy. |
| `lecture-notes/01-rendering-pipeline-and-the-fragment-shader.md` | The pipeline, the data flow, the mental model.            |
| `lecture-notes/02-godot-shader-system-uniforms-and-canvas-item.md` | `ShaderMaterial`, uniforms, hints, the `canvas_item` shader. |
| `lecture-notes/03-effects-toolbox-and-the-post-process-quad.md` | Six effects, the post-process pattern, the polish tripod.   |
| `exercises/exercise-01-identity-and-tint.gdshader`| Minimal identity shader plus a tint uniform.                         |
| `exercises/exercise-02-hit-flash.gdshader`        | A one-uniform white-flash mix.                                       |
| `exercises/exercise-02-hit-flash-driver.gd`       | The GDScript that tweens the uniform on hit.                         |
| `exercises/exercise-03-dissolve.gdshader`         | Noise-threshold dissolve.                                            |
| `exercises/exercise-04-outline.gdshader`          | Four-tap alpha-outline.                                              |
| `exercises/exercise-05-screen-wave.gdshader`      | Post-process screen distortion.                                      |
| `exercises/exercise-06-palette-swap.gdshader`     | Indexed palette swap via a 1-D LUT.                                  |
| `exercises/exercise-07-particles.gd`              | `GPUParticles2D` configured from code.                               |
| `exercises/uv-playground.py`                      | A Pygame-based UV visualiser; helps internalise the coordinate system without a GPU. |
| `exercises/SOLUTIONS.md`                          | Walk-through of every exercise.                                      |
| `challenges/challenge-01-port-a-shadertoy.md`     | Take one Shadertoy effect, port it to Godot canvas-item syntax.     |
| `challenges/challenge-02-design-a-LUT.md`         | Design a 16x16 colour-grade LUT in Python, export, apply in Godot.  |
| `quiz.md`                                         | 20 multiple-choice + short-answer questions.                        |
| `homework.md`                                     | The week's structured homework. Three problems plus a write-up.      |
| `mini-project/README.md`                          | The polish-pass spec: take Week 9 (or Week 8), apply three effects. |
| `mini-project/screen_shake.gd`                    | The screen-shake helper for the polish pass.                        |
| `mini-project/post_process.gdshader`              | The single combined post-process shader for the worked example.     |

## How to run any shader in this folder

1. Open Godot 4.2+ (or newer).
2. Create a new 2D scene with a `Sprite2D` (or any `CanvasItem`).
3. Assign a texture to the sprite (any PNG; the `icon.svg` Godot ships works).
4. In the inspector, set the sprite's *Material* to a *New ShaderMaterial*.
5. On the `ShaderMaterial`, set *Shader* to a *New Shader*.
6. Paste the contents of any `.gdshader` file into the shader editor.
7. Save the shader file.

If the sprite turns black, your shader is writing `vec4(0.0)` to `COLOR`. If the editor shows a red error, read the line number; GLSL compilers are unforgiving but precise.

## Grading

| Component             | Weight |
|-----------------------|-------:|
| Quiz (20 questions)   |   15%  |
| Homework (3 problems) |   25%  |
| Exercises (8 files)   |   20%  |
| Challenges (2 files)  |   15%  |
| Mini-project          |   25%  |
| **Total**             | **100%** |

A pass is 70%. The mini-project is the single largest weight; the recorded screen-capture (10 seconds of gameplay with all three effects applied) is the deliverable that counts.

## Common pitfalls

A short list of pitfalls that catch first-time shader students. None is fatal; all are easy to fix once recognised.

- **Black sprite.** Most often: you wrote `COLOR = vec4(0.0);` or you forgot the `vec4(... , 1.0)` alpha component and the sprite renders fully transparent against a black background. Read the line that writes to `COLOR`; check the alpha.
- **Pink sprite (Godot's missing-shader colour).** The shader has a compile error and Godot is falling back. Open the shader in the editor; the error is in the *Errors* panel below the code with a precise line number.
- **The flash is permanent.** The tween finished but its end-value got stuck. Add a `_set_flash(0.0)` call in `_ready()` and verify the tween reaches its end value. Confirm by checking the inspector's *Shader Parameters* after the tween completes.
- **Every sprite flashes when one does.** Material sharing. Add `material = material.duplicate()` in `_ready()`.
- **The outline is on the wrong side.** Texture wrap mode is set to *Repeat*. Switch to *Disable* in the texture's import settings.
- **The post-process is invisible.** The SubViewport is not rendering. Set `render_target_update_mode = ALWAYS`. Also check that the SubViewport's *Disable 3D* flag is on (2D-only scenes should not pay 3D-render cost).
- **The particles do not appear.** The `emitting` toggle is true but the system already finished its one-shot cycle. Call `restart()` instead of setting `emitting = true`.
- **The dissolve shows the entire sprite tinted edge-colour, not just the edge.** `edge_width` is set higher than 1.0 or the dissolve_noise texture is a constant colour. Reduce edge_width to ~0.05; verify the noise texture has varied pixel values.
- **The screen-wave looks like ripples on a still pond when you wanted heat shimmer.** The frequency is too low. Raise `wave_frequency` to 60-80 for fine shimmer.

When in doubt, the debug trick from Lecture 1 applies: output an intermediate value as a colour. Write `COLOR = vec4(your_variable, 0.0, 0.0, 1.0);` and squint.

## A note on the next week

Week 11 picks up *physics and collision response* with full 2D rigid bodies in Godot. You will replace the kinematic movement of every prior week with `RigidBody2D`-driven motion, learn the difference between an impulse and a force, and ship a tiny pinball-style mini-game. The dissolve and hit-flash you build this week will carry over and have a home there.

The skills compound across weeks. Week 9 gave you the network. Week 10 gives you the polish. Week 11 will give you the physics. By the end of the course, the toolbox is big enough that a "small polish pass" on a prototype takes an afternoon and meaningfully changes how the prototype reads to a fresh player. That is the moment the course's investment pays off.

The shader work this week is also the foundation for any future graphics-heavy project: 3D shaders are a superset of the 2D pipeline you learned (vertex shaders do more work, fragment shaders gain access to lighting inputs, but the function-of-pure-data nature is identical). If the math felt natural this week, you have everything you need to expand into 3D in a later course. If it felt awkward, that is normal too — shaders are one of the few topics where the first week is genuinely the hardest, and where the second exposure (in a Week-15 lighting topic, say) lands much faster than the first.

Save your `.gdshader` files. Reuse them. Build a personal library. By the time you have shipped a few projects with polish passes like this one, you will have a folder of two dozen tested shaders that handle 90% of effects you reach for. That folder is more valuable than any single project's shader. It is the working toolbox of a professional.
