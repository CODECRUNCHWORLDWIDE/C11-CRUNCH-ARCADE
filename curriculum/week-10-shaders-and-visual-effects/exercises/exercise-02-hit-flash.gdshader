// exercise-02-hit-flash.gdshader
//
// Goal
// ----
// A canvas-item shader that mixes the sprite's rgb toward a configurable
// colour by a `flash` uniform in 0..1. The companion `exercise-02-hit-
// flash-driver.gd` file drives the uniform with a 120 ms tween every
// time the player presses Space.
//
// Together these two files implement the polish-tripod's middle leg:
// the hit-flash. Apply it to every enemy in your game; the increase in
// game-feel is disproportionate to the code volume.
//
// What you learn
// --------------
// - mix(a, b, t) is the GLSL built-in for linear interpolation.
//   mix(a, b, 0.0) == a; mix(a, b, 1.0) == b; mix(a, b, 0.5) is halfway.
// - Mixing rgb only and preserving alpha keeps transparent pixels
//   transparent. This matters for sprite atlases.
// - A uniform driven by a tween is the canonical pattern for time-
//   bounded effects.
// - hint_range and source_color hints make the editor a real tool.
//
// Expected behaviour
// ------------------
// With `flash = 0.0`: identity. Sprite renders normally.
// With `flash = 1.0`: sprite renders as solid `flash_color` (white by
//   default), preserving alpha.
// Driven by the .gd file: the sprite flashes white for ~120 ms each
//   time the player presses Space.
//
// To run
// ------
// 1. Open Godot 4.2+ in a new or existing project.
// 2. Create a 2D scene with a Sprite2D. Assign any PNG with an alpha
//    channel as its texture (Godot's icon.svg works).
// 3. Set Material to "New ShaderMaterial".
// 4. On the ShaderMaterial, set Shader to "New Shader".
// 5. Paste this file into the shader editor. Save.
// 6. Attach `exercise-02-hit-flash-driver.gd` as the Sprite2D's script.
// 7. Run the scene. Press Space. Watch the sprite flash white.
//
// To complete
// -----------
// This exercise ships complete. Read the shader, run it, then change
// `flash_color`'s default to vec3(1.0, 0.2, 0.2) for a red flash.
// Try changing the duration in the driver script to 60 ms (faster) and
// 300 ms (sluggish). Find the duration that feels right for your sprite.
//
// References
// ----------
// - Godot 4 docs, *Tween*:
//   https://docs.godotengine.org/en/stable/classes/class_tween.html
// - *The Book of Shaders*, chapter 3 *Uniforms*:
//   https://thebookofshaders.com/03/
// - GLSL 4.60 spec, section 8.3 (common functions including mix):
//   https://registry.khronos.org/OpenGL/specs/gl/GLSLangSpec.4.60.pdf
// - Jan Willem Nijman (Vlambeer), *The art of screen-shake*, GDC 2013.
//   The canonical talk on the polish tripod.

shader_type canvas_item;

// =====================================================================
// Uniforms.
// =====================================================================

// The flash intensity. 0.0 = identity; 1.0 = fully `flash_color`.
// Driven by GDScript via material.set_shader_parameter("flash", value).
// hint_range gives the editor a slider for manual testing.
uniform float flash : hint_range(0.0, 1.0) = 0.0;

// The colour to mix toward. White is the default; red and green are
// common alternatives for damage-direction or status-effect flashes.
// `source_color` linearises the input from sRGB.
uniform vec3 flash_color : source_color = vec3(1.0, 1.0, 1.0);

// Optional: how much to boost the alpha during a flash. Useful when
// the sprite is partially transparent and you want the flash to read
// as opaque. 0.0 keeps the sprite's natural alpha; 1.0 forces opaque.
uniform float flash_opacity_boost : hint_range(0.0, 1.0) = 0.0;

// =====================================================================
// Fragment function.
// =====================================================================

void fragment() {
    // Sample the sprite's albedo.
    vec4 base = texture(TEXTURE, UV);

    // Mix the rgb toward flash_color by `flash`. Alpha is independent.
    // mix(a, b, t) returns a * (1 - t) + b * t.
    vec3 mixed_rgb = mix(base.rgb, flash_color, flash);

    // Optionally boost alpha during the flash. The max(...) keeps the
    // natural alpha if flash_opacity_boost is 0.
    float mixed_alpha = max(base.a, base.a + (1.0 - base.a) * flash * flash_opacity_boost);

    COLOR = vec4(mixed_rgb, mixed_alpha);
}

// =====================================================================
// Things to try
// =====================================================================
// 1. Set `flash_color` to vec3(1.0, 0.0, 0.0). The flash now reads as
//    "took damage from a fire enemy."
// 2. Set `flash_color` to vec3(0.0, 0.5, 1.0). The flash now reads as
//    "took damage from a freeze enemy."
// 3. Set `flash_opacity_boost` to 1.0. Transparent regions of the sprite
//    light up white during the flash, giving a brief "silhouette" look.
// 4. In the driver script (next file), change the tween duration from
//    120 ms to 60 ms. The flash now reads as a hard, fast hit.
// 5. In the driver script, change the tween easing curve. The default
//    is linear; try Tween.EASE_OUT (decays fast at the start) for a
//    pop-and-fade feel.
//
// The shader is five lines of math. The tuning is hours. That is the
// shape of every shader effect in production: tiny code, careful values.
// =====================================================================
