// exercise-05-screen-wave.gdshader
//
// Goal
// ----
// A *post-process* shader. Apply it to a full-screen TextureRect whose
// material samples the SubViewport's rendered output. The shader
// distorts the screen sample UV by a sine wave in screen-y, animated in
// TIME. The visual result reads as heat haze, underwater shimmer, or
// "hit-shock" if you ramp the amplitude up for 200 ms after a hit.
//
// This is the first exercise that uses the post-process viewport quad
// pattern. The set-up in the scene tree is described in the header
// comment of mini-project/post_process.gdshader and in Lecture 3
// section 2.
//
// What you learn
// --------------
// - `hint_screen_texture` binds the current viewport's texture to a
//   uniform automatically. The Godot 4 idiom; replaces the older
//   custom-texture-pass pattern from Godot 3.x.
// - SCREEN_UV is the fragment's screen position normalised to 0..1.
//   It is the input you distort.
// - The classic distortion math: `sin(uv.y * frequency + TIME * speed)`.
//   The frequency controls how many wave-crests appear vertically; the
//   speed controls how fast they scroll.
// - amplitude scales the magnitude of the distortion in UV-space.
//   Typical values: 0.001 for subtle shimmer, 0.01 for dramatic shock.
//
// Expected behaviour
// ------------------
// The scene rendered into the SubViewport appears with a horizontal
// wave that scrolls vertically. With wave_amplitude near 0, the
// distortion is invisible; with it at 0.02, the screen visibly ripples.
//
// To set up the scene
// -------------------
// 1. Open Godot 4.2+. Create a new 2D scene.
// 2. Add a SubViewportContainer node, set its `stretch` to true and its
//    anchors to fill the parent rect.
// 3. As a child of SubViewportContainer, add a SubViewport. Set its
//    size to 1920x1080 (or whatever your project resolution is).
// 4. Under SubViewport, build your "game" — typically a Camera2D plus
//    a few Sprite2Ds for testing.
// 5. As a sibling of SubViewportContainer, add a TextureRect. Set its
//    anchors to fill the parent rect.
// 6. Set the TextureRect's Material to "New ShaderMaterial" -> Shader
//    to "New Shader". Paste this file.
// 7. In the inspector, the `screen_texture` uniform is auto-bound via
//    `hint_screen_texture`. You do not need to assign it manually.
// 8. Tune `wave_frequency`, `wave_speed`, and `wave_amplitude` in the
//    inspector. Watch the rippling.
//
// To complete
// -----------
// Ships complete. Tune all three uniforms, then try replacing the sine
// with a chained sin/cos for a 2D wavy distortion, and try driving
// `wave_amplitude` from GDScript with a tween for a "hit-shock" effect.
//
// References
// ----------
// - Godot 4 docs, *Screen-reading shaders*:
//   https://docs.godotengine.org/en/stable/tutorials/shaders/screen-reading_shaders.html
// - Godot 4 docs, *Custom post-processing*:
//   https://docs.godotengine.org/en/stable/tutorials/shaders/advanced_postprocessing.html
// - *The Book of Shaders*, chapter 7 *Matrices* (for the transformation
//   math that motivates UV distortion):
//   https://thebookofshaders.com/07/
// - GLSL 4.60 spec, section 8.1 (sin, cos, and friends):
//   https://registry.khronos.org/OpenGL/specs/gl/GLSLangSpec.4.60.pdf

shader_type canvas_item;
// `unshaded` skips the 2D lighting pass; we are not lit.
render_mode blend_mix, unshaded;

// =====================================================================
// Uniforms.
// =====================================================================

// `hint_screen_texture` auto-binds the current viewport's rendered
// content. `filter_linear` gives a smooth resample under distortion;
// `filter_nearest` would give a chunky retro look.
uniform sampler2D screen_texture : hint_screen_texture, filter_linear, repeat_disable;

// Number of full wave cycles across the screen height.
// 10 = 10 horizontal "ridges"; 30 = 30; 100 = fine shimmer.
uniform float wave_frequency : hint_range(1.0, 100.0) = 30.0;

// How fast the wave scrolls upward, in cycles per second.
uniform float wave_speed : hint_range(0.0, 20.0) = 5.0;

// Magnitude of the UV distortion, in UV units (i.e. fraction of screen).
// 0.001 = subtle; 0.005 = visible; 0.02 = dramatic; 0.05 = comical.
uniform float wave_amplitude : hint_range(0.0, 0.05) = 0.005;

// Optional secondary axis: distort in y too for a 2D ripple.
// 0.0 = pure horizontal shimmer; 1.0 = full 2D ripple.
uniform float vertical_factor : hint_range(0.0, 1.0) = 0.0;

// Phase offset for the wave. 0.0 = aligned to TIME. Drive this from
// GDScript if you want to sync the wave to gameplay (e.g. randomise
// per scene transition).
uniform float wave_phase = 0.0;

// =====================================================================
// Fragment function.
// =====================================================================

void fragment() {
    // Start with the unmodified screen UV.
    vec2 uv = SCREEN_UV;

    // Compute the wave's argument. The frequency multiplies into UV.y;
    // TIME * speed scrolls the wave; wave_phase lets us offset it
    // externally.
    float arg = uv.y * wave_frequency + TIME * wave_speed + wave_phase;

    // Distort the x component by a sine of the argument.
    uv.x += sin(arg) * wave_amplitude;

    // Optionally distort the y component by a cosine for a 2D ripple.
    // We use a different frequency on y (1.7x) to avoid the cross-
    // pattern looking too regular.
    uv.y += cos(arg * 1.7) * wave_amplitude * vertical_factor;

    // Sample the screen texture at the distorted UV.
    // Clamp UV to 0..1 to avoid wrap-around when amplitude is high.
    uv = clamp(uv, vec2(0.0), vec2(1.0));

    COLOR = texture(screen_texture, uv);
}

// =====================================================================
// Things to try
// =====================================================================
// 1. Set `wave_amplitude` to 0. Identity post-process. The scene
//    renders unchanged. Useful as a "no effect" baseline.
// 2. Set `wave_amplitude` to 0.02 and `wave_frequency` to 5.0. Big,
//    slow waves — reads as underwater.
// 3. Set `wave_amplitude` to 0.005, `wave_frequency` to 80.0, `wave_speed`
//    to 12.0. Fine, fast shimmer — reads as heat haze above hot metal.
// 4. Drive `wave_amplitude` from GDScript with a tween that ramps it
//    to 0.03 over 50 ms and back to 0 over 250 ms when the player takes
//    damage. The result is a "hit-shock" effect that punches without
//    being permanent.
// 5. Set `vertical_factor` to 1.0 and `wave_frequency` to 8.0. The
//    screen distorts in 2D — looks like the world is sloshing.
// 6. Chain this shader with a vignette (Lecture 3 section 2.4) by
//    putting a second TextureRect with a vignette shader after this
//    one. Compose your own post-process stack.
// =====================================================================
