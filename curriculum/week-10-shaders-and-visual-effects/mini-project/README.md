# Mini-project — Polish Pass on a Prior Week's Game

> **Estimated time:** 4-6 hours.
> **Submit by:** Sunday 23:59.
> **Deliverable:** the polished prior-week project, three new files (`screen_shake.gd`, `post_process.gdshader`, and one shader of your choice), plus a 10-second screen-recording.

## The brief

Take a mini-project you shipped in a prior week (Week 8 audio recommended; Week 9 multiplayer is the worked example below; any prior week with a visible interaction loop is acceptable) and apply *three* of the visual effects you built this week to it. The result should feel demonstrably more polished without the gameplay being any different.

Specifically, you must apply:

1. **A screen-shake** triggered on at least one in-game event. Use the included `screen_shake.gd`.
2. **A hit-flash** on at least one sprite, triggered on at least one in-game event. Reuse `exercise-02-hit-flash.gdshader` and its driver.
3. **A third effect of your choice** from this week's toolbox: dissolve, outline, screen wave, palette swap, LUT colour grade, or a custom shader you wrote. Apply it to either a sprite or as a post-process. The included `post_process.gdshader` provides a screen-wave + vignette combined post-process you can use directly, or you can author your own.

The point is *compound polish*. One effect in isolation is fine; three effects working together is the moment a prototype starts to feel like a real game.

## The worked example: polishing Week 9's two-cursor cursor demo

The Week 9 mini-project is a LAN-only two-cursor shared canvas. Two Pygame clients (or a Pygame and a Godot client) connect to a Python authoritative server and see each other's mouse cursor on a shared screen. It is correct, it is networked, it is exactly as visually flat as a working network demo tends to be.

This week we add:

1. **Screen-shake** when the two cursors touch (within 16 pixels). The shake reads as "an interaction happened."
2. **Hit-flash** on a cursor when it is the one being touched. The flash leans toward red when shaken from the right, blue from the left.
3. **A screen-wave post-process** that briefly intensifies during a touch, then decays over 400 ms.

The Week 9 game runs identically — same UDP packets, same 20 Hz tick, same interpolation — but now feels like an event happens when two cursors meet. The visual reward turns a tech demo into a play experience.

### File-level changes to the Week 9 project

If you are polishing Week 9, the diff is approximately:

- **Add** `screen_shake.gd` (provided in this folder; ~80 lines).
- **Add** `post_process.gdshader` (provided in this folder; ~50 lines).
- **Add** `exercise-02-hit-flash.gdshader` and its driver (copy from the week-10 exercises folder).
- **Modify** the cursor scene to wire each cursor's `flash` and to wire the shake on cursor-touch.
- **Modify** the main scene to add a SubViewport + TextureRect for the post-process.

Total LOC change: ~150 lines added, ~10 lines modified. Time: 90-120 minutes if you know the Week 9 codebase, longer if it has been a while.

## Files in this folder

| File                     | What it is                                                              |
|--------------------------|-------------------------------------------------------------------------|
| `README.md`              | This file. The brief, the worked example, the grading rubric.           |
| `screen_shake.gd`        | A drop-in screen-shake helper. Attach to your `Camera2D`. Call `add_shake(amount)`. |
| `post_process.gdshader`  | A combined screen-wave + vignette post-process. Use on a full-screen TextureRect over a SubViewport. |

You do not need to modify these unless you want to. They are intentionally tuned to look "good enough" out of the box.

## Step-by-step (worked example, Godot port of Week 9)

### Step 0: snapshot the base game

Before starting the polish, commit your Week 9 project as a baseline. The grading rubric requires a *before* and *after* comparison; you need both to exist.

### Step 1: build the SubViewport + TextureRect for the post-process

In the root scene:

1. Add a `SubViewportContainer`. Set `stretch = true` and anchor full rect.
2. Under it, a `SubViewport`. Set its size to your game's resolution (e.g. 1280x720). Set `render_target_update_mode = ALWAYS`.
3. Move every existing game node (Camera2D, the cursor scenes, the background) to be a child of the SubViewport.
4. Add a `TextureRect` as a sibling of the SubViewportContainer. Set its anchors to fill the parent rect.
5. On the TextureRect, set Material to a new `ShaderMaterial`. On the ShaderMaterial, set Shader to a new Shader; paste `post_process.gdshader` into it.

At this point the game renders identically (the post-process is configured but its uniforms are at neutral values).

### Step 2: install the screen-shake

1. Find your project's `Camera2D`. Attach `screen_shake.gd` to it.
2. In your network-handler script (the one that processes incoming snapshots), find where you detect a "touch" event between two cursors.
3. Call `$Camera2D.add_shake(8.0)` on the touch. Pick a value between 4 and 16; tune to taste.

Run the project. Touch the two cursors. The camera jiggles.

### Step 3: install the hit-flash

1. Copy `exercise-02-hit-flash.gdshader` and `exercise-02-hit-flash-driver.gd` into your project's `shaders/` folder (create one if you do not have it).
2. On each cursor's Sprite2D node, set Material to a new `ShaderMaterial` pointing at the hit-flash shader.
3. Attach the driver script to each cursor.
4. In your network-handler, when a touch happens, call `your_cursor_sprite.flash_with_color(Vector3(1.0, 0.4, 0.4), 120.0)` (or whatever colour and duration you prefer).

Run the project. Touch the two cursors. They flash.

### Step 4: install the screen-wave

The included `post_process.gdshader` has a `wave_amplitude` uniform that starts at 0 (the wave is invisible). In your network-handler, when a touch happens:

```gdscript
var mat: ShaderMaterial = $TextureRect.material as ShaderMaterial
var tween: Tween = create_tween()
tween.tween_method(
    func(v: float) -> void: mat.set_shader_parameter("wave_amplitude", v),
    0.02, 0.0, 0.4
)
```

`0.02` is the peak amplitude; `0.4` is the decay duration in seconds. The wave intensifies on the touch and decays over 400 ms.

### Step 5: tune

This is the longest step. Each of the three effects has at least one knob; spending 20 minutes adjusting them is the entire polish craft.

Tune in this order:

1. **Shake strength.** Too low: barely visible. Too high: nauseating. Sweet spot: 6-10 units.
2. **Flash duration.** Too short: invisible. Too long: looks like a bug. Sweet spot: 80-150 ms.
3. **Flash colour.** Pure white reads as "neutral hit." Tinted red reads as "damage." Tinted yellow reads as "neutral collision."
4. **Wave amplitude peak.** Too low: invisible. Too high: visibly distorts and reads as a bug. Sweet spot: 0.01-0.03.
5. **Wave decay duration.** Too short: the wave is gone before the player notices. Too long: feels sluggish. Sweet spot: 250-500 ms.

Iterate until you get a one-second window after the touch where shake, flash, and wave compound visibly but none of them dominates.

### Step 6: record

Capture a 10-second screen recording of two cursors interacting at least twice. Save as MP4 or GIF. This is the deliverable.

## Grading rubric

- **20%** — the project runs without errors. No shader compile errors, no GDScript exceptions, no missing-uniform warnings.
- **30%** — all three effects are visibly active in the recording.
- **20%** — the effects are tuned. A tester (or you, after a 30-minute break) watching the recording should not say "the shake is too strong" or "the flash is invisible."
- **20%** — the integration is clean. The shake, flash, and wave fire on the same triggering event(s) and behave consistently across repeated triggers.
- **10%** — the recording is well-framed: shows the before-state for a second, shows the trigger, shows the post-trigger state. Not just a chaotic clip.

## Stretch goals

If the basics fly past in under three hours and you want to push further:

1. **Add freeze-frame.** Set `Engine.time_scale = 0.05` for 60-80 ms on the touch, then restore. The "weight" goes up a level.
2. **Add particles.** Place a `GPUParticles2D` at the touch point and trigger a one-shot burst (use the configuration from `exercise-07-particles.gd`). Now there are four effects compounding.
3. **Differentiate the cursors.** Use the palette-swap shader to give each player a distinct colour palette. Set the palette texture from a per-player config so the artist can re-skin without touching code.
4. **Author a custom shader.** Pick an effect not covered this week (chromatic aberration, scanlines, pixelation, a CRT curve) and add it as a fourth post-process pass. Find one on the [Godot Shaders gallery](https://godotshaders.com/) under a permissive licence and adapt it.
5. **Profile.** Open the Godot debugger's *Monitors* tab. Note the `frame_time_gpu` reading before and after your polish pass. Most projects on integrated graphics should still hit 60 fps; if not, identify the offending shader (typically the screen-wave or LUT) and reduce its sample count or texture size.

The stretch goals are *not* required for full marks. The base brief — three effects, tuned, recorded — is the deliverable. The stretches are for students who finish early and want to keep going.

## A note on the previous week being polished

This is the second consecutive week where the deliverable depends on a prior week's project. The course design assumes you keep your previous mini-projects in a state you can re-open. If your Week 9 (or Week 8) mini-project is broken, the right move is *not* to fix it under time pressure this week; the right move is to polish a *different* prior week's project (Week 4 platformer, Week 6 dialogue system, Week 7 inventory) where the source is still alive. The lesson — *applying polish to a working game raises its perceived quality by an order of magnitude* — is the same regardless of which game is polished.

## How to submit

Bundle:

```text
mini-project-submission/
  README-changes.md       # ~200 words: what you polished, what knobs you tuned
  recording.mp4           # or recording.gif; 10 seconds
  screenshot-before.png   # the unpolished version (or a frame from the before-state)
  screenshot-after.png    # the polished version with all three effects visible
  src/                    # your modified game source
```

The `README-changes.md` is graded separately from the rubric above (it is part of the 20% "integration is clean" line item). It does not need to be long; it needs to be specific.

## Reflection

After submission, take 15 minutes to write down (just for yourself, no submission required):

1. What was the smallest change that produced the biggest visible improvement?
2. What was the largest change that produced no visible improvement?
3. If you had one more week on this game, what would you polish next?

These are the questions a senior engineer asks during a polish review. Answering them now is practice for the rest of your career.
