// exercise-01-identity-and-tint.gdshader
//
// Goal
// ----
// The minimal Godot 4 canvas-item shader. Two phases:
//   Phase A: the identity shader (sprite renders unchanged).
//   Phase B: add a tint uniform (sprite renders multiplied by a colour).
//
// This is the entry-point exercise for the week. Every other shader in
// the course is a variant of this template.
//
// What you learn
// --------------
// - shader_type canvas_item;  — declares a 2D shader.
// - The fragment() function is required; it runs once per fragment.
// - texture(TEXTURE, UV) samples the sprite's albedo at the fragment's UV.
// - COLOR is the fragment's output. Write to it to set the displayed colour.
// - uniform vec4 foo : source_color = vec4(1.0);  — declare a tint uniform
//   with a colour-picker hint and a default value of opaque white.
// - The artist tunes the tint from the Godot inspector without recompiling.
//
// Expected behaviour
// ------------------
// Phase A (lines 50-58 only): the sprite renders pixel-for-pixel identical
// to the same sprite with no material assigned.
// Phase B (lines 60-72 in addition): the sprite renders multiplied by
// `tint`. Set `tint` to (1.0, 0.5, 0.5, 1.0) for pink; (0.5, 0.5, 1.0, 1.0)
// for blue; (1.0, 1.0, 1.0, 1.0) for unchanged (the default).
//
// To run
// ------
// 1. Open Godot 4.2+ in a new or existing project.
// 2. Create a 2D scene with a Sprite2D and assign any PNG as its texture.
// 3. In the inspector, set Material to "New ShaderMaterial".
// 4. On the new ShaderMaterial, set Shader to "New Shader".
// 5. Paste this entire file into the shader editor.
// 6. Save (Ctrl+S inside the shader editor).
// 7. Phase B: in the inspector's Shader Parameters section, the `tint`
//    uniform appears as a colour picker. Drag the hue around. The sprite
//    changes live.
//
// To complete
// -----------
// This exercise ships complete. Read every line, then change `tint`'s
// default from vec4(1.0) to vec4(0.5, 1.0, 0.5, 1.0) and verify the
// sprite renders green. Then try multiplying by sin(TIME) for a pulse.
//
// References
// ----------
// - Godot 4 docs, *Your first shader*:
//   https://docs.godotengine.org/en/stable/tutorials/shaders/your_first_shader/index.html
// - *The Book of Shaders*, chapter 2 *Hello world*:
//   https://thebookofshaders.com/02/
// - GLSL 4.60 specification, section 8.13 (texture lookup functions):
//   https://registry.khronos.org/OpenGL/specs/gl/GLSLangSpec.4.60.pdf

// =====================================================================
// PHASE A: identity shader.
// =====================================================================

shader_type canvas_item;

// Declare a `tint` uniform with a colour-picker hint in the editor.
// `source_color` tells Godot the input is in sRGB and to linearise it
// before the math happens. Without `source_color`, you would be doing
// gamma-encoded multiplication, which is wrong.
// The `= vec4(1.0)` is the default: opaque white. Tinting by white is
// the identity, so the default behaviour matches Phase A.
uniform vec4 tint : source_color = vec4(1.0);

// Optional: a TIME-driven pulse uniform. When non-zero, the tint pulses
// at this frequency. Off by default.
uniform float pulse_hz : hint_range(0.0, 10.0) = 0.0;

void fragment() {
    // =================================================================
    // PHASE A: sample the sprite's albedo at the fragment's UV.
    // =================================================================
    // `texture(sampler, uv)` is the GLSL built-in for sampling a texture.
    // It returns a vec4 (rgba). The sampler's filter (linear by default)
    // determines how the GPU interpolates between texels.
    vec4 base = texture(TEXTURE, UV);

    // =================================================================
    // PHASE B: multiply by tint.
    // =================================================================
    // If `pulse_hz` is non-zero, modulate the tint amount by a sine
    // wave. The 0.5 + 0.5 * sin() trick maps the -1..1 range of sin()
    // into the 0..1 range we want for an intensity.
    // The TAU constant is 2 * PI, the period of the sine wave in radians.
    float pulse = (pulse_hz > 0.0)
        ? (0.5 + 0.5 * sin(TIME * pulse_hz * TAU))
        : 1.0;

    // Apply the tint. Multiplying rgba by a vec4 multiplies each channel
    // independently. The pulse scales the rgb but not the alpha.
    vec4 tinted = base * tint;
    tinted.rgb *= pulse;

    // Write the final fragment colour.
    COLOR = tinted;
}

// =====================================================================
// Things to try, in order:
// =====================================================================
// 1. Comment out lines 92-98 and replace with `COLOR = base;` — the
//    sprite renders identical to no-shader. Identity shader achieved.
// 2. Replace with `COLOR = vec4(UV, 0.0, 1.0);` — the sprite becomes a
//    red-green gradient revealing its UV layout. UV.x is in the red
//    channel; UV.y is in the green channel. This is a debugging trick
//    you will use often.
// 3. Replace with `COLOR = vec4(vec3(sin(TIME) * 0.5 + 0.5), 1.0);` —
//    the sprite pulses between black and white at 1/TAU Hz.
// 4. Replace with `COLOR = vec4(base.rgb * (0.5 + 0.5 * cos(UV.x * TAU * 10.0)), base.a);`
//    — vertical stripes scrolling left to right.
// 5. Set `tint` to vec4(1.0, 0.0, 0.0, 1.0) and `pulse_hz` to 4.0 —
//    the sprite pulses red at 4 Hz. The first vague heartbeat.
//
// Every one of those is a one-line edit to this file. That is the power
// of the fragment shader's simple function-shape: (uv, time) -> color.
// =====================================================================
