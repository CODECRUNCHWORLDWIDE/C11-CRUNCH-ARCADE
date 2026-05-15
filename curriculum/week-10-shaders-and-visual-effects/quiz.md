# Week 10 Quiz — Shaders and Visual Effects

> **Time:** 30 minutes.
> **Open book:** yes (lectures, exercises, Godot docs allowed; no chat assistants).
> **Total:** 20 questions, 1 point each. Pass at 14/20.

Write your answers in a new file `quiz-answers.md` next to this one. For multiple-choice questions, give the letter and a one-sentence justification. For short-answer questions, two to four sentences are enough.

---

## Section A — The rendering pipeline (5 questions)

**1.** Which of the following is **not** one of the four pipeline stages relevant to a 2D shader (as defined in Lecture 1)?

(a) Vertex processing  
(b) Rasterisation  
(c) Tessellation  
(d) Fragment processing  
(e) Blend

**2.** A "fragment" in the GPU pipeline is:

(a) The same thing as a pixel after blending.  
(b) A candidate colour at a screen position with an interpolated set of varyings, before the blend step.  
(c) The geometry data produced by a vertex shader.  
(d) An incomplete shader program that the GPU rejects.

**3.** True or false: a fragment shader can read the colour that the fragment shader for the neighbouring pixel just wrote, by sampling at `UV + TEXTURE_PIXEL_SIZE`.

**4.** Explain in one or two sentences why a fragment shader cannot use recursion.

**5.** Name the GLSL built-in function that performs linear interpolation between two values, and give its signature.

---

## Section B — Godot shader system (5 questions)

**6.** Which Godot material type would you use to apply a custom 5-line fragment shader to a Sprite2D?

(a) `CanvasItemMaterial`  
(b) `ShaderMaterial`  
(c) `ParticleProcessMaterial`  
(d) `StandardMaterial2D` (no such class exists; trick option)

**7.** What does the `: source_color` hint do when applied to a `vec4` uniform?

(a) It restricts the uniform to opaque colours (alpha 1.0).  
(b) It tells the engine the input is in sRGB and to linearise it.  
(c) It exposes the uniform as read-only to the editor.  
(d) It changes the uniform's type from `vec4` to `vec3`.

**8.** A student writes the shader below and assigns it to two Sprite2D nodes that share the same `ShaderMaterial` resource. When they call `node_a.material.set_shader_parameter("flash", 1.0)`, both sprites flash. Why? How do you fix it in one line?

```gdscript
extends Sprite2D
func _ready() -> void:
    pass  # nothing here
```

**9.** Give the line of GDScript that assigns the value `0.7` to a uniform named `threshold` on the current node's `ShaderMaterial`.

**10.** What is the difference between `TIME` and `delta` (the parameter of `_process`) in the context of a shader's animation?

---

## Section C — UV coordinates and the toolbox (5 questions)

**11.** In a Godot `canvas_item` fragment shader, what range does `UV.y` cover and at which end of the sprite is `UV.y = 0`?

**12.** Write the *minimal* fragment-shader expression that produces a horizontal red-green gradient across the sprite (red at left, green at right).

**13.** The hit-flash shader writes `COLOR.rgb = mix(base.rgb, vec3(1.0), flash);`. What value of `flash` results in the unchanged sprite, and what value results in fully white?

**14.** In the outline shader, why must the sprite's texture have transparent border pixels around its visible content?

**15.** Describe in one sentence what `smoothstep(edge0, edge1, x)` returns at `x == (edge0 + edge1) / 2`.

---

## Section D — Post-processing and particles (5 questions)

**16.** Describe the post-process viewport quad pattern in one paragraph (3-5 sentences). What goes in the SubViewport; what samples it; what is the role of `hint_screen_texture`?

**17.** A student is configuring a `GPUParticles2D` and sets `mat.gravity = Vector2(0, 400)`. Godot raises an error. Why?

(a) Gravity in particles is read-only.  
(b) Even in 2D particles, the `gravity` field is a `Vector3`.  
(c) The value 400 exceeds the maximum gravity strength of 100.  
(d) The student must enable the `gravity_enabled` flag first.

**18.** When configuring a one-shot particle burst (e.g. a hit-spark), which of these is the correct setup?

(a) `emitting = true`, `one_shot = false`, restart with `emitting = false`.  
(b) `emitting = true`, `one_shot = true`, re-trigger with `restart()`.  
(c) `emitting = false`, `one_shot = true`, re-trigger by setting `emitting = true`.  
(d) `emitting = false`, `one_shot = false`, re-trigger by setting `lifetime = 0`.

**19.** Name the three components of the "polish tripod" and which of the three is implemented as a shader.

**20.** Short-essay (3-5 sentences): describe a situation in which you would *fold* multiple effects into a single fragment shader rather than *stack* them as separate post-process passes. Cite at least one trade-off.

---

## Reference answers (for self-grading after attempt)

Do not read this section until you have written your full answers in `quiz-answers.md`.

1. **(c) Tessellation.** Tessellation is a 3D pipeline stage; 2D shaders skip it.
2. **(b).** Fragments are candidates with interpolated varyings; the blend step happens after.
3. **False.** Fragments execute in parallel with no ordering guarantee; the neighbour's output is not available. You can sample the *texture* at `UV + offset`, which is what the outline shader does, but that samples the input texture, not another fragment's output.
4. Fragment shaders execute in parallel on many GPU cores with no shared call stack; recursion would require a per-thread stack of unknown depth that the architecture does not support. The compiler enforces this restriction.
5. `mix(a, b, t)`, returns `a * (1 - t) + b * t`.
6. **(b) ShaderMaterial.**
7. **(b).** Linearises sRGB input. Without it, the math operates on gamma-encoded values.
8. The `ShaderMaterial` resource is shared between the two nodes. Fix: in `_ready()`, write `material = material.duplicate()`.
9. `material.set_shader_parameter("threshold", 0.7)` (assuming `material` is the node's ShaderMaterial).
10. `TIME` is engine-time in seconds, monotonic; useful inside a shader where you have no other clock. `delta` is the per-frame elapsed time, used CPU-side to advance state. They serve different scopes.
11. `UV.y` covers 0..1. In Godot canvas_item, `UV.y = 0` is at the top of the sprite.
12. `COLOR = vec4(UV.x, 1.0 - UV.x, 0.0, 1.0);` (or equivalent — accept any expression with the right gradient).
13. `flash = 0.0` gives the unchanged sprite. `flash = 1.0` gives fully white.
14. Because the four (or eight) neighbour samples occur at `UV +/- TEXTURE_PIXEL_SIZE`. If the sprite is cropped tight, those samples land outside the texture. With `repeat_disable` they return transparent, which we want; with `repeat_enable` they wrap, breaking the outline. Even with `repeat_disable`, an artist who paints to the very edge of the texture cannot grow an outline outward because there is no room.
15. `smoothstep` returns a Hermite-interpolated value (approximately 0.5 at the midpoint, but with smoother derivatives than linear; it is the value 0.5 + 3/8 * 0 = 0.5 by the smoothstep polynomial at t=0.5, and yes the midpoint is exactly 0.5).
16. The SubViewport renders the game (Camera2D + game-world children). A full-screen TextureRect samples the SubViewport's output texture via a ShaderMaterial. The `hint_screen_texture` hint on a `uniform sampler2D` auto-binds the rendered viewport content, removing the need for manual texture wiring. The TextureRect's shader is the post-process pass; it reads `SCREEN_UV` and writes the final output.
17. **(b).** `gravity` is `Vector3` even in 2D particles. Pass `Vector3(0, 400, 0)`.
18. **(b).** `one_shot = true`, `emitting = true` initially, and use `restart()` to re-trigger.
19. Screen-shake, hit-flash, and freeze-frame. Only the hit-flash is implemented as a shader. (Shake is camera-translation; freeze-frame is `Engine.time_scale`.)
20. Folding is appropriate when (a) the effects are stable and final, (b) the texture-sampling cost dominates and a single combined pass avoids redundant samples, or (c) the platform is mobile/HTML5 where every full-screen pass is expensive. Trade-off: folded shaders are harder to A/B disable individual effects; stacked shaders are debuggable per-pass. Production typically starts stacked and folds late in the cycle.
