# exercise-02-hit-flash-driver.gd
#
# Goal
# ----
# Drive the `flash` uniform of `exercise-02-hit-flash.gdshader` with a
# tween that runs from 1.0 to 0.0 over a configurable duration. Trigger
# the flash on a key press, on a signal, or programmatically.
#
# Attach this script to a Sprite2D whose Material is a ShaderMaterial
# whose Shader is exercise-02-hit-flash.gdshader.
#
# What you learn
# --------------
# - How to read a ShaderMaterial off a node's Material property.
# - How to duplicate a ShaderMaterial so each node has its own uniform
#   bag (the "shared material gotcha" — see Lecture 2 section 9).
# - How to drive a uniform with a Tween via tween_method.
# - How to cancel an in-flight tween before starting a new one.
# - The shape of the polish-tripod's flash leg in production code.
#
# Expected behaviour
# ------------------
# Pressing Space (or whatever you map to "flash") sets the `flash`
# uniform to 1.0 and tweens it back to 0.0 over FLASH_MS milliseconds.
# Subsequent presses cancel any in-flight tween and start fresh.
#
# To run
# ------
# 1. Save this file alongside exercise-02-hit-flash.gdshader.
# 2. Create a 2D scene; add a Sprite2D; assign any PNG as its texture.
# 3. Set the Sprite2D's Material to "New ShaderMaterial" pointing to the
#    .gdshader file.
# 4. Attach this script to the Sprite2D.
# 5. In Project Settings -> Input Map, add an action "flash" mapped to
#    the Space key.
# 6. Run the scene. Press Space. Sprite flashes.
#
# To complete
# -----------
# Ships complete. Read it, run it, then try:
#   - Changing FLASH_MS to 60.0 (snappy) and 250.0 (mushy).
#   - Changing the tween's transition to Tween.TRANS_EXPO and the easing
#     to Tween.EASE_OUT for a hard-pop, soft-fade curve.
#   - Adding a second action "red_flash" that calls flash_with_color()
#     with vec3(1.0, 0.0, 0.0) for a red flash on a different key.
#
# References
# ----------
# - Godot 4 docs, *Tween*:
#   https://docs.godotengine.org/en/stable/classes/class_tween.html
# - Godot 4 docs, *Input*:
#   https://docs.godotengine.org/en/stable/tutorials/inputs/input_examples.html
# - Godot 4 docs, *ShaderMaterial.set_shader_parameter*:
#   https://docs.godotengine.org/en/stable/classes/class_shadermaterial.html

extends Sprite2D

# How long the flash lasts in milliseconds.
const FLASH_MS: float = 120.0

# The tween currently driving the flash, if any. We keep a reference so
# subsequent calls can cancel the previous tween before starting a new
# one. Without the cancel, simultaneous tweens fight and the flash
# flickers.
var _flash_tween: Tween = null

# The action name in Project Settings -> Input Map.
# Default expects a "flash" action mapped to the Space key.
const FLASH_ACTION: String = "flash"


func _ready() -> void:
	# Materials are shared by default. Duplicate so this Sprite2D has its
	# own uniform bag. Without this, every sprite with the same shader
	# flashes when one of them is hit.
	if material is ShaderMaterial:
		material = (material as ShaderMaterial).duplicate() as ShaderMaterial

	# Defensive: set flash to 0 explicitly. Otherwise a hot-reload of the
	# scene can leave the uniform at its tween end-state (often 1.0).
	_set_flash(0.0)

	# Defensive: warn if the action isn't mapped. This catches the most
	# common student mistake on first run.
	if not InputMap.has_action(FLASH_ACTION):
		push_warning(
			"Action '%s' is not in the Input Map. Add it in Project Settings."
			% FLASH_ACTION
		)


func _input(event: InputEvent) -> void:
	# Trigger a flash on the configured action.
	if event.is_action_pressed(FLASH_ACTION):
		flash()


# Triggers a default white flash. The most common case.
func flash() -> void:
	flash_with_color(Vector3(1.0, 1.0, 1.0), FLASH_MS)


# Triggers a flash with a custom colour and duration.
# This is the form to call from gameplay code on damage events:
#   sprite.flash_with_color(Vector3(1, 0.2, 0.2), 120.0)  # red, 120 ms
#   sprite.flash_with_color(Vector3(0.4, 0.8, 1.0), 80.0)  # cold, 80 ms
func flash_with_color(color: Vector3, duration_ms: float) -> void:
	# Cancel any in-flight tween.
	if _flash_tween != null and _flash_tween.is_valid():
		_flash_tween.kill()

	# Snap the uniforms to their start state.
	# The shader's `flash_color` is a vec3; Godot maps Vector3 -> vec3.
	if material is ShaderMaterial:
		(material as ShaderMaterial).set_shader_parameter("flash_color", color)
	_set_flash(1.0)

	# Start a new tween that drives flash from 1.0 to 0.0 over the duration.
	# tween_method(callable, from, to, duration_seconds) calls the callable
	# once per frame with the interpolated value.
	_flash_tween = create_tween()
	_flash_tween.tween_method(
		Callable(self, "_set_flash"),
		1.0,
		0.0,
		duration_ms / 1000.0
	)
	# An ease-out feels best for hit-flashes: the colour holds bright for
	# the first ~40% of the duration and fades fast at the end.
	_flash_tween.set_ease(Tween.EASE_OUT)
	_flash_tween.set_trans(Tween.TRANS_QUAD)


# Internal: writes the `flash` uniform.
# Kept as a separate method so the tween can target it cleanly.
func _set_flash(value: float) -> void:
	if material is ShaderMaterial:
		(material as ShaderMaterial).set_shader_parameter("flash", value)


# =====================================================================
# Optional: a "double-tap to flash green" Easter egg.
# Demonstrates how gameplay code typically calls flash_with_color().
# Uncomment to try.
# =====================================================================
# var _last_press_time: float = -1.0
# const DOUBLE_TAP_WINDOW_MS: float = 300.0
#
# func _on_double_tap() -> void:
#     flash_with_color(Vector3(0.2, 1.0, 0.4), 200.0)
#
# func _input(event: InputEvent) -> void:
#     if event.is_action_pressed(FLASH_ACTION):
#         var now := Time.get_ticks_msec() / 1000.0
#         if _last_press_time > 0.0 and (now - _last_press_time) * 1000.0 < DOUBLE_TAP_WINDOW_MS:
#             _on_double_tap()
#         else:
#             flash()
#         _last_press_time = now
