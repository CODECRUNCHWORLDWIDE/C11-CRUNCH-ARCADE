// exercise-04-outline.gdshader
//
// Goal
// ----
// A canvas-item shader that detects the alpha boundary of a sprite by
// sampling four (or eight) neighbour texels and emits an outline colour
// at the boundary. The outline reads as "this sprite is highlighted"
// and is the standard "selectable / hovered / hit" affordance in
// strategy games, RPGs, and roguelikes.
//
// The trick is purely a fragment-shader trick: no extra geometry, no
// extra draw call, no extra texture beyond the sprite's own albedo.
//
// What you learn
// --------------
// - TEXTURE_PIXEL_SIZE is `(1.0/texture_width, 1.0/texture_height)`.
//   It is the size of one texel in UV-space, which is the unit you need
//   to step to the next neighbour.
// - Sampling four neighbours: right, left, up, down.
// - Optional eight-neighbour mode adds the four diagonals at a higher
//   sample cost but a thicker, rounder outline.
// - The trade-off of branching in a shader: `if (base.a > 0.5)` is
//   fine; long if/else chains are not. Modern GPUs handle short
//   branches cheaply; older mobile GPUs hate any branching.
//
// Expected behaviour
// ------------------
// Sprite renders with a one-pixel border of `outline_color` everywhere
// its alpha boundary is. Internal opaque regions are unchanged;
// transparent regions outside the outline keep their natural transparency.
//
// To run
// ------
// 1. Open Godot 4.2+, create a 2D scene with a Sprite2D.
// 2. Assign a PNG with a clearly defined alpha boundary (e.g. Godot's
//    icon.svg, or any sprite with a transparent background).
// 3. *Important*: the sprite's texture must have a border of transparent
//    pixels around its visible content. Cropped-tight sprites cannot
//    grow an outline because the neighbours sample outside the texture.
//    In Godot, set the texture's import settings to disable mipmaps
//    (mipmaps blur the boundary) and ensure filter is set to Linear.
// 4. Set Material to "New ShaderMaterial" -> Shader to "New Shader".
// 5. Paste this file. Save.
// 6. Tune `outline_width` (1.0 is a one-texel outline; 3.0 is thicker).
// 7. Tune `outline_color` (white is debug; bright yellow is "selected";
//    red is "danger").
//
// To complete
// -----------
// Ships complete. Read the four-tap math; then try the eight-tap
// `EIGHT_TAP` define for a rounder outline; finally, try animating
// `outline_color`'s alpha with TIME for a "pulsing selected" feel.
//
// References
// ----------
// - Godot Shaders community, *2D outline / stroke* (MIT):
//   https://godotshaders.com/shader/2d-outline-stroke/
// - *The Book of Shaders*, chapter 9 *2D matrices*:
//   https://thebookofshaders.com/07/
// - GLSL 4.60 spec, section 8.13 (texture function variants):
//   https://registry.khronos.org/OpenGL/specs/gl/GLSLangSpec.4.60.pdf

shader_type canvas_item;
render_mode blend_mix;

// =====================================================================
// Uniforms.
// =====================================================================

// The outline colour. source_color linearises from sRGB.
uniform vec4 outline_color : source_color = vec4(1.0, 1.0, 1.0, 1.0);

// How many texels to step. 1.0 is a one-texel outline; 2.0 is two-texel;
// fractional values give sub-pixel outlines that anti-alias nicely under
// linear filtering.
uniform float outline_width : hint_range(0.0, 8.0) = 1.0;

// Whether to use the eight-neighbour (diagonals included) variant.
// More samples per fragment, but the outline is rounder at corners.
uniform bool eight_tap = false;

// Optional pulsing: animate the outline alpha over time.
// 0.0 = no pulse; values around 2.0 give a "this is selected" feel.
uniform float pulse_hz : hint_range(0.0, 10.0) = 0.0;

// =====================================================================
// Helper: sample the sprite's alpha at an offset UV.
// Out-of-bounds samples return 0 by default in Godot when wrap is
// disabled, which is what we want.
// =====================================================================

float sample_alpha(vec2 uv) {
    return texture(TEXTURE, uv).a;
}

// =====================================================================
// Fragment function.
// =====================================================================

void fragment() {
    vec4 base = texture(TEXTURE, UV);

    // If the current fragment is already inside the sprite (opaque),
    // draw it normally. The outline is only emitted from previously-
    // transparent fragments adjacent to opaque ones.
    // Threshold of 0.5 splits the alpha cleanly; 0.01 would catch any
    // antialiased edge fragment and is also reasonable.
    if (base.a > 0.5) {
        COLOR = base;
        return;
    }

    // One texel in UV-space, scaled by the desired outline width.
    vec2 step = TEXTURE_PIXEL_SIZE * outline_width;

    // Sample the four cardinal neighbours.
    float a_right = sample_alpha(UV + vec2(step.x, 0.0));
    float a_left  = sample_alpha(UV - vec2(step.x, 0.0));
    float a_down  = sample_alpha(UV + vec2(0.0, step.y));
    float a_up    = sample_alpha(UV - vec2(0.0, step.y));

    float max_neighbour = max(max(a_right, a_left), max(a_down, a_up));

    // Optionally sample the four diagonals as well. The diagonals fill
    // the gaps at corners that a four-tap leaves jagged.
    if (eight_tap) {
        float a_dr = sample_alpha(UV + vec2(step.x, step.y));
        float a_dl = sample_alpha(UV + vec2(-step.x, step.y));
        float a_ur = sample_alpha(UV + vec2(step.x, -step.y));
        float a_ul = sample_alpha(UV + vec2(-step.x, -step.y));
        max_neighbour = max(max_neighbour, max(max(a_dr, a_dl), max(a_ur, a_ul)));
    }

    // If at least one neighbour is opaque, this fragment is on the
    // outline. Otherwise, discard — keep this transparent pixel transparent.
    if (max_neighbour > 0.5) {
        // Optional pulse: modulate outline alpha by TIME.
        float pulse = (pulse_hz > 0.0)
            ? (0.5 + 0.5 * sin(TIME * pulse_hz * TAU))
            : 1.0;
        COLOR = vec4(outline_color.rgb, outline_color.a * pulse);
    } else {
        discard;
    }
}

// =====================================================================
// Things to try
// =====================================================================
// 1. Set `outline_width` to 2.0. The outline is two texels thick.
// 2. Set `eight_tap` to true and `outline_width` to 1.5. Rounder, fatter.
// 3. Set `outline_color` to vec4(1.0, 0.2, 0.2, 1.0) and `pulse_hz` to 4.0.
//    The sprite has a red, pulsing outline — perfect for "low health
//    enemy" or "critical objective marker."
// 4. Combine with the hit-flash shader: chain them as two TextureRects
//    in a post-process stack, or fold them into one longer shader.
// 5. The technique extends naturally to a *normal-mapped* outline: use
//    the normal direction to bias the sampling pattern. Out of scope
//    this week but worth knowing for stretch goals.
// =====================================================================
