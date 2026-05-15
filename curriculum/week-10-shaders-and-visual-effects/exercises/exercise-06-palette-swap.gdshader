// exercise-06-palette-swap.gdshader
//
// Goal
// ----
// A canvas-item shader that uses each fragment's red channel as a 1-D
// coordinate into a small *palette texture*. The displayed colour is
// the palette texture sampled at that coordinate. Same source sprite,
// any number of palettes, one shader.
//
// This is the technique behind Mega Man's weapon-tinted sprites, every
// fighting-game character's alt costumes, Pokémon's shiny variants,
// and a thousand JRPG status-effect tints.
//
// What you learn
// --------------
// - A 1-D palette texture (e.g. 16x1 pixels) used as a colour lookup.
// - Indexing via the red channel of the source sprite. The source is
//   authored as a *grayscale* image where each region is filled with
//   a uniform red value: region 0 = r=0/16, region 1 = r=1/16, etc.
// - filter_nearest on the palette: we want crisp, exact palette entries,
//   not interpolated colours. Linear filtering on a 16-entry palette
//   would smear adjacent colours into each other.
// - The technique extends trivially: 2D palettes encode "frame x outfit"
//   if the source's green channel is used as the second coordinate.
//
// Expected behaviour
// ------------------
// With the canonical "ramp" palette (a horizontal gradient from black
// to white), the shader is the identity (red channel becomes lightness).
// With a custom palette, the sprite re-colours wholesale. Swap the
// palette texture; the sprite changes outfit without re-authoring.
//
// To run
// ------
// 1. Open Godot 4.2+. Create a 2D scene with a Sprite2D.
// 2. Author or generate a "palette source" sprite: a grayscale image
//    where each visible region has a uniform red value, chosen as
//    an index into the palette. Save as `hero_palette_indices.png`.
// 3. Author or generate a "palette" texture: a 16x1 (or 32x1) PNG
//    where each column is one palette entry's rgb. Save as
//    `palette_a.png`.
// 4. Assign the indices texture as the Sprite2D's main texture.
// 5. Set Material to "New ShaderMaterial" -> Shader to "New Shader".
// 6. Paste this file. Save.
// 7. Assign `palette_a.png` to the `palette` uniform in the inspector.
// 8. Try swapping to `palette_b.png`. The sprite re-colours instantly.
//
// SOLUTIONS.md walks through generating both the indices sprite and
// several palettes in Python with the standard library only (no PIL,
// no Pillow). The output is two PNG files; total Python script is ~40
// lines.
//
// To complete
// -----------
// Ships complete. Read it, swap palettes at runtime via GDScript:
//   $Sprite2D.material.set_shader_parameter("palette", new_palette_texture)
// and use this to implement a "shiny" toggle on a pet sprite.
//
// References
// ----------
// - Godot Shaders community, *Palette swap*:
//   https://godotshaders.com/shader/palette-swap/
// - *The Book of Shaders*, chapter 8 *Colors*:
//   https://thebookofshaders.com/06/
// - GLSL 4.60 spec, section 8.13 (texture sampling):
//   https://registry.khronos.org/OpenGL/specs/gl/GLSLangSpec.4.60.pdf

shader_type canvas_item;

// =====================================================================
// Uniforms.
// =====================================================================

// The palette texture. A 1-D strip of colours indexed by the source
// sprite's red channel.
// filter_nearest: we want exact palette entries, not interpolated.
// repeat_disable: out-of-bounds indices clamp to edge.
// hint_default_white: degrade gracefully if no palette is assigned.
uniform sampler2D palette : filter_nearest, repeat_disable, hint_default_white;

// Optional palette-row offset. For 2D palettes (e.g. a 16x4 texture
// with 4 different outfits), this selects which row.
// 0.0 = first row; 0.25 = second row of 4; etc.
uniform float palette_row : hint_range(0.0, 1.0) = 0.5;

// Optional bypass: when 0.0, the shader is the identity (renders the
// source unchanged). Lets you A/B compare with and without the swap.
uniform float swap_amount : hint_range(0.0, 1.0) = 1.0;

// =====================================================================
// Fragment function.
// =====================================================================

void fragment() {
    // Sample the source sprite. We treat its red channel as a palette
    // index in 0..1.
    vec4 source = texture(TEXTURE, UV);

    // Construct the palette UV. x is the source's red channel; y is
    // the palette_row uniform.
    vec2 palette_uv = vec2(source.r, palette_row);

    // Sample the palette at that UV.
    vec3 swapped_rgb = texture(palette, palette_uv).rgb;

    // Mix between the original and the swapped colour by `swap_amount`.
    // At 0.0 the sprite renders unchanged; at 1.0 the swap is full.
    vec3 final_rgb = mix(source.rgb, swapped_rgb, swap_amount);

    // Preserve the source's alpha.
    COLOR = vec4(final_rgb, source.a);
}

// =====================================================================
// Authoring tips
// =====================================================================
// - Use a small number of distinct red values in the source. 8 to 16 is
//   typical. Use r=0/16, 1/16, 2/16, ... in your image editor's colour
//   picker.
// - When painting the source, set the image mode to *indexed colour*
//   in GIMP or Krita to enforce the discrete red levels. Otherwise
//   antialiasing along edges will pick intermediate red values and
//   sample the wrong palette entries.
// - Palette textures are tiny. A 16x1 RGBA PNG is ~100 bytes. You can
//   ship 100 palettes for the price of one diff in a build.
// - For animated sprites (a 4-frame walk cycle), use the same palette
//   indices across all four frames. The palette swap works uniformly
//   across animation states.
//
// =====================================================================
// Things to try
// =====================================================================
// 1. Author three different `palette_X.png` files (default, fire, ice)
//    and swap between them on a key press from GDScript.
// 2. Use a 16x4 palette and animate `palette_row` from 0.0 to 1.0 over
//    1 second when the player levels up. The character cycles through
//    four outfits in a "level-up flash" reading.
// 3. Set `swap_amount` to 0.5. The sprite renders as a 50/50 blend of
//    the original and the swap — useful for "transition" frames.
// 4. Chain with the hit-flash shader. The palette swap defines the
//    base colour; the hit-flash overrides it temporarily.
// 5. For palettes with more than 16 entries, increase the source
//    sprite's red precision: divide the red values by 32 instead of 16.
//    The palette texture grows to 32x1.
// =====================================================================
