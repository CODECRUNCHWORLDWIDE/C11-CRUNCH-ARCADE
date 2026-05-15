// exercise-03-dissolve.gdshader
//
// Goal
// ----
// A canvas-item shader that "burns away" a sprite in a randomised pattern
// driven by a noise texture and a single `threshold` uniform in 0..1.
// At threshold = 0 the sprite is fully visible; at threshold = 1 the
// sprite has fully dissolved. A coloured edge tracks the burn front.
//
// This is the standard dissolve transition seen in dozens of action
// games: enemy death, item materialisation, scene wipe. The shader
// itself is short; the *driver* (a tween from 0 to 1) is what makes it
// feel like a transition rather than a slider.
//
// What you learn
// --------------
// - The `discard` keyword: a fragment shader can opt out of writing
//   any colour for the current fragment. The pixel keeps whatever was
//   already in the framebuffer.
// - A noise texture as the "per-fragment random number" trick. The
//   noise is computed offline (or generated once in Python; see
//   SOLUTIONS.md). At runtime, every fragment samples it and gets a
//   stable but spatially-varied value to threshold against.
// - smoothstep(edge0, edge1, x) for soft-falloff edges. The edge of
//   the dissolve is more visually arresting than a hard discard line.
// - mix(a, b, t) reappears for the edge-colour blend.
// - hint_default_white makes the shader degrade gracefully if no noise
//   texture is assigned in the editor.
//
// Expected behaviour
// ------------------
// With threshold = 0 and a typical noise texture, the sprite renders
// almost normally (a few pixels of noise just below 0 still discard,
// but they are rare).
// As threshold increases toward 1, progressively more fragments fail
// the threshold check and discard. The remaining fragments near the
// burn front are tinted toward edge_color.
// At threshold = 1, almost no fragments survive; the sprite is gone.
//
// To run
// ------
// 1. Open Godot 4.2+ and create a 2D scene.
// 2. Add a Sprite2D; assign any opaque PNG as its texture.
// 3. Set Material to "New ShaderMaterial" and Shader to "New Shader".
// 4. Paste this file.
// 5. Generate a noise texture (or use the script in SOLUTIONS.md to
//    write `noise_256.png`). Drop it in your project. Assign it to the
//    `dissolve_noise` uniform in the inspector.
// 6. Drag the `threshold` slider from 0 to 1. Watch the sprite vanish.
// 7. Optional: attach a small GDScript that tweens `threshold` from 0
//    to 1 over 1 second when the scene loads.
//
// To complete
// -----------
// Ships complete. Read it, tune `edge_width` (narrow = sharp burn,
// wide = soft fade), and try generating noise textures of different
// frequencies in Python. High-frequency noise gives a fine dither;
// low-frequency noise gives chunky region-by-region dissolution.
//
// References
// ----------
// - Godot Shaders community, *Dissolve shader* (CC0):
//   https://godotshaders.com/shader/dissolve-shader/
// - *The Book of Shaders*, chapter 11 *Noise*:
//   https://thebookofshaders.com/11/
// - GLSL 4.60 spec, section 8.3 (smoothstep, mix, step):
//   https://registry.khronos.org/OpenGL/specs/gl/GLSLangSpec.4.60.pdf
// - Inigo Quilez, *Useful little functions*:
//   https://iquilezles.org/articles/functions/

shader_type canvas_item;

// =====================================================================
// Uniforms.
// =====================================================================

// The noise texture. Each fragment samples its red channel as a
// "per-fragment random number" to compare against `threshold`.
// `repeat_enable` lets us tile the noise across larger sprites.
// `hint_default_white` means: if no texture is assigned, fall back to
// a 1x1 white texture, which gives a uniform dissolve from 1.0 down.
uniform sampler2D dissolve_noise : repeat_enable, filter_linear, hint_default_white;

// The dissolve progress. 0.0 = visible; 1.0 = fully dissolved.
// Driven by GDScript via material.set_shader_parameter("threshold", t).
uniform float threshold : hint_range(0.0, 1.0) = 0.0;

// The colour of the burning edge. Bright orange is the canonical
// "fire" choice; cool blue is the canonical "ice" choice.
uniform vec4 edge_color : source_color = vec4(1.0, 0.6, 0.0, 1.0);

// How wide the coloured edge band is, in noise-value units.
// 0.0 disables the edge effect (clean discard); 0.2 gives a thick band.
uniform float edge_width : hint_range(0.0, 0.2) = 0.05;

// How the noise texture is sampled in UV space.
// 1.0 = one tile per sprite; 4.0 = four tiles per sprite (finer dissolve).
uniform float noise_scale : hint_range(0.5, 16.0) = 1.0;

// =====================================================================
// Fragment function.
// =====================================================================

void fragment() {
    // Sample the sprite's base albedo.
    vec4 base = texture(TEXTURE, UV);

    // Sample the noise texture, optionally tiled. We only need the red
    // channel; the texture is grayscale by design.
    float noise = texture(dissolve_noise, UV * noise_scale).r;

    // Fragments below the threshold are discarded — they contribute no
    // colour and the framebuffer keeps whatever was drawn before this
    // sprite.
    if (noise < threshold) {
        discard;
    }

    // Fragments within `edge_width` of the threshold are tinted toward
    // edge_color. smoothstep gives a soft falloff: 0 at noise=threshold,
    // 1 at noise=threshold+edge_width.
    float edge_t = smoothstep(threshold, threshold + edge_width, noise);

    // mix(edge_color, base, edge_t) — when edge_t == 0 (right at the
    // burn front), output edge_color; when edge_t == 1 (far from the
    // front), output the sprite normally; in between, a smooth blend.
    // We preserve alpha by mixing only rgb; alpha follows the base.
    vec3 final_rgb = mix(edge_color.rgb, base.rgb, edge_t);

    COLOR = vec4(final_rgb, base.a);
}

// =====================================================================
// Things to try
// =====================================================================
// 1. Set `edge_width` to 0. The dissolve has a hard binary edge.
// 2. Set `edge_width` to 0.2 and `edge_color` to vec4(1.0, 0.2, 0.0, 1.0).
//    The burn front is a thick orange band — feels more "on fire."
// 3. Set `noise_scale` to 8.0. The dissolve becomes fine-grained;
//    looks like sand dispersing.
// 4. Set `noise_scale` to 0.5 and use a low-frequency noise texture.
//    The dissolve happens in big chunks; reads as "the sprite is
//    being eaten alive."
// 5. Tween `threshold` from 0 to 1 over 800 ms in GDScript. The result
//    is a one-shot dissolve transition perfect for enemy death.
// 6. Tween `threshold` from 1 to 0 over 800 ms. The result is a
//    "materialise" effect perfect for boss spawn.
// 7. Replace `discard` with `return` (after writing COLOR = vec4(0))
//    to use alpha-zero instead of discard. discard is faster on most
//    GPUs and is the right choice here, but compare on your hardware.
// =====================================================================
