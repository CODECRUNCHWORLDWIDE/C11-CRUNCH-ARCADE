# exercise-07-particles.gd
#
# Goal
# ----
# Configure a GPUParticles2D node from code with a ParticleProcessMaterial
# that emits a one-shot "hit-spark" burst: 32 short-lived particles
# launched outward from a point, with gravity pulling them down and
# scale and colour fading over their lifetime.
#
# Together with the hit-flash shader and a screen-shake call, this is
# the full "you hit something" feedback stack: 32 sparks fly, the
# target flashes white, the camera jiggles, the game freezes for 80 ms.
# Players cannot articulate why the hit feels weighty; they feel it.
#
# What you learn
# --------------
# - GPUParticles2D vs CPUParticles2D. GPU is the default; CPU is only
#   needed for HTML5 export or hardware without compute support.
# - ParticleProcessMaterial: the inspector resource that defines a
#   particle system's behaviour. Configure emission shape, lifetime,
#   velocity, gravity, scale-over-life, and colour-over-life.
# - One-shot emission: set `one_shot = true` and `emitting = true`.
#   The system fires once and stops.
# - Restarting emission: call `restart()` to fire again. Setting
#   `emitting = true` on an already-emitting system has no effect.
# - The Vector3-for-gravity-in-2D trap: even in GPUParticles2D, the
#   gravity field is Vector3. The z-component is ignored; you must
#   still provide it.
#
# Expected behaviour
# ------------------
# Pressing Space (action "fire") triggers a burst of 32 yellow-orange
# sparks at the node's position. The sparks fly outward in a 360-degree
# spread, slow under gravity, fade to red, and shrink over a 400 ms
# lifetime. Repeated presses re-trigger.
#
# To run
# ------
# 1. Open Godot 4.2+. Create a 2D scene.
# 2. Add a GPUParticles2D node. Set its texture to any small (8x8 or
#    16x16) PNG; a white square works for testing.
# 3. Attach this script to the GPUParticles2D node.
# 4. In Project Settings -> Input Map, add an action "fire" mapped to
//    Space (and/or mouse button 0).
// 5. Run the scene. Press fire. Watch sparks.
//
// To complete
// -----------
// Ships complete. Tweak `BURST_COUNT`, `LIFETIME_S`, and the colour
// gradient. Try chaining: a fire-spark variant uses orange-to-black
// colours; a magic-spark variant uses cyan-to-white; a blood variant
// uses dark red with a stronger gravity.
//
// References
// ----------
// - Godot 4 docs, *GPUParticles2D*:
//   https://docs.godotengine.org/en/stable/classes/class_gpuparticles2d.html
// - Godot 4 docs, *ParticleProcessMaterial*:
//   https://docs.godotengine.org/en/stable/classes/class_particleprocessmaterial.html
// - *Game Programming Patterns*, *Object Pool* chapter:
//   https://gameprogrammingpatterns.com/object-pool.html

extends GPUParticles2D

# =====================================================================
# Tunables.
# =====================================================================

# Number of particles per burst.
const BURST_COUNT: int = 32

# Lifetime of each particle in seconds.
const LIFETIME_S: float = 0.4

# Initial velocity range in pixels per second.
const VELOCITY_MIN: float = 80.0
const VELOCITY_MAX: float = 200.0

# Gravity in pixels/sec^2. Vector3 even though we are 2D.
const GRAVITY: Vector3 = Vector3(0.0, 400.0, 0.0)

# Emission shape radius (in pixels). Sparks emit from a small sphere
# rather than a single point, which reads more natural.
const EMISSION_RADIUS: float = 4.0

# The action name in Project Settings -> Input Map.
const FIRE_ACTION: String = "fire"

# =====================================================================
# Set-up.
# =====================================================================

func _ready() -> void:
	# Configure the GPUParticles2D node itself.
	amount = BURST_COUNT
	lifetime = LIFETIME_S
	one_shot = true
	# Start with emitting=false; we'll trigger via restart() on input.
	emitting = false
	# `explosiveness` 1.0 emits all particles at t=0 of the cycle (a
	# burst). 0.0 distributes emission across the lifetime evenly
	# (a fountain).
	explosiveness = 1.0
	# `randomness` adds jitter to per-particle lifetime; 0.2 is mild.
	randomness = 0.2

	# Build the ParticleProcessMaterial in code. In production you'd
	# typically save this as a .tres resource and assign it in the
	# inspector; we do it in code here for completeness.
	var mat: ParticleProcessMaterial = ParticleProcessMaterial.new()

	# Emission shape: a small sphere. Sparks emit from anywhere in this
	# sphere with random initial direction.
	mat.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_SPHERE
	mat.emission_sphere_radius = EMISSION_RADIUS

	# Initial direction: outward (a full 360-degree spread in 2D).
	# In 3D this is a unit vector in the chosen "forward" direction.
	# For 2D, we set the spread angle to 180 degrees so the cone
	# becomes a full circle.
	mat.direction = Vector3(0.0, -1.0, 0.0)  # "up"
	mat.spread = 180.0  # full circle
	mat.flatness = 1.0  # constrain to xy plane

	# Initial velocity.
	mat.initial_velocity_min = VELOCITY_MIN
	mat.initial_velocity_max = VELOCITY_MAX

	# Gravity.
	mat.gravity = GRAVITY

	# Linear damping. Slows particles to a stop before they reach the
	# bottom of their lifetime. Cinematic but optional.
	mat.damping_min = 80.0
	mat.damping_max = 200.0

	# Scale over life: shrink from 1.5 to 0.0.
	mat.scale_min = 0.5
	mat.scale_max = 1.5
	mat.scale_curve = _make_scale_curve()

	# Colour over life: yellow-white at birth, fading to dark red, then
	# fully transparent at death. Authored as a Gradient.
	mat.color_ramp = _make_colour_gradient()

	# Apply the material.
	process_material = mat

	# Defensive: warn if the action isn't mapped.
	if not InputMap.has_action(FIRE_ACTION):
		push_warning(
			"Action '%s' is not in the Input Map." % FIRE_ACTION
		)


# Build a scale-over-life curve via a CurveTexture.
# We start at 1.0 (full size at birth) and fade to 0.0 over the lifetime.
func _make_scale_curve() -> CurveTexture:
	var curve: Curve = Curve.new()
	curve.add_point(Vector2(0.0, 1.0))
	curve.add_point(Vector2(1.0, 0.0))
	var tex: CurveTexture = CurveTexture.new()
	tex.curve = curve
	return tex


# Build a colour-over-life gradient via a GradientTexture1D.
# Stops: bright yellow at birth, orange in the middle, dark red at end,
# alpha fading to 0 at the very end.
func _make_colour_gradient() -> GradientTexture1D:
	var grad: Gradient = Gradient.new()
	grad.offsets = PackedFloat32Array([0.0, 0.4, 0.9, 1.0])
	grad.colors = PackedColorArray([
		Color(1.0, 1.0, 0.6, 1.0),  # bright yellow-white
		Color(1.0, 0.6, 0.1, 1.0),  # orange
		Color(0.6, 0.1, 0.0, 0.8),  # dark red, partially transparent
		Color(0.0, 0.0, 0.0, 0.0),  # fully transparent at death
	])
	var tex: GradientTexture1D = GradientTexture1D.new()
	tex.gradient = grad
	return tex


# =====================================================================
# Input.
# =====================================================================

func _input(event: InputEvent) -> void:
	if event.is_action_pressed(FIRE_ACTION):
		fire()


# Re-emit the burst. Use restart() rather than setting emitting=true
# because a one-shot system that has finished is technically still
# "emitting=true" (the cycle ran out); restart() rewinds the cycle.
func fire() -> void:
	restart()


# =====================================================================
# Things to try
# =====================================================================
# 1. Change BURST_COUNT to 8 (too few — reads as "popcorn") or to 200
#    (too many — reads as "fog"). Find the sweet spot for your art style.
# 2. Change LIFETIME_S to 0.15 (snappy, hard) or to 1.2 (lingering,
#    dreamy). The lifetime is the duration the player perceives the
#    feedback for.
# 3. Replace the colour gradient with a fire variant (orange to black)
#    or a magic variant (cyan to white). One-line change in
#    _make_colour_gradient().
# 4. Reduce GRAVITY to Vector3(0, 0, 0). Particles drift in their initial
#    direction forever — reads as "in space" or "underwater."
# 5. Stack three particle nodes on the same impact: yellow sparks +
#    grey smoke + a single white flash particle. The composite reads
#    as a much bigger event than any of the three alone.
# 6. Trigger fire() from a gameplay event (an enemy taking damage)
#    rather than an input action. The particles are the visible reward
#    for the gameplay loop.
# =====================================================================
