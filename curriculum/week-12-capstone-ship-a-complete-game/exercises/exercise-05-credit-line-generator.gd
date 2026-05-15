# Exercise 05 — The in-game credits roll generator.
#
# Goal
# ----
# Read a CREDITS.md file at runtime and render its contents as a scrolling
# credits roll in the game's title-or-end screen. The roll mirrors the
# project's CREDITS.md (the source of truth from Lecture 3) so that you
# only edit the credits in one place.
#
# Features
# --------
# - Parses a CREDITS.md with H1/H2 sections, bullet lines, and a couple of
#   recognised CC licence tags.
# - Renders the roll into a Label inside a ScrollContainer (or any node you
#   wire up) as a Tween-driven scroll from screen-bottom to screen-top.
# - Exposes a public render_credits(label, viewport_height) entry point so a
#   capstone scene can attach this script to any node and call it.
# - Exposes a render_text_only() entry point for headless / test contexts.
#
# Usage in the capstone
# ---------------------
# 1. Open Godot 4.2+.
# 2. Add a Control scene with: ScrollContainer -> VBoxContainer -> Label.
# 3. Attach this script to the Control root.
# 4. Place CREDITS.md in res:// (the project root) or pass an absolute path.
# 5. Call render_credits(label_node, viewport_size.y) from _ready().
#
# Run as a headless smoke test from the Godot project root:
#
#     godot --headless --script exercises/exercise-05-credit-line-generator.gd
#
# Headless mode emits the rendered text-only roll to stdout and quits.

extends Node

# ---------------------------------------------------------------------------
# Constants.
# ---------------------------------------------------------------------------

const DEFAULT_CREDITS_PATH: String = "res://CREDITS.md"
const SCROLL_SECONDS_PER_LINE: float = 0.6
const PIXELS_PER_LINE: int = 24

# ---------------------------------------------------------------------------
# Public API.
# ---------------------------------------------------------------------------

# Render the credits to a Label node. The label is positioned starting
# below the viewport and tweened upward at a fixed line-per-second cadence.
func render_credits(target_label: Label, viewport_height: float) -> void:
	var lines: PackedStringArray = _load_credits_lines(DEFAULT_CREDITS_PATH)
	var rendered: String = _format_lines_for_screen(lines)
	target_label.text = rendered
	target_label.position = Vector2(0, viewport_height)
	var total_lines: int = lines.size()
	var duration: float = max(8.0, total_lines * SCROLL_SECONDS_PER_LINE)
	var target_y: float = -float(total_lines * PIXELS_PER_LINE) - 40.0
	var tween: Tween = create_tween()
	tween.tween_property(target_label, "position:y", target_y, duration)

# Render the credits to a plain string. Useful for a headless test or for
# logging during a Sunday QA pass.
func render_text_only(path: String = DEFAULT_CREDITS_PATH) -> String:
	var lines: PackedStringArray = _load_credits_lines(path)
	return _format_lines_for_screen(lines)

# ---------------------------------------------------------------------------
# Parsing helpers.
# ---------------------------------------------------------------------------

# Load the credits file and return a PackedStringArray of cleaned-up lines.
# H1/H2 headings are kept; bullet lines are stripped of leading dashes and
# bold markers (**...**) but otherwise preserved.
func _load_credits_lines(path: String) -> PackedStringArray:
	var lines: PackedStringArray = PackedStringArray()
	if not FileAccess.file_exists(path):
		push_warning("CREDITS.md not found at %s; using placeholder." % path)
		return _placeholder_credits()
	var f: FileAccess = FileAccess.open(path, FileAccess.READ)
	if f == null:
		push_error("Could not open %s for reading." % path)
		return _placeholder_credits()
	var raw_text: String = f.get_as_text()
	f.close()
	for raw_line in raw_text.split("\n"):
		var line: String = raw_line.strip_edges()
		if line.begins_with("# "):
			lines.append(line.substr(2).to_upper())
			lines.append("")
		elif line.begins_with("## "):
			lines.append("--- " + line.substr(3) + " ---")
			lines.append("")
		elif line.begins_with("- "):
			lines.append(_clean_bullet_line(line.substr(2)))
		elif line.begins_with("http"):
			# A standalone URL line; keep but mark as a sub-line.
			lines.append("    " + line)
		elif line == "":
			lines.append("")
		else:
			lines.append(line)
	return lines

# Strip bold markers (**...**) from a bullet line and collapse internal
# whitespace. Returns a plain-text rendering suitable for an in-game label.
func _clean_bullet_line(text: String) -> String:
	var cleaned: String = text.replace("**", "")
	# Collapse multiple spaces.
	while cleaned.find("  ") != -1:
		cleaned = cleaned.replace("  ", " ")
	return "  " + cleaned

# Join the cleaned lines into a final string. Blank lines are preserved as
# spacing in the rolled output; runs of three or more blanks are collapsed
# to two for tighter pacing.
func _format_lines_for_screen(lines: PackedStringArray) -> String:
	var out: PackedStringArray = PackedStringArray()
	var blank_run: int = 0
	for line in lines:
		if line == "":
			blank_run += 1
			if blank_run <= 2:
				out.append("")
		else:
			blank_run = 0
			out.append(line)
	# Tail card.
	out.append("")
	out.append("")
	out.append("THANK YOU FOR PLAYING.")
	out.append("")
	out.append("Built for Code Crunch Worldwide C11 Crunch Arcade, 2026.")
	return "\n".join(out)

# Fallback content if CREDITS.md is missing on disk. The capstone build
# should never hit this path in production; it is for local development
# before CREDITS.md is written.
func _placeholder_credits() -> PackedStringArray:
	var lines: PackedStringArray = PackedStringArray()
	lines.append("CREDITS")
	lines.append("")
	lines.append("--- Art ---")
	lines.append("  Frog sprite, CC0 by PixelArtist123 on OpenGameArt.")
	lines.append("  Car sprites, CC-BY by RoadWarriorArt on OpenGameArt.")
	lines.append("")
	lines.append("--- Audio ---")
	lines.append("  Hop SFX, CC0 by FreesoundUser42 on Freesound.")
	lines.append("  Music loop, CC-BY by AmbientCreator99 on Freesound.")
	lines.append("")
	lines.append("--- Tools ---")
	lines.append("  Godot 4.2.2, MIT licence.")
	lines.append("  OBS Studio, GPL.")
	lines.append("  Shotcut, GPL.")
	return lines

# ---------------------------------------------------------------------------
# Headless smoke test entry point.
# ---------------------------------------------------------------------------

# When invoked with `godot --headless --script exercise-05-credit-line-generator.gd`,
# the engine calls this function. It renders the credits to stdout and quits.
func _init() -> void:
	if Engine.is_editor_hint():
		return
	if not OS.has_feature("standalone"):
		# Avoid running the headless smoke test inside the editor.
		return
	print("--- Exercise 05 headless smoke test ---")
	var text: String = render_text_only(DEFAULT_CREDITS_PATH)
	print(text)
	print("--- end of credits roll ---")
