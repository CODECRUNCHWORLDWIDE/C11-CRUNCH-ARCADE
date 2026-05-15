// post_process.gdshader
//
// Goal
// ----
// A combined post-process shader for the mini-project's polish pass.
// Folds three effects into one fragment program:
//   1. Screen-wave (Exercise 5).
//   2. Vignette (Lecture 3 section 2.4).
//   3. Subtle saturation lift (a "modern indie" colour shift).
//
// Attached to a full-screen TextureRect over a SubViewport. The shader
// reads the rendered scene via hint_screen_texture and outputs the
// post-processed result. All three effects have their own uniforms;
// set any of them to its neutral value to disable that effect.
//
// What you learn
// --------------
// - Folding multiple effects into one shader saves N-1 full-screen
//   texture samples versus stacking. The trade-off: harder to disable
//   one effect independently.
// - Sequential operation in fragment(): each effect operates on the
//   result of the previous, so the order matters.
// - Saturation lift is a tiny but consistent visual gain. The formula
//   mix(luminance, rgb, saturation_factor) with factor > 1 boosts
//   saturation; < 1 mutes it.
//
// Expected behaviour
// ------------------
// At default uniforms (wave_amplitude=0, vignette_strength=0, saturation=1.0):
//   identity. The scene renders unchanged.
// At wave_amplitude=0.02, vignette_strength=0.5, saturation=1.1:
//   the scene shimmers slightly, darkens at the corners, and has a
//   subtle "filmic" colour pop.
//
// To set up
// ---------
// 1. Build the SubViewport + TextureRect tree (Lecture 3 section 2.1).
// 2. On the TextureRect, set Material to a New ShaderMaterial -> Shader
//    to a New Shader.
// 3. Paste this file.
// 4. Drive `wave_amplitude` from GDScript on game events (e.g. tween to
//    0.02 and back on a "touch" or "hit" event).
// 5. Leave `vignette_strength` and `saturation` at constant tuned values.
//
// To complete
// -----------
// Ships complete. Drop into the mini-project; tune the three uniforms.
//
// References
// ----------
// - Lecture 3 section 2 (post-process viewport quad pattern).
// - Lecture 3 section 2.3 (screen wave).
// - Lecture 3 section 2.4 (vignette).
// - Godot 4 docs, *Screen-reading shaders*:
//   https://docs.godotengine.org/en/stable/tutorials/shaders/screen-reading_shaders.html
// - GLSL 4.60 spec, section 8.3 (mix, smoothstep, length, dot):
//   https://registry.khronos.org/OpenGL/specs/gl/GLSLangSpec.4.60.pdf

shader_type canvas_item;
render_mode blend_mix, unshaded;

// =====================================================================
// Uniforms.
// =====================================================================

// Auto-bound to the rendered viewport content (the SubViewport's output).
uniform sampler2D screen_texture : hint_screen_texture, filter_linear, repeat_disable;

// ---- screen-wave -----------------------------------------------------

// Magnitude of UV distortion in screen-UV units. 0 disables.
// Drive this from GDScript with a tween for "hit-shock" effects.
uniform float wave_amplitude : hint_range(0.0, 0.05) = 0.0;

// Number of wave cycles vertically across the screen.
uniform float wave_frequency : hint_range(1.0, 100.0) = 30.0;

// Cycles per second.
uniform float wave_speed : hint_range(0.0, 20.0) = 5.0;

// ---- vignette --------------------------------------------------------

// How dark the corners get. 0 = no vignette; 1 = corners fully black.
uniform float vignette_strength : hint_range(0.0, 1.0) = 0.5;

// Inner radius where vignette starts. Smaller = vignette closer to the
// centre; larger = vignette only at the very corners.
uniform float vignette_softness : hint_range(0.0, 1.0) = 0.5;

// ---- saturation lift -------------------------------------------------

// Saturation factor. 1.0 = unchanged; >1 boosts; <1 mutes; 0 = grayscale.
uniform float saturation : hint_range(0.0, 2.0) = 1.0;

// ---- master enable ---------------------------------------------------

// A single toggle to bypass all post-processing. Useful for A/B testing
// the "before vs after" comparison without disconnecting nodes.
uniform bool enabled = true;


// =====================================================================
// Helpers.
// =====================================================================

// Standard Rec. 709 luminance weights for the perceptual brightness.
// Used by the saturation operation: lift away from the per-pixel luminance.
const vec3 LUMINANCE_WEIGHTS = vec3(0.2126, 0.7152, 0.0722);

vec3 apply_saturation(vec3 rgb, float factor) {
    // The luminance is a scalar measure of the colour's perceptual brightness.
    float luminance = dot(rgb, LUMINANCE_WEIGHTS);
    // Mix between the grayscale equivalent and the original.
    // factor < 1: pull toward gray (desaturate).
    // factor > 1: push away from gray (saturate).
    return mix(vec3(luminance), rgb, factor);
}

vec2 apply_wave(vec2 uv, float amplitude, float frequency, float speed, float time) {
    if (amplitude <= 0.0) {
        // Skip the math when disabled.
        return uv;
    }
    float arg = uv.y * frequency + time * speed;
    vec2 out_uv = uv;
    out_uv.x += sin(arg) * amplitude;
    // Clamp to avoid wrap-around at the edges.
    return clamp(out_uv, vec2(0.0), vec2(1.0));
}

float apply_vignette(vec2 uv, float strength, float softness) {
    if (strength <= 0.0) {
        return 1.0;
    }
    // Distance from the centre; ~0 at centre, ~0.71 at corners.
    float d = distance(uv, vec2(0.5));
    // softness == 0 -> hard vignette starts at centre.
    // softness == 1 -> vignette only at the very corners.
    float inner = softness * 0.5;
    return 1.0 - smoothstep(inner, 0.71, d) * strength;
}


// =====================================================================
// Fragment function.
// =====================================================================

void fragment() {
    // Master bypass.
    if (!enabled) {
        COLOR = texture(screen_texture, SCREEN_UV);
        return;
    }

    // 1. Distort the sample UV with the screen wave.
    vec2 sample_uv = apply_wave(SCREEN_UV, wave_amplitude, wave_frequency, wave_speed, TIME);

    // 2. Sample the rendered scene at the distorted UV.
    vec3 c = texture(screen_texture, sample_uv).rgb;

    // 3. Apply the saturation lift.
    c = apply_saturation(c, saturation);

    // 4. Apply the vignette darkening.
    float v = apply_vignette(SCREEN_UV, vignette_strength, vignette_softness);
    c *= v;

    COLOR = vec4(c, 1.0);
}

// =====================================================================
// Tuning notes
// =====================================================================
//
// For a "modern action game" feel:
//   wave_amplitude        = 0.0       (driven by events only)
//   wave_frequency        = 30.0
//   wave_speed            = 5.0
//   vignette_strength     = 0.4
//   vignette_softness     = 0.6
//   saturation            = 1.08
//
// For a "horror" feel:
//   wave_amplitude        = 0.0       (driven by events only)
//   vignette_strength     = 0.8
//   vignette_softness     = 0.3
//   saturation            = 0.85       (slightly muted)
//
// For an "underwater" feel:
//   wave_amplitude        = 0.012     (constant subtle shimmer)
//   wave_frequency        = 8.0
//   wave_speed            = 3.0
//   vignette_strength     = 0.5
//   vignette_softness     = 0.4
//   saturation            = 1.2       (lush)
//
// For a "no effect" baseline (proof the bypass works):
//   enabled               = false
// =====================================================================
