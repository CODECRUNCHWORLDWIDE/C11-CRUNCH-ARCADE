# Week 10 Resources — Shaders and Visual Effects

Every resource on this list is **free**. Where a book has a print edition, the free online version is the cited one. Where a specification has a paid PDF, the free Khronos-published version is the cited one. We do not require any paid tutorial, video course, or asset pack this week.

The reading list is structured in three tiers. Tier A is required for the lectures and the exercises. Tier B sharpens specific muscles and is worth doing for any student who wants to move beyond the toolbox. Tier C is for the curious; it is where you go when the toolbox runs out and you want to ship something the lectures did not cover.

---

## Tier A — Required

### A1. *The Book of Shaders* by Patricio Gonzalez Vivo and Jen Lowe

- **URL:** [https://thebookofshaders.com/](https://thebookofshaders.com/)
- **Cost:** Free. Open source under the CC-BY-NC-SA licence; the code samples are MIT-licensed.
- **Format:** Web book with live in-browser shader editors on every page. Reads top-to-bottom; each chapter ends with an exercise you can complete in the embedded editor.
- **Required chapters for this week:** Chapters 1 ("What is a shader?"), 2 ("Hello world"), 3 ("Uniforms"), 4 ("Running your shader"), 5 ("Algorithmic drawing"), 6 ("Shapes"), 7 ("Matrices") — read in order. Estimated time: 90 minutes if you do the in-page exercises, 30 minutes if you skim.
- **Why it is the canonical first contact:** the author is one of the maintainers of the open-source GLSL editor *glslEditor*; every example is live; the prose assumes no graphics background. The free chapters end at chapter 13 ("Image processing") which is enough material for an entire course on its own.
- **Citation in this week's notes:** cited in every lecture and exercise that uses UV coordinates or time animation.

### A2. Godot 4.x shader docs

- **URL:** [https://docs.godotengine.org/en/stable/tutorials/shaders/index.html](https://docs.godotengine.org/en/stable/tutorials/shaders/index.html)
- **Cost:** Free. The Godot documentation is CC-BY 3.0.
- **Required pages for this week:**
  - *Introduction* — [https://docs.godotengine.org/en/stable/tutorials/shaders/introduction_to_shaders.html](https://docs.godotengine.org/en/stable/tutorials/shaders/introduction_to_shaders.html)
  - *Your first shader* — [https://docs.godotengine.org/en/stable/tutorials/shaders/your_first_shader/index.html](https://docs.godotengine.org/en/stable/tutorials/shaders/your_first_shader/index.html)
  - *Canvas item shaders* — [https://docs.godotengine.org/en/stable/tutorials/shaders/shader_reference/canvas_item_shader.html](https://docs.godotengine.org/en/stable/tutorials/shaders/shader_reference/canvas_item_shader.html)
  - *Shading language reference* — [https://docs.godotengine.org/en/stable/tutorials/shaders/shader_reference/shading_language.html](https://docs.godotengine.org/en/stable/tutorials/shaders/shader_reference/shading_language.html)
- **Why it is required:** the *Canvas item shaders* page is the load-bearing reference for everything in the exercises. It enumerates every built-in input (`UV`, `COLOR`, `TIME`, `SCREEN_UV`, `TEXTURE`, `MODULATE`, `SCREEN_PIXEL_SIZE`, and friends), every built-in function, and every render mode (`blend_mix`, `blend_add`, `unshaded`, ...) you will use.
- **Local tip:** Godot 4.x ships its own help system; press `F1` in the editor and search "Shader" for offline coverage. Use the online docs when you need to copy a URL into homework.

### A3. *OpenGL Shading Language* (GLSL) 4.60 specification

- **URL:** [https://registry.khronos.org/OpenGL/specs/gl/GLSLangSpec.4.60.pdf](https://registry.khronos.org/OpenGL/specs/gl/GLSLangSpec.4.60.pdf)
- **Cost:** Free. Published by the Khronos Group.
- **Length:** 250 PDF pages. *Do not* read it front-to-back; treat it as a reference manual.
- **Required reading for this week:** Sections 1, 4.1 ("Basic types"), 5.1 ("Operators"), and 8 ("Built-in functions"). The built-in functions list is the gold-standard reference for `mix`, `smoothstep`, `step`, `clamp`, `length`, `distance`, `dot`, `cross`, and the transcendentals.
- **Why it matters:** Godot's shader language is a curated subset of GLSL plus a few Godot-specific built-ins. When you write `smoothstep(0.0, 1.0, x)` and want to know exactly what that function returns at `x = 0.5`, the spec is the answer (it returns the Hermite-interpolated value, not 0.5).
- **A practical aside:** the GLSL spec is famously dense. Most students will read sections 8.1–8.4 (angle and trigonometry functions, exponentials, common functions, geometric functions) a few times this week and never open the rest. That is the correct way to use a language specification.

---

## Tier B — Strongly recommended

### B1. Inigo Quilez's articles and 3D SDF reference

- **URL:** [https://iquilezles.org/articles/](https://iquilezles.org/articles/)
- **Cost:** Free.
- **Highlighted articles for this week:**
  - *Painting Mona Lisa with Maths* — a tour of how to build shapes from analytic equations.
  - *Smooth Minimum* — the `smin` function that makes shader-built shapes blend like blobs.
  - *Distance functions* — the canonical reference for signed-distance shapes. The 3D index is also linked from this page; the 2D primitives we use this week are at [https://iquilezles.org/articles/distfunctions2d/](https://iquilezles.org/articles/distfunctions2d/).
- **Why it matters:** Quilez is one of the most influential figures in real-time graphics and the original creator of Shadertoy. The articles are short, generous, and full of working code.

### B2. Shadertoy

- **URL:** [https://www.shadertoy.com/](https://www.shadertoy.com/)
- **Cost:** Free. Account required to save your own shaders; not required to view others'.
- **How to use it for this course:**
  - Browse [https://www.shadertoy.com/results?query=&sort=popular](https://www.shadertoy.com/results?query=&sort=popular) for inspiration.
  - For each shader you like, read the GLSL source on the page; understand it before porting.
  - Note: Shadertoy uses raw OpenGL GLSL with the `mainImage(out vec4 fragColor, in vec2 fragCoord)` entry point. Godot's canvas-item shaders use `void fragment()` with `COLOR` as the implicit output and `UV` as the coordinate. Challenge 1 walks the port mechanically.
- **Caveat:** Shadertoy is open culture; not every shader is hand-rolled by its author and not every shader works in Godot without translation. Read the comments; many top shaders are forks of forks.

### B3. *Real-Time Rendering*, 4th edition — chapters 1–3 (overview chapters)

- **URL:** [https://www.realtimerendering.com/](https://www.realtimerendering.com/) — the book's site links every free supplementary chapter and erratum. The book itself is not free; the first three chapters' worth of material is well-summarised in the freely-available *Crash Course in BRDF Implementation* by Jakub Boksansky at [https://boksajak.github.io/blog/BRDF](https://boksajak.github.io/blog/BRDF) for the rendering-equation side, and the introductory chapters of *Real Shading in Unreal Engine 4* (Brian Karis, SIGGRAPH 2013 course notes; free PDF at [https://blog.selfshadow.com/publications/s2013-shading-course/karis/s2013_pbs_epic_notes_v2.pdf](https://blog.selfshadow.com/publications/s2013-shading-course/karis/s2013_pbs_epic_notes_v2.pdf)) for the practical side.
- **Cost:** The book is not free; the cited supplements are.
- **When to read:** if you want to extend the toolbox into 3D shaders in a later week.

---

## Tier C — Worth knowing exists

### C1. Freya Holmér's "Shaders for Game Devs" video series

- **URL:** [https://www.youtube.com/c/Acegikmo](https://www.youtube.com/c/Acegikmo)
- **Cost:** Free.
- **Why it is here:** Holmér is one of the best public educators on shader math currently working. Her *math for game developers* and *shader fundamentals* playlists are exceptional. We list her under Tier C only because video pacing is slower than reading; if you prefer video, promote this to Tier A.

### C2. Khronos OpenGL wiki — *Rendering Pipeline Overview*

- **URL:** [https://www.khronos.org/opengl/wiki/Rendering_Pipeline_Overview](https://www.khronos.org/opengl/wiki/Rendering_Pipeline_Overview)
- **Cost:** Free.
- **Why it is here:** the canonical free reference for the pipeline diagram in Lecture 1. We do not require it for the week's work but the diagram is worth a glance.

### C3. *Game Programming Patterns* — *Component* and *Object Pool* chapters

- **URL:** [https://gameprogrammingpatterns.com/contents.html](https://gameprogrammingpatterns.com/contents.html)
- **Cost:** Free online edition.
- **Relevance to this week:** the *Object Pool* chapter is the right pattern for the particle systems we configure in Exercise 7; Godot's `GPUParticles2D` is internally an object pool of GPU-side particle records. Knowing the pattern by name makes the engine's behaviour less mysterious.

### C4. *NVIDIA GPU Gems 1* (free online)

- **URL:** [https://developer.nvidia.com/gpugems/gpugems/contributors](https://developer.nvidia.com/gpugems/gpugems/contributors)
- **Cost:** Free. NVIDIA published GPU Gems 1 in full online.
- **Why it is here:** the historical record of where many shader effects were first popularised. Chapter 19 (*Image Processing*) and Chapter 21 (*True Impostors*) are particularly relevant to 2D screen-space effects.

### C5. Godot Asset Library — *Godot Shaders* gallery

- **URL:** [https://godotshaders.com/](https://godotshaders.com/)
- **Cost:** Free.
- **Why it is here:** a community catalogue of MIT-licensed `.gdshader` files. *Do not* copy-paste these for the week's exercises; do browse them after the homework is in to see what shipped projects look like. Many of these shaders are the de-facto "Godot dialect" of effects that originated on Shadertoy.

---

## A note on citation hygiene

In your homework write-ups, in any blog post you publish about this week, and in any comment in a shipped `.gdshader` file, **cite the source** when you ported a non-trivial technique. The three Tier-A resources are public domain or permissive; Shadertoy shaders are author-owned and most require attribution. When in doubt, attribute. The shader community is small and lives on attribution.

A reasonable citation in a `.gdshader` comment looks like:

```glsl
// Outline algorithm: 4-tap alpha sampling.
// Reference: Godot Shaders, "2D outline / stroke",
// <https://godotshaders.com/shader/2d-outline/> (MIT, accessed 2026-05).
```

That is enough. No formal-paper bibliography is required at this level.

## Reading order, in one paragraph

Read *The Book of Shaders* chapters 1-3 on Monday morning before Lecture 1. Read the Godot *Introduction* and *Your first shader* pages Monday evening before Tuesday's exercises. Read *The Book of Shaders* chapters 4-7 across Tuesday and Wednesday. Read the *Canvas item shaders* docs page in full on Thursday before the post-process exercise. Open the GLSL spec exactly once, on Friday, when you need to look up what `smoothstep` does (section 8.4); never read it cover-to-cover. Browse Shadertoy on the weekend for one hour, no more, looking for the effect you want to port for Challenge 1.

That is the week.
