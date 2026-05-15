# screen_shake.gd
#
# Goal
# ----
# A drop-in screen-shake helper for any 2D project. Attach to a Camera2D.
# Call add_shake(amount) to nudge the camera; the shake intensity decays
# automatically over time.
#
# This is the first leg of the polish tripod (Lecture 3 section 1). The
# entire implementation is ~30 lines of meaningful code; the rest is
# tunables, docstring, and the optional "named-budget" feature that
# lets different gameplay events have independent shake budgets that
# do not stomp each other.
#
# What you learn
# --------------
# - The screen-shake idiom: random offset scaled by a decaying strength.
# - Why `max(current, new)` is the correct combinator for stacked shakes
#   rather than `current + new` (the addition spirals out of control).
# - How to expose per-event named "budgets" so the camera's shake from
#   "hit" and "explosion" decay independently and combine cleanly.
# - How to fully restore camera offset at shake_strength == 0, so the
#   camera does not stay slightly jittered.
#
# Expected behaviour
# ------------------
# - Idle: camera renders at its scene-defined position.
# - After add_shake(N): camera's offset jiggles for ~N/SHAKE_DECAY seconds,
#   decaying linearly to zero.
# - Multiple add_shake() calls do not stack additively; they take the max.
# - add_named_shake("hit", 4.0) and add_named_shake("explosion", 12.0)
#   compose: the camera shakes by max of the two budgets.
#
# To use
# ------
# 1. Attach this script to a Camera2D in any scene.
# 2. From any game-event handler:
#        get_tree().get_first_node_in_group("camera").add_shake(8.0)
#    (Group the camera as "camera" in the inspector for easy lookup.)
# 3. Tune SHAKE_DECAY (units per second) and the per-call amount for taste.
#
# References
# ----------
# - Jan Willem Nijman (Vlambeer), *The art of screen-shake*, GDC 2013.
#   The canonical talk on screen-shake. YouTube; ~30 minutes.
# - Godot 4 docs, *Camera2D*:
#   https://docs.godotengine.org/en/stable/classes/class_camera2d.html

extends Camera2D

# How fast shake intensity decays in units per second.
# 5.0 = a unit-1 shake fully decays in 0.2 seconds.
# 2.0 = same shake takes 0.5 seconds.
# Tune for the game's pacing: snappy combat -> 5..8; cinematic -> 2..3.
const SHAKE_DECAY: float = 5.0

# Maximum allowed shake intensity. Caps runaway from naive `add_shake(huge)`.
const MAX_SHAKE: float = 32.0

# Internal: a dictionary of named budgets. The total visible shake is
# the maximum of all named budgets.
# String -> float.
var _budgets: Dictionary = {}


func _ready() -> void:
	# Group ourselves as "camera" so other nodes can find us without
	# a hard reference path. Optional but convenient.
	add_to_group("camera")


# Add to the unnamed default budget. Most common call.
# Use this for a generic "something happened" shake.
func add_shake(amount: float) -> void:
	add_named_shake("default", amount)


# Add to a named budget. Use distinct names for distinct event classes
# so that, e.g., a constant low-level rumble from "engine" does not
# get overwritten by a stronger one-shot "hit". The camera shakes by
# the max across all budgets.
func add_named_shake(budget_name: String, amount: float) -> void:
	# Clamp to MAX_SHAKE.
	var clamped: float = min(amount, MAX_SHAKE)
	# Take the max with the existing budget. Stacked shakes do not add;
	# the larger one wins until it decays past the smaller.
	if _budgets.has(budget_name):
		_budgets[budget_name] = max(float(_budgets[budget_name]), clamped)
	else:
		_budgets[budget_name] = clamped


# Cancel a named budget immediately. Useful when a continuous shake
# (e.g. a rumble while the boss is on-screen) needs to stop when the
# triggering condition ends.
func clear_named_shake(budget_name: String) -> void:
	if _budgets.has(budget_name):
		_budgets.erase(budget_name)


# Cancel all shake. Restores camera offset to zero on the next frame.
func clear_all_shake() -> void:
	_budgets.clear()


# Read-only view of the current total shake strength, for debugging.
func get_total_strength() -> float:
	var maximum: float = 0.0
	for v in _budgets.values():
		maximum = max(maximum, float(v))
	return maximum


func _process(delta: float) -> void:
	# Decay every named budget linearly.
	for key in _budgets.keys():
		var v: float = max(0.0, float(_budgets[key]) - SHAKE_DECAY * delta)
		_budgets[key] = v

	# Drop budgets that have fully decayed.
	var dead_keys: Array = []
	for key in _budgets.keys():
		if float(_budgets[key]) <= 0.0:
			dead_keys.append(key)
	for k in dead_keys:
		_budgets.erase(k)

	# Apply the visible shake as the max of all budgets.
	var strength: float = get_total_strength()
	if strength <= 0.0:
		offset = Vector2.ZERO
		return

	# Random offset in [-strength, +strength] on each axis.
	# randf_range is uniform random; perfectly acceptable for camera shake.
	offset = Vector2(
		randf_range(-strength, strength),
		randf_range(-strength, strength),
	)


# =====================================================================
# Optional: named events that map to specific shake profiles.
# Call these instead of add_named_shake() for common gameplay events.
# Tune the amounts here once and the rest of the codebase calls a name.
# =====================================================================

func shake_for_hit() -> void:
	add_named_shake("hit", 6.0)

func shake_for_explosion() -> void:
	add_named_shake("explosion", 14.0)

func shake_for_jump_landing() -> void:
	add_named_shake("landing", 3.0)

func shake_for_player_death() -> void:
	# A big, slow shake. The death is the event the player remembers.
	add_named_shake("death", 24.0)
